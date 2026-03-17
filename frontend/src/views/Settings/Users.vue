<template>
  <div class="users-page">
    <div class="fixed-top-area">
      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Всього користувачів</p>
              <p class="kimi-stat-value text-indigo-600">{{ users.length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
              <el-icon><User /></el-icon>
            </div>
          </div>
        </div>
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Адміністратори</p>
              <p class="kimi-stat-value text-emerald-600">{{ users.filter(u => u.role === 'admin').length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
              <el-icon><Key /></el-icon>
            </div>
          </div>
        </div>
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Менеджери</p>
              <p class="kimi-stat-value text-amber-600">{{ users.filter(u => u.role === 'manager').length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
              <el-icon><Avatar /></el-icon>
            </div>
          </div>
        </div>
        <div class="kimi-stat-card kimi-stat-blue">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Активні зараз</p>
              <p class="kimi-stat-value text-blue-600">{{ users.filter(u => u.is_active).length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-blue-100 text-blue-600">
              <el-icon><Monitor /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== SEARCH & FILTER BAR ===== -->
      <div class="kimi-filter-bar">
        <div class="kimi-filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="Пошук за ім'ям або email..."
            :prefix-icon="Search"
            clearable
            class="kimi-search-input"
          />
          <el-button class="kimi-refresh-btn" @click="fetchUsers" title="Оновити">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        <div class="kimi-filter-right">
          <button class="kimi-primary-btn" @click="openCreateModal">
            <el-icon><Plus /></el-icon> Новий користувач
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MAIN TABLE CARD ===== -->
    <div class="table-card scrollable-table-area">
      <el-table
        v-loading="loading"
        :data="filteredUsers"
        height="100%"
        size="small"
        style="width: 100%"
        class="kimi-table"
        row-class-name="kimi-row"
        header-row-class-name="kimi-header-row"
      >
        <el-table-column label="Користувач" min-width="250">
          <template #default="{ row }">
            <div class="user-info-cell">
              <div class="user-avatar" :style="{ backgroundColor: getAvatarColor(row) }">
                {{ getInitials(row) }}
              </div>
              <div class="user-details">
                <p class="kimi-text-sm kimi-font-medium">{{ row.first_name }} {{ row.last_name }}</p>
                <p class="kimi-text-xxs kimi-text-slate-400">{{ row.email }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Роль" width="150" align="center">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getRoleBadgeClass(row.role)">
              {{ getRoleName(row.role) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="120" align="center">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-dot" :class="{ 'is-active': row.is_active }"></span>
              <span class="kimi-text-xs">{{ row.is_active ? 'Активний' : 'Неактивний' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="180" align="center">
          <template #default="{ row }">
            <div class="kimi-actions-col">
              <button class="kimi-ghost-btn" @click="openEditModal(row)" title="Редагувати">
                <el-icon class="kimi-text-indigo-400"><Edit /></el-icon>
              </button>
              <button class="kimi-ghost-btn" @click="openPasswordModal(row)" title="Скинути пароль">
                <el-icon class="kimi-text-amber-400"><Key /></el-icon>
              </button>
              <button class="kimi-ghost-btn" @click="confirmDelete(row)" title="Видалити" v-if="row.id !== userStore.user?.id">
                <el-icon class="kimi-text-rose-400"><Delete /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? 'Редагувати користувача' : 'Новий користувач'"
      width="500px"
      class="kimi-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Ім'я" prop="first_name">
              <el-input v-model="form.first_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="Прізвище" prop="last_name">
              <el-input v-model="form.last_name" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>

        <el-form-item label="Роль" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="Адміністратор" value="admin" />
            <el-option label="Менеджер" value="manager" />
            <el-option label="Працівник" value="worker" />
          </el-select>
        </el-form-item>

        <el-form-item label="Доступи" v-if="form.role !== 'admin'">
          <div class="permissions-container">
            <div v-for="group in permissionGroups" :key="group.key" class="permission-group">
              <div class="group-header">
                <el-checkbox 
                  v-model="group.all" 
                  @change="(val) => handleGroupAllChange(group, val)"
                >
                  <strong>{{ group.label }}</strong>
                </el-checkbox>
              </div>
              <div class="group-items">
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

        <el-form-item v-if="!isEditing" label="Пароль" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEditing ? 'Зберегти' : 'Створити' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Password Reset Dialog -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="Скидання пароля"
      width="400px"
      class="kimi-dialog"
    >
      <div class="password-reset-content">
        <p class="kimi-text-sm kimi-mb-4">
          Ви збираєтеся скинути пароль для <strong>{{ passwordForm.name }}</strong>.
        </p>
        
        <el-checkbox v-model="passwordForm.sendEmail" class="kimi-mb-4">
          Надіслати новий пароль на email
        </el-checkbox>

        <div v-if="passwordForm.newPassword" class="new-password-display kimi-mt-4">
          <p class="kimi-text-xs kimi-text-slate-400">Новий тимчасовий пароль:</p>
          <div class="password-box">
            <span class="password-text">{{ passwordForm.newPassword }}</span>
            <el-button link @click="copyToClipboard(passwordForm.newPassword)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
          <p class="kimi-text-xxs kimi-text-rose-500 kimi-mt-2">
            * Обов'язково скопіюйте цей пароль зараз, він не буде показаний знову.
          </p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">Закрити</el-button>
          <el-button type="primary" @click="submitPasswordReset" :loading="submitting">
            {{ passwordForm.newPassword ? 'Згенерувати ще раз' : 'Згенерувати пароль' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { 
  Plus, Search, Edit, Delete, Key, 
  Refresh, User, Avatar, Monitor, 
  CopyDocument, Check, Close 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const formRef = ref()

const form = reactive({
  id: null,
  first_name: '',
  last_name: '',
  email: '',
  role: 'worker',
  password: '',
  permissions: {}
})

const permissionGroups = ref([
  {
    label: 'Склад',
    key: 'inventory',
    all: false,
    items: [
      { label: 'Перегляд', key: 'inventory.view' },
      { label: 'Номенклатура', key: 'inventory.nomenclature.view' },
      { label: 'Склади', key: 'inventory.warehouses.view' },
      { label: 'Залишки', key: 'inventory.stock.view' }
    ]
  },
  {
    label: 'Продажі',
    key: 'sales',
    all: false,
    items: [
      { label: 'Перегляд', key: 'sales.view' },
      { label: 'Контрагенти', key: 'sales.counterparties.view' },
      { label: 'Замовлення', key: 'sales.orders.view' },
      { label: 'Рахунки', key: 'sales.invoices.view' }
    ]
  },
  {
    label: 'Закупівлі',
    key: 'purchases',
    all: false,
    items: [
      { label: 'Перегляд', key: 'purchases.view' },
      { label: 'Замовлення', key: 'purchases.orders.view' },
      { label: 'Прибуткові накладні', key: 'purchases.receipts.view' }
    ]
  },
  {
    label: 'Фінанси',
    key: 'finance',
    all: false,
    items: [
      { label: 'Перегляд', key: 'finance.view' },
      { label: 'Каса', key: 'finance.cash.view' },
      { label: 'Банк', key: 'finance.bank.view' }
    ]
  }
])

const handleGroupAllChange = (group, val) => {
  group.items.forEach(item => {
    form.permissions[item.key] = val
  })
}

const passwordForm = reactive({
  id: null,
  name: '',
  sendEmail: true,
  newPassword: ''
})

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => 
    u.first_name.toLowerCase().includes(q) || 
    u.last_name.toLowerCase().includes(q) || 
    u.email.toLowerCase().includes(q)
  )
})

const rules = {
  first_name: [{ required: true, message: "Введіть ім'я", trigger: 'blur' }],
  last_name: [{ required: true, message: 'Введіть прізвище', trigger: 'blur' }],
  email: [
    { required: true, message: 'Введіть email', trigger: 'blur' },
    { type: 'email', message: 'Некоректний email', trigger: 'blur' }
  ],
  role: [{ required: true, message: 'Оберіть роль', trigger: 'change' }],
  password: [{ required: true, message: 'Введіть пароль', trigger: 'blur' }, { min: 8, message: 'Мінімум 8 символів', trigger: 'blur' }]
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('Не вдалося завантажити користувачів')
  } finally {
    loading.value = false
  }
}

const getRoleName = (role) => {
  const roles = {
    'admin': 'Адміністратор',
    'manager': 'Менеджер',
    'worker': 'Працівник'
  }
  return roles[role] || role
}

const openCreateModal = () => {
  isEditing.value = false
  form.id = null
  form.first_name = ''
  form.last_name = ''
  form.email = ''
  form.role = 'worker'
  form.password = ''
  form.permissions = {}
  permissionGroups.value.forEach(g => g.all = false)
  dialogVisible.value = true
}

const openEditModal = (row) => {
  isEditing.value = true
  form.id = row.id
  form.first_name = row.first_name
  form.last_name = row.last_name
  form.email = row.email
  form.role = row.role
  form.permissions = { ...(row.permissions || {}) }
  
  permissionGroups.value.forEach(group => {
    group.all = group.items.every(item => form.permissions[item.key])
  })
  
  dialogVisible.value = true
}

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
    const response = await api.post(`/users/${passwordForm.id}/password-reset`, null, {
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

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditing.value) {
          await api.put(`/users/${form.id}`, {
            first_name: form.first_name,
            last_name: form.last_name,
            email: form.email,
            role: form.role,
            permissions: form.permissions
          })
          ElMessage.success('Користувача оновлено')
        } else {
          await api.post('/users', {
            first_name: form.first_name,
            last_name: form.last_name,
            email: form.email,
            role: form.role,
            permissions: form.permissions,
            password: form.password,
            company_id: userStore.user?.companyId
          })
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

const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити користувача ${row.first_name} ${row.last_name}?`,
    'Попередження',
    { confirmButtonText: 'Видалити', cancelButtonText: 'Скасувати', type: 'warning' }
  ).then(async () => {
    try {
      await api.delete(`/users/${row.id}`)
      ElMessage.success('Користувача видалено')
      fetchUsers()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Не вдалося видалити')
    }
  })
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Скопійовано!')
}

const getInitials = (user) => {
  return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
}

const getAvatarColor = (user) => {
  const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  const index = (user.first_name?.length || 0) % colors.length
  return colors[index]
}

const getRoleBadgeClass = (role) => {
  const map = {
    'admin': 'kimi-status-rose',
    'manager': 'kimi-status-amber',
    'worker': 'kimi-status-slate'
  }
  return map[role] || 'kimi-status-slate'
}

onMounted(fetchUsers)
</script>

<style scoped>
/* ===== PAGE ===== */
.users-page {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #f4f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== FIXED TOP AREA ===== */
.fixed-top-area {
  flex-shrink: 0;
  background: #f4f5f9;
  padding: 16px 20px 0px;
  display: flex;
  flex-direction: column;
}

/* ===== TABLE CARD ===== */
.table-card {
  background: #fff;
  border-radius: 8px;
  margin: 16px 20px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

.scrollable-table-area {
  overflow: auto;
}

/* ===== USER CELL ===== */
.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-details p {
  margin: 0;
  line-height: 1.2;
}

/* ===== STATUS CELL ===== */
.status-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #cbd5e1;
}

.status-dot.is-active {
  background-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

/* ===== PASSWORD RESET ===== */
.password-box {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.password-text {
  font-family: monospace;
  font-size: 18px;
  font-weight: 700;
  color: #1e1b4b;
  letter-spacing: 1px;
}

/* ===== PERMISSIONS ===== */
.permissions-container {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.permission-group {
  margin-bottom: 15px;
}

.group-header {
  border-bottom: 1px solid var(--el-border-color-extra-light);
  margin-bottom: 8px;
  padding-bottom: 4px;
}

.group-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  padding-left: 10px;
}

.kimi-actions-col {
  display: flex;
  justify-content: center;
  gap: 8px;
}
</style>
