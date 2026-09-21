<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="22"><Shop /></el-icon>
        <span>电商运营平台</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#ffffff"
      >
        <el-menu-item v-for="m in visibleMenus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="page-title">{{ $route.meta.title }}</div>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" class="avatar">{{ avatarText }}</el-avatar>
            <span class="username">{{ authStore.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

    <!-- AI 助手悬浮按钮 -->
    <div v-if="$route.path !== '/ai'" class="ai-fab" @click="goAi">
      <el-icon :size="20"><MagicStick /></el-icon>
      <span>AI 助手</span>
    </div>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore, ROLE_MENUS } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 全量菜单配置
const menus = [
  { path: '/dashboard', title: '经营总览', icon: 'Odometer' },
  { path: '/orders', title: '订单管理', icon: 'List' },
  { path: '/products', title: '商品与类目', icon: 'Goods' },
  { path: '/customers', title: '客户分析', icon: 'User' },
  { path: '/sellers', title: '卖家分析', icon: 'Shop' },
  { path: '/logistics', title: '物流分析', icon: 'Van' },
  { path: '/inventory', title: '库存管理', icon: 'Box' },
  { path: '/ai', title: 'AI 运营助手', icon: 'ChatDotRound' },
  { path: '/users', title: '系统用户管理', icon: 'Setting' },
  { path: '/logs', title: '操作日志', icon: 'Document' },
]

// 根据当前角色过滤可见菜单
const visibleMenus = computed(() => {
  const allowed = ROLE_MENUS[authStore.role] || []
  return menus.filter((m) => allowed.includes(m.path))
})

const avatarText = computed(() => (authStore.username || 'U').slice(0, 1).toUpperCase())

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

// 跳转到 AI 助手
function goAi() {
  router.push('/ai')
}
</script>

<style scoped>
.layout {
  height: 100%;
}
.aside {
  background: #1e293b;
  display: flex;
  flex-direction: column;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  letter-spacing: 1px;
}
.menu {
  flex: 1;
  border-right: none;
  padding: 8px;
}
.menu .el-menu-item {
  height: 46px;
  border-radius: 8px;
  margin-bottom: 4px;
}
.menu .el-menu-item.is-active {
  background: var(--el-color-primary);
}
.menu .el-menu-item:hover {
  background: rgba(148, 163, 184, 0.15);
}
.menu .el-menu-item.is-active:hover {
  background: var(--el-color-primary);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #334155;
}
.avatar {
  background: var(--el-color-primary);
}
.username {
  font-size: 14px;
}

.main {
  background: #f1f5f9;
  padding: 20px;
}

/* AI 助手悬浮按钮 */
.ai-fab {
  position: fixed;
  right: 32px;
  bottom: 40px;
  height: 48px;
  padding: 0 20px;
  border-radius: 24px;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
  transition: all 0.25s;
  z-index: 1000;
  font-size: 14px;
  font-weight: 600;
}
.ai-fab:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.55);
}
</style>
