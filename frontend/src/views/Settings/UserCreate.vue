<template>
  <div class="user-create-page erp-light-container">
    <div class="page-header kimi-mb-6">
      <h1 class="kimi-text-2xl kimi-font-bold kimi-text-slate-800">Новий користувач</h1>
      <p class="kimi-text-sm kimi-text-slate-500">Створення облікового запису та налаштування прав доступу</p>
    </div>

    <el-tabs v-model="activeTab" class="user-card-tabs">
      <el-tab-pane label="Основне" name="main" />
      <el-tab-pane label="Доступи" name="permissions" />
      <el-tab-pane label="Активність" name="activity" />
      <el-tab-pane label="Безпека" name="security" />
      <el-tab-pane label="Історія змін" name="history" />
    </el-tabs>

    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-row :gutter="24">
        <!-- Left Block: Form (60%) -->
        <el-col :xs="24" :md="14">
          <div v-show="activeTab === 'main'" class="premium-card left-card">
            <!-- Avatar -->
            <div class="avatar-upload-section kimi-mb-6">
              <el-form-item label="Аватар">
                <el-upload
                  class="avatar-uploader"
                  action="/api/v1/upload"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <img v-if="form.avatar_url" :src="form.avatar_url" class="avatar-img" />
                  <div v-else class="avatar-placeholder">
                    <el-icon class="avatar-icon"><Plus /></el-icon>
                    <span>Завантажити</span>
                  </div>
                </el-upload>
              </el-form-item>
            </div>

            <!-- Name & Surname -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Ім'я" prop="first_name">
                  <el-input v-model="form.first_name" placeholder="Введіть ім'я" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Прізвище" prop="last_name">
                  <el-input v-model="form.last_name" placeholder="Введіть прізвище" />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- Email & Phone -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Email" prop="email">
                  <el-input v-model="form.email" placeholder="example@mail.com" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Телефон" prop="phone">
                  <el-input v-model="form.phone" placeholder="+38 (0__) ___-__-__" />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- Role -->
            <el-form-item label="Роль" prop="role">
              <el-select v-model="form.role" style="width: 100%" @change="handleRoleChange">
                <el-option
                  v-for="role in ROLE_OPTIONS"
                  :key="role.value"
                  :label="role.label"
                  :value="role.value"
                />
              </el-select>
            </el-form-item>

            <!-- Password & Confirm Password -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Пароль" prop="password">
                  <el-input v-model="form.password" type="password" show-password placeholder="Мінімум 8 символів" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Підтвердження" prop="confirmPassword">
                  <el-input v-model="form.confirmPassword" type="password" show-password placeholder="Повторіть пароль" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div v-show="activeTab === 'activity'" class="premium-card placeholder-card">
            <h3 class="section-title kimi-mb-4">Активність</h3>
            <p>Журнал активності з'явиться після створення користувача.</p>
          </div>

          <div v-show="activeTab === 'security'" class="premium-card placeholder-card">
            <h3 class="section-title kimi-mb-4">Безпека</h3>
            <p>Пароль задається під час створення. Скидання пароля доступне в картці користувача.</p>
          </div>

          <div v-show="activeTab === 'history'" class="premium-card placeholder-card">
            <h3 class="section-title kimi-mb-4">Історія змін</h3>
            <p>Історія змін буде доступна після першого збереження.</p>
          </div>
        </el-col>

        <!-- Right Block: Permissions (40%) -->
        <el-col :xs="24" :md="10">
          <div v-show="activeTab === 'permissions' || activeTab === 'main'" class="premium-card right-card">
            <h3 class="section-title kimi-mb-4">Доступи</h3>
            
            <el-form-item v-if="form.role !== 'admin'">
              <div class="permissions-container">
                <div v-for="group in permissionGroups" :key="group.key" class="permission-group kimi-mb-4">
                  <div class="group-header kimi-mb-2">
                    <el-checkbox 
                      v-model="group.all" 
                      @change="(val) => handleGroupAllChange(group, val)"
                    >
                      <strong class="kimi-text-slate-700">{{ group.label }}</strong>
                    </el-checkbox>
                  </div>
                  <div class="group-items kimi-flex kimi-flex-wrap kimi-gap-3">
                    <el-checkbox 
                      v-for="perm in group.items" 
                      :key="perm.key"
                      v-model="form.permissions[perm.key]"
                    >
                      {{ perm.label }}
                    </el-checkbox>
                  </div>
                </div>
              </div>
            </el-form-item>
            <div v-else class="admin-info kimi-py-4 kimi-text-center">
              <el-tag type="success" size="large" effect="plain">Адміністратор має доступ до всіх функцій системи</el-tag>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Footer Actions -->
      <div class="form-actions kimi-mt-6 kimi-flex kimi-justify-end kimi-gap-4">
        <el-button size="large" @click="goBack">Скасувати</el-button>
        <el-button type="primary" size="large" class="gradient-btn" @click="submitForm" :loading="submitting">
          Створити користувача
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useRouter } from 'vue-router'
import {
  ROLE_OPTIONS,
  buildPermissionGroups,
  buildPermissionsForRole,
  setGroupPermissions,
  syncPermissionGroups,
} from '@/permissions/registry'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)
const activeTab = ref('main')

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  role: 'manager',
  password: '',
  confirmPassword: '',
  avatar_url: '',
  permissions: {}
})

