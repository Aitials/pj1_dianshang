<template>
  <div>
    <div class="page-title">
      <el-icon><Van /></el-icon>
      <span>物流分析</span>
    </div>

    <!-- 核心指标 -->
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="4">
        <el-card class="metric-card">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 延迟与评分关联 -->
    <el-card class="section">
      <div class="chart-title">延迟 vs 准时 订单评分对比</div>
      <div ref="ratingChartRef" style="height: 320px"></div>
    </el-card>

    <!-- 地域分布 -->
    <el-card class="section">
      <div class="chart-title">各州物流表现（订单量 + 延迟率）</div>
      <div ref="geoChartRef" style="height: 380px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getLogisticsOverview, getLogisticsGeo, getDelayRating } from '../api/logistics'

const data = ref({})
const geoChartRef = ref(null)
let geoChart = null

const cards = computed(() => [
  { label: '平均履约时长(天)', value: data.value.avg_delivery_days ?? '-' },
  { label: '准时率', value: data.value.on_time_rate ? data.value.on_time_rate + '%' : '-' },
  { label: '延迟率', value: data.value.delay_rate ? data.value.delay_rate + '%' : '-' },
  { label: '已送达订单', value: data.value.total_delivered ?? '-' },
  { label: '准时订单', value: data.value.on_time_count ?? '-' },
  { label: '延迟订单', value: data.value.delayed_count ?? '-' },
])

const ratingChartRef = ref(null)
let ratingChart = null

async function loadOverview() {
  data.value = await getLogisticsOverview()
}

async function loadGeo() {
  const res = await getLogisticsGeo()
  const list = res.geo || []
  geoChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['订单量', '延迟率'], top: 0 },
    grid: { left: 60, right: 60, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: list.map((i) => i.state) },
    yAxis: [
      { type: 'value', name: '订单量' },
      { type: 'value', name: '延迟率(%)', max: 100 },
    ],
    series: [
      { name: '订单量', type: 'bar', data: list.map((i) => i.order_count), itemStyle: { color: '#2563eb' } },
      { name: '延迟率', type: 'line', yAxisIndex: 1, data: list.map((i) => i.delay_rate), itemStyle: { color: '#f59e0b' } },
    ],
  })
}

async function loadRatingCompare() {
  const res = await getDelayRating()
  ratingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 60, right: 30, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: ['准时订单', '延迟订单'] },
    yAxis: { type: 'value', name: '平均评分', min: 0, max: 5 },
    series: [
      {
        name: '平均评分',
        type: 'bar',
        data: [res.on_time_avg_score, res.delayed_avg_score],
        itemStyle: { color: '#2563eb', borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top' },
      },
    ],
  })
}

onMounted(async () => {
  ratingChart = echarts.init(ratingChartRef.value)
  geoChart = echarts.init(geoChartRef.value)
  await Promise.all([loadOverview(), loadGeo(), loadRatingCompare()])
})

onBeforeUnmount(() => {
  ratingChart?.dispose()
  geoChart?.dispose()
})
</script>

<style scoped>
.metric-card {
  text-align: center;
  margin-bottom: 16px;
}
.metric-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}
.metric-value {
  color: #0f172a;
  font-size: 22px;
  font-weight: 700;
}
.section {
  margin-bottom: 16px;
}
.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
}
</style>
