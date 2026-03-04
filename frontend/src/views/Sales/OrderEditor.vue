<template>
  <div class="page-container">
    <!-- === TOP BAR === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle size="small" @click="goBack" class="back-btn" />
        <div>
          <div class="header-title-row">
            <h2>{{ isEditMode ? 'Замовлення №' + form.order_number : 'Нове замовлення' }}</h2>
            <el-dropdown trigger="click" @command="handleStatusChange" v-if="isEditMode && form.status">
              <div class="creative-status-btn" :style="{ '--status-color': statusColor }">
                <span class="status-dot" :style="{ backgroundColor: statusColor, boxShadow: `0 0 8px ${statusColor}80` }"></span>
                <span class="status-text">{{ statusLabel }}</span>
                <el-icon class="status-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="status-dropdown">
                  <el-dropdown-item v-for="s in orderStatuses" :key="s.code" :command="s.code" :class="{ 'is-active': form.status === s.code }">
                    <span class="status-dot-small" :style="{ backgroundColor: s.color || '#94a3b8' }"></span>
                    {{ s.name }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="breadcrumb-row">Головна / Продажі / Замовлення{{ isEditMode ? ' / №' + form.order_number : '' }}</div>
        </div>
      </div>
      <div class="header-actions">
        <el-dropdown v-if="isEditMode" trigger="click" @command="handleCreateBasedOn">
          <el-button type="default">
            Створити на основі <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="invoice">Видаткова накладна</el-dropdown-item>
              <el-dropdown-item command="payment">Вхідний платіж</el-dropdown-item>
              <el-dropdown-item command="purchase_order">Замовлення постачальнику</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="goBack">Записати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrder" class="btn-submit">
          Провести
        </el-button>
      </div>
    </div>

    <!-- === COMPACT INFO CARD === -->
    <div class="order-details-card">
      <div class="info-section-label">Основна інформація</div>
      <el-form :model="form" label-position="top" class="details-form">
        <div class="compact-form-grid">
          <!-- Клієнт -->
          <div class="cf-item">
            <span class="cf-label">Клієнт <span class="req">*</span></span>
            <el-select v-model="form.counterparty_id" filterable placeholder="Оберіть клієнта" class="cf-input" @change="onClientChange">
              <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>
          <!-- Договір -->
          <div class="cf-item">
            <span class="cf-label">Договір</span>
            <el-input v-model="form.contract" placeholder="№ договору" class="cf-input" />
          </div>
          <!-- Склад -->
          <div class="cf-item">
            <span class="cf-label">Склад <span class="req">*</span></span>
            <el-select v-model="form.warehouse_id" placeholder="Оберіть склад" class="cf-input">
              <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <span>{{ w.name }}</span>
                  <el-tag v-if="w.is_default" size="small" type="success" effect="plain">Основний</el-tag>
                </div>
              </el-option>
            </el-select>
          </div>
          <!-- Дата створення -->
          <div class="cf-item">
            <span class="cf-label">Створено</span>
            <el-date-picker v-model="form.order_date" type="date" class="cf-input" value-format="YYYY-MM-DD" />
          </div>
          <!-- Дата відвантаження -->
          <div class="cf-item">
            <span class="cf-label">Відвантаження</span>
            <el-date-picker v-model="form.shipping_date" type="date" class="cf-input" value-format="YYYY-MM-DD" placeholder="Планова" />
          </div>
          <!-- Джерело ліда -->
          <div class="cf-item">
            <span class="cf-label">Джерело ліда</span>
            <el-select v-model="form.lead_source" placeholder="Не вказано" class="cf-input" clearable>
              <el-option v-for="ls in leadSources" :key="ls.code" :label="ls.name" :value="ls.code" />
            </el-select>
          </div>
        </div>
      </el-form>
    </div>

    <!-- === PRODUCT LINES === -->
    <div class="lines-section-card" v-loading="loading">
      <div class="lines-header">
        <div class="lines-header-left">
          <el-button type="primary" :icon="Plus" @click="addLine" size="small" class="btn-add-line">Додати позицію</el-button>
        </div>
        <div class="lines-header-right">
          <span class="lines-title">Товари та послуги</span>
          <el-popover placement="bottom-end" :width="200" trigger="click">
            <template #reference>
              <el-button :icon="Setting" circle size="small" class="col-settings-btn" title="Налаштування колонок" />
            </template>
            <div class="col-toggle-list">
              <div class="col-toggle-title">Показати колонки</div>
              <el-checkbox v-model="visibleCols.characteristic">Характеристика</el-checkbox>
              <el-checkbox v-model="visibleCols.discount">Знижка</el-checkbox>
            </div>
          </el-popover>
        </div>
      </div>

      <el-table :data="form.lines" border style="width: 100%" class="lines-table">
        <el-table-column type="index" label="№" width="44" align="center" />
        <el-table-column label="Товар" min-width="180">
          <template #default="scope">
            <el-select
              v-model="scope.row.product_id"
              filterable
              placeholder="Пошук товару..."
              style="width:100%"
              @change="(val) => handleProductChange(val, scope.row)"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column v-if="visibleCols.characteristic" label="Характеристика" min-width="130">
          <template #default="scope">
            <div class="characteristic-cell-wrapper">
              <div
                class="characteristic-display-box"
                :class="{ 'has-value': scope.row.variant_id || scope.row._virtual_label }"
                @click="openVariantSelector(scope.row)"
              >
                <div v-if="scope.row.variant_id" class="selection-content">
                  <span class="selection-text">{{ getVariantLabelByLine(scope.row) }}</span>
                </div>
                <div v-else-if="scope.row._virtual_label" class="selection-content">
                  <span class="selection-text virtual">{{ scope.row._virtual_label }}</span>
                </div>
                <div v-else class="selection-placeholder">Оберіть...</div>
              </div>
              <el-button
                v-if="scope.row.product_id"
                :icon="Setting"
                circle
                size="small"
                class="config-btn"
                @click="openVariantSelector(scope.row)"
                title="Конфігуратор характеристик"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Кількість" width="120">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.quantity" :min="0.001" @change="updateLineTotal(scope.row)" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Ціна" width="120">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" :precision="2" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column v-if="visibleCols.discount" label="Знижка" width="80" align="center">
          <template #default="scope">
            <span class="text-sm" style="color:#94a3b8">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="110" align="right">
          <template #default="scope">
            <span class="line-total">{{ formatCurrency(scope.row.total) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Дія" width="50" align="center" fixed="right">
          <template #default="scope">
            <el-button type="danger" :icon="Delete" link size="small" @click="removeLine(scope.$index)" />
          </template>
        </el-table-column>
      </el-table>

      <div v-if="form.lines.length === 0" class="empty-lines">
        <el-empty description="Додайте товари до замовлення" :image-size="60">
          <el-button type="primary" :icon="Plus" @click="addLine">Додати позицію</el-button>
        </el-empty>
      </div>
    </div>

    <!-- === STICKY FOOTER === -->
    <div class="order-footer">
      <div class="footer-left">
        <div class="footer-comment-label">Коментар до замовлення</div>
        <el-input
          v-model="form.comment"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 2 }"
          placeholder="Внутрішній коментар або уточнення..."
          class="comment-input"
        />
      </div>
      <div class="footer-right">
        <div class="footer-total-label">РАЗОМ ДО СПЛАТИ</div>
        <div class="footer-total-amount">{{ formatCurrency(totalAmount) }}</div>
        <div v-if="discountAmount > 0" class="footer-discount">Знижка: -{{ formatCurrency(discountAmount) }}</div>
        <div class="discount-inline">
          <span class="s-label">Знижка %:</span>
          <el-input-number
            v-model="form.discount_percent"
            :min="0" :max="100" :precision="1" :step="1"
            controls-position="right" size="small"
            style="width: 90px"
          />
        </div>
      </div>
    </div>

    <!-- === DIALOG: Nomenclature Selection === -->
    <el-dialog
      v-model="nomenclatureDialogVisible"
      title="Вибір номенклатури"
      width="800px"
      destroy-on-close
    >
      <el-input
        v-model="nomenclatureSearch"
        placeholder="Пошук за назвою або SKU..."
        :prefix-icon="Search"
        clearable
        style="margin-bottom: 16px"
      />
      <el-table
        :data="filteredProducts"
        border
        height="400px"
        highlight-current-row
        @current-change="onDialogProductSelect"
      >
        <el-table-column property="sku" label="SKU" width="120" />
        <el-table-column property="name" label="Назва" min-width="250" />
        <el-table-column property="category" label="Категорія" width="150" />
        <el-table-column label="Ціна" width="120" align="right">
          <template #default="scope">
            {{ formatShort(scope.row.price) }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="nomenclatureDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" :disabled="!selectedDialogProduct" @click="confirmDialogSelection">
          Вибрати
        </el-button>
      </template>
    </el-dialog>

    <!-- === DIALOG: Interactive Variant Selector === -->
    <VariantSelectorDialog
      v-model="variantSelectorVisible"
      :product="selectedProductForSelector"
      @select="onVariantSelected"
      @clear="clearVirtualVariant(activeLineForSelector)"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Search, Setting, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import VariantSelectorDialog from './VariantSelectorDialog.vue'

const route = useRoute()
const router = useRouter()

const handleCreateBasedOn = (command) => {
  const orderId = route.params.id;
  if (!orderId) return;

  if (command === 'invoice') {
    // router.push({ path: '/sales/invoices/new', query: { based_on: orderId } })
    ElMessage.info('Створення Видаткової накладної (в розробці)')
  } else if (command === 'payment') {
    // router.push({ path: '/finance/payments/new', query: { based_on: orderId, type: 'incoming' } })
    ElMessage.info('Створення Вхідного платежу (в розробці)')
  } else if (command === 'purchase_order') {
    // router.push({ path: '/purchases/orders/new', query: { based_on: orderId } })
    ElMessage.info('Створення Замовлення постачальнику (в розробці)')
  }
}


// State
const loading = ref(false)
const submitting = ref(false)
const isEditMode = computed(() => !!route.params.id)

const form = reactive({
  order_number: 'Авто',
  order_date: new Date().toISOString().split('T')[0],
  shipping_date: null,
  counterparty_id: '',
  warehouse_id: '',
  contract: '',
  comment: '',
  discount_percent: 0,
  status: 'draft',
  lead_source: null,
  lines: []
})

const orderStatuses = ref([])
const leadSources = ref([])

// Column Visibility
const visibleCols = reactive({
  characteristic: true,
  discount: true
})

// Options
const customers = ref([])
const warehouses = ref([])
const products = ref([])

// Nomenclature Dialog State
const nomenclatureDialogVisible = ref(false)
const nomenclatureSearch = ref('')
const activeLineIndex = ref(-1)
const selectedDialogProduct = ref(null)

// Variant Selector State
const variantSelectorVisible = ref(false)
const selectedProductForSelector = ref(null)
const activeLineForSelector = ref(null)

// Computed
const subtotal = computed(() => {
  return form.lines.reduce((acc, line) => acc + (line.total || 0), 0)
})

const discountAmount = computed(() => {
  return subtotal.value * (form.discount_percent || 0) / 100
})

const totalAmount = computed(() => {
  return subtotal.value - discountAmount.value
})

const filteredProducts = computed(() => {
  if (!nomenclatureSearch.value) return products.value
  const s = nomenclatureSearch.value.toLowerCase()
  return products.value.filter(p =>
    p.name.toLowerCase().includes(s) ||
    p.sku.toLowerCase().includes(s)
  )
})

const statusType = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  const color = status?.color || 'info'
  const validTypes = ['primary', 'success', 'info', 'warning', 'danger']
  return validTypes.includes(color) ? color : 'info'
})

const statusColor = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  const c = status?.color || 'gray'
  // Map our basic element colors to actual hex codes for dynamic display if they used standard names
  const colorMap = {
    gray: '#64748b',
    info: '#64748b',
    blue: '#3b82f6',
    primary: '#3b82f6',
    green: '#10b981',
    success: '#10b981',
    orange: '#f59e0b',
    warning: '#f59e0b',
    red: '#ef4444',
    danger: '#ef4444'
  }
  return status?.color || 'gray' // Return the raw color name/hex
})

