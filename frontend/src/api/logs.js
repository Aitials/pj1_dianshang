import request from '../utils/request'

// 操作日志（分页）
export function getLogs(params) {
  return request.get('/logs', { params })
}
