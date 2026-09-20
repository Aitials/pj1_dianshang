import request from '../utils/request'

// 物流总览
export function getLogisticsOverview() {
  return request.get('/logistics/overview')
}

// 物流地域分布
export function getLogisticsGeo() {
  return request.get('/logistics/geo')
}

// 延迟与评分关联
export function getDelayRating() {
  return request.get('/logistics/delay-rating')
}
