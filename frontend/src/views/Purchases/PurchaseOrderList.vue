<template>
  <div class="purchase-orders-page">
    <!-- Breadcrumbs & Header -->
    <div class="breadcrumb-nav">
      Закупівлі <el-icon><ArrowRight /></el-icon> Замовлення постачальникам
    </div>

    <div class="page-header">
      <div class="header-content">
        <h1>Замовлення постачальникам <el-icon class="fav-star"><Star /></el-icon></h1>
        <p>Контроль закупівель матеріалів, оплат і очікуваних поставок</p>
      </div>
      <div class="header-actions">
        <el-button class="btn-export" @click="handleExport">
          <el-icon><Download /></el-icon> Експорт
        </el-button>
        <el-button class="btn-secondary" @click="openNeedsDrawer">
          <el-icon><Box /></el-icon> Створити з потреб виробництва
        </el-button>
        <el-button type="primary" class="btn-create" @click="handleCreate">
          <el-icon><Plus /></el-icon> Нове замовлення
        </el-button>
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
          <div class="kpi-chart" v-if="kpi.path">
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
      <div class="filter-row top-filter-row">
        <div class="search-wrap">
          <el-icon><Search /></el-icon>
          <input 
            ref="searchInputRef"
            type="text" 
            v-model="filters.search" 
            placeholder="Пошук за номером, постачальником, матеріалом..." 
          />
        </div>
        
        <div class="filter-group">
          <span class="filter-label">Статус:</span>
          <el-select v-model="filters.status" placeholder="Усі" clearable class="minimal-select">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </div>

        <div class="filter-group">
          <span class="filter-label">Постачальник:</span>
          <el-select v-model="filters.supplierId" placeholder="Усі" clearable filterable class="minimal-select">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </div>

        <div class="filter-group">
          <span class="filter-label">Оплата:</span>
          <el-select v-model="filters.payment" placeholder="Усі" clearable class="minimal-select">
            <el-option v-for="p in paymentOptions" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </div>
      </div>

      <div class="filter-row bottom-filter-row">
        <div class="filter-group">
          <span class="filter-label">Пріоритет:</span>
          <el-select v-model="filters.priority" placeholder="Усі" clearable class="minimal-select">
            <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </div>

        <el-date-picker
          v-model="filters.expectedDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="Очікувана дата"
          class="date-picker-compact"
        />

        <div class="checkbox-chips">
          <div 
            class="filter-chip" 
            :class="{ active: filters.onlyOverdue }"
            @click="filters.onlyOverdue = !filters.onlyOverdue"
          >
            <el-icon v-if="filters.onlyOverdue"><Check /></el-icon>
            Тільки прострочені
          </div>
          <div 
            class="filter-chip" 
            :class="{ active: filters.onlyNotReceived }"
            @click="filters.onlyNotReceived = !filters.onlyNotReceived"
          >
            <el-icon v-if="filters.onlyNotReceived"><Check /></el-icon>
            Тільки неотримані
          </div>
        </div>

        <div class="filter-actions">
          <el-button circle class="btn-refresh" @click="fetchOrders">
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button link class="btn-clear-all" v-if="hasActiveFilters" @click="resetFilters">Очистити все</el-button>
          <el-button circle link class="btn-table-settings"><el-icon><Setting /></el-icon></el-button>
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

        <el-table-column label="Статус" width="150" align="center">
          <template #default="{ row }">
            <div class="status-dot-wrap">
              <span class="status-dot" :style="{ backgroundColor: getStatusColor(normalizeStatus(row)) }"></span>
              <span class="status-text" :style="{ color: getStatusColor(normalizeStatus(row)) }">
                {{ getStatusLabel(normalizeStatus(row)) }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="160" align="center">
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

        <el-table-column label="Очікується" width="150" sortable="custom" prop="expected_date">
          <template #default="{ row }">
            <div class="expected-info">
              <div class="exp-date">{{ formatDate(row.expected_date) }}</div>
              <div class="exp-relative" :class="{ 'overdue': getOverdueDays(row) > 0 }">
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
  Plus, Search, Download, Filter, Setting, MoreFilled, Star, ArrowRight, ArrowDown,
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

const kpiCards = computed(() => [
  { label: 'Усього замовлень', value: orders.value.length, icon: 'ShoppingCart', bg: '#F1F5FF', color: '#1463FF', trend: '+18%', trendClass: 'trend-up', path: 'M0 20C10 25 20 15 30 18C40 21 50 10 64 5' },
  { label: 'Очікується постачання', value: expectedOrders.value.length, icon: 'Box', bg: '#F0FDF4', color: '#10B981', sub: formatCurrency(orders.value.filter(o => normalizeStatus(o) === 'expected').reduce((s, o) => s + Number(o.total_amount || 0), 0)), path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 10' },
  { label: 'На підтвердженні', value: orders.value.filter(o => o.status === 'ordered').length, icon: 'Check', bg: '#F0F9FF', color: '#0EA5E9', sub: 'Активні запити', path: 'M0 20C10 15 20 18 30 12C40 6 50 10 64 8' },
  { label: 'Прострочено', value: overdueOrders.value.length, icon: 'Warning', bg: '#FEF2F2', color: '#EF4444', sub: 'Потребують уваги', path: 'M0 10C10 15 20 12 30 18C40 24 50 20 64 25' },
  { label: 'Сума замовлень', value: formatCurrency(totalAmount.value), icon: 'Wallet', bg: '#F0FDFA', color: '#0D9488', trend: '+22%', trendClass: 'trend-up', path: 'M0 25C10 20 20 22 30 15C40 8 50 12 64 5' },
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
const getStatusColor = v => {
  if (v === 'draft') return '#94A3B8'
  if (v === 'ordered') return '#10B981'
  if (v === 'expected') return '#3B82F6'
  if (v === 'partial_received') return '#F59E0B'
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

const getPaymentLabel = row => paymentOptions.find(p => p.value === getPaymentStatus(row))?.label || 'Не оплачено'
const getPaymentColor = row => {
  const s = getPaymentStatus(row)
  if (s === 'paid') return '#10B981'
  if (s === 'partial') return '#3B82F6'
  return '#EF4444'
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
.purchase-orders-page { display: flex; flex-direction: column; gap: 16px; height: 100%; }
.breadcrumb-nav { font-size: 12px; color: var(--erp-text-muted); display: flex; align-items: center; gap: 8px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.header-content h1 { font-size: 24px; font-weight: 800; color: var(--erp-text-heading); display: flex; align-items: center; gap: 12px; margin: 0; }
.header-content p { font-size: 13px; color: var(--erp-text-muted); margin: 4px 0 0; }
.fav-star { font-size: 20px; color: #CBD5E1; cursor: pointer; }
.header-actions { display: flex; gap: 10px; }

.btn-export, .btn-secondary { background: #FFF; border: 1px solid #E2E8F0; border-radius: 10px; height: 40px; font-weight: 600; color: var(--erp-text-main); }
.btn-create { background: var(--erp-primary); border: none; border-radius: 10px; height: 40px; padding: 0 16px; font-weight: 700; color: #FFF; box-shadow: 0 4px 12px rgba(20, 99, 255, 0.2); }

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
.kpi-card { background: #FFF; border-radius: 20px; padding: 16px; box-shadow: var(--erp-shadow-soft); display: flex; flex-direction: column; justify-content: space-between; min-height: 100px; }
.kpi-main { display: grid; grid-template-columns: 44px 1fr 64px; gap: 12px; align-items: flex-start; }
.kpi-icon-box { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 20px; }
.kpi-label { font-size: 11px; font-weight: 600; color: var(--erp-text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 22px; font-weight: 800; color: var(--erp-text-heading); margin-top: 2px; }
.kpi-footer { font-size: 11px; margin-top: 10px; font-weight: 600; }
.trend-up { color: #10B981; }

.filter-panel { background: #FFF; border-radius: 16px; padding: 12px 16px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01); display: flex; flex-direction: column; gap: 12px; }
.filter-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.search-wrap { flex: 1; min-width: 200px; display: flex; align-items: center; gap: 8px; background: #F8FAFC; padding: 0 12px; border-radius: 10px; border: 1px solid #E2E8F0; height: 38px; }
.search-wrap input { flex: 1; border: none; background: transparent; outline: none; font-size: 13px; }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-label { font-size: 12px; color: var(--erp-text-muted); font-weight: 600; }
.minimal-select { width: 140px; }
.date-picker-compact { width: 160px; }

.checkbox-chips { display: flex; gap: 8px; }
.filter-chip { padding: 0 12px; height: 32px; border-radius: 20px; border: 1px solid #E2E8F0; font-size: 12px; display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.2s; color: var(--erp-text-muted); font-weight: 600; }
.filter-chip.active { background: var(--erp-primary-light); border-color: var(--erp-primary); color: var(--erp-primary); }

.filter-actions { display: flex; align-items: center; gap: 12px; margin-left: auto; }
.btn-refresh { border-color: #E2E8F0; color: var(--erp-text-muted); }
.btn-clear-all { font-size: 12px; font-weight: 700; color: var(--erp-primary); }

.bulk-actions-bar { position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%); background: #1E293B; color: #FFF; padding: 12px 24px; border-radius: 12px; display: flex; align-items: center; gap: 24px; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.bulk-info { font-size: 14px; }
.bulk-btns { display: flex; gap: 8px; }

.table-surface { background: #FFF; border-radius: 20px; padding: 8px; box-shadow: var(--erp-shadow-soft); flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.nexora-table :deep(.el-table__header th) { background: #FFF !important; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; border-bottom: 1px solid #F1F5F9; padding: 12px 0; }

.cell-id.clickable { color: var(--erp-primary); font-weight: 800; cursor: pointer; }
.cell-date { font-size: 11px; color: var(--erp-text-muted); }
.supplier-cell { display: flex; align-items: center; gap: 10px; }
.supplier-logo { width: 32px; height: 32px; border-radius: 8px; color: #FFF; display: grid; place-items: center; font-weight: 800; font-size: 14px; }
.supplier-name { font-weight: 700; font-size: 13px; color: var(--erp-text-heading); }
.supplier-code { font-size: 11px; color: var(--erp-text-muted); }
.materials-info .mat-count { font-size: 12px; font-weight: 700; color: var(--erp-text-main); }
.materials-info .mat-list { font-size: 11px; color: var(--erp-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.status-dot-wrap { display: flex; align-items: center; gap: 8px; justify-content: center; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-text { font-size: 12px; font-weight: 700; }

.payment-dot-wrap { display: flex; align-items: center; gap: 8px; justify-content: center; }
.payment-dot { width: 6px; height: 6px; border-radius: 50%; }
.pay-label { font-size: 12px; font-weight: 700; }
.pay-percent { font-size: 11px; color: var(--erp-text-muted); }

.expected-info .exp-date { font-size: 12px; font-weight: 700; }
.expected-info .exp-relative { font-size: 11px; color: #10B981; font-weight: 700; }
.expected-info .exp-relative.overdue { color: #EF4444; }
.amount-cell .total { font-weight: 800; font-size: 14px; }
.amount-cell .tax { font-size: 10px; color: var(--erp-text-muted); text-transform: uppercase; }

.pagination-container { display: flex; justify-content: space-between; align-items: center; padding: 12px 8px; }
.page-size-picker { font-size: 12px; color: var(--erp-text-muted); }

.needs-head { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
.needs-head h3 { margin: 0; }
.needs-supplier-select { width: 240px; }
.drawer-footer { padding: 20px; border-top: 1px solid #F1F5F9; display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
.drawer-meta { background: #F8FAFC; padding: 16px; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.meta-item span { display: block; font-size: 11px; color: var(--erp-text-muted); text-transform: uppercase; font-weight: 700; }
.meta-item strong { font-size: 14px; }
.drawer-lines h4 { margin-bottom: 12px; border-bottom: 1px solid #F1F5F9; padding-bottom: 8px; }
.line-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #F1F5F9; }
.line-name { font-size: 13px; font-weight: 600; }
.line-qty { font-size: 12px; color: var(--erp-text-muted); }
</style>
