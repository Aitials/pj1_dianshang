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
      <div class="chart-title">各州物流表现（按订单量排序）</div>
      <el-table :data="geo" v-loading="geoLoading" stripe>
        <el-table-column prop="state" label="州" width="100" />
        <el-table-column prop="order_count" label="订单量" />
        <el-table-column prop="avg_fulfillment_days" label="平均履约天数" />
        <el-table-column prop="delay_rate" label="延迟率" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getLogisticsOverview, getLogisticsGeo, getDelayRating } from '../api/logistics'

const data = ref({})
const geo = ref([])
const geoLoading = ref(false)

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
  geoLoading.value = true
  try {
    const res = await getLogisticsGeo()
    geo.value = res.geo
  } finally {
    geoLoading.value = false
  }
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
  await Promise.all([loadOverview(), loadGeo(), loadRatingCompare()])
})

onBeforeUnmount(() => {
  ratingChart?.dispose()
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
