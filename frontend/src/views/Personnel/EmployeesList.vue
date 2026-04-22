<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Співробітники</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Персонал</el-breadcrumb-item>
          <el-breadcrumb-item>Співробітники</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-primary">
          Новий співробітник
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-toolbar">
      <div class="left-filters">
        <el-input
          v-model="searchQuery"
          placeholder="ПІБ співробітника..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <el-select 
          v-model="departmentId" 
          placeholder="Всі підрозділи" 
          clearable 
          @change="fetchEmployees"
          class="filter-select"
        >
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
      </div>
    </div>

    <!-- Data Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        v-loading="loading" 
        :data="employees" 
        stripe 
        style="width: 100%"
        class="custom-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="full_name" label="Співробітник" min-width="220">
          <template #default="scope">
            <div class="employee-cell">
              <el-avatar :size="32" :src="scope.row.photo_url" class="employee-avatar">
                {{ scope.row.full_name.charAt(0) }}
              </el-avatar>
              <div class="employee-name-pos">
                <span class="emp-name">{{ scope.row.full_name }}</span>
                <span class="emp-pos">{{ scope.row.position }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="department_name" label="Підрозділ" width="180" />
        
        <el-table-column prop="status_name" label="Статус" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status_name)" size="small">
              {{ scope.row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="phone" label="Телефон" width="150" />
        
        <el-table-column prop="hire_date" label="Дата прийому" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.hire_date) }}
          </template>
        </el-table-column>
        
        <el-table-column label="Дії" width="100" align="right">
          <template #default="scope">
            <el-button link type="primary" :icon="Edit" @click.stop="handleEdit(scope.row)" />
            <el-button link type="danger" :icon="Delete" @click.stop="handleDelete(scope.row)" />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          background
          layout="total, prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()

// State
const loading = ref(false)
const employees = ref([])
const departments = ref([])
const total = ref(0)
const currentPage = ref(1)
const limit = ref(15)

const searchQuery = ref('')
const departmentId = ref(null)

const fetchEmployees = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * limit.value,
      limit: limit.value,
      search: searchQuery.value || undefined,
      department_id: departmentId.value || undefined
    }
    const res = await api.get('/api/v1/employees', { params })
    employees.value = res.data
    // Mock total
    total.value = employees.value.length < limit.value ? employees.value.length : 100
  } catch (error) {
    ElMessage.error('Помилка завантаження співробітників')
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const res = await api.get('/api/v1/departments')
    departments.value = res.data
  } catch (error) {
    console.error('Failed to fetch departments', error)
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchEmployees()
}

let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchEmployees()
  }, 300)
}

const handleCreate = () => {
  router.push('/personnel/employees/new')
}

const handleEdit = (row) => {
  router.push(`/personnel/employees/${row.id}`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити (архівувати) ${row.full_name}? Співробітник перестане відображатися в основному списку.`,
    'Підтвердження видалення',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/employees/${row.id}`)
      ElMessage.success('Співробітника видалено')
      fetchEmployees()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  })
}

const handleRowClick = (row) => {
  router.push(`/personnel/employees/${row.id}`)
}

const getStatusType = (statusName) => {
  if (!statusName) return 'info'
  const name = statusName.toLowerCase()
  if (name.includes('актив') || name.includes('працює')) return 'success'
  if (name.includes('відпуст')) return 'warning'
  if (name.includes('звільн')) return 'danger'
  return 'info'
}

const formatDate = (date) => {
  return date ? dayjs(date).format('DD.MM.YYYY') : '—'
}

onMounted(() => {
  fetchEmployees()
  fetchDepartments()
})
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
  margin-bottom: 24px;
}

.left-filters {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 200px;
}

.content-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.employee-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.employee-name-pos {
  display: flex;
  flex-direction: column;
}

.emp-name {
  font-weight: 600;
  color: #1a1d1f;
  font-size: 14px;
}

.emp-pos {
  font-size: 12px;
  color: #6f767e;
}

.pagination-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.custom-table {
  cursor: pointer;
}
</style>
