<template>
  <div v-loading="loading">
    <div class="page-title">
      <el-icon><Goods /></el-icon>
      <span>商品详情</span>
      <el-button link type="primary" class="back-btn" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>
    <el-card>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="商品ID" :span="2">{{ detail.product_id }}</el-descriptions-item>
        <el-descriptions-item label="类目">{{ detail.product_category_name }}</el-descriptions-item>
        <el-descriptions-item label="名称长度">{{ detail.product_name_length }}</el-descriptions-item>
        <el-descriptions-item label="描述长度">{{ detail.product_description_length }}</el-descriptions-item>
        <el-descriptions-item label="照片数">{{ detail.product_photos_qty }}</el-descriptions-item>
        <el-descriptions-item label="重量(g)">{{ detail.product_weight_g }}</el-descriptions-item>
        <el-descriptions-item label="长(cm)">{{ detail.product_length_cm }}</el-descriptions-item>
        <el-descriptions-item label="高(cm)">{{ detail.product_height_cm }}</el-descriptions-item>
        <el-descriptions-item label="宽(cm)">{{ detail.product_width_cm }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductDetail } from '../api/products'

const route = useRoute()
const router = useRouter()

const detail = ref({})
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    detail.value = await getProductDetail(route.params.id)
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
