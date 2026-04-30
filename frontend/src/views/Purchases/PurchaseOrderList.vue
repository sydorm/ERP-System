<template>
  <div class="purchase-orders-page">

    <!-- ===== PAGE HEADER (only "+ Нове замовлення") ===== -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Замовлення постачальникам</h1>
        <p class="page-subtitle">Контроль закупівель матеріалів, оплат і очікуваних поставок</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="btn-primary" @click="handleCreate">
          <el-icon><Plus /></el-icon> Нове замовлення
        </el-button>
      </div>
    </div>

    <!-- ===== KPI Analytics Cards ===== -->
    <div class="kpi-grid">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="kpi-card">
        <div class="kpi-icon-badge" :style="{ backgroundColor: kpi.bg, color: kpi.color }">
          <el-icon><component :is="kpi.icon" /></el-icon>
        </div>
        <div class="kpi-content">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value-row">
            <span class="kpi-value">{{ kpi.value }}</span>
            <div class="kpi-sparkline" v-if="kpi.path">
              <svg width="60" height="24" viewBox="0 0 64 32">
                <path :d="kpi.path" :stroke="kpi.color" stroke-width="2" fill="none" stroke-linecap="round" />
              </svg>
            </div>
          </div>
          <div class="kpi-subtext" :class="kpi.trendClass">
            <span v-if="kpi.trend">{{ kpi.trend }} vs минулий місяць</span>
            <span v-else>{{ kpi.sub }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== FILTER TOOLBAR ===== -->
    <div class="filter-toolbar">
      <div class="filter-main-row">

        <!-- Search -->
        <div class="search-field">
          <el-icon><Search /></el-icon>
          <input
            ref="searchInputRef"
            type="text"
            v-model="filters.search"
            placeholder="Пошук за номером, постачальником..."
          />
        </div>

        <!-- Export -->
        <el-button class="toolbar-btn" @click="handleExport">
          <el-icon><Download /></el-icon>
          <span class="btn-label">Експорт</span>
        </el-button>

        <!-- Create from needs -->
        <el-button class="toolbar-btn" @click="openNeedsDrawer">
          <el-icon><Box /></el-icon>
          <span class="btn-label">З потреб</span>
        </el-button>

        <div class="filter-divider"></div>

        <!-- Filters popover -->
        <el-popover
          v-model:visible="filtersPopoverVisible"
          placement="bottom-start"
          :width="360"
          trigger="click"
          popper-class="filters-popover"
        >
          <template #reference>
            <el-badge :value="activeFiltersCount" :hidden="activeFiltersCount === 0" class="filter-badge">
              <el-button class="toolbar-btn filters-btn" :class="{ 'filters-active': activeFiltersCount > 0 }">
                <el-icon><Filter /></el-icon>
                <span class="btn-label">Фільтри</span>
              </el-button>
            </el-badge>
          </template>

          <!-- Popover content -->
          <div class="filters-panel">
            <div class="filters-panel-title">Фільтри</div>

            <div class="fp-row">
              <label>Статус</label>
              <el-select v-model="filters.status" placeholder="Будь-який" clearable style="width:100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </div>

            <div class="fp-row">
              <label>Постачальник</label>
              <el-select v-model="filters.supplierId" placeholder="Будь-який" clearable filterable style="width:100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </div>

            <div class="fp-row">
              <label>Оплата</label>
              <el-select v-model="filters.payment" placeholder="Будь-яка" clearable style="width:100%">
                <el-option v-for="p in paymentOptions" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </div>

            <div class="fp-row">
              <label>Пріоритет</label>
              <el-select v-model="filters.priority" placeholder="Будь-який" clearable style="width:100%">
                <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </div>

            <div class="fp-row">
              <label>Дата доставки</label>
              <el-date-picker
                v-model="filters.expectedDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="Оберіть дату"
                style="width:100%"
              />
            </div>

            <div class="fp-toggles">
              <div class="fp-toggle" :class="{ active: filters.onlyOverdue }" @click="filters.onlyOverdue = !filters.onlyOverdue">
                <span>Тільки прострочені</span>
                <div class="fp-toggle-dot" />
              </div>
              <div class="fp-toggle" :class="{ active: filters.onlyNotReceived }" @click="filters.onlyNotReceived = !filters.onlyNotReceived">
                <span>Тільки неотримані</span>
                <div class="fp-toggle-dot" />
              </div>
            </div>

            <div class="fp-footer">
              <el-button size="small" @click="resetFilters">Скинути</el-button>
              <el-button size="small" type="primary" @click="filtersPopoverVisible = false">Застосувати</el-button>
            </div>
          </div>
        </el-popover>

        <!-- Refresh -->
        <el-button class="toolbar-btn icon-only" @click="fetchOrders" title="Оновити">
          <el-icon><Refresh /></el-icon>
        </el-button>

        <!-- Settings -->
        <el-button class="toolbar-btn icon-only" title="Налаштування колонок">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>

      <!-- Active filter chips -->
      <div class="active-chips" v-if="activeFilterChips.length">
        <div
          v-for="chip in activeFilterChips"
          :key="chip.key"
          class="active-chip"
          @click="clearFilterChip(chip.key)"
        >
          {{ chip.label }}
          <el-icon class="chip-close"><Close /></el-icon>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <transition name="el-fade-in-linear">
      <div class="bulk-actions-bar" v-if="selected.length">
        <div class="bulk-info">Вибрано: <strong>{{ selected.length }}</strong></div>
        <div class="bulk-btns">
          <el-button type="primary" size="small" @click="bulkConfirm">Підтвердити</el-button>
          <el-button type="danger" size="small" @click="bulkDelete">Видалити</el-button>
          <el-button size="small" @click="selected = []">Скасувати</el-button>
        </div>
      </div>
    </transition>

    <!-- Data Table -->
    <div class="table-surface">
      <el-table
        v-loading="loading"
        :data="pagedOrders"
        class="nexora-table"
        height="100%"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="50" align="center" />
        
        <el-table-column label="№ / Дата" width="160" sortable="custom" prop="order_date">
          <template #default="{ row }">
            <div class="cell-id clickable" @click="handleEdit(row)">{{ row.order_number }}</div>
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
                <div class="supplier-code">Код: {{ row.supplier_id?.slice(0,8) }}</div>
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

        <el-table-column label="Статус" width="160" align="center">
          <template #default="{ row }">
            <div class="badge-pill" :style="getStatusBadgeStyle(normalizeStatus(row))">
              <span class="badge-dot" :style="{ backgroundColor: getStatusColor(normalizeStatus(row)) }"></span>
              {{ getStatusLabel(normalizeStatus(row)) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="160" align="center">
          <template #default="{ row }">
            <div class="badge-pill" :style="getPaymentBadgeStyle(row)">
              <span class="badge-dot" :style="{ backgroundColor: getPaymentColor(row) }"></span>
              {{ getPaymentLabel(row) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Очікується" width="160" sortable="custom" prop="expected_date">
          <template #default="{ row }">
            <div class="expected-cell">
              <div class="exp-date">{{ formatDate(row.expected_date) }}</div>
              <div class="exp-hint" :class="{ 'overdue': getOverdueDays(row) > 0 }">
                {{ getRelativeTime(row) }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Сума" width="140" align="right" sortable="custom" prop="total_amount">
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
      <div class="pagination-container">
        <div class="page-size-picker">
          Показати 
          <el-select v-model="pageSize" size="small" style="width: 70px; margin: 0 8px;" @change="currentPage = 1">
            <el-option v-for="s in [10, 20, 50, 100]" :key="s" :label="s" :value="s" />
          </el-select>
          з {{ filteredOrders.length }} записів
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

    <!-- Procurement Needs Drawer -->
    <el-drawer v-model="needsDrawerVisible" title="Створити з потреб виробництва" size="720px">
      <div class="needs-head">
        <div>
          <h3>Дефіцитні матеріали</h3>
          <p>Оберіть позиції, які потрібно додати у замовлення постачальнику.</p>
        </div>
        <el-select v-model="needsSupplierId" placeholder="Оберіть постачальника" filterable clearable class="needs-supplier-select">
          <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
      </div>

      <el-table
        v-loading="needsLoading"
        :data="procurementNeeds"
        size="small"
        @selection-change="needsSelection = $event"
      >
        <el-table-column type="selection" width="42" />
        <el-table-column label="Матеріал" min-width="200">
          <template #default="{ row }">
            <div class="mat-name">{{ row.name }}</div>
            <div class="mat-sku">{{ row.sku || 'немає артикула' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Потрібно" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.to_order) }} {{ row.unit }}</template>
        </el-table-column>
        <el-table-column label="Дефіцит" width="100" align="right">
          <template #default="{ row }"><span class="text-danger">{{ formatQty(Math.max(0, Number(row.min_stock || 0) - Number(row.real_balance || 0))) }}</span></template>
        </el-table-column>
        <el-table-column label="Об'єкт" width="150">
          <template #default="{ row }">{{ row.production_order || 'Складські запаси' }}</template>
        </el-table-column>
      </el-table>

      <div class="drawer-footer">
        <el-button @click="needsDrawerVisible = false">Скасувати</el-button>
        <el-button type="primary" :loading="creatingFromNeeds" :disabled="!needsSelection.length" @click="createFromNeeds">
          Створити замовлення
        </el-button>
      </div>
    </el-drawer>

    <!-- Details View Drawer -->
    <el-drawer v-model="drawerVisible" :title="selectedOrder?.order_number || 'Деталі замовлення'" size="480px">
      <template v-if="selectedOrder">
        <div class="drawer-meta">
          <div class="meta-item"><span>Постачальник:</span><strong>{{ getCounterpartyName(selectedOrder.supplier_id) }}</strong></div>
          <div class="meta-item"><span>Очікується:</span><strong>{{ formatDate(selectedOrder.expected_date) }}</strong></div>
          <div class="meta-item"><span>Статус:</span><strong :style="{ color: getStatusColor(normalizeStatus(selectedOrder)) }">{{ getStatusLabel(normalizeStatus(selectedOrder)) }}</strong></div>
          <div class="meta-item"><span>Сума:</span><strong>{{ formatCurrency(selectedOrder.total_amount) }}</strong></div>
        </div>
        <div class="drawer-lines">
          <h4>Склад замовлення</h4>
          <div v-for="line in selectedOrder.lines || []" :key="line.id" class="line-item">
            <div class="line-name">{{ getProductName(line.product_id) }}</div>
            <div class="line-qty">{{ formatQty(line.quantity) }} x {{ formatCurrency(line.price) }}</div>
          </div>
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
import { ref, reactive, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Download, Filter, Close, Setting, MoreFilled, Star, ArrowRight, ArrowDown,
  List, Van, Warning, Wallet, Money, Loading, Refresh, Box, Check, View, Edit, CopyDocument, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const selected = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const sortField = ref('order_date')
const sortOrder = ref('descending')
const searchInputRef = ref(null)

const drawerVisible = ref(false)
const selectedOrder = ref(null)
const needsDrawerVisible = ref(false)
const needsLoading = ref(false)
const procurementNeeds = ref([])
const needsSelection = ref([])
const needsSupplierId = ref(null)
const creatingFromNeeds = ref(false)

const filters = reactive({
  search: '',
  status: '',
  supplierId: '',
  payment: '',
  priority: '',
  expectedDate: '',
  onlyOverdue: false,
  onlyNotReceived: false,
})

const filtersPopoverVisible = ref(false)

const statusOptions = [
  { value: 'draft', label: 'Чернетка' },
  { value: 'ordered', label: 'Замовлено' },
  { value: 'expected', label: 'Очікується' },
  { value: 'partial_received', label: 'Частково отримано' },
  { value: 'received', label: 'Отримано' },
  { value: 'cancelled', label: 'Скасовано' },
]

const paymentOptions = [
  { value: 'unpaid', label: 'Не оплачено' },
  { value: 'partial', label: 'Частково оплачено' },
  { value: 'paid', label: 'Оплачено' },
]

const priorityOptions = [
  { value: 'low', label: 'Низький' },
  { value: 'medium', label: 'Середній' },
  { value: 'high', label: 'Високий' },
  { value: 'urgent', label: 'Терміново' },
]

const expectedOrders = computed(() => orders.value.filter(o => ['ordered', 'expected', 'partial_received'].includes(normalizeStatus(o))))
const overdueOrders = computed(() => orders.value.filter(o => getOverdueDays(o) > 0))
const unpaidOrders = computed(() => orders.value.filter(o => getPaymentStatus(o) === 'unpaid'))
const totalAmount = computed(() => orders.value.reduce((sum, o) => sum + Number(o.total_amount || 0), 0))
const hasActiveFilters = computed(() => Object.values(filters).some(v => v !== '' && v !== false && v !== null))

const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.status) count++
  if (filters.supplierId) count++
  if (filters.payment) count++
  if (filters.priority) count++
  if (filters.expectedDate) count++
  if (filters.onlyOverdue) count++
  if (filters.onlyNotReceived) count++
  return count
})

const activeFilterChips = computed(() => {
  const chips = []
  if (filters.status) chips.push({ key: 'status', label: `Статус: ${getStatusLabel(filters.status)}` })
  if (filters.supplierId) chips.push({ key: 'supplierId', label: `Постачальник: ${getCounterpartyName(filters.supplierId)}` })
  if (filters.payment) chips.push({ key: 'payment', label: `Оплата: ${paymentOptions.find(p => p.value === filters.payment)?.label}` })
  if (filters.priority) chips.push({ key: 'priority', label: `Пріоритет: ${priorityOptions.find(p => p.value === filters.priority)?.label}` })
  if (filters.expectedDate) chips.push({ key: 'expectedDate', label: `Дата: ${formatDate(filters.expectedDate)}` })
  if (filters.onlyOverdue) chips.push({ key: 'onlyOverdue', label: 'Тільки прострочені' })
  if (filters.onlyNotReceived) chips.push({ key: 'onlyNotReceived', label: 'Тільки неотримані' })
  return chips
})

const kpiCards = computed(() => [
  { label: 'Усього замовлень', value: orders.value.length, icon: 'ShoppingCart', bg: 'var(--erp-primary-light)', color: 'var(--erp-primary)', trend: '+12%', trendClass: 'trend-up', path: 'M0 20C10 25 20 15 30 18C40 21 50 10 64 5' },
  { label: 'Очікується', value: expectedOrders.value.length, icon: 'Box', bg: 'var(--erp-status-success-bg)', color: 'var(--erp-status-success)', sub: formatCurrency(orders.value.filter(o => normalizeStatus(o) === 'expected').reduce((s, o) => s + Number(o.total_amount || 0), 0)), path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 10' },
  { label: 'Прострочено', value: overdueOrders.value.length, icon: 'Warning', bg: 'var(--erp-status-danger-bg)', color: 'var(--erp-status-danger)', sub: 'Потребують уваги', path: 'M0 10C10 15 20 12 30 18C40 24 50 20 64 25' },
  { label: 'Не оплачено', value: unpaidOrders.value.length, icon: 'Wallet', bg: 'var(--erp-status-warning-bg)', color: 'var(--erp-status-warning)', sub: 'Загальна сума богу', path: 'M0 20C10 15 20 18 30 12C40 6 50 10 64 8' },
  { label: 'Загальна сума', value: formatCurrency(totalAmount.value), icon: 'Money', bg: 'var(--erp-status-info-bg)', color: 'var(--erp-status-info)', trend: '+8%', trendClass: 'trend-up', path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 5' },
])

const filteredOrders = computed(() => {
  const q = filters.search.trim().toLowerCase()
  let list = orders.value.filter(order => {
    const materialText = (order.lines || []).map(line => getProductName(line.product_id)).join(' ').toLowerCase()
    const matchesSearch = !q ||
      order.order_number?.toLowerCase().includes(q) ||
      getCounterpartyName(order.supplier_id).toLowerCase().includes(q) ||
      materialText.includes(q)

    return matchesSearch &&
      (!filters.status || normalizeStatus(order) === filters.status) &&
      (!filters.supplierId || order.supplier_id === filters.supplierId) &&
      (!filters.payment || getPaymentStatus(order) === filters.payment) &&
      (!filters.priority || getPriority(order) === filters.priority) &&
      (!filters.expectedDate || sameDate(order.expected_date, filters.expectedDate)) &&
      (!filters.onlyOverdue || getOverdueDays(order) > 0) &&
      (!filters.onlyNotReceived || !['received', 'cancelled'].includes(normalizeStatus(order)))
  })

  list = list.sort((a, b) => {
    let va = a[sortField.value]
    let vb = b[sortField.value]
    if (va < vb) return sortOrder.value === 'ascending' ? -1 : 1
    if (va > vb) return sortOrder.value === 'ascending' ? 1 : -1
    return 0
  })

  return list
})

const pagedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredOrders.value.slice(start, start + pageSize.value)
})

const fetchOrders = async () => {
  loading.value = true
  try {
    const [ordersRes, suppliersRes, warehousesRes, productsRes] = await Promise.all([
      api.get('/api/v1/purchase-orders', { params: { limit: 500 } }),
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products'),
    ])
    orders.value = ordersRes.data || []
    suppliers.value = suppliersRes.data || []
    warehouses.value = warehousesRes.data || []
    products.value = productsRes.data || []
  } catch {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const openNeedsDrawer = async () => {
  needsDrawerVisible.value = true
  needsLoading.value = true
  try {
    const res = await api.get('/api/v1/purchase-orders/procurement-alerts')
    procurementNeeds.value = [...(res.data?.critical || []), ...(res.data?.soon || [])]
    needsSupplierId.value = procurementNeeds.value.find(item => item.default_supplier_id)?.default_supplier_id || suppliers.value[0]?.id || null
  } catch {
    ElMessage.error('Не вдалося завантажити потреби виробництва')
  } finally {
    needsLoading.value = false
  }
}

const createFromNeeds = async () => {
  const supplierId = needsSupplierId.value
  const warehouseId = warehouses.value.find(w => w.is_default)?.id || warehouses.value[0]?.id

  if (!supplierId) return ElMessage.warning('Оберіть постачальника')
  if (!warehouseId) return ElMessage.warning('Не знайдено склад')

  creatingFromNeeds.value = true
  try {
    const lines = needsSelection.value.map(item => ({
      product_id: item.product_id,
      quantity: Number(item.to_order || 1),
      price: 0,
      total: 0,
      attribute_values: [],
    }))

    const res = await api.post('/api/v1/purchase-orders', {
      order_number: 'Авто',
      order_date: new Date().toISOString(),
      expected_date: new Date(Date.now() + 7 * 86400000).toISOString(),
      supplier_id: supplierId,
      warehouse_id: warehouseId,
      currency: 'UAH',
      total_amount: 0,
      status: 'draft',
      notes: 'Створено з потреб виробництва',
      lines,
    })

    ElMessage.success('Замовлення створено')
    needsDrawerVisible.value = false
    await fetchOrders()
    router.push(`/purchases/orders/${res.data.id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка створення')
  } finally {
    creatingFromNeeds.value = false
  }
}

const resetFilters = () => {
  Object.assign(filters, {
    search: '', status: '', supplierId: '', payment: '', priority: '', expectedDate: '',
    onlyOverdue: false, onlyNotReceived: false
  })
}

const clearFilterChip = (key) => {
  if (typeof filters[key] === 'boolean') filters[key] = false
  else filters[key] = ''
}

const handleSortChange = ({ prop, order }) => {
  sortField.value = prop || 'order_date'
  sortOrder.value = order || 'descending'
}

const handleSelectionChange = rows => { selected.value = rows }
const handleCreate = () => router.push('/purchases/orders/new')
const handleEdit = row => router.push(`/purchases/orders/${row.id}`)
const openView = row => {
  selectedOrder.value = row
  drawerVisible.value = true
}

const handleRowCommand = (command, row) => {
  if (command === 'view') openView(row)
  if (command === 'edit') handleEdit(row)
  if (command === 'duplicate') router.push({ path: '/purchases/orders/new', query: { copy_from: row.id } })
  if (command === 'delete') handleDelete(row)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити замовлення ${row.order_number}?`, 'Підтвердження', { type: 'warning' }).then(async () => {
    await api.delete(`/api/v1/purchase-orders/${row.id}`)
    ElMessage.success('Видалено')
    fetchOrders()
  })
}

const bulkConfirm = async () => {
  for (const row of selected.value) {
    try { await api.put(`/api/v1/purchase-orders/${row.id}`, { status: 'ordered' }) } catch {}
  }
  selected.value = []
  ElMessage.success('Замовлення підтверджено')
  fetchOrders()
}

const bulkDelete = async () => {
  await ElMessageBox.confirm(`Видалити ${selected.value.length} замовлень?`, 'Увага', { type: 'warning' })
  for (const row of selected.value) {
    try { await api.delete(`/api/v1/purchase-orders/${row.id}`) } catch {}
  }
  selected.value = []
  ElMessage.success('Видалено')
  fetchOrders()
}

const normalizeStatus = (row) => {
  if (row.status === 'draft') return 'draft'
  if (row.status === 'done' || row.status === 'received') return 'received'
  if (row.status === 'cancelled') return 'cancelled'
  if (row.received_quantity > 0) return 'partial_received'
  return 'ordered'
}

const getStatusLabel = v => statusOptions.find(s => s.value === v)?.label || '—'
const getStatusBadgeStyle = v => {
  const bg = getStatusColor(v) + '15'
  const color = getStatusColor(v)
  return { backgroundColor: bg, color: color }
}

const getPaymentBadgeStyle = row => {
  const status = getPaymentStatus(row)
  const color = getPaymentColor(row)
  return { backgroundColor: color + '15', color: color }
}

const getStatusColor = v => {
  if (v === 'draft') return '#94A3B8'
  if (v === 'ordered') return 'var(--erp-status-success)'
  if (v === 'expected') return 'var(--erp-status-info)'
  if (v === 'partial_received') return 'var(--erp-status-warning)'
  if (v === 'received') return 'var(--erp-status-success)'
  return 'var(--erp-text-muted)'
}

const getPaymentStatus = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  if (total > 0 && paid >= total) return 'paid'
  if (paid > 0) return 'partial'
  return 'unpaid'
}

const getPaymentLabel = row => paymentOptions.find(p => p.value === getPaymentStatus(row))?.label || 'Не оплачено'
const getPaymentColor = row => {
  const s = getPaymentStatus(row)
  if (s === 'paid') return 'var(--erp-status-success)'
  if (s === 'partial') return 'var(--erp-status-info)'
  return 'var(--erp-status-danger)'
}

const getPaymentPercent = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  return total ? Math.round((paid / total) * 100) : 0
}

const getPriority = row => {
  if (getOverdueDays(row) > 0) return 'urgent'
  return 'medium'
}

const getCounterpartyName = id => suppliers.value.find(s => s.id === id)?.name || '—'
const getProductName = id => products.value.find(p => p.id === id)?.name || ''
const getMaterialPreview = row => {
  const names = (row.lines || []).map(l => getProductName(l.product_id)).filter(Boolean)
  return { text: names.slice(1).join(', ') || 'Завантаження...' }
}

const getOverdueDays = row => {
  if (!row.expected_date || normalizeStatus(row) === 'received') return 0
  const diff = new Date() - new Date(row.expected_date)
  return Math.max(0, Math.floor(diff / 86400000))
}

const getRelativeTime = row => {
  const days = getOverdueDays(row)
  if (days > 0) return `прострочено на ${days} дн.`
  if (!row.expected_date) return '—'
  const d = Math.ceil((new Date(row.expected_date) - new Date()) / 86400000)
  return d > 0 ? `через ${d} дн.` : 'сьогодні'
}

const getSupplierColor = id => {
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return colors[String(id).length % colors.length]
}

const sameDate = (d1, d2) => d1 && d2 && d1.slice(0, 10) === d2.slice(0, 10)
const formatDate = d => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatQty = v => Number(v || 0).toLocaleString('uk-UA')
const formatCurrency = v => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(v)

const handleKeydown = e => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return
  if (e.key === 'n' || e.key === 'N') { e.preventDefault(); handleCreate() }
  if (e.key === '/') { e.preventDefault(); searchInputRef.value?.focus() }
}

const handleExport = () => { ElMessage.info('Експорт замовлень розпочато...') }

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  fetchOrders()
})
onActivated(fetchOrders)
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.purchase-orders-page { 
  display: flex; 
  flex-direction: column; 
  gap: 24px; 
  height: 100%; 
  padding: 0 0 24px;
}

/* ===== PAGE HEADER ===== */
.page-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-end; 
  padding: 0 24px;
}

.page-title { 
  font-size: 26px; 
  font-weight: 800; 
  color: var(--erp-text-heading); 
  margin: 0; 
  letter-spacing: -0.5px;
}

.page-subtitle { 
  font-size: 14px; 
  color: var(--erp-text-muted); 
  margin: 4px 0 0; 
}

.header-actions { 
  display: flex; 
  gap: 12px; 
}

.btn-outline { 
  background: #FFF; 
  border: 1px solid var(--erp-border); 
  border-radius: var(--erp-radius-btn); 
  height: 40px; 
  font-weight: 600; 
  color: var(--erp-text-secondary); 
}

.btn-secondary { 
  background: var(--erp-bg-surface-soft); 
  border: 1px solid var(--erp-border); 
  border-radius: var(--erp-radius-btn); 
  height: 40px; 
  font-weight: 600; 
  color: var(--erp-text-primary); 
}

.btn-primary { 
  background: var(--erp-primary); 
  border: none; 
  border-radius: var(--erp-radius-btn); 
  height: 40px; 
  padding: 0 20px; 
  font-weight: 700; 
  color: #FFF; 
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.15); 
}

/* ===== KPI GRID ===== */
.kpi-grid { 
  display: grid; 
  grid-template-columns: repeat(5, 1fr); 
  gap: 20px; 
  padding: 0 24px;
}

.kpi-card { 
  background: #FFF; 
  border-radius: var(--erp-radius-kpi); 
  padding: 20px; 
  box-shadow: var(--erp-shadow-soft); 
  display: flex; 
  align-items: flex-start; 
  gap: 16px; 
  height: 116px;
  border: 1px solid var(--erp-border);
  transition: transform 0.2s, shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--erp-shadow-hover);
}

.kpi-icon-badge { 
  width: 48px; 
  height: 48px; 
  border-radius: 14px; 
  display: grid; 
  place-items: center; 
  font-size: 22px; 
  flex-shrink: 0;
}

.kpi-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.kpi-label { 
  font-size: 12px; 
  font-weight: 600; 
  color: var(--erp-text-muted); 
  text-transform: uppercase; 
  letter-spacing: 0.5px; 
  margin-bottom: 4px;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 4px;
}

.kpi-value { 
  font-size: 24px; 
  font-weight: 800; 
  color: var(--erp-text-heading); 
}

.kpi-sparkline {
  opacity: 0.6;
}

.kpi-subtext { 
  font-size: 11px; 
  font-weight: 600; 
}
.trend-up { color: var(--erp-status-success); }

/* ===== FILTER TOOLBAR ===== */
.filter-toolbar { 
  background: #FFF; 
  margin: 0 24px;
  border-radius: var(--erp-radius-card); 
  padding: 12px 16px; 
  box-shadow: var(--erp-shadow-soft);
  border: 1px solid var(--erp-border);
}

.filter-main-row { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  flex-wrap: wrap; 
}

.search-field { 
  flex: 1; 
  min-width: 240px; 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  background: var(--erp-bg-page); 
  padding: 0 14px; 
  border-radius: var(--erp-radius-input); 
  border: 1px solid var(--erp-border); 
  height: 42px; 
  transition: border-color 0.2s;
}

.search-field:focus-within {
  border-color: var(--erp-primary);
  background: #FFF;
}

.search-field el-icon {
  color: var(--erp-text-muted);
}

.search-field input { 
  flex: 1; 
  border: none; 
  background: transparent; 
  outline: none; 
  font-size: 14px; 
  color: var(--erp-text-primary);
}

.filter-select { width: 130px; }
.filter-select-wide { width: 200px; }
.filter-date-picker { width: 150px; }

:deep(.el-input__wrapper) {
  border-radius: var(--erp-radius-input) !important;
  box-shadow: none !important;
  border: 1px solid var(--erp-border) !important;
  height: 42px !important;
}

.filter-divider {
  width: 1px;
  height: 24px;
  background: var(--erp-border);
  margin: 0 4px;
}

/* ===== TOOLBAR BUTTONS ===== */
.toolbar-btn {
  height: 42px;
  border: 1px solid var(--erp-border);
  background: var(--erp-bg-page);
  color: var(--erp-text-secondary);
  border-radius: var(--erp-radius-btn);
  font-weight: 600;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  white-space: nowrap;
  transition: all 0.18s;
}
.toolbar-btn:hover {
  background: #FFF;
  border-color: var(--erp-primary);
  color: var(--erp-primary);
}
.toolbar-btn.icon-only {
  width: 42px;
  padding: 0;
  justify-content: center;
}
.btn-label { font-size: 13px; }

/* Filters button with active state */
.filters-btn { }
.filters-btn.filters-active {
  background: var(--erp-primary-light);
  border-color: var(--erp-primary);
  color: var(--erp-primary);
}
.filter-badge :deep(.el-badge__content) {
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 5px;
  min-width: 16px;
}

/* ===== FILTERS PANEL (inside popover) ===== */
.filters-panel { padding: 4px 0; }
.filters-panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--erp-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.fp-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}
.fp-row label {
  font-size: 12px;
  font-weight: 600;
  color: var(--erp-text-muted);
}

