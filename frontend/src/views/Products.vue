<template>
  <div>
    <div class="page-title">
      <el-icon><Goods /></el-icon>
      <span>商品与类目</span>
    </div>
    <el-card>
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
        <el-table-column prop="product_length_cm" label="长(cm)" />
        <el-table-column prop="product_height_cm" label="高(cm)" />
        <el-table-column prop="product_width_cm" label="宽(cm)" />
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
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '../api/products'

const router = useRouter()

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

onMounted(load)
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
</style>
