<template>
  <div class="forgot-password-container">
    <el-card class="forgot-password-card">
      <template #header>
        <div class="card-header">
          <h2>Відновлення пароля</h2>
          <p>Введіть ваш email для отримання інструкцій</p>
        </div>
      </template>

      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="Email" prop="email">
          <el-input
            v-model="forgotForm.email"
            placeholder="your@email.com"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item v-if="recoveryMessage" class="recovery-result">
          <el-alert
            :title="recoveryMessage"
            type="success"
            :closable="false"
            show-icon
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
            class="submit-button"
            :disabled="!!recoveryMessage"
          >
            Відправити
          </el-button>
        </el-form-item>
      </el-form>

      <div class="back-link">
        <el-link type="primary" @click="goToLogin" :underline="false">
          Повернутися до входу
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const forgotFormRef = ref()
const loading = ref(false)
const recoveryMessage = ref('')

const forgotForm = reactive({
  email: ''
})

const forgotRules = {
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Введіть правильний email', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!forgotFormRef.value) return
  
  await forgotFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const response = await api.post('/auth/forgot-password', {
          email: forgotForm.email
        })
        
        recoveryMessage.value = response.data.message
        ElMessage.success('Запит успішно відправлено')
      } catch (error) {
        console.error('Forgot password error:', error)
        ElMessage.error(error.response?.data?.detail || 'Помилка при відправці запиту.')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-password-card {
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
  font-size: 24px;
  font-weight: 600;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.submit-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.back-link {
  text-align: center;
  margin-top: 20px;
}

.recovery-result {
  margin-top: 10px;
  margin-bottom: 20px;
}
</style>
