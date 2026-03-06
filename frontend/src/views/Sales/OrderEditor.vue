<template>
  <div class="erp-page-container">
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button type="warning" size="small" :loading="submitting" @click="saveOrder" class="erp-btn-primary">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveOrder" class="erp-btn">Записати</el-button>
        <el-button size="small" @click="saveOrder" class="erp-btn">Провести</el-button>
        <el-dropdown v-if="isEditMode" trigger="click" @command="handleCreateBasedOn" size="small">
          <el-button size="small" class="erp-btn">
            Створити на підставі <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="invoice">Видаткова накладна</el-dropdown-item>
              <el-dropdown-item command="payment">Вхідний платіж</el-dropdown-item>
              <el-dropdown-item command="purchase_order">Замовлення постачальнику</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <div class="erp-doc-info">
            <span class="erp-doc-title">{{ isEditMode ? 'Замовлення покупця ' + form.order_number : 'Замовлення покупця (створення)' }}</span>
            <el-button v-if="isEditMode" size="small" class="erp-btn-icon" :icon="Timer" title="Історія змін" @click="showAuditLog" style="margin-left: 12px;" />
        </div>
      </div>
    </div>

    <div class="erp-header-fields">
      <div class="erp-field-row">
        <div class="erp-field">
          <span class="erp-label">Стан:</span>
          <el-select v-model="form.status" size="small" class="erp-input-wrapper status-select" :class="'status-' + form.status">
            <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code" />
          </el-select>
        </div>
        <div class="erp-field">
          <span class="erp-label">Номер:</span>
          <el-input v-model="form.order_number" size="small" class="erp-input-wrapper" disabled />
        </div>
        <div class="erp-field">
          <span class="erp-label">від:</span>
          <el-date-picker v-model="form.order_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" />
        </div>
        <div class="erp-field-links">
           <a href="javascript:void(0)" class="erp-link">Підписи та інші реквізити</a>
        </div>
      </div>
      <div class="erp-field-row">
        <div class="erp-field client-field">
          <span class="erp-label req">Покупець:</span>
          <el-select v-model="form.counterparty_id" filterable size="small" class="erp-input-wrapper" @change="onClientChange">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
      </div>
      <div class="erp-field-row">
        <div class="erp-field">
          <span class="erp-label">Відвантаження:</span>
          <el-date-picker v-model="form.shipping_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" placeholder="Планова" />
        </div>
        <div class="erp-field">
           <a href="javascript:void(0)" class="erp-link">+ Калькуляція замовлення</a>
        </div>
      </div>
    </div>

    <div class="erp-tabs-section">
      <div class="erp-tabs">
        <div class="erp-tab active">Товари, послуги</div>
        <div class="erp-tab">Доставка</div>
        <div class="erp-tab">Додатково</div>
      </div>
      
      <div class="erp-table-toolbar">
        <el-button size="small" class="erp-btn" @click="addLine">Додати</el-button>
        <el-button size="small" class="erp-btn-icon" title="Вгору">↑</el-button>
        <el-button size="small" class="erp-btn-icon" title="Вниз">↓</el-button>
        <el-button size="small" class="erp-btn" :icon="Search" @click="openNomenclatureDialog(form.lines.length - 1 || 0)">Підібрати</el-button>
        <el-button size="small" class="erp-btn-icon" :icon="Setting" title="Налаштування колонок"></el-button>
      </div>

      <div class="erp-field-row erp-warehouse-row">
        <div class="erp-field">
          <span class="erp-label">Склад (резерв): <span class="req">*</span></span>
          <el-select v-model="form.warehouse_id" size="small" class="erp-input-wrapper warehouse-select">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </div>
      </div>
    </div>

    <div class="erp-table-wrapper" v-loading="loading">
      <el-table :data="form.lines" border size="small" class="erp-dense-table" height="100%">
        <el-table-column type="index" label="N" width="40" align="center" />
        <el-table-column label="Номенклатура" min-width="200">
          <template #default="scope">
            <el-select
              v-model="scope.row.product_id"
              filterable
              size="small"
              placeholder=""
              class="erp-cell-input"
              @change="(val) => handleProductChange(val, scope.row)"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Характеристика" min-width="150" v-if="visibleCols.characteristic">
          <template #default="scope">
            <div class="erp-cell-trigger" @click="openVariantSelector(scope.row)">
              <span class="selection-text" v-if="scope.row.variant_id">{{ getVariantLabelByLine(scope.row) }}</span>
              <span class="selection-text virtual" v-else-if="scope.row._virtual_label">{{ scope.row._virtual_label }}</span>
              <span class="placeholder" v-else>...</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Кількість" width="90">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.quantity" :min="0.001" :step="0.001" :precision="3" :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="В резерв" width="80" align="center">
          <template #default="scope">
            <el-checkbox />
          </template>
        </el-table-column>
        <el-table-column label="Ціна" width="100">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.price" :min="0" :step="0.01" :precision="2" :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="100">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.total" :min="0" :step="0.01" :precision="2" :controls="false" @change="updateLinePrice(scope.row)" class="erp-cell-input num sum-input" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="Специфікація" min-width="100">
           <template #default>
              <span class="placeholder">...</span>
           </template>
        </el-table-column>
        <el-table-column label="" width="40" align="center" fixed="right">
          <template #default="scope">
            <el-button type="danger" :icon="Delete" link size="small" @click="removeLine(scope.$index)" style="padding:0;height:auto;" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="erp-footer">
      <div class="erp-footer-left">
        <el-input
          v-model="form.comment"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 3 }"
          placeholder="Коментар..."
          class="erp-comment-input"
        />
      </div>
      <div class="erp-footer-right">
        <div class="erp-total-row">
            <span class="erp-total-label">Знижка руч., %:</span>
            <el-input-number v-model="form.discount_percent" :min="0" :max="100" :precision="1" :controls="false" size="small" class="erp-total-input" />
            <span class="erp-total-label ml-4">ПДВ:</span>
            <span class="erp-total-value">0,00</span>
        </div>
        <div class="erp-total-row">
            <span class="erp-total-label">Знижка руч., Σ:</span>
            <el-input-number :model-value="discountAmount" disabled :controls="false" size="small" class="erp-total-input" />
            <span class="erp-total-label ml-4">Всього:</span>
            <span class="erp-total-value sum">{{ formatCurrency(totalAmount) }}</span>
        </div>
      </div>
    </div>

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
        :data="filteredProducts" border height="400px" highlight-current-row @current-change="onDialogProductSelect"
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

    <VariantSelectorDialog
      v-model="variantSelectorVisible"
      :product="selectedProductForSelector"
      @select="onVariantSelected"
      @clear="clearVirtualVariant(activeLineForSelector)"
    />

    <AuditLogViewer
      v-if="isEditMode"
      v-model="auditLogVisible"
      entity-type="order"
      :entity-id="route.params.id"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Search, Setting, ArrowDown, Timer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import VariantSelectorDialog from './VariantSelectorDialog.vue'
