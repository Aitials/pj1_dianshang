<template>
  <div>
    <div class="page-title">
      <el-icon><Goods /></el-icon>
      <span>商品与类目</span>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 商品列表 -->
        <el-tab-pane label="商品列表" name="list">
          <div class="filter-bar">
            <el-input
              v-model="filters.product_category_name"
              placeholder="按类目名筛选"
              clearable
              style="width: 220px"
              @keyup.enter="search"
            />
            <el-button type="primary" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <el-table :data="products" v-loading="loading" stripe>
            <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
            <el-table-column prop="product_category_name" label="类目" width="170" />
            <el-table-column prop="product_name_length" label="名称长度" />
            <el-table-column prop="product_description_length" label="描述长度" />
            <el-table-column prop="product_photos_qty" label="照片数" />
            <el-table-column prop="product_weight_g" label="重量(g)" />
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

        <!-- 类目分析 -->
        <el-tab-pane label="类目分析" name="category">
          <div class="chart-title" style="margin-bottom: 12px">类目销售额 Top 10</div>
          <div ref="categoryChartRef" style="height: 380px"></div>
          <el-table :data="categoryAnalysis" v-loading="categoryLoading" stripe style="margin-top: 16px">
            <el-table-column prop="category_name" label="类目" />
            <el-table-column prop="sales" label="销售额" />
            <el-table-column prop="order_count" label="订单量" />
            <el-table-column prop="avg_price" label="平均单价" />
          </el-table>
        </el-tab-pane>

        <!-- 评分排行 -->
        <el-tab-pane label="商品评分排行" name="rating">
          <div class="filter-bar">
            <el-radio-group v-model="ratingOrder" @change="loadRating">
              <el-radio-button value="desc">高分在前</el-radio-button>
              <el-radio-button value="asc">低分在前</el-radio-button>
            </el-radio-group>
            <span class="tip">最少评论数</span>
            <el-input-number v-model="minReviews" :min="1" :max="500" @change="loadRating" style="width: 130px" />
            <el-button type="primary" @click="loadRating">刷新</el-button>
          </div>
          <el-table :data="ratingRank" v-loading="ratingLoading" stripe>
            <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
            <el-table-column prop="avg_score" label="平均评分" width="120" />
            <el-table-column prop="review_count" label="评论数" width="120" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getProducts, getCategoryAnalysis, getRatingRank } from '../api/products'

const router = useRouter()

const activeTab = ref('list')

// 商品列表
const products = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const filters = reactive({ product_category_name: '' })

async function load() {
  loading.value = true
  try {
    const res = await getProducts({
      page: page.value,
      page_size: pageSize.value,
      product_category_name: filters.product_category_name || undefined,
    })
    products.value = res.items
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
  filters.product_category_name = ''
  search()
}

function goDetail(row) {
  router.push(`/products/${row.product_id}`)
}

// 类目分析
const categoryAnalysis = ref([])
const categoryLoading = ref(false)
const categoryChartRef = ref(null)
let categoryChart = null

async function loadCategory() {
  categoryLoading.value = true
  try {
    const res = await getCategoryAnalysis(10)
    categoryAnalysis.value = res.category_analysis
    renderCategoryChart(res.category_analysis)
  } finally {
    categoryLoading.value = false
  }
}

function renderCategoryChart(data) {
  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 150, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: data.map((i) => i.category_name) },
    series: [
      { name: '销售额', type: 'bar', data: data.map((i) => i.sales), itemStyle: { color: '#2563eb', borderRadius: [0, 4, 4, 0] } },
    ],
  })
}

// 评分排行
const ratingRank = ref([])
const ratingLoading = ref(false)
const ratingOrder = ref('desc')
const minReviews = ref(10)

async function loadRating() {
  ratingLoading.value = true
  try {
    const res = await getRatingRank(20, ratingOrder.value, minReviews.value)
    ratingRank.value = res.rating_rank
  } finally {
    ratingLoading.value = false
  }
}

onMounted(async () => {
  load()
  categoryChart = echarts.init(categoryChartRef.value)
  await loadCategory()
  await loadRating()
})

onBeforeUnmount(() => {
  categoryChart?.dispose()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.tip {
  color: #64748b;
  font-size: 13px;
  margin-left: 8px;
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
}
</style>
