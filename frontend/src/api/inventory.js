import request from '../utils/request'

// 库存列表（分页）
export function getInventory(params, config) {
  return request.get('/inventory', { params, ...config })
}

// 调整库存
export function adjustInventory(productId, data) {
  return request.post(`/adjust/${productId}/`, data)
}
