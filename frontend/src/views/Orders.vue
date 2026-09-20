<template>
  <div>
    <div class="page-title">
      <el-icon><List /></el-icon>
      <span>订单管理</span>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 订单列表 -->
        <el-tab-pane label="订单列表" name="list">
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

          <div class="pagination">
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
        </el-tab-pane>

        <!-- 订单分析 -->
        <el-tab-pane label="订单分析" name="analysis">
          <el-row :gutter="16">
            <el-col :span="10">
              <div class="chart-title">订单状态分布</div>
              <div ref="statusChartRef" style="height: 360px"></div>
            </el-col>
            <el-col :span="14">
              <div class="chart-title">月度订单趋势（订单量 + 销售额）</div>
              <div ref="trendChartRef" style="height: 360px"></div>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getOrders, getOrderStatusDistribution, getOrderMonthlyTrend } from '../api/orders'

const router = useRouter()

const activeTab = ref('list')

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

// 状态颜色（环形图用）
const statusColor = {
  delivered: '#10b981',
  shipped: '#2563eb',
  canceled: '#ef4444',
  processing: '#f59e0b',
  approved: '#8b5cf6',
  invoiced: '#06b6d4',
  created: '#94a3b8',
  unavailable: '#cbd5e1',
}

// 订单状态分布
const statusChartRef = ref(null)
let statusChart = null
async function loadStatusDistribution() {
  const res = await getOrderStatusDistribution()
  const list = res.items || []
  statusChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        data: list.map((i) => ({ name: i.status, value: i.count, itemStyle: { color: statusColor[i.status] || '#94a3b8' } })),
        label: { formatter: '{b}: {c}' },
      },
    ],
  })
}

// 月度趋势（双轴：订单量柱 + 销售额线）
const trendChartRef = ref(null)
let trendChart = null
async function loadMonthlyTrend() {
  const res = await getOrderMonthlyTrend()
  const list = res.items || []
  trendChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['订单量', '销售额'], top: 0 },
    grid: { left: 60, right: 70, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: list.map((i) => i.month) },
    yAxis: [
      { type: 'value', name: '订单量' },
      { type: 'value', name: '销售额(R$)' },
    ],
    series: [
      { name: '订单量', type: 'bar', data: list.map((i) => i.order_count), itemStyle: { color: '#2563eb' } },
      { name: '销售额', type: 'line', yAxisIndex: 1, data: list.map((i) => i.sales), itemStyle: { color: '#f59e0b' } },
    ],
  })
}

async function onTabChange(name) {
  await nextTick()
  if (name === 'analysis' && !statusChart) {
    statusChart = echarts.init(statusChartRef.value)
    trendChart = echarts.init(trendChartRef.value)
    loadStatusDistribution()
    loadMonthlyTrend()
  }
}

onMounted(load)

onBeforeUnmount(() => {
  statusChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
}
</style>
