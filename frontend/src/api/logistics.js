import request from '../utils/request'

export function getLogisticsOverview() {
  return request.get('/logistics/overview')
}
