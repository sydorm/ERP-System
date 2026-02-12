<template>
  <div class="signup-container">
    <el-card class="signup-card">
      <template #header>
        <div class="card-header">
          <h2>Реєстрація компанії</h2>
          <p>Створіть обліковий запис для вашої компанії</p>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="Компанія" />
        <el-step title="Адміністратор" />
        <el-step title="Налаштування" />
      </el-steps>

      <div class="step-content">
        <!-- Step 1: Company Info -->
        <el-form
          v-show="currentStep === 0"
          ref="companyFormRef"
          :model="companyForm"
          :rules="companyRules"
          label-position="top"
          size="large"
        >
          <el-form-item label="Назва компанії" prop="name">
            <el-input
              v-model="companyForm.name"
              placeholder="ТОВ 'Ваша компанія'"
              clearable
            />
          </el-form-item>

          <el-form-item label="Правова форма" prop="legalForm">
            <el-select
              v-model="companyForm.legalForm"
              placeholder="Оберіть правову форму"
              style="width: 100%"
            >
              <el-option label="ТОВ (Товариство з обмеженою відповідальністю)" value="TOV" />
              <el-option label="ФОП (Фізична особа підприємець)" value="FOP" />
              <el-option label="ПП (Приватне підприємство)" value="PP" />
              <el-option label="АТ (Акціонерне товариство)" value="AT" />
            </el-select>
          </el-form-item>

          <el-form-item label="Код ЄДРПОУ / ІПН" prop="taxId">
            <el-input
              v-model="companyForm.taxId"
              placeholder="12345678"
              maxlength="10"
              clearable
            />
          </el-form-item>
        </el-form>

        <!-- Step 2: Admin User -->
        <el-form
          v-show="currentStep === 1"
          ref="adminFormRef"
          :model="adminForm"
          :rules="adminRules"
          label-position="top"
          size="large"
        >
          <el-form-item label="Ім'я" prop="firstName">
            <el-input
              v-model="adminForm.firstName"
              placeholder="Іван"
              clearable
            />
          </el-form-item>

          <el-form-item label="Прізвище" prop="lastName">
            <el-input
              v-model="adminForm.lastName"
              placeholder="Іваненко"
              clearable
            />
          </el-form-item>

          <el-form-item label="Email" prop="email">
            <el-input
              v-model="adminForm.email"
              placeholder="admin@company.com"
              clearable
            />
          </el-form-item>

          <el-form-item label="Пароль" prop="password">
            <el-input
              v-model="adminForm.password"
              type="password"
              placeholder="Мінімум 8 символів"
              show-password
            />
          </el-form-item>

          <el-form-item label="Підтвердіть пароль" prop="confirmPassword">
            <el-input
              v-model="adminForm.confirmPassword"
              type="password"
              placeholder="Повторіть пароль"
              show-password
            />
          </el-form-item>
        </el-form>

        <!-- Step 3: Initial Settings -->
        <el-form
          v-show="currentStep === 2"
          ref="settingsFormRef"
          :model="settingsForm"
          :rules="settingsRules"
          label-position="top"
          size="large"
        >
          <el-form-item label="Назва основного складу" prop="warehouseName">
            <el-input
              v-model="settingsForm.warehouseName"
              placeholder="Основний склад"
              clearable
            />
          </el-form-item>

          <el-form-item label="Валюта за замовчуванням" prop="currency">
            <el-select
              v-model="settingsForm.currency"
              placeholder="Оберіть валюту"
              style="width: 100%"
            >
              <el-option label="₴ UAH (Гривня)" value="UAH" />
              <el-option label="$ USD (Долар США)" value="USD" />
              <el-option label="€ EUR (Євро)" value="EUR" />
            </el-select>
          </el-form-item>

          <el-form-item label="Часовий пояс" prop="timezone">
            <el-select
              v-model="settingsForm.timezone"
              placeholder="Оберіть часовий пояс"
              style="width: 100%"
            >
              <el-option label="(UTC+2) Київ" value="Europe/Kiev" />
              <el-option label="(UTC+3) Москва" value="Europe/Moscow" />
              <el-option label="(UTC+1) Варшава" value="Europe/Warsaw" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="step-actions">
        <el-button
          v-if="currentStep > 0"
          @click="prevStep"
          size="large"
        >
          Назад
        </el-button>
        <el-button
          v-if="currentStep < 2"
          type="primary"
          @click="nextStep"
          size="large"
        >
          Далі
        </el-button>
        <el-button
          v-if="currentStep === 2"
          type="success"
          :loading="loading"
          @click="handleSubmit"
          size="large"
        >
          Зареєструвати компанію
        </el-button>
      </div>

      <el-divider />

      <div class="login-link">
        <span>Вже маєте обліковий запис?</span>
        <el-link type="primary" @click="goToLogin" :underline="false">
          Увійти
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const currentStep = ref(0)
const loading = ref(false)

