<template>
  <div class="crm-order-redesign min-h-screen bg-[#F9FAFB] font-inter text-[#1F2937] antialiased">
    
    <!-- ─── TOP PROGRESS BAR ─── -->
    <div class="sticky top-0 z-[1020] bg-white border-b border-gray-200 px-6 py-4">
      <div class="max-w-[1440px] mx-auto flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button @click="router.back()" class="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <div>
            <h1 class="text-lg font-bold">Створення замовлення</h1>
            <p class="text-xs text-gray-500">Заповніть дані для формування нової угоди</p>
          </div>
        </div>

        <!-- Progress Steps -->
        <div class="hidden md:flex items-center gap-8">
          <div 
            v-for="(step, idx) in ['Клієнт', 'Товар', 'Логістика', 'Підтвердження']" 
            :key="step"
            class="flex items-center gap-3"
          >
            <div 
              class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
              :class="currentStep >= idx ? 'bg-[#2563EB] text-white' : 'bg-gray-100 text-gray-400'"
            >
              {{ idx + 1 }}
            </div>
            <span 
              class="text-sm font-semibold transition-colors"
              :class="currentStep >= idx ? 'text-[#2563EB]' : 'text-gray-400'"
            >
              {{ step }}
            </span>
            <div v-if="idx < 3" class="w-8 h-[2px] bg-gray-100"></div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <span class="text-2xl font-black text-gray-200">#NEW</span>
        </div>
      </div>
    </div>

    <!-- ─── MAIN WORKSPACE (60/40 Split) ─── -->
    <main class="max-w-[1440px] mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 pt-8 pb-32">
      
      <!-- LEFT COLUMN: PRIMARY DATA (60%) -->
      <div class="lg:col-span-7 space-y-8">
        
        <!-- CARD 1: Customer & Logistics -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden relative">
          <div 
            class="absolute left-0 top-0 w-1.5 h-full transition-colors duration-500"
            :class="readinessData.items[0].done ? 'bg-[#2563EB]' : 'bg-gray-200'"
          ></div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-[16px] font-bold flex items-center gap-2">
                <el-icon class="text-blue-600"><User /></el-icon>
                Замовник та логістика
              </h2>
              <el-tag v-if="form.counterparty_id" type="success" effect="light" round size="small">Контакт обрано</el-tag>
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
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden relative">
          <div 
            class="absolute left-0 top-0 w-1.5 h-full transition-colors duration-500"
            :class="readinessData.items[1].done ? 'bg-[#2563EB]' : 'bg-gray-200'"
          ></div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-[16px] font-bold flex items-center gap-2">
                <el-icon class="text-blue-600"><Box /></el-icon>
                Конфігурація замовлення
              </h2>
              <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Крок 2</span>
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
      </div>

      <!-- RIGHT COLUMN: ADDITIONAL (40%) -->
      <div class="lg:col-span-5 space-y-8 sticky top-28">
        
        <!-- CARD 3: Financial Details -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden relative">
          <div class="p-6">
            <h2 class="text-[16px] font-bold flex items-center gap-2 mb-6">
              <el-icon class="text-blue-600"><Money /></el-icon>
              Фінанси та терміни
            </h2>
            <div class="space-y-6">
              <CrmFinanceBlock
                :form="form"
                :bank-accounts="bankAccounts"
                :auto-payment-status="autoPaymentStatus"
                :format-currency="formatCurrency"
                @set-prepay-pct="setPrepayPercent"
              />
              
              <div class="h-px bg-gray-100"></div>

              <CrmDeadlinesBlock
                :form="form"
                :priorities="priorities"
                :format-date="formatDate"
              />
            </div>
          </div>
        </div>

        <!-- CARD 4: Manager & Tasks -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
           <CrmReadinessChecklist
             :progress="readinessData.progress"
             :items="readinessData.items"
           />
        </div>
      </div>
    </main>

    <!-- ─── STICKY FOOTER ACTIONS ─── -->
    <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 z-[1030] shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
      <div class="max-w-[1440px] mx-auto flex items-center justify-between">
        <div class="flex items-center gap-6">
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-gray-400 uppercase">Сума до сплати</span>
            <span class="text-xl font-black text-[#2563EB]">{{ formatCurrency(form.total_amount) }} ₴</span>
          </div>
        </div>
        
        <div class="flex items-center gap-4">
          <button 
            @click="save('draft')" 
            class="px-6 py-2.5 rounded-xl border border-gray-300 text-gray-600 font-bold text-sm hover:bg-gray-50 transition-colors"
          >
            Зберегти чернетку
          </button>
          <button 
            @click="save('production')" 
            :disabled="saving"
            class="px-10 py-2.5 rounded-xl bg-[#2563EB] text-white font-bold text-sm shadow-lg shadow-blue-200 hover:bg-blue-700 disabled:opacity-50 transition-all active:scale-95"
          >
            {{ orderId ? 'Оновити замовлення' : 'Створити замовлення' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Client Dialog -->
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
import CrmFinanceBlock from './components/CrmFinanceBlock.vue'
import CrmContactPanel from './components/CrmContactPanel.vue'
import CrmCommunicationHistory from './components/CrmCommunicationHistory.vue'
import CrmMaterialsCheckBlock from './components/CrmMaterialsCheckBlock.vue'
import CrmDeadlinesBlock from './components/CrmDeadlinesBlock.vue'
import CrmReadinessChecklist from './components/CrmReadinessChecklist.vue'
import CrmAiAssistant from './components/CrmAiAssistant.vue'
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
  total_amount: 0,
  prepayment_amount: 0,
  payment_status: 'unpaid',
  deadline_date: null,
  comment: '',
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

.crm-editor-premium-page {
  padding-bottom: 100px;
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
