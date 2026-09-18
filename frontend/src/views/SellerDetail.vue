<template>
  <div v-loading="loading">
    <div class="page-title">
      <el-icon><Shop /></el-icon>
      <span>卖家详情</span>
      <el-button link type="primary" class="back-btn" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>
    <el-card>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="卖家ID" :span="2">{{ detail.seller_id }}</el-descriptions-item>
        <el-descriptions-item label="邮编">{{ detail.seller_zip_code_prefix }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ detail.seller_city }}</el-descriptions-item>
        <el-descriptions-item label="州">{{ detail.seller_state }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSellerDetail } from '../api/sellers'

const route = useRoute()
const router = useRouter()

const detail = ref({})
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    detail.value = await getSellerDetail(route.params.id)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.back-btn {
  margin-left: auto;
}
</style>