.fp-toggles {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}
.fp-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid var(--erp-border);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--erp-text-secondary);
  background: var(--erp-bg-page);
  transition: all 0.18s;
}
.fp-toggle:hover { border-color: var(--erp-primary); }
.fp-toggle.active {
  background: var(--erp-primary-light);
  border-color: var(--erp-primary);
  color: var(--erp-primary);
}
.fp-toggle-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid currentColor;
  transition: background 0.18s;
}
.fp-toggle.active .fp-toggle-dot {
  background: currentColor;
}

.fp-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 4px;
  border-top: 1px solid var(--erp-border);
  margin-top: 4px;
}

/* ===== ACTIVE FILTER CHIPS ===== */
.active-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.active-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 26px;
  padding: 0 10px;
  border-radius: 13px;
  background: var(--erp-primary-light);
  color: var(--erp-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--erp-primary);
  transition: all 0.15s;
}
.active-chip:hover {
  background: var(--erp-primary);
  color: #FFF;
}
.chip-close { font-size: 11px; }

/* ===== TABLE AREA ===== */
.table-surface { 
  background: #FFF; 
  margin: 0 24px;
  border-radius: var(--erp-radius-card); 
  padding: 4px; 
  box-shadow: var(--erp-shadow-soft); 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  border: 1px solid var(--erp-border);
}

