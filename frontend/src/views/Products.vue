<template>
  <div>
    <div class="page-title">
      <el-icon><Goods /></el-icon>
      <span>商品与类目</span>
    </div>
    <el-card>
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
        <el-table-column prop="product_category_name" label="类目" width="160" />
        <el-table-column prop="product_name_length" label="名称长度" />
        <el-table-column prop="product_description_length" label="描述长度" />
        <el-table-column prop="product_photos_qty" label="照片数" />
        <el-table-column prop="product_weight_g" label="重量(g)" />
        <el-table-column prop="product_length_cm" label="长(cm)" />
        <el-table-column prop="product_height_cm" label="高(cm)" />
        <el-table-column prop="product_width_cm" label="宽(cm)" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getProducts } from '../api/products'

const products = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getProducts()
    products.value = res.products
  } finally {
    loading.value = false
  }
})
</script>
