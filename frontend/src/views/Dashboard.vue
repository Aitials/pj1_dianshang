<template>
  <div>
    <div class="page-title">
      <el-icon><Odometer /></el-icon>
      <span>经营总览</span>
    </div>

    <!-- 核心指标卡 -->
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="4">
        <el-card class="metric-card">
          <div class="metric-body">
            <div class="metric-icon" :style="{ background: card.bg }">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div>
              <div class="metric-label">{{ card.label }}</div>
              <div class="metric-value">{{ card.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警区 -->
    <el-card class="alert-card">
      <div class="chart-title">经营预警</div>
      <div class="alert-list">
        <div class="alert-item">
          <div class="alert-icon" style="background: #fef2f2">
            <el-icon :size="22" color="#ef4444"><WarningFilled /></el-icon>
          </div>
          <div>
            <div class="alert-label">低库存商品</div>
            <div class="alert-value">{{ alerts.low_stock_count ?? '-' }} 个</div>
          </div>
        </div>
        <div class="alert-item">
          <div class="alert-icon" style="background: #fff7ed">
            <el-icon :size="22" color="#f59e0b"><Clock /></el-icon>
          </div>
          <div>
            <div class="alert-label">延迟订单</div>
            <div class="alert-value">{{ alerts.delayed_order_count ?? '-' }} 单</div>
          </div>
        </div>
        <div class="alert-item">
          <div class="alert-icon" style="background: #f5f3ff">
            <el-icon :size="22" color="#8b5cf6"><Star /></el-icon>
          </div>
          <div>
            <div class="alert-label">低评分卖家（&lt;3 分）</div>
            <div class="alert-value">{{ alerts.low_review_count ?? '-' }} 个</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 销售趋势 -->
    <el-card class="chart-card">
      <div class="chart-title">销售趋势（按月）</div>
      <div ref="trendChartRef" style="height: 350px"></div>
    </el-card>

    <!-- 排行 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">类目销售额 Top 10</div>
          <div ref="categoryChartRef" style="height: 420px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">卖家销售额 Top 10</div>
          <div ref="sellerChartRef" style="height: 420px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <div class="chart-title">商品销售额 Top 10</div>
      <div ref="productChartRef" style="height: 420px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import {
  getOverview,
  getAlerts,
  getOnTimeRate,
  getSalesTrend,
  getCategoryRanking,
  getSellerRanking,
  getProductsRanking,
} from '../api/dashboard'

const overview = ref({})
const alerts = ref({})
const onTimeRate = ref(0)

const cards = computed(() => [
  { label: '销售额 (R$)', value: formatMoney(overview.value.total_sales), icon: 'Money', bg: '#eff6ff', color: '#2563eb' },
  { label: '订单量', value: formatNumber(overview.value.total_orders), icon: 'List', bg: '#ecfdf5', color: '#10b981' },
  { label: '客单价 (R$)', value: formatMoney(overview.value.average_order_value), icon: 'Coin', bg: '#fff7ed', color: '#f59e0b' },
  { label: '客户数', value: formatNumber(overview.value.customer_count), icon: 'User', bg: '#f5f3ff', color: '#8b5cf6' },
  { label: '平均评分', value: overview.value.avg_review_score ?? '-', icon: 'Star', bg: '#fffbeb', color: '#f59e0b' },
  { label: '准时率', value: onTimeRate.value ? onTimeRate.value + '%' : '-', icon: 'Clock', bg: '#ecfeff', color: '#06b6d4' },
])

const trendChartRef = ref(null)
const categoryChartRef = ref(null)
const sellerChartRef = ref(null)
const productChartRef = ref(null)
let trendChart = null
let categoryChart = null
let sellerChart = null
let productChart = null

function formatNumber(n) {
  if (n === undefined || n === null) return '-'
  return Number(n).toLocaleString('zh-CN')
}
function formatMoney(n) {
  if (n === undefined || n === null) return '-'
  return Number(n).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

async function loadOverview() {
  const [ov, al, rate] = await Promise.all([getOverview(), getAlerts(), getOnTimeRate()])
  overview.value = ov
  alerts.value = al
  onTimeRate.value = rate.send_time_rate ?? 0
}

async function loadTrend() {
  const res = await getSalesTrend()
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 70, right: 30, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: res.trend.map((i) => i.month) },
    yAxis: { type: 'value' },
    series: [
      {
        name: '销售额',
        type: 'line',
        data: res.trend.map((i) => i.sales),
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#2563eb' },
      },
    ],
  })
}

function buildBarOption(names, values, color) {
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 150, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: names },
    series: [{ name: '销售额', type: 'bar', data: values, itemStyle: { color, borderRadius: [0, 4, 4, 0] } }],
  }
}

function shortId(id) {
  return id && id.length > 12 ? id.slice(0, 12) + '…' : id
}

async function loadRankings() {
  const [cat, seller, product] = await Promise.all([
    getCategoryRanking(10),
    getSellerRanking(10),
    getProductsRanking(10),
  ])
  categoryChart.setOption(
    buildBarOption(
      cat.category_ranking.map((i) => i.category_name),
      cat.category_ranking.map((i) => i.sales),
      '#2563eb'
    )
  )
  sellerChart.setOption(
    buildBarOption(
      seller.seller_ranking.map((i) => i.seller_id),
      seller.seller_ranking.map((i) => i.sales),
      '#10b981'
    )
  )
  productChart.setOption(
    buildBarOption(
      product.product_ranking.map((i) => shortId(i.product_id)),
      product.product_ranking.map((i) => i.sales),
      '#f59e0b'
    )
  )
}

onMounted(async () => {
  trendChart = echarts.init(trendChartRef.value)
  categoryChart = echarts.init(categoryChartRef.value)
  sellerChart = echarts.init(sellerChartRef.value)
  productChart = echarts.init(productChartRef.value)
  await Promise.all([loadOverview(), loadTrend(), loadRankings()])
})

onBeforeUnmount(() => {
  trendChart?.dispose()
  categoryChart?.dispose()
  sellerChart?.dispose()
  productChart?.dispose()
})
</script>

<style scoped>
.metric-card {
  margin-bottom: 16px;
}
.metric-body {
  display: flex;
  align-items: center;
  gap: 12px;
}
.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.metric-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 4px;
}
.metric-value {
  color: #0f172a;
  font-size: 22px;
  font-weight: 700;
}
.alert-card {
  margin-bottom: 16px;
}
.alert-list {
  display: flex;
  gap: 24px;
}
.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.alert-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.alert-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 2px;
}
.alert-value {
  color: #0f172a;
  font-size: 18px;
  font-weight: 600;
}
.chart-card {
  margin-bottom: 16px;
}
.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
}
</style>
