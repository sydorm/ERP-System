<template>
  <div class="crm-order-page min-h-screen bg-[#F4F6F9] font-inter text-[#1F2937] antialiased">

    <!-- ─── COMPACT STICKY HEADER ─── -->
    <header class="sticky top-0 z-[1020] bg-white border-b border-gray-100 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div class="flex items-center h-[50px] px-8 gap-5">

        <!-- Left: back + title -->
        <div class="flex items-center gap-2.5 flex-shrink-0">
          <button @click="router.back()"
                  class="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all flex-shrink-0">
            <el-icon class="text-sm"><ArrowLeft /></el-icon>
          </button>
          <div class="leading-none">
            <div class="text-[13px] font-bold text-gray-800 leading-tight">
              {{ orderId ? 'Редагування' : 'Нове замовлення' }}
            </div>
            <div class="text-[10px] text-gray-400 leading-none mt-0.5">CRM · Угоди</div>
          </div>
        </div>

        <div class="w-px h-5 bg-gray-200 flex-shrink-0"></div>

        <!-- Center: stepper -->
        <div class="hidden md:flex items-center flex-1 justify-center gap-0">
          <template v-for="(step, idx) in ['Клієнт', 'Товар', 'Логістика', 'Підтвердження']" :key="idx">
            <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg select-none"
                 :class="currentStep >= idx ? 'text-blue-600' : 'text-gray-400'">
              <div class="w-[18px] h-[18px] rounded-full flex items-center justify-center text-[10px] font-black flex-shrink-0 transition-all"
                   :class="{
                     'bg-emerald-500 text-white': currentStep > idx,
                     'bg-blue-600 text-white shadow-[0_2px_6px_rgba(37,99,235,0.4)]': currentStep === idx,
                     'bg-gray-100 text-gray-400': currentStep < idx
                   }">
                <el-icon v-if="currentStep > idx" style="font-size:9px"><Check /></el-icon>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <span class="text-[11.5px] font-semibold leading-none">{{ step }}</span>
            </div>
            <div v-if="idx < 3"
                 class="w-8 h-px flex-shrink-0 transition-colors rounded-full"
                 :class="currentStep > idx ? 'bg-emerald-300' : 'bg-gray-200'"></div>
          </template>
        </div>

        <!-- Right: progress ring + order id -->
        <div class="flex items-center gap-3 flex-shrink-0 ml-auto">
          <div class="flex items-center gap-2">
            <div class="w-[72px] h-[3px] bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full bg-blue-500 rounded-full transition-all duration-700"
                   :style="`width:${readinessData.progress}%`"></div>
            </div>
            <span class="text-[11px] font-bold text-gray-400 w-8 text-right">{{ readinessData.progress }}%</span>
          </div>
          <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-gray-50 border border-gray-200 text-[10px] font-black text-gray-400 tracking-widest">
            #{{ orderId ? String(orderId).slice(-6).toUpperCase() : 'NEW' }}
          </span>
        </div>

      </div>
    </header>

    <!-- ─── MAIN WORKSPACE ─── -->
    <main class="px-8 pt-5 pb-8 grid grid-cols-1 lg:grid-cols-12 gap-5">

      <!-- LEFT: forms (8/12) -->
      <div class="lg:col-span-8 space-y-4">

        <!-- CARD 1: Client & Logistics -->
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden relative">
          <div class="absolute left-0 top-0 w-[3px] h-full transition-colors duration-500 rounded-l-xl"
               :class="readinessData.items[0].done ? 'bg-blue-500' : 'bg-gray-200'"></div>
          <div class="pl-5 pr-5 pt-4 pb-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-[13.5px] font-bold flex items-center gap-2 text-gray-800">
                <el-icon class="text-blue-500 text-sm"><User /></el-icon>
                Замовник та логістика
              </h2>
              <transition name="el-fade-in">
                <span v-if="form.counterparty_id"
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-100 text-[10px] font-bold text-emerald-600">
                  <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                  Контакт обрано
                </span>
              </transition>
            </div>
            <CrmClientBlock
              :form="form"
              :v-errors="vErrors"
              :counterparties="counterparties"
              :lead-sources="leadSources"
              :delivery-methods="deliveryMethods"
              :manager-options="users"
              :can-reassign-manager="true"
              @counterparty-change="onClientChange"
              @new-client="openCreateCounterparty"
            />
          </div>
        </div>

        <!-- CARD 2: Product -->
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden relative">
          <div class="absolute left-0 top-0 w-[3px] h-full transition-colors duration-500 rounded-l-xl"
               :class="readinessData.items[1].done ? 'bg-blue-500' : 'bg-gray-200'"></div>
          <div class="pl-5 pr-5 pt-4 pb-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-[13.5px] font-bold flex items-center gap-2 text-gray-800">
                <el-icon class="text-blue-500 text-sm"><Box /></el-icon>
                Конфігурація замовлення
              </h2>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Крок 2</span>
            </div>
            <CrmProductBlock
              :form="form"
              :products="products"
              :product-attributes="productAttributes"
              @product-change="onProductChange"
              @set-attr-value="setAttrValue"
              @set-attr-dim="setAttrDim"
              @upload-photo="handlePhotoUpload"
            />
          </div>
        </div>

        <!-- Finalization -->
        <CrmFinalizationBlock
          :form="form"
          :base-price="selectedProductPrice"
          :priorities="priorities"
          :format-currency="formatCurrency"
          :format-date="formatDate"
          @set-prepay-pct="setPrepayPercent"
          @update-total="val => form.total_amount = val"
        />

      </div>

      <!-- RIGHT: sidebar (4/12) -->
      <div class="lg:col-span-4">
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 sticky top-[62px]">
          <CrmReadinessChecklist
            :progress="readinessData.progress"
            :items="readinessData.items"
          />
        </div>
      </div>

    </main>

    <!-- ─── STICKY FOOTER ─── -->
    <footer class="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-t border-gray-100 px-8 py-2.5 z-[1030] shadow-[0_-1px_6px_rgba(0,0,0,0.06)]">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Сума:</span>
          <span class="text-[15px] font-black text-blue-600">{{ formatCurrency(form.total_amount) }} ₴</span>
        </div>
        <div class="flex items-center gap-2.5">
          <button @click="save('draft')"
                  class="px-5 py-[7px] rounded-lg border border-gray-200 text-gray-600 font-semibold text-[12px] hover:bg-gray-50 transition-colors">
            Чернетка
          </button>
          <button @click="save('production')" :disabled="saving"
                  class="px-7 py-[7px] rounded-lg bg-blue-600 text-white font-bold text-[12px] shadow-md shadow-blue-200 hover:bg-blue-700 disabled:opacity-50 transition-all active:scale-95">
            {{ orderId ? 'Оновити замовлення' : 'Створити замовлення' }}
          </button>
        </div>
      </div>
    </footer>

    <CrmNewClientDialog
      v-model="cpDialogVisible"
      :loading="creatingCp"
      @create="createCounterparty"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

