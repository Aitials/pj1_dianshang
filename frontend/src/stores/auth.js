import { defineStore } from 'pinia'
import { getUsers } from '../api/users'
import { getInventory } from '../api/inventory'
import { getOrders } from '../api/orders'

// 角色 → 可访问菜单路径映射（与后端 RBAC 权限对齐）
export const ROLE_MENUS = {
  admin: ['/dashboard', '/orders', '/products', '/customers', '/sellers', '/logistics', '/inventory', '/users', '/logs'],
  operator: ['/dashboard', '/orders', '/products', '/customers', '/sellers', '/logistics'],
  warehouse: ['/products', '/inventory'],
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    role: localStorage.getItem('role') || '',
  }),
  getters: {
    isAdmin: (state) => state.role === 'admin',
  },
  actions: {
    setAuth(token, username) {
      this.token = token
      this.username = username
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
    },
    // 通过探测关键接口判断当前用户角色（后端 /me 不返回角色，故用静默探测）
    async loadPermissions() {
      let role = ''
      try {
        await getUsers({ page: 1, page_size: 1 }, { silent: true })
        role = 'admin' // 拥有 user:read
      } catch (e) {
        try {
          await getInventory({ page: 1, page_size: 1 }, { silent: true })
          role = 'warehouse' // 拥有 inventory:read
        } catch (e2) {
          try {
            await getOrders({ page: 1, page_size: 1 }, { silent: true })
            role = 'operator' // 拥有 order:read
          } catch (e3) {
            role = ''
          }
        }
      }
      this.role = role
      localStorage.setItem('role', role)
      return role
    },
    logout() {
      this.token = ''
      this.username = ''
      this.role = ''
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
    },
  },
})
