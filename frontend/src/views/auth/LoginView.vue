<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>ERP System</h2>
          <p>Увійдіть до системи</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="Email" prop="email">
          <el-input
            v-model="loginForm.email"
            placeholder="your@email.com"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="Пароль" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Введіть пароль"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <div class="form-footer">
            <el-checkbox v-model="loginForm.remember">
              Запам'ятати мене
            </el-checkbox>
            <el-link type="primary" :underline="false">
              Забули пароль?
            </el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            Увійти
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider>або</el-divider>

      <div class="signup-link">
        <span>Ще немає облікового запису?</span>
        <el-link type="primary" @click="goToSignup" :underline="false">
          Зареєструвати компанію
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

const loginRules = {
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Введіть правильний email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Введіть пароль', trigger: 'blur' },
    { min: 6, message: 'Пароль має бути мінімум 6 символів', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const response = await api.post('/auth/login', {
          email: loginForm.email,
          password: loginForm.password
        })
        
        const { access_token } = response.data
        userStore.setToken(access_token)
        
        // Get user profile
        const profileResponse = await api.get('/auth/me')
        userStore.setUser({
          id: profileResponse.data.id,
          email: profileResponse.data.email,
          firstName: profileResponse.data.first_name,
          lastName: profileResponse.data.last_name,
          role: profileResponse.data.role,
          companyId: profileResponse.data.company_id
        })
        
        ElMessage.success('Успішний вхід!')
        router.push('/dashboard')
      } catch (error) {
        console.error('Login error:', error)
        ElMessage.error(error.response?.data?.detail || 'Помилка входу. Перевірте дані.')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToSignup = () => {
  router.push('/signup')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.form-footer {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.signup-link {
  text-align: center;
  color: #606266;
}

.signup-link span {
  margin-right: 8px;
}
</style>
