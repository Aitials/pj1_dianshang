import request from '../utils/request'

// 总览指标（5 个，缺准时率）
export function getOverview() {
  return request.get('/dashboard/overview')
}

// 准时率（单独接口）
export function getOnTimeRate() {
  return request.get('/dashboard/send_time')
}

// 销售趋势（按月）
export function getSalesTrend() {
  return request.get('/dashboard/trend')
}

// 类目排行
export function getCategoryRanking(top = 10) {
  return request.get('/dashboard/category-ranking', { params: { top } })
}

// 卖家排行
export function getSellerRanking(top = 10) {
  return request.get('/dashboard/seller-ranking', { params: { top } })
}
