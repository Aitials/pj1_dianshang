<template>
  <div>
    <div class="page-title">
      <el-icon><Shop /></el-icon>
      <span>卖家分析</span>
    </div>
    <el-card>
      <el-table :data="sellers" v-loading="loading" stripe>
        <el-table-column prop="seller_id" label="卖家ID" width="230" show-overflow-tooltip />
        <el-table-column prop="seller_zip_code_prefix" label="邮编" width="100" />
        <el-table-column prop="seller_city" label="城市" />
        <el-table-column prop="seller_state" label="州" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getSellers } from '../api/sellers'

const sellers = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getSellers()
    sellers.value = res.sellers
  } finally {
    loading.value = false
  }
})
</script>
