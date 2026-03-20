<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>Мій Профіль</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
        <el-breadcrumb-item>Профіль</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-row :gutter="20" class="profile-row">
      <!-- Column 1: General Info & Avatar -->
      <el-col :xs="24" :md="8" :lg="6">
        <el-card class="box-card profile-card primary-card">
          <template #header>
            <div class="card-header">
              <span>👤 Загальна інформація</span>
            </div>
          </template>
          
          <div class="user-avatar-section">
            <el-avatar :size="100" class="profile-avatar shadow-sm">
              {{ initials }}
            </el-avatar>
            <div class="user-role-badge">
              <el-tag :type="roleType" effect="dark" round size="large">{{ roleName }}</el-tag>
            </div>
          </div>

          <el-form 
            ref="profileFormRef" 
            :model="profileForm" 
            :rules="profileRules" 
            label-position="top"
            class="profile-form"
          >
            <el-form-item label="Ім'я" prop="first_name">
              <el-input v-model="profileForm.first_name" placeholder="Введіть ім'я" />
            </el-form-item>
            
            <el-form-item label="Прізвище" prop="last_name">
              <el-input v-model="profileForm.last_name" placeholder="Введіть прізвище" />
            </el-form-item>
            
            <el-form-item label="Email" prop="email">
              <el-input v-model="profileForm.email" placeholder="email@example.com" />
            </el-form-item>

            <el-form-item label="Телефон" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="+380..." />
            </el-form-item>

            <el-button type="primary" class="w-100 save-btn" @click="updateProfile" :loading="profileLoading">
              Зберегти профіль
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- Column 2: Security & Preferences -->
      <el-col :xs="24" :md="16" :lg="18">
        <el-row :gutter="20">
          <!-- Preferences Section -->
          <el-col :xs="24" :lg="12">
            <el-card class="box-card mb-4 mt-xs-4">
              <template #header>
                <div class="card-header">
                  <span>⚙️ Налаштування інтерфейсу</span>
                </div>
              </template>
              
              <el-form label-position="left" label-width="150px">
                <el-form-item label="Мова інтерфейсу">
                  <el-select v-model="preferences.language" class="w-100">
                    <el-option label="Українська" value="uk" />
                    <el-option label="English" value="en" />
                  </el-select>
                </el-form-item>

                <el-form-item label="Часовий пояс">
                  <el-select v-model="preferences.timezone" class="w-100">
                    <el-option label="(GMT+02:00) Київ" value="Europe/Kiev" />
                    <el-option label="(UTC) London" value="UTC" />
                  </el-select>
                </el-form-item>

                <el-divider />

                <el-form-item label="Компактний режим">
                  <el-switch v-model="preferences.compactMode" />
                  <span class="ml-2 text-muted">Більше даних на екрані</span>
                </el-form-item>

                <el-form-item label="Звукові сповіщення">
                  <el-switch v-model="preferences.notifications.sound" />
                </el-form-item>

                <el-form-item label="Браузерні сповіщення">
                  <el-switch v-model="preferences.notifications.browser" />
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <!-- Security Section -->
          <el-col :xs="24" :lg="12">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span>🔒 Безпека</span>
                </div>
              </template>

              <el-form 
                ref="passwordFormRef" 
                :model="passwordForm" 
                :rules="passwordRules" 
                label-position="top"
              >
                <el-alert
                  title="Зміна пароля"
                  type="info"
                  description="Використовуйте надійний пароль (мінімум 8 символів)."
                  show-icon
                  :closable="false"
                  class="mb-4"
                />
                
                <el-form-item label="Поточний пароль" prop="current_password">
                  <el-input v-model="passwordForm.current_password" type="password" show-password />
                </el-form-item>

                <el-form-item label="Новий пароль" prop="new_password">
                  <el-input v-model="passwordForm.new_password" type="password" show-password />
                </el-form-item>

                <el-form-item label="Підтвердження пароля" prop="confirm_password">
                  <el-input v-model="passwordForm.confirm_password" type="password" show-password />
                </el-form-item>

                <el-form-item>
                  <el-button type="warning" @click="changePassword" :loading="passwordLoading" class="w-100">
                    Оновити пароль
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import api from '@/api'

const userStore = useUserStore()

