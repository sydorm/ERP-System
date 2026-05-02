<template>
  <div class="page-container">

    <!-- ─── KPI CARDS (VUEXY STYLE) ─── -->
    <div class="kpi-grid-modern">
      <div v-for="stat in statsCards" :key="stat.title" class="kpi-card-modern">
        <div class="kpi-info">
          <span class="kpi-label">{{ stat.title }}</span>
          <div class="kpi-value-row">
            <span class="kpi-value">{{ stat.value }}</span>
            <span :class="['kpi-trend', stat.trend >= 0 ? 'trend-up' : 'trend-down']">
              ({{ stat.trend >= 0 ? '+' : '' }}{{ stat.trend }}%)
            </span>
          </div>
          <span class="kpi-subtext">Аналітика за тиждень</span>
        </div>
        <div class="kpi-icon-wrapper" :style="{ backgroundColor: stat.colorBg }">
          <el-icon :style="{ color: stat.colorIcon }"><component :is="stat.icon" /></el-icon>
        </div>
      </div>
    </div>

    <!-- ─── FILTERS TOOLBAR (COMPACT) ─── -->
    <div class="filters-card-modern">
      <div class="filter-header">
        <span class="filter-title">Фільтри</span>
      </div>
      <div class="filter-row-modern">
        <div class="filter-group">
          <el-select v-model="departmentId" placeholder="Оберіть підрозділ" clearable @change="fetchEmployees" class="select-modern">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="Статус" clearable @change="fetchEmployees" class="select-modern">
            <el-option label="Активні" value="active" />
            <el-option label="У відпустці" value="leave" />
            <el-option label="Звільнені" value="fired" />
          </el-select>
        </div>
        
        <div class="action-group-modern">
          <div class="search-wrapper-modern">
            <el-input
              v-model="searchQuery"
              placeholder="Пошук співробітника..."
              :prefix-icon="Search"
              clearable
              @input="handleSearch"
              class="search-input-modern"
            />
          </div>
          <el-dropdown trigger="click">
            <el-button class="btn-secondary-modern">
              <el-icon class="mr-2"><Download /></el-icon> Експорт
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>Експорт в Excel</el-dropdown-item>
                <el-dropdown-item>Експорт в PDF</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-button @click="handleCreate" class="btn-primary-compact">
            <el-icon class="mr-2"><Plus /></el-icon>
            <span>Новий співробітник</span>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-card-modern">
      <el-table 
        v-loading="loading" 
        :data="employees" 
        style="width: 100%"
        class="erp-table-modern"
        @row-click="handleRowClick"
      >
        <el-table-column prop="full_name" label="Співробітник" min-width="280">
          <template #default="scope">
            <div class="employee-info-cell">
              <el-avatar :size="38" :src="scope.row.photo_url" class="modern-avatar">
                {{ scope.row.full_name.charAt(0) }}
              </el-avatar>
              <div class="name-details">
                <div class="main-name">{{ scope.row.full_name }}</div>
                <div class="sub-pos">{{ scope.row.position || 'Посада не вказана' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="department_name" label="Підрозділ" width="200">
          <template #default="scope">
            <span class="dept-text">{{ scope.row.department_name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status_name" label="Статус" width="160">
          <template #default="scope">
            <div :class="['modern-badge', getStatusClass(scope.row.status_name)]">
              {{ scope.row.status_name }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="phone" label="Телефон" width="160">
          <template #default="scope">
            <span class="phone-text">{{ scope.row.phone || '—' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="hire_date" label="Дата прийому" width="140">
          <template #default="scope">
            <span class="date-text">{{ formatDate(scope.row.hire_date) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="Дії" width="120" align="right">
          <template #default="scope">
            <div class="table-actions">
              <el-tooltip content="Редагувати" placement="top">
                <button class="action-btn-mini edit" @click.stop="handleEdit(scope.row)">
                  <el-icon><Edit /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="Видалити" placement="top">
                <button class="action-btn-mini delete" @click.stop="handleDelete(scope.row)">
                  <el-icon><Delete /></el-icon>
                </button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer-modern">
        <div class="pagination-info">
          Показано {{ employees.length }} з {{ total }} співробітників
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          background
          layout="prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Edit, Delete, User, UserFilled, 
  Calendar, TrendCharts, Download 
} from '@element-plus/icons-vue'
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
const statusFilter = ref(null)

// Stats Calculation
const statsCards = computed(() => [
  { 
    title: 'Всього співробітників', 
    value: total.value, 
    trend: 12, 
    icon: 'User', 
    colorIcon: '#6366F1', 
    colorBg: 'rgba(99, 102, 241, 0.12)' 
  },
  { 
    title: 'Активні', 
    value: employees.value.filter(e => !e.status_name?.includes('звільн')).length, 
    trend: 8, 
    icon: 'UserFilled', 
    colorIcon: '#10B981', 
    colorBg: 'rgba(16, 185, 129, 0.12)' 
  },
  { 
    title: 'Нові (цей місяць)', 
    value: 3, 
    trend: 24, 
    icon: 'Calendar', 
    colorIcon: '#F59E0B', 
    colorBg: 'rgba(245, 158, 11, 0.12)' 
  },
  { 
    title: 'Плинність', 
    value: '2.4%', 
    trend: -14, 
    icon: 'TrendCharts', 
    colorIcon: '#EF4444', 
    colorBg: 'rgba(239, 68, 68, 0.12)' 
  }
])

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

const getStatusClass = (statusName) => {
  if (!statusName) return 'status-default'
  const name = statusName.toLowerCase()
  if (name.includes('актив') || name.includes('працює')) return 'status-active'
  if (name.includes('відпуст')) return 'status-warning'
  if (name.includes('звільн')) return 'status-danger'
  return 'status-default'
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
  padding: 24px 32px;
  background-color: #F8F7FA;
  min-height: 100vh;
  color: #444050;
}

/* Header & Breadcrumbs */
.header-section-modern {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}
.breadcrumb-modern {
  margin-bottom: 4px;
}
:deep(.el-breadcrumb__inner) {
  color: #94A3B8 !important;
  font-weight: 500;
  font-size: 13px;
}
:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #444050 !important;
}
.title-modern {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #444050;
  letter-spacing: -0.01em;
}

.btn-primary-compact {
  background: #6366F1;
  border: none;
  color: #fff;
  height: 40px;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.2);
  transition: all 0.2s;
}
.btn-primary-compact:hover {
  background: #4F46E5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* KPI Cards */
.kpi-grid-modern {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}
.kpi-card-modern {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  box-shadow: 0 4px 18px 0 rgba(15, 20, 34, 0.05);
}
.kpi-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748B;
  display: block;
  margin-bottom: 4px;
}
.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 4px;
}
.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: #444050;
}
.kpi-trend {
  font-size: 13px;
  font-weight: 700;
}
.trend-up { color: #10B981; }
.trend-down { color: #EF4444; }
.kpi-subtext {
  font-size: 11px;
  color: #94A3B8;
  font-weight: 500;
}
.kpi-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

/* Filters Toolbar */
.filters-card-modern {
  background: #fff;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid #F1F5F9;
  padding: 16px 24px;
}
.filter-header {
  margin-bottom: 12px;
}
.filter-title {
  font-size: 15px;
  font-weight: 700;
  color: #444050;
}
.filter-row-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-group {
  display: flex;
  gap: 16px;
}
.select-modern {
  width: 200px;
}
:deep(.el-input__wrapper) {
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
}

.action-group-modern {
  display: flex;
  gap: 12px;
  align-items: center;
}
.search-input-modern {
  width: 250px;
}
.btn-secondary-modern {
  height: 40px;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  color: #64748B;
  font-weight: 600;
}

/* Table Section */
.table-card-modern {
  background: #fff;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 4px 18px 0 rgba(15, 20, 34, 0.05);
}
.erp-table-modern {
  border-radius: 0 0 12px 12px;
}
:deep(.el-table__header) th {
  background-color: #F8F9FA !important;
  color: #444050 !important;
  font-weight: 700 !important;
  font-size: 12px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  padding: 12px 0 !important;
}
:deep(.el-table__row) {
  cursor: pointer;
}

.employee-info-cell {
  display: flex;
  align-items: center;
  gap: 14px;
}
.modern-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.name-details {
  display: flex;
  flex-direction: column;
}
.main-name {
  font-weight: 700;
  color: #444050;
  font-size: 14px;
}
.sub-pos {
  font-size: 12px;
  color: #94A3B8;
  font-weight: 500;
}

.modern-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.status-active { background: rgba(16, 185, 129, 0.12); color: #10B981; }
.status-warning { background: rgba(245, 158, 11, 0.12); color: #F59E0B; }
.status-danger { background: rgba(239, 68, 68, 0.12); color: #EF4444; }
.status-default { background: rgba(148, 163, 184, 0.12); color: #64748B; }

.table-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.action-btn-mini {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
  color: #64748B;
}
.action-btn-mini:hover {
  background: #F1F5F9;
  color: #444050;
}
.action-btn-mini.delete:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #EF4444;
}

.pagination-footer-modern {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-info {
  font-size: 13px;
  color: #94A3B8;
  font-weight: 500;
}
</style>