const companyFormRef = ref()
const adminFormRef = ref()
const settingsFormRef = ref()

const companyForm = reactive({
  name: '',
  legalForm: '',
  taxId: ''
})

const adminForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const settingsForm = reactive({
  warehouseName: 'Основний склад',
  currency: 'UAH',
  timezone: 'Europe/Kiev'
})

const companyRules = {
  name: [{ required: true, message: 'Введіть назву компанії', trigger: 'blur' }],
  legalForm: [{ required: true, message: 'Оберіть правову форму', trigger: 'change' }],
  taxId: [
    { required: true, message: 'Введіть код ЄДРПОУ/ІПН', trigger: 'blur' },
    { min: 8, max: 10, message: 'Має бути 8-10 цифр', trigger: 'blur' }
  ]
}

const adminRules = {
  firstName: [{ required: true, message: "Введіть ім'я", trigger: 'blur' }],
  lastName: [{ required: true, message: 'Введіть прізвище', trigger: 'blur' }],
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Введіть правильний email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Введіть пароль', trigger: 'blur' },
    { min: 8, message: 'Пароль має бути мінімум 8 символів', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Підтвердіть пароль', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== adminForm.password) {
          callback(new Error('Паролі не співпадають'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const settingsRules = {
  warehouseName: [{ required: true, message: 'Введіть назву складу', trigger: 'blur' }],
  currency: [{ required: true, message: 'Оберіть валюту', trigger: 'change' }],
  timezone: [{ required: true, message: 'Оберіть часовий пояс', trigger: 'change' }]
}

const nextStep = async () => {
  let formRef
  if (currentStep.value === 0) formRef = companyFormRef.value
  else if (currentStep.value === 1) formRef = adminFormRef.value
  
  if (formRef) {
    await formRef.validate((valid) => {
      if (valid) {
        currentStep.value++
      }
    })
  }
}

const prevStep = () => {
  currentStep.value--
}

const handleSubmit = async () => {
  if (!settingsFormRef.value) return
  
  await settingsFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      
      // DEMO MODE: Mock registration (no backend needed)
      const registrationData = {
        company: companyForm,
        admin: adminForm,
        settings: settingsForm
      }
      
      console.log('Registration data:', registrationData)
      
      setTimeout(() => {
        // Set mock user data
        userStore.setUser({
          id: '1',
          email: adminForm.email,
          firstName: adminForm.firstName,
          lastName: adminForm.lastName
        })
        
        // Set mock token
        userStore.setToken('demo-token-12345')
        
        loading.value = false
        ElMessage.success('Компанію успішно зареєстровано! Входимо в систему...')
        
        // Redirect to dashboard instead of login
        router.push('/dashboard')
      }, 1500)
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.signup-card {
  width: 100%;
  max-width: 600px;
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

.step-content {
  margin: 30px 0;
  min-height: 350px;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.step-actions .el-button {
  flex: 1;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.login-link {
  text-align: center;
  color: #606266;
}

.login-link span {
  margin-right: 8px;
}
</style>