// Profile Data
const profileFormRef = ref()
const profileLoading = ref(false)
const profileForm = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: ''
})

// Preferences Data (Local state, could be moved to store/DB later)
const preferences = reactive({
  language: 'uk',
  timezone: 'Europe/Kiev',
  compactMode: false,
  notifications: {
    sound: true,
    browser: true
  }
})

const profileRules = {
  first_name: [{ required: true, message: "Введіть ім'я", trigger: 'blur' }],
  last_name: [{ required: true, message: 'Введіть прізвище', trigger: 'blur' }],
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Некоректний email', trigger: 'blur' }
  ],
  phone: [{ pattern: /^\+?[0-9\s-]{10,20}$/, message: 'Некоректний формат телефону', trigger: 'blur' }]
}

// Password Data
const passwordFormRef = ref()
const passwordLoading = ref(false)
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('Будь ласка, введіть пароль ще раз'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('Паролі не співпадають!'))
  } else {
    callback()
  }
}

const passwordRules = {
  current_password: [{ required: true, message: 'Введіть поточний пароль', trigger: 'blur' }],
  new_password: [
    { required: true, message: 'Введіть новий пароль', trigger: 'blur' },
    { min: 8, message: 'Мінімум 8 символів', trigger: 'blur' }
  ],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

// Computed
const initials = computed(() => {
  const f = profileForm.first_name ? profileForm.first_name[0] : ''
  const l = profileForm.last_name ? profileForm.last_name[0] : ''
  return (f + l).toUpperCase()
})

const roleName = computed(() => {
  const roles = {
    'admin': 'Адміністратор',
    'manager': 'Менеджер',
    'worker': 'Працівник'
  }
  return roles[userStore.user?.role] || userStore.user?.role
})

const roleType = computed(() => {
   const types = {
    'admin': 'danger',
    'manager': 'warning',
    'worker': 'info'
  }
  return types[userStore.user?.role] || ''
})

// Actions
const loadUserProfile = async () => {
    // If store is empty, try fetching. But usually store has data.
    // Let's fetch fresh data to be sure
    try {
        const response = await api.get('/auth/me')
        const user = response.data
        profileForm.first_name = user.first_name
        profileForm.last_name = user.last_name
        profileForm.email = user.email
    } catch (error) {
        // Fallback to store if fetch fails (rare)
        if (userStore.user) {
            profileForm.first_name = userStore.user.firstName
            profileForm.last_name = userStore.user.lastName
            profileForm.email = userStore.user.email
        }
    }
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      profileLoading.value = true
      try {
        const response = await api.put('/auth/me', {
            first_name: profileForm.first_name,
            last_name: profileForm.last_name,
            email: profileForm.email
        })
        
        // Update Store
        userStore.setUser({
            ...userStore.user,
            firstName: response.data.first_name,
            lastName: response.data.last_name,
            email: response.data.email
        })
        
        ElMessage.success('Профіль оновлено')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка оновлення профілю')
      } finally {
        profileLoading.value = false
      }
    }
  })
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        await api.post('/auth/password', {
            current_password: passwordForm.current_password,
            new_password: passwordForm.new_password
        })
        
        ElMessage.success('Пароль успішно змінено')
        // Clear form
        passwordForm.current_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
        passwordFormRef.value.resetFields()
        
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка зміни пароля')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

onMounted(() => {
    loadUserProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-row {
    margin-top: 10px;
}

.page-header {
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.box-card {
    border-radius: 12px;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.primary-card {
    border-top: 4px solid #409eff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.user-avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 25px;
    margin-top: 5px;
}

.profile-avatar {
    background-color: #409eff;
    font-size: 40px;
    margin-bottom: 15px;
}

.shadow-sm {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-role-badge {
    margin-bottom: 5px;
}

.profile-form {
    padding: 0 5px;
}

.save-btn {
    height: 44px;
    font-weight: 600;
}

.w-100 {
    width: 100%;
}

.mb-4 {
    margin-bottom: 16px;
}

.ml-2 {
    margin-left: 8px;
}

.text-muted {
    color: #909399;
    font-size: 12px;
}

@media (max-width: 768px) {
    .mt-xs-4 {
        margin-top: 20px;
    }
}
</style>