const statusLabel = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  return status?.name || form.status
})

const goBack = () => router.push('/sales/orders')

const onClientChange = (clientId) => {
  const client = customers.value.find(c => c.id === clientId)
  if (client && client.default_contract) {
    form.contract = client.default_contract
  }
}

const addLine = () => {
  form.lines.push({
    product_id: '',
    variant_id: null,
    quantity: 1,
    price: 0,
    total: 0
  })
}

const removeLine = (index) => {
  form.lines.splice(index, 1)
}

const updateLineTotal = (line) => {
  line.total = parseFloat((line.quantity * line.price).toFixed(2))
}

const handleProductChange = (productId, line) => {
  const product = products.value.find(p => p.id === productId)
  if (product) {
    line.variant_id = null
    const primaryVar = product.variants?.find(v => v.is_primary) || product.variants?.[0]
    if (primaryVar && primaryVar.values?.length > 0) {
      line.variant_id = primaryVar.id
      line.price = primaryVar.price_override || product.price
    } else {
      line.price = product.price
    }
    updateLineTotal(line)
  }
}

// Nomenclature Dialog Methods
const openNomenclatureDialog = (index) => {
  activeLineIndex.value = index
  nomenclatureSearch.value = ''
  selectedDialogProduct.value = null
  nomenclatureDialogVisible.value = true
}

