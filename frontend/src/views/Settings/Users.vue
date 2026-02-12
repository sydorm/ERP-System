<template>
  <div class="users-page">
    <div class="page-header">
      <h2>Користувачі</h2>
      <el-button type="primary" :icon="Plus" @click="openCreateModal">
        Додати користувача
      </el-button>
    </div>

    <el-card>
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="first_name" label="Ім'я" />
        <el-table-column prop="last_name" label="Прізвище" />
        <el-table-column prop="email" label="Email" />
        <el-table-column prop="role" label="Роль">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleName(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="Статус">
            <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? 'Активний' : 'Неактивний' }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column label="Дії" width="150" align="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" :icon="Edit" @click="openEditModal(row)" title="Редагувати" />
              <el-button size="small" type="warning" :icon="Lock" @click="openPasswordModal(row)" title="Змінити пароль" />
              <el-button size="small" type="danger" :icon="Delete" @click="confirmDelete(row)" title="Видалити" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? 'Редагувати користувача' : 'Новий користувач'"
      width="500px"
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
      title="Зміна пароля"
      width="400px"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-position="top">
        <el-form-item label="Новий пароль" prop="password">
          <el-input v-model="passwordForm.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="submitPasswordChange" :loading="submitting">
            Змінити
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete, Lock } from '@element-plus/icons-vue'
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
const formRef = ref()
const passwordFormRef = ref()

const form = reactive({
  id: null,
  first_name: '',
  last_name: '',
  email: '',
  role: 'worker',
  password: ''
})

const passwordForm = reactive({
  id: null,
  password: ''
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

const passwordRules = {
  password: [{ required: true, message: 'Введіть новий пароль', trigger: 'blur' }, { min: 8, message: 'Мінімум 8 символів', trigger: 'blur' }]
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

const getRoleType = (role) => {
  const types = {
    'admin': 'danger',
    'manager': 'warning',
    'worker': 'info'
  }
  return types[role] || ''
}

const openCreateModal = () => {
  isEditing.value = false
  form.id = null
  form.first_name = ''
  form.last_name = ''
  form.email = ''
  form.role = 'worker'
  form.password = ''
  dialogVisible.value = true
}

const openEditModal = (row) => {
  isEditing.value = true
  form.id = row.id
  form.first_name = row.first_name
  form.last_name = row.last_name
  form.email = row.email
  form.role = row.role
  dialogVisible.value = true
}

const openPasswordModal = (row) => {
  passwordForm.id = row.id
  passwordForm.password = ''
  passwordDialogVisible.value = true
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
            role: form.role
          })
          ElMessage.success('Користувача оновлено')
        } else {
          await api.post('/users', {
            first_name: form.first_name,
            last_name: form.last_name,
            email: form.email,
            role: form.role,
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

const submitPasswordChange = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await api.post(`/users/${passwordForm.id}/password?password=${passwordForm.password}`)
        ElMessage.success('Пароль змінено')
        passwordDialogVisible.value = false
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка зміни пароля')
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
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await api.delete(`/users/${row.id}`)
        ElMessage.success('Користувача видалено')
        fetchUsers()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Не вдалося видалити')
      }
    })
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
