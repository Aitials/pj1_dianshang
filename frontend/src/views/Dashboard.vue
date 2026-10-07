<template>
  <div>
    <div class="page-title">
      <el-icon><Odometer /></el-icon>
      <span>经营总览</span>
    </div>

    <!-- 核心指标卡：整卡可点，跳到对应明细模块（没权限的模块不显示跳转提示） -->
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="4">
        <el-card
          class="metric-card"
          :class="{ clickable: canAccess(card.path) }"
          @click="go(card.path)"
        >
          <div class="metric-body">
            <div class="metric-icon" :style="{ background: card.bg }">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div>
              <div class="metric-label">{{ card.label }}</div>
              <div class="metric-value">{{ card.value }}</div>
            </div>
          </div>
          <div class="card-more" v-if="canAccess(card.path)">
            查看明细
            <el-icon><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警区：每一项可点，跳到对应模块 -->
    <el-card class="alert-card">
      <div class="chart-title">经营预警</div>
      <div class="alert-list">
        <div
          v-for="a in alertItems"
          :key="a.label"
          class="alert-item"
          :class="{ clickable: canAccess(a.path) }"
          @click="go(a.path)"
        >
          <div class="alert-icon" :style="{ background: a.bg }">
            <el-icon :size="22" :color="a.color"><component :is="a.icon" /></el-icon>
          </div>
          <div>
            <div class="alert-label">{{ a.label }}</div>
            <div class="alert-value">{{ a.value }}</div>
          </div>
          <el-icon class="alert-arrow" v-if="canAccess(a.path)"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- 销售趋势 -->
    <el-card class="chart-card">
      <div class="chart-title">
        <span>销售趋势（按月）</span>
        <span class="chart-more" v-if="canAccess('/orders')" @click="go('/orders')">
          查看订单明细
          <el-icon><ArrowRight /></el-icon>
        </span>
      </div>
      <div ref="trendChartRef" style="height: 350px"></div>
    </el-card>

    <!-- 排行 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">
            <span>类目销售额 Top 10</span>
            <span class="chart-more" v-if="canAccess('/products')" @click="go('/products')">
              查看类目分析
              <el-icon><ArrowRight /></el-icon>
            </span>
          </div>
          <div ref="categoryChartRef" style="height: 420px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">
            <span>卖家销售额 Top 10</span>
            <span class="chart-hint" v-if="canAccess('/sellers')">点柱子查看卖家详情</span>
          </div>
          <div ref="sellerChartRef" style="height: 420px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <div class="chart-title">
        <span>商品销售额 Top 10</span>
        <span class="chart-hint" v-if="canAccess('/products')">点柱子查看商品详情</span>
      </div>
      <div ref="productChartRef" style="height: 420px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { ROLE_MENUS } from '../stores/auth'
import {
  getOverview,
  getAlerts,
  getOnTimeRate,
  getSalesTrend,
  getCategoryRanking,
  getSellerRanking,
  getProductsRanking,
} from '../api/dashboard'

const router = useRouter()

// 当前角色可访问的模块白名单（与路由守卫、后端 RBAC 是同一份）
// 用来决定看板上的卡片/预警项是否做成可点击 —— 没权限的点了也会被守卫弹回去
const allowedMenus = ROLE_MENUS[localStorage.getItem('role')] || []

function canAccess(path) {
  if (!path) return false
  // 详情页（/orders/xxx）也算所属模块可访问
  return allowedMenus.some((p) => path === p || path.startsWith(p + '/'))
}

function go(path) {
  if (!path) return
  if (!canAccess(path)) {
    ElMessage.warning('没有访问该模块的权限')
    return
  }
  router.push(path)
}

const overview = ref({})
const alerts = ref({})
const onTimeRate = ref(0)

// 指标卡：path 是点击后要跳的模块
const cards = computed(() => [
  { label: '销售额 (R$)', value: formatMoney(overview.value.total_sales), icon: 'Money', bg: '#eff6ff', color: '#2563eb', path: '/orders' },
  { label: '订单量', value: formatNumber(overview.value.total_orders), icon: 'List', bg: '#ecfdf5', color: '#10b981', path: '/orders' },
  { label: '客单价 (R$)', value: formatMoney(overview.value.average_order_value), icon: 'Coin', bg: '#fff7ed', color: '#f59e0b', path: '/orders' },
  { label: '客户数', value: formatNumber(overview.value.customer_count), icon: 'User', bg: '#f5f3ff', color: '#8b5cf6', path: '/customers' },
  { label: '平均评分', value: overview.value.avg_review_score ?? '-', icon: 'Star', bg: '#fffbeb', color: '#f59e0b', path: '/orders' },
  { label: '准时率', value: onTimeRate.value ? onTimeRate.value + '%' : '-', icon: 'Clock', bg: '#ecfeff', color: '#06b6d4', path: '/logistics' },
])