// Modular components
import CrmOrderHeader from './components/CrmOrderHeader.vue'
import CrmClientBlock from './components/CrmClientBlock.vue'
import CrmProductBlock from './components/CrmProductBlock.vue'
import CrmFinalizationBlock from './components/CrmFinalizationBlock.vue'
import CrmReadinessChecklist from './components/CrmReadinessChecklist.vue'
import CrmNewClientDialog from './components/CrmNewClientDialog.vue'

const router = useRouter()
const route = useRoute()

const orderId = computed(() => {
  const id = route.params.id
  return (id && id !== 'new') ? id : null
})

// MASTER STATE
const loading = ref(true)
const saving = ref(false)
const vErrors = reactive({ client: false })
const form = reactive({
  counterparty_id: null,
  client_name: '',
  client_phone: '',
  lead_source_id: null,
  order_number: '',
  product_id: null,
  crm_stage: 'new',
  city: '',
  delivery_method_id: null,
  attributes_values: {},
  base_price: 0,
  manual_price: null,
  price_override_reason: '',
  discount_percent: 0,
  discount_amount: 0,
  discount_reason: '',
  total_amount: 0,
  prepayment_amount: 0,
  payment_status: 'unpaid',
  deadline_date: null,
  comment: '',
  production_comment: '',
  next_contact_at: null,
  next_contact_comment: '',
  priority: 'normal'
})

// Data sets
const products = ref([])
const counterparties = ref([])
const leadSources = ref([])
const deliveryMethods = ref([])
const users = ref([])
const productAttributes = ref([])
const materials = ref([])
const bankAccounts = ref([])
const contactHistory = ref([])
const checkingMaterials = ref(false)

const stages = [
  { key: 'new', label: 'НОВІ' },
  { key: 'payment', label: 'ОПЛАТА' },
  { key: 'processing', label: 'В РОБОТІ' },
  { key: 'production', label: 'ВИРОБНИЦТВО' },
  { key: 'done', label: 'ВИКОНАНО' }
]

const priorities = ref([
  { value: 'low', label: 'Низький', color: '#94A3B8' },
  { value: 'normal', label: 'Нормальний', color: '#6366F1' },
  { value: 'high', label: 'Високий', color: '#F59E0B' },
  { value: 'critical', label: 'Критичний', color: '#EF4444' }
])

