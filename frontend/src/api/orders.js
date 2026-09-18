import request from '../utils/request'

// 订单列表（分页 + 筛选）
export function getOrders(params, config) {
  return request.get('/orders', { params, ...config })
}

// 订单详情
export function getOrderDetail(orderId) {
  return request.get(`/orders/${orderId}`)
}
