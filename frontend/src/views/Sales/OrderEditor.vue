<template>
  <div class="page-container">
    <!-- === TOP BAR: Title + Save === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? 'Замовлення №' + form.order_number : 'Нове замовлення' }}</h2>
        <el-tag v-if="isEditMode && form.status" :type="statusType" size="small">{{ statusLabel }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrder">
          Зберегти замовлення
        </el-button>
      </div>
    </div>

    <!-- === STICKY: Order details panel === -->
    <div class="order-details-panel">
      <el-form :model="form" label-position="top" size="default" class="details-form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="3" :lg="3">
            <el-form-item label="Номер">
              <el-input v-model="form.order_number" placeholder="ORD-0001" />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="12" :md="4" :lg="4">
            <el-form-item label="Дата створення">
              <el-date-picker v-model="form.order_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="12" :md="4" :lg="4">
            <el-form-item label="Дата відвантаження">
              <el-date-picker v-model="form.shipping_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" placeholder="Планова" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="5" :lg="5">
            <el-form-item label="Клієнт" required>
              <template #label>
                <span class="required-label">Клієнт <span>*</span></span>
              </template>
              <el-select v-model="form.counterparty_id" filterable placeholder="Оберіть клієнта" style="width: 100%" @change="onClientChange">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="4" :lg="4">
            <el-form-item label="Договір">
              <el-input v-model="form.contract" placeholder="№ договору" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="4" :lg="4">
            <el-form-item label="Склад" required>
              <template #label>
                <span class="required-label">Склад <span>*</span></span>
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
        </el-row>
      </el-form>
    </div>

    <!-- === MIDDLE: Scrollable product lines === -->
    <div class="lines-section" v-loading="loading">
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
        <el-table-column label="Характеристика" min-width="180">
          <template #default="scope">
            <div style="display: flex; gap: 8px; align-items: center;">
              <el-select
                v-model="scope.row.variant_id"
                placeholder="Оберіть..."
                style="flex: 1"
                clearable
                :disabled="!scope.row.product_id || getProductVariants(scope.row.product_id).length === 0"
                @change="(val) => handleVariantChange(val, scope.row)"
              >
                <el-option
                  v-for="v in getProductVariants(scope.row.product_id)"
                  :key="v.id"
                  :label="getVariantLabel(v)"
                  :value="v.id"
                >
                  <span>{{ getVariantLabel(v) }}</span>
                  <el-tag v-if="v.price_override" size="small" type="warning" style="margin-left: 8px">
                    {{ formatShort(v.price_override) }}
                  </el-tag>
                </el-option>
              </el-select>
              <el-button 
                v-if="scope.row.product_id && getProductVariants(scope.row.product_id).length > 0"
                :icon="Setting" 
                circle 
                size="small" 
                @click="openVariantSelector(scope.row)" 
                title="Конфігуратор характеристик"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Кількість" width="130">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="0.001" @change="updateLineTotal(scope.row)" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Ціна" width="140">
          <template #default="scope">
            <el-input-number v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" :precision="2" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="130" align="right">
          <template #default="scope">
            <span class="line-total">{{ formatCurrency(scope.row.total) }}</span>
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
          :rows="2"
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
  order_number: 'ORD-' + Date.now().toString().slice(-6),
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
  const map = { draft: 'info', confirmed: '', shipped: 'warning', completed: 'success', cancelled: 'danger' }
  return map[form.status] || 'info'
})

const statusLabel = computed(() => {
  const map = { draft: 'Чернетка', confirmed: 'Підтверджено', shipped: 'Відвантажено', completed: 'Завершено', cancelled: 'Скасовано' }
  return map[form.status] || form.status
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
    activeLineForSelector.value.variant_id = variant.id
    handleVariantChange(variant.id, activeLineForSelector.value)
  }
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
  if (!variant.values || variant.values.length === 0) return variant.sku
  // Return only values, comma-separated
  return variant.values.map(v => v.option?.value || v.text_value).filter(Boolean).join(', ')
}

const fetchData = async () => {
  loading.value = true
  try {
    const [custRes, whRes, prodRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_customer: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products')
    ])
    customers.value = custRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    
    if (isEditMode.value) {
      const res = await api.get(`/api/v1/orders/${route.params.id}`)
      Object.assign(form, res.data)
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

/* === STICKY DETAILS PANEL === */
.order-details-panel {
  background: white;
  padding: 24px;
  margin: 20px;
  border-radius: 0.75rem; /* rounded-xl */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06); /* shadow-sm */
  border: 1px solid #e2e8f0; /* border-slate-200 */
  flex-shrink: 0;
}

/* Label Styling */
.details-form :deep(.el-form-item__label) {
  color: #334155 !important; /* text-slate-700 */
  font-weight: 500 !important; /* font-medium */
  font-size: 0.875rem !important; /* text-sm */
  padding-bottom: 6px !important;
  line-height: 1.25 !important;
}

.required-label span {
  color: #f56c6c;
  margin-left: 2px;
}

/* Input Styling (Slate background and border) */
.details-form :deep(.el-input__wrapper),
.details-form :deep(.el-select .el-input__wrapper),
.details-form :deep(.el-date-editor.el-input__wrapper) {
  background-color: #f8fafc !important; /* bg-slate-50 */
  box-shadow: 0 0 0 1px #e2e8f0 inset !important; /* border-slate-200 */
  border-radius: 0.5rem !important;
  transition: all 0.2s;
}

/* Focus Styling (Indigo accent) */
.details-form :deep(.el-input__wrapper.is-focus),
.details-form :deep(.el-select .el-input__wrapper.is-focus),
.details-form :deep(.el-date-editor.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2), 0 0 0 1px #6366f1 inset !important; /* focus:ring-2 focus:ring-indigo-500 */
}

/* === SCROLLABLE LINES === */
.lines-section {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px;
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 4px;
}

.lines-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.lines-table {
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.lines-table :deep(th.el-table__cell) {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
}

/* === FIXED FOOTER === */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  margin: 0 20px 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  gap: 24px;
}

.footer-left {
  flex: 1;
  max-width: 500px;
}

.comment-input :deep(.el-textarea__inner) {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}

.footer-right {
  flex-shrink: 0;
  min-width: 300px;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

