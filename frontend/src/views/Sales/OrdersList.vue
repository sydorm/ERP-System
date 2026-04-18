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
            <p class="kimi-stat-value text-amber-600">{{ orders.filter(o => ['confirmed','draft','shipped'].includes(o.status)).length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
            <el-icon><Clock /></el-icon>
          </div>
        </div>
        <!-- Виконано -->
        <div class="kimi-stat-card kimi-stat-blue">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Виконано</p>
            <p class="kimi-stat-value text-blue-600">{{ orders.filter(o => o.status === 'completed').length }}</p>
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
          style="width:150px"
          @change="(v) => setTab(v || '')"
          class="kimi-status-select"
        >
          <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code" />
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
          @change="currentPage = 1"
        />
        <button
          class="kimi-adv-btn"
          :class="{ active: showAdvancedFilters || advancedFiltersCount > 0 }"
          @click="showAdvancedFilters = !showAdvancedFilters"
          title="Додаткові фільтри"
        >
          <el-icon><Filter /></el-icon>
          <span class="adv-btn-label">Фільтри</span>
          <span class="adv-count-badge" v-if="advancedFiltersCount">{{ advancedFiltersCount }}</span>
        </button>
        <el-popover trigger="click" placement="bottom-end" :width="290" popper-class="col-settings-popper">
          <template #reference>
            <button
              class="kimi-adv-btn"
              :class="{ active: columnConfig.some(c => c.fixed && !c.required) }"
              title="Налаштування стовпців"
            >
              <el-icon><Setting /></el-icon>
              <span class="adv-btn-label">Стовпці</span>
            </button>
          </template>
          <div class="col-settings-panel">
            <div class="col-settings-header">
              <span class="col-settings-title">Стовпці таблиці</span>
              <el-button size="small" link @click="resetColConfig">Скинути</el-button>
            </div>
            <div class="col-settings-list">
              <div v-for="col in columnConfig" :key="col.key" class="col-settings-row">
                <el-switch v-model="col.visible" :disabled="col.required" size="small" @change="saveColConfig" />
                <span class="col-settings-label" :class="{ 'col-required': col.required }">{{ col.label }}</span>
                <button
                  v-if="col.visible && !col.required"
                  class="col-pin-btn"
                  :class="{ active: col.fixed }"
                  @click="col.fixed = !col.fixed; saveColConfig()"
                  title="Закріпити зліва"
                >
                  <el-icon><Lock /></el-icon>
                  {{ col.fixed ? 'Закріплено' : 'Закріпити' }}
                </button>
              </div>
            </div>
            <div class="col-settings-hint">
              <el-icon><Lock /></el-icon> — зафіксувати стовпець зліва при прокручуванні
            </div>
          </div>
        </el-popover>
        <el-button class="kimi-refresh-btn" @click="fetchOrders" title="Оновити">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button link class="reset-btn" @click="handleReset" v-if="hasActiveFilters">
          Скинути
        </el-button>
      </div>
      <div class="kimi-filter-right">
        <button class="kimi-primary-btn" @click="handleCreate">
          <el-icon><Plus /></el-icon> Нове замовлення
        </button>
      </div>
    </div>

    <!-- ===== ADVANCED FILTERS PANEL ===== -->
    <transition name="adv-panel">
      <div class="adv-filters-panel" v-if="showAdvancedFilters">
        <div class="adv-group">
          <span class="adv-label">Оплата</span>
          <div class="payment-pills">
            <button :class="['pay-pill', paymentFilter === '' && 'active']" @click="paymentFilter = ''; currentPage = 1">Всі</button>
            <button :class="['pay-pill', 'pay-paid', paymentFilter === 'paid' && 'active']" @click="paymentFilter = 'paid'; currentPage = 1">Оплачено</button>
            <button :class="['pay-pill', 'pay-partial', paymentFilter === 'partial' && 'active']" @click="paymentFilter = 'partial'; currentPage = 1">Частково</button>
            <button :class="['pay-pill', 'pay-unpaid', paymentFilter === 'unpaid' && 'active']" @click="paymentFilter = 'unpaid'; currentPage = 1">Не оплачено</button>
          </div>
        </div>
        <div class="adv-divider" />
        <div class="adv-group">
          <span class="adv-label">Сума (₴)</span>
          <el-input-number
            v-model="amountMin"
            :min="0"
            placeholder="Від"
            controls-position="right"
            size="small"
            class="adv-amount-input"
            @change="currentPage = 1"
          />
          <span class="adv-range-sep">—</span>
          <el-input-number
            v-model="amountMax"
            :min="0"
            placeholder="До"
            controls-position="right"
            size="small"
            class="adv-amount-input"
            @change="currentPage = 1"
          />
        </div>
      </div>
    </transition>

    <!-- ===== ACTIVE FILTER CHIPS ===== -->
    <transition name="chips-fade">
      <div class="active-chips-row" v-if="activeFilterChips.length">
        <span class="chips-row-label">Фільтри:</span>
        <div class="chip" v-for="chip in activeFilterChips" :key="chip.key">
          {{ chip.label }}
          <button class="chip-remove" @click="chip.remove()">×</button>
        </div>
        <button class="chips-clear-all" @click="handleReset">Скинути всі</button>
      </div>
    </transition>

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
        <el-table-column label="Номер / Дата" width="160" sortable="custom" prop="order_number" :fixed="colFixed('order_number')">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium kimi-text-indigo-600">{{ row.order_number }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ formatDate(row.order_date) }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Клієнт" min-width="200" v-if="colVisible('client')" :fixed="colFixed('client')">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium">{{ getCounterpartyName(row.counterparty_id) || '—' }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ getCounterpartyPhone(row.counterparty_id) || '—' }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="155" align="center" v-if="colVisible('status')" :fixed="colFixed('status')">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getStatusBadgeClass(row.status)">
              <el-icon class="kimi-badge-icon" v-if="getStatusIcon(row.status)"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>

        <!-- Payment -->
        <el-table-column label="Оплата" width="155" align="center" v-if="colVisible('payment')" :fixed="colFixed('payment')">
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

        <el-table-column prop="total_amount" label="Сума" width="140" align="right" sortable="custom" v-if="colVisible('total_amount')" :fixed="colFixed('total_amount')">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium">{{ formatCurrency(row.total_amount) }} ₴</p>
              <p class="kimi-text-xxs kimi-text-emerald-600" v-if="(row.discount_amount || 0) > 0">
                - {{ formatCurrency(row.discount_amount) }} ₴
              </p>
            </div>
          </template>
        </el-table-column>

        <!-- Shipping date (відвантаження) -->
        <el-table-column label="Відвантаження" width="130" align="center" v-if="colVisible('shipping_date')" :fixed="colFixed('shipping_date')">
          <template #default="{ row }">
            <div v-if="row.shipping_date" class="date-cell" :class="getDateClass(row.shipping_date)">
              <span class="date-cell-text">{{ formatDate(row.shipping_date) }}</span>
              <span class="date-cell-hint date-hint-overdue" v-if="getDateClass(row.shipping_date) === 'date-overdue'">протерм.</span>
              <span class="date-cell-hint date-hint-today"   v-else-if="getDateClass(row.shipping_date) === 'date-today'">сьогодні</span>
              <span class="date-cell-hint date-hint-soon"    v-else-if="getDateClass(row.shipping_date) === 'date-soon'">скоро</span>
            </div>
            <span class="kimi-text-xs kimi-text-slate-400" v-else>—</span>
          </template>
        </el-table-column>

        <!-- Delivery date -->
        <el-table-column label="Доставка" width="115" align="center" v-if="colVisible('delivery_date')" :fixed="colFixed('delivery_date')">
          <template #default="{ row }">
            <div v-if="row.delivery_date" class="date-cell" :class="getDateClass(row.delivery_date)">
              <span class="date-cell-text">{{ formatDate(row.delivery_date) }}</span>
              <span class="date-cell-hint date-hint-overdue" v-if="getDateClass(row.delivery_date) === 'date-overdue'">протерм.</span>
              <span class="date-cell-hint date-hint-today"   v-else-if="getDateClass(row.delivery_date) === 'date-today'">сьогодні</span>
              <span class="date-cell-hint date-hint-soon"    v-else-if="getDateClass(row.delivery_date) === 'date-soon'">скоро</span>
            </div>
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
  Clock, Refresh, View, Edit, Delete, Printer, Filter, Setting, Lock
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
const showAdvancedFilters = ref(false)
const paymentFilter = ref('')
const amountMin = ref(null)
const amountMax = ref(null)

// ===== COLUMN CONFIG =====
const COL_DEFAULTS = [
  { key: 'order_number', label: 'Номер / Дата',    visible: true,  fixed: true,  required: true },
  { key: 'client',       label: 'Клієнт',           visible: true,  fixed: false },
  { key: 'status',       label: 'Статус',           visible: true,  fixed: false },
  { key: 'payment',      label: 'Оплата',           visible: true,  fixed: false },
  { key: 'total_amount', label: 'Сума',             visible: true,  fixed: false },
  { key: 'shipping_date',label: 'Відвантаження',    visible: false, fixed: false },
  { key: 'delivery_date',label: 'Доставка',         visible: true,  fixed: false },
]
const COLS_STORAGE_KEY = 'erp_orders_cols_v1'
const columnConfig = ref((() => {
  try {
    const saved = JSON.parse(localStorage.getItem(COLS_STORAGE_KEY))
    if (Array.isArray(saved) && saved.length === COL_DEFAULTS.length) return saved
  } catch {}
  return COL_DEFAULTS.map(c => ({ ...c }))
})())
const colVisible = (key) => columnConfig.value.find(c => c.key === key)?.visible ?? true
const colFixed  = (key) => (columnConfig.value.find(c => c.key === key)?.fixed ? 'left' : undefined)
const saveColConfig  = () => localStorage.setItem(COLS_STORAGE_KEY, JSON.stringify(columnConfig.value))
const resetColConfig = () => { columnConfig.value = COL_DEFAULTS.map(c => ({ ...c })); saveColConfig() }

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
      getCounterpartyName(o.counterparty_id)?.toLowerCase().includes(q) ||
      getCounterpartyPhone(o.counterparty_id)?.toLowerCase().includes(q)
    )
  }

  if (dateRange.value) {
    const [from, to] = dateRange.value
    const fromMs = new Date(from).setHours(0, 0, 0, 0)
    const toMs = new Date(to).setHours(23, 59, 59, 999)
    list = list.filter(o => {
      const d = new Date(o.order_date).getTime()
      return d >= fromMs && d <= toMs
    })
  }

  if (paymentFilter.value) {
    list = list.filter(o => {
      const paid = parseFloat(o.paid_amount) || 0
      const total = parseFloat(o.total_amount) || 0
      if (paymentFilter.value === 'paid') return paid >= total && total > 0
      if (paymentFilter.value === 'partial') return paid > 0 && paid < total
      if (paymentFilter.value === 'unpaid') return paid === 0
      return true
    })
  }

  if (amountMin.value != null) {
    list = list.filter(o => parseFloat(o.total_amount) >= amountMin.value)
  }
  if (amountMax.value != null) {
    list = list.filter(o => parseFloat(o.total_amount) <= amountMax.value)
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

const hasActiveFilters = computed(() =>
  !!(searchQuery.value || activeTab.value || dateRange.value || paymentFilter.value || amountMin.value != null || amountMax.value != null)
)

const advancedFiltersCount = computed(() => {
  let n = 0
  if (dateRange.value) n++
  if (paymentFilter.value) n++
  if (amountMin.value != null || amountMax.value != null) n++
  return n
})

const activeFilterChips = computed(() => {
  const chips = []
  if (searchQuery.value) chips.push({
    key: 'search',
    label: `Пошук: ${searchQuery.value}`,
    remove: () => { searchQuery.value = ''; currentPage.value = 1 }
  })
  if (activeTab.value) chips.push({
    key: 'status',
    label: `Статус: ${getStatusLabel(activeTab.value)}`,
    remove: () => { activeTab.value = ''; currentPage.value = 1 }
  })
  if (dateRange.value) {
    const [from, to] = dateRange.value
    chips.push({
      key: 'date',
      label: `Дата: ${formatDate(from)} — ${formatDate(to)}`,
      remove: () => { dateRange.value = null; currentPage.value = 1 }
    })
  }
  if (paymentFilter.value) {
    const labels = { paid: 'Оплачено', partial: 'Частково', unpaid: 'Не оплачено' }
    chips.push({
      key: 'payment',
      label: `Оплата: ${labels[paymentFilter.value]}`,
      remove: () => { paymentFilter.value = '' }
    })
  }
  if (amountMin.value != null || amountMax.value != null) {
    let label = 'Сума:'
    if (amountMin.value != null) label += ` від ${formatCurrency(amountMin.value)}`
    if (amountMax.value != null) label += ` до ${formatCurrency(amountMax.value)}`
    chips.push({
      key: 'amount',
      label,
      remove: () => { amountMin.value = null; amountMax.value = null }
    })
  }
  return chips
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
  paymentFilter.value = ''
  amountMin.value = null
  amountMax.value = null
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

const getDateClass = (dateStr) => {
  if (!dateStr) return ''
  const diff = Math.floor((new Date(dateStr) - new Date().setHours(0,0,0,0)) / 86400000)
  if (diff < 0) return 'date-overdue'
  if (diff === 0) return 'date-today'
  if (diff <= 3) return 'date-soon'
  return ''
}

const getStatusStyle = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  const color = s?.color || 'gray'
  const map = {
    blue: { background: '#dbeafe', color: '#2563eb', border: '1px solid #93c5fd' },
    green: { background: '#d1fae5', color: '#059669', border: '1px solid #6ee7b7' },
    success: { background: '#d1fae5', color: '#059669', border: '1px solid #6ee7b7' },
    orange: { background: '#fef3c7', color: '#d97706', border: '1px solid #fcd34d' },
    warning: { background: '#fef3c7', color: '#d97706', border: '1px solid #fcd34d' },
    red: { background: '#ffe4e6', color: '#e11d48', border: '1px solid #fda4af' },
    danger: { background: '#ffe4e6', color: '#e11d48', border: '1px solid #fda4af' },
    gray: { background: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1' }
  }
  return map[color] || map.gray
}

const handlePrint = (row) => {
  window.open(`/sales/orders/${row.id}?print=1`, '_blank')
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
  min-width: 0;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.08); transform: translateY(-1px); }
.stat-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.stat-value { font-size: 18px; font-weight: 800; color: #1e1b4b; line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-label { font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
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

/* ===== STAT CARDS (using global classes from tailwind.css) ===== */
.kimi-stat-indigo { background: linear-gradient(to bottom right, #eef2ff, #fff); }
.kimi-stat-emerald { background: linear-gradient(to bottom right, #ecfdf5, #fff); }
.kimi-stat-amber { background: linear-gradient(to bottom right, #fffbeb, #fff); }
.kimi-stat-blue { background: linear-gradient(to bottom right, #eff6ff, #fff); }
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

.kimi-filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 8px; }
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

/* ===== DATE CELL HIGHLIGHTING ===== */
.date-cell {
  display: inline-flex; flex-direction: column; align-items: center;
  gap: 1px; border-radius: 5px; padding: 2px 7px;
}
.date-cell-text { font-size: 12px; font-weight: 500; color: #475569; }
.date-cell-hint { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; }

.date-overdue { background: #fff1f2; }
.date-overdue .date-cell-text { color: #dc2626; }
.date-hint-overdue { color: #dc2626; }

.date-today { background: #fff7ed; }
.date-today .date-cell-text { color: #ea580c; font-weight: 700; }
.date-hint-today { color: #ea580c; }

.date-soon { background: #fefce8; }
.date-soon .date-cell-text { color: #ca8a04; }
.date-hint-soon { color: #ca8a04; }

/* ===== COLUMN SETTINGS PANEL ===== */
.col-settings-panel { user-select: none; }
.col-settings-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;
}
.col-settings-title { font-size: 13px; font-weight: 600; color: #374151; }
.col-settings-list { display: flex; flex-direction: column; gap: 2px; margin-bottom: 8px; }
.col-settings-row {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 8px; border-radius: 6px; transition: background 0.12s;
}
.col-settings-row:hover { background: #f8fafc; }
.col-settings-label { flex: 1; font-size: 13px; color: #374151; }
.col-settings-label.col-required { color: #94a3b8; font-style: italic; }
.col-pin-btn {
  display: inline-flex; align-items: center; gap: 4px;
  border: 1px solid #e2e8f0; border-radius: 5px; background: #fff;
  padding: 2px 8px; cursor: pointer; font-size: 11px; color: #94a3b8;
  transition: all 0.15s; white-space: nowrap;
}
.col-pin-btn:hover { border-color: #6366f1; color: #6366f1; }
.col-pin-btn.active { border-color: #6366f1; background: #eef2ff; color: #4f46e5; font-weight: 600; }
.col-settings-hint {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: #94a3b8; padding-top: 8px;
  border-top: 1px solid #f1f5f9;
}

/* ===== DATE PICKER ===== */
.kimi-date-picker { width: 220px !important; flex-shrink: 0; }
.kimi-date-picker :deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.kimi-date-picker :deep(.el-range-input) { font-size: 12px; }
.kimi-date-picker :deep(.el-input__wrapper.is-focus) {
  border-color: #4f46e5 !important;
  box-shadow: 0 0 0 2px rgba(79,70,229,0.1) !important;
}

/* ===== ADVANCED FILTER BUTTON ===== */
.kimi-adv-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 0 12px; height: 32px;
  border: 1px solid #e2e8f0; border-radius: 6px;
  background: #fff; color: #64748b; font-size: 13px; cursor: pointer;
  transition: all 0.15s; white-space: nowrap; flex-shrink: 0;
}
.kimi-adv-btn:hover { border-color: #4f46e5; color: #4f46e5; }
.kimi-adv-btn.active { border-color: #4f46e5; color: #4f46e5; background: #eef2ff; }
.adv-btn-label { font-size: 13px; }
.adv-count-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; padding: 0 5px;
  background: #4f46e5; color: #fff;
  border-radius: 10px; font-size: 11px; font-weight: 700;
}

/* ===== ADVANCED FILTERS PANEL ===== */
.adv-filters-panel {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 10px 16px; margin-bottom: 8px;
}
.adv-panel-enter-active, .adv-panel-leave-active {
  transition: all 0.2s ease; overflow: hidden;
}
.adv-panel-enter-from, .adv-panel-leave-to { opacity: 0; transform: translateY(-6px); }

.adv-group { display: flex; align-items: center; gap: 8px; }
.adv-label { font-size: 12px; font-weight: 600; color: #64748b; white-space: nowrap; }
.adv-divider { width: 1px; height: 24px; background: #e2e8f0; flex-shrink: 0; }
.adv-range-sep { color: #94a3b8; font-size: 13px; }
.adv-amount-input { width: 110px !important; }
.adv-amount-input :deep(.el-input__wrapper) { border-radius: 6px; }

/* ===== PAYMENT PILLS ===== */
.payment-pills { display: flex; gap: 4px; }
.pay-pill {
  padding: 3px 10px; border-radius: 14px; font-size: 12px; font-weight: 500;
  border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer;
  transition: all 0.15s;
}
.pay-pill:hover { border-color: #94a3b8; }
.pay-pill.active { border-color: #4f46e5; background: #4f46e5; color: #fff; }
.pay-pill.pay-paid.active { background: #059669; border-color: #059669; }
.pay-pill.pay-partial.active { background: #d97706; border-color: #d97706; }
.pay-pill.pay-unpaid.active { background: #e11d48; border-color: #e11d48; }

/* ===== ACTIVE FILTER CHIPS ===== */
.active-chips-row {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  margin-bottom: 8px;
}
.chips-fade-enter-active, .chips-fade-leave-active { transition: all 0.2s ease; }
.chips-fade-enter-from, .chips-fade-leave-to { opacity: 0; transform: translateY(-4px); }
.chips-row-label { font-size: 12px; color: #94a3b8; white-space: nowrap; }
.chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px 3px 10px; border-radius: 14px;
  background: #eef2ff; color: #4f46e5;
  font-size: 12px; font-weight: 500; border: 1px solid #c7d2fe;
}
.chip-remove {
  background: none; border: none; cursor: pointer; color: #818cf8;
  font-size: 15px; line-height: 1; display: flex; align-items: center; padding: 0;
}
.chip-remove:hover { color: #4f46e5; }
.chips-clear-all {
  padding: 3px 10px; border-radius: 14px; font-size: 12px;
  border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer;
}
.chips-clear-all:hover { border-color: #e11d48; color: #e11d48; }

</style>
