<template>
  <div>
    <div class="page-title">
      <el-icon><Shop /></el-icon>
      <span>卖家分析</span>
    </div>
    <el-card>
      <div class="filter-bar">
        <el-input v-model="filters.seller_city" placeholder="按城市筛选" clearable style="width: 180px" @keyup.enter="search" />
        <el-input v-model="filters.seller_state" placeholder="按州筛选（如 SP）" clearable style="width: 180px" @keyup.enter="search" />
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
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getSellers } from '../api/sellers'

const router = useRouter()

const sellers = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const filters = reactive({ seller_city: '', seller_state: '' })

async function load() {
  loading.value = true
  try {
    const res = await getSellers({
      page: page.value,
      page_size: pageSize.value,
      seller_city: filters.seller_city || undefined,
      seller_state: filters.seller_state || undefined,
    })
    sellers.value = res.sellers
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
