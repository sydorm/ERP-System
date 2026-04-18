<template>
  <div class="erp-page-container">

    <!-- ===== TOOLBAR ===== -->
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button type="warning" size="small" :loading="submitting" @click="saveOrder('post_close')" class="erp-btn-primary">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveOrder('save')" class="erp-btn" :loading="submitting">Записати</el-button>
        <el-button size="small" @click="saveOrder('post')" class="erp-btn" :loading="submitting">Провести</el-button>
        <el-dropdown v-if="isEditMode" trigger="click" @command="handleCreateBasedOn" size="small">
          <el-button size="small" class="erp-btn">
            Створити на підставі <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="receipt">Прибуткова накладна</el-dropdown-item>
              <el-dropdown-item command="payment">Вихідний платіж</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <div class="erp-doc-info">
          <span class="erp-doc-title">{{ isEditMode ? 'Замовлення постачальнику ' + form.order_number : 'Замовлення постачальнику (створення)' }}</span>
        </div>
      </div>
      <div class="erp-toolbar-right">
        <el-button size="small" class="erp-btn-icon" :icon="isHeaderExpanded ? ArrowUp : ArrowDown" @click="isHeaderExpanded = !isHeaderExpanded" title="Шапка" />
        <el-dropdown trigger="click" size="small">
          <el-button size="small" class="erp-btn-icon" :icon="MoreFilled" title="Більше дій" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handlePrint"><el-icon><Printer /></el-icon> Друк</el-dropdown-item>
              <el-dropdown-item @click="handleSendToSupplier" :disabled="!selectedSupplierObj">
                <el-icon><Promotion /></el-icon> Надіслати постачальнику
              </el-dropdown-item>
              <el-dropdown-item @click="handleExportExcel"><el-icon><Download /></el-icon> Експорт в Excel</el-dropdown-item>
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
            <el-input v-model="form.order_number" size="small" class="erp-input-wrapper" disabled style="width:120px" />
          </div>
          <div class="erp-field">
            <span class="erp-label">від:</span>
            <el-date-picker v-model="form.order_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:145px" />
          </div>
          <div class="erp-field">
            <span class="erp-label">Очікується:</span>
            <el-date-picker v-model="form.expected_date" type="date" size="small" value-format="YYYY-MM-DD" placeholder="Планова" style="width:145px" />
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
            <div class="tab-toolbar">
              <el-button size="small" class="erp-btn" @click="addLine">Додати</el-button>
              <div class="tab-toolbar-right">
                <span class="erp-label">Склад:</span>
                <el-select v-model="form.warehouse_id" size="small" class="warehouse-select">
                  <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
                </el-select>
              </div>
            </div>
            <div class="erp-table-wrapper" v-loading="loading">
              <el-table :data="form.lines" border size="small" class="erp-dense-table" height="100%">
                <el-table-column type="index" label="N" width="40" align="center" />
                <el-table-column label="Номенклатура" min-width="260">
                  <template #default="scope">
                    <el-select v-model="scope.row.product_id" filterable size="small" placeholder="" class="erp-cell-input"
                      @change="(val) => handleProductChange(val, scope.row)">
                      <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="К-ть" width="100">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.quantity" :min="0.001" :precision="3"
                      :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="Ціна" width="110">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.price" :min="0" :precision="2"
                      :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="110">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.total" :min="0" :precision="2"
                      :controls="false" @change="updateLinePrice(scope.row)" class="erp-cell-input num sum-input" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="" width="40" align="center" fixed="right">
                  <template #default="scope">
                    <el-button type="danger" :icon="Delete" link size="small" @click="removeLine(scope.$index)"
                      style="padding:0;height:auto;" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="items-comment">
              <el-input v-model="form.comment" type="textarea" :autosize="{ minRows: 2, maxRows: 3 }"
                placeholder="Коментар до замовлення..." class="erp-comment-input" />
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
                  <label class="field-label">Очікувана дата отримання</label>
                  <el-date-picker v-model="delivery.expected_date" type="date" size="small"
                    value-format="YYYY-MM-DD" style="width:100%" />
                </div>
                <div class="field-block">
                  <label class="field-label">Вартість доставки (₴)</label>
                  <el-input-number v-model="delivery.cost" :min="0" :precision="2"
                    :controls="false" size="small" style="width:100%" />
                </div>
              </div>
              <div class="fields-grid-2">
                <div class="field-block">
                  <label class="field-label">Контактна особа постачальника</label>
                  <el-input v-model="delivery.contact_name" size="small" placeholder="ПІБ" />
                </div>
                <div class="field-block">
                  <label class="field-label">Телефон</label>
                  <el-input v-model="delivery.contact_phone" size="small" placeholder="+380..." />
                </div>
              </div>
              <div class="field-block">
                <label class="field-label">Адреса отримання</label>
                <el-input v-model="delivery.address" type="textarea" :autosize="{ minRows: 2 }"
                  size="small" placeholder="Адреса складу для отримання товару..." />
              </div>
              <div class="field-block" v-if="delivery.method === 'np_branch'">
                <label class="field-label">Номер відділення НП</label>
                <el-input v-model="delivery.branch_number" size="small" placeholder="№ відділення" style="width:160px" />
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
                    <el-option value="card" label="Картка" />
                    <el-option value="bank_transfer" label="Банківський переказ" />
                    <el-option value="prepayment" label="Передоплата" />
                    <el-option value="postpay" label="Постоплата" />
                  </el-select>
                </div>
                <div class="field-block">
                  <label class="field-label">Оплатити до</label>
                  <el-date-picker v-model="payment.due_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:100%" />
                </div>
                <div class="field-block">
                  <label class="field-label">Статус оплати</label>
                  <div class="payment-status-badge" :class="paymentStatusClass">{{ paymentStatusLabel }}</div>
                </div>
              </div>
              <div class="payment-summary-box">
                <div class="ps-row"><span>Сума замовлення:</span><span>{{ formatCurrency(totalAmount) }}</span></div>
                <div class="ps-row"><span>Доставка:</span><span>{{ formatCurrency(delivery.cost) }}</span></div>
                <div class="ps-divider"></div>
                <div class="ps-row ps-row--bold"><span>Всього до оплати:</span><span>{{ formatCurrency(totalAmount + delivery.cost) }}</span></div>
                <div class="ps-divider"></div>
                <div class="ps-row"><span>Сплачено:</span><span class="text-green">{{ formatCurrency(paidAmount) }}</span></div>
                <div class="ps-row">
                  <span>Залишок:</span>
                  <span :class="remainingAmount > 0 ? 'text-red' : 'text-green'">{{ formatCurrency(remainingAmount) }}</span>
                </div>
              </div>
              <div v-if="payment.records.length > 0" class="payments-list">
                <div class="payments-list-title">Історія платежів</div>
                <el-table :data="payment.records" size="small" border>
                  <el-table-column prop="date" label="Дата" width="110" />
                  <el-table-column prop="method_label" label="Спосіб" />
                  <el-table-column label="Сума" align="right" width="120">
                    <template #default="s">{{ formatCurrency(s.row.amount) }}</template>
                  </el-table-column>
                  <el-table-column label="Статус" width="110" align="center">
                    <template #default="s">
                      <el-tag size="small" :type="s.row.status === 'completed' ? 'success' : 'warning'">
                        {{ s.row.status === 'completed' ? 'Виконано' : 'Очікує' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <el-button v-if="remainingAmount > 0" size="small" class="erp-btn" :icon="Plus"
                @click="showAddPaymentDialog = true" style="margin-top:12px">Додати платіж</el-button>
            </div>
          </el-tab-pane>

          <!-- TAB: Документи -->
          <el-tab-pane name="documents">
            <template #label>
              <el-icon><Document /></el-icon>&nbsp;Документи
              <el-badge v-if="orderDocs.length" :value="orderDocs.length" class="tab-badge" />
            </template>
            <div class="tab-content-card">
              <div class="docs-actions">
                <el-button size="small" class="erp-btn" :icon="Van" @click="createReceipt">Прибуткова накладна</el-button>
                <el-button size="small" class="erp-btn" :icon="Document" @click="createSupplierInvoice">Рахунок від постачальника</el-button>
              </div>
              <div v-if="orderDocs.length === 0" class="empty-state">
                <el-icon size="40" color="#cbd5e1"><Document /></el-icon>
                <p>Документи ще не створені</p>
              </div>
              <div v-else class="docs-list">
                <div v-for="doc in orderDocs" :key="doc.id" class="doc-item">
                  <el-icon size="24" :color="doc.type === 'receipt' ? '#10b981' : '#f59e0b'">
                    <component :is="doc.type === 'receipt' ? Van : Document" />
                  </el-icon>
                  <div class="doc-info">
                    <span class="doc-name">{{ doc.type === 'receipt' ? 'Прибуткова накладна' : 'Рахунок від постачальника' }}</span>
                    <span class="doc-meta">№ {{ doc.number }} від {{ doc.date }}</span>
                  </div>
                  <el-tag size="small" :type="doc.status === 'issued' ? 'primary' : 'info'">
                    {{ doc.status === 'issued' ? 'Виписано' : 'Чернетка' }}
                  </el-tag>
                  <el-button size="small" :icon="View" circle class="erp-btn-icon" />
                  <el-button size="small" :icon="Printer" circle class="erp-btn-icon" />
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- TAB: Історія -->
          <el-tab-pane name="history">
            <template #label><el-icon><Timer /></el-icon>&nbsp;Історія</template>
            <div class="tab-content-card" style="padding:0">
              <div class="empty-state">
                <el-icon size="40" color="#cbd5e1"><Timer /></el-icon>
                <p>{{ isEditMode ? 'Журнал змін (в розробці)' : 'Збережіть замовлення щоб бачити історію' }}</p>
              </div>
            </div>
          </el-tab-pane>

        </el-tabs>
      </div>

      <!-- ===== SIDEBAR ===== -->
      <div class="order-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">Підсумки замовлення</div>
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
            <el-button size="small" class="qa-btn" @click="activeTab = 'delivery'">
              <el-icon><Van /></el-icon> Заповнити доставку
            </el-button>
            <el-button size="small" class="qa-btn" @click="createReceipt">
              <el-icon><Document /></el-icon> Прибуткова накладна
            </el-button>
            <el-button size="small" class="qa-btn" @click="handlePrint">
              <el-icon><Printer /></el-icon> Друк замовлення
            </el-button>
            <el-button size="small" class="qa-btn" @click="handleSendToSupplier" :disabled="!selectedSupplierObj">
              <el-icon><Promotion /></el-icon> Надіслати постачальнику
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== ADD PAYMENT DIALOG ===== -->
    <el-dialog v-model="showAddPaymentDialog" title="Додати платіж" width="380px">
      <el-form label-width="130px" size="small">
        <el-form-item label="Сума платежу">
          <el-input-number v-model="newPaymentAmount" :min="0" :max="remainingAmount"
            :precision="2" :controls="false" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPaymentDialog = false">Скасувати</el-button>
        <el-button type="primary" @click="addPayment">Додати</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, Plus, Delete, ArrowDown, ArrowUp, MoreFilled,
  Printer, Promotion, Download, Phone, Message, Location,
  Box, Van, CreditCard, Document, Timer, View
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// ===== STATE =====
const loading = ref(false)
const submitting = ref(false)
const isEditMode = computed(() => !!route.params.id && route.params.id !== 'new')
const activeTab = ref('items')
const isHeaderExpanded = ref(true)

const delivery = reactive({
  method: 'self',
  expected_date: null,
  cost: 0,
  contact_name: '',
  contact_phone: '',
  address: '',
  branch_number: ''
})

const payment = reactive({
  method: 'bank_transfer',
  due_date: null,
  records: []
})
const showAddPaymentDialog = ref(false)
const newPaymentAmount = ref(0)
const orderDocs = ref([])

const form = reactive({
  order_number: 'Авто',
  order_date: new Date().toISOString().split('T')[0],
  expected_date: null,
  supplier_id: '',
  warehouse_id: '',
  comment: '',
  currency: 'UAH',
  status: 'draft',
  lines: []
})

const suppliers = ref([])
const warehouses = ref([])
const products = ref([])

// ===== COMPUTED =====
const subtotal = computed(() => form.lines.reduce((acc, line) => acc + (line.total || 0), 0))
const totalAmount = computed(() => subtotal.value)
const totalQty = computed(() => form.lines.reduce((sum, l) => sum + (l.quantity || 0), 0))

const paidAmount = computed(() =>
  payment.records.filter(r => r.status === 'completed').reduce((sum, r) => sum + r.amount, 0)
)
const remainingAmount = computed(() =>
  Math.max(0, totalAmount.value + delivery.cost - paidAmount.value)
)

const paymentStatusClass = computed(() => {
  if (remainingAmount.value <= 0) return 'ps-badge--green'
  if (paidAmount.value > 0) return 'ps-badge--amber'
  return 'ps-badge--red'
})

const paymentStatusLabel = computed(() => {
  if (remainingAmount.value <= 0) return 'Оплачено повністю'
  if (paidAmount.value > 0) return 'Частково оплачено'
  return 'Не оплачено'
})

const selectedSupplierObj = computed(() =>
  suppliers.value.find(s => s.id === form.supplier_id) || null
)

const statusBadgeClass = computed(() => ({
  draft: 'status-draft',
  confirmed: 'status-confirmed',
  done: 'status-done',
  cancelled: 'status-cancelled'
}[form.status] || 'status-draft'))

const statusLabel = computed(() => ({
  draft: 'Чернетка',
  confirmed: 'Підтверджено',
  done: 'Виконано',
  cancelled: 'Скасовано'
}[form.status] || form.status))

// ===== ACTIONS =====
const goBack = () => router.push('/purchases/orders')

const handleCreateBasedOn = (command) => {
  if (command === 'receipt') ElMessage.info('Створення Прибуткової накладної (в розробці)')
  if (command === 'payment') ElMessage.info('Створення Вихідного платежу (в розробці)')
}

const handlePrint = () => ElMessage.info('Друк замовлення (в розробці)')

const handleSendToSupplier = () => {
  const s = selectedSupplierObj.value
  if (!s?.email) { ElMessage.warning('У постачальника не вказано email'); return }
  ElMessage.success(`Email надіслано на ${s.email}`)
}

const handleExportExcel = () => ElMessage.info('Експорт в Excel (в розробці)')

const createReceipt = () => {
  const num = `ПН-${form.order_number || Date.now()}`
  orderDocs.value.push({ id: Date.now(), type: 'receipt', number: num, date: new Date().toISOString().split('T')[0], status: 'draft' })
  activeTab.value = 'documents'
  ElMessage.success(`Накладна ${num} створена`)
}

const createSupplierInvoice = () => {
  const num = `РХ-${form.order_number || Date.now()}`
  orderDocs.value.push({ id: Date.now(), type: 'invoice', number: num, date: new Date().toISOString().split('T')[0], status: 'issued' })
  activeTab.value = 'documents'
  ElMessage.success(`Рахунок ${num} створено`)
}

const addPayment = () => {
  if (!newPaymentAmount.value || newPaymentAmount.value <= 0) { ElMessage.error('Введіть суму'); return }
  const methodLabels = { cash: 'Готівка', card: 'Картка', bank_transfer: 'Банківський переказ', prepayment: 'Передоплата', postpay: 'Постоплата' }
  payment.records.push({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    amount: newPaymentAmount.value,
    method_label: methodLabels[payment.method] || payment.method,
    status: 'completed'
  })
  ElMessage.success(`Платіж ${formatCurrency(newPaymentAmount.value)} додано`)
  newPaymentAmount.value = 0
  showAddPaymentDialog.value = false
}

const onSupplierChange = (supplierId) => {
  const supplier = suppliers.value.find(s => s.id === supplierId)
  if (supplier) {
    if (supplier.address && !delivery.address) delivery.address = supplier.address
    if (supplier.phone && !delivery.contact_phone) delivery.contact_phone = supplier.phone
  }
}

// ===== LINE OPERATIONS =====
const addLine = () => {
  form.lines.push({ product_id: '', quantity: 1, price: 0, total: 0 })
}

const removeLine = (index) => {
  form.lines.splice(index, 1)
}

const updateLineTotal = (line) => {
  line.total = parseFloat((line.quantity * line.price).toFixed(2))
}

const updateLinePrice = (line) => {
  if (line.quantity > 0) line.price = parseFloat((line.total / line.quantity).toFixed(2))
}

const handleProductChange = (productId, line) => {
  const product = products.value.find(p => p.id === productId)
  if (product) {
    line.price = product.price || 0
    updateLineTotal(line)
  }
}

// ===== DATA FETCHING =====
const fetchData = async () => {
  loading.value = true
  try {
    const [supRes, whRes, prodRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products')
    ])
    suppliers.value = supRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data

    if (isEditMode.value) {
      const res = await api.get(`/api/v1/purchase-orders/${route.params.id}`)
      const data = res.data
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
const saveOrder = async (action = 'save') => {
  if (!form.supplier_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля та додайте товари")
    return
  }

  if ((action === 'post' || action === 'post_close') && form.status === 'draft') {
    form.status = 'confirmed'
  }

  const payload = {
    ...form,
    lines: form.lines.map(l => ({
      product_id: l.product_id,
      quantity: l.quantity,
      price: l.price,
      total: l.total
    })),
    total_amount: totalAmount.value,
    expected_date: form.expected_date || null,
    comment: form.comment || null
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/purchase-orders/${route.params.id}`, payload)
      ElMessage.success('Замовлення оновлено')
      if (action === 'post_close') router.push('/purchases/orders')
      else await fetchData()
    } else {
      const res = await api.post('/api/v1/purchase-orders', payload)
      ElMessage.success('Замовлення створено')
      if (action === 'post_close') router.push('/purchases/orders')
      else router.push(`/purchases/orders/${res.data.id}`)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    submitting.value = false
  }
}

// ===== HELPERS =====
const formatCurrency = (val) =>
  new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)

onMounted(fetchData)
</script>

<style scoped>
.erp-page-container {
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
  background-color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif;
}

/* ===== TOOLBAR ===== */
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
.erp-btn:hover, .erp-btn-icon:hover { background-color: #f5f7fa !important; border-color: #c0c4cc !important; }
.erp-btn-primary {
  background-color: #eef2ff !important; border-color: #6366f1 !important;
  color: #4338ca !important; font-weight: 600 !important;
}
.erp-btn-primary:hover { background-color: #e0e7ff !important; }
.erp-btn-icon { padding: 0 8px !important; }
.erp-doc-info { margin-left: 16px; }
.erp-doc-title { font-size: 14px; font-weight: 600; color: #303133; }

/* ===== HEADER FIELDS ===== */
.erp-header-fields {
  background-color: #f6f7f9; padding: 10px 16px 8px 16px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid #e4e7ed;
}
.erp-field-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.erp-field { display: flex; align-items: center; }
.erp-label { font-size: 15px; color: #374151; padding-right: 8px; white-space: nowrap; font-weight: 500; }
.erp-label.req::after { content: ' *'; color: #f56c6c; }
.erp-input-wrapper { width: 160px; }
.client-select { width: 320px; }
.erp-header-fields :deep(.el-input__wrapper), .erp-header-fields :deep(.el-select__wrapper) {
  border-radius: 4px !important; box-shadow: none !important; border: 1px solid #d1d5db !important;
  background-color: #fff !important; min-height: 30px !important; height: 30px !important; padding: 0 10px !important;
}
.erp-header-fields :deep(.el-input__inner) {
  height: 28px !important; line-height: 28px !important; font-size: 15px !important; color: #111827 !important;
}
.erp-badges-group { display: flex; align-items: center; gap: 8px; margin-left: auto; }

/* Status pills */
.erp-status-pill {
  display: inline-flex; align-items: center; padding: 3px 12px;
  border-radius: 12px; font-size: 12px; font-weight: 600; border: 1px solid;
}
.status-draft { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.status-confirmed { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
.status-done { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }
.status-cancelled { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }

/* Supplier info banner */
.client-info-banner {
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;
  padding: 6px 12px; font-size: 12px; color: #0369a1; margin-top: 4px;
}
.client-info-item { display: flex; align-items: center; gap: 4px; }

/* ===== MAIN BODY ===== */
.order-body { flex: 1; display: flex; overflow: hidden; }
.order-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

/* ===== TABS ===== */
.order-tabs { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.order-tabs :deep(.el-tabs__header) {
  margin: 0; background: #fff; padding: 0 12px;
  border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.order-tabs :deep(.el-tabs__item) { font-size: 13px; height: 38px; }
.order-tabs :deep(.el-tabs__item.is-active) { color: #6366f1; font-weight: 600; }
.order-tabs :deep(.el-tabs__active-bar) { background-color: #6366f1; }
.order-tabs :deep(.el-tabs__content) { flex: 1; overflow: auto; padding: 0; }
.order-tabs :deep(.el-tab-pane) { display: flex; flex-direction: column; height: 100%; }
.tab-badge { margin-left: 4px; }

/* Tab toolbar */
.tab-toolbar {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px;
  background: #f6f7f9; border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.tab-toolbar-right { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.warehouse-select { width: 200px; }

/* ===== TABLE ===== */
.erp-table-wrapper { flex: 1; overflow: hidden; }
.erp-dense-table { width: 100%; border: 1px solid #dcdfe6 !important; }
.erp-dense-table :deep(th.el-table__cell) {
  background-color: #f5f7fa !important; color: #606266; font-size: 12px;
  font-weight: 600; padding: 4px 0 !important;
  border-bottom: 1px solid #dcdfe6 !important; border-right: 1px solid #dcdfe6 !important;
}
.erp-dense-table :deep(td.el-table__cell) {
  padding: 0 !important; border-bottom: 1px solid #ebeef5 !important; border-right: 1px solid #ebeef5 !important;
}
.erp-dense-table :deep(.cell) { padding: 0 6px !important; line-height: 24px !important; }
.erp-cell-input { width: 100%; }
.erp-cell-input :deep(.el-input__wrapper), .erp-cell-input :deep(.el-select__wrapper) {
  box-shadow: none !important; border: 1px solid transparent !important;
  background-color: transparent !important; padding: 0 4px !important;
  border-radius: 2px !important; min-height: 24px !important; height: 24px !important;
}
.erp-cell-input :deep(.el-input__wrapper:focus-within), .erp-cell-input :deep(.el-input__wrapper:hover) {
  border-color: #dcdfe6 !important; background-color: #fff !important;
}
.erp-cell-input :deep(.el-input__inner) { font-size: 13px !important; height: 22px !important; line-height: 22px !important; }
.erp-cell-input.num :deep(.el-input__inner) { text-align: right !important; }
.items-comment { padding: 8px 12px; background: #f6f7f9; border-top: 1px solid #e4e7ed; flex-shrink: 0; }
.erp-comment-input :deep(.el-textarea__inner) {
  border-radius: 2px; border: 1px solid #dcdfe6; font-size: 13px; padding: 6px;
}

/* Tab content card */
.tab-content-card { padding: 16px; display: flex; flex-direction: column; gap: 14px; max-width: 900px; }
.fields-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.fields-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.field-block { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 12px; color: #606266; font-weight: 500; }
.mt-1 { margin-top: 4px; }

/* ===== PAYMENT ===== */
.payment-status-badge {
  display: inline-flex; align-items: center; padding: 4px 12px;
  border-radius: 20px; font-size: 12px; font-weight: 500;
}
.ps-badge--green { background: #d1fae5; color: #065f46; }
.ps-badge--amber { background: #fef3c7; color: #92400e; }
.ps-badge--red { background: #fee2e2; color: #991b1b; }
.payment-summary-box {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
  padding: 12px 16px; display: flex; flex-direction: column; gap: 6px; max-width: 400px;
}
.ps-row { display: flex; justify-content: space-between; font-size: 13px; }
.ps-row--bold { font-weight: 600; }
.ps-divider { height: 1px; background: #e2e8f0; margin: 2px 0; }
.text-green { color: #059669; }
.text-red { color: #dc2626; }
.payments-list-title { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; }

/* ===== DOCUMENTS ===== */
.docs-actions { display: flex; gap: 8px; }
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; padding: 40px; color: #94a3b8; font-size: 13px;
}
.docs-list { display: flex; flex-direction: column; gap: 8px; }
.doc-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border: 1px solid #e2e8f0; border-radius: 8px; background: #fff;
}
.doc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.doc-name { font-size: 13px; font-weight: 500; color: #1e293b; }
.doc-meta { font-size: 11px; color: #94a3b8; }

/* ===== SIDEBAR ===== */
.order-sidebar {
  width: 280px; flex-shrink: 0; background: #fff; border-left: 1px solid #e4e7ed;
  overflow-y: auto; display: flex; flex-direction: column;
}
.sidebar-card { padding: 14px 16px; border-bottom: 1px solid #f0f2f5; }
.sidebar-card-title {
  font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 1px solid #e4e7ed;
}
.summary-rows { display: flex; flex-direction: column; gap: 5px; margin-bottom: 4px; }
.sum-row { display: flex; justify-content: space-between; font-size: 12px; color: #606266; }
.sum-row--total { font-size: 14px; font-weight: 700; color: #1e293b; margin-top: 2px; }
.total-value { color: #6366f1; }
.sum-divider { height: 1px; background: #e4e7ed; margin: 3px 0; }

/* Quick actions */
.quick-actions { display: flex; flex-direction: column; gap: 6px; }
.qa-btn {
  width: 100%; justify-content: flex-start !important; text-align: left;
  height: 30px !important; font-size: 12px !important; margin-left: 0 !important;
  background: #f8fafc !important; border-color: #e2e8f0 !important; color: #374151 !important;
}
.qa-btn:hover { background: #f0f9ff !important; border-color: #bae6fd !important; color: #0369a1 !important; }
</style>