.nexora-table :deep(.el-table__header th) { 
  background: #F8FAFC !important; 
  color: #7A88A0; 
  font-size: 12px; 
  font-weight: 600; 
  border-bottom: 1px solid var(--erp-border); 
  padding: 16px 0; 
}

.nexora-table :deep(.el-table__row td) {
  height: 64px;
  padding: 0 !important;
}

.cell-id.clickable { color: var(--erp-primary); font-weight: 700; cursor: pointer; font-size: 14px; }
.cell-date { font-size: 12px; color: var(--erp-text-muted); margin-top: 2px; }

.supplier-cell { display: flex; align-items: center; gap: 12px; }
.supplier-logo { 
  width: 36px; 
  height: 36px; 
  border-radius: 10px; 
  color: #FFF; 
  display: grid; 
  place-items: center; 
  font-weight: 800; 
  font-size: 15px; 
  flex-shrink: 0;
}
.supplier-name { font-weight: 600; font-size: 14px; color: var(--erp-text-primary); }
.supplier-code { font-size: 11px; color: var(--erp-text-muted); margin-top: 1px; }

.materials-info .mat-count { font-size: 13px; font-weight: 600; color: var(--erp-text-primary); }
.materials-info .mat-list { font-size: 12px; color: var(--erp-text-muted); margin-top: 2px; }

