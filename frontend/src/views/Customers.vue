<template>
  <div>
    <div class="page-title">
      <el-icon><User /></el-icon>
      <span>客户分析</span>
    </div>
    <el-card>
      <el-table :data="customers" v-loading="loading" stripe>
        <el-table-column prop="customer_id" label="客户ID" width="230" show-overflow-tooltip />
        <el-table-column prop="customer_unique_id" label="唯一客户ID" width="230" show-overflow-tooltip />
        <el-table-column prop="customer_zip_code_prefix" label="邮编" width="100" />
        <el-table-column prop="customer_city" label="城市" />
        <el-table-column prop="customer_state" label="州" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCustomers } from '../api/customers'

const customers = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getCustomers()
    customers.value = res.customers
  } finally {
    loading.value = false
  }
})
</script>
