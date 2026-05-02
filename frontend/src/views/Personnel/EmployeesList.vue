<template>
  <div class="page-container">

    <!-- ─── KPI CARDS (EXTRACTED) ─── -->
    <EmployeeStats :stats="statsCards" />

    <!-- ─── FILTERS BLOCK (SEPARATED) ─── -->
    <div class="filters-card-modern">
      <div class="filter-header">
        <span class="filter-title">ФІЛЬТРИ</span>
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

    <!-- ─── TABLE BLOCK (SEPARATED) ─── -->
    <div class="table-card-modern">
      <el-table 
        v-loading="loading" 
        :data="employees" 
        height="100%"
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
              <span v-if="getStatusClass(scope.row.status_name) === 'status-active'" class="pulse-dot"></span>
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
import { useDark, useToggle } from '@vueuse/core'
import { 
  Plus, Search, Edit, Delete, User, UserFilled, 
  Calendar, TrendCharts, Download, Sunny, Moon 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'
import EmployeeStats from '@/components/Personnel/EmployeeStats.vue'

const router = useRouter()
const isDark = useDark()
const toggleTheme = useToggle(isDark)

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
const statsCards = computed(() => {
  const all = employees.value
  const activeCount = all.filter(e => {
    const s = (e.status_name || '').toLowerCase()
    return !s.includes('звільн') && !s.includes('fired')
  }).length
  
  const now = dayjs()
  const newThisMonth = all.filter(e => {
    if (!e.hire_date) return false
    return dayjs(e.hire_date).isSame(now, 'month')
  }).length

  const firedCount = all.filter(e => (e.status_name || '').toLowerCase().includes('звільн')).length
  const turnoverRate = all.length > 0 ? ((firedCount / all.length) * 100).toFixed(1) : 0

  return [
    { 
      title: 'Всього співробітників', 
      value: total.value || all.length, 
      trend: 12, 
      icon: 'User', 
      colorIcon: '#6366F1', 
      colorBg: 'rgba(99, 102, 241, 0.12)',
      trendUp: true
    },
    { 
      title: 'Активні', 
      value: activeCount, 
      trend: 8, 
      icon: 'UserFilled', 
      colorIcon: '#10B981', 
      colorBg: 'rgba(16, 185, 129, 0.12)',
      trendUp: true
    },
    { 
      title: 'Нові (цей місяць)', 
      value: newThisMonth, 
      trend: 24, 
      icon: 'Calendar', 
      colorIcon: '#F59E0B', 
      colorBg: 'rgba(245, 158, 11, 0.12)',
      trendUp: true
    },
    { 
      title: 'Плинність кадрів', 
      value: `${turnoverRate}%`, 
      trend: -14, 
      icon: 'TrendCharts', 
      colorIcon: '#EF4444', 
      colorBg: 'rgba(239, 68, 68, 0.12)',
      trendUp: false
    }
  ]
})

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
  padding: 0;
  background-color: var(--erp-bg-page);
  height: calc(100vh - 64px - 48px); /* 64px header, 48px view-container padding (24*2) */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  color: #444050;
  font-size: 13px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

/* Dark Mode Overrides */
:deep(.dark) .page-container,
.page-container.dark-mode-manual {
  background-color: #28243D !important;
  color: #D0D4F1 !important;
}

:deep(.dark) .kpi-card-modern,
:deep(.dark) .filters-card-modern,
:deep(.dark) .table-card-modern {
  background-color: #2F3349 !important;
  box-shadow: 0 4px 18px 0 rgba(0, 0, 0, 0.25) !important;
}

:deep(.dark) .kpi-value,
:deep(.dark) .filter-title,
:deep(.dark) .main-name {
  color: #D0D4F1 !important;
}

:deep(.dark) .kpi-label,
:deep(.dark) .kpi-subtext,
:deep(.dark) .sub-pos,
:deep(.dark) .dept-text,
:deep(.dark) .phone-text,
:deep(.dark) .date-text,
:deep(.dark) .pagination-info {
  color: #A3A7C5 !important;
}

:deep(.dark) .el-table {
  --el-table-bg-color: #2F3349 !important;
  --el-table-tr-bg-color: #2F3349 !important;
  --el-table-header-bg-color: #363B54 !important;
  --el-table-border-color: #434968 !important;
  --el-table-text-color: #D0D4F1 !important;
}

:deep(.dark) .el-input__wrapper,
:deep(.dark) .el-select__wrapper {
  background-color: #2F3349 !important;
  box-shadow: 0 0 0 1px #434968 inset !important;
}

:deep(.dark) .el-input__inner {
  color: #D0D4F1 !important;
}

:deep(.dark) .filters-card-modern {
  border-bottom-color: #434968 !important;
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
  background: linear-gradient(135deg, #7367f0 0%, #a8a1f8 100%);
  border: none;
  color: #fff;
  height: 40px;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  box-shadow: 0 4px 14px rgba(115, 103, 240, 0.4);
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  display: flex;
  align-items: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-primary-compact:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
  filter: brightness(1.1);
}

.btn-primary-compact:active {
  transform: translateY(0) scale(0.98);
}

/* KPI Cards */
.kpi-grid-modern {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}
.kpi-card-modern {
  background: rgba(255, 255, 255, 0.9);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: 
    0 2px 4px rgba(15, 20, 34, 0.02),
    0 10px 20px rgba(15, 20, 34, 0.04);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.kpi-card-modern:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 
    0 4px 8px rgba(99, 102, 241, 0.05),
    0 20px 40px rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.kpi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.kpi-icon-wrapper {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.kpi-trend {
  font-size: 12px;
  font-weight: 600;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #444050;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #8E8BA2;
  margin-top: 4px;
}

/* Filters Toolbar */
.filters-card-modern {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  padding: 16px;
  border-radius: 14px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 20px 0 rgba(15, 20, 34, 0.03);
}

.filter-title {
  font-size: 11px;
  font-weight: 800;
  color: #8E8BA2;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  display: block;
  margin-bottom: 12px;
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
  border-radius: 14px;
  box-shadow: 0 2px 12px 0 rgba(15, 20, 34, 0.04);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 0;
}
.erp-table-modern {
  flex: 1;
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
.status-active { 
  background: rgba(16, 185, 129, 0.1); 
  color: #10B981; 
  display: flex;
  align-items: center;
  gap: 6px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
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
