<template>
  <div class="orders-page">
    <div class="fixed-top-area">

      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <!-- Всього замовлень -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Всього замовлень</p>
            <p class="kimi-stat-value text-indigo-600">{{ orders.length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
            <el-icon><Document /></el-icon>
          </div>
        </div>
        <!-- Загальна сума -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Загальна сума</p>
            <p class="kimi-stat-value text-emerald-600">{{ formatCurrency(orders.reduce((s, o) => s + (+o.total_amount || 0), 0)) }} ₴</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
            <el-icon><Wallet /></el-icon>
          </div>
        </div>
        <!-- В роботі -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">В роботі</p>
            <p class="kimi-stat-value text-amber-600">{{ orders.filter(o => ['confirmed','draft'].includes(o.status)).length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
            <el-icon><Clock /></el-icon>
          </div>
        </div>
        <!-- Виконано -->
        <div class="kimi-stat-card kimi-stat-blue">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Виконано</p>
            <p class="kimi-stat-value text-blue-600">{{ orders.filter(o => o.status === 'done').length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-blue-100 text-blue-600">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>

    <!-- ===== SEARCH & FILTER BAR ===== -->
    <div class="kimi-filter-bar">
      <div class="kimi-filter-left">
        <el-input
          ref="searchInputRef"
          v-model="searchQuery"
          placeholder="Пошук за номером, постачальником..."
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

        <el-table-column label="Постачальник" min-width="200">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium">{{ getCounterpartyName(row.supplier_id) || '—' }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ getCounterpartyPhone(row.supplier_id) || '—' }}</p>
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

        <!-- Expected date -->
        <el-table-column label="Очікується" width="115" align="center">
          <template #default="{ row }">
            <span class="kimi-text-xs" v-if="row.expected_date">{{ formatDate(row.expected_date) }}</span>
            <span class="kimi-text-xs kimi-text-slate-400" v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="120" align="center">
          <template #default="{ row }">
            <div @click.stop class="kimi-actions-col">
              <button class="kimi-ghost-btn" @click.stop="() => { selectedOrder = row; drawerVisible = true }" title="Переглянути"><el-icon class="kimi-text-slate-400"><View /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="handleEdit(row)" title="Редагувати"><el-icon class="kimi-text-indigo-400"><Edit /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="handleDelete(row)" title="Видалити"><el-icon class="kimi-text-rose-400"><Delete /></el-icon></button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- PAGINATION -->
      <div class="pagination-footer">
        <span class="total-hint">Показано {{ filteredOrders.length }} з {{ orders.length }}</span>
        <div class="custom-pagination-container">
          <el-select v-model="pageSize" size="small" class="limit-select" @change="handleSizeChange">
            <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
          </el-select>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalCount"
            background
            layout="prev, pager, next"
            class="custom-pagination-numeric"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- ===== QUICK VIEW DRAWER ===== -->
    <el-drawer
      v-model="drawerVisible"
      :title="selectedOrder?.order_number || 'Замовлення постачальнику'"
      direction="rtl"
      size="480px"
      class="order-drawer"
    >
      <template v-if="selectedOrder">
        <!-- Order meta -->
        <div class="drawer-meta">
          <div class="meta-row">
            <span class="meta-key">Постачальник</span>
            <span class="meta-val">{{ getCounterpartyName(selectedOrder.supplier_id) || '—' }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Дата</span>
            <span class="meta-val">{{ formatDate(selectedOrder.order_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Очікується</span>
            <span class="meta-val">{{ formatDate(selectedOrder.expected_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">Статус</span>
            <span class="status-badge" :class="getStatusBadgeClass(selectedOrder.status)">
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
  Clock, Refresh, View, Edit, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// ===== STATE =====
const loading = ref(false)
const orders = ref([])
const counterparties = ref({})
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

const orderStatuses = ref([
  { code: 'draft', name: 'Чернетка', color: 'gray' },
  { code: 'confirmed', name: 'Підтверджено', color: 'blue' },
  { code: 'done', name: 'Виконано', color: 'green' },
  { code: 'cancelled', name: 'Скасовано', color: 'red' }
])

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
      getCounterpartyName(o.supplier_id)?.toLowerCase().includes(q)
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

// ===== API =====
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = { limit: 500 }
    const res = await api.get('/api/v1/purchase-orders', { params })
    orders.value = res.data

    // Load supplier names & phone
    const cpIds = [...new Set(res.data.map(o => o.supplier_id))].filter(id => id && !counterparties.value[id])
    for (const id of cpIds) {
      try {
        const r = await api.get(`/api/v1/counterparties/${id}`)
        counterparties.value[id] = { name: r.data.name, phone: r.data.phone }
      } catch {
        counterparties.value[id] = { name: 'Н/Д', phone: '' }
      }
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
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleRowClick = (row) => {
  selectedOrder.value = row
  drawerVisible.value = true
}

const handleCreate = () => router.push('/purchases/orders/new')
const handleEdit = (row) => router.push(`/purchases/orders/${row.id}`)

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Видалити замовлення ${row.order_number}?`,
    'Підтвердження',
    { confirmButtonText: 'Видалити', type: 'warning' }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/purchase-orders/${row.id}`)
      ElMessage.success('Видалено')
      fetchOrders()
    } catch { ElMessage.error('Помилка видалення') }
  })
}

// ===== BULK ACTIONS =====
const bulkConfirm = async () => {
  for (const row of selected.value) {
    try { await api.put(`/api/v1/purchase-orders/${row.id}`, { status: 'confirmed' }) } catch {}
  }
  ElMessage.success(`Підтверджено ${selected.value.length} замовлень`)
  selected.value = []
  fetchOrders()
}

const bulkDelete = async () => {
  await ElMessageBox.confirm(`Видалити ${selected.value.length} замовлень?`, 'Увага', { type: 'warning' })
  for (const row of selected.value) {
    try { await api.delete(`/api/v1/purchase-orders/${row.id}`) } catch {}
  }
  ElMessage.success('Видалено')
  selected.value = []
  fetchOrders()
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
    'done': 'Check',
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
  if (['confirmed','done'].includes(order.status))
    events.push({ label: 'Підтверджено менеджером', type: 'success', time: '—' })
  if (order.status === 'done')
    events.push({ label: 'Виконано / Отримано', type: 'success', time: '—' })
  if (order.status === 'cancelled')
    events.push({ label: 'Скасовано', type: 'danger', time: '—' })
  if (!['done','cancelled'].includes(order.status))
    events.push({ label: 'Очікується наступний крок...', type: 'info', time: '' })
  return events
}
</script>

<style scoped>
/* ===== PAGE ===== */
.orders-page {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #f4f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}

/* ===== FIXED TOP AREA ===== */
.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 0px;
  display: flex;
  flex-direction: column;
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

/* ===== STAT CARDS (using global classes from tailwind.css) ===== */
.kimi-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.kimi-stat-card {
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
.kimi-stat-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.08); transform: translateY(-1px); }

.kimi-stat-indigo { background: linear-gradient(to bottom right, #eef2ff, #fff); }
.kimi-stat-emerald { background: linear-gradient(to bottom right, #ecfdf5, #fff); }
.kimi-stat-amber { background: linear-gradient(to bottom right, #fffbeb, #fff); }
.kimi-stat-blue { background: linear-gradient(to bottom right, #eff6ff, #fff); }

.kimi-stat-info { flex: 1; }
.kimi-stat-value { font-size: 18px; font-weight: 800; color: #1e1b4b; line-height: 1; margin: 0; }
.kimi-stat-label { font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin: 0; }

.kimi-stat-icon-wrapper {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.text-indigo-600 { color: #4f46e5; }
.text-emerald-600 { color: #059669; }
.text-amber-600 { color: #d97706; }
.text-blue-600 { color: #2563eb; }
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
  margin: 0 0 20px;
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
.orders-table :deep(.kimi-row) { cursor: pointer; transition: background 0.15s; }
.orders-table :deep(.kimi-row:hover > td) { background: #f8fafc !important; }

/* ===== PAGINATION ===== */
.pagination-footer {
  display: flex; justify-content: space-between; align-items: center; padding: 12px 20px;
  border-top: 1px solid #e2e8f0; background: #f8fafc; flex-shrink: 0;
}
.total-hint { font-size: 13px; color: #64748b; }
.custom-pagination-container {
  display: flex;
  align-items: center;
  gap: 12px;
}
.limit-select {
  width: 64px !important;
}
.limit-select :deep(.el-input__wrapper) {
  border-radius: 6px;
  background: #ffffff !important;
}
.custom-pagination-numeric :deep(.el-pager li) { border-radius: 6px; min-width: 30px; height: 30px; line-height: 30px; font-weight: 500; }
.custom-pagination-numeric :deep(.el-pager li.is-active) { background: #4f46e5 !important; color: #fff !important; }

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

/* Kimi Table classes */
.kimi-header-row th { background: #f8fafc !important; color: #64748b; font-size: 12px; font-weight: 500; border-bottom: 1px solid #e2e8f0 !important; }
.kimi-row td { padding: 12px 0 !important; border-bottom: 1px solid #f1f5f9 !important; }

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

.kimi-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 500; border: 1px solid transparent; }
.kimi-badge-icon { margin-right: 4px; font-size: 12px; }

.kimi-status-slate { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }
.kimi-status-blue { background: #dbeafe; color: #2563eb; border-color: #bfdbfe; }
.kimi-status-amber { background: #fef3c7; color: #d97706; border-color: #fde68a; }
.kimi-status-emerald { background: #d1fae5; color: #059669; border-color: #a7f3d0; }
.kimi-status-indigo { background: #e0e7ff; color: #4f46e5; border-color: #c7d2fe; }
.kimi-status-rose { background: #ffe4e6; color: #e11d48; border-color: #fecdd3; }

.kimi-actions-col { display: flex; align-items: center; justify-content: center; gap: 4px; }
.kimi-ghost-btn {
  background: none; border: none; cursor: pointer; padding: 4px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
}
.kimi-ghost-btn:hover { background: #f1f5f9; }
.kimi-ghost-btn .el-icon { font-size: 16px; }

/* Payment badge */
.kimi-payment-col { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.kimi-payment-emerald { background: #d1fae5; color: #059669; border-color: #a7f3d0; }
.kimi-payment-amber   { background: #fef3c7; color: #d97706; border-color: #fde68a; }
.kimi-payment-rose    { background: #ffe4e6; color: #e11d48; border-color: #fecdd3; }

</style>
