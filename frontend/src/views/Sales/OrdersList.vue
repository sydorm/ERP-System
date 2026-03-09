<template>
  <div class="orders-page">
    <div class="fixed-top-area">
      <el-breadcrumb separator="/" class="kimi-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Продажі</el-breadcrumb-item>
        <el-breadcrumb-item>Замовлення</el-breadcrumb-item>
      </el-breadcrumb>

      <!-- ===== PAGE HEADER ===== -->
      <div class="kimi-page-header">
        <div>
          <h1 class="kimi-page-title">Замовлення покупців</h1>
          <p class="kimi-page-subtitle">Керуйте вашими товарами та відстежуйте запаси</p>
        </div>
      </div>

      <!-- ===== APP TABS (Visual only to match screenshot) ===== -->
      <div class="kimi-app-tabs">
        <div class="kimi-app-tab">Головна</div>
        <div class="kimi-app-tab active">Номенклатура <span class="close-x">×</span></div>
        <div class="kimi-app-tab">Склади</div>
      </div>

      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <!-- Всього замовлень -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Всього замовлень</p>
              <p class="kimi-stat-value text-indigo-600">{{ orders.length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
              <el-icon><Document /></el-icon>
            </div>
          </div>
        </div>
        <!-- Загальна сума -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Загальна сума</p>
              <p class="kimi-stat-value text-emerald-600">{{ formatCurrency(orders.reduce((s, o) => s + (+o.total_amount || 0), 0)) }} ₴</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
              <el-icon><Wallet /></el-icon>
            </div>
          </div>
        </div>
        <!-- В роботі -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">В роботі</p>
              <p class="kimi-stat-value text-amber-600">{{ orders.filter(o => ['confirmed','draft','shipped'].includes(o.status)).length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
              <el-icon><Clock /></el-icon>
            </div>
          </div>
        </div>
        <!-- Виконано -->
        <div class="kimi-stat-card kimi-stat-blue">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Виконано</p>
              <p class="kimi-stat-value text-blue-600">{{ orders.filter(o => o.status === 'completed').length }}</p>
            </div>
            <div class="kimi-stat-icon-wrapper bg-blue-100 text-blue-600">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

    <!-- ===== SEARCH & FILTER BAR ===== -->
    <div class="kimi-filter-bar">
      <div class="kimi-filter-left">
        <el-input
          ref="searchInputRef"
          v-model="searchQuery"
          placeholder="Пошук за номером, клієнтом або телефоном..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="kimi-search-input"
        />
        <el-select
          v-model="activeTab"
          placeholder="Всі статуси"
          clearable
          style="width:160px"
          @change="(v) => setTab(v || '')"
          class="kimi-status-select"
        >
          <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code" />
        </el-select>
        <el-button class="kimi-refresh-btn" @click="fetchOrders" title="Оновити">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button link class="reset-btn" @click="handleReset" v-if="searchQuery || dateRange || activeTab">
          Скинути
        </el-button>
      </div>
      <div class="kimi-filter-right">
        <button class="kimi-primary-btn" @click="handleCreate">
          <el-icon><Plus /></el-icon> Нове замовлення
        </button>
      </div>
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
        row-class-name="kimi-row"
        header-row-class-name="kimi-header-row"
      >
        <el-table-column type="selection" width="40" align="center" />

        <!-- Row # -->
        <el-table-column label="№" width="46" align="center">
          <template #default="{ $index }">
            <span class="kimi-text-xs kimi-text-slate-400">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
          </template>
        </el-table-column>

        <!-- Order number + date combined -->
        <el-table-column label="Номер / Дата" width="160" sortable="custom" prop="order_number">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium kimi-text-indigo-600">{{ row.order_number }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ formatDate(row.order_date) }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Клієнт" min-width="200">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium">{{ getCounterpartyName(row.counterparty_id) || '—' }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ getCounterpartyPhone(row.counterparty_id) || '—' }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="155" align="center">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getStatusBadgeClass(row.status)">
              <el-icon class="kimi-badge-icon" v-if="getStatusIcon(row.status)"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>

        <!-- Payment -->
        <el-table-column label="Оплата" width="155" align="center">
          <template #default="{ row }">
            <div class="kimi-payment-col">
              <span class="kimi-badge" :class="getPaymentBadgeClass(row)">
                {{ getPaymentLabel(row) }}
              </span>
              <p class="kimi-text-xxs kimi-text-slate-400 kimi-mt-1" v-if="row.paid_amount > 0">
                {{ formatCurrency(row.paid_amount) }} / {{ formatCurrency(row.total_amount) }} ₴
              </p>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="total_amount" label="Сума" width="140" align="right" sortable="custom">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium">{{ formatCurrency(row.total_amount) }} ₴</p>
              <p class="kimi-text-xxs kimi-text-emerald-600" v-if="(row.discount_amount || 0) > 0">
                - {{ formatCurrency(row.discount_amount) }} ₴
              </p>
            </div>
          </template>
        </el-table-column>

        <!-- Delivery date -->
        <el-table-column label="Доставка" width="115" align="center">
          <template #default="{ row }">
            <span class="kimi-text-xs" v-if="row.delivery_date">{{ formatDate(row.delivery_date) }}</span>
            <span class="kimi-text-xs kimi-text-slate-400" v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="120" align="center">
          <template #default="{ row }">
            <div @click.stop class="kimi-actions-col">
              <button class="kimi-ghost-btn" @click.stop="() => { selectedOrder = row; drawerVisible = true }" title="Переглянути"><el-icon class="kimi-text-slate-400"><View /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="handleEdit(row)" title="Редагувати"><el-icon class="kimi-text-indigo-400"><Edit /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="() => handlePrint(row)" title="Друк"><el-icon class="kimi-text-slate-400"><Printer /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="handleDelete(row)" title="Видалити"><el-icon class="kimi-text-rose-400"><Delete /></el-icon></button>
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
const getCounterpartyName = (id) => counterparties.value[id]?.name || counterparties.value[id] || ''
const getCounterpartyPhone = (id) => counterparties.value[id]?.phone || ''

const getClientInitials = (id) => {
  const name = getCounterpartyName(id) || '?'
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
const formatCurrency = (v) =>
  new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(v || 0)

const getStatusBadgeClass = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  const color = s?.color || 'gray'
  const map = {
    blue: 'kimi-status-blue',
    green: 'kimi-status-emerald',
    success: 'kimi-status-emerald',
    red: 'kimi-status-rose',
    danger: 'kimi-status-rose',
    orange: 'kimi-status-amber',
    warning: 'kimi-status-amber',
    purple: 'kimi-status-indigo',
    gray: 'kimi-status-slate'
  }
  return map[color] || 'kimi-status-slate'
}

const getStatusIcon = (code) => {
  const map = {
    'draft': 'Document',
    'confirmed': 'Check',
    'in_production': 'Clock',
    'ready': 'Box',
    'shipped': 'Van',
    'delivered': 'Check',
    'cancelled': 'Close'
  }
  return map[code] || ''
}

const getStatusLabel = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  return s?.name || code || '—'
}

// ===== PAYMENT HELPERS =====
const getPaymentBadgeClass = (row) => {
  if (!row.total_amount || row.total_amount <= 0) return 'kimi-payment-rose'
  const paid = parseFloat(row.paid_amount) || 0
  const total = parseFloat(row.total_amount) || 0
  if (paid >= total) return 'kimi-payment-emerald'
  if (paid > 0) return 'kimi-payment-amber'
  return 'kimi-payment-rose'
}

const getPaymentLabel = (row) => {
  if (!row.total_amount || row.total_amount <= 0) return 'Не оплачено'
  const paid = parseFloat(row.paid_amount) || 0
  const total = parseFloat(row.total_amount) || 0
  if (paid >= total) return 'Оплачено'
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
/* ===== KIMI NEW STYLES ===== */
.kimi-breadcrumb { font-size: 13px; margin-bottom: 4px; color: #64748b; }
.kimi-page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.kimi-page-title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0; line-height: 1.2; }
.kimi-page-subtitle { font-size: 13px; color: #64748b; margin: 4px 0 0 0; }

.kimi-app-tabs { display: flex; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px; gap: 20px; }
.kimi-app-tab { 
  font-size: 14px; color: #64748b; padding-bottom: 8px; cursor: pointer; position: relative;
  display: flex; align-items: center; gap: 6px;
}
.kimi-app-tab.active { color: #4f46e5; font-weight: 600; }
.kimi-app-tab.active::after {
  content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 2px; background: #4f46e5;
}
.kimi-app-tab .close-x { font-size: 16px; font-weight: 400; color: #94a3b8; }

.kimi-stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.kimi-stat-card {
  background: #fff; border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0;
}
.kimi-stat-indigo { background: linear-gradient(to bottom right, #eef2ff, #fff); border-color: #e0e7ff; }
.kimi-stat-emerald { background: linear-gradient(to bottom right, #ecfdf5, #fff); border-color: #d1fae5; }
.kimi-stat-amber { background: linear-gradient(to bottom right, #fffbeb, #fff); border-color: #fef3c7; }
.kimi-stat-blue { background: linear-gradient(to bottom right, #eff6ff, #fff); border-color: #dbeafe; }

.kimi-stat-content { display: flex; align-items: center; justify-content: space-between; }
.kimi-stat-label { font-size: 12px; color: #64748b; margin: 0 0 4px 0; }
.kimi-stat-value { font-size: 24px; font-weight: 700; margin: 0; line-height: 1; }
.text-indigo-600 { color: #4f46e5; }
.text-emerald-600 { color: #059669; }
.text-amber-600 { color: #d97706; }
.text-blue-600 { color: #2563eb; }

.kimi-stat-icon-wrapper {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.bg-indigo-100 { background: #e0e7ff; }
.bg-emerald-100 { background: #d1fae5; }
.bg-amber-100 { background: #fef3c7; }
.bg-blue-100 { background: #dbeafe; }

.kimi-filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.kimi-filter-left { display: flex; align-items: center; gap: 8px; flex: 1; }
.kimi-search-input { max-width: 400px; }
.kimi-search-input :deep(.el-input__wrapper) { border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.kimi-status-select :deep(.el-select__wrapper) { border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.kimi-refresh-btn { border-radius: 6px !important; padding: 8px 12px !important; }

.kimi-primary-btn {
  background: #4f46e5; color: #fff; border: none; border-radius: 6px; font-size: 14px; font-weight: 500;
  padding: 8px 16px; cursor: pointer; display: flex; align-items: center; gap: 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.kimi-primary-btn:hover { background: #4338ca; }

/* Kimi Table classes */
.kimi-header-row th { background: #f8fafc !important; color: #64748b; font-size: 12px; font-weight: 500; border-bottom: 1px solid #e2e8f0 !important; }
.kimi-row td { padding: 12px 0 !important; border-bottom: 1px solid #f1f5f9 !important; }
.kimi-row:hover > td { background-color: #f8fafc !important; }

.kimi-text-xs { font-size: 12px; }
.kimi-text-xxs { font-size: 10px; }
.kimi-text-sm { font-size: 14px; }
.kimi-font-medium { font-weight: 500; }
.kimi-text-slate-400 { color: #94a3b8; }
.kimi-text-indigo-600 { color: #4f46e5; }
.kimi-text-indigo-400 { color: #818cf8; }
.kimi-text-emerald-600 { color: #059669; }
.kimi-text-rose-400 { color: #fb7185; }
.kimi-mt-1 { margin-top: 4px; }

.kimi-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 500; }
.kimi-badge-icon { margin-right: 4px; font-size: 12px; }

.kimi-status-slate { background: #f1f5f9; color: #475569; }
.kimi-status-blue { background: #dbeafe; color: #2563eb; }
.kimi-status-amber { background: #fef3c7; color: #d97706; }
.kimi-status-emerald { background: #d1fae5; color: #059669; }
.kimi-status-indigo { background: #e0e7ff; color: #4f46e5; }
.kimi-status-rose { background: #ffe4e6; color: #e11d48; }

.kimi-payment-col { display: flex; flex-direction: column; align-items: center; }
.kimi-payment-emerald { background: #d1fae5; color: #059669; }
.kimi-payment-amber { background: #fef3c7; color: #d97706; }
.kimi-payment-rose { background: #ffe4e6; color: #e11d48; }

.kimi-actions-col { display: flex; align-items: center; justify-content: center; gap: 4px; }
.kimi-ghost-btn {
  background: none; border: none; cursor: pointer; padding: 4px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
}
.kimi-ghost-btn:hover { background: #f1f5f9; }
.kimi-ghost-btn .el-icon { font-size: 16px; }

</style>
