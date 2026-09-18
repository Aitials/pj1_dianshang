import request from '../utils/request'

// 商品列表（分页 + 类目筛选）
export function getProducts(params) {
  return request.get('/products', { params })
}

// 商品详情
export function getProductDetail(productId) {
  return request.get(`/products/${productId}`)
}