// Contact Logic
const commTypes = ref([{ code: 'CALL', name: 'Дзвінок', icon: '📞' }, { code: 'CHAT', name: 'Месенджер', icon: '💬' }])
const contactResults = ref([{ code: 'CONFIRMED', name: 'Підтвердив' }, { code: 'THINKING', name: 'Думає' }, { code: 'NO_ANSWER', name: 'Не взяв' }, { code: 'REFUSED', name: 'Відмова' }])
const contactResult = ref(null)
const contactCommType = ref('CALL')
const contactPlanReason = ref('first_touch')
const contactNextAt = ref(null)
const contactNote = ref('')
const savingContact = ref(false)

// Computed
const autoPaymentStatus = computed(() => {
  if (form.prepayment_amount >= form.total_amount && form.total_amount > 0) return { key: 'paid', label: 'Оплачено' }
  if (form.prepayment_amount > 0) return { key: 'partial', label: 'Часткова оплата' }
  return { key: 'unpaid', label: 'Очікує оплати' }
})

const nextTouchSummary = computed(() => form.next_contact_at ? `Наступний контакт: ${new Date(form.next_contact_at).toLocaleString()}` : 'Не заплановано')

const selectedProductPrice = computed(() => {
  const p = products.value.find(p => String(p.id) === String(form.product_id))
  return p ? p.price : 0
})

const currentStep = computed(() => {
  if (readinessData.value.progress < 25) return 0
  if (readinessData.value.progress < 50) return 1
  if (readinessData.value.progress < 75) return 2
  return 3
})

const readinessData = computed(() => {
  const items = [
    { key: 'client', label: 'Дані замовника', done: !!form.counterparty_id },
    { key: 'product', label: 'Виріб обрано', done: !!form.product_id },
    { key: 'finance', label: 'Фінанси', done: form.total_amount > 0 },
    { key: 'deadline', label: 'Терміни', done: !!form.deadline_date }
  ]
  const doneCount = items.filter(i => i.done).length
  const progress = Math.round((doneCount / items.length) * 100)
  return { items, progress }
})

const materialCheck = computed(() => ({
  items: materials.value || [],
  has_issues: (materials.value || []).some(m => m.status !== 'ok')
}))

// Methods
const isStagePast = (stageKey) => {
  const idx = stages.findIndex(s => s.key === stageKey)
  const currentIdx = stages.findIndex(s => s.key === form.crm_stage)
  return idx <= currentIdx
}

const setStage = (stage) => form.crm_stage = stage

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatDate = (val) => val ? new Date(val).toLocaleDateString('uk-UA') : '—'
const formatDateTime = (val) => val ? new Date(val).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'
const formatQty = (val) => Number(val || 0).toLocaleString('uk-UA', { maximumFractionDigits: 3 })

const onClientChange = async (id) => {
  if (!id) return
  const res = await api.get(`/api/v1/counterparties/${id}`)
  const c = res.data
  form.city = c.city || ''; form.client_phone = c.phone || ''; form.client_name = c.name || ''
  if (c.lead_source_id) form.lead_source_id = c.lead_source_id
}

const onProductChange = async (id) => {
  if (!id) return
  const res = await api.get(`/api/v1/products/${id}/attributes`)
  productAttributes.value = res.data; checkMaterials()
}

const checkMaterials = async () => {
  if (!form.product_id) return
  checkingMaterials.value = true
  try {
    const res = await api.get(`/api/v1/crm/orders/check-materials?product_id=${form.product_id}`)
    materials.value = res.data.items || []
  } finally { checkingMaterials.value = false }
}

const setAttrValue = (attrId, val) => {
  if (!form.attributes_values) form.attributes_values = {}
  form.attributes_values[attrId] = val
}

const setAttrDim = (attrId, key, val) => {
  if (!form.attributes_values[attrId]) form.attributes_values[attrId] = { w: 0, h: 0 }
  form.attributes_values[attrId][key] = val
}

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
}

const handleCalcPrepayment = () => {}
const handlePrepaymentInput = () => {}
const handlePrint = () => window.print()

const getResultHint = (code) => {
  const map = { CONFIRMED: 'Заявку підтверджено', THINKING: 'Потрібен повторний дотик', NO_ANSWER: 'Не взяв трубку', REFUSED: 'Клієнт відмовився' }
  return map[code] || ''
}

const handlePhotoUpload = (photo) => {
  if (!form.photos) form.photos = []
  form.photos.push(photo)
}

const handleContactPreset = (opts) => {
  const d = new Date()
  if (opts.minutes) d.setMinutes(d.getMinutes() + opts.minutes)
  if (opts.tomorrow) { d.setDate(d.getDate() + 1); d.setHours(opts.h || 10, 0, 0, 0) }
  if (opts.syncContactLog) contactNextAt.value = d.toISOString()
  else form.next_contact_at = d.toISOString()
}

