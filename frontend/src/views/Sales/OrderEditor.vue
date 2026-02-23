<template>
  <div class="page-container">
    <!-- === TOP BAR: Title + Save === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? 'Замовлення №' + form.order_number : 'Нове замовлення' }}</h2>
        <el-tag v-if="isEditMode && form.status" :type="statusType" size="small">{{ statusLabel }}</el-tag>
      </div>
      <div class="header-actions flex gap-2">
        <el-button @click="goBack" class="hover:bg-gray-100 transition-colors">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrder" class="shadow-md hover:shadow-lg transition-transform active:scale-95">
          Зберегти замовлення
        </el-button>
      </div>
    </div>

    <!-- === STICKY: Order details panel === -->
    <!-- === MODERN HEADER: Two-column card layout === -->
    <div class="order-details-card">
      <el-form :model="form" label-position="top" size="default" class="details-form">
        <el-row :gutter="40">
          <!-- Left Column: Customer Info -->
          <el-col :xs="24" :md="12" class="column-separator">
            <h3 class="section-title flex items-center gap-2">
              <el-icon><User /></el-icon>
              Інформація про клієнта
            </h3>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item required>
                  <template #label>
                    <span class="custom-label">Клієнт <span class="req">*</span></span>
                  </template>
                  <el-select v-model="form.counterparty_id" filterable placeholder="Оберіть клієнта" style="width: 100%" @change="onClientChange">
                    <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <template #label>
                    <span class="custom-label">Договір</span>
                  </template>
                  <el-input v-model="form.contract" placeholder="№ договору" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>

          <!-- Right Column: System/Order Info -->
          <el-col :xs="24" :md="12">
            <h3 class="section-title flex items-center gap-2">
              <el-icon><Document /></el-icon>
              Дані замовлення
            </h3>
            <el-row :gutter="20">
              <el-col :sm="12">
                <el-form-item>
                  <template #label>
                    <span class="custom-label">Номер</span>
                  </template>
                  <el-input v-model="form.order_number" placeholder="Автоматично" />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item required>
                  <template #label>
                    <span class="custom-label">Склад <span class="req">*</span></span>
                  </template>
                  <el-select v-model="form.warehouse_id" placeholder="Оберіть склад" style="width: 100%">
                    <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id">
                       <div style="display: flex; justify-content: space-between; align-items: center;">
                         <span>{{ w.name }}</span>
                         <el-tag v-if="w.is_default" size="small" type="success" effect="plain">Основний</el-tag>
                       </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item>
                  <template #label>
                    <span class="custom-label">Дата створення</span>
                  </template>
                  <el-date-picker v-model="form.order_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item>
                  <template #label>
                    <span class="custom-label">Дата відвантаження</span>
                  </template>
                  <el-date-picker v-model="form.shipping_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" placeholder="Планова" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- === MIDDLE: Scrollable product lines === -->
    <div class="lines-section-card" v-loading="loading">
      <div class="lines-header">
        <h3>Товари та послуги</h3>
        <el-button type="primary" :icon="Plus" @click="addLine" size="small">Додати рядок</el-button>
      </div>

      <el-table :data="form.lines" border style="width: 100%" class="lines-table">
        <el-table-column type="index" label="№" width="50" align="center" />
        <el-table-column label="Товар" min-width="200">
          <template #default="scope">
            <div style="display: flex; gap: 8px; align-items: center;">
              <el-select 
                v-model="scope.row.product_id" 
                filterable 
                placeholder="Пошук товару..." 
                style="flex: 1"
                @change="(val) => handleProductChange(val, scope.row)"
              >
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id">
                  <span>{{ p.name }}</span>
                </el-option>
              </el-select>
              <el-button :icon="Search" circle size="small" @click="openNomenclatureDialog(scope.$index)" title="Відкрити номенклатуру" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Характеристика" min-width="140">
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
                <div v-else class="selection-placeholder">
                  Оберіть...
                </div>
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
        <el-table-column label="Ціна" width="130">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" :precision="2" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="120" align="right">
          <template #default="scope">
            <span class="line-total text-sm font-medium">{{ formatCurrency(scope.row.total) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="" width="50" align="center">
          <template #default="scope">
            <el-button type="danger" :icon="Delete" link @click="removeLine(scope.$index)" />
          </template>
        </el-table-column>
      </el-table>

      <div v-if="form.lines.length === 0" class="empty-lines">
        <el-empty description="Додайте товари до замовлення" :image-size="60">
          <el-button type="primary" :icon="Plus" @click="addLine">Додати рядок</el-button>
        </el-empty>
      </div>
    </div>

    <!-- === FIXED BOTTOM: Comments, discount, total === -->
    <div class="order-footer">
      <div class="footer-left">
        <el-input
          v-model="form.comment"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 3 }"
          placeholder="Коментар до замовлення..."
          class="comment-input"
        />
      </div>
      <div class="footer-right">
        <div class="summary-rows">
          <div class="summary-row">
            <span class="s-label">Сума:</span>
            <span class="s-value">{{ formatCurrency(subtotal) }}</span>
          </div>
          <div class="summary-row discount-row">
            <span class="s-label">Знижка (%):</span>
            <el-input-number
              v-model="form.discount_percent"
              :min="0"
              :max="100"
              :precision="1"
              :step="1"
              controls-position="right"
              size="small"
              style="width: 100px"
            />
          </div>
          <div class="summary-row total-row" v-if="discountAmount > 0">
            <span class="s-label">Знижка:</span>
            <span class="s-value text-danger">-{{ formatCurrency(discountAmount) }}</span>
          </div>
          <div class="summary-row total-row">
            <span class="s-label total-label">Разом:</span>
            <span class="s-value total-value">{{ formatCurrency(totalAmount) }}</span>
          </div>
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
      :initial-variant-id="activeLineForSelector?.variant_id"
      @select="onVariantSelected"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Search, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import VariantSelectorDialog from './VariantSelectorDialog.vue'

const route = useRoute()
const router = useRouter()

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
  lines: []
})

