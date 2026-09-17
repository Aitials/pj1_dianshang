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
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>经营总览</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品与类目</span>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <span>客户分析</span>
        </el-menu-item>
        <el-menu-item index="/sellers">
          <el-icon><Shop /></el-icon>
          <span>卖家分析</span>
        </el-menu-item>
        <el-menu-item index="/logistics">
          <el-icon><Van /></el-icon>
          <span>物流分析</span>
        </el-menu-item>
        <el-menu-item index="/inventory">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
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
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const avatarText = computed(() => (authStore.username || 'U').slice(0, 1).toUpperCase())

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
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
</style>
