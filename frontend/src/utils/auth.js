import axios from 'axios'

// ---------------------------------------------------------------------------
// JWT 本地解析与"临期静默续签"
//
// 背景：access token 有效期 8 小时（见 backend/app/core/security.py 的
// ACCESS_TOKEN_EXPIRE_MINUTES）。纯无状态方案下，token 一旦真的过期就无法续期，
// 只能在请求发出前提前换新。
//
// 因此策略是"临期静默续签"：
//   1. 发请求前本地解析 JWT 的 exp，剩余不足 RENEW_AHEAD_MS 就先调 /auth/refresh；
//   2. 续签成功后用新 token 发原请求，用户全程无感；
//   3. 万一还是撞上 401（例如页面空闲超过阈值导致 token 已彻底过期），
//      由 request.js 统一清登录态并带 redirect 回登录页，登录后回到原地址。
//
// 这里只解析 payload 判断时间，**不做签名校验**（前端拿不到 SECRET_KEY，
// 也没必要）——真正的校验始终在后端。前端解析只用于决定"要不要提前续签"。
// ---------------------------------------------------------------------------

export const TOKEN_KEY = 'token'
export const USERNAME_KEY = 'username'
export const ROLE_KEY = 'role'

// 剩余有效期低于该值时提前续签。与后端 ACCESS_TOKEN_RENEW_AHEAD_MINUTES 对齐（5 分钟）。
const RENEW_AHEAD_MS = 5 * 60 * 1000

// 续签请求用独立 axios 实例：绝不走 request 实例，否则会再次触发请求拦截器，
// 形成"续签里又调续签"的递归。
const rawHttp = axios.create({ baseURL: '/api', timeout: 10000 })

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.removeItem(ROLE_KEY)
}

/**
 * 解析 JWT payload 的 exp，返回剩余毫秒数。
 * 解析失败（格式非法 / 无 exp / 缺 padding）返回 null，调用方按"未知"处理，
 * 不做提前续签、也不因此拦截请求，避免误伤。
 */
export function getTokenRemainingMs(token) {
  const value = token || getToken()
  if (!value) return null

  try {
    const payloadSeg = value.split('.')[1]
    if (!payloadSeg) return null
    // base64url → base64：替换 URL 安全字符，并补齐 padding
    const base64 = payloadSeg.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
    const payload = JSON.parse(atob(padded))
    if (typeof payload.exp !== 'number') return null
    return payload.exp * 1000 - Date.now()
  } catch (e) {
    return null
  }
}

export function isTokenExpiring(token) {
  const remaining = getTokenRemainingMs(token)
  // 剩余时间未知 → 不主动续签，交给 401 分支兜底
  if (remaining === null) return false
  return remaining <= RENEW_AHEAD_MS
}

// 并发去重：多个请求同时发现 token 临期时，只能发一次续签请求。
// 否则并发续签会各自拿到新 token，后写的覆盖先写的，还可能互相判定失效。
// 这里让后来者直接复用同一个 Promise。
let refreshingPromise = null

/**
 * 调后端 /auth/refresh 换新 token 并写入 localStorage。
 *
 * 返回值语义：
 *   - 新 token 字符串：续签成功
 *   - null：旧 token 已彻底过期（后端 401），需要重新登录
 *   - 抛异常：网络错误或其他非 401 失败，由调用方决定如何处理
 */
export function refreshToken() {
  if (refreshingPromise) return refreshingPromise

  refreshingPromise = (async () => {
    const current = getToken()
    if (!current) return null

    try {
      const res = await rawHttp.post(
        '/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${current}` } }
      )
      const data = res.data
      const newToken = data?.data?.access_token || data?.access_token
      if (!newToken) return null

      localStorage.setItem(TOKEN_KEY, newToken)
      return newToken
    } catch (e) {
      if (e.response?.status === 401) return null
      throw e
    }
  })().finally(() => {
    refreshingPromise = null
  })

  return refreshingPromise
}

/**
 * 供**非 axios 请求**（如流式 fetch）复用的续签入口。
 * 流式请求走 fetch + ReadableStream，不经过 axios 拦截器，
 * 所以必须自己保证 token 新鲜，否则会出现"流已开始后才过期"的静默失败。
 */
export async function ensureFreshToken() {
  if (!isTokenExpiring()) return getToken()
  try {
    return (await refreshToken()) ?? getToken()
  } catch (e) {
    return getToken()
  }
}

/**
 * 清登录态并跳登录页，带上当前地址以便登录后回跳。
 * 校验 redirect 只能是站内路径（以单个 / 开头且非 //），防止开放重定向。
 *
 * 用 redirecting 标记保证每次页面加载只跳一次：多个并发请求同时 401 时，
 * 每个都会走到这里，若不拦，后一次会用已被改写的地址覆盖，
 * 甚至丢掉最初那个 redirect 参数。
 */
let redirecting = false

export function redirectToLogin() {
  if (redirecting) return
  redirecting = true

  clearAuth()
  const current = window.location.pathname + window.location.search
  const safe = current && current.startsWith('/') && !current.startsWith('//') && !current.startsWith('/login')
  window.location.href = safe ? `/login?redirect=${encodeURIComponent(current)}` : '/login'
}
