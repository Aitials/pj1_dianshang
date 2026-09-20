import request from '../utils/request'

// 订单列表（分页 + 筛选）
export function getOrders(params, config) {
  return request.get('/orders', { params, ...config })
}

// 订单详情
export function getOrderDetail(orderId) {
  return request.get(`/orders/${orderId}`)
}

// 订单状态分布
export function getOrderStatusDistribution() {
  return request.get('/orders/status-distribution')
}

// 月度订单趋势
export function getOrderMonthlyTrend() {
  return request.get('/orders/monthly-trend')
}
