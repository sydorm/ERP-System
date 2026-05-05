<template>
  <div class="erp-page-container">
    <!-- ===== HEADER SECTION (BLOCK 1) ===== -->
    <div class="erp-header-section">
      <div class="erp-header-top">
        <div class="erp-title-row">
          <h1 class="erp-doc-title">
            {{ isEditMode ? 'Прибуткова накладна №' + form.receipt_number : 'Прибуткова накладна (створення)' }}
          </h1>
          <div class="erp-header-badges">
            <div class="erp-status-pill" :class="statusBadgeClass">{{ statusLabel }}</div>
            <div class="payment-status-badge" :class="paymentStatusClass">{{ paymentStatusLabel }}</div>
          </div>
        </div>
        
        <!-- BLOCK 3: Icon Actions -->
        <div class="erp-header-actions-icons">
          <el-tooltip content="Прикріпити файл" placement="top">
            <el-button size="small" circle :icon="Paperclip" class="icon-action-btn" />
          </el-tooltip>
          <el-tooltip content="Надіслати на пошту" placement="top">
            <el-button size="small" circle :icon="Message" class="icon-action-btn" />
          </el-tooltip>
          <el-tooltip content="Створити нагадування" placement="top">
            <el-button size="small" circle :icon="Bell" class="icon-action-btn" />
          </el-tooltip>
          <el-tooltip content="Друк" placement="top">
            <el-button size="small" circle :icon="Printer" class="icon-action-btn" @click="handlePrint" />
          </el-tooltip>
        </div>
      </div>

      <!-- BUTTONS ROW (BLOCK 1) -->
      <div class="erp-toolbar-buttons">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-back">Назад</el-button>
        <el-button type="primary" size="small" :loading="submitting" @click="saveReceipt('post_close')" class="erp-btn-save-close">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveReceipt('save')" class="erp-btn-secondary" :loading="submitting">Записати</el-button>
        <el-button size="small" @click="saveReceipt('post')" class="erp-btn-secondary" :loading="submitting">Провести</el-button>
      </div>
    </div>

    <div class="erp-content-scrollable">
      <div class="erp-document-card">
        <!-- ===== REQUISITES (BLOCK 2) ===== -->
        <div class="erp-requisites-grid">
          <div class="requisite-item narrow">
            <label class="requisite-label">Номер</label>
            <el-input v-model="form.receipt_number" size="small" disabled />
          </div>
          <div class="requisite-item date-item">
            <label class="requisite-label">Від</label>
            <el-date-picker v-model="form.receipt_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:100%" />
          </div>
          <div class="requisite-item basis-item">
            <label class="requisite-label">На підставі</label>
            <el-select v-model="form.base_order_id" clearable placeholder="—" size="small" style="width:100%" @change="onBaseOrderChange">
              <el-option v-for="o in purchaseOrders" :key="o.id" :label="o.order_number" :value="o.id" />
            </el-select>
          </div>
          <div class="requisite-item wide">
            <label class="requisite-label">Постачальник</label>
            <el-select v-model="form.supplier_id" filterable size="small" style="width:100%" @change="onSupplierChange">
              <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </div>
        </div>

        <!-- Supplier Info Banner -->
        <div class="client-info-banner" v-if="selectedSupplierObj">
          <span class="client-info-item"><el-icon><Phone /></el-icon> {{ selectedSupplierObj.phone || '—' }}</span>
          <span class="client-info-item"><el-icon><Message /></el-icon> {{ selectedSupplierObj.email || '—' }}</span>
          <span class="client-info-item"><el-icon><Location /></el-icon> {{ selectedSupplierObj.address || '—' }}</span>
        </div>

        <!-- ===== MAIN BODY ===== -->
        <div class="order-body">
          <div class="order-main">
            <el-tabs v-model="activeTab" class="order-tabs">
              <!-- TAB: Товари -->
              <el-tab-pane name="items">
                <template #label>
                  <el-icon><Box /></el-icon>&nbsp;Товари
                  <el-badge v-if="form.lines.length" :value="form.lines.length" class="tab-badge" />
                </template>
                <div class="erp-table-container" v-loading="loading">
                  <DocumentItemsTable
                    :items="form.lines"
                    :products="products"
                    :warehouses="warehouses"
                    v-model:warehouse-id="form.warehouse_id"
                    mode="invoice"
                    :show-specification="false"
                    :show-warehouse="true"
                    :show-characteristics="hasAnyCharacteristics"
                    @add-line="addLine"
                    @remove-line="removeLine"
                  />
                </div>
                
                <!-- BLOCK 4: Comment -->
                <div class="comment-section">
                  <label class="comment-label">Коментар до накладної</label>
                  <el-input v-model="form.comment" type="textarea" :autosize="{ minRows: 2, maxRows: 3 }"
                    placeholder="Напишіть коментар..." class="erp-comment-input" />
                </div>
              </el-tab-pane>

              <!-- TAB: Доставка -->
              <el-tab-pane name="delivery">
                <template #label><el-icon><Van /></el-icon>&nbsp;Доставка</template>
                <div class="tab-content-card">
                  <div class="fields-grid-3">
                    <div class="field-block">
                      <label class="field-label">Спосіб доставки</label>
                      <el-select v-model="delivery.method" size="small" style="width:100%">
                        <el-option value="self" label="Самовивіз" />
                        <el-option value="supplier" label="Доставка постачальника" />
                        <el-option value="np_branch" label="Нова Пошта (відділення)" />
                        <el-option value="np_courier" label="Нова Пошта (кур'єр)" />
                        <el-option value="truck" label="Вантажний транспорт" />
                      </el-select>
                    </div>
                    <div class="field-block">
                      <label class="field-label">Вартість доставки (₴)</label>
                      <el-input-number v-model="delivery.cost" :min="0" :precision="2" :controls="false" size="small" style="width:100%" />
                    </div>
                  </div>
                  <div class="field-block">
                    <label class="field-label">Адреса отримання</label>
                    <el-input v-model="delivery.address" type="textarea" :autosize="{ minRows: 2 }" size="small" placeholder="Адреса складу..." />
                  </div>
                </div>
              </el-tab-pane>

              <!-- TAB: Оплата -->
              <el-tab-pane name="payment">
                <template #label><el-icon><CreditCard /></el-icon>&nbsp;Оплата</template>
                <div class="tab-content-card">
                  <div class="fields-grid-3">
                    <div class="field-block">
                      <label class="field-label">Спосіб оплати</label>
                      <el-select v-model="payment.method" size="small" style="width:100%">
                        <el-option value="cash" label="Готівка" />
                        <el-option value="bank_transfer" label="Банківський переказ" />
                      </el-select>
                    </div>
                    <div class="field-block">
                      <label class="field-label">Статус оплати</label>
                      <div class="payment-status-badge" :class="paymentStatusClass">{{ paymentStatusLabel }}</div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- TAB: Документи -->
              <el-tab-pane name="documents">
                <template #label><el-icon><Document /></el-icon>&nbsp;Документи</template>
                <div class="tab-content-card">
                  <div v-if="form.base_order_id" class="doc-item">
                    <el-icon size="24" color="#6366f1"><Document /></el-icon>
                    <div class="doc-info">
                      <span class="doc-name">Замовлення постачальнику (основа)</span>
                      <span class="doc-meta">№ {{ getOrderNumber(form.base_order_id) }}</span>
                    </div>
                    <el-button size="small" @click="router.push(`/purchases/orders/${form.base_order_id}`)" circle :icon="View" />
                  </div>
                  <div v-else class="empty-state">Пов'язаних документів немає</div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- ===== SIDEBAR (BLOCK 5) ===== -->
          <div class="order-sidebar">
            <div class="sidebar-card">
              <div class="sidebar-card-title">Підсумки накладної</div>
              <div class="summary-rows">
                <div class="sum-row"><span>Позицій:</span><span>{{ form.lines.length }}</span></div>
                <div class="sum-row"><span>К-ть товарів:</span><span>{{ formattedTotalQty }} шт</span></div>
                <div class="sum-row"><span>Доставка:</span><span>{{ formatCurrency(delivery.cost) }}</span></div>
                <div class="sum-divider"></div>
                <div class="sum-row"><span>Сума без ПДВ:</span><span>{{ formatCurrency(totalAmount / 1.2) }}</span></div>
                <div class="sum-row"><span>ПДВ (20%):</span><span>{{ formatCurrency(totalAmount - totalAmount / 1.2) }}</span></div>
                <div class="sum-divider-bold"></div>
                <div class="sum-row sum-row--total">
                  <span>ВСЬОГО:</span>
                  <span class="total-value">{{ formatCurrency(totalAmount + delivery.cost) }}</span>
                </div>
              </div>
            </div>

            <div class="sidebar-spacer"></div>

            <div class="sidebar-card">
              <div class="sidebar-card-title">Швидкі дії</div>
              <div class="quick-actions">
                <el-button size="small" class="qa-btn" @click="handlePrint">
                  <el-icon><Printer /></el-icon> Друк накладної
                </el-button>
                <el-button size="small" class="qa-btn" @click="handleCreateInvoice">
                  <el-icon><CreditCard /></el-icon> Виставити рахунок
                </el-button>
                <el-button size="small" class="qa-btn" @click="activeTab = 'delivery'">
                  <el-icon><Van /></el-icon> Параметри доставки
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, Plus, ArrowDown, ArrowUp, MoreFilled,
  Printer, CreditCard, Phone, Message, Location,
  Box, Van, Document, Timer, View, Paperclip, Bell
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import DocumentItemsTable from '@/components/DocumentItemsTable.vue'

