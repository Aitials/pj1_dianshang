import request from '../utils/request'

// 客户列表（分页 + 筛选）
export function getCustomers(params) {
  return request.get('/customers', { params })
}

// 客户详情
export function getCustomerDetail(customerId) {
  return request.get(`/customers/${customerId}`)
}

// 州列表（筛选下拉用）
export function getCustomerStates() {
  return request.get('/customers/states')
}

// 客户消费排行
export function getCustomerRanking(top = 10) {
  return request.get('/customers/ranking', { params: { top } })
}

// 复购分析
export function getCustomerRepurchase() {
  return request.get('/customers/repurchase')
}

// 客户地域分布
export function getCustomerGeo() {
  return request.get('/customers/geo')
}
