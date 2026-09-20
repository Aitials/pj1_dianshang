import request from '../utils/request'

// 商品列表（分页 + 类目筛选）
export function getProducts(params) {
  return request.get('/products', { params })
}

// 商品详情
export function getProductDetail(productId) {
  return request.get(`/products/${productId}`)
}

// 类目列表（筛选下拉用）
export function getCategories() {
  return request.get('/products/categories')
}

// 类目分析
export function getCategoryAnalysis(top = 10) {
  return request.get('/products/category-analysis', { params: { top } })
}

// 商品评分排行
export function getRatingRank(top = 10, order = 'desc', min_reviews = 10) {
  return request.get('/products/rating_rank', { params: { top, order, min_reviews } })
}
