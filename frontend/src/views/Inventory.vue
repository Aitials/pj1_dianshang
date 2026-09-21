<template>
  <div>
    <div class="page-title">
      <el-icon><Box /></el-icon>
      <span>库存管理</span>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 库存台账 -->
        <el-tab-pane label="库存台账" name="list">
          <div class="filter-bar">
            <el-input v-model="searchProductId" placeholder="输入商品ID搜索" clearable style="width: 280px" @keyup.enter="searchInventory" />
            <el-button type="primary" @click="searchInventory">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </div>
          <el-table :data="inventory" v-loading="loading" stripe>
            <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
            <el-table-column prop="quantity" label="当前库存" width="120" />
            <el-table-column prop="safe_stock" label="安全库存" width="120" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="openAdjust(row)">调整</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              layout="total, prev, pager, next"
              @current-change="load"
            />
          </div>
        </el-tab-pane>

        <!-- 补货建议 -->
        <el-tab-pane label="补货建议" name="replenish">
          <div class="filter-bar">
            <span class="tip">补货周期（天）</span>
            <el-input-number v-model="replenishDays" :min="1" :max="365" style="width: 140px" />
            <el-button type="primary" @click="loadReplenish">刷新</el-button>
          </div>
          <el-table :data="replenish" v-loading="replenishLoading" stripe>
            <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
            <el-table-column prop="avg_daily_sales" label="日均销量" width="120" />
            <el-table-column prop="current_quantity" label="当前库存" width="120" />
            <el-table-column prop="safety_stock" label="安全库存" width="120" />
            <el-table-column prop="suggest_quantity" label="建议补货量" width="120">
              <template #default="{ row }">
                <el-tag :type="row.suggest_quantity > 0 ? 'warning' : 'success'">
                  {{ row.suggest_quantity }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 库存流水 -->
        <el-tab-pane label="库存流水" name="logs">
          <div class="filter-bar">
            <el-input v-model="logProductId" placeholder="输入商品ID" style="width: 280px" clearable />
            <el-button type="primary" @click="searchLogs">查询</el-button>
          </div>
          <el-table :data="logs" v-loading="logsLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="product_id" label="商品ID" width="230" show-overflow-tooltip />
            <el-table-column prop="change" label="变化量" width="90" />
            <el-table-column prop="before" label="调整前" width="90" />
            <el-table-column prop="after" label="调整后" width="90" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="operator" label="操作人" width="120" />
            <el-table-column label="时间" :formatter="fmtTime" prop="created_at" />
          </el-table>
          <div class="pagination">
            <el-pagination
              v-model:current-page="logPage"
              v-model:page-size="logPageSize"
              :total="logTotal"
              layout="total, prev, pager, next"
              @current-change="loadLogs"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 调整库存弹窗 -->
    <el-dialog v-model="showAdjust" title="调整库存" width="400px">
      <p style="margin-bottom: 16px">商品ID：{{ current.product_id }}</p>
      <el-form>
        <el-form-item label="变化量">
          <el-input-number v-model="adjustForm.change" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="adjustForm.reason" placeholder="如：采购入库 / 销售出库" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdjust = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust">提交</el-button>
      </template>
    </el-dialog>

    <!-- 商品查询结果弹窗 -->
    <el-dialog v-model="showSearchResult" title="商品库存信息" width="420px">
      <div v-if="searchResult" class="search-result">
        <div class="result-row"><span class="result-label">商品ID</span><span class="result-value">{{ searchResult.product_id }}</span></div>
        <div class="result-row"><span class="result-label">当前库存</span><span class="result-value">{{ searchResult.quantity }}</span></div>
        <div class="result-row"><span class="result-label">安全库存</span><span class="result-value">{{ searchResult.safe_stock }}</span></div>
      </div>
      <template #footer>
        <el-button @click="showSearchResult = false">关闭</el-button>
        <el-button type="primary" @click="adjustSearchResult">调整库存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventory, adjustInventory, getReplenish, getInventoryLogs, getInventoryDetail } from '../api/inventory'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('list')

// 库存台账
const inventory = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showAdjust = ref(false)
const current = ref({})
const adjustForm = reactive({ change: 0, reason: '' })

const searchProductId = ref('')
const showSearchResult = ref(false)
const searchResult = ref(null)
const searchLoading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await getInventory({
      page: page.value,
      page_size: pageSize.value,
    })
    inventory.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 按商品ID查询单个库存，命中则弹窗展示
async function searchInventory() {
  const id = searchProductId.value.trim()
  if (!id) {
    ElMessage.warning('请输入商品ID')
    return
  }
  searchLoading.value = true
  try {
    const res = await getInventoryDetail(id)
    if (res) {
      searchResult.value = res
      showSearchResult.value = true
    } else {
      searchResult.value = null
      showSearchResult.value = false
      ElMessage.warning('未找到该商品，请检查商品ID')
    }
  } finally {
    searchLoading.value = false
  }
}

function resetSearch() {
  searchProductId.value = ''
  searchResult.value = null
  showSearchResult.value = false
}

// 从查询结果弹窗直接打开调整
function adjustSearchResult() {
  showSearchResult.value = false
  openAdjust(searchResult.value)
}

function openAdjust(row) {
  current.value = row
  adjustForm.change = 0
  adjustForm.reason = ''
  showAdjust.value = true
}

async function submitAdjust() {
  await adjustInventory(current.value.product_id, {
    change: adjustForm.change,
    reason: adjustForm.reason,
    operator: authStore.username,
  })
  ElMessage.success('调整成功')
  showAdjust.value = false
  load()
}

// 补货建议
const replenish = ref([])
const replenishLoading = ref(false)
const replenishDays = ref(30)

async function loadReplenish() {
  replenishLoading.value = true
  try {
    const res = await getReplenish(replenishDays.value)
    replenish.value = res.items
  } finally {
    replenishLoading.value = false
  }
}

// 库存流水
const logs = ref([])
const logTotal = ref(0)
const logPage = ref(1)
const logPageSize = ref(10)
const logsLoading = ref(false)
const logProductId = ref('')

async function loadLogs() {
  if (!logProductId.value) {
    ElMessage.warning('请输入商品ID')
    return
  }
  logsLoading.value = true
  try {
    const res = await getInventoryLogs({
      product_id: logProductId.value,
      page: logPage.value,
      page_size: logPageSize.value,
    })
    logs.value = res.items
    logTotal.value = res.total
  } finally {
    logsLoading.value = false
  }
}

function searchLogs() {
  logPage.value = 1
  loadLogs()
}

function fmtTime(row, column, value) {
  return value ? String(value).slice(0, 19) : '-'
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
.tip {
  color: #64748b;
  font-size: 13px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.search-result {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.result-label {
  color: #64748b;
  font-size: 14px;
}
.result-value {
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
  word-break: break-all;
}
</style>
