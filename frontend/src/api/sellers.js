import request from '../utils/request'

export function getSellers() {
  return request.get('/sellers')
}