import AuditLogViewer from '@/components/AuditLogViewer.vue'

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

// Audit Log State
const auditLogVisible = ref(false)
const showAuditLog = () => {
  auditLogVisible.value = true
}

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

const updateLinePrice = (line) => {
  if (line.quantity > 0) {
    line.price = parseFloat((line.total / line.quantity).toFixed(2))
  }
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
.erp-page-container {
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
  background-color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif;
}
.erp-toolbar {
  display: flex; align-items: center; padding: 6px 12px;
  background-color: #fcfcfc; border-bottom: 1px solid #dcdfe6; flex-shrink: 0;
}
.erp-toolbar-left { display: flex; align-items: center; gap: 8px; }
.erp-btn, .erp-btn-icon, .erp-btn-primary {
  border-radius: 2px !important; font-size: 13px !important; height: 28px !important;
  padding: 0 12px !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; color: #303133 !important;
}
.erp-btn:hover, .erp-btn-icon:hover { background-color: #f5f7fa !important; border-color: #c0c4cc !important; }
.erp-btn-primary {
  background-color: #eef2ff !important; border-color: #6366f1 !important;
  color: #4338ca !important; font-weight: 600 !important;
}
.erp-btn-primary:hover { background-color: #e0e7ff !important; }
.erp-btn-icon { padding: 0 8px !important; }
.erp-doc-info { margin-left: 16px; display: flex; align-items: center; }
.erp-doc-title { font-size: 14px; font-weight: 600; color: #303133; }
.erp-header-fields {
  background-color: #f6f7f9; padding: 12px 16px 8px 16px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px;
}
.erp-field-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.erp-field { display: flex; align-items: center; }
.erp-label {
  font-size: 13px; color: #606266; width: 105px; text-align: left; padding-right: 8px;
}
.erp-label.req { color: #f56c6c; text-decoration: underline dotted #fbc4c4; text-underline-offset: 3px; }
.erp-input-wrapper { width: 160px; }
.client-field .erp-input-wrapper { width: 320px; }
.erp-header-fields :deep(.el-input__wrapper), .erp-header-fields :deep(.el-select__wrapper) {
  border-radius: 2px !important; box-shadow: none !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; min-height: 26px !important; height: 26px !important; padding: 0 8px !important;
}
.erp-header-fields :deep(.el-input__inner) {
  height: 24px !important; line-height: 24px !important; font-size: 13px !important; color: #303133 !important;
}
.erp-header-fields :deep(.el-select__wrapper) { min-height: 26px !important; }
.erp-header-fields :deep(.el-input__wrapper:focus-within), .erp-header-fields :deep(.el-select__wrapper.is-focus) {
  border-color: #c0c4cc !important; box-shadow: inset 0 0 2px rgba(0,0,0,0.1) !important;
}
.erp-link { font-size: 13px; color: #409eff; text-decoration: none; margin-left: 8px; }
.erp-link:hover { text-decoration: underline; }
.erp-tabs-section {
  display: flex; flex-direction: column; background-color: #f6f7f9; padding: 0 16px; flex-shrink: 0;
}
.erp-tabs { display: flex; border-bottom: 2px solid #6366f1; margin-bottom: 8px; margin-top: 4px; }
.erp-tab {
  padding: 6px 16px; font-size: 13px; cursor: pointer; color: #606266;
  background-color: #e4e7ed; border: 1px solid #dcdfe6; border-bottom: none;
  border-radius: 4px 4px 0 0; margin-right: 4px;
}
.erp-tab.active { background-color: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 600; }
.erp-table-toolbar { display: flex; gap: 6px; margin-bottom: 6px; }
.erp-warehouse-row { margin-bottom: 6px; }
.warehouse-select { width: 250px; }
.erp-table-wrapper { flex: 1; padding: 0 16px; overflow: hidden; margin-bottom: 12px; }
.erp-dense-table { width: 100%; border: 1px solid #dcdfe6 !important; }
.erp-dense-table :deep(th.el-table__cell) {
  background-color: #f5f7fa !important; color: #606266; font-size: 12px;
  font-weight: 600; padding: 4px 0 !important; border-bottom: 1px solid #dcdfe6 !important; border-right: 1px solid #dcdfe6 !important;
}
.erp-dense-table :deep(td.el-table__cell) {
  padding: 0 !important; border-bottom: 1px solid #ebeef5 !important; border-right: 1px solid #ebeef5 !important;
}
.erp-dense-table :deep(.cell) { padding: 0 6px !important; line-height: 24px !important; }
.erp-cell-input { width: 100%; }
.erp-cell-input :deep(.el-input__wrapper), .erp-cell-input :deep(.el-select__wrapper) {
  box-shadow: none !important; border: 1px solid transparent !important; background-color: transparent !important;
  padding: 0 4px !important; border-radius: 2px !important; min-height: 24px !important; height: 24px !important;
  transition: all 0.2s;
}
.erp-cell-input :deep(.el-input__wrapper:focus-within), .erp-cell-input :deep(.el-input__wrapper:hover) {
  border-color: #dcdfe6 !important; background-color: #fff !important;
}
.erp-cell-input :deep(.el-input__inner) { font-size: 13px !important; height: 22px !important; line-height: 22px !important; }
.erp-cell-input.num :deep(.el-input__inner) { text-align: right !important; }
.erp-cell-trigger { width: 100%; height: 24px; display: flex; align-items: center; font-size: 13px; cursor: pointer; }
.erp-cell-text { font-size: 13px; line-height: 24px; }
.virtual { color: #67c23a; }
.placeholder { color: #c0c4cc; }
.erp-footer {
  display: flex; justify-content: space-between; padding: 12px 16px;
  background-color: #f6f7f9; border-top: 1px solid #dcdfe6; flex-shrink: 0; gap: 20px;
}
.erp-footer-left { flex: 1; max-width: 500px; }
.erp-comment-input :deep(.el-textarea__inner) {
  border-radius: 2px; border: 1px solid #dcdfe6; font-size: 13px; padding: 6px;
}
.erp-footer-right { display: flex; flex-direction: column; gap: 6px; width: 320px; }
.erp-total-row { display: flex; align-items: center; justify-content: flex-end; }
.erp-total-label { font-size: 13px; color: #606266; width: 110px; text-align: right; margin-right: 8px; }
.ml-4 { margin-left: 16px; width: 40px; }
.erp-total-input { width: 80px; }
.erp-total-input :deep(.el-input__wrapper) {
  border-radius: 2px !important; box-shadow: none !important; border: 1px solid #dcdfe6 !important;
  height: 24px !important; min-height: 24px !important; padding: 0 6px !important;
}
.erp-total-input :deep(.el-input__inner) { font-size: 13px !important; height: 24px !important; text-align: right; }
.erp-total-value { width: 90px; text-align: right; font-size: 13px; font-weight: 600; color: #303133; }
.erp-total-value.sum { font-weight: 700; font-size: 15px; }
.req { color: #f56c6c; }
</style>