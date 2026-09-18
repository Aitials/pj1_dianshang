<template>
  <div>
    <div class="page-title">
      <el-icon><Odometer /></el-icon>
      <span>经营总览</span>
    </div>

    <!-- 指标卡 -->
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
  getOnTimeRate,
  getSalesTrend,
  getCategoryRanking,
  getSellerRanking,
  getProductsRanking,
} from '../api/dashboard'

const overview = ref({})
const onTimeRate = ref(0)

const deliveredRate = computed(() => {
  const total = overview.value.total_orders
  const delivered = overview.value.delivered_orders
  if (!total || delivered === undefined) return '-'
  return ((delivered / total) * 100).toFixed(1) + '%'
})

const cards = computed(() => [
  { label: '销售额 (R$)', value: formatMoney(overview.value.total_sales), icon: 'Money', bg: '#eff6ff', color: '#2563eb' },
  { label: '订单量', value: formatNumber(overview.value.total_orders), icon: 'List', bg: '#ecfdf5', color: '#10b981' },
  { label: '已送达', value: formatNumber(overview.value.delivered_orders), icon: 'CircleCheck', bg: '#f0f9ff', color: '#0ea5e9' },
  { label: '已取消', value: formatNumber(overview.value.canceled_orders), icon: 'CircleClose', bg: '#fef2f2', color: '#ef4444' },
  { label: '准时率', value: onTimeRate.value ? onTimeRate.value + '%' : '-', icon: 'Clock', bg: '#ecfeff', color: '#06b6d4' },
  { label: '已送达率', value: deliveredRate.value, icon: 'DataLine', bg: '#f5f3ff', color: '#8b5cf6' },
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
  const [ov, rate] = await Promise.all([getOverview(), getOnTimeRate()])
  overview.value = ov
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

// 商品 ID 太长，展示时截断，tooltip 显示完整
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
