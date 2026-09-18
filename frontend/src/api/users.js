import request from '../utils/request'

// 用户列表（分页）；config 用于传递 silent 等自定义配置
export function getUsers(params, config) {
  return request.get('/users', { params, ...config })
}

// 用户详情
export function getUserDetail(userId) {
  return request.get(`/users/${userId}`)
}

// 创建用户
export function createUser(data) {
  return request.post('/users', data)
}

// 修改用户密码
export function updateUser(userId, data) {
  return request.put(`/users/${userId}`, data)
}
