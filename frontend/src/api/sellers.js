import request from '../utils/request'

// 卖家列表（分页 + 筛选）
export function getSellers(params) {
  return request.get('/sellers', { params })
}

// 卖家详情
export function getSellerDetail(sellerId) {
  return request.get(`/sellers/${sellerId}`)
}