// 预警项：同样带上要跳转的模块
const alertItems = computed(() => [
  { label: '低库存商品', value: `${alerts.value.low_stock_count ?? '-'} 个`, icon: 'WarningFilled', bg: '#fef2f2', color: '#ef4444', path: '/inventory' },
  { label: '延迟订单', value: `${alerts.value.delayed_order_count ?? '-'} 单`, icon: 'Clock', bg: '#fff7ed', color: '#f59e0b', path: '/logistics' },
  { label: '低评分卖家（<3 分）', value: `${alerts.value.low_review_count ?? '-'} 个`, icon: 'Star', bg: '#f5f3ff', color: '#8b5cf6', path: '/sellers' },
])

const trendChartRef = ref(null)
const categoryChartRef = ref(null)
const sellerChartRef = ref(null)
const productChartRef = ref(null)
let trendChart = null
let categoryChart = null
let sellerChart = null
let productChart = null

// 图表上显示的名字可能被截断过（shortId），点击柱子要用原始 id，
// 所以把排行榜按图表顺序另存一份，click 回调里用 dataIndex 取
const sellerIds = ref([])
const productIds = ref([])

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

// clickable=true 时把鼠标改成手型，暗示"这根柱子可以点"
function buildBarOption(names, values, color, clickable = false) {
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 150, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: names },
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: values,
        cursor: clickable ? 'pointer' : 'default',
        itemStyle: { color, borderRadius: [0, 4, 4, 0] },
      },
    ],
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
  // 存一份原始 id，供柱子点击时拼详情页地址
  sellerIds.value = seller.seller_ranking.map((i) => i.seller_id)
  productIds.value = product.product_ranking.map((i) => i.product_id)

  sellerChart.setOption(
    buildBarOption(
      seller.seller_ranking.map((i) => i.seller_id),
      seller.seller_ranking.map((i) => i.sales),
      '#10b981',
      true
    )
  )
  productChart.setOption(
    buildBarOption(
      product.product_ranking.map((i) => shortId(i.product_id)),
      product.product_ranking.map((i) => i.sales),
      '#f59e0b',
      true
    )
  )
}

onMounted(async () => {
  trendChart = echarts.init(trendChartRef.value)
  categoryChart = echarts.init(categoryChartRef.value)
  sellerChart = echarts.init(sellerChartRef.value)
  productChart = echarts.init(productChartRef.value)

  // 点柱子 → 对应详情页。
  // 类目图不做点击：类目没有详情路由（/products/:id 是商品详情），
  // 所以类目只保留标题上的「查看类目分析」入口。
  sellerChart.on('click', (p) => {
    const id = sellerIds.value[p.dataIndex]
    if (id) go(`/sellers/${id}`)
  })
  productChart.on('click', (p) => {
    const id = productIds.value[p.dataIndex]
    if (id) go(`/products/${id}`)
  })

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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
}

/* ---- 可点击跳转的交互提示 ---- */

/* 指标卡 / 预警项：只有能跳转的才给手型和悬停反馈 */
.metric-card.clickable,
.alert-item.clickable {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12);
}
.alert-item.clickable:hover {
  background: #f8fafc;
}

/* 指标卡底部的「查看明细」 */
.card-more {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 2px;
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}
.metric-card.clickable:hover .card-more {
  color: #2563eb;
}

/* 预警项右侧的小箭头 */
.alert-arrow {
  margin-left: auto;
  color: #cbd5e1;
}
.alert-item.clickable:hover .alert-arrow {
  color: #2563eb;
}

/* 图表标题右侧：能点的是蓝色链接，纯提示的是灰色小字 */
.chart-more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 400;
  color: #2563eb;
  cursor: pointer;
}
.chart-more:hover {
  text-decoration: underline;
}
.chart-hint {
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
}
</style>