/* Badges */
.badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.expected-cell .exp-date { font-size: 13px; font-weight: 600; color: var(--erp-text-primary); }
.expected-cell .exp-hint { font-size: 11px; color: var(--erp-status-success); font-weight: 700; margin-top: 2px; }
.expected-cell .exp-hint.overdue { color: var(--erp-status-danger); }

.amount-cell .total { font-weight: 700; font-size: 14px; color: var(--erp-text-heading); }
.amount-cell .tax { font-size: 11px; color: var(--erp-text-muted); }

.btn-row-more {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  color: var(--erp-text-secondary);
  transition: all 0.2s;
}
.btn-row-more:hover {
  background: var(--erp-bg-surface-soft);
  color: var(--erp-primary);
}

.pagination-container { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-top: 1px solid var(--erp-border); }
.page-size-picker { font-size: 13px; color: var(--erp-text-secondary); }

/* Bulk Actions */
.bulk-actions-bar { 
  position: fixed; 
  bottom: 32px; 
  left: 50%; 
  transform: translateX(-50%); 
  background: #1B2430; 
  color: #FFF; 
  padding: 12px 24px; 
  border-radius: 16px; 
  display: flex; 
  align-items: center; 
  gap: 24px; 
  z-index: 1000; 
  box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
}

/* Other elements remain similar but use tokens */
</style>
