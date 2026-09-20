<template>
  <div>
    <div class="page-title">
      <el-icon><Document /></el-icon>
      <span>操作日志</span>
    </div>

    <el-card>
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="operator" label="操作人" width="140" />
        <el-table-column prop="action" label="操作类型" width="160">
          <template #default="{ row }">
            <el-tag>{{ actionText(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="操作对象" width="230" show-overflow-tooltip />
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
        <el-table-column label="时间" :formatter="fmtTime" prop="created_at" width="180" />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="load"
          @size-change="load"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getLogs } from '../api/logs'

const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await getLogs({ page: page.value, page_size: pageSize.value })
    logs.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function fmtTime(row, column, value) {
  return value ? String(value).slice(0, 19) : '-'
}

function actionText(action) {
  const map = {
    adjust_inventory: '调整库存',
    create_user: '创建用户',
    assign_role: '分配角色',
  }
  return map[action] || action
}

onMounted(load)
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
