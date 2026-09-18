<template>
  <div v-loading="loading">
    <div class="page-title">
      <el-icon><List /></el-icon>
      <span>订单详情</span>
      <el-button link type="primary" class="back-btn" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-card class="section">
      <div class="section-title">订单信息</div>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="订单号" :span="2">{{ detail.order?.order_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(detail.order?.order_status)">{{ detail.order?.order_status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ fmtTime(detail.order?.order_purchase_timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="审批时间">{{ fmtTime(detail.order?.order_approved_at) }}</el-descriptions-item>
        <el-descriptions-item label="承运日期">{{ fmtTime(detail.order?.order_delivered_carrier_date) }}</el-descriptions-item>
        <el-descriptions-item label="实际送达">{{ fmtTime(detail.order?.order_delivered_customer_date) }}</el-descriptions-item>
        <el-descriptions-item label="预计送达">{{ fmtTime(detail.order?.order_estimated_delivery_date) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="section">
      <div class="section-title">客户信息</div>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="客户ID">{{ detail.customer?.customer_id }}</el-descriptions-item>
        <el-descriptions-item label="唯一客户ID">{{ detail.customer?.customer_unique_id }}</el-descriptions-item>
        <el-descriptions-item label="邮编">{{ detail.customer?.customer_zip_code_prefix }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ detail.customer?.customer_city }}</el-descriptions-item>
        <el-descriptions-item label="州">{{ detail.customer?.customer_state }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="section">
      <div class="section-title">商品明细</div>
      <el-table :data="detail.items || []" stripe>
        <el-table-column prop="order_item_id" label="明细ID" width="80" />
        <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
        <el-table-column prop="seller_id" label="卖家ID" width="230" show-overflow-tooltip />
        <el-table-column prop="price" label="单价" />
        <el-table-column prop="freight_value" label="运费" />
        <el-table-column label="发货期限" :formatter="fmtTime" prop="shipping_limit_date" />
      </el-table>
    </el-card>

    <el-card class="section">
      <div class="section-title">支付信息</div>
      <el-table :data="detail.payments || []" stripe>
        <el-table-column prop="payment_sequential" label="序号" width="80" />
        <el-table-column prop="payment_type" label="支付方式" />
        <el-table-column prop="payment_installments" label="分期数" />
        <el-table-column prop="payment_value" label="支付金额" />
      </el-table>
    </el-card>

    <el-card v-if="detail.reviews" class="section">
      <div class="section-title">订单评价</div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="评分">
          <el-rate :model-value="detail.reviews.review_score" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="评价标题">{{ detail.reviews.review_comment_title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="评价内容" :span="2">{{ detail.reviews.review_comment_message || '-' }}</el-descriptions-item>
        <el-descriptions-item label="评价时间">{{ fmtTime(detail.reviews.review_creation_date) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrderDetail } from '../api/orders'

const route = useRoute()
const router = useRouter()

const detail = ref({})
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    detail.value = await getOrderDetail(route.params.id)
  } finally {
    loading.value = false
  }
}

function fmtTime(value) {
  return value ? String(value).slice(0, 19) : '-'
}

function statusType(status) {
  const map = {
    delivered: 'success',
    shipped: 'primary',
    canceled: 'danger',
    processing: 'warning',
    approved: 'info',
    invoiced: 'info',
    created: 'info',
    unavailable: 'info',
  }
  return map[status] || 'info'
}

onMounted(load)
</script>

<style scoped>
.back-btn {
  margin-left: auto;
}
.section {
  margin-bottom: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
}
</style>