const permissionGroups = ref(buildPermissionGroups())

const handleGroupAllChange = (group, val) => {
  setGroupPermissions(form.permissions, group, val)
}

const handleRoleChange = (newRole) => {
  form.permissions = buildPermissionsForRole(newRole)
  syncPermissionGroups(permissionGroups.value, form.permissions)
}

// Initialize default role perms
handleRoleChange('manager')

const rules = {
  first_name: [{ required: true, message: "Введіть ім'я", trigger: 'blur' }],
  last_name: [{ required: true, message: 'Введіть прізвище', trigger: 'blur' }],
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Некоректний email', trigger: 'blur' }
  ],
  role: [{ required: true, message: 'Оберіть роль', trigger: 'change' }],
  password: [
    { required: true, message: 'Введіть пароль', trigger: 'blur' },
    { min: 8, message: 'Мінімум 8 символів', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Підтвердіть пароль', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('Паролі не співпадають'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          phone: form.phone,
          role: form.role,
          avatar_url: form.avatar_url,
          permissions: form.permissions,
          password: form.password
        }
        
        await api.post('/users', payload)
        ElMessage.success('Користувача успішно створено!')
        router.push('/settings/users')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка створення користувача')
      } finally {
        submitting.value = false
      }
    }
  })
}

const goBack = () => {
  router.push('/settings/users')
}

const handleAvatarSuccess = (res) => {
  form.avatar_url = res.url
}

const beforeAvatarUpload = (file) => {
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('Розмір фото не може перевищувати 2MB!')
  }
  return isLt2M
}
</script>

<style scoped>
.user-create-page {
  padding: 24px;
  background-color: #F8FAFC;
  min-height: calc(100vh - 60px);
}
.premium-card {
  background: #FFFFFF;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  height: 100%;
  border: 1px solid #F1F5F9;
}
.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1E293B;
  border-bottom: 1px solid #F1F5F9;
  padding-bottom: 12px;
}
.avatar-uploader {
  display: inline-block;
  border: 2px dashed #cbd5e1;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}
.avatar-uploader:hover {
  border-color: #6C63FF;
}
.avatar-placeholder {
  width: 100px;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 12px;
}
.avatar-icon {
  font-size: 24px;
  margin-bottom: 6px;
}
.avatar-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}
.gradient-btn {
  background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 100%);
  border: none;
  color: white;
}
.gradient-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  color: white;
}
.permissions-container {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}
.user-card-tabs {
  margin-bottom: 16px;
}
.placeholder-card {
  color: #64748b;
  min-height: 240px;
}
</style>