const route = useRoute()
const router = useRouter()

// ===== STATE =====
const loading = ref(false)
const submitting = ref(false)
const isEditMode = computed(() => !!route.params.id && route.params.id !== 'new')
const activeTab = ref('items')
const isHeaderExpanded = ref(true)

const delivery = reactive({ method: 'self', cost: 0, address: '' })
const payment = reactive({ method: 'bank_transfer' })

const form = reactive({
  receipt_number: 'Авто',
  receipt_date: new Date().toISOString().split('T')[0],
  supplier_id: '',
  warehouse_id: '',
  base_order_id: null,
  comment: '',
  currency: 'UAH',
  status: 'draft',
  lines: []
})

const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const purchaseOrders = ref([])

// ===== COMPUTED =====
const totalAmount = computed(() => form.lines.reduce((acc, line) => acc + (line.total || 0), 0))
const totalQty = computed(() => form.lines.reduce((sum, l) => sum + (l.quantity || 0), 0))
const formattedTotalQty = computed(() => {
  const qty = totalQty.value
  return Number.isInteger(qty) ? qty.toString() : qty.toFixed(3).replace(/\.?0+$/, '')
})

const hasAnyCharacteristics = computed(() => {
  return form.lines.some(l => {
    const p = products.value.find(prod => prod.id === l.product_id)
    return p?.product_attributes?.some(a => a.generates_sku) || l.variant_id
  })
})

