<template>
  <div class="crm-order-page min-h-screen bg-[#F4F6F9] font-inter text-[#1F2937] antialiased">

    <!-- ─── 1. TOP STICKY HEADER (PREMIUM STYLE) ─── -->
    <div class="order-topbar-wrapper">
      <header class="order-topbar">
        <div class="flex items-center h-[58px] px-6 justify-between">
          
          <!-- Left: Back & Breadcrumbs -->
          <div class="flex items-center gap-4">
            <button @click="router.back()" class="text-gray-400 hover:text-[#6C63FF] transition-all transform hover:scale-110">
              <el-icon class="text-lg"><ArrowLeft /></el-icon>
            </button>
            <div class="flex flex-col leading-tight">
              <span class="text-[13px] font-bold text-gray-900 tracking-tight">{{ orderId ? 'Редагування' : 'Створення' }}</span>
              <span class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">CRM · Угоди</span>
            </div>
          </div>

          <!-- Center: CRM Stages (Premium) -->
          <div class="hidden lg:flex items-center gap-0">
            <template v-for="(s, idx) in stages" :key="s.key">
              <div 
                class="flex items-center gap-2.5 px-4 py-2 cursor-pointer transition-all group"
                @click="setStage(s.key)"
              >
                <div 
                  class="w-2 h-2 rounded-full transition-all duration-500"
                  :class="[
                    form.crm_stage === s.key ? 'bg-[#6C63FF] stage-glow' : '',
                    isStagePast(s.key) && form.crm_stage !== s.key ? 'bg-emerald-500' : 'bg-gray-200'
                  ]"
                ></div>
                <span 
                  class="text-[11px] font-black tracking-widest uppercase transition-colors"
                  :class="[
                    form.crm_stage === s.key ? 'text-[#6C63FF]' : 'text-gray-400 group-hover:text-gray-600',
                    isStagePast(s.key) && form.crm_stage !== s.key ? 'text-emerald-600' : ''
                  ]"
                >
                  {{ s.label }}
                </span>
              </div>
              <!-- Connector line -->
              <div v-if="idx < stages.length - 1" 
                   class="w-6 h-[2px] transition-colors duration-500"
                   :class="isStagePast(stages[idx+1].key) ? 'bg-emerald-500' : 'bg-gray-100'"></div>
            </template>
          </div>

          <!-- Right: Progress & Actions -->
          <div class="flex items-center gap-6">
            <!-- Readiness Pill Badge -->
            <div class="flex items-center px-3 py-1.5 rounded-full bg-[rgba(108,99,255,0.08)] border border-[rgba(108,99,255,0.2)]">
              <span class="text-[11px] font-black text-[#6C63FF] uppercase tracking-tighter">Готовність {{ readinessData.progress }}%</span>
            </div>

            <!-- Buttons -->
            <div class="flex items-center gap-3">
              <button 
                @click="save('draft')"
                class="px-5 py-2 rounded-lg border border-[#E5E7EB] text-gray-500 font-bold text-[12px] hover:bg-gray-50 hover:text-gray-700 transition-all active:scale-95"
              >
                Чернетка
              </button>
              <button 
                @click="save('production')" 
                :disabled="saving"
                class="btn-premium px-7 py-2 rounded-lg bg-gradient-to-r from-[#6C63FF] to-[#00C9A7] text-white font-black text-[12px] uppercase tracking-wider disabled:opacity-50 transition-all active:scale-95"
              >
                {{ orderId ? 'Оновити замовлення' : 'Створити замовлення' }}
              </button>
            </div>
          </div>
        </div>
        <!-- 1. Bottom Progress Line (2px) -->
        <div class="h-[2px] w-full bg-gray-50 overflow-hidden">
          <div class="h-full bg-gradient-to-r from-[#6C63FF] to-[#00C9A7] transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(108,99,255,0.5)]"
               :style="`width: ${readinessData.progress}%`"></div>
        </div>
      </header>
    </div>

    <!-- ─── 3. MAIN WORKSPACE ─── -->
    <main class="pt-6 pb-12 grid grid-cols-1 lg:grid-cols-12 gap-6 px-3">
      
      <!-- LEFT COLUMN: Primary Data (9/12) -->
      <div class="lg:col-span-9 ml-3 space-y-6">
        
        <!-- CARD 1: Customer & Logistics -->
        <div class="bg-white rounded-[12px] border border-gray-200 shadow-sm overflow-hidden relative group hover:shadow-[0_4px_20px_rgba(0,0,0,0.06)] transition-all duration-300">
          <div class="absolute left-0 top-0 w-full h-[40px] bg-gradient-to-r from-[rgba(108,99,255,0.03)] to-transparent pointer-events-none"></div>
          <div class="p-6 relative">
            <div class="flex items-center justify-between mb-5">
              <h2 class="text-[14px] font-bold flex items-center gap-2 text-gray-800">
                <el-icon class="text-[#6C63FF] text-base"><User /></el-icon>
                Замовник та логістика
              </h2>
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

        <!-- CARD 2: Product Configuration -->
        <div class="bg-white rounded-[12px] border border-gray-200 shadow-sm overflow-hidden relative group hover:shadow-[0_4px_20px_rgba(0,0,0,0.06)] transition-all duration-300">
          <div class="absolute left-0 top-0 w-full h-[40px] bg-gradient-to-r from-[rgba(108,99,255,0.03)] to-transparent pointer-events-none"></div>
          <div class="p-6 relative">
            <div class="flex items-center justify-between mb-5">
              <h2 class="text-[14px] font-bold flex items-center gap-2 text-gray-800">
                <el-icon class="text-[#6C63FF] text-base"><Box /></el-icon>
                Конфігурація замовлення
              </h2>
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

        <!-- 2. Finalization block stays (Calculated cost) -->
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

      <!-- RIGHT COLUMN: Readiness & AI (3/12) -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-[12px] border border-gray-200 shadow-sm p-5 sticky top-[76px]">
          <CrmReadinessChecklist
            :progress="readinessData.progress"
            :items="readinessData.items"
          />
        </div>
      </div>
    </main>

    <!-- ─── 2. BOTTOM SUM BAR REMOVED ─── -->

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
  product_lines: [],
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

.order-topbar-wrapper {
  margin: 0 !important;
  padding: 0 !important;
  width: calc(100% + 48px) !important;
  margin-left: -24px !important;
  margin-right: -24px !important;
}

.order-topbar {
  position: sticky;
  top: 0;
  z-index: 99;
  width: 100%;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  border-bottom: 1px solid #EAECF4;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  padding: 0 24px;
  transition: background 0.3s ease;
}

.stage-glow {
  box-shadow: 0 0 12px rgba(108, 99, 255, 0.6);
}

.btn-premium {
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25);
}

.btn-premium:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(108, 99, 255, 0.35);
}

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
