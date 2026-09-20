import request from '../utils/request'

// 用户列表（分页）
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

// 角色列表
export function getRoles() {
  return request.get('/roles')
}

// 给用户分配角色
export function assignRole(userId, roleIds) {
  return request.put(`/users/${userId}/roles`, { role_ids: roleIds })
}
