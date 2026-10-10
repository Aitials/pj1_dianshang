import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, isTokenExpiring, refreshToken, redirectToLogin } from './auth'

// axios 实例，baseURL 指向 /api（配合 vite 代理转发到后端 8000）
const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：自动带上 token；若 token 临近过期，先静默续签再发原请求。
//
// 为什么放在请求前而不是等 401：本方案是无状态的（没有 refresh token），
// token 一旦真的过期就无法再续，只能重新登录。所以必须抢在过期前换新。
request.interceptors.request.use(async (config) => {
  // 续签请求本身不能再触发续签逻辑（它走独立实例，不会有此问题，这里再兜一层）
  if (config.url?.includes('/auth/refresh')) return config

  if (isTokenExpiring()) {
    try {
      await refreshToken()
    } catch (e) {
      // 续签失败（网络抖动等）不在这里拦截，让原请求照常发出，
      // 由响应拦截器的 401 分支统一兜底，避免"网络一抖就跳登录页"
    }
  }

  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一解包 + 错误处理
request.interceptors.response.use(
  (response) => {
    const data = response.data
    // 统一响应格式 {code, message, data} → 解包出 data
    if (data && typeof data === 'object' && 'code' in data && 'message' in data && 'data' in data) {
      return data.data
    }
    // 旧格式（如登录、部分 dashboard 接口）原样返回
    return data
  },
  async (error) => {
    const status = error.response?.status
    const body = error.response?.data
    const original = error.config
    // silent 标记的请求不弹全局错误提示
    const silent = original?.silent
    // 后端异常统一体是 {code, message, data}（见 backend/app/main.py 的异常处理器），
    // detail 只作为 FastAPI 默认格式的兜底，否则错误文案会退化成通用提示
    const message = body?.message || body?.detail

    // 401 兜底：先尝试续签一次并重放原请求。
    // 走到这里通常有两种情况：① token 已彻底过期；② 服务端刚重启换了 SECRET_KEY 等。
    // 用 _retried 标记防止无限重试（续签后仍 401 时只失败一次，不再循环）。
    if (status === 401 && original && !original._retried) {
      original._retried = true
      let newToken = null
      try {
        newToken = await refreshToken()
      } catch (e) {
        newToken = null
      }

      if (newToken) {
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${newToken}`
        return request(original)
      }

      ElMessage.error(message || '登录已过期，请重新登录')
      redirectToLogin()
      return Promise.reject(error)
    }

    if (status === 401) {
      // 已重试过仍 401：清登录态回登录页，不重复弹提示（避免多个并发请求刷屏）
      redirectToLogin()
    } else if (!silent) {
      ElMessage.error(message || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
