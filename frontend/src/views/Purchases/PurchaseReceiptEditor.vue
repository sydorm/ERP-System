<template>
  <div class="erp-page-container">

    <!-- ===== TOOLBAR ===== -->
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button type="warning" size="small" :loading="submitting" @click="saveReceipt('post_close')" class="erp-btn-primary">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveReceipt('save')" class="erp-btn" :loading="submitting">Записати</el-button>
        <el-button size="small" @click="saveReceipt('post')" class="erp-btn" :loading="submitting">Провести</el-button>
        
        <div class="erp-doc-info">
          <span class="erp-doc-title">{{ isEditMode ? 'Прибуткова накладна №' + form.receipt_number : 'Прибуткова накладна (створення)' }}</span>
        </div>
      </div>
      <div class="erp-toolbar-right">
        <el-button size="small" class="erp-btn-icon" :icon="isHeaderExpanded ? ArrowUp : ArrowDown" @click="isHeaderExpanded = !isHeaderExpanded" title="Шапка" />
        <el-dropdown trigger="click" size="small">
          <el-button size="small" class="erp-btn-icon" :icon="MoreFilled" title="Більше дій" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handlePrint"><el-icon><Printer /></el-icon> Друк накладної</el-dropdown-item>
              <el-dropdown-item @click="handleCreateInvoice"><el-icon><CreditCard /></el-icon> Виставити рахунок</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- ===== HEADER FIELDS ===== -->
    <el-collapse-transition>
      <div class="erp-header-fields" v-show="isHeaderExpanded">
        <div class="erp-field-row justify-between">
          <div class="erp-field">
            <span class="erp-label">Номер:</span>
            <el-input v-model="form.receipt_number" size="small" class="erp-input-wrapper" disabled style="width:120px" />
          </div>
          <div class="erp-field">
            <span class="erp-label">від:</span>
            <el-date-picker v-model="form.receipt_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:145px" />
          </div>
          <div class="erp-field">
            <span class="erp-label">На підставі:</span>
            <el-select v-model="form.base_order_id" clearable placeholder="—" size="small" style="width:160px" @change="onBaseOrderChange">
              <el-option v-for="o in purchaseOrders" :key="o.id" :label="o.order_number" :value="o.id" />
            </el-select>
          </div>
          <div class="erp-badges-group ml-auto">
            <div class="erp-status-pill" :class="statusBadgeClass">{{ statusLabel }}</div>
            <div class="payment-status-badge" :class="paymentStatusClass">{{ paymentStatusLabel }}</div>
          </div>
        </div>
        <div class="erp-field-row mt-1">
          <div class="erp-field client-field">
            <span class="erp-label req">Постачальник:</span>
            <el-select v-model="form.supplier_id" filterable size="small" class="erp-input-wrapper client-select" @change="onSupplierChange">
              <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </div>
        </div>
        <div class="client-info-banner" v-if="selectedSupplierObj">
          <span class="client-info-item"><el-icon><Phone /></el-icon> {{ selectedSupplierObj.phone || '—' }}</span>
          <span class="client-info-item"><el-icon><Message /></el-icon> {{ selectedSupplierObj.email || '—' }}</span>
          <span class="client-info-item"><el-icon><Location /></el-icon> {{ selectedSupplierObj.address || '—' }}</span>
        </div>
      </div>
    </el-collapse-transition>

    <!-- ===== MAIN BODY ===== -->
    <div class="order-body">
      <div class="order-main">
        <el-tabs v-model="activeTab" class="order-tabs">

          <!-- TAB: Товари -->
          <el-tab-pane name="items">
            <template #label><el-icon><Box /></el-icon>&nbsp;Товари
              <el-badge v-if="form.lines.length" :value="form.lines.length" class="tab-badge" />
            </template>
            <div class="erp-table-wrapper" v-loading="loading">
              <DocumentItemsTable
                :items="form.lines"
                :products="products"
                :warehouses="warehouses"
                v-model:warehouse-id="form.warehouse_id"
                mode="invoice"
                :show-specification="false"
                :show-warehouse="true"
                @add-line="addLine"
                @remove-line="removeLine"
              />
            </div>
            <div class="items-comment">
              <el-input v-model="form.comment" type="textarea" :autosize="{ minRows: 2, maxRows: 3 }"
                placeholder="Коментар до накладної..." class="erp-comment-input" />
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

          <!-- TAB: Історія -->
          <el-tab-pane name="history">
            <template #label><el-icon><Timer /></el-icon>&nbsp;Історія</template>
            <div class="tab-content-card">
              <div class="empty-state">Журнал змін (в розробці)</div>
            </div>
          </el-tab-pane>

        </el-tabs>
      </div>

      <!-- ===== SIDEBAR ===== -->
      <div class="order-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">Підсумки накладної</div>
          <div class="summary-rows">
            <div class="sum-row"><span>Позицій:</span><span>{{ form.lines.length }}</span></div>
            <div class="sum-row"><span>К-ть товарів:</span><span>{{ totalQty }} шт</span></div>
            <div class="sum-row"><span>Доставка:</span><span>{{ formatCurrency(delivery.cost) }}</span></div>
            <div class="sum-divider"></div>
            <div class="sum-row"><span>Сума без ПДВ:</span><span>{{ formatCurrency(totalAmount / 1.2) }}</span></div>
            <div class="sum-row"><span>ПДВ (20%):</span><span>{{ formatCurrency(totalAmount - totalAmount / 1.2) }}</span></div>
            <div class="sum-divider"></div>
            <div class="sum-row sum-row--total">
              <span>ВСЬОГО:</span>
              <span class="total-value">{{ formatCurrency(totalAmount + delivery.cost) }}</span>
            </div>
          </div>
        </div>
        <div class="sidebar-card">
          <div class="sidebar-card-title">Швидкі дії</div>
          <div class="quick-actions">
            <el-button size="small" class="qa-btn" @click="handlePrint">
              <el-icon><Printer /></el-icon> Друк накладної
            </el-button>
            <el-button size="small" class="qa-btn" @click="handleCreateInvoice">
              <el-icon><CreditCard /></el-icon> Виставити рахунок
            </el-button>
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
  Box, Van, Document, Timer, View
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