const onDialogProductSelect = (val) => {
  selectedDialogProduct.value = val
}

const confirmDialogSelection = () => {
  if (selectedDialogProduct.value && activeLineIndex.value > -1) {
    const line = form.lines[activeLineIndex.value]
    line.product_id = selectedDialogProduct.value.id
    handleProductChange(line.product_id, line)
    nomenclatureDialogVisible.value = false
  }
}

// Variant Selector Methods
const openVariantSelector = (line) => {
  const product = products.value.find(p => p.id === line.product_id)
  if (!product) return
  activeLineForSelector.value = line
  selectedProductForSelector.value = product
  variantSelectorVisible.value = true
}

const onVariantSelected = (variant) => {
  if (activeLineForSelector.value) {
    if (variant.id) {
      activeLineForSelector.value.variant_id = variant.id
      activeLineForSelector.value._virtual_label = null
      handleVariantChange(variant.id, activeLineForSelector.value)
    } else {
      activeLineForSelector.value.variant_id = null
      activeLineForSelector.value._virtual_label = getVariantLabel(variant)
      activeLineForSelector.value._virtual_values = variant.values
      const prod = products.value.find(p => p.id === activeLineForSelector.value.product_id)
      activeLineForSelector.value.price = prod?.price || 0
      updateLineTotal(activeLineForSelector.value)
    }
  }
}

