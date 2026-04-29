<template>
  <div class="purchase-orders-page">
    <div class="po-top">
      <div class="po-header">
        <div>
          <h1>Замовлення постачальникам</h1>
          <p>Контроль закупівель матеріалів, оплат і очікуваних поставок</p>
        </div>
        <div class="po-header-actions">
          <button class="po-secondary-btn" @click="openNeedsDrawer">
            <el-icon><Box /></el-icon>
            Створити з потреб виробництва
          </button>
          <button class="po-primary-btn" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            Нове замовлення
          </button>
        </div>
      </div>

      <div class="po-kpis">
        <div class="po-kpi">
          <span>Всього замовлень</span>
          <strong>{{ orders.length }}</strong>
        </div>
        <div class="po-kpi po-kpi-blue">
          <span>Очікується поставка</span>
          <strong>{{ expectedOrders.length }}</strong>
        </div>
        <div class="po-kpi po-kpi-rose">
          <span>Прострочено</span>
          <strong>{{ overdueOrders.length }}</strong>
        </div>
        <div class="po-kpi po-kpi-amber">
          <span>Не оплачено</span>
          <strong>{{ unpaidOrders.length }}</strong>
        </div>
        <div class="po-kpi po-kpi-green">
          <span>Загальна сума</span>
          <strong>{{ formatCurrency(totalAmount) }}</strong>
        </div>
      </div>

      <div class="po-filters">
        <el-input
          ref="searchInputRef"
          v-model="filters.search"
          placeholder="Пошук за номером, постачальником, матеріалом..."
          :prefix-icon="Search"
          clearable
          class="po-search"
        />
        <el-select v-model="filters.status" placeholder="Статус" clearable>
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filters.supplierId" placeholder="Постачальник" clearable filterable>
          <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filters.payment" placeholder="Оплата" clearable>
          <el-option v-for="p in paymentOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="Пріоритет" clearable>
          <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-date-picker
          v-model="filters.expectedDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="Очікувана дата"
          class="po-date"
        />
        <el-checkbox v-model="filters.onlyOverdue">Тільки прострочені</el-checkbox>
        <el-checkbox v-model="filters.onlyNotReceived">Тільки неотримані</el-checkbox>
        <button class="po-refresh-btn" @click="fetchOrders">
          <el-icon><Refresh /></el-icon>
        </button>
        <button class="po-reset-btn" v-if="hasActiveFilters" @click="resetFilters">Скинути</button>
      </div>

      <transition name="bulk-bar">
        <div class="po-bulk" v-if="selected.length">
          <span>Виділено: <strong>{{ selected.length }}</strong></span>
          <button @click="bulkConfirm">Підтвердити</button>
          <button class="danger" @click="bulkDelete">Видалити</button>
          <button class="ghost" @click="selected = []">Скасувати вибір</button>
        </div>
      </transition>
    </div>

    <div class="po-table-card">
      <el-table
        v-loading="loading"
        :data="pagedOrders"
        height="100%"
        size="small"
        class="po-table"
        empty-text=""
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="42" align="center" />

        <el-table-column label="№" width="54" align="center">
          <template #default="{ $index }">
            <span class="row-num">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Номер / дата" min-width="150" sortable="custom" prop="order_date">
          <template #default="{ row }">
            <button class="order-link" @click="openView(row)">{{ row.order_number }}</button>
            <small>{{ formatDate(row.order_date) }}</small>
          </template>
        </el-table-column>

        <el-table-column label="Постачальник" min-width="180">
          <template #default="{ row }">
            <strong class="supplier-name">{{ getCounterpartyName(row.supplier_id) || '—' }}</strong>
            <small>{{ getCounterpartyPhone(row.supplier_id) || 'без телефону' }}</small>
          </template>
        </el-table-column>

        <el-table-column label="Матеріали" min-width="220">
          <template #default="{ row }">
            <div class="materials-cell">
              <span>{{ getMaterialPreview(row).first }}</span>
              <small v-if="getMaterialPreview(row).more">+ ще {{ getMaterialPreview(row).more }} позиції</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Пов'язано з" width="130">
          <template #default="{ row }">
            <div class="related-cell" v-if="getRelatedDocs(row).length">
              <span v-for="doc in getRelatedDocs(row)" :key="doc">{{ doc }}</span>
            </div>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="145" align="center">
          <template #default="{ row }">
            <span class="po-badge" :class="`status-${normalizeStatus(row)}`">{{ getStatusLabel(normalizeStatus(row)) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="145" align="center">
          <template #default="{ row }">
            <span class="po-badge" :class="`payment-${getPaymentStatus(row)}`">{{ getPaymentLabel(row) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Очікується" width="150" align="center" sortable="custom" prop="expected_date">
          <template #default="{ row }">
            <div class="expected-cell">
              <span>{{ formatDate(row.expected_date) }}</span>
              <small v-if="getOverdueDays(row) > 0">Прострочено {{ getOverdueDays(row) }} дні</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Сума" width="130" align="right" sortable="custom" prop="total_amount">
          <template #default="{ row }">
            <strong class="amount">{{ formatCurrency(row.total_amount) }}</strong>
          </template>
        </el-table-column>

        <el-table-column label="Пріоритет" width="120" align="center">
          <template #default="{ row }">
            <span class="priority-pill" :class="`priority-${getPriority(row)}`">{{ getPriorityLabel(getPriority(row)) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="128" align="center" fixed="right">
          <template #default="{ row }">
            <div class="po-actions" @click.stop>
              <button title="Переглянути" @click="openView(row)"><el-icon><View /></el-icon></button>
              <button title="Редагувати" @click="handleEdit(row)"><el-icon><Edit /></el-icon></button>
              <el-dropdown trigger="click" @command="cmd => handleRowCommand(cmd, row)">
                <button title="Ще"><el-icon><MoreFilled /></el-icon></button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="duplicate">Дублювати</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>Видалити</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <div class="po-empty">
            <h3>Замовлень постачальникам ще немає</h3>
            <p>Створіть перше замовлення вручну або сформуйте його з потреб виробництва.</p>
            <div>
              <button class="po-primary-btn" @click="handleCreate"><el-icon><Plus /></el-icon> Нове замовлення</button>
              <button class="po-secondary-btn" @click="openNeedsDrawer"><el-icon><Box /></el-icon> Створити з потреб виробництва</button>
            </div>
          </div>
        </template>
      </el-table>

      <div class="po-pagination">
        <span>Показано {{ pagedOrders.length }} з {{ filteredOrders.length }}</span>
        <div>
          <el-select v-model="pageSize" size="small" class="page-size" @change="currentPage = 1">
            <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
          </el-select>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="filteredOrders.length"
            background
            layout="prev, pager, next"
          />
        </div>
      </div>
    </div>

    <el-drawer v-model="drawerVisible" :title="selectedOrder?.order_number || 'Замовлення постачальнику'" size="480px">
      <template v-if="selectedOrder">
        <div class="drawer-meta">
          <div><span>Постачальник</span><strong>{{ getCounterpartyName(selectedOrder.supplier_id) || '—' }}</strong></div>
          <div><span>Очікується</span><strong>{{ formatDate(selectedOrder.expected_date) }}</strong></div>
          <div><span>Статус</span><strong>{{ getStatusLabel(normalizeStatus(selectedOrder)) }}</strong></div>
          <div><span>Сума</span><strong>{{ formatCurrency(selectedOrder.total_amount) }}</strong></div>
        </div>
        <h4>Матеріали</h4>
        <div class="drawer-lines">
          <div v-for="line in selectedOrder.lines || []" :key="line.id">
            <span>{{ getProductName(line.product_id) }}</span>
            <strong>{{ formatQty(line.quantity) }} × {{ formatCurrency(line.price) }}</strong>
          </div>
        </div>
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">Закрити</el-button>
          <el-button type="primary" @click="handleEdit(selectedOrder)">Редагувати</el-button>
        </div>
      </template>
    </el-drawer>

    <el-drawer v-model="needsDrawerVisible" title="Створити з потреб виробництва" size="720px">
      <div class="needs-head">
        <div>
          <h3>Дефіцитні матеріали</h3>
          <p>Оберіть позиції, які потрібно додати у замовлення постачальнику.</p>
        </div>
        <el-select v-model="needsSupplierId" placeholder="Постачальник" filterable clearable class="needs-supplier">
          <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
      </div>

      <el-table
        v-loading="needsLoading"
        :data="procurementNeeds"
        size="small"
        class="needs-table"
        @selection-change="needsSelection = $event"
      >
        <el-table-column type="selection" width="42" />
        <el-table-column label="Матеріал" min-width="210">
          <template #default="{ row }">
            <strong>{{ row.name }}</strong>
            <small>{{ row.sku || 'без артикула' }}</small>
          </template>
        </el-table-column>
        <el-table-column label="Потрібно" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.to_order) }} {{ row.unit }}</template>
        </el-table-column>
        <el-table-column label="Доступно" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.current_stock) }}</template>
        </el-table-column>
        <el-table-column label="Дефіцит" width="110" align="right">
          <template #default="{ row }"><strong class="deficit">{{ formatQty(Math.max(0, Number(row.min_stock || 0) - Number(row.real_balance || 0))) }}</strong></template>
        </el-table-column>
        <el-table-column label="Пов'язане виробництво" width="170">
          <template #default="{ row }">{{ row.production_order || 'Виробничі потреби' }}</template>
        </el-table-column>
      </el-table>

      <div class="needs-footer">
        <el-button @click="needsDrawerVisible = false">Скасувати</el-button>
        <el-button type="primary" :loading="creatingFromNeeds" :disabled="!needsSelection.length" @click="createFromNeeds">
          Створити замовлення
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Box, Edit, MoreFilled, Plus, Refresh, Search, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const orders = ref([])
const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const selected = ref([])
const drawerVisible = ref(false)
const selectedOrder = ref(null)
const needsDrawerVisible = ref(false)
const needsLoading = ref(false)
const procurementNeeds = ref([])
const needsSelection = ref([])
const needsSupplierId = ref(null)
const creatingFromNeeds = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const sortField = ref('order_date')
const sortOrder = ref('descending')
const searchInputRef = ref(null)

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
const totalAmount = computed(() => orders.value.reduce((sum, order) => sum + Number(order.total_amount || 0), 0))
const hasActiveFilters = computed(() => Object.values(filters).some(Boolean))

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
    if (['order_date', 'expected_date'].includes(sortField.value)) {
      va = va ? new Date(va).getTime() : 0
      vb = vb ? new Date(vb).getTime() : 0
    }
    if (sortField.value === 'total_amount') {
      va = Number(va || 0)
      vb = Number(vb || 0)
    }
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
    ElMessage.error('Помилка завантаження замовлень')
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
  const supplierId = needsSupplierId.value || needsSelection.value.find(item => item.default_supplier_id)?.default_supplier_id
  const warehouseId = warehouses.value.find(w => w.is_default)?.id || warehouses.value[0]?.id

  if (!supplierId) return ElMessage.warning('Оберіть постачальника')
  if (!warehouseId) return ElMessage.warning('Не знайдено склад для замовлення')

  creatingFromNeeds.value = true
  try {
    const lines = needsSelection.value.map(item => ({
      product_id: item.product_id,
      quantity: Number(item.to_order || 1),
      price: 0,
      total: 0,
      attribute_values: [],
    }))

    const maxDeliveryDays = Math.max(...needsSelection.value.map(item => Number(item.delivery_days || 0)), 3)
    const expected = new Date()
    expected.setDate(expected.getDate() + maxDeliveryDays)

    const res = await api.post('/api/v1/purchase-orders', {
      order_number: 'Авто',
      order_date: new Date().toISOString(),
      expected_date: expected.toISOString(),
      supplier_id: supplierId,
      warehouse_id: warehouseId,
      currency: 'UAH',
      total_amount: 0,
      status: 'draft',
      notes: 'Створено з потреб виробництва',
      lines,
    })

    ElMessage.success('Замовлення створено з потреб виробництва')
    needsDrawerVisible.value = false
    await fetchOrders()
    router.push(`/purchases/orders/${res.data.id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Не вдалося створити замовлення')
  } finally {
    creatingFromNeeds.value = false
  }
}

const resetFilters = () => {
  Object.assign(filters, {
    search: '',
    status: '',
    supplierId: '',
    payment: '',
    priority: '',
    expectedDate: '',
    onlyOverdue: false,
    onlyNotReceived: false,
  })
  currentPage.value = 1
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
  if (command === 'delete') handleDelete(row)
  if (command === 'duplicate') router.push({ path: '/purchases/orders/new', query: { copy_from: row.id } })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити замовлення ${row.order_number}?`, 'Підтвердження', {
    confirmButtonText: 'Видалити',
    cancelButtonText: 'Скасувати',
    type: 'warning',
  }).then(async () => {
    await api.delete(`/api/v1/purchase-orders/${row.id}`)
    ElMessage.success('Видалено')
    fetchOrders()
  })
}

