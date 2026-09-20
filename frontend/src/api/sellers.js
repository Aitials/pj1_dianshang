import request from '../utils/request'

// 卖家列表（分页 + 筛选）
export function getSellers(params) {
  return request.get('/sellers', { params })
}

// 卖家详情
export function getSellerDetail(sellerId) {
  return request.get(`/sellers/${sellerId}`)
}

// 州列表（筛选下拉用）
export function getSellerStates() {
  return request.get('/sellers/states')
}

// 卖家销售排行
export function getSellerRank(top = 10) {
  return request.get('/seller/rank', { params: { top } })
}

// 卖家评分表现
export function getSellerReview(top = 20) {
  return request.get('/seller/review', { params: { top } })
}