const selectedSupplierObj = computed(() => suppliers.value.find(s => s.id === form.supplier_id) || null)

const statusBadgeClass = computed(() => form.status === 'posted' ? 'status-done' : 'status-draft')
const statusLabel = computed(() => form.status === 'posted' ? 'Проведено' : 'Чернетка')
const paymentStatusClass = computed(() => 'ps-badge--red')
const paymentStatusLabel = computed(() => 'Не оплачено')

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
      total: Number(l.total)
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
      Object.assign(form, res.data)
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
  const missingVariant = form.lines.find(l => {
     const p = products.value.find(prod => prod.id === l.product_id)
     return p?.product_attributes?.some(a => a.generates_sku) && !l.variant_id
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

onMounted(fetchData)
</script>

<style scoped>
/* Reusing styles from PurchaseOrderEditor.vue */
.erp-page-container {
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
  background-color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif;
}
.erp-toolbar {
  display: flex; align-items: center; justify-content: space-between; padding: 6px 12px;
  background-color: #fcfcfc; border-bottom: 1px solid #dcdfe6; flex-shrink: 0;
}
.erp-toolbar-left { display: flex; align-items: center; gap: 8px; }
.erp-toolbar-right { display: flex; align-items: center; gap: 6px; }
.erp-btn, .erp-btn-icon, .erp-btn-primary {
  border-radius: 2px !important; font-size: 13px !important; height: 28px !important;
  padding: 0 12px !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; color: #303133 !important;
}
.erp-btn-primary {
  background-color: #eef2ff !important; border-color: #6366f1 !important;
  color: #4338ca !important; font-weight: 600 !important;
}
.erp-doc-info { margin-left: 16px; }
.erp-doc-title { font-size: 14px; font-weight: 600; color: #303133; }

.erp-header-fields {
  background-color: #f6f7f9; padding: 10px 16px 8px 16px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid #e4e7ed;
}
.erp-field-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.erp-field { display: flex; align-items: center; }
.erp-label { font-size: 13px; color: #374151; padding-right: 8px; white-space: nowrap; font-weight: 500; }
.erp-label.req::after { content: ' *'; color: #f56c6c; }
.erp-input-wrapper { width: 160px; }
.client-select { width: 320px; }
.erp-header-fields :deep(.el-input__wrapper), .erp-header-fields :deep(.el-select__wrapper) {
  border-radius: 4px !important; box-shadow: none !important; border: 1px solid #d1d5db !important;
  background-color: #fff !important; min-height: 28px !important; height: 28px !important;
}

.erp-badges-group { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.erp-status-pill {
  display: inline-flex; align-items: center; padding: 2px 10px;
  border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid;
}
.status-draft { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.status-done { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }

.client-info-banner {
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;
  padding: 4px 12px; font-size: 11px; color: #0369a1; margin-top: 4px;
}
.client-info-item { display: flex; align-items: center; gap: 4px; }

.order-body { flex: 1; display: flex; overflow: hidden; }
.order-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
.order-tabs { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.order-tabs :deep(.el-tabs__header) { margin: 0; background: #fff; padding: 0 12px; border-bottom: 1px solid #e4e7ed; }
.order-tabs :deep(.el-tabs__content) { flex: 1; overflow: auto; }
.order-tabs :deep(.el-tab-pane) { height: 100%; }

.erp-table-wrapper { flex: 1; }
.items-comment { padding: 8px 12px; background: #f6f7f9; border-top: 1px solid #e4e7ed; }

.tab-content-card { padding: 16px; display: flex; flex-direction: column; gap: 14px; max-width: 800px; }
.fields-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.field-block { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 12px; color: #606266; font-weight: 500; }

.payment-status-badge { padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 500; }
.ps-badge--red { background: #fee2e2; color: #991b1b; }

.doc-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border: 1px solid #e2e8f0; border-radius: 8px; background: #fff;
}
.doc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.doc-name { font-size: 13px; font-weight: 500; color: #1e293b; }
.doc-meta { font-size: 11px; color: #94a3b8; }
.empty-state { padding: 40px; color: #94a3b8; font-size: 13px; text-align: center; }

.order-sidebar {
  width: 260px; flex-shrink: 0; background: #fff; border-left: 1px solid #e4e7ed;
  overflow-y: auto; display: flex; flex-direction: column;
}
.sidebar-card { padding: 14px 16px; border-bottom: 1px solid #f0f2f5; }
.sidebar-card-title { font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.summary-rows { display: flex; flex-direction: column; gap: 6px; }
.sum-row { display: flex; justify-content: space-between; font-size: 13px; color: #606266; }
.sum-row--total { font-size: 15px; font-weight: 700; color: #1e293b; margin-top: 4px; }
.total-value { color: #6366f1; }
.sum-divider { height: 1px; background: #e4e7ed; margin: 4px 0; }

.quick-actions { display: flex; flex-direction: column; gap: 6px; }
.qa-btn { width: 100%; justify-content: flex-start !important; height: 32px !important; font-size: 12px !important; margin-left: 0 !important; }
</style>
