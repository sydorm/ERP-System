<template>
  <div class="users-page-premium">
    <div class="page-header-zone">
      <!-- ===== PREMIUM KPI CARDS ===== -->
      <div class="premium-stats-grid">
        <div class="stat-glass-card indigo">
          <div class="stat-content">
            <span class="stat-label">Всього користувачів</span>
            <span class="stat-value">{{ users.length }}</span>
          </div>
          <div class="stat-icon-box">
            <el-icon><User /></el-icon>
          </div>
        </div>

        <div class="stat-glass-card emerald">
          <div class="stat-content">
            <span class="stat-label">Адміністратори</span>
            <span class="stat-value">{{ users.filter(u => u.role === 'admin').length }}</span>
          </div>
          <div class="stat-icon-box">
            <el-icon><Key /></el-icon>
          </div>
        </div>

        <div class="stat-glass-card amber">
          <div class="stat-content">
            <span class="stat-label">Менеджери</span>
            <span class="stat-value">{{ users.filter(u => u.role === 'manager').length }}</span>
          </div>
          <div class="stat-icon-box">
            <el-icon><Avatar /></el-icon>
          </div>
        </div>

        <div class="stat-glass-card blue">
          <div class="stat-content">
            <span class="stat-label">В мережі</span>
            <span class="stat-value">{{ onlineCount }}</span>
          </div>
          <div class="stat-icon-box">
            <el-icon><Monitor /></el-icon>
          </div>
        </div>
      </div>

      <!-- ===== ACTION TOOLBAR ===== -->
      <div class="premium-toolbar-card saas-premium-shadow">
        <div class="search-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <input
            v-model="searchQuery"
            placeholder="Пошук за ім'ям або email"
            class="premium-native-search"
          />
        </div>
        <div class="actions-wrapper">
          <button class="premium-add-btn" @click="openCreateModal">
            <el-icon><Plus /></el-icon>
            <span>Новий користувач</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MAIN CONTENT ===== -->
    <div class="users-content-area">
      <div class="premium-table-container saas-premium-shadow">
        <el-table
          v-loading="loading"
          :data="filteredUsers"
          height="100%"
          class="premium-modern-table"
          header-row-class-name="premium-header-row"
          row-class-name="premium-row"
        >
          <el-table-column label="Користувач" min-width="280">
            <template #default="{ row }">
              <div class="user-cell-premium">
                <div class="avatar-container">
                  <el-avatar :size="40" :src="row.avatar_url" v-if="row.avatar_url" class="avatar-main" />
                  <div v-else class="avatar-placeholder" :style="{ background: getAvatarColor(row) }">
                    {{ getInitials(row) }}
                  </div>
                  <div class="online-indicator" :class="{ active: isUserOnline(row) }" />
                </div>
                <div class="user-meta">
                  <span class="user-full-name">
                    {{ row.first_name }} {{ row.last_name }}
                    <span v-if="isRecentlyAdded(row)" class="new-badge">NEW</span>
                  </span>
                  <span class="user-email">{{ row.email }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Телефон" width="160">
            <template #default="{ row }">
              <span class="phone-text">{{ row.phone || '—' }}</span>
            </template>
          </el-table-column>

          <el-table-column label="Роль" width="160">
            <template #default="{ row }">
              <div class="role-pill" :class="row.role">
                <span class="dot"></span>
                {{ getRoleName(row.role) }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Активність" width="180">
            <template #default="{ row }">
              <span class="activity-text">{{ formatTime(row.last_login_at) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="Статус" width="140" align="center">
            <template #default="{ row }">
              <div class="status-badge-premium" :class="row.blocked_at ? 'blocked' : 'active'">
                {{ row.blocked_at ? 'Заблокований' : 'Активний' }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="Дії" width="120" align="right">
            <template #default="{ row }">
              <div class="table-actions-premium">
                <el-tooltip content="Редагувати" placement="top">
                  <button class="action-minimal-btn" @click="openEditModal(row)">
                    <el-icon><Edit /></el-icon>
                  </button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- ===== PREMIUM DIALOG ===== -->
    <el-dialog
      v-model="dialogVisible"
      title="Налаштування профілю"
      width="800px"
      class="premium-glass-dialog"
      destroy-on-close
    >
      <div class="dialog-content-wrapper">
        <el-tabs v-model="dialogTab" class="premium-tabs-vertical">
          <el-tab-pane label="Основні дані" name="main">
            <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="premium-form">
              <div class="avatar-upload-zone">
                <el-upload
                  class="avatar-uploader-premium"
                  action="/api/v1/upload/image"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <img v-if="form.avatar_url" :src="form.avatar_url" class="uploaded-avatar" />
                  <div v-else class="upload-placeholder">
                    <el-icon><Camera /></el-icon>
                    <span>Додати фото</span>
                  </div>
                </el-upload>
                <div class="avatar-help">
                  <h4>Фото профілю</h4>
                  <p>Рекомендовано квадратне фото, мін. 400x400px</p>
                </div>
              </div>

              <div class="form-grid-2">
                <el-form-item label="Ім'я" prop="first_name">
                  <el-input v-model="form.first_name" placeholder="Введіть ім'я" />
                </el-form-item>
                <el-form-item label="Прізвище" prop="last_name">
                  <el-input v-model="form.last_name" placeholder="Введіть прізвище" />
                </el-form-item>
              </div>
              
              <div class="form-grid-2">
                <el-form-item label="Email адреса" prop="email">
                  <el-input v-model="form.email" placeholder="example@mail.com" />
                </el-form-item>
                <el-form-item label="Телефон" prop="phone">
                  <el-input v-model="form.phone" placeholder="+380..." />
                </el-form-item>
              </div>

              <el-form-item label="Системна роль" prop="role">
                <el-select v-model="form.role" style="width: 100%" @change="handleRoleChange" class="premium-select">
                  <el-option
                    v-for="role in ROLE_OPTIONS"
                    :key="role.value"
                    :label="role.label"
                    :value="role.value"
                  />
                </el-select>
              </el-form-item>

              <div v-if="!isEditing" class="form-grid-2">
                <el-form-item label="Пароль" prop="password">
                  <el-input v-model="form.password" type="password" show-password placeholder="Мінімум 8 символів" />
                </el-form-item>
                <el-form-item label="Підтвердження" prop="confirmPassword">
                  <el-input v-model="form.confirmPassword" type="password" show-password placeholder="Повторіть пароль" />
                </el-form-item>
              </div>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="Доступи" name="permissions">
            <div class="permissions-explorer">
              <div v-for="group in permissionGroups" :key="group.key" class="perm-group-card">
                <div class="group-head">
                  <el-checkbox 
                    v-model="group.all" 
                    @change="(val) => handleGroupAllChange(group, val)"
                  >
                    {{ group.label }}
                  </el-checkbox>
                </div>
                <div class="group-body">
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
          </el-tab-pane>
          
          <el-tab-pane label="Активність" name="activity">
            <div class="user-activity-log">
              <div v-if="loadingActivity" class="activity-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>Завантаження активності...</span>
              </div>
              <div v-else-if="userActivity.length === 0" class="activity-empty">
                <el-icon><InfoFilled /></el-icon>
                <span>Немає записів про активність</span>
              </div>
              <div v-else class="activity-list">
                <div v-for="log in userActivity" :key="log.id" class="activity-item">
                  <div class="activity-icon" :class="log.action">
                    <el-icon v-if="log.action === 'login'"><Key /></el-icon>
                    <el-icon v-else-if="log.action === 'create'"><Plus /></el-icon>
                    <el-icon v-else><Edit /></el-icon>
                  </div>
                  <div class="activity-info">
                    <div class="activity-header">
                      <span class="activity-action">{{ getActionText(log.action) }}</span>
                      <span class="activity-time">{{ formatFullTime(log.created_at) }}</span>
                    </div>
                    <div class="activity-details" v-if="log.changes">
                      {{ formatActivityDetails(log) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Історія руху" name="history">
            <div class="user-history-log">
              <el-table :data="userHistory" style="width: 100%" height="400px" class="history-table">
                <el-table-column prop="created_at" label="Час" width="160">
                  <template #default="{ row }">
                    {{ formatFullTime(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column prop="action" label="Подія" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getActionTagType(row.action)" size="small">
                      {{ getActionText(row.action) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="details" label="Деталі">
                  <template #default="{ row }">
                    <span class="history-details-text">{{ formatActivityDetails(row) }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <div class="premium-dialog-footer">
          <button class="btn-secondary" @click="dialogVisible = false">Скасувати</button>
          <button class="btn-primary" @click="submitForm" :loading="submitting">
            <el-icon><Check /></el-icon>
            {{ isEditing ? 'Зберегти зміни' : 'Створити акаунт' }}
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- ===== PASSWORD RESET DIALOG ===== -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="Скидання пароля"
      width="440px"
      class="premium-glass-dialog secondary"
    >
      <div class="password-reset-content">
        <p class="desc">Ви збираєтеся згенерувати новий пароль для <strong>{{ passwordForm.name }}</strong>.</p>
        
        <el-checkbox v-model="passwordForm.sendEmail" class="send-email-check">
          Надіслати новий пароль на email
        </el-checkbox>

        <div v-if="passwordForm.newPassword" class="new-password-box">
          <span class="label">Новий тимчасовий пароль:</span>
          <div class="code-wrapper">
            <span class="code">{{ passwordForm.newPassword }}</span>
            <button class="copy-btn" @click="copyToClipboard(passwordForm.newPassword)">
              <el-icon><CopyDocument /></el-icon>
            </button>
          </div>
          <p class="warning">* Скопіюйте цей пароль зараз. Він не буде показаний знову.</p>
        </div>
      </div>
      <template #footer>
        <div class="premium-dialog-footer">
          <button class="btn-secondary" @click="passwordDialogVisible = false">Закрити</button>
          <button class="btn-primary warning" @click="submitPasswordReset" :loading="submitting">
            <el-icon><Refresh /></el-icon>
            {{ passwordForm.newPassword ? 'Згенерувати ще раз' : 'Згенерувати пароль' }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { 
  Plus, Search, Edit, Delete, Key, 
  User, Avatar, Monitor, Camera,
  CircleClose, Check, Close, Loading, InfoFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import {
  ROLE_OPTIONS,
  buildPermissionGroups,
  buildPermissionsForRole,
  getRoleName as getRegistryRoleName,
  setGroupPermissions,
  syncPermissionGroups,
} from '@/permissions/registry'

const router = useRouter()
const userStore = useUserStore()

const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const formRef = ref()
const dialogTab = ref('main')
const userActivity = ref([])
const userHistory = ref([])
const loadingActivity = ref(false)

const form = reactive({
  id: null,
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

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => 
    u.first_name.toLowerCase().includes(q) || 
    u.last_name.toLowerCase().includes(q) || 
    u.email.toLowerCase().includes(q) ||
    (u.phone && u.phone.includes(q))
  )
})

const onlineCount = computed(() => {
  const fifteenMinsAgo = new Date(Date.now() - 15 * 60 * 1000)
  return users.value.filter(u => u.last_login_at && new Date(u.last_login_at) > fifteenMinsAgo).length
})

const isUserOnline = (user) => {
  if (!user.last_login_at) return false
  return new Date(user.last_login_at) > new Date(Date.now() - 15 * 60 * 1000)
}

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

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('Не вдалося завантажити користувачів')
  } finally {
    loading.value = false
  }
}

const getRoleName = (role) => getRegistryRoleName(role)

const openCreateModal = () => {
  router.push('/settings/users/create')
}

const openEditModal = (row) => {
  isEditing.value = true
  Object.assign(form, {
    id: row.id, first_name: row.first_name, last_name: row.last_name,
    email: row.email, phone: row.phone || '', role: row.role,
    avatar_url: row.avatar_url || '', permissions: { ...(row.permissions || {}) }
  })
  permissionGroups.value.forEach(group => {
    group.all = group.items.every(item => form.permissions[item.key])
  })
  dialogTab.value = 'main'
  dialogVisible.value = true
  fetchUserActivity(row.id)
}

const fetchUserActivity = async (userId) => {
  loadingActivity.value = true
  try {
    const response = await api.get(`/api/v1/users/${userId}/activity`)
    userActivity.value = response.data
    userHistory.value = response.data // Using same source for history for now
  } catch (error) {
    console.error('Error fetching activity:', error)
  } finally {
    loadingActivity.value = false
  }
}

const getActionText = (action) => {
  const map = {
    'login': 'Вхід в систему',
    'logout': 'Вихід',
    'create': 'Створення об\'єкта',
    'update': 'Оновлення даних',
    'delete': 'Видалення',
    'status_change': 'Зміна статусу',
    'permission_change': 'Зміна прав доступу'
  }
  return map[action] || action
}

const getActionTagType = (action) => {
  const map = {
    'create': 'success',
    'update': 'warning',
    'delete': 'danger',
    'login': 'info',
    'permission_change': 'primary'
  }
  return map[action] || ''
}

const formatActivityDetails = (log) => {
  if (log.action === 'login') return 'Авторизація через Web-інтерфейс'
  if (log.action === 'permission_change') return 'Оновлено набір дозволів користувача'
  if (log.changes) {
    const keys = Object.keys(log.changes).filter(k => k !== 'password')
    if (keys.length > 0) return `Змінено: ${keys.join(', ')}`
  }
  return 'Системна подія'
}

const formatFullTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          first_name: form.first_name, last_name: form.last_name,
          email: form.email, phone: form.phone, role: form.role,
          avatar_url: form.avatar_url, permissions: form.permissions
        }
        if (isEditing.value) {
          await api.put(`/api/v1/users/${form.id}`, payload)
          ElMessage.success('Користувача оновлено')
        } else {
          payload.password = form.password
          payload.company_id = userStore.user?.companyId
          await api.post('/api/v1/users', payload)
          ElMessage.success('Користувача створено')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
      } finally {
        submitting.value = false
      }
    }
  })
}

const blockUser = (row) => {
  const action = row.blocked_at ? 'розблокувати' : 'заблокувати'
  ElMessageBox.confirm(
    `Ви впевнені, що хочете ${action} користувача ${row.first_name} ${row.last_name}?`,
    'Попередження',
    { confirmButtonText: action.charAt(0).toUpperCase() + action.slice(1), cancelButtonText: 'Скасувати', type: 'warning' }
  ).then(async () => {
    try {
      if (row.blocked_at) {
        await api.patch(`/api/v1/users/${row.id}/unblock`)
      } else {
        await api.patch(`/api/v1/users/${row.id}/block`)
      }
      ElMessage.success(`Користувача ${action}овано`)
      fetchUsers()
    } catch (error) {
      ElMessage.error('Не вдалося змінити статус')
    }
  })
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити користувача ${row.first_name} ${row.last_name}?`,
    'Видалення користувача',
    { confirmButtonText: 'Видалити назавжди', cancelButtonText: 'Скасувати', type: 'error' }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/users/${row.id}`)
      ElMessage.success('Користувача видалено')
      fetchUsers()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

const handleAvatarSuccess = (res) => { form.avatar_url = res.url }
const beforeAvatarUpload = (file) => {
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) ElMessage.error('Розмір фото не може перевищувати 2MB!')
  return isLt2M
}

const formatTime = (dateString) => {
  if (!dateString) return 'Давно'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'Тільки що'
  if (diffMins < 60) return `${diffMins} хв тому`
  return date.toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const getInitials = (user) => `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
const getAvatarColor = (user) => {
  const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  const index = (user.first_name?.length || 0) % colors.length
  return colors[index]
}

const selectedUserRow = ref(null)
const passwordDialogVisible = ref(false)
const passwordForm = reactive({
  id: null,
  name: '',
  sendEmail: true,
  newPassword: ''
})

const openPasswordModal = (row) => {
  passwordForm.id = row.id
  passwordForm.name = `${row.first_name} ${row.last_name}`
  passwordForm.sendEmail = true
  passwordForm.newPassword = ''
  passwordDialogVisible.value = true
}

const submitPasswordReset = async () => {
  submitting.value = true
  try {
    const response = await api.post(`/api/v1/users/${passwordForm.id}/password-reset`, null, {
      params: { send_email: passwordForm.sendEmail }
    })
    passwordForm.newPassword = response.data.temp_password
    ElMessage.success('Пароль успішно скинуто')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка скидання пароля')
  } finally {
    submitting.value = false
  }
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Скопійовано!')
}

const isRecentlyAdded = (user) => {
  if (!user.created_at) return false
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
  return new Date(user.created_at) > oneDayAgo
}

onMounted(fetchUsers)
</script>

<style scoped>
.users-page-premium {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F8FAFC;
  overflow: hidden;
}

.page-header-zone {
  padding: 24px 32px 0;
  background: #fff;
  border-bottom: 1px solid #E2E8F0;
  flex-shrink: 0;
}

/* KPI CARDS */
.premium-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-glass-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.stat-glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.06);
}

.stat-content { display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 11px; font-weight: 800; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-value { font-size: 32px; font-weight: 900; }

.stat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 24px;
}

.indigo .stat-value { color: #6366F1; }
.emerald .stat-value { color: #15B97A; }
.amber .stat-value { color: #F59E0B; }
.blue .stat-value { color: #1463FF; }

.indigo .stat-icon-box { background: rgba(99, 102, 241, 0.1); color: #6366F1; }
.emerald .stat-icon-box { background: rgba(21, 185, 122, 0.1); color: #15B97A; }
.amber .stat-icon-box { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
.blue .stat-icon-box { background: rgba(20, 99, 255, 0.1); color: #1463FF; }

/* TOOLBAR */
.premium-toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  border-radius: 16px;
  margin-bottom: 24px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.search-icon {
  font-size: 18px;
  color: #94A3B8;
}

.premium-native-search {
  border: none;
  background: transparent;
  font-size: 14px;
  color: #1E293B;
  width: 100%;
  outline: none;
}

.premium-native-search::placeholder {
  color: #94A3B8;
}

.premium-add-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1463FF 0%, #0047D1 100%);
  color: #fff;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.25);
}

.premium-add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
}

/* CONTENT AREA */
.users-content-area {
  flex: 1;
  padding: 24px 32px;
  overflow: hidden;
}

.premium-table-container {
  height: 100%;
  background: #fff;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid #E2E8F0;
}

.user-cell-premium {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-container { position: relative; }
.avatar-placeholder {
  width: 40px; height: 40px; border-radius: 12px;
  display: grid; place-items: center;
  color: #fff; font-weight: 800; font-size: 14px;
}
.online-indicator {
  position: absolute; bottom: -2px; right: -2px;
  width: 12px; height: 12px; border-radius: 50%;
  background: #CBD5E1; border: 2px solid #fff;
}
.online-indicator.active { background: #15B97A; box-shadow: 0 0 0 4px rgba(21, 185, 122, 0.2); }

.user-meta { display: flex; flex-direction: column; }
.user-full-name { font-weight: 700; color: #0F172A; font-size: 14px; }
.user-email { font-size: 12px; color: #94A3B8; }

.role-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 700;
  background: #F1F5F9; color: #475569;
}
.role-pill.admin { background: #EEF2FF; color: #6366F1; }
.role-pill.manager { background: #ECFDF5; color: #15B97A; }
.role-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

.status-badge-premium {
  display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; text-transform: uppercase;
}
.status-badge-premium.active { background: #DCFCE7; color: #166534; }
.status-badge-premium.blocked { background: #FEE2E2; color: #991B1B; }

.table-actions-premium { display: flex; gap: 8px; justify-content: flex-end; }
.action-minimal-btn {
  width: 32px; height: 32px; border-radius: 8px; border: none;
  background: transparent; color: #94A3B8; cursor: pointer; transition: all 0.2s;
  display: grid; place-items: center;
}
.action-minimal-btn:hover { color: #6366F1; background: #F5F7FF; }

/* DIALOG */
.premium-glass-dialog :deep(.el-dialog) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.avatar-upload-zone {
  display: flex; align-items: center; gap: 20px; margin-bottom: 24px;
  padding: 20px; background: #F8FAFC; border-radius: 16px;
}
.avatar-uploader-premium {
  width: 80px; height: 80px; border-radius: 20px; border: 2px dashed #E2E8F0;
  display: grid; place-items: center; cursor: pointer; overflow: hidden;
}
.uploaded-avatar { width: 100%; height: 100%; object-fit: cover; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; font-size: 10px; color: #94A3B8; }
.upload-placeholder .el-icon { font-size: 24px; margin-bottom: 4px; }

.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.premium-tabs-vertical :deep(.el-tabs__item) {
  font-weight: 700; height: 50px; border-radius: 12px; margin-bottom: 4px;
}

.premium-dialog-footer {
  display: flex; justify-content: flex-end; gap: 12px; padding: 20px 0 0;
}
.btn-secondary {
  padding: 10px 20px; border-radius: 12px; border: 1px solid #E2E8F0; background: #fff;
  font-weight: 700; cursor: pointer;
}
.btn-primary {
  display: flex; align-items: center; gap: 8px; padding: 10px 24px; border-radius: 12px;
  background: #6366F1; color: #fff; border: none; font-weight: 700; cursor: pointer;
}

.permissions-explorer { display: grid; gap: 16px; }
.perm-group-card { border: 1px solid #E2E8F0; border-radius: 16px; overflow: hidden; }
.group-head { background: #F8FAFC; padding: 10px 16px; border-bottom: 1px solid #E2E8F0; }
.group-body { padding: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

@media (max-width: 1200px) {
  .premium-stats-grid { grid-template-columns: 1fr 1fr; }
}
.btn-primary.warning { background: #F59E0B; }

.new-badge {
  font-size: 9px; background: #6366F1; color: #fff; padding: 1px 5px; border-radius: 4px;
  margin-left: 6px; vertical-align: middle; font-weight: 900;
}

.password-reset-content { padding: 10px 0; }
.password-reset-content .desc { font-size: 14px; color: #475569; margin-bottom: 20px; }
.send-email-check { margin-bottom: 24px; }

.new-password-box {
  background: #F8FAFC; border: 1px dashed #E2E8F0; border-radius: 16px; padding: 20px;
}
.new-password-box .label { font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; display: block; }
.code-wrapper { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.code-wrapper .code { font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 800; color: #0F172A; letter-spacing: 2px; }
.copy-btn { border: none; background: #EEF2FF; color: #6366F1; width: 40px; height: 40px; border-radius: 10px; cursor: pointer; display: grid; place-items: center; font-size: 20px; }
.new-password-box .warning { font-size: 11px; color: #EF4444; font-weight: 700; margin-top: 12px; }

/* ACTIVITY & HISTORY TABS */
.user-activity-log, .user-history-log {
  padding: 8px 0;
  min-height: 400px;
}

.activity-loading, .activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94A3B8;
  gap: 12px;
}

.activity-loading .el-icon { font-size: 24px; }
.activity-empty .el-icon { font-size: 32px; }

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  background: #F8FAFC;
  border: 1px solid #F1F5F9;
  transition: all 0.2s;
}

.activity-item:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #E2E8F0;
  color: #64748B;
}

.activity-icon.login { color: #1463FF; background: rgba(20, 99, 255, 0.05); }
.activity-icon.create { color: #10B981; background: rgba(16, 185, 129, 0.05); }
.activity-icon.update { color: #F59E0B; background: rgba(245, 158, 11, 0.05); }

.activity-info { flex: 1; min-width: 0; }

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.activity-action {
  font-weight: 700;
  color: #1E293B;
  font-size: 14px;
}

.activity-time {
  font-size: 12px;
  color: #94A3B8;
}

.activity-details {
  font-size: 13px;
  color: #64748B;
}

.history-details-text {
  font-size: 13px;
  color: #475569;
}

.history-table :deep(.el-table__row) {
  cursor: default;
}
</style>
