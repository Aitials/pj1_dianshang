import request from '../utils/request'

// 总览指标
export function getOverview() {
  return request.get('/dashboard/overview')
}

// 预警
export function getAlerts() {
  return request.get('/dashboard/alerts')
}

// 准时率
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
  return request.get('/dashboard/seller_ranking', { params: { top } })
}

// 商品排行
export function getProductsRanking(top = 10) {
  return request.get('/dashboard/products_ranking', { params: { top } })
}
