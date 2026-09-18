import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ROLE_MENUS } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '经营总览' },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/Orders.vue'),
        meta: { title: '订单管理' },
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('../views/OrderDetail.vue'),
        meta: { title: '订单详情' },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue'),
        meta: { title: '商品与类目' },
      },
      {
        path: 'products/:id',
        name: 'ProductDetail',
        component: () => import('../views/ProductDetail.vue'),
        meta: { title: '商品详情' },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/Customers.vue'),
        meta: { title: '客户分析' },
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('../views/CustomerDetail.vue'),
        meta: { title: '客户详情' },
      },
      {
        path: 'sellers',
        name: 'Sellers',
        component: () => import('../views/Sellers.vue'),
        meta: { title: '卖家分析' },
      },
      {
        path: 'sellers/:id',
        name: 'SellerDetail',
        component: () => import('../views/SellerDetail.vue'),
        meta: { title: '卖家详情' },
      },
      {
        path: 'logistics',
        name: 'Logistics',
        component: () => import('../views/Logistics.vue'),
        meta: { title: '物流分析' },
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/Inventory.vue'),
        meta: { title: '库存管理' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '系统用户管理', requiresAdmin: true },
      },
    ],
  },
  // 兜底：未实现的菜单，点击显示"开发中"
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/Placeholder.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录去登录页；已登录按角色校验模块访问权限
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }

  if (token && to.path !== '/login' && to.path !== '/') {
    const role = localStorage.getItem('role')
    if (!role) {
      // 未分配角色
      next('/login')
      return
    }
    const allowed = ROLE_MENUS[role] || []
    const canAccess = allowed.some((p) => to.path === p || to.path.startsWith(p + '/'))
    if (!canAccess) {
      ElMessage.warning('没有访问该模块的权限')
      next(allowed[0] || '/login')
      return
    }
  }

  next()
})

export default router