const logContact = async () => {
  if (!orderId.value) return
  savingContact.value = true
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      note: contactNote.value, result: contactResult.value,
      communication_type: contactCommType.value, next_contact_at: contactNextAt.value
    })
    contactNote.value = ''; contactResult.value = null; loadContacts()
  } finally { savingContact.value = false }
}

// Comm History Helpers
const getContactResultColor = (res) => {
  const map = { CONFIRMED: '#10B981', THINKING: '#F59E0B', NO_ANSWER: '#64748B', REFUSED: '#EF4444' }
  return map[res] || '#64748B'
}
const getCommIcon = (type) => type === 'CALL' ? '📞' : '💬'
const getCommName = (type) => type === 'CALL' ? 'Дзвінок' : 'Месенджер'
const contactResultLabel = (res) => contactResults.value.find(r => r.code === res)?.name || res

const save = async (action) => {
  saving.value = true
  try {
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Збережено')
    if (!orderId.value) router.push(`/crm/orders/${res.data.id}`)
  } finally { saving.value = false }
}

const cpDialogVisible = ref(false); const creatingCp = ref(false)
const openCreateCounterparty = () => cpDialogVisible.value = true
const createCounterparty = async (data) => {
  creatingCp.value = true
  try {
    const res = await api.post('/api/v1/counterparties', { ...data, is_customer: true })
    counterparties.value.push(res.data); form.counterparty_id = res.data.id; cpDialogVisible.value = false
  } finally { creatingCp.value = false }
}

const loadData = async () => {
  loading.value = true
  try {
    const [p, ls, dm, u, ba, cp] = await Promise.all([
      api.get('/api/v1/products?limit=200'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] })),
      api.get('/api/v1/warehouses').catch(() => ({ data: [] })),
      api.get('/api/v1/users/colleagues'),
      api.get('/api/v1/bank-accounts').catch(() => ({ data: [] })),
      api.get('/api/v1/counterparties?limit=1000').catch(() => ({ data: [] }))
    ])
    products.value = p.data; leadSources.value = ls.data; deliveryMethods.value = dm.data; users.value = u.data; bankAccounts.value = ba.data; counterparties.value = cp.data
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}`)
      Object.assign(form, res.data)
      if (form.product_id) onProductChange(form.product_id)
      loadContacts()
    }
  } finally { loading.value = false }
}

const loadContacts = async () => {
  if (!orderId.value) return
  const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
  contactHistory.value = res.data
}

watch(() => form.prepayment_amount, (val) => {
  if (val >= form.total_amount && form.total_amount > 0) form.payment_status = 'paid'
  else if (val > 0) form.payment_status = 'partial'
  else form.payment_status = 'unpaid'
})

onMounted(loadData)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
.font-inter { font-family: 'Inter', sans-serif; }

.crm-order-page {
  padding-bottom: 64px;
}

.step-card-premium {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.02);
  border: 1px solid #F1F5F9;
  transition: all 0.2s ease;
}

.step-card-premium:hover {
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.side-widget-premium {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  padding: 4px;
  border: 1px solid #F1F5F9;
}

.readiness-box {
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F7FF 100%);
  border-color: #EEF2FF;
}

.ai-widget {
  background: linear-gradient(135deg, #F0FDFA 0%, #FFFFFF 100%);
  border-color: #CCFBF1;
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  border-radius: 12px !important;
  box-shadow: none !important;
  border: 1px solid #E5E7EB !important;
  background: #FFFFFF !important;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover), :deep(.el-select__wrapper:hover) {
  border-color: #2563EB !important;
}

:deep(.el-input__wrapper.is-focus), :deep(.el-select__wrapper.is-focus) {
  border-color: #2563EB !important;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
}

/* Timeline Custom Styles */
:deep(.comm-timeline) {
  margin-top: 16px;
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
:deep(.timeline-item) {
  display: flex;
  gap: 16px;
  position: relative;
}
:deep(.timeline-dot) {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
  box-shadow: 0 0 0 4px #fff;
  z-index: 2;
}
:deep(.timeline-content) {
  flex: 1;
  background: #F8FAFC;
  padding: 16px;
  border-radius: 20px;
  border: 1px solid #F1F5F9;
}
:deep(.timeline-header) {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
:deep(.timeline-channel) {
  font-weight: 800;
  font-size: 13px;
  color: #1E293B;
}
:deep(.timeline-time) {
  font-size: 11px;
  color: #94A3B8;
  font-weight: 600;
}
:deep(.timeline-res-badge) {
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  margin-right: 12px;
}
:deep(.timeline-note) {
  margin-top: 10px;
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
}
:deep(.timeline-manager) {
  font-size: 12px;
  color: #64748B;
  font-weight: 600;
}
:deep(.timeline-reminder) {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #E2E8F0;
  font-size: 12px;
  color: #6366F1;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
