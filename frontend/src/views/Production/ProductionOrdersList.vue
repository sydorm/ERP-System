<template>
  <div class="orders-page">
    <div class="fixed-top-area">
      <!-- ===== STAT CARDS (CRM Style) ===== -->
      <div class="kimi-stats-row">
        <!-- Всього в роботі -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Всього в роботі</p>
            <p class="kimi-stat-value text-indigo-600">{{ stats.in_progress }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
            <el-icon><Document /></el-icon>
          </div>
        </div>
        <!-- Прострочено -->
        <div class="kimi-stat-card kimi-stat-rose">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Прострочено</p>
            <p class="kimi-stat-value text-rose-600">{{ stats.overdue }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-rose-100 text-rose-600">
            <el-icon><Clock /></el-icon>
          </div>
        </div>
        <!-- Готово сьогодні -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Готово сьогодні</p>
            <p class="kimi-stat-value text-emerald-600">{{ stats.completed_today }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
            <el-icon><Check /></el-icon>
          </div>
        </div>
        <!-- Заплановано -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Заплановано</p>
            <p class="kimi-stat-value text-amber-600">{{ stats.planned }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
            <el-icon><Calendar /></el-icon>
          </div>
        </div>
      </div>

      <!-- ===== FILTER BAR (CRM Style) ===== -->
      <div class="kimi-filter-bar">
        <div class="kimi-filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="Пошук за номером, виробом..."
            :prefix-icon="Search"
            clearable
            class="kimi-search-input"
          />
          <el-select
            v-model="filterStatus"
            placeholder="Всі статуси"
            clearable
            style="width:155px"
            class="kimi-status-select"
          >
            <el-option label="Всі статуси" value="" />
            <el-option label="Заплановано" value="draft" />
            <el-option label="В роботі" value="in_progress" />
            <el-option label="Готово" value="completed" />
            <el-option label="Скасовано" value="cancelled" />
          </el-select>
          
          <el-select
            v-model="filterMaster"
            placeholder="Майстер"
            clearable
            style="width:155px"
            class="kimi-status-select"
          >
            <el-option v-for="m in masters" :key="m.id" :label="m.full_name" :value="m.id" />
          </el-select>

          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="—"
            start-placeholder="Від"
            end-placeholder="До"
            format="DD.MM.YYYY"
            value-format="YYYY-MM-DD"
            clearable
            class="kimi-date-picker"
          />

          <button class="kimi-adv-btn">
            <el-icon><Filter /></el-icon>
            <span class="adv-btn-label">Фільтри</span>
          </button>
          
          <button class="kimi-adv-btn">
            <el-icon><Setting /></el-icon>
            <span class="adv-btn-label">Стовпці</span>
          </button>

          <el-button class="kimi-refresh-btn" @click="fetchData" title="Оновити">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        <div class="kimi-filter-right">
          <button class="kimi-primary-btn" @click="createNew">
            <el-icon><Plus /></el-icon> Створити завдання
          </button>
        </div>
      </div>
    </div>

    <!-- ===== TABLE CARD ===== -->
    <div class="table-card scrollable-table-area mt-2">
      <el-table
        v-loading="loading"
        :data="filteredOrders"
        size="small"
        height="100%"
        style="width: 100%"
        class="orders-table"
        row-class-name="kimi-row"
        header-row-class-name="kimi-header-row"
        @row-click="handleRowClick"
      >
        <el-table-column type="selection" width="40" align="center" />
        
        <el-table-column label="№" width="46" align="center">
          <template #default="{ $index }">
            <span class="row-num text-slate-400">{{ $index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column label="НОМЕР / ДАТА" width="160" prop="order_number">
          <template #default="{ row }">
            <div class="num-date-cell">
              <span class="kimi-text-sm kimi-font-medium kimi-text-indigo-600">{{ row.order_number }}</span>
              <span class="kimi-text-xxs kimi-text-slate-400">{{ formatDateSimple(row.order_date) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="КЛІЄНТ" min-width="160">
          <template #default="{ row }">
            <span class="kimi-text-sm font-medium">{{ getClientName(row.client_id) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="ВИРІБ" min-width="180">
          <template #default="{ row }">
            <div class="kimi-text-sm">{{ getProductName(row) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="МАЙСТЕР" min-width="160">
          <template #default="{ row }">
            <span class="kimi-text-sm">{{ getMasterName(row) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="ЕТАП" width="140">
          <template #default="{ row }">
            <el-tag v-if="getCurrentStage(row)" size="small" effect="plain" type="info">
              {{ getCurrentStage(row) }}
            </el-tag>
            <span v-else class="text-xs text-gray-400">—</span>
          </template>
        </el-table-column>

        <el-table-column label="ДЕДЛАЙН" width="130" align="center">
          <template #default="{ row }">
            <div v-if="row.due_date" class="date-cell" :class="getDateClass(row.due_date, row.status)">
              <span class="date-cell-dot" />
              <span class="date-cell-text">{{ formatDateSimple(row.due_date) }}</span>
            </div>
            <span v-else class="kimi-text-xs text-slate-400">—</span>
          </template>
        </el-table-column>

        <el-table-column label="СТАТУС" width="140" align="center">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getStatusBadgeClass(row.status, row.due_date)">
              {{ getStatusLabel(row.status, row.due_date) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="ДІЇ" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <div @click.stop class="kimi-actions-col">
              <button class="kimi-ghost-btn" @click.stop="() => handleEdit(row)" title="Редагувати">
                <el-icon class="kimi-text-indigo-400"><Edit /></el-icon>
              </button>
              <button class="kimi-ghost-btn" @click.stop="() => handleDelete(row)" title="Видалити">
                <el-icon class="kimi-text-rose-400"><Delete /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <el-empty description="Немає завдань на виробництво">
             <el-button type="primary" :icon="Plus" @click="createNew">Створити перше завдання</el-button>
          </el-empty>
        </template>
      </el-table>

      <!-- PAGINATION -->
      <div class="pagination-footer">
        <span class="total-hint">Показано {{ filteredOrders.length }} з {{ orders.length }}</span>
        <div class="custom-pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="orders.length"
            background
            layout="prev, pager, next"
            class="custom-pagination-numeric"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Refresh, Edit, Delete, Clock, Check, Calendar, Document, Filter, Setting
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const masters = ref([])
const clients = ref([])
const products = ref([])

// Filters
const searchQuery = ref('')
const filterStatus = ref('')
const filterMaster = ref('')
const dateRange = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)

// Stats
const stats = computed(() => {
  const now = dayjs().startOf('day')
  return {
    in_progress: orders.value.filter(o => ['in_progress', 'released'].includes(o.status)).length,
    overdue: orders.value.filter(o => o.status !== 'completed' && o.due_date && dayjs(o.due_date).isBefore(now)).length,
    completed_today: orders.value.filter(o => o.status === 'completed' && dayjs(o.updated_at).isSame(now, 'day')).length,
    planned: orders.value.filter(o => o.status === 'draft').length
  }
})

const filteredOrders = computed(() => {
  let list = [...orders.value]
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => o.order_number?.toLowerCase().includes(q))
  }
  if (filterStatus.value) {
    list = list.filter(o => o.status === filterStatus.value)
  }
  if (filterMaster.value) {
    list = list.filter(o => o.assignments?.some(a => a.employee_id === filterMaster.value))
  }
  if (dateRange.value) {
    const [start, end] = dateRange.value
    list = list.filter(o => o.order_date >= start && o.order_date <= end)
  }
  return list.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
})

// HELPERS
const formatDateSimple = (d) => d ? dayjs(d).format('DD.MM.YY') : '-'

const getClientName = (id) => clients.value.find(c => c.id === id)?.name || 'Вручну'

const getProductName = (row) => {
  if (row.lines?.length > 0) {
    const prodId = row.lines[0].product_id
    return products.value.find(p => p.id === prodId)?.name || 'Виріб #' + prodId
  }
  return '-'
}

const getMasterName = (row) => {
  if (row.assignments?.length > 0) {
    const empId = row.assignments[0].employee_id
    return masters.value.find(m => m.id === empId)?.full_name || 'Не призначено'
  }
  return '—'
}

const getCurrentStage = (row) => {
  if (row.assignments?.length > 0) {
    const active = row.assignments.find(a => a.status !== 'completed')
    return active ? (active.stage_label || active.stage?.name) : 'Всі завершені'
  }
  return null
}

const getDateClass = (date, status) => {
  if (!date || status === 'completed') return ''
  const d = dayjs(date)
  const now = dayjs().startOf('day')
  if (d.isBefore(now)) return 'date-overdue'
  if (d.isSame(now.add(1, 'day'), 'day')) return 'date-today' 
  return ''
}

const getStatusBadgeClass = (status, dueDate) => {
  if (status === 'completed') return 'kimi-status-emerald'
  if (status === 'cancelled') return 'kimi-status-slate'
  if (status === 'in_progress') return 'kimi-status-blue'
  
  const now = dayjs().startOf('day')
  if (dueDate && dayjs(dueDate).isBefore(now) && status !== 'completed') return 'kimi-status-rose'
  
  return 'kimi-status-slate' // Planned / Draft
}

const getStatusLabel = (status, dueDate) => {
  const now = dayjs().startOf('day')
  if (dueDate && dayjs(dueDate).isBefore(now) && status !== 'completed') return 'ПРОСТРОЧЕНО'
  
  const map = {
    draft: 'ЗАПЛАНОВАНО',
    released: 'В РОБОТІ',
    in_progress: 'В РОБОТІ',
    completed: 'ГОТОВО',
    cancelled: 'СКАСОВАНО'
  }
  return map[status] || status.toUpperCase()
}

// ACTIONS
const createNew = () => router.push('/production/orders/new')
const handleEdit = (row) => router.push(`/production/orders/${row.id}`)
const handleRowClick = (row) => handleEdit(row)

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити завдання ${row.order_number}?`, 'Увага', { type: 'warning' })
    .then(async () => {
      await api.delete(`/api/v1/production/${row.id}`)
      ElMessage.success('Видалено')
      fetchData()
    })
}

const fetchData = async () => {
  loading.value = true
  try {
    const [ordersRes, mastersRes, clientsRes, productsRes] = await Promise.all([
      api.get('/api/v1/production/'),
      api.get('/api/v1/employees/'),
      api.get('/api/v1/counterparties/'),
      api.get('/api/v1/products/')
    ])
    orders.value = ordersRes.data
    masters.value = mastersRes.data
    clients.value = clientsRes.data
    products.value = productsRes.data
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.orders-page { 
  display: flex; flex-direction: column; height: calc(100vh - 60px); 
  padding: 0 20px 20px; background: #f1f5f9; 
}

.fixed-top-area { flex-shrink: 0; padding-top: 20px; }

/* ===== KIMI STATS ===== */
.kimi-stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
.kimi-stat-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-radius: 12px; border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02); transition: transform 0.2s;
}
.kimi-stat-card:hover { transform: translateY(-2px); }

.kimi-stat-indigo { background: linear-gradient(to bottom right, #eef2ff, #fff); }
.kimi-stat-rose { background: linear-gradient(to bottom right, #fff1f2, #fff); }
.kimi-stat-emerald { background: linear-gradient(to bottom right, #ecfdf5, #fff); }
.kimi-stat-amber { background: linear-gradient(to bottom right, #fffbeb, #fff); }

.kimi-stat-label { font-size: 13px; color: #64748b; font-weight: 500; margin: 0; }
.kimi-stat-value { font-size: 24px; font-weight: 700; margin: 4px 0 0 0; }

.text-indigo-600 { color: #4f46e5; }
.text-rose-600 { color: #e11d48; }
.text-emerald-600 { color: #059669; }
.text-amber-600 { color: #d97706; }

.kimi-stat-icon-wrapper {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.bg-indigo-100 { background: #e0e7ff; }
.bg-rose-100 { background: #ffe4e6; }
.bg-emerald-100 { background: #d1fae5; }
.bg-amber-100 { background: #fef3c7; }

/* ===== FILTER BAR ===== */
.kimi-filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
.kimi-filter-left { display: flex; align-items: center; gap: 8px; flex: 1; }

.kimi-search-input { max-width: 320px; }
.kimi-search-input :deep(.el-input__wrapper) { border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.kimi-status-select :deep(.el-select__wrapper) { border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.kimi-date-picker { width: 220px !important; }
.kimi-date-picker :deep(.el-input__wrapper) { border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.kimi-adv-btn {
  display: flex; align-items: center; gap: 6px; padding: 0 12px; height: 32px;
  border: 1px solid #e2e8f0; border-radius: 6px; background: #fff;
  color: #64748b; font-size: 13px; cursor: pointer; transition: all 0.15s;
}
.kimi-adv-btn:hover { border-color: #4f46e5; color: #4f46e5; }

.kimi-refresh-btn { border-radius: 6px !important; height: 32px; }

.kimi-primary-btn {
  background: #4f46e5; color: #fff; border: none; border-radius: 6px;
  font-size: 14px; font-weight: 500; padding: 8px 16px; cursor: pointer;
  display: flex; align-items: center; gap: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.kimi-primary-btn:hover { background: #4338ca; }

/* ===== TABLE ===== */
.table-card { 
  background: #fff; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; 
  flex: 1; display: flex; flex-direction: column;
}
.orders-table :deep(.kimi-header-row th) { 
  background: #f8fafc !important; color: #64748b; font-size: 11px; 
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  border-bottom: 1px solid #e2e8f0 !important;
}
.orders-table :deep(.kimi-row td) { padding: 8px 0 !important; cursor: pointer; }

.kimi-text-sm { font-size: 13px; }
.kimi-text-xxs { font-size: 10px; }
.kimi-font-medium { font-weight: 500; }
.kimi-text-indigo-600 { color: #4f46e5; }
.kimi-text-slate-400 { color: #94a3b8; }

.kimi-badge { 
  display: inline-flex; align-items: center; padding: 2px 10px; 
  border-radius: 14px; font-size: 10px; font-weight: 700; white-space: nowrap;
}
.kimi-status-blue { background: #dbeafe; color: #2563eb; }
.kimi-status-emerald { background: #d1fae5; color: #059669; }
.kimi-status-rose { background: #ffe4e6; color: #e11d48; }
.kimi-status-slate { background: #f1f5f9; color: #475569; }

/* DATE CELL */
.date-cell { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 6px; }
.date-cell-dot { width: 6px; height: 6px; border-radius: 50%; background: #94a3b8; }
.date-cell-text { font-size: 12px; font-weight: 500; }

.date-overdue { background: #fff1f2; }
.date-overdue .date-cell-text { color: #dc2626; font-weight: 700; }
.date-overdue .date-cell-dot { background: #dc2626; }

.date-today { background: #fffbeb; }
.date-today .date-cell-text { color: #d97706; font-weight: 700; }
.date-today .date-cell-dot { background: #d97706; }

.kimi-actions-col { display: flex; gap: 4px; justify-content: center; }
.kimi-ghost-btn { background: none; border: none; cursor: pointer; padding: 4px; border-radius: 6px; }
.kimi-ghost-btn:hover { background: #f1f5f9; }
.kimi-text-indigo-400 { color: #818cf8; }
.kimi-text-rose-400 { color: #fb7185; }

.pagination-footer { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 12px 20px; border-top: 1px solid #e2e8f0; background: #f8fafc;
}
.total-hint { font-size: 12px; color: #64748b; }
</style>