const orderStatuses = ref([])

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
  return status?.color || 'info'
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
    // Reset variant
    line.variant_id = null
    
    // Auto-select primary variant or first variant if it has values
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
      // Virtual variant from configurator
      activeLineForSelector.value.variant_id = null
      activeLineForSelector.value._virtual_label = getVariantLabel(variant)
      activeLineForSelector.value._virtual_values = variant.values
      // Keep product price as base for virtual
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
  
  // Return "Attribute: Value", comma-separated
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

const getProductPrice = (productId) => {
  const prod = products.value.find(p => p.id === productId)
  return prod?.price || 0
}

const fetchData = async () => {
  loading.value = true
  try {
    const [custRes, whRes, prodRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_customer: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products'),
      api.get('/api/v1/dictionaries/ORDER_STATUS')
    ])
    customers.value = custRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    orderStatuses.value = statusRes.data
    
    if (isEditMode.value) {
      const data = res.data
      // Normalize numbers from API (Decimal strings -> Numbers)
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
      // Auto-select default warehouse for new orders
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

const saveOrder = async () => {
  if (!form.counterparty_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля та додайте товари")
    return
  }

  // Clean empty optional fields
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
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: #f8fafc; /* bg-slate-50 */
}

/* === TOP BAR === */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0; /* border-slate-200 */
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* shadow-sm placeholder */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1d1f;
}

/* === MODERN HEADER: Card layout === */
.order-details-card {
  margin: 0 16px 12px 16px;
  background: #ffffff;
  padding: 14px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f2f5;
  flex-shrink: 0;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.custom-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
  margin-bottom: 2px;
  display: block;
}

.req {
  color: #ef4444;
  margin-left: 2px;
}

.column-separator {
  position: relative;
}

@media (min-width: 992px) {
  .column-separator::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background: #f1f5f9;
  }
}

