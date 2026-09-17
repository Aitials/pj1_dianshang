<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* ============ 全局基础 ============ */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html,
body,
#app {
  height: 100%;
  font-family: 'Inter', 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  background: #f1f5f9;
}

/* ============ 配色变量 ============ */
:root {
  --el-color-primary: #2563eb;
  --el-color-primary-light-3: #5b8def;
  --el-color-primary-light-5: #93b4f3;
  --el-color-primary-light-7: #c7d7f9;
  --el-color-primary-light-8: #dde6fb;
  --el-color-primary-light-9: #eef3fd;
  --el-color-primary-dark-2: #1d4fd8;
  --sidebar-bg: #1e293b;
  --sidebar-active: #2563eb;
  --page-bg: #f1f5f9;
}

/* ============ 通用卡片 ============ */
.el-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
}

/* ============ 表格 ============ */
.el-table {
  --el-table-border-color: #f1f5f9;
  --el-table-header-bg-color: #f8fafc;
  --el-table-header-text-color: #475569;
}
.el-table th.el-table__cell {
  font-weight: 600;
}

/* ============ 页面标题 ============ */
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
}
.page-title .el-icon {
  color: var(--el-color-primary);
  font-size: 22px;
}

/* ============ 滚动条 ============ */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
