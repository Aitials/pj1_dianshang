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

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    if (status === 401) {
      ElMessage.error(detail || '登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else {
      ElMessage.error(detail || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
