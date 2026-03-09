<template>
  <div class="orders-page">
    <div class="fixed-top-area">
      <!-- ===== PAGE HEADER ===== -->
      <div class="page-header">
      <div>
        <h1 class="page-title">Замовлення клієнтів</h1>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Продажі</el-breadcrumb-item>
          <el-breadcrumb-item>Замовлення</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-actions">
        <el-button :icon="Download" @click="handleExportCSV" class="btn-export">
          Excel
        </el-button>
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-create">
          Створити замовлення
        </el-button>
      </div>
    </div>

    <!-- ===== STAT CARDS ===== -->
    <div class="stats-row">
      <!-- Всього замовлень -->
      <div class="stat-card">
        <div class="stat-icon" style="background:#ede9fe"><el-icon style="color:#6366f1"><Document /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ orders.length }}</div>
          <div class="stat-label">Всього замовлень</div>
        </div>
        <div class="stat-dot" style="background:#6366f1"></div>
      </div>
      <!-- Загальна сума -->
      <div class="stat-card">
        <div class="stat-icon" style="background:#d1fae5"><el-icon style="color:#10b981"><Wallet /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value stat-value--sum">{{ formatCurrency(orders.reduce((s, o) => s + (+o.total_amount || 0), 0)) }}</div>
          <div class="stat-label">Загальна сума</div>
        </div>
        <div class="stat-dot" style="background:#10b981"></div>
      </div>
      <!-- В роботі -->
      <div class="stat-card">
        <div class="stat-icon" style="background:#fef3c7"><el-icon style="color:#f59e0b"><Clock /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ orders.filter(o => ['confirmed','draft','shipped'].includes(o.status)).length }}</div>
          <div class="stat-label">В роботі</div>
        </div>
        <div class="stat-dot" style="background:#f59e0b"></div>
      </div>
      <!-- Виконано -->
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0fdf4"><el-icon style="color:#22c55e"><Check /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ orders.filter(o => o.status === 'completed').length }}</div>
          <div class="stat-label">Виконано</div>
        </div>
        <div class="stat-dot" style="background:#22c55e"></div>
      </div>
    </div>

    <!-- ===== QUICK FILTER TABS ===== -->
    <div class="quick-filters">
      <button
        class="filter-tab"
        :class="{ active: activeTab === '' }"
        @click="setTab('')"
      >Всі <span class="tab-count">{{ orders.length }}</span></button>
      <button
        v-for="s in orderStatuses"
        :key="s.code"
        class="filter-tab"
        :class="{ active: activeTab === s.code }"
        :style="activeTab === s.code ? { background: getStatusHex(s.color), color: '#fff', borderColor: getStatusHex(s.color) } : {}"
        @click="setTab(s.code)"
      >
        {{ s.name }}
        <span class="tab-count" :style="activeTab === s.code ? { background: 'rgba(255,255,255,0.25)', color: '#fff' } : {}">
          {{ orders.filter(o => o.status === s.code).length }}
        </span>
      </button>
    </div>

    <!-- ===== SEARCH & FILTER BAR ===== -->
    <div class="filter-bar">
      <el-input
        ref="searchInputRef"
        v-model="searchQuery"
        placeholder="Пошук за номером або клієнтом або телефоном..."
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
        class="search-input"
      />
      <el-select
        v-model="activeTab"
        placeholder="Всі статуси"
        clearable
        style="width:155px;flex-shrink:0"
        @change="(v) => setTab(v || '')"
        class="status-select"
      >
        <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code" />
      </el-select>
      <div style="width: 230px; flex-shrink: 0; overflow: hidden;">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          size="small"
          style="width: 230px !important"
          range-separator="—"
          start-placeholder="Від"
          end-placeholder="До"
          format="DD.MM.YYYY"
          value-format="YYYY-MM-DD"
          @change="fetchOrders"
          class="date-picker"
        />
      </div>
      <el-button :icon="Refresh" circle @click="fetchOrders" class="refresh-btn" title="Оновити" />
      <el-button link class="reset-btn" @click="handleReset" v-if="searchQuery || dateRange || activeTab">
        Скинути фільтри
      </el-button>
    </div>

    <!-- ===== BULK ACTION BAR ===== -->
    <transition name="bulk-bar">
      <div class="bulk-bar" v-if="selected.length > 0">
        <el-icon><Select /></el-icon>
        <span>Виділено: <strong>{{ selected.length }}</strong></span>
        <el-divider direction="vertical" />
        <el-button size="small" type="primary" @click="bulkConfirm">Підтвердити</el-button>
        <el-button size="small" type="danger" plain @click="bulkDelete">Видалити</el-button>
        <el-button size="small" link @click="selected = []">Скасувати вибір</el-button>
      </div>
    </transition>
    </div> <!-- END fixed-top-area -->

    <!-- ===== MAIN TABLE CARD ===== -->
    <div class="table-card scrollable-table-area">
      <el-table
        v-loading="loading"
        :data="filteredOrders"
        height="100%"
        size="small"
        style="width: 100%"
        class="orders-table"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        @row-click="handleRowClick"
        row-class-name="order-row"
      >
        <el-table-column type="selection" width="40" />

        <!-- Row # -->
        <el-table-column label="№" width="46" align="center">
          <template #default="{ $index }">
            <span class="row-num">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
          </template>
        </el-table-column>

        <!-- Order number + date combined -->
        <el-table-column label="Номер / Дата" width="160" sortable="custom" prop="order_number">
          <template #default="{ row }">
            <div class="num-date-cell">
              <span class="order-num">{{ row.order_number }}</span>
              <span class="date-sub">{{ formatDate(row.order_date) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Клієнт" min-width="200">
          <template #default="{ row }">
            <div class="client-cell">
              <div class="client-avatar">{{ getClientInitials(row.counterparty_id) }}</div>
              <span>{{ getCounterpartyName(row.counterparty_id) || '—' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="155">
          <template #default="{ row }">
            <span class="status-badge" :style="getStatusStyle(row.status)">
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>

        <!-- Payment -->
        <el-table-column label="Оплата" width="155">
          <template #default="{ row }">
            <div class="payment-cell">
              <span class="payment-badge" :class="getPaymentClass(row)">{{ getPaymentLabel(row) }}</span>
              <span class="payment-detail" v-if="row.paid_amount > 0">
                {{ formatCurrency(row.paid_amount) }} — {{ formatCurrency(row.total_amount) }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="total_amount" label="Сума" width="140" align="right" sortable="custom">
          <template #default="{ row }">
            <span class="amount-text">{{ formatCurrency(row.total_amount) }}</span>
          </template>
        </el-table-column>

        <!-- Delivery date -->
        <el-table-column label="Доставка" width="115" align="center">
          <template #default="{ row }">
            <span class="delivery-date">{{ row.delivery_date ? formatDate(row.delivery_date) : '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="ДЕ" width="76" align="center">
          <template #default="{ row }">
            <div @click.stop class="action-buttons">
              <el-tooltip content="Переглянути" placement="top">
                <span class="action-btn" @click.stop="() => { selectedOrder = row; drawerVisible = true }"><el-icon><View /></el-icon></span>
              </el-tooltip>
              <el-tooltip content="Редагувати" placement="top">
                <span class="action-btn" @click.stop="handleEdit(row)"><el-icon><Edit /></el-icon></span>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- PAGINATION -->
      <div class="pagination-footer">
        <span class="total-hint">Показано {{ filteredOrders.length }} з {{ orders.length }}</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="prev, pager, next"
          :total="totalCount"
          @current-change="handlePageChange"
          class="custom-pagination"
        />
      </div>
    </div>

    <!-- ===== QUICK VIEW DRAWER ===== -->
    <el-drawer
      v-model="drawerVisible"
      :title="selectedOrder?.order_number || 'Замовлення'"
      direction="rtl"
      size="480px"
      class="order-drawer"
    >
      <template v-if="selectedOrder">
        <!-- Order meta -->
        <div class="drawer-meta">
          <div class="meta-row">
            <span class="meta-key">Клієнт</span>
            <span class="meta-val">{{ getCounterpartyName(selectedOrder.counterparty_id) || '—' }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Дата</span>
            <span class="meta-val">{{ formatDate(selectedOrder.order_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Статус</span>
            <span class="status-badge" :style="getStatusStyle(selectedOrder.status)">
              {{ getStatusLabel(selectedOrder.status) }}
            </span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Сума</span>
            <span class="meta-val amount-lg">{{ formatCurrency(selectedOrder.total_amount) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Товарів</span>
            <span class="meta-val">{{ selectedOrder.lines?.length || 0 }} позицій</span>
          </div>
        </div>

        <!-- Activity Timeline -->
        <div class="timeline-section">
          <div class="timeline-title">Активність</div>
          <el-timeline>
            <el-timeline-item
              v-for="event in getTimeline(selectedOrder)"
              :key="event.label"
              :type="event.type"
              :timestamp="event.time"
              placement="top"
            >
              {{ event.label }}
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- Footer actions -->
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">Закрити</el-button>
          <el-button type="primary" @click="handleEdit(selectedOrder)">
            Відкрити замовлення
          </el-button>
        </div>
      </template>
    </el-drawer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, Download, MoreFilled,
  Document, Wallet, Check, Close, Select,
  Clock, Refresh, View, Edit
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// ===== STATE =====
const loading = ref(false)
const orders = ref([])
const counterparties = ref({})
const orderStatuses = ref([])
const searchQuery = ref('')
const dateRange = ref(null)
const activeTab = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const sortField = ref('order_date')
const sortOrder = ref('descending')
const selected = ref([])
const drawerVisible = ref(false)
const selectedOrder = ref(null)
const searchInputRef = ref(null)

// ===== COMPUTED =====
const filteredOrders = computed(() => {
  let list = [...orders.value]

  if (activeTab.value) {
    list = list.filter(o => o.status === activeTab.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o =>
      o.order_number?.toLowerCase().includes(q) ||
      getCounterpartyName(o.counterparty_id)?.toLowerCase().includes(q)
    )
  }

  // Sort
  list.sort((a, b) => {
    let va = a[sortField.value]
    let vb = b[sortField.value]
    if (sortField.value === 'order_date') {
      va = new Date(va); vb = new Date(vb)
    }
    if (sortField.value === 'total_amount') {
      va = Number(va); vb = Number(vb)
    }
    if (va < vb) return sortOrder.value === 'ascending' ? -1 : 1
    if (va > vb) return sortOrder.value === 'ascending' ? 1 : -1
    return 0
  })

  totalCount.value = list.length
  const start = (currentPage.value - 1) * pageSize.value
  return list.slice(start, start + pageSize.value)
})

const statCards = computed(() => [
  {
    label: 'Всього', value: orders.value.length,
    icon: Document, color: '#6366f1', bg: '#ede9fe'
  },
  {
    label: 'Чернетки', value: orders.value.filter(o => o.status === 'draft').length,
    icon: Document, color: '#8b5cf6', bg: '#f5f3ff'
  },
  {
    label: 'Підтверджено', value: orders.value.filter(o => o.status === 'confirmed').length,
    icon: Check, color: '#10b981', bg: '#d1fae5'
  },
  {
    label: 'Завершено', value: orders.value.filter(o => o.status === 'completed').length,
    icon: Wallet, color: '#6b7280', bg: '#f3f4f6'
  },
])

// ===== API =====
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = { limit: 500 }
    const res = await api.get('/api/v1/orders', { params })
    orders.value = res.data

    // Load counterparty names
    const cpIds = [...new Set(res.data.map(o => o.counterparty_id))].filter(id => id && !counterparties.value[id])
    for (const id of cpIds) {
      try {
        const r = await api.get(`/api/v1/counterparties/${id}`)
        counterparties.value[id] = r.data.name
      } catch {
        counterparties.value[id] = 'Н/Д'
      }
    }

    // Load statuses from dictionary
    if (orderStatuses.value.length === 0) {
      const sr = await api.get('/api/v1/dictionaries/ORDER_STATUS')
      orderStatuses.value = sr.data
    }
  } catch {
    ElMessage.error('Помилка завантаження замовлень')
  } finally {
    loading.value = false
  }
}

// ===== INTERACTIONS =====
const setTab = (code) => {
  activeTab.value = code
  currentPage.value = 1
}

const handleReset = () => {
  searchQuery.value = ''
  dateRange.value = null
  activeTab.value = ''
  currentPage.value = 1
}

let searchTimer = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { currentPage.value = 1 }, 300)
}

const handleSortChange = ({ prop, order }) => {
  sortField.value = prop || 'order_date'
  sortOrder.value = order || 'descending'
}

const handleSelectionChange = (rows) => { selected.value = rows }
const handlePageChange = (p) => { currentPage.value = p }

const handleRowClick = (row) => {
  selectedOrder.value = row
  drawerVisible.value = true
}

const handleCreate = () => router.push('/sales/orders/new')
const handleEdit = (row) => router.push(`/sales/orders/${row.id}`)

const handleCommand = (cmd, row) => {
  if (cmd === 'view') { selectedOrder.value = row; drawerVisible.value = true }
  if (cmd === 'edit') handleEdit(row)
  if (cmd === 'delete') handleDelete(row)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Видалити замовлення ${row.order_number}?`,
    'Підтвердження',
    { confirmButtonText: 'Видалити', type: 'warning' }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/orders/${row.id}`)
      ElMessage.success('Видалено')
      fetchOrders()
    } catch { ElMessage.error('Помилка видалення') }
  })
}

// ===== BULK ACTIONS =====
const bulkConfirm = async () => {
  for (const row of selected.value) {
    try { await api.put(`/api/v1/orders/${row.id}`, { status: 'confirmed' }) } catch {}
  }
  ElMessage.success(`Підтверджено ${selected.value.length} замовлень`)
  selected.value = []
  fetchOrders()
}

const bulkDelete = async () => {
  await ElMessageBox.confirm(`Видалити ${selected.value.length} замовлень?`, 'Увага', { type: 'warning' })
  for (const row of selected.value) {
    try { await api.delete(`/api/v1/orders/${row.id}`) } catch {}
  }
  ElMessage.success('Видалено')
  selected.value = []
  fetchOrders()
}

// ===== EXPORT CSV =====
const handleExportCSV = () => {
  const rows = filteredOrders.value
  const headers = ['№ Замовлення', 'Дата', 'Клієнт', 'Сума', 'Статус']
  const csv = [
    headers.join(';'),
    ...rows.map(r => [
      r.order_number,
      formatDate(r.order_date),
      getCounterpartyName(r.counterparty_id) || '',
      r.total_amount,
      getStatusLabel(r.status)
    ].join(';'))
  ].join('\n')

  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `orders_${new Date().toISOString().slice(0,10)}.csv`
  link.click()
  ElMessage.success('Файл завантажено')
}

// ===== KEYBOARD SHORTCUTS =====
const handleKeydown = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  if (e.key === 'n' || e.key === 'N') { e.preventDefault(); handleCreate() }
  if (e.key === 'Escape') { drawerVisible.value = false }
  if (e.key === '/') { e.preventDefault(); searchInputRef.value?.focus() }
}
onMounted(() => { window.addEventListener('keydown', handleKeydown); fetchOrders() })
onActivated(() => {
  if (orders.value.length > 0) {
    fetchOrders()
  }
})
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

// ===== HELPERS =====
const formatDate = (d) => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const getCounterpartyName = (id) => counterparties.value[id] || ''
const getClientInitials = (id) => {
  const name = counterparties.value[id] || '?'
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
const formatCurrency = (v) =>
  new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(v || 0)

const STATUS_HEX = {
  blue: '#6366f1', green: '#10b981', red: '#ef4444',
  orange: '#f59e0b', gray: '#6b7280', purple: '#8b5cf6',
  teal: '#14b8a6', info: '#6366f1', success: '#10b981',
  warning: '#f59e0b', danger: '#ef4444'
}
const getStatusHex = (color) => STATUS_HEX[color] || '#6366f1'

const getStatusStyle = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  const hex = getStatusHex(s?.color)
  return {
    background: hex + '18',
    color: hex,
    borderColor: hex + '40'
  }
}
const getStatusLabel = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  return s?.name || code || '—'
}

// ===== PAYMENT HELPERS =====
const getPaymentClass = (row) => {
  if (!row.total_amount || row.total_amount <= 0) return 'payment-none'
  const paid = parseFloat(row.paid_amount) || 0
  const total = parseFloat(row.total_amount) || 0
  if (paid >= total) return 'payment-full'
  if (paid > 0) return 'payment-partial'
  return 'payment-none'
}

const getPaymentLabel = (row) => {
  const paid = parseFloat(row.paid_amount) || 0
  const total = parseFloat(row.total_amount) || 0
  if (paid >= total && total > 0) return 'Оплачено'
  if (paid > 0) return 'Частково'
  return 'Не оплачено'
}

const getTimeline = (order) => {
  const events = []
  events.push({ label: 'Замовлення створено', type: 'success', time: formatDate(order.order_date) })
  if (['confirmed','shipped','completed'].includes(order.status))
    events.push({ label: 'Підтверджено менеджером', type: 'success', time: '—' })
  if (['shipped','completed'].includes(order.status))
    events.push({ label: 'Відвантажено', type: 'success', time: '—' })
  if (order.status === 'completed')
    events.push({ label: 'Завершено', type: 'success', time: '—' })
  if (order.status === 'cancelled')
    events.push({ label: 'Скасовано', type: 'danger', time: '—' })
  if (!['completed','cancelled'].includes(order.status))
    events.push({ label: 'Очікується наступний крок...', type: 'info', time: '' })
  return events
}
</script>

<style scoped>
/* ===== PAGE ===== */
.orders-page {
  padding: 0;
  background: #f4f5f9;
  min-height: 100%;
  box-sizing: border-box;
}

/* ===== FIXED TOP AREA ===== */
.fixed-top-area {
  position: sticky;
  top: -20px;  /* offset to compensate for parent .view-container padding: 20px */
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ===== HEADER ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.page-title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.3px;
}
.breadcrumb { margin-top: 2px; }
.header-actions { display: flex; gap: 10px; }

.btn-export {
  border: 1px solid #e0e0e0;
  color: #555;
  border-radius: 9px;
  font-weight: 500;
}
.btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 9px;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  transition: box-shadow 0.2s, transform 0.15s;
}
.btn-create:hover {
  box-shadow: 0 6px 20px rgba(99,102,241,0.45);
  transform: translateY(-1px);
}

/* ===== STAT CARDS ===== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.08); transform: translateY(-1px); }
.stat-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.stat-value { font-size: 18px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.stat-label { font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-dot {
  position: absolute; top: 10px; right: 10px;
  width: 6px; height: 6px; border-radius: 50%;
}

/* ===== QUICK FILTER TABS ===== */
.quick-filters {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.filter-tab {
  padding: 4px 10px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-tab:hover { border-color: #6366f1; color: #6366f1; }
.filter-tab.active {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
  box-shadow: 0 2px 8px rgba(99,102,241,0.28);
}
.tab-count {
  background: rgba(99,102,241,0.1);
  color: #6366f1;
  border-radius: 10px;
  padding: 0 7px;
  font-size: 11px;
  font-weight: 700;
}
.filter-tab.active .tab-count { background: rgba(255,255,255,0.25); color: #fff; }

/* ===== FILTER BAR ===== */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}
.search-input { flex: 1; max-width: 320px; }
.search-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  background: #fff;
  height: 28px;
}
.search-input :deep(.el-input__inner) { font-size: 12px; }
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}
.date-picker { 
  width: 240px !important;
  flex: 0 0 240px;
}
.date-picker :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  height: 28px;
  padding: 0 10px;
}
.date-picker :deep(.el-range-input) {
  font-size: 12px;
}
.date-picker :deep(.el-range-separator) {
  color: #64748b;
  font-size: 11px;
}
.date-picker :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}
.reset-btn { color: #6366f1; font-size: 13px; }

/* ===== BULK BAR ===== */
.bulk-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  padding: 10px 16px;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
}
.bulk-bar :deep(.el-button--small) { height: 28px; padding: 0 12px; font-size: 12px; }
.bulk-bar-enter-active, .bulk-bar-leave-active { transition: all 0.25s ease; }
.bulk-bar-enter-from, .bulk-bar-leave-to { opacity: 0; transform: translateY(-8px); }

/* ===== TABLE CARD ===== */
.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  margin: 0 20px 20px;
}

