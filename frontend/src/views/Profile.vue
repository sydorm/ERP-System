<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>Мій Профіль</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
        <el-breadcrumb-item>Профіль</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-row :gutter="20">
      <!-- General Information -->
      <el-col :xs="24" :md="12" :lg="8">
        <el-card class="box-card profile-card">
          <template #header>
            <div class="card-header">
              <span>Загальна інформація</span>
            </div>
          </template>
          
          <div class="user-avatar-section">
            <el-avatar :size="100" class="profile-avatar">
              {{ initials }}
            </el-avatar>
            <div class="user-role-badge">
              <el-tag :type="roleType" effect="dark" round>{{ roleName }}</el-tag>
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
              <el-input v-model="profileForm.first_name" />
            </el-form-item>
            
            <el-form-item label="Прізвище" prop="last_name">
              <el-input v-model="profileForm.last_name" />
            </el-form-item>
            
            <el-form-item label="Email" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>

            <el-button type="primary" class="w-100" @click="updateProfile" :loading="profileLoading">
              Зберегти зміни
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- Security / Password -->
      <el-col :xs="24" :md="12" :lg="16">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>Безпека</span>
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

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Новий пароль" prop="new_password">
                  <el-input v-model="passwordForm.new_password" type="password" show-password />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Підтвердження пароля" prop="confirm_password">
                  <el-input v-model="passwordForm.confirm_password" type="password" show-password />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button type="warning" @click="changePassword" :loading="passwordLoading">
                Змінити пароль
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
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
  email: ''
})

const profileRules = {
  first_name: [{ required: true, message: "Введіть ім'я", trigger: 'blur' }],
  last_name: [{ required: true, message: 'Введіть прізвище', trigger: 'blur' }],
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Некоректний email', trigger: 'blur' }
  ]
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
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.user-avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 30px;
    margin-top: 10px;
}

.profile-avatar {
    background-color: #409eff;
    font-size: 36px;
    margin-bottom: 15px;
}

.user-role-badge {
    margin-bottom: 10px;
}

.w-100 {
    width: 100%;
}

.mb-4 {
    margin-bottom: 16px;
}
</style>
