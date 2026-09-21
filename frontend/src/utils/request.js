import axios from 'axios'
import { ElMessage } from 'element-plus'

// axios 实例，baseURL 指向 /api（配合 vite 代理转发到后端 8000）
const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：自动带上 token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
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
  (error) => {
    const status = error.response?.status
    const body = error.response?.data
    // 后端异常统一体是 {code, message, data}（见 backend/app/main.py 的异常处理器），
    // detail 只作为 FastAPI 默认格式的兜底，否则错误文案会退化成通用提示
    const message = body?.message || body?.detail
    // silent 标记的请求不弹全局错误提示
    const silent = error.config?.silent

    if (status === 401) {
      ElMessage.error(message || '登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      window.location.href = '/login'
    } else if (!silent) {
      ElMessage.error(message || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