.orders-table :deep(th.el-table__cell) {
  background: #f8fafc !important;
  color: #64748b;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  border-bottom: 1px solid #e2e8f0 !important;
  padding: 6px 8px !important;
}
.orders-table :deep(td.el-table__cell) {
  border-bottom: 1px solid #f1f5f9 !important;
  border-right: none !important;
  padding: 4px 8px !important;
}
.orders-table :deep(.order-row) { cursor: pointer; transition: background 0.15s; }
.orders-table :deep(.order-row:hover > td) { background: #f8fafc !important; }
.orders-table :deep(.el-table__inner-wrapper::before) { display: none; }

/* Cell styles — existing */
.order-num { font-weight: 600; color: #1e293b; font-size: 12px; }
.date-text { color: #64748b; font-size: 12px; }

/* NEW: combined Номер/Дата cell */
.num-date-cell { display: flex; flex-direction: column; gap: 1px; }
.date-sub { color: #94a3b8; font-size: 11px; }

/* Row number */
.row-num { color: #94a3b8; font-size: 11px; font-weight: 600; }

.client-cell { display: flex; align-items: center; gap: 6px; }
.client-avatar {
  width: 20px; height: 20px; border-radius: 4px;
  background: linear-gradient(135deg, #64748b, #94a3b8);
  color: #fff; font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.client-cell span { font-size: 12px; font-weight: 500; color: #1e293b; }
.lines-badge {
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
}
.amount-text { font-weight: 600; color: #1e293b; font-size: 12px; }

/* Payment cell */
.payment-cell { display: flex; flex-direction: column; gap: 2px; }
.payment-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  max-width: fit-content;
}
.payment-full { background: #d1fae5; color: #059669; }
.payment-partial { background: #fef3c7; color: #d97706; }
.payment-none { background: #fee2e2; color: #dc2626; }
.payment-detail { font-size: 10px; color: #94a3b8; }

/* Delivery */
.delivery-date { font-size: 12px; color: #475569; }

/* Action buttons in-row */
.action-buttons { display: flex; gap: 2px; justify-content: center; }

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

/* Status select in filter bar */
.status-select :deep(.el-select__wrapper) {
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  background: #fff;
  height: 28px;
}

/* Refresh button */
.refresh-btn {
  color: #64748b;
  border: 1px solid #e2e8f0;
  background: #fff;
}
.refresh-btn:hover { color: #6366f1; border-color: #6366f1; }

.action-btn {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 7px;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover { background: #ede9fe; color: #6366f1; }

/* ===== PAGINATION ===== */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid #f4f5f9;
}
.total-hint { font-size: 13px; color: #9ca3af; }
.custom-pagination :deep(.el-pager li) {
  border-radius: 7px; min-width: 30px; height: 30px; line-height: 30px;
}
.custom-pagination :deep(.el-pager li.is-active) {
  background: #6366f1 !important; color: #fff !important;
}

/* ===== DRAWER ===== */
.order-drawer :deep(.el-drawer__header) {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff !important;
  padding: 18px 20px;
  margin-bottom: 0;
}
.order-drawer :deep(.el-drawer__title) { color: #fff !important; font-weight: 700; font-size: 16px; }
.order-drawer :deep(.el-drawer__close-btn) { color: rgba(255,255,255,0.8) !important; }

.drawer-meta {
  background: #f8f7ff;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ede9fe;
}
.meta-row:last-child { border-bottom: none; }
.meta-key { font-size: 13px; color: #9ca3af; font-weight: 500; }
.meta-val { font-size: 13px; color: #1e1b4b; font-weight: 600; }
.amount-lg { font-size: 16px; color: #6366f1; font-weight: 800; }

.timeline-section { margin-bottom: 20px; }
.timeline-title {
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}
.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f7;
}

/* ===== MOBILE ===== */
@media (max-width: 768px) {
  .orders-page { padding: 12px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .page-header { flex-direction: column; gap: 12px; }
  .header-actions { width: 100%; }
  .btn-create, .btn-export { flex: 1; }
  .filter-bar { flex-wrap: wrap; }
  .search-input { max-width: 100%; }
}
@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr 1fr; gap: 8px; }
  .client-avatar { display: none; }
}
</style>
