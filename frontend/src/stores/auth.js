import { defineStore } from 'pinia'
import { getMe } from '../api/auth'

// 角色 → 可访问菜单路径映射（与后端 RBAC 权限对齐）
export const ROLE_MENUS = {
  admin: ['/dashboard', '/orders', '/products', '/customers', '/sellers', '/logistics', '/inventory', '/ai', '/users', '/logs'],
  operator: ['/dashboard', '/orders', '/products', '/customers', '/sellers', '/logistics', '/ai'],
  warehouse: ['/products', '/inventory', '/ai'],
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
    // 从 /auth/me 拿角色（后端返回 {"username", "role": ["admin"]}）
    async loadPermissions() {
      try {
        const res = await getMe()
        const role = (res.role && res.role[0]) || ''
        this.role = role
        localStorage.setItem('role', role)
        return role
      } catch (e) {
        this.role = ''
        return ''
      }
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
