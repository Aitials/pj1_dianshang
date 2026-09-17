import request from '../utils/request'

export function getCustomers() {
  return request.get('/customers')
}
