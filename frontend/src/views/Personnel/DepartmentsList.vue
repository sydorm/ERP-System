<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Підрозділи</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Персонал</el-breadcrumb-item>
          <el-breadcrumb-item>Підрозділи</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-primary">
          Додати підрозділ
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук за назвою..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
      </div>
    </div>

    <!-- Data Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        v-loading="loading" 
        :data="departments" 
        stripe 
        style="width: 100%"
        class="custom-table"
      >
        <el-table-column prop="name" label="Назва підрозділу" min-width="200">
          <template #default="scope">
            <span class="dept-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="head_name" label="Керівник" min-width="150">
          <template #default="scope">
            <span>{{ scope.row.head_name || '—' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="Статус" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'" size="small">
              {{ scope.row.is_active ? 'Активний' : 'Неактивний' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Дії" width="120" align="right">
          <template #default="scope">
            <el-button link type="primary" :icon="Edit" @click="handleEdit(scope.row)">Редагувати</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? 'Редагувати підрозділ' : 'Додати підрозділ'"
      width="450px"
      @closed="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="Назва підрозділу" prop="name">
          <el-input v-model="form.name" placeholder="Наприклад: Виробництво" />
        </el-form-item>
        
        <el-form-item label="Керівник" prop="head_id">
          <el-select 
            v-model="form.head_id" 
            placeholder="Оберіть співробітника" 
            clearable 
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="emp in employees"
              :key="emp.id"
              :label="emp.full_name"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Статус">
          <el-switch
            v-model="form.is_active"
            active-text="Активний"
            inactive-text="Неактивний"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          Зберегти
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

// State
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const departments = ref([])
const employees = ref([])
const searchQuery = ref('')

const formRef = ref(null)
const form = ref({
  id: null,
  name: '',
  head_id: null,
  is_active: true
})

const rules = {
  name: [
    { required: true, message: 'Будь ласка, введіть назву підрозділу', trigger: 'blur' }
  ]
}

const fetchDepartments = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value || undefined
    }
    const res = await api.get('/api/v1/departments', { params })
    departments.value = res.data
  } catch (error) {
    ElMessage.error('Помилка завантаження підрозділів')
  } finally {
    loading.value = false
  }
}

const fetchEmployees = async () => {
  try {
    const res = await api.get('/api/v1/employees', { params: { limit: 1000 } })
    employees.value = res.data
  } catch (error) {
    console.error('Failed to fetch employees for dropdown', error)
  }
}

const handleSearch = () => {
  fetchDepartments()
}

const handleCreate = () => {
  isEdit.value = false
  form.value = { id: null, name: '', head_id: null, is_active: true }
  dialogVisible.value = true
  fetchEmployees()
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
  fetchEmployees()
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/api/v1/departments/${form.value.id}`, form.value)
          ElMessage.success('Підрозділ оновлено')
        } else {
          await api.post('/api/v1/departments', form.value)
          ElMessage.success('Підрозділ додано')
        }
        dialogVisible.value = false
        fetchDepartments()
      } catch (error) {
        ElMessage.error('Помилка збереження')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(fetchDepartments)
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1d1f;
}

.btn-primary {
  background: #2a85ff;
  border: none;
  font-weight: 600;
}

.filters-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.search-input {
  width: 350px;
}

.content-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.dept-name {
  font-weight: 600;
  color: #1a1d1f;
}

.custom-table {
  border-radius: 8px;
  overflow: hidden;
}
</style>