const bulkConfirm = async () => {
  for (const row of selected.value) {
    try { await api.put(`/api/v1/purchase-orders/${row.id}`, { status: 'confirmed' }) } catch {}
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
  if (row.status === 'done') return 'received'
  if (row.status === 'cancelled') return 'cancelled'
  if (row.received_quantity && Number(row.received_quantity) > 0) return 'partial_received'
  if (row.expected_date) return 'expected'
  return 'ordered'
}

const getStatusLabel = value => statusOptions.find(s => s.value === value)?.label || '—'

const getPaymentStatus = row => {
  const paid = Number(row.paid_amount || 0)
  const total = Number(row.total_amount || 0)
  if (total > 0 && paid >= total) return 'paid'
  if (paid > 0) return 'partial'
  return 'unpaid'
}

const getPaymentLabel = row => paymentOptions.find(p => p.value === getPaymentStatus(row))?.label || 'Не оплачено'

const getPriority = row => {
  if (getOverdueDays(row) > 0) return 'urgent'
  if (Number(row.total_amount || 0) > 50000) return 'high'
  if (normalizeStatus(row) === 'draft') return 'low'
  return 'medium'
}

const getPriorityLabel = value => priorityOptions.find(p => p.value === value)?.label || 'Середній'
const getCounterpartyName = id => suppliers.value.find(s => s.id === id)?.name || ''
const getCounterpartyPhone = id => suppliers.value.find(s => s.id === id)?.phone || ''
const getProductName = id => products.value.find(p => p.id === id)?.name || `Матеріал ${String(id || '').slice(0, 8)}`

const getMaterialPreview = row => {
  const names = (row.lines || []).map(line => getProductName(line.product_id)).filter(Boolean)
  return {
    first: names[0] || '—',
    more: Math.max(0, names.length - 1),
  }
}

const getRelatedDocs = row => {
  const docs = []
  if (row.production_order_number) docs.push(row.production_order_number)
  if (row.crm_order_number) docs.push(row.crm_order_number)
  if (row.source_order_number) docs.push(row.source_order_number)
  return docs
}

const getOverdueDays = row => {
  if (!row.expected_date || ['received', 'cancelled'].includes(normalizeStatus(row))) return 0
  const expected = new Date(row.expected_date)
  expected.setHours(0, 0, 0, 0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return Math.max(0, Math.floor((today - expected) / 86400000))
}

const sameDate = (left, right) => {
  if (!left || !right) return false
  return new Date(left).toISOString().slice(0, 10) === right
}

const formatDate = d => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatQty = value => new Intl.NumberFormat('uk-UA', { maximumFractionDigits: 2 }).format(Number(value || 0))
const formatCurrency = value => new Intl.NumberFormat('uk-UA', {
  style: 'currency',
  currency: 'UAH',
  maximumFractionDigits: 0,
}).format(Number(value || 0))

const handleKeydown = e => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return
  if (e.key === 'n' || e.key === 'N') { e.preventDefault(); handleCreate() }
  if (e.key === '/') { e.preventDefault(); searchInputRef.value?.focus() }
  if (e.key === 'Escape') { drawerVisible.value = false; needsDrawerVisible.value = false }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  fetchOrders()
})
onActivated(() => {
  if (orders.value.length) fetchOrders()
})
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.purchase-orders-page {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f4f6f9;
}

