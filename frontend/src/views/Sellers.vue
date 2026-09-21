<template>
  <div>
    <div class="page-title">
      <el-icon><Shop /></el-icon>
      <span>卖家分析</span>
    </div>
    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 销售排行 -->
        <el-tab-pane label="销售排行" name="ranking">
          <div class="chart-title">卖家销售额 Top 10</div>
          <div ref="rankChartRef" style="height: 460px"></div>
        </el-tab-pane>

        <!-- 评分表现 -->
        <el-tab-pane label="评分表现" name="review">
          <div class="chart-title">卖家评分 vs 评论数（Top 20）</div>
          <div ref="reviewChartRef" style="height: 460px"></div>
        </el-tab-pane>

        <!-- 卖家列表 -->
        <el-tab-pane label="卖家列表" name="list">
          <div class="filter-bar">
            <el-input v-model="filters.seller_city" placeholder="按城市筛选" clearable style="width: 180px" @keyup.enter="search" />
            <el-select v-model="filters.seller_state" placeholder="按州筛选" clearable style="width: 160px" @change="search">
              <el-option v-for="s in states" :key="s" :label="s" :value="s" />
            </el-select>
            <el-button type="primary" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <el-table :data="sellers" v-loading="loading" stripe>
            <el-table-column prop="seller_id" label="卖家ID" width="230" show-overflow-tooltip />
            <el-table-column prop="seller_zip_code_prefix" label="邮编" width="100" />
            <el-table-column prop="seller_city" label="城市" />
            <el-table-column prop="seller_state" label="州" width="80" />
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
import { getSellers, getSellerStates, getSellerRank, getSellerReview } from '../api/sellers'

const router = useRouter()

const activeTab = ref('ranking')

// 卖家列表
const sellers = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const filters = reactive({ seller_city: '', seller_state: '' })

// 州下拉选项
const states = ref([])
async function loadStates() {
  const res = await getSellerStates()
  states.value = res.states || []
}

async function load() {
  loading.value = true
  try {
    const res = await getSellers({
      page: page.value,
      page_size: pageSize.value,
      seller_city: filters.seller_city || undefined,
      seller_state: filters.seller_state || undefined,
    })
    sellers.value = res.items
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
  filters.seller_city = ''
  filters.seller_state = ''
  search()
}

function goDetail(row) {
  router.push(`/sellers/${row.seller_id}`)
}

// 销售排行
const rankChartRef = ref(null)
let rankChart = null
async function loadRanking() {
  const res = await getSellerRank(10)
  const list = res.rank || []
  rankChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 150, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', name: '销售额' },
    yAxis: {
      type: 'category',
      data: list.map((i) => (i.seller_id.length > 12 ? i.seller_id.slice(0, 12) + '…' : i.seller_id)),
    },
    series: [
      { name: '销售额', type: 'bar', data: list.map((i) => i.sales), itemStyle: { color: '#10b981', borderRadius: [0, 4, 4, 0] } },
    ],
  })
}

// 评分表现（散点图：评分 × 评论数）
const reviewChartRef = ref(null)
let reviewChart = null
async function loadReview() {
  const res = await getSellerReview(20)
  const list = res.review_rank || []
  reviewChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => `卖家: ${p.data.seller_id}<br/>评分: ${p.data.value[1]}<br/>评论数: ${p.data.value[0]}`,
    },
    grid: { left: 60, right: 40, top: 30, bottom: 50 },
    xAxis: { type: 'value', name: '评论数' },
    yAxis: { type: 'value', name: '平均评分', min: 0, max: 5 },
    series: [
      {
        type: 'scatter',
        data: list.map((i) => ({
          seller_id: i.seller_id,
          value: [i.review_count, i.avg_score],
        })),
        symbolSize: 12,
        itemStyle: { color: '#f59e0b' },
      },
    ],
  })
}

// 切到对应 tab 时才初始化图表
async function onTabChange(name) {
  await nextTick()
  if (name === 'ranking' && !rankChart) {
    rankChart = echarts.init(rankChartRef.value)
    loadRanking()
  } else if (name === 'review' && !reviewChart) {
    reviewChart = echarts.init(reviewChartRef.value)
    loadReview()
  }
}

onMounted(async () => {
  load()
  loadStates()
  // 默认 tab 是销售排行，页面加载时就初始化图表
  await nextTick()
  rankChart = echarts.init(rankChartRef.value)
  loadRanking()
})

onBeforeUnmount(() => {
  rankChart?.dispose()
  reviewChart?.dispose()
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
</style>
