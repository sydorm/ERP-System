<template>
  <div class="crm-editor-premium-page bg-[#F8FAFC] min-h-screen font-inter antialiased">
    
    <!-- ─── MODULAR HEADER ─── -->
    <CrmOrderHeader
      :stages="stages"
      :active-stage="form.crm_stage"
      :is-passed-stage="isStagePast"
      :order-id="orderId"
      :saving="saving"
      @back="router.back()"
      @set-stage="setStage"
      @save-draft="save('draft')"
      @save-production="save('production')"
      @print="handlePrint"
    />

    <!-- ─── MULTI-COLUMN WORKSPACE (70/30 Split) ─── -->
    <main class="max-w-[1700px] mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-10 items-start pt-8">
      
      <!-- LEFT: CORE WORKFLOW (70% - Col 8) -->
      <div class="lg:col-span-8 space-y-12">
        
        <!-- STEP 1: Client Management -->
        <section class="step-card-premium">
          <CrmClientBlock
            :form="form"
            :v-errors="vErrors"
            :counterparties="counterparties"
            :lead-sources="leadSources"
            :delivery-methods="deliveryMethods"
            :manager-options="users"
            :can-reassign-manager="true"
            :client-name="form.client_name"
            :client-phone="form.client_phone"
            @update:clientName="form.client_name = $event"
            @update:clientPhone="form.client_phone = $event"
            @counterparty-change="onClientChange"
            @new-client="openCreateCounterparty"
          />
        </section>

        <!-- STEP 2: Product Configuration -->
        <section class="step-card-premium">
          <CrmProductBlock
            :form="form"
            :products="products"
            :product-attributes="productAttributes"
            @product-change="onProductChange"
            @set-attr-value="setAttrValue"
            @set-attr-dim="setAttrDim"
            @upload-photo="handlePhotoUpload"
          />
        </section>

        <!-- STEP 3: Financial Calculations -->
        <section class="step-card-premium">
          <CrmFinanceBlock
            :form="form"
            :bank-accounts="bankAccounts"
            :auto-payment-status="autoPaymentStatus"
            :format-currency="formatCurrency"
            @set-prepay-pct="setPrepayPercent"
            @calc-prepayment="handleCalcPrepayment"
            @prepayment-input="handlePrepaymentInput"
          />
        </section>

        <!-- STEP 4: Deadlines & Priorities -->
        <section class="step-card-premium">
          <CrmDeadlinesBlock
            :form="form"
            :priorities="priorities"
            :format-date="formatDate"
          />
        </section>
      </div>

      <!-- RIGHT: INTELLIGENCE & INTERACTION (30% - Col 4) -->
      <div class="lg:col-span-4 space-y-10 sticky top-24">
        
        <!-- COMPONENT: Readiness Checklist (Top Status) -->
        <div class="side-widget-premium readiness-box">
          <CrmReadinessChecklist
            :progress="readinessData.progress"
            :items="readinessData.items"
          />
        </div>

        <!-- COMPONENT: Interaction Hub -->
        <div class="side-widget-premium">
          <CrmContactPanel
            :form="form"
            :order-id="orderId"
            :communication-types="commTypes"
            :contact-results="contactResults"
            :contact-result="contactResult"
            :contact-comm-type="contactCommType"
            :contact-plan-reason="contactPlanReason"
            :contact-next-at="contactNextAt"
            :contact-note="contactNote"
            :next-touch-summary="nextTouchSummary"
            :saving-contact="savingContact"
            :get-result-hint="getResultHint"
            @update:contact-comm-type="contactCommType = $event"
            @update:contact-plan-reason="contactPlanReason = $event"
            @update:contact-next-at="contactNextAt = $event"
            @update:contact-note="contactNote = $event"
            @set-next-contact-preset="handleContactPreset"
            @apply-contact-result="contactResult = $event"
            @log-contact="logContact"
          />

          <!-- Integrated Communication History -->
          <CrmCommunicationHistory
            v-if="contactHistory.length"
            :contacts="contactHistory"
            :get-contact-result-color="getContactResultColor"
            :get-comm-icon="getCommIcon"
            :get-comm-name="getCommName"
            :format-date-time="formatDateTime"
            :contact-result-label="contactResultLabel"
          />
        </div>

        <!-- COMPONENT: Warehouse Sync (Analysis) -->
        <div class="side-widget-premium" v-if="form.product_id">
          <CrmMaterialsCheckBlock
            :form="form"
            :material-check="materialCheck"
            :materials-loading="checkingMaterials"
            :format-qty="formatQty"
            @go-to-purchases="router.push('/purchases/new')"
          />
        </div>

        <!-- COMPONENT: Smart Assistant Tips -->
        <div class="side-widget-premium ai-widget">
          <CrmAiAssistant 
            v-if="orderId"
            :form="form"
            :readiness-progress="readinessData.progress"
            @check="loadData"
          />
        </div>
      </div>
    </main>

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
  { key: 'new', label: 'Заявка' },
  { key: 'negotiation', label: 'Перемовини' },
  { key: 'payment', label: 'Оплата' },
  { key: 'processing', label: 'В роботі' },
  { key: 'production', label: 'Виробництво' },
  { key: 'delivery', label: 'Доставка' },
  { key: 'done', label: 'Виконано' }
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

const readinessData = computed(() => {
  const items = [
    { key: 'client', label: 'Дані замовника', done: !!form.counterparty_id },
    { key: 'product', label: 'Виріб обрано', done: !!form.product_id },
    { key: 'specs', label: 'Характеристики', done: Object.keys(form.attributes_values || {}).length > 0 },
    { key: 'prepayment', label: 'Передоплата', done: form.prepayment_amount > 0 },
    { key: 'deadline', label: 'Дедлайн встановлено', done: !!form.deadline_date }
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
    const [p, ls, dm, u, ba] = await Promise.all([
      api.get('/api/v1/products?limit=200'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] })),
      api.get('/api/v1/warehouses').catch(() => ({ data: [] })),
      api.get('/api/v1/users/colleagues'),
      api.get('/api/v1/bank-accounts').catch(() => ({ data: [] }))
    ])
    products.value = p.data; leadSources.value = ls.data; deliveryMethods.value = dm.data; users.value = u.data; bankAccounts.value = ba.data
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
  border-radius: 32px;
  box-shadow: 0 10px 40px -10px rgba(15, 23, 42, 0.08);
  border: 1px solid #F1F5F9;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-card-premium:hover {
  box-shadow: 0 20px 60px -15px rgba(15, 23, 42, 0.12);
  transform: translateY(-2px);
}

.side-widget-premium {
  background: #fff;
  border-radius: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  padding: 4px;
  border: 1px solid #F8FAFC;
}

.readiness-box {
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F7FF 100%);
  border-color: #EEF2FF;
}

.ai-widget {
  background: linear-gradient(135deg, #F0FDFA 0%, #FFFFFF 100%);
  border-color: #CCFBF1;
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