.po-top {
  flex-shrink: 0;
  padding: 16px 20px 12px;
  background: #f4f6f9;
}

.po-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.po-header h1 {
  margin: 0;
  color: #0f172a;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0;
}

.po-header p,
.needs-head p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.po-header-actions,
.po-empty div,
.needs-footer,
.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.po-primary-btn,
.po-secondary-btn,
.po-refresh-btn,
.po-reset-btn,
.po-bulk button {
  min-height: 34px;
  border: 0;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.po-primary-btn {
  background: #4338ca;
  color: #fff;
  box-shadow: 0 10px 22px rgba(67, 56, 202, .18);
}

.po-secondary-btn {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #334155;
}

.po-refresh-btn {
  width: 34px;
  padding: 0;
  justify-content: center;
  border: 1px solid #dbe4f0;
  background: #fff;
  color: #475569;
}

.po-reset-btn {
  background: transparent;
  color: #4338ca;
}

.po-kpis {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.po-kpi {
  min-height: 70px;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.po-kpi span {
  display: block;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.po-kpi strong {
  display: block;
  margin-top: 8px;
  color: #0f172a;
  font-size: 22px;
  font-weight: 900;
}

.po-kpi-blue strong { color: #2563eb; }
.po-kpi-rose strong { color: #e11d48; }
.po-kpi-amber strong { color: #d97706; }
.po-kpi-green strong { color: #059669; }

.po-filters {
  display: grid;
  grid-template-columns: minmax(280px, 1.6fr) repeat(4, minmax(130px, .75fr)) 150px auto auto 36px auto;
  align-items: center;
  gap: 8px;
}

.po-search,
.po-date {
  width: 100%;
}

.po-bulk {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eef2ff;
  color: #3730a3;
}

.po-bulk button {
  min-height: 28px;
  background: #4338ca;
  color: #fff;
}

.po-bulk .danger {
  background: #e11d48;
}

.po-bulk .ghost {
  background: #fff;
  color: #4338ca;
}

.po-table-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin: 0 20px 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.po-table {
  flex: 1;
  min-height: 0;
}

.po-table :deep(th.el-table__cell) {
  padding: 8px 10px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  background: #f8fafc !important;
  color: #64748b;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .04em;
  text-transform: uppercase;
}

.po-table :deep(td.el-table__cell) {
  padding: 8px 10px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  vertical-align: middle;
}

.po-table :deep(.cell) {
  line-height: 1.25;
}

.row-num,
.muted,
.po-table small {
  display: block;
  color: #94a3b8;
  font-size: 11px;
  line-height: 1.35;
}

.order-link {
  display: block;
  border: 0;
  padding: 0;
  background: transparent;
  color: #3730a3;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.supplier-name,
.amount {
  display: block;
  color: #0f172a;
  font-size: 13px;
}

.materials-cell span,
.related-cell span {
  display: block;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
}

.materials-cell small {
  color: #4338ca;
}

.related-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.related-cell span {
  width: fit-content;
  padding: 2px 6px;
  border-radius: 999px;
  background: #f1f5f9;
  font-size: 11px;
}

.po-badge,
.priority-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
}

.status-draft { background: #f1f5f9; color: #475569; }
.status-ordered { background: #dbeafe; color: #1d4ed8; }
.status-expected { background: #eef2ff; color: #4338ca; }
.status-partial_received { background: #fffbeb; color: #b45309; }
.status-received { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #ffe4e6; color: #be123c; }

.payment-unpaid { background: #fff1f2; color: #be123c; }
.payment-partial { background: #fef3c7; color: #b45309; }
.payment-paid { background: #dcfce7; color: #15803d; }

.priority-low { background: #f1f5f9; color: #475569; }
.priority-medium { background: #e0f2fe; color: #0369a1; }
.priority-high { background: #fef3c7; color: #b45309; }
.priority-urgent { background: #ffe4e6; color: #be123c; }

.expected-cell small {
  width: fit-content;
  margin: 4px auto 0;
  padding: 3px 7px;
  border-radius: 999px;
  background: #fff7ed;
  color: #c2410c;
  font-weight: 800;
}

.po-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.po-actions button {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.po-actions button:hover {
  background: #f1f5f9;
  color: #4338ca;
}

.po-empty {
  padding: 48px 16px;
  text-align: center;
}

.po-empty h3 {
  margin: 0 0 6px;
  color: #0f172a;
  font-size: 18px;
}

.po-empty p {
  margin: 0 0 16px;
  color: #64748b;
}

.po-pagination {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
}

.po-pagination > div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-size {
  width: 74px;
}

.drawer-meta {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 10px;
  background: #f8fafc;
}

.drawer-meta div,
.drawer-lines div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.drawer-meta span {
  color: #64748b;
}

.drawer-lines {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.drawer-lines div {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.drawer-footer,
.needs-footer {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}

.needs-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.needs-head h3 {
  margin: 0;
}

.needs-supplier {
  width: 260px;
}

.needs-table strong,
.needs-table small {
  display: block;
}

.deficit {
  color: #be123c;
}

.bulk-bar-enter-active,
.bulk-bar-leave-active {
  transition: all .2s ease;
}

.bulk-bar-enter-from,
.bulk-bar-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 1500px) {
  .po-kpis {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .po-kpi-amber {
    display: none;
  }
}

@media (max-width: 1200px) {
  .po-filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .po-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
