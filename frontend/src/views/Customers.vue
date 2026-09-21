<template>
  <div>
    <div class="page-title">
      <el-icon><User /></el-icon>
      <span>客户分析</span>
    </div>
    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 消费排行 -->
        <el-tab-pane label="消费排行" name="ranking">
          <div class="chart-title">客户消费额 Top 10</div>
          <div ref="rankChartRef" style="height: 460px"></div>
        </el-tab-pane>

        <!-- 复购分析 -->
        <el-tab-pane label="复购分析" name="repurchase">
          <el-row :gutter="16" style="margin-bottom: 16px">
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-label">总购买客户数</div>
                <div class="stat-value">{{ formatNumber(repurchase.total_customers) }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-label">复购客户数</div>
                <div class="stat-value">{{ formatNumber(repurchase.repeat_customers) }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-label">复购率</div>
                <div class="stat-value">{{ repurchase.repurchase_rate ?? '-' }}%</div>
              </el-card>
            </el-col>
          </el-row>
          <div ref="repurchaseChartRef" style="height: 360px"></div>
        </el-tab-pane>

        <!-- 地域分布 -->
        <el-tab-pane label="地域分布" name="geo">
          <div class="chart-title">各州客户分布</div>
          <div ref="geoChartRef" style="height: 500px"></div>
        </el-tab-pane>

        <!-- 客户列表 -->
        <el-tab-pane label="客户列表" name="list">
          <div class="filter-bar">
            <el-input v-model="filters.customer_city" placeholder="按城市筛选" clearable style="width: 180px" @keyup.enter="search" />
            <el-select v-model="filters.customer_state" placeholder="按州筛选" clearable style="width: 160px" @change="search">
              <el-option v-for="s in states" :key="s" :label="s" :value="s" />
            </el-select>
            <el-button type="primary" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <el-table :data="customers" v-loading="loading" stripe>
            <el-table-column prop="customer_id" label="客户ID" width="230" show-overflow-tooltip />
            <el-table-column prop="customer_unique_id" label="唯一客户ID" width="230" show-overflow-tooltip />
            <el-table-column prop="customer_zip_code_prefix" label="邮编" width="100" />
            <el-table-column prop="customer_city" label="城市" />
            <el-table-column prop="customer_state" label="州" width="80" />
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
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getCustomers, getCustomerStates, getCustomerRanking, getCustomerRepurchase, getCustomerGeo } from '../api/customers'

const router = useRouter()

const activeTab = ref('ranking')

// 客户列表
const customers = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const filters = reactive({ customer_city: '', customer_state: '' })

// 州下拉选项
const states = ref([])
async function loadStates() {
  const res = await getCustomerStates()
  states.value = res.states || []
}

async function load() {
  loading.value = true
  try {
    const res = await getCustomers({
      page: page.value,
      page_size: pageSize.value,
      customer_city: filters.customer_city || undefined,
      customer_state: filters.customer_state || undefined,
    })
    customers.value = res.items
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
  filters.customer_city = ''
  filters.customer_state = ''
  search()
}

function goDetail(row) {
  router.push(`/customers/${row.customer_id}`)
}

function formatNumber(n) {
  if (n === undefined || n === null) return '-'
  return Number(n).toLocaleString('zh-CN')
}

// 消费排行
const rankChartRef = ref(null)
let rankChart = null
async function loadRanking() {
  const res = await getCustomerRanking(10)
  const list = res.customer_rank || []
  rankChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 150, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', name: '消费额' },
    yAxis: {
      type: 'category',
      data: list.map((i) => (i.customer_unique_id.length > 12 ? i.customer_unique_id.slice(0, 12) + '…' : i.customer_unique_id)),
    },
    series: [
      { name: '消费额', type: 'bar', data: list.map((i) => i.sales), itemStyle: { color: '#2563eb', borderRadius: [0, 4, 4, 0] } },
    ],
  })
}

// 复购分析
const repurchase = ref({})
const repurchaseChartRef = ref(null)
let repurchaseChart = null
async function loadRepurchase() {
  const res = await getCustomerRepurchase()
  repurchase.value = res
  const nonRepeat = (res.total_customers || 0) - (res.repeat_customers || 0)
  repurchaseChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [
      {
        name: '客户构成',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        data: [
          { name: '复购客户', value: res.repeat_customers || 0, itemStyle: { color: '#2563eb' } },
          { name: '非复购客户', value: nonRepeat, itemStyle: { color: '#e2e8f0' } },
        ],
        label: { formatter: '{b}: {c}' },
      },
    ],
  })
}

// 地域分布
const geoChartRef = ref(null)
let geoChart = null
async function loadGeo() {
  const res = await getCustomerGeo()
  // 按州聚合客户数
  const byState = {}
  for (const item of res.items || []) {
    if (!item.state) continue
    byState[item.state] = (byState[item.state] || 0) + (item.customer_count || 0)
  }
  const sorted = Object.entries(byState)
    .map(([state, count]) => ({ state, count }))
    .sort((a, b) => b.count - a.count)
  geoChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 70, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', name: '客户数' },
    yAxis: { type: 'category', data: sorted.map((i) => i.state) },
    series: [
      { name: '客户数', type: 'bar', data: sorted.map((i) => i.count), itemStyle: { color: '#10b981', borderRadius: [0, 4, 4, 0] } },
    ],
  })
}

// 切到对应 tab 时才初始化图表（隐藏容器里 init 会宽高为 0）
async function onTabChange(name) {
  await nextTick()
  if (name === 'ranking' && !rankChart) {
    rankChart = echarts.init(rankChartRef.value)
    loadRanking()
  } else if (name === 'repurchase' && !repurchaseChart) {
    repurchaseChart = echarts.init(repurchaseChartRef.value)
    loadRepurchase()
  } else if (name === 'geo' && !geoChart) {
    geoChart = echarts.init(geoChartRef.value)
    loadGeo()
  }
}

onMounted(async () => {
  load()
  loadStates()
  // 默认 tab 是消费排行，页面加载时就初始化图表
  await nextTick()
  rankChart = echarts.init(rankChartRef.value)
  loadRanking()
})

onBeforeUnmount(() => {
  rankChart?.dispose()
  repurchaseChart?.dispose()
  geoChart?.dispose()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
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
.stat-card {
  text-align: center;
}
.stat-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}
.stat-value {
  color: #0f172a;
  font-size: 26px;
  font-weight: 700;
}
</style>
