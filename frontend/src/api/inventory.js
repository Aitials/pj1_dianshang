import request from '../utils/request'

// 库存列表（分页）
export function getInventory(params, config) {
  return request.get('/inventory', { params, ...config })
}

// 调整库存
export function adjustInventory(productId, data) {
  return request.post(`/adjust/${productId}/`, data)
}

// 按商品ID查询单个库存
export function getInventoryDetail(productId) {
  return request.get('/inventory/detail', { params: { product_id: productId } })
}

// 低库存预警
export function getWarnings() {
  return request.get('/inventory/warnings')
}

// 补货建议
export function getReplenish(replenishDays = 30) {
  return request.get('/inventory/replenish', { params: { replenish_days: replenishDays } })
}

// 库存流水
export function getInventoryLogs(params) {
  return request.get('/inventory/logs', { params })
}
