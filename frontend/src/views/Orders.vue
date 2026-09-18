<template>
  <div>
    <div class="page-title">
      <el-icon><List /></el-icon>
      <span>订单管理</span>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-select v-model="filters.order_status" placeholder="订单状态" clearable style="width: 160px">
          <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          start-placeholder="下单开始日期"
          end-placeholder="下单结束日期"
          style="width: 280px"
        />
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

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
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="goDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="load"
          @size-change="search"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getOrders } from '../api/orders'

const router = useRouter()

const statusOptions = ['created', 'approved', 'invoiced', 'processing', 'shipped', 'delivered', 'canceled', 'unavailable']

const orders = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const filters = reactive({ order_status: '' })
const dateRange = ref([])

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      order_status: filters.order_status || undefined,
      start_time: dateRange.value?.[0] || undefined,
      end_time: dateRange.value?.[1] || undefined,
    }
    const res = await getOrders(params)
    orders.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}

function reset() {
  filters.order_status = ''
  dateRange.value = []
  search()
}

function goDetail(row) {
  router.push(`/orders/${row.order_id}`)
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

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
</style>