.details-form :deep(.el-form-item) {
  margin-bottom: 10px;
}

.details-form :deep(.el-input__wrapper),
.details-form :deep(.el-select__wrapper),
.details-form :deep(.el-date-editor.el-input__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  background-color: #ffffff !important;
  transition: all 0.2s ease;
  padding: 2px 10px;
  min-height: 34px;
}

.details-form :deep(.el-input__wrapper:hover),
.details-form :deep(.el-select__wrapper:hover),
.details-form :deep(.el-date-editor.el-input__wrapper:hover) {
  border-color: #cbd5e1 !important;
}

.details-form :deep(.el-form-item__label) {
  padding-bottom: 0 !important;
  line-height: normal !important;
}

/* === TABLE INPUTS === */
.lines-table :deep(.el-input__wrapper),
.lines-table :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  background-color: #ffffff !important;
  transition: all 0.2s ease;
  min-height: 32px;
}

.lines-table :deep(.el-input__wrapper:hover),
.lines-table :deep(.el-select__wrapper:hover) {
  border-color: #cbd5e1 !important;
}

.lines-table :deep(.el-input__wrapper.is-focus),
.lines-table :deep(.el-select__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* Compact table rows */
.lines-table :deep(.el-table__cell) {
  padding: 8px !important;
}

/* === SCROLLABLE LINES === */
.lines-section-card {
  margin: 0 16px 12px 16px;
  background: #ffffff;
  padding: 14px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f2f5;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.lines-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.lines-table {
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.lines-table :deep(th.el-table__cell) {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* === FIXED FOOTER === */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 16px;
  margin: 0 16px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
  gap: 16px;
}

.footer-left {
  flex: 1;
  max-width: 300px;
}

.comment-input :deep(.el-textarea__inner) {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  min-height: 40px !important;
  max-height: 80px;
  resize: none;
  font-size: 13px;
}

.footer-right {
  flex-shrink: 0;
  min-width: 280px;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.s-label {
  font-size: 14px;
  color: #64748b;
}

.s-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.total-row {
  padding-top: 12px;
  border-top: 2px solid #f1f5f9;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.total-value {
  font-size: 24px;
  font-weight: 700;
  color: #4f46e5; /* indigo-600 */
}

/* Variant Selector Styles */
.characteristic-cell-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.characteristic-display-box {
  flex: 1;
  min-height: 32px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 4px 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.characteristic-display-box:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.characteristic-display-box.has-value {
  background: white;
  border-color: #4f46e5;
  box-shadow: 0 1px 2px rgba(79, 70, 229, 0.05);
}

.selection-content {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selection-text {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

.selection-text.virtual {
  color: #059669; /* emerald-600 */
}

.selection-placeholder {
  font-size: 13px;
  color: #94a3b8;
}

.config-btn {
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.config-btn:hover {
  transform: rotate(30deg);
}

.option-item-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 12px;
}

.label-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-tag {
  flex-shrink: 0;
  font-family: inherit;
  font-weight: 600;
}

.virtual-selection {
  margin-left: 4px;
}

.virtual-selection :deep(.el-tag) {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
  color: #15803d;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
  }
  .order-details-panel {
    margin: 8px;
    padding: 16px;
  }
  .details-form :deep(.el-form-item__label) {
    font-size: 0.8125rem !important;
    padding-bottom: 4px !important;
  }
  .lines-section {
    padding: 0 8px 8px;
  }
  .order-footer {
    flex-direction: column;
    margin: 0 8px 8px;
    padding: 16px;
    gap: 16px;
  }
  .footer-right {
    min-width: 0;
    width: 100%;
  }
}

/* Extra small mobile fixes for very narrow screens */
@media (max-width: 480px) {
  .header-left h2 {
    font-size: 16px;
  }
  .summary-row {
     gap: 8px;
  }
  .total-value {
    font-size: 20px;
  }
}
</style>