// ===== ACTIONS =====
const goBack = () => router.push('/purchases/receipts')
const handlePrint = () => ElMessage.info('Друк накладної (в розробці)')
const handleCreateInvoice = () => ElMessage.info('Виставлення рахунку (в розробці)')

const onSupplierChange = (id) => {
  const s = suppliers.value.find(x => x.id === id)
  if (s && s.address) delivery.address = s.address
}

const onBaseOrderChange = async (orderId) => {
  if (!orderId) return
  try {
    const res = await api.get(`/api/v1/purchase-orders/${orderId}`)
    const order = res.data
    form.supplier_id = order.supplier_id
    form.warehouse_id = order.warehouse_id
    form.lines = (order.lines || []).map(l => ({
      product_id: l.product_id,
      variant_id: l.variant_id,
      quantity: Number(l.quantity),
      price: Number(l.price),
      total: Number(l.total),
      values: l.attribute_values || []
    }))
    onSupplierChange(order.supplier_id)
    ElMessage.success(`Дані замовлення ${order.order_number} завантажено`)
  } catch {
    ElMessage.error('Помилка завантаження замовлення')
  }
}

const getOrderNumber = (id) => purchaseOrders.value.find(o => o.id === id)?.order_number || '—'

const addLine = () => {
  form.lines.push({ product_id: '', variant_id: null, quantity: 1, price: 0, total: 0 })
}
const removeLine = (index) => form.lines.splice(index, 1)

