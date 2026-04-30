<template>
  <div class="purchase-orders-page">
    <!-- Breadcrumbs & Header -->
    <div class="breadcrumb-nav">
      Закупівлі <el-icon><ArrowRight /></el-icon> Замовлення постачальникам
    </div>

    <div class="page-header">
      <div class="header-content">
        <h1>Замовлення постачальникам <el-icon class="fav-star"><Star /></el-icon></h1>
      </div>
      <div class="header-actions">
        <el-button class="btn-export">
          <el-icon><Download /></el-icon> Експорт
        </el-button>
        <el-dropdown split-button type="primary" class="btn-create-split" @click="handleCreate">
          <el-icon><Plus /></el-icon> Створити замовлення
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="openNeedsDrawer">З потреб виробництва</el-dropdown-item>
              <el-dropdown-item>Імпорт з Excel</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- KPI Analytics Cards -->
    <div class="kpi-grid">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="kpi-card">
        <div class="kpi-main">
          <div class="kpi-icon-box" :style="{ backgroundColor: kpi.bg, color: kpi.color }">
            <el-icon><component :is="kpi.icon" /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value">{{ kpi.value }}</div>
          </div>
          <div class="kpi-chart">
            <svg width="64" height="32" viewBox="0 0 64 32">
              <path :d="kpi.path" :stroke="kpi.color" stroke-width="2" fill="none" stroke-linecap="round" />
            </svg>
          </div>
        </div>
        <div class="kpi-footer" :class="kpi.trendClass">
          <span v-if="kpi.trend">{{ kpi.trend }} порівняно з мин. місяцем</span>
          <span v-else-if="kpi.sub">{{ kpi.sub }}</span>
        </div>
      </div>
    </div>

    <!-- Filter Panel -->
    <div class="filter-panel">
      <div class="filter-row">
        <div class="search-wrap">
          <el-icon><Search /></el-icon>
          <input type="text" v-model="filters.search" placeholder="Пошук за номером, постачальником, матеріалом..." />
        </div>
        
        <div class="filter-group">
          <span class="filter-label">Статус:</span>
          <el-select v-model="filters.status" placeholder="Усі" clearable class="minimal-select">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </div>

        <div class="filter-group">
          <span class="filter-label">Оплата:</span>
          <el-select v-model="filters.payment" placeholder="Усі" clearable class="minimal-select">
            <el-option v-for="p in paymentOptions" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </div>

        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          format="DD.MM.YYYY"
          start-placeholder="01.05.2026"
          end-placeholder="31.05.2026"
          class="date-range-picker"
        />

        <el-button class="btn-filters-more"><el-icon><Filter /></el-icon> Фільтри <el-icon><ArrowDown /></el-icon></el-button>
        <el-button link class="btn-clear-all" @click="resetFilters">Очистити</el-button>
        <el-button circle link class="btn-table-settings"><el-icon><Setting /></el-icon></el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-surface">
      <el-table
        v-loading="loading"
        :data="pagedOrders"
        class="nexora-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />
        
        <el-table-column label="№ / Дата" width="160" sortable>
          <template #default="{ row }">
            <div class="cell-id">{{ row.order_number }}</div>
            <div class="cell-date">{{ formatDate(row.order_date) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Постачальник" min-width="220">
          <template #default="{ row }">
            <div class="supplier-cell">
              <div class="supplier-logo" :style="{ backgroundColor: getSupplierColor(row.supplier_id) }">
                {{ getCounterpartyName(row.supplier_id).charAt(0) }}
              </div>
              <div class="supplier-info">
                <div class="supplier-name">{{ getCounterpartyName(row.supplier_id) }}</div>
                <div class="supplier-code">Код: {{ row.supplier_id?.slice(0,8) || '30567891' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Матеріали" min-width="220">
          <template #default="{ row }">
            <div class="materials-info">
              <div class="mat-count">{{ (row.lines || []).length }} позиції</div>
              <div class="mat-list">{{ getMaterialPreview(row).text }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="160">
          <template #default="{ row }">
            <div class="status-dot-wrap">
              <span class="status-dot" :style="{ backgroundColor: getStatusColor(normalizeStatus(row)) }"></span>
              <span class="status-text" :style="{ color: getStatusColor(normalizeStatus(row)) }">
                {{ getStatusLabel(normalizeStatus(row)) }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="180">
          <template #default="{ row }">
            <div class="payment-dot-wrap">
              <span class="payment-dot" :style="{ backgroundColor: getPaymentColor(row) }"></span>
              <div class="payment-info">
                <div class="pay-label">{{ getPaymentLabel(row) }}</div>
                <div class="pay-percent">{{ getPaymentPercent(row) }}%</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Очікується" width="150">
          <template #default="{ row }">
            <div class="expected-info">
              <div class="exp-date">{{ formatDate(row.expected_date) }}</div>
              <div class="exp-relative" :class="{ 'overdue': getOverdueDays(row) > 0 }">
                {{ getRelativeTime(row) }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Сума" width="150" align="right">
          <template #default="{ row }">
            <div class="amount-cell">
              <div class="total">{{ formatCurrency(row.total_amount) }}</div>
              <div class="tax">з ПДВ</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="60" align="center" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="cmd => handleRowCommand(cmd, row)">
              <el-button link class="btn-row-more">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view">Переглянути</el-dropdown-item>
                  <el-dropdown-item command="edit">Редагувати</el-dropdown-item>
                  <el-dropdown-item command="delete" divided class="text-danger">Видалити</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <div class="page-size-picker">
          Показати 
          <el-select v-model="pageSize" size="small" style="width: 60px; margin: 0 8px;">
            <el-option v-for="s in [10, 20, 50]" :key="s" :label="s" :value="s" />
          </el-select>
          з {{ filteredOrders.length }}
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredOrders.length"
          layout="prev, pager, next"
          class="nexora-pagination"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Download, Filter, Setting, MoreFilled, Star, ArrowRight, ArrowDown,
  List, Van, Warning, Wallet, Money, Loading
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const suppliers = ref([])
const products = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  search: '',
  status: '',
  payment: '',
  dateRange: null
})

const kpiCards = computed(() => [
  { label: 'Усього замовлень', value: orders.value.length, icon: 'ShoppingCart', bg: '#F1F5FF', color: '#1463FF', trend: '+18%', trendClass: 'trend-up', path: 'M0 20C10 25 20 15 30 18C40 21 50 10 64 5' },
  { label: 'Очікується постачання', value: expectedOrders.value.length, icon: 'Box', bg: '#F0FDF4', color: '#10B981', sub: formatCurrency(expectedAmount.value), path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 10' },
  { label: 'На підтвердженні', value: 17, icon: 'Check', bg: '#F0F9FF', color: '#0EA5E9', sub: '2 125 700,00 ₴', path: 'M0 20C10 15 20 18 30 12C40 6 50 10 64 8' },
  { label: 'Прострочено', value: overdueOrders.value.length, icon: 'Warning', bg: '#FEF2F2', color: '#EF4444', sub: '895 250,00 ₴', path: 'M0 10C10 15 20 12 30 18C40 24 50 20 64 25' },
  { label: 'Сума замовлень', value: formatCurrency(totalAmount.value), icon: 'Wallet', bg: '#F0FDFA', color: '#0D9488', trend: '+22%', trendClass: 'trend-up', path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 5' },
])

const expectedOrders = computed(() => orders.value.filter(o => ['ordered', 'expected'].includes(normalizeStatus(o))))
const expectedAmount = computed(() => expectedOrders.value.reduce((sum, o) => sum + Number(o.total_amount || 0), 0))
const overdueOrders = computed(() => orders.value.filter(o => getOverdueDays(o) > 0))
const totalAmount = computed(() => orders.value.reduce((sum, o) => sum + Number(o.total_amount || 0), 0))

const statusOptions = [
  { value: 'draft', label: 'Чернетка' },
  { value: 'ordered', label: 'Підтверджено' },
  { value: 'expected', label: 'На підтвердженні' },
  { value: 'partial_received', label: 'Очікується' },
  { value: 'received', label: 'Отримано' },
  { value: 'cancelled', label: 'Скасовано' },
]

const paymentOptions = [
  { value: 'unpaid', label: 'Не оплачено' },
  { value: 'partial', label: 'Частково оплачено' },
  { value: 'paid', label: 'Оплачено' },
]

const filteredOrders = computed(() => {
  let list = orders.value
  const q = filters.search.toLowerCase()
  if (q) {
    list = list.filter(o => 
      o.order_number?.toLowerCase().includes(q) || 
      getCounterpartyName(o.supplier_id).toLowerCase().includes(q)
    )
  }
  return list
})

const pagedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredOrders.value.slice(start, start + pageSize.value)
})

const fetchOrders = async () => {
  loading.value = true
  try {
    const [ordersRes, suppliersRes, productsRes] = await Promise.all([
      api.get('/api/v1/purchase-orders', { params: { limit: 500 } }),
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/products')
    ])
    orders.value = ordersRes.data || []
    suppliers.value = suppliersRes.data || []
    products.value = productsRes.data || []
  } catch {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const normalizeStatus = (row) => {
  if (row.status === 'draft') return 'draft'
  if (row.status === 'done' || row.status === 'received') return 'received'
  if (row.status === 'cancelled') return 'cancelled'
  if (getOverdueDays(row) > 0) return 'overdue'
  if (row.received_quantity > 0) return 'partial_received'
  return 'ordered'
}

const getStatusLabel = v => {
  if (v === 'overdue') return 'Прострочено'
  return statusOptions.find(s => s.value === v)?.label || 'Підтверджено'
}

const getStatusColor = v => {
  if (v === 'draft') return '#94A3B8'
  if (v === 'ordered') return '#10B981'
  if (v === 'expected') return '#3B82F6'
  if (v === 'partial_received') return '#F59E0B'
  if (v === 'overdue') return '#EF4444'
  if (v === 'received') return '#10B981'
  return '#64748B'
}

const getPaymentStatus = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  if (total > 0 && paid >= total) return 'paid'
  if (paid > 0) return 'partial'
  return 'unpaid'
}

const getPaymentColor = row => {
  const s = getPaymentStatus(row)
  if (s === 'paid') return '#10B981'
  if (s === 'partial') return '#3B82F6'
  return '#64748B'
}

const getPaymentLabel = row => {
  const s = getPaymentStatus(row)
  if (s === 'paid') return 'Оплачено'
  if (s === 'partial') return 'Частково оплачено'
  return 'Не оплачено'
}

const getPaymentPercent = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  if (!total) return 0
  return Math.round((paid / total) * 100)
}

const getSupplierColor = id => {
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return colors[id?.length % colors.length] || '#3B82F6'
}

const getCounterpartyName = id => suppliers.value.find(s => s.id === id)?.name || '—'
const getProductName = id => products.value.find(p => p.id === id)?.name || ''
const getMaterialPreview = row => {
  const names = (row.lines || []).map(l => getProductName(l.product_id)).filter(Boolean)
  return { text: names.slice(1).join(', ') || 'Металопрокат, Кріплення...' }
}

const getRelativeTime = row => {
  const days = getOverdueDays(row)
  if (days > 0) return `прострочено на ${days} дн.`
  if (!row.expected_date) return '—'
  const diff = new Date(row.expected_date) - new Date()
  const d = Math.ceil(diff / 86400000)
  return d > 0 ? `через ${d} дн.` : 'сьогодні'
}

const getOverdueDays = row => {
  if (!row.expected_date || normalizeStatus(row) === 'received') return 0
  const diff = new Date() - new Date(row.expected_date)
  return Math.max(0, Math.floor(diff / 86400000))
}

const formatDate = d => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatCurrency = v => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(v)

const handleCreate = () => router.push('/purchases/orders/new')
const resetFilters = () => { filters.search = ''; filters.status = ''; filters.payment = ''; filters.dateRange = null }
const handleRowCommand = (cmd, row) => {
  if (cmd === 'edit') router.push(`/purchases/orders/${row.id}`)
  if (cmd === 'delete') handleDelete(row)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити замовлення ${row.order_number}?`, 'Увага', { type: 'warning' }).then(async () => {
    await api.delete(`/api/v1/purchase-orders/${row.id}`)
    ElMessage.success('Видалено')
    fetchOrders()
  })
}

onMounted(fetchOrders)
</script>

<style scoped>
.purchase-orders-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.breadcrumb-nav {
  font-size: 12px;
  color: var(--erp-text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 800;
  color: var(--erp-text-heading);
  display: flex;
  align-items: center;
  gap: 12px;
}

.fav-star {
  font-size: 20px;
  color: #CBD5E1;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-export {
  background: #FFF;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  height: 44px;
  font-weight: 600;
}

.btn-create-split :deep(.el-button) {
  height: 44px;
  border-radius: 10px;
  font-weight: 700;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.kpi-card {
  background: #FFF;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 110px;
}

.kpi-main {
  display: grid;
  grid-template-columns: 48px 1fr 64px;
  align-items: flex-start;
  gap: 12px;
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 20px;
}

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--erp-text-muted);
}

.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--erp-text-heading);
  margin-top: 4px;
}

.kpi-footer {
  font-size: 11px;
  margin-top: 12px;
  font-weight: 600;
}

.trend-up { color: #10B981; }

/* Filter Panel */
.filter-panel {
  background: #FFF;
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #94A3B8;
}

.search-wrap input {
  border: none;
  outline: none;
  width: 100%;
  font-size: 13px;
  color: var(--erp-text-main);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.filter-label {
  font-size: 13px;
  color: var(--erp-text-muted);
}

.minimal-select :deep(.el-input__wrapper) {
  box-shadow: none !important;
  padding: 0;
  background: transparent;
}

.minimal-select :deep(.el-input__inner) {
  font-weight: 600;
  color: var(--erp-text-heading);
  font-size: 13px;
}

.date-range-picker {
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  height: 36px;
  width: 240px;
}

.btn-filters-more {
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  height: 36px;
  font-weight: 600;
}

.btn-clear-all {
  color: #94A3B8;
  font-size: 13px;
  font-weight: 600;
}

/* Table */
.table-surface {
  background: #FFF;
  border-radius: 20px;
  padding: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
}

.nexora-table :deep(.el-table__header th) {
  background: #FFF !important;
  color: #94A3B8;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 12px 0;
  border-bottom: 1px solid #F1F5F9;
}

.cell-id { color: #64748B; font-weight: 700; font-size: 13px; }
.cell-date { color: #94A3B8; font-size: 11px; margin-top: 2px; }

.supplier-cell { display: flex; align-items: center; gap: 12px; }
.supplier-logo { width: 32px; height: 32px; border-radius: 8px; color: #FFF; display: grid; place-items: center; font-weight: 800; font-size: 14px; }
.supplier-name { font-weight: 700; color: #334155; font-size: 13px; }
.supplier-code { font-size: 11px; color: #94A3B8; }

.materials-info .mat-count { font-size: 12px; font-weight: 700; color: #475569; }
.materials-info .mat-list { font-size: 11px; color: #94A3B8; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.status-dot-wrap { display: flex; align-items: center; gap: 8px; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-text { font-size: 12px; font-weight: 700; }

.payment-dot-wrap { display: flex; align-items: center; gap: 8px; }
.payment-dot { width: 6px; height: 6px; border-radius: 50%; }
.pay-label { font-size: 12px; font-weight: 700; color: #475569; }
.pay-percent { font-size: 11px; color: #94A3B8; }

.expected-info .exp-date { font-size: 12px; font-weight: 600; color: #334155; }
.expected-info .exp-relative { font-size: 11px; color: #10B981; font-weight: 700; }
.expected-info .exp-relative.overdue { color: #EF4444; }

.amount-cell .total { font-weight: 800; font-size: 14px; color: #1E293B; }
.amount-cell .tax { font-size: 10px; color: #94A3B8; text-transform: uppercase; }

.btn-row-more { font-size: 18px; color: #CBD5E1; }

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 8px;
}

.page-size-picker { font-size: 12px; color: #94A3B8; }
</style>
