<template>
  <div>
    <div class="page-title">
      <el-icon><Van /></el-icon>
      <span>物流分析</span>
    </div>
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="4">
        <el-card class="metric-card">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getLogisticsOverview } from '../api/logistics'

const data = ref({})

const cards = computed(() => [
  { label: '平均履约时长(天)', value: data.value.avg_delivery_days ?? '-' },
  { label: '准时率', value: data.value.on_time_rate ? data.value.on_time_rate + '%' : '-' },
  { label: '延迟率', value: data.value.delay_rate ? data.value.delay_rate + '%' : '-' },
  { label: '已送达订单', value: data.value.total_delivered ?? '-' },
  { label: '准时订单', value: data.value.on_time_count ?? '-' },
  { label: '延迟订单', value: data.value.delayed_count ?? '-' },
])

onMounted(async () => {
  data.value = await getLogisticsOverview()
})
</script>

<style scoped>
.metric-card {
  text-align: center;
  margin-bottom: 16px;
}
.metric-label {
  color: #909399;
  font-size: 13px;
  margin-bottom: 8px;
}
.metric-value {
  color: #303133;
  font-size: 22px;
  font-weight: bold;
}
</style>