const clearVirtualVariant = (line) => {
  line._virtual_label = null
  line._virtual_values = null
}

const handleVariantChange = (variantId, line) => {
  const product = products.value.find(p => p.id === line.product_id)
  if (!product) return
  if (variantId) {
    const variant = product.variants?.find(v => v.id === variantId)
    if (variant) {
      line.price = variant.price_override || product.price
    }
  } else {
    line.price = product.price
  }
  updateLineTotal(line)
}

const getProductVariants = (productId) => {
  const product = products.value.find(p => p.id === productId)
  return product?.variants || []
}

const getVariantLabel = (variant) => {
  if (!variant) return ''
  if (!variant.values || variant.values.length === 0) return variant.sku || ''
  return variant.values.map(v => {
    const attrName = v.attribute?.name || ''
    const valText = v.option?.value || v.text_value || ''
    return attrName ? `${attrName}: ${valText}` : valText
  }).filter(Boolean).join(', ')
}

const getVariantLabelByLine = (line) => {
  if (!line.variant_id) return ''
  const variants = getProductVariants(line.product_id)
  const variant = variants.find(v => v.id === line.variant_id)
  return getVariantLabel(variant)
}

const fetchData = async () => {
  loading.value = true
  try {
    const [custRes, whRes, prodRes, statusRes, leadRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_customer: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products'),
      api.get('/api/v1/dictionaries/ORDER_STATUS'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] }))
    ])
    customers.value = custRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    orderStatuses.value = statusRes.data
    leadSources.value = leadRes.data

    if (isEditMode.value) {
      const orderRes = await api.get(`/api/v1/orders/${route.params.id}`)
      const data = orderRes.data
      data.discount_percent = Number(data.discount_percent || 0)
      if (data.lines) {
        data.lines.forEach(line => {
          line.quantity = Number(line.quantity || 0)
          line.price = Number(line.price || 0)
          line.total = Number(line.total || 0)
        })
      }
      Object.assign(form, data)
    } else {
      const defaultWH = warehouses.value.find(w => w.is_default)
      if (defaultWH) {
        form.warehouse_id = defaultWH.id
      }
      addLine()
    }
  } catch (e) {
    console.error('Data loading error:', e)
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const handleStatusChange = async (command) => {
  if (form.status === command) return
  const oldStatus = form.status
  form.status = command
  try {
    const res = await api.put(`/api/v1/orders/${route.params.id}`, form)
    ElMessage.success('Статус оновлено')
  } catch (err) {
    form.status = oldStatus // Revert on failure
    console.error('Failed to change status:', err)
    ElMessage.error(err.response?.data?.detail || 'Помилка при зміні статусу')
  }
}

const saveOrder = async () => {
  if (!form.counterparty_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля та додайте товари")
    return
  }

  const payload = {
    ...form,
    total_amount: totalAmount.value,
    shipping_date: form.shipping_date || null,
    contract: form.contract || null,
    comment: form.comment || null,
    discount_percent: form.discount_percent || 0
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/orders/${route.params.id}`, payload)
      ElMessage.success('Замовлення оновлено')
    } else {
      await api.post('/api/v1/orders', payload)
      ElMessage.success('Замовлення створено')
    }
    goBack()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)
const formatShort = (val) => new Intl.NumberFormat('uk-UA').format(val) + ' грн'

onMounted(fetchData)
</script>

<style scoped>
/* ===== PAGE CONTAINER ===== */
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: #f4f5f9;
}

/* ===== TOP BAR ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 24px;
  background: white;
  border-bottom: 1px solid #f0f0f7;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.3px;
}

.status-tag { vertical-align: middle; }

.breadcrumb-row {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
  margin-top: 1px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-submit {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 8px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(99,102,241,0.3);
}

.back-btn { flex-shrink: 0; }

/* === CREATIVE STATUS BUTTON === */
.creative-status-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  /* Dynamic colors injected via CSS custom property --status-color */
  color: var(--status-color, #475569);
  background: color-mix(in srgb, var(--status-color) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--status-color) 30%, transparent);
}
.creative-status-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-icon {
  font-size: 12px;
  opacity: 0.7;
}

/* Dropdown items */
.status-dropdown .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-weight: 500;
}
.status-dropdown .el-dropdown-menu__item.is-active {
  background-color: #f8fafc;
  font-weight: 700;
}
.status-dot-small {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

/* ===== MODERN INFO CARD ===== */
.order-details-card {
  margin: 16px 24px 0;
  background: #fff;
  padding: 24px 28px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  flex-shrink: 0;
}

.info-section-label {
  display: none;
}

.compact-form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px 24px;
}

.cf-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cf-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  line-height: 1.2;
}

.cf-input {
  width: 100%;
}
.cf-input :deep(.el-input__wrapper),
.cf-input :deep(.el-select__wrapper) {
  min-height: 38px !important;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #cbd5e1 inset;
  background-color: #f8fafc;
  padding: 0 12px;
}
.cf-input :deep(.el-input__inner) {
  font-size: 14px;
  height: 38px;
  line-height: 38px;
  color: #1e293b;
}
.cf-input :deep(.el-select__wrapper) {
  line-height: 38px;
}
.details-form :deep(.el-input__wrapper),
.details-form :deep(.el-select__wrapper),
.details-form :deep(.el-date-editor.el-input__wrapper) {
  box-shadow: none !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px !important;
  background-color: #f8fafc !important;
  transition: all 0.2s ease;
  min-height: 38px;
  padding: 0 12px;
}

.details-form :deep(.el-input__wrapper:hover),
.details-form :deep(.el-select__wrapper:hover) {
  border-color: #c7d2fe !important;
}

.details-form :deep(.el-input__wrapper.is-focus),
.details-form :deep(.el-select__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

.details-form :deep(.el-form-item) { margin-bottom: 0; }

.req { color: #ef4444; margin-left: 2px; }

/* ===== LINES SECTION ===== */
.lines-section-card {
  margin: 20px 24px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
  flex-shrink: 0;
}

.lines-header-left,
.lines-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lines-title {
  font-size: 15px;
  font-weight: 700;
  color: #1e1b4b;
}

.btn-add-line {
  background: #6366f1;
  border-color: #6366f1;
  border-radius: 7px;
  font-weight: 700;
}

.col-settings-btn { color: #94a3b8; border-color: #e2e8f0; }
.col-settings-btn:hover { color: #6366f1; border-color: #6366f1; background: #f5f3ff; }

.col-toggle-list { display: flex; flex-direction: column; gap: 8px; }
.col-toggle-title {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ===== UNIFORM TABLE HEADERS ===== */
.lines-table :deep(th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #e2e8f0 !important;
  padding: 12px 0 !important;
}

.lines-table :deep(td.el-table__cell) {
  border-bottom: 1px solid #f1f5f9 !important;
  padding: 14px 12px !important;
}

.lines-table :deep(.el-input__wrapper),
.lines-table :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 6px !important;
  background-color: #fff !important;
  min-height: 36px;
}
.lines-table :deep(.el-input__wrapper.is-focus),
.lines-table :deep(.el-select__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.12) !important;
}

.line-total {
  font-size: 13px;
  font-weight: 700;
  color: #1e1b4b;
}

.empty-lines {
  padding: 24px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== CHARACTERISTIC COLUMN ===== */
.characteristic-cell-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.characteristic-display-box {
  flex: 1;
  min-height: 28px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  padding: 3px 10px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.15s ease;
  overflow: hidden;
}
.characteristic-display-box:hover { border-color: #c7d2fe; background: #f5f3ff; }
.characteristic-display-box.has-value { border-color: #6366f1; background: white; }

.selection-content { width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.selection-text { font-size: 12px; color: #374151; font-weight: 500; }
.selection-text.virtual { color: #059669; }
.selection-placeholder { font-size: 12px; color: #94a3b8; }

.config-btn { flex-shrink: 0; transition: transform 0.2s; }
.config-btn:hover { transform: rotate(30deg); }

/* ===== STICKY FOOTER ===== */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
  flex-shrink: 0;
  gap: 20px;
}

.footer-left {
  flex: 1;
  max-width: 480px;
}

.footer-comment-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 6px;
}

.comment-input :deep(.el-textarea__inner) {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  min-height: 38px !important;
  max-height: 60px;
  resize: none;
  font-size: 13px;
}

.footer-right {
  text-align: right;
  flex-shrink: 0;
}

.footer-total-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 3px;
}

.footer-total-amount {
  font-size: 28px;
  font-weight: 800;
  color: #1e1b4b;
  line-height: 1;
  margin-bottom: 4px;
}

.footer-discount {
  font-size: 12px;
  color: #ef4444;
  font-weight: 600;
  margin-bottom: 4px;
}

.discount-inline {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

.s-label { font-size: 12px; color: #64748b; }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .compact-form-grid { grid-template-columns: repeat(2, 1fr); }
  .order-footer { flex-direction: column; align-items: flex-start; gap: 12px; }
  .footer-right { text-align: left; width: 100%; }
  .discount-inline { justify-content: flex-start; }
}

@media (max-width: 480px) {
  .compact-form-grid { grid-template-columns: 1fr; }
  .footer-total-amount { font-size: 22px; }
}
</style>
