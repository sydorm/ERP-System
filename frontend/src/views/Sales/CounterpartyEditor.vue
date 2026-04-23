<template>
  <div class="page-container">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <div class="name-section">
          <h2>{{ isEditMode ? form.name || 'Контрагент' : 'Новий контрагент' }}</h2>
          <div class="header-tags" v-if="isEditMode">
            <el-tag v-if="form.is_customer" type="success" size="small" round>Клієнт</el-tag>
            <el-tag v-if="form.is_supplier" type="warning" size="small" round>Постачальник</el-tag>
            <el-tag v-for="tag in (form.tags || [])" :key="tag" type="info" size="small" effect="plain" round>{{ tag }}</el-tag>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <template v-if="isEditMode">
          <el-button type="success" :icon="Plus" @click="createNewOrder">Нове замовлення</el-button>
          <el-button type="primary" @click="writeTelegram" plain>
            <el-icon><ChatDotRound /></el-icon> Telegram
          </el-button>
          <el-button type="info" @click="callPhone" plain>
            <el-icon><Phone /></el-icon> Зателефонувати
          </el-button>
        </template>
        
        <el-divider direction="vertical" />

        <el-button v-if="isEditMode" type="danger" @click="confirmDelete" plain>
          Видалити
        </el-button>
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveCounterparty">
          Зберегти
        </el-button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="editor-content" v-loading="loading">
      <el-tabs v-model="activeTab" class="cp-tabs">
        <!-- 1. General Information -->
        <el-tab-pane label="Загальна інформація" name="general">
          <div class="tab-content">
            <div class="form-grid">
              <!-- Left Column: Core and Supplier -->
              <div class="grid-col">
                <el-card shadow="never" class="form-card">
                  <template #header><span class="card-title">Основні дані</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <el-form-item label="Назва (коротка)" required>
                      <el-input v-model="form.name" placeholder="Наприклад: ТОВ 'Атлант'" />
                    </el-form-item>
                    <el-form-item label="Юридична назва">
                      <el-input v-model="form.legal_name" placeholder="Повна юридична назва" />
                    </el-form-item>
                    <el-form-item label="ЄДРПОУ / ІПН">
                      <el-input v-model="form.tax_id" placeholder="8 або 10 цифр" />
                    </el-form-item>
                    <div class="flags-box">
                      <el-form-item label="Це клієнт?">
                        <el-switch v-model="form.is_customer" />
                      </el-form-item>
                      <el-form-item label="Це постачальник?">
                        <el-switch v-model="form.is_supplier" />
                      </el-form-item>
                      <el-form-item label="Активний?">
                        <el-switch v-model="form.is_active" />
                      </el-form-item>
                    </div>
                  </el-form>
                </el-card>

                <!-- Supplier Block -->
                <el-card v-if="form.is_supplier" shadow="never" class="form-card mt-20">
                  <template #header><span class="card-title">Налаштування постачальника</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <div class="form-row">
                      <el-form-item label="Час доставки (днів)" class="flex-1">
                        <el-input-number v-model="form.delivery_days" :min="0" class="w-full" />
                      </el-form-item>
                      <el-form-item label="Мін. замовлення (грн)" class="flex-1">
                        <el-input-number v-model="form.min_order_amount" :min="0" class="w-full" />
                      </el-form-item>
                    </div>
                    <el-form-item label="Умови оплати">
                      <el-select v-model="form.payment_terms" placeholder="Оберіть умови..." class="w-full">
                        <el-option label="Передоплата" value="prepaid" />
                        <el-option label="Післяплата" value="postpaid" />
                        <el-option label="Відтермінування" value="deferred" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="Контактна особа">
                      <el-input v-model="form.contact_person" placeholder="ПІБ контактної особи" />
                    </el-form-item>
                    <el-form-item label="Матеріали">
                      <el-input v-model="form.supplied_materials" type="textarea" :rows="2" placeholder="Що постачає..." />
                    </el-form-item>
                  </el-form>
                </el-card>
              </div>

              <!-- Right Column: CRM and Logistics -->
              <div class="grid-col">
                <el-card shadow="never" class="form-card">
                  <template #header><span class="card-title">Контакти та CRM</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <div class="form-row">
                      <el-form-item label="Телефон" class="flex-1">
                        <el-input v-model="form.phone" placeholder="+380...">
                          <template #prefix><el-icon><Phone /></el-icon></template>
                        </el-input>
                      </el-form-item>
                      <el-form-item label="Email" class="flex-1">
                        <el-input v-model="form.email" placeholder="example@mail.com">
                          <template #prefix><el-icon><Message /></el-icon></template>
                        </el-input>
                      </el-form-item>
                    </div>
                    
                    <template v-if="form.is_customer">
                      <el-form-item label="Канал звернення">
                        <el-select v-model="form.acquisition_channel_id" placeholder="Оберіть канал..." class="w-full" clearable>
                          <el-option v-for="c in channels" :key="c.id" :label="c.name" :value="c.id" />
                        </el-select>
                      </el-form-item>
                      <div class="form-row">
                        <el-form-item label="Місто" class="flex-1">
                          <el-input v-model="form.city" placeholder="Місто..." />
                        </el-form-item>
                        <el-form-item label="Відділення НП" class="flex-1">
                          <el-input v-model="form.np_department" placeholder="Відділення..." />
                        </el-form-item>
                      </div>
                      <el-form-item label="Знижка %">
                        <el-input-number v-model="form.discount_percent" :min="0" :max="100" class="w-full" />
                      </el-form-item>
                      <el-form-item label="Теги">
                        <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="Теги клієнта" class="w-full">
                          <el-option v-for="t in tagOptions" :key="t.id" :label="t.name" :value="t.name" />
                        </el-select>
                      </el-form-item>
                    </template>

                    <el-form-item label="Нотатки">
                      <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="Додаткова інформація..." />
                    </el-form-item>
                  </el-form>
                </el-card>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 2. Sales History -->
        <el-tab-pane v-if="form.is_customer" label="Історія продажів" name="sales" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header-flex">
                  <span class="card-title">Замовлення</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="createNewOrder" plain>Нове замовлення</el-button>
                </div>
              </template>
              <el-table :data="salesOrders" style="width: 100%">
                <el-table-column prop="order_number" label="Номер" width="120" />
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.order_date) }}</template>
                </el-table-column>
                <el-table-column label="Виріб" min-width="200">
                  <template #default="{ row }">
                    <span class="product-info">{{ row.product_summary || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Статус" width="130">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small" effect="dark" class="u-status">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Оплата" width="120">
                  <template #default="{ row }">
                    <el-tag :type="row.payment_status === 'paid' ? 'success' : 'info'" size="small" plain>
                      {{ row.payment_status === 'paid' ? 'Оплачено' : 'Не оплачено' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="130" align="right">
                  <template #default="{ row }">
                    <strong>{{ formatCurrency(row.total_amount) }}</strong>
                  </template>
                </el-table-column>
                <el-table-column width="60" align="right">
                  <template #default="{ row }">
                    <el-button :icon="Right" circle size="small" @click="viewOrder(row)" />
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="salesOrders.length === 0" description="Немає замовлень" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 3. Purchase History -->
        <el-tab-pane v-if="form.is_supplier" label="Історія закупівель" name="purchases" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header><span class="card-title">Прибуткові накладні</span></template>
              <el-table :data="purchaseReceipts" style="width: 100%">
                <el-table-column prop="receipt_number" label="Номер" width="140" />
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.receipt_date) }}</template>
                </el-table-column>
                <el-table-column label="Статус" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="150" align="right">
                  <template #default="{ row }">
                    <strong>{{ formatCurrency(row.total_amount) }}</strong>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="purchaseReceipts.length === 0" description="Немає накладних" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 4. Finances -->
        <el-tab-pane label="Фінанси" name="finances" :disabled="!isEditMode">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Всього продажів</span>
                    <span class="f-value text-success">{{ formatCurrency(financeSummary.totalSales) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Всього закупівель</span>
                    <span class="f-value text-warning">{{ formatCurrency(financeSummary.totalPurchases) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Баланс (Сальдо)</span>
                    <span class="f-value" :class="financeSummary.balance >= 0 ? 'text-success' : 'text-danger'">
                      {{ formatCurrency(financeSummary.balance) }}
                    </span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-card shadow="never" class="form-card mt-20">
              <template #header><span class="card-title">Фінансові операції</span></template>
              <el-table :data="financeOperations" style="width: 100%">
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.date) }}</template>
                </el-table-column>
                <el-table-column prop="reference" label="Документ" width="140" />
                <el-table-column prop="type" label="Тип" width="160">
                  <template #default="{ row }">
                    <el-tag :type="row.type.includes('Продаж') ? 'success' : 'warning'" size="small" plain>{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="150" align="right">
                  <template #default="{ row }">
                    <strong :class="row.amount < 0 ? 'text-danger' : 'text-success'">
                      {{ formatCurrency(row.amount) }}
                    </strong>
                  </template>
                </el-table-column>
                <el-table-column label="Оплата">
                  <template #default="{ row }">
                    <el-tag :type="row.is_paid ? 'success' : 'danger'" size="small">
                      {{ row.is_paid ? 'Оплачено' : 'Очікується' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Phone, Message, Document, 
  ChatDotRound, Plus, Right 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id)

// Dictionary Data
const channels = ref([])
const tagOptions = ref([])

const form = reactive({
  id: null,
  name: '',
  legal_name: '',
  tax_id: '',
  is_customer: true,
  is_supplier: false,
  phone: '',
  email: '',
  address: '',
  default_contract: '',
  is_active: true,
  acquisition_channel_id: null,
  city: '',
  np_department: '',
  discount_percent: 0,
  notes: '',
  tags: [],
  delivery_days: 0,
  min_order_amount: 0,
  payment_terms: 'prepaid',
  contact_person: '',
  supplied_materials: ''
})

const salesOrders = ref([])
const purchaseReceipts = ref([])
const financeSummary = reactive({
  totalSales: 0,
  totalPurchases: 0,
  balance: 0
})

const financeOperations = computed(() => {
  const ops = []
  salesOrders.value.forEach(o => ops.push({
    id: o.id, date: o.order_date, reference: o.order_number, 
    type: 'Замовлення (Продаж)', amount: Number(o.total_amount), 
    is_paid: o.payment_status === 'paid', sort_date: new Date(o.order_date)
  }))
  purchaseReceipts.value.forEach(r => ops.push({
    id: r.id, date: r.receipt_date, reference: r.receipt_number, 
    type: 'Прибуткова накладна', amount: -Number(r.total_amount), 
    is_paid: r.status === 'done', sort_date: new Date(r.receipt_date)
  }))
  return ops.sort((a, b) => b.sort_date - a.sort_date)
})

// Methods
const goBack = () => router.push('/sales/counterparties')

const fetchCounterparty = async () => {
  if (!isEditMode.value) return
  loading.value = true
  try {
    const res = await api.get(`/api/v1/counterparties/${route.params.id}`)
    Object.assign(form, res.data)
    if (!form.tags) form.tags = []
    fetchSalesHistory()
    fetchPurchaseHistory()
  } catch (e) {
    ElMessage.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

const fetchDictionaries = async () => {
  try {
    const [cRes, tRes] = await Promise.all([
      api.get('/api/v1/dictionaries/LEAD_SOURCE'),
      api.get('/api/v1/dictionaries/CLIENT_TAG')
    ])
    channels.value = cRes.data || []
    tagOptions.value = tRes.data || []
  } catch (e) {}
}

const fetchSalesHistory = async () => {
  try {
    const res = await api.get('/api/v1/orders', { params: { counterparty_id: route.params.id } })
    salesOrders.value = res.data || []
    calculateFinance()
  } catch (e) {}
}

const fetchPurchaseHistory = async () => {
  try {
    const res = await api.get('/api/v1/purchase-receipts', { params: { supplier_id: route.params.id } })
    purchaseReceipts.value = res.data || []
    calculateFinance()
  } catch (e) {}
}

const calculateFinance = () => {
  financeSummary.totalSales = salesOrders.value.reduce((acc, o) => acc + Number(o.total_amount), 0)
  financeSummary.totalPurchases = purchaseReceipts.value.reduce((acc, r) => acc + Number(r.total_amount), 0)
  financeSummary.balance = financeSummary.totalSales - financeSummary.totalPurchases
}

const saveCounterparty = async () => {
  if (!form.name) return ElMessage.warning('Вкажіть назву')
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEditMode.value) {
      await api.put(`/api/v1/counterparties/${form.id}`, payload)
      ElMessage.success('Оновлено')
    } else {
      const res = await api.post('/api/v1/counterparties', payload)
      ElMessage.success('Створено')
      router.push(`/sales/counterparties/${res.data.id}`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Помилка')
  } finally {
    submitting.value = false
  }
}

const confirmDelete = async () => {
  try {
    await ElMessageBox.confirm('Видалити цього контрагента?', 'Увага', { type: 'warning' })
    await api.delete(`/api/v1/counterparties/${form.id}`)
    ElMessage.success('Видалено')
    goBack()
  } catch (e) {}
}

const writeTelegram = () => {
  if (!form.phone) return ElMessage.info('Вкажіть телефон')
  window.open(`https://t.me/${form.phone.replace(/\D/g, '')}`, '_blank')
}

const callPhone = () => {
  if (!form.phone) return ElMessage.info('Вкажіть телефон')
  window.location.href = `tel:${form.phone}`
}

const createNewOrder = () => router.push({ name: 'OrderEditor', query: { counterparty_id: form.id } })
const viewOrder = (order) => router.push(`/sales/orders/${order.id}`)

const formatDate = (d) => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatCurrency = (v) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(v || 0)

const getStatusLabel = (s) => ({
  'draft': 'ЧЕРНЕТКА', 'confirmed': 'ПІДТВЕРДЖЕНО', 'in_production': 'В РОБОТІ',
  'done': 'ГОТОВО', 'cancelled': 'СКАСОВАНО', 'shipped': 'ВІДВАНТАЖЕНО'
}[s] || s)

const getStatusType = (s) => ({
  'draft': 'info', 'confirmed': 'primary', 'in_production': 'warning',
  'done': 'success', 'shipped': 'success', 'cancelled': 'danger'
}[s] || 'info')

onMounted(() => {
  fetchDictionaries()
  fetchCounterparty()
})
</script>

<style scoped>
.page-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 15px 25px;
  background: white;
  border-bottom: 1px solid #edf2f7;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left { display: flex; align-items: center; gap: 15px; }
.name-section h2 { margin: 0; font-size: 20px; color: #1a202c; }
.header-tags { display: flex; gap: 6px; margin-top: 4px; }
.header-actions { display: flex; align-items: center; gap: 10px; }

.editor-content { flex: 1; overflow-y: auto; background: #f7fafc; }
.tab-content { padding: 25px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.form-card { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.card-title { font-weight: 700; color: #2d3748; }

.flags-box {
  display: flex; justify-content: space-between;
  background: #f8fafc; padding: 15px; border-radius: 8px; margin-top: 15px;
}

.mt-20 { margin-top: 20px; }
.w-full { width: 100%; }
.flex-1 { flex: 1; }
.form-row { display: flex; gap: 15px; }

.finance-card { border-radius: 12px; text-align: center; }
.f-stat { padding: 10px; }
.f-label { display: block; font-size: 12px; color: #718096; margin-bottom: 5px; }
.f-value { font-size: 20px; font-weight: 800; }

.text-success { color: #48bb78; }
.text-warning { color: #ed8936; }
.text-danger { color: #f56565; }

.u-status { font-weight: 700; letter-spacing: 0.5px; }
.product-info { font-size: 13px; color: #4a5568; }

@media (max-width: 1024px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
