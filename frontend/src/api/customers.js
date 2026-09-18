import request from '../utils/request'

// 客户列表（分页 + 筛选）
export function getCustomers(params) {
  return request.get('/customers', { params })
}

// 客户详情
export function getCustomerDetail(customerId) {
  return request.get(`/customers/${customerId}`)
}
