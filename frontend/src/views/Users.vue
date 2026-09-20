<template>
  <div>
    <div class="page-title">
      <el-icon><Setting /></el-icon>
      <span>系统用户管理</span>
    </div>

    <el-card>
      <div class="toolbar">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>

      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openAssign(row)">分配角色</el-button>
            <el-button size="small" @click="openReset(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </el-card>

    <!-- 新建用户 -->
    <el-dialog v-model="showCreate" title="新建用户" width="400px">
      <el-form>
        <el-form-item label="用户名">
          <el-input v-model="createForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="createForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 分配角色 -->
    <el-dialog v-model="showAssign" title="分配角色" width="420px">
      <p class="reset-tip">用户：{{ currentUser.username }}</p>
      <el-checkbox-group v-model="assignForm.roleIds">
        <el-checkbox v-for="role in roles" :key="role.id" :value="role.id" :label="role.id">
          {{ role.name }}（{{ role.description || '无描述' }}）
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showAssign = false">取消</el-button>
        <el-button type="primary" @click="submitAssign">确认分配</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码 -->
    <el-dialog v-model="showReset" title="重置密码" width="400px">
      <p class="reset-tip">用户：{{ currentUser.username }}</p>
      <el-form>
        <el-form-item label="新密码">
          <el-input v-model="resetForm.password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReset = false">取消</el-button>
        <el-button type="primary" @click="submitReset">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, createUser, updateUser, getRoles, assignRole } from '../api/users'

const users = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)

const roles = ref([])

const showCreate = ref(false)
const showAssign = ref(false)
const showReset = ref(false)
const createForm = reactive({ username: '', password: '' })
const assignForm = reactive({ roleIds: [] })
const resetForm = reactive({ password: '' })
const currentUser = ref({})

async function load() {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, page_size: pageSize })
    users.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  const res = await getRoles()
  roles.value = res.roles
}

function openCreate() {
  createForm.username = ''
  createForm.password = ''
  showCreate.value = true
}

async function submitCreate() {
  if (!createForm.username || !createForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  await createUser({ username: createForm.username, password: createForm.password })
  ElMessage.success('创建成功')
  showCreate.value = false
  page.value = 1
  load()
}

function openAssign(row) {
  currentUser.value = row
  assignForm.roleIds = []
  showAssign.value = true
}

async function submitAssign() {
  await assignRole(currentUser.value.id, assignForm.roleIds)
  ElMessage.success('角色分配成功')
  showAssign.value = false
}

function openReset(row) {
  currentUser.value = row
  resetForm.password = ''
  showReset.value = true
}

async function submitReset() {
  if (!resetForm.password) {
    ElMessage.warning('请输入新密码')
    return
  }
  await updateUser(currentUser.value.id, { password: resetForm.password })
  ElMessage.success('密码已重置')
  showReset.value = false
}

onMounted(() => {
  load()
  loadRoles()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}
.page-num {
  color: #64748b;
  font-size: 13px;
}
.reset-tip {
  margin-bottom: 16px;
  color: #334155;
}
</style>
