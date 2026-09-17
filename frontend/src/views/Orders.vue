<template>
  <div>
    <div class="page-title">
      <el-icon><List /></el-icon>
      <span>订单管理</span>
    </div>
    <el-card>
      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_id" label="订单号" width="230" show-overflow-tooltip />
        <el-table-column prop="customer_id" label="客户ID" width="230" show-overflow-tooltip />
        <el-table-column prop="order_status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.order_status)">{{ row.order_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下单时间" :formatter="fmtTime" prop="order_purchase_timestamp" />
        <el-table-column label="实际送达" :formatter="fmtTime" prop="order_delivered_customer_date" />
        <el-table-column label="预计送达" :formatter="fmtTime" prop="order_estimated_delivery_date" />
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
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
import { getOrders } from '../api/orders'

const orders = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await getOrders({ page: page.value, page_size: pageSize.value })
    orders.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 时间只显示日期部分
function fmtTime(row, column, value) {
  return value ? String(value).slice(0, 19) : '-'
}

function statusType(status) {
  const map = {
    delivered: 'success',
    shipped: 'primary',
    canceled: 'danger',
    processing: 'warning',
    approved: 'info',
    invoiced: 'info',
    created: 'info',
    unavailable: 'info',
  }
  return map[status] || 'info'
}

onMounted(load)
</script>