// ===== DATA FETCHING =====
const fetchData = async () => {
  loading.value = true
  try {
    const [supRes, whRes, prodRes, ordRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products'),
      api.get('/api/v1/purchase-orders')
    ])
    suppliers.value = supRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    purchaseOrders.value = ordRes.data

    if (isEditMode.value) {
      const res = await api.get(`/api/v1/purchase-receipts/${route.params.id}`)
      const data = res.data
      if (data.lines) {
          data.lines.forEach(l => {
              l.values = l.attribute_values || []
          })
      }
      Object.assign(form, data)
    } else if (route.query.base_order_id) {
      form.base_order_id = route.query.base_order_id
      await onBaseOrderChange(form.base_order_id)
    } else {
      const defaultWH = warehouses.value.find(w => w.is_default)
      if (defaultWH) form.warehouse_id = defaultWH.id
      addLine()
    }
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

// ===== SAVE =====
const saveReceipt = async (action = 'save') => {
  if (!form.supplier_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля")
    return
  }

  // Frontend validation for variants
  // Skip check if line already has attribute_values (materials skip variant creation)
  const missingVariant = form.lines.find(l => {
     const p = products.value.find(prod => prod.id === l.product_id)
     const hasAttributes = p?.product_attributes?.some(a => a.generates_sku)
     const hasValues = l.values && l.values.length > 0
     return hasAttributes && !l.variant_id && !hasValues
  })
  if (missingVariant) {
    ElMessage.error('Будь ласка, оберіть характеристику для всіх товарів')
    return
  }

  if (action === 'post' || action === 'post_close') {
    form.status = 'posted'
  }

  const payload = {
    ...form,
    lines: form.lines.map(l => ({
      product_id: l.product_id,
      variant_id: l.variant_id,
      quantity: l.quantity,
      price: l.price,
      total: l.total,
      attribute_values: l.values,
      characteristic_width: l.characteristic_width,
      characteristic_height: l.characteristic_height
    })),
    total_amount: totalAmount.value
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/purchase-receipts/${route.params.id}`, payload)
      ElMessage.success('Накладну оновлено')
    } else {
      const res = await api.post('/api/v1/purchase-receipts', payload)
      ElMessage.success('Накладну створено та проведено')
    }
    if (action.includes('close') || !isEditMode.value) router.push('/purchases/receipts')
    else await fetchData()
  } catch (error) {
    ElMessage.error('Помилка збереження')
  } finally {
    submitting.value = false
  }
}

// ===== HELPERS =====
const formatCurrency = (val) =>
  new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH', maximumFractionDigits: 0 }).format(val || 0)

onMounted(fetchData)
</script>

<style scoped>
/* ===== NEW DESIGN STYLES (BLOCK 6) ===== */
.erp-page-container {
  display: flex; flex-direction: column; height: 100vh; overflow: hidden;
  background-color: #F5F6FA; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2D3748;
}

.erp-header-section {
  background: #fff; padding: 16px 24px 12px 24px; border-bottom: 1px solid #E2E8F0;
  flex-shrink: 0;
}

.erp-header-top {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}

.erp-title-row {
  display: flex; align-items: center; gap: 16px;
}

.erp-doc-title {
  font-size: 18px; font-weight: 700; color: #1A202C; margin: 0;
}

.erp-header-badges {
  display: flex; align-items: center; gap: 8px;
}

.erp-status-pill {
  padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase;
  display: inline-flex; align-items: center;
}
.status-draft { background: #EDF2F7; color: #4A5568; }
.status-done { background: #C6F6D5; color: #22543D; }

.payment-status-badge {
  padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase;
  display: inline-flex; align-items: center;
}
.ps-badge--red { background: #FED7D7; color: #822727; }

.erp-header-actions-icons {
  display: flex; gap: 8px;
}

.icon-action-btn {
  border: 1px solid #E2E8F0 !important; color: #718096 !important;
  transition: all 0.2s;
}
.icon-action-btn:hover {
  background: #EDF2F7 !important; color: #4A5568 !important; border-color: #CBD5E0 !important;
}

.erp-toolbar-buttons {
  display: flex; gap: 10px; align-items: center;
}

.erp-btn-back {
  background: #fff !important; border: 1px solid #E2E8F0 !important; color: #4A5568 !important;
}

.erp-btn-save-close {
  background: #3182CE !important; border-color: #3182CE !important;
  color: #fff !important; font-weight: 600 !important; padding: 0 16px !important;
}

.erp-btn-secondary {
  background: #fff !important; border: 1px solid #3182CE !important;
  color: #3182CE !important; font-weight: 600 !important;
}

.erp-content-scrollable {
  flex: 1; overflow-y: auto; padding: 24px;
}

.erp-document-card {
  background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  max-width: 1366px; margin: 0 auto; display: flex; flex-direction: column;
}

.erp-requisites-grid {
  display: grid; grid-template-columns: 120px 160px 180px 1fr; gap: 20px;
  padding: 24px; border-bottom: 1px solid #F7FAFC;
}

.requisite-item {
  display: flex; flex-direction: column; gap: 6px;
}

.requisite-label {
  font-size: 11px; color: #718096; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
}

.client-info-banner {
  margin: 0 24px 16px 24px; padding: 10px 16px; background: #EBF8FF;
  border-radius: 8px; display: flex; gap: 24px; font-size: 13px; color: #2B6CB0;
}

.order-body {
  display: flex; flex: 1; padding: 0 24px 24px 24px; gap: 24px;
}

.order-main {
  flex: 1; display: flex; flex-direction: column; min-width: 0;
}

.erp-table-container {
  border: 1px solid #E2E8F0; border-radius: 8px; overflow: hidden; flex: 1;
  min-height: 300px;
}

.comment-section {
  margin-top: 24px; display: flex; flex-direction: column; gap: 8px;
}

.comment-label {
  font-size: 13px; font-weight: 600; color: #4A5568;
}

.order-sidebar {
  width: 300px; display: flex; flex-direction: column; gap: 16px; flex-shrink: 0;
}

.sidebar-card {
  background: #F7FAFC; padding: 20px; border-radius: 10px; border: 1px solid #EDF2F7;
}

.sidebar-card-title {
  font-size: 12px; font-weight: 700; color: #718096; margin-bottom: 16px;
  text-transform: uppercase; letter-spacing: 1px;
}

.summary-rows {
  display: flex; flex-direction: column; gap: 8px;
}

.sum-row {
  display: flex; justify-content: space-between; font-size: 14px; color: #4A5568;
}

.sum-divider {
  height: 1px; background: #E2E8F0; margin: 8px 0;
}

.sum-divider-bold {
  height: 2px; background: #CBD5E0; margin: 12px 0;
}

.sum-row--total {
  font-size: 16px; font-weight: 800; color: #1A202C; padding: 10px;
  background: #EBF8FF; border-radius: 6px;
}

.total-value {
  color: #2B6CB0;
}

.sidebar-spacer {
  height: 16px;
}

.quick-actions {
  display: flex; flex-direction: column; gap: 10px;
}

.qa-btn {
  width: 100%; justify-content: flex-start !important; height: 40px !important;
  font-size: 13px !important; margin-left: 0 !important;
  border: 1px solid #E2E8F0 !important;
  background: #fff !important;
}
.qa-btn:hover { background: #F7FAFC !important; border-color: #3182CE !important; color: #3182CE !important; }

/* Tabs adjustments */
.order-tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background-color: #E2E8F0; }
.order-tabs :deep(.el-tabs__item) { font-weight: 600; color: #718096; font-size: 14px; height: 40px; }
.order-tabs :deep(.el-tabs__item.is-active) { color: #3182CE; }
.order-tabs :deep(.el-tabs__content) { overflow: visible; }

.tab-content-card { padding: 24px 0; display: flex; flex-direction: column; gap: 20px; }
.fields-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.field-block { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 12px; color: #718096; font-weight: 600; text-transform: uppercase; }

@media (max-width: 1366px) {
  .erp-requisites-grid { grid-template-columns: 100px 140px 150px 1fr; }
  .order-sidebar { width: 260px; }
}
</style>
