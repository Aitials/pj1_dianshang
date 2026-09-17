<template>
  <div>
    <div class="page-title">
      <el-icon><Box /></el-icon>
      <span>库存管理</span>
    </div>
    <el-card>
      <el-table :data="inventory" v-loading="loading" stripe>
        <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
        <el-table-column prop="quantity" label="当前库存" width="120" />
        <el-table-column prop="safe_stock" label="安全库存" width="120" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openAdjust(row)">调整</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </el-card>

    <el-dialog v-model="showAdjust" title="调整库存" width="400px">
      <p style="margin-bottom: 16px">商品ID：{{ current.product_id }}</p>
      <el-form>
        <el-form-item label="变化量">
          <el-input-number v-model="adjustForm.change" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="adjustForm.reason" placeholder="如：采购入库 / 销售出库" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdjust = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventory, adjustInventory } from '../api/inventory'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const inventory = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showAdjust = ref(false)
const current = ref({})
const adjustForm = reactive({ change: 0, reason: '' })

async function load() {
  loading.value = true
  try {
    const res = await getInventory({ page: page.value, page_size: pageSize.value })
    inventory.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function openAdjust(row) {
  current.value = row
  adjustForm.change = 0
  adjustForm.reason = ''
  showAdjust.value = true
}

async function submitAdjust() {
  await adjustInventory(current.value.product_id, {
    change: adjustForm.change,
    reason: adjustForm.reason,
    operator: authStore.username,
  })
  ElMessage.success('调整成功')
  showAdjust.value = false
  load()
}

onMounted(load)
</script>
