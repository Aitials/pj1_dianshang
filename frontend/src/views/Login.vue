<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo">
        <el-icon :size="40"><Shop /></el-icon>
      </div>
      <h2 class="title">电商运营管理与智能分析平台</h2>
      <p class="subtitle">E-commerce Operations &amp; Intelligent Analytics</p>

      <el-form class="form" @keyup.enter="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
          登 录
        </el-button>
      </el-form>

      <p class="tip">还没有账号？<a @click="showRegister = true">立即注册</a></p>
    </div>

    <el-dialog v-model="showRegister" title="注册账号" width="400px" :append-to-body="true">
      <el-form>
        <el-form-item>
          <el-input v-model="regForm.username" placeholder="用户名" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="regForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Shop, User, Lock } from '@element-plus/icons-vue'
import { login, register } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const showRegister = ref(false)
const form = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login({ username: form.username, password: form.password })
    authStore.setAuth(res.access_token, res.username)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!regForm.username || !regForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  await register({ username: regForm.username, password: regForm.password })
  ElMessage.success('注册成功，请登录')
  showRegister.value = false
  form.username = regForm.username
  regForm.password = ''
}
</script>

<style scoped>
.login-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
  position: relative;
  overflow: hidden;
}
.login-container::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(96, 165, 250, 0.25), transparent 70%);
  top: -200px;
  right: -150px;
}
.login-container::after {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.2), transparent 70%);
  bottom: -180px;
  left: -120px;
}

.login-card {
  width: 420px;
  padding: 40px 36px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.3);
  position: relative;
  z-index: 1;
}
.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2563eb, #60a5fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.title {
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}
.subtitle {
  text-align: center;
  color: #64748b;
  font-size: 12px;
  margin: 8px 0 28px;
  letter-spacing: 0.5px;
}
.login-btn {
  width: 100%;
  margin-top: 4px;
  border-radius: 8px;
  font-weight: 600;
  letter-spacing: 4px;
}
.tip {
  text-align: center;
  margin-top: 20px;
  color: #64748b;
  font-size: 13px;
}
.tip a {
  color: #2563eb;
  cursor: pointer;
  font-weight: 600;
}
</style>
