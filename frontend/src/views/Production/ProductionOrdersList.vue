<template>
  <div class="erp-page-container">
    <!-- Header -->
    <div class="erp-toolbar">
      <div class="toolbar-left">
        <h1 class="page-title">Завдання на виробництво ({{ orders.length }})</h1>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="createNew">Створити завдання</el-button>
        <el-button :icon="Refresh" @click="fetchData">Оновити</el-button>
      </div>
    </div>

    <!-- Stats Cards (CRM style) -->
    <div class="stats-overview mb-4">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card blue">
            <div class="stat-label">Всього в роботі</div>
            <div class="stat-value">{{ stats.in_progress }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card red">
            <div class="stat-label">Прострочено</div>
            <div class="stat-value">{{ stats.overdue }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card green">
            <div class="stat-label">Готово сьогодні</div>
            <div class="stat-value">{{ stats.ready_today }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card gray">
            <div class="stat-label">Заплановано</div>
            <div class="stat-value">{{ stats.planned }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Filters Bar -->
    <div class="erp-filters-bar mb-4">
      <el-row :gutter="10" align="middle" style="width: 100%">
        <el-col :span="6">
          <el-input 
            v-model="filters.search" 
            placeholder="Пошук за номером, виробом..." 
            clearable 
            :prefix-icon="Search" 
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="Всі статуси" clearable style="width: 100%">
            <el-option label="🔵 Заплановано" value="draft" />
            <el-option label="🟡 В роботі" value="in_progress" />
            <el-option label="🟢 Готово" value="completed" />
            <el-option label="⚫ Скасовано" value="cancelled" />
            <el-option label="🔴 Прострочено" value="overdue" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.master_id" placeholder="Майстер" clearable style="width: 100%">
            <el-option v-for="m in masters" :key="m.id" :label="m.full_name" :value="m.id" />
          </el-select>
        </el-col>
        <el-col :span="7">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="Від"
            end-placeholder="До"
            style="width: 100%"
          />
        </el-col>
      </el-row>
    </div>

    <!-- Data Table -->
    <div class="erp-table-container" v-loading="loading">
      <el-table
        :data="filteredOrders"
        style="width: 100%"
        class="erp-table"
        stripe
        hover
        @row-dblclick="handleRowDblClick"
      >
        <el-table-column label="№ завдання" width="130">
          <template #default="{ row }">
            <span class="code-text" @click.stop="editOrder(row)">#{{ row.order_number }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="Замовлення (CRM)" width="160">
          <template #default="{ row }">
            <div v-if="row.source_id" class="doc-badge clickable" @click.stop="openSource(row)">
              <el-icon><Document /></el-icon> №{{ row.order_number }}
            </div>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>

        <el-table-column label="Виріб" min-width="200">
          <template #default="{ row }">
            <div class="product-info">
              <span class="product-name">{{ getProductName(row) }}</span>
              <small class="client-name" v-if="row.client">{{ row.client.name }}</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Майстер" width="180">
          <template #default="{ row }">
            <div class="user-avatar-tag" v-if="getMainMaster(row)">
               <el-avatar :size="24" :src="getMainMaster(row).photo_url">{{ getMainMaster(row).full_name?.charAt(0) }}</el-avatar>
               <span>{{ getMainMaster(row).full_name }}</span>
            </div>
            <span v-else class="text-gray-400">Не призначено</span>
          </template>
        </el-table-column>

        <el-table-column label="Етап (поточний)" min-width="180">
          <template #default="{ row }">
            <div class="current-stage" v-if="row.status === 'in_progress' || row.status === 'draft'">
              <el-tag size="small" :type="getStageTagType(row)" effect="light">
                 {{ getCurrentStageName(row) }}
              </el-tag>
            </div>
            <span v-else-if="row.status === 'completed'" class="text-success">Всі етапи завершено</span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="Дедлайн" width="120">
          <template #default="{ row }">
             <span :class="getDeadlineClass(row.due_date, row.status)">
               {{ formatDateSimple(row.due_date) }}
             </span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark" class="status-badge" round>
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column fixed="right" label="Дії" width="80" align="center">
          <template #default="{ row }">
            <el-dropdown trigger="click" @click.stop>
              <span class="el-dropdown-link">
                <el-icon><MoreFilled /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :icon="Edit" @click="editOrder(row)">Відкрити</el-dropdown-item>
                  <el-dropdown-item :icon="Printer">Друк тех. карти</el-dropdown-item>
                  <el-dropdown-item divided type="danger" :icon="Delete" @confirm="deleteOrder(row)">Видалити</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="Немає завдань на виробництво">
             <el-button type="primary" :icon="Plus" @click="createNew">Створити перше завдання</el-button>
          </el-empty>
        </template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Refresh, Search, Edit, Delete, Document, User, MoreFilled, Printer 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const masters = ref([])

const filters = reactive({
  search: '',
  status: '',
  master_id: '',
  dateRange: null
})

const stats = reactive({
  in_progress: 0,
  overdue: 0,
  ready_today: 0,
  planned: 0
})

// Computed
const filteredOrders = computed(() => {
  return orders.value.filter(o => {
    // 1. Search
    const q = filters.search.toLowerCase()
    const matchesSearch = !q || 
      (o.order_number && o.order_number.toLowerCase().includes(q)) ||
      (getProductName(o).toLowerCase().includes(q))
    
    // 2. Status (Special handling for 'overdue')
    let matchesStatus = true
    if (filters.status === 'overdue') {
      matchesStatus = o.status !== 'completed' && o.due_date && dayjs(o.due_date).isBefore(dayjs(), 'day')
    } else if (filters.status) {
      matchesStatus = o.status === filters.status
    }
    
    // 3. Master
    const matchesMaster = !filters.master_id || 
      o.assignments?.some(a => a.employee_id === filters.master_id)
      
    // 4. Date Range
    let matchesDate = true
    if (filters.dateRange && filters.dateRange.length === 2) {
      const start = dayjs(filters.dateRange[0]).startOf('day')
      const end = dayjs(filters.dateRange[1]).endOf('day')
      const docDate = dayjs(o.order_date)
      matchesDate = docDate.isAfter(start) && docDate.isBefore(end)
    }
    
    return matchesSearch && matchesStatus && matchesMaster && matchesDate
  })
})

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const [ordersRes, mastersRes] = await Promise.all([
      api.get('/api/v1/production'),
      api.get('/api/v1/employees') // Fetching all and we'll filter production dept later if needed
    ])
    orders.value = ordersRes.data
    masters.value = mastersRes.data
    calculateStats()
  } catch (error) {
    console.error('Failed to load production orders', error)
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.in_progress = orders.value.filter(o => o.status === 'in_progress').length
  stats.planned = orders.value.filter(o => o.status === 'draft').length
  stats.ready_today = orders.value.filter(o => o.status === 'completed' && dayjs(o.completed_at).isSame(dayjs(), 'day')).length
  stats.overdue = orders.value.filter(o => o.status !== 'completed' && o.due_date && dayjs(o.due_date).isBefore(dayjs(), 'day')).length
}

const getProductName = (row) => {
  if (row.lines && row.lines.length > 0) {
    return row.lines[0].product?.name || 'Виріб #' + (row.lines[0].product_id?.substring(0,4))
  }
  return 'Швидке замовлення'
}

const getMainMaster = (row) => {
  // Return first assigned worker or main master
  return row.assignments?.[0]?.employee
}

const getCurrentStageName = (row) => {
  if (row.status === 'draft') return 'Очікує запуску'
  const pending = row.assignments?.find(a => a.status !== 'completed')
  return pending?.stage?.name || 'Завершення...'
}

const getStageTagType = (row) => {
  if (row.status === 'draft') return 'info'
  return 'warning'
}

const getStatusLabel = (status) => {
  const map = {
    draft: 'Заплановано',
    in_progress: 'В роботі',
    completed: 'Готово',
    cancelled: 'Скасовано'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    draft: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const isOverdue = (date) => {
  if (!date) return false
  return dayjs(date).isBefore(dayjs(), 'day')
}

const isTomorrow = (date) => {
  if (!date) return false
  return dayjs(date).isSame(dayjs().add(1, 'day'), 'day')
}

const getDeadlineClass = (date, status) => {
  if (status === 'completed' || !date) return ''
  if (isOverdue(date)) return 'deadline-overdue'
  if (isTomorrow(date)) return 'deadline-tomorrow'
  return ''
}

const formatDateSimple = (date) => (date ? dayjs(date).format('DD.MM.YY') : '-')

const createNew = () => router.push('/production/orders/new')
const editOrder = (row) => router.push(`/production/orders/${row.id}`)
const handleRowDblClick = (row) => editOrder(row)

const openSource = (row) => {
  if (row.source_type === 'crm' && row.source_id) {
    router.push(`/crm/orders/${row.source_id}`)
  }
}

const deleteOrder = async (row) => {
  try {
    await api.delete(`/api/v1/production/${row.id}`)
    ElMessage.success('Завдання видалено')
    fetchData()
  } catch (err) {
    ElMessage.error('Помилка видалення')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<script>
// Extra exports for icons if needed
export default {
  name: 'ProductionOrdersList'
}
</script>

<style scoped>
.stats-overview {
  margin-top: 10px;
}

.stat-card {
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  border-left: 5px solid #eee;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.1);
}

.stat-card.blue { 
  background: #ecf5ff;
  border-left-color: #409EFF; 
  color: #409EFF;
}
.stat-card.orange { 
  background: #fdf6ec;
  border-left-color: #E6A23C; 
  color: #E6A23C;
}
.stat-card.green { 
  background: #f0f9eb;
  border-left-color: #67C23A; 
  color: #67C23A;
}
.stat-card.gray { 
  background: #f4f4f5;
  border-left-color: #909399; 
  color: #909399;
}

.stat-card.red {
  background: #fef0f0;
  border-left-color: #F56C6C;
  color: #F56C6C;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.code-text {
  font-family: 'Roboto Mono', monospace;
  font-weight: 600;
  color: #409eff;
  cursor: pointer;
}

.product-info {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: 500;
  color: #303133;
}

.client-name {
  color: #909399;
  font-size: 11px;
}

.doc-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f0f7ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #409eff;
  border: 1px solid #d9ecff;
}

.doc-badge.clickable {
  cursor: pointer;
}

.doc-badge.clickable:hover {
  background: #ecf5ff;
}

.user-avatar-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.status-badge {
  min-width: 100px;
  font-weight: 600;
  font-size: 11px;
}

.deadline-overdue {
  color: #f56c6c;
  font-weight: 700;
}

.deadline-tomorrow {
  color: #e6a23c;
  font-weight: 700;
}

.mb-4 { margin-bottom: 20px; }
.ml-2 { margin-left: 8px; }
.text-gray-400 { color: #c0c4cc; }
.text-success { color: #67c23a; }
</style>
