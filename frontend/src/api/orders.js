import request from '../utils/request'

// 订单列表（分页）
export function getOrders(params) {
  return request.get('/orders', { params })
}
