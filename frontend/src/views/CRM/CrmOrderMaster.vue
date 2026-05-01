<template>
  <div class="min-h-screen bg-[#F8FAFC] font-inter text-slate-900 antialiased">
    
    <!-- ─── ENTERPRISE GLOBAL HEADER ─── -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-[100] shadow-sm">
      <div class="max-w-[1700px] mx-auto px-6 py-4">
        <div class="flex items-center justify-between gap-8">
          <div class="flex items-center gap-5">
            <button @click="router.back()" class="p-2.5 hover:bg-slate-50 rounded-xl transition-all text-slate-400 border border-transparent hover:border-slate-200">
              <el-icon :size="20"><ArrowLeft /></el-icon>
            </button>
            <div class="h-8 w-px bg-slate-200"></div>
            <div>
              <div class="text-[10px] font-black text-slate-400 uppercase tracking-[2px] leading-none mb-1.5">MASTER WORKSPACE</div>
              <h1 class="text-xl font-black flex items-center gap-3 leading-none">
                {{ form.order_number || 'НОВА ЗАЯВКА' }}
                <span class="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-md text-[10px] font-black uppercase tracking-wider">{{ form.crm_stage }}</span>
              </h1>
            </div>
          </div>
          
          <!-- HORIZONTAL STATUS STEPPER -->
          <div class="hidden xl:flex items-center flex-1 max-w-4xl px-12">
            <div v-for="(stage, idx) in stages" :key="stage.key" class="flex-1 flex items-center relative group">
              <div 
                @click="form.crm_stage = stage.key"
                :class="[
                  'h-1.5 flex-1 rounded-full cursor-pointer transition-all duration-300',
                  isStagePast(stage.key) ? 'bg-indigo-600' : (form.crm_stage === stage.key ? 'bg-indigo-600 ring-4 ring-indigo-50' : 'bg-slate-100 hover:bg-slate-200')
                ]"
              ></div>
              <div v-if="idx < stages.length - 1" class="w-1.5 h-1.5 bg-slate-200 rounded-full mx-1.5"></div>
              <div class="absolute -bottom-6 left-0 right-0 text-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-[9px] font-black uppercase text-indigo-400 tracking-widest">{{ stage.label }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button @click="save('draft')" class="px-5 py-2.5 text-[11px] font-black uppercase text-slate-400 hover:text-slate-600 transition-colors tracking-widest">ЧЕРНЕТКА</button>
            <button @click="save('save')" :loading="saving" class="px-8 py-2.5 bg-slate-900 text-white text-[11px] font-black uppercase rounded-xl hover:bg-slate-800 shadow-xl shadow-slate-200 transition-all active:scale-95 flex items-center gap-2 tracking-widest">
              <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
              ЗБЕРЕГТИ ЗАЯВКУ
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── MULTI-COLUMN WORKSPACE ─── -->
    <main class="max-w-[1700px] mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- LEFT COLUMN: PRIMARY INPUTS (Col 7) -->
      <div class="lg:col-span-7 space-y-8">
        
        <!-- INTEGRATED: CrmClientBlock -->
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

        <!-- PRODUCT CONFIGURATION CARD -->
        <section class="bg-white rounded-[32px] p-8 border border-slate-100 shadow-sm transition-all hover:shadow-md">
          <div class="flex items-center gap-4 mb-8">
            <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
              <el-icon :size="24"><Box /></el-icon>
            </div>
            <div>
              <h2 class="text-lg font-black text-slate-800 leading-none mb-1">Виріб та Конфігурація</h2>
              <p class="text-xs text-slate-400 font-medium tracking-tight">Налаштуйте параметри виробництва та специфікації.</p>
            </div>
          </div>

          <div class="space-y-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <label class="text-[11px] font-black text-slate-400 uppercase tracking-widest ml-1">Базова модель</label>
                <el-select v-model="form.product_id" filterable @change="onProductChange" class="master-select w-full" placeholder="Оберіть модель...">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </div>
              <div class="space-y-2">
                <label class="text-[11px] font-black text-slate-400 uppercase tracking-widest ml-1">Термін виробництва</label>
                <el-date-picker
                  v-model="form.deadline_date"
                  type="date"
                  placeholder="Оберіть дату"
                  format="DD.MM.YYYY"
                  value-format="YYYY-MM-DD"
                  class="master-datepicker w-full"
                />
              </div>
            </div>

            <!-- Dynamic Attributes (Master Style) -->
            <div v-if="productAttributes.length" class="p-6 bg-slate-50 rounded-2xl border border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="attr in productAttributes" :key="attr.id" class="space-y-2">
                <label class="text-[10px] font-black text-slate-500 uppercase tracking-tighter">{{ attr.name }}</label>
                <el-select v-model="form.attributes_values[attr.id]" class="master-select-mini w-full">
                  <el-option v-for="v in attr.values" :key="v" :label="v" :value="v" />
                </el-select>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-[11px] font-black text-slate-400 uppercase tracking-widest ml-1">Технічне завдання / Коментар</label>
              <textarea v-model="form.comment" class="master-input min-h-[120px] py-4" placeholder="Опишіть особливі побажання клієнта..."></textarea>
            </div>
          </div>
        </section>
      </div>

      <!-- RIGHT COLUMN: FINANCE & INTERACTION (Col 5) -->
      <div class="lg:col-span-5 space-y-8">
        
        <!-- FINANCIAL HUB (Premium Card) -->
        <section class="bg-slate-900 rounded-[32px] p-8 text-white shadow-2xl relative overflow-hidden group">
          <div class="absolute -right-12 -top-12 w-48 h-48 bg-indigo-500/20 rounded-full blur-[80px] group-hover:bg-indigo-500/30 transition-all duration-700"></div>
          
          <div class="flex items-center justify-between mb-10 relative z-10">
            <h2 class="text-[11px] font-black uppercase tracking-[4px] text-indigo-400/80">ФІНАНСОВИЙ МОДУЛЬ</h2>
            <div class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-black uppercase tracking-widest">{{ form.payment_status }}</div>
          </div>
          
          <div class="space-y-8 relative z-10">
            <div class="flex items-end justify-between">
              <div class="space-y-1">
                <span class="text-[10px] font-black text-white/30 uppercase tracking-widest block">Загальна сума</span>
                <div class="flex items-center gap-2">
                  <input type="number" v-model="form.total_amount" class="bg-transparent border-none p-0 text-4xl font-black text-white w-40 focus:ring-0" />
                  <span class="text-2xl font-black text-indigo-500/50">₴</span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-[10px] font-black text-white/30 uppercase tracking-widest block mb-1">Сплачено</span>
                <div class="text-2xl font-black">{{ prepaymentPercent }}%</div>
              </div>
            </div>

            <div class="w-full h-3 bg-white/5 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-500 transition-all duration-700 shadow-[0_0_15px_rgba(99,102,241,0.5)]" :style="{ width: `${prepaymentPercent}%` }"></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
              <div class="space-y-2">
                <label class="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">Предоплата</label>
                <div class="flex items-center gap-3 bg-white/5 rounded-xl p-1 border border-white/5 focus-within:border-indigo-500 transition-all">
                  <input type="number" v-model="form.prepayment_amount" class="bg-transparent border-none p-2 text-xl font-black text-white w-full focus:ring-0" />
                </div>
              </div>
              <div class="flex flex-wrap gap-1.5 pt-6">
                <button v-for="pct in [30, 50, 100]" :key="pct" @click="setPrepayPercent(pct)" class="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-[10px] font-black transition-all border border-white/5">{{ pct }}%</button>
              </div>
            </div>

            <button class="w-full py-5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-[11px] font-black uppercase tracking-[2px] transition-all shadow-[0_15px_30px_rgba(99,102,241,0.3)] active:scale-95">
              ЗГЕНЕРУВАТИ РАХУНОК
            </button>
          </div>
        </section>

        <!-- INTEGRATED: CrmContactPanel (The Interaction Hub) -->
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

        <!-- ACTIVITY FEED (Minimalist Style) -->
        <section class="bg-white rounded-[32px] p-8 border border-slate-100 shadow-sm overflow-hidden">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-sm font-black uppercase tracking-widest text-slate-800">Історія контактів</h2>
            <el-icon class="text-slate-300"><Clock /></el-icon>
          </div>
          <div class="space-y-6 max-h-[400px] overflow-y-auto pr-2 scrollbar-hide">
            <div v-for="log in contactHistory" :key="log.id" class="flex gap-4 group">
              <div class="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center shrink-0 border border-slate-100 group-hover:border-indigo-100 transition-all">
                <el-icon :size="16" class="text-slate-400 group-hover:text-indigo-500 transition-all"><component :is="getLogIcon(log.communication_type)" /></el-icon>
              </div>
              <div class="space-y-1">
                <div class="flex items-center gap-3">
                  <span class="text-[11px] font-black text-slate-700 uppercase tracking-tight">{{ log.result || 'Update' }}</span>
                  <span class="text-[9px] font-bold text-slate-400">{{ formatRelativeTime(log.contacted_at) }}</span>
                </div>
                <p class="text-[13px] text-slate-500 leading-snug font-medium">{{ log.note }}</p>
              </div>
            </div>
            <div v-if="!contactHistory.length" class="text-center py-10 opacity-20">
              <el-icon :size="48"><ChatLineSquare /></el-icon>
              <p class="text-[10px] font-black uppercase mt-4">Немає подій</p>
            </div>
          </div>
        </section>

      </div>
    </main>

    <!-- Modal for Quick Client Profile Edit -->
    <el-dialog v-model="cpDialogVisible" title="Профіль клієнта" width="400px" class="master-dialog">
      <div class="space-y-4">
        <div class="space-y-2">
          <label class="text-[11px] font-black uppercase text-slate-400 ml-1">Ім'я</label>
          <input v-model="newCp.name" class="master-input" placeholder="ПІБ Клієнта" />
        </div>
        <div class="space-y-2">
          <label class="text-[11px] font-black uppercase text-slate-400 ml-1">Телефон</label>
          <input v-model="newCp.phone" class="master-input" placeholder="+380..." />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-2">
          <button @click="cpDialogVisible = false" class="flex-1 py-3 text-[10px] font-black uppercase text-slate-400 tracking-widest">Скасувати</button>
          <button @click="createCounterparty" :loading="creatingCp" class="flex-1 py-3 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-xl">Створити</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Loading, User, Box, Wallet, Timer, ChatDotRound, 
  Promotion, Phone, Position, Clock, Calendar, Message, ChatLineSquare 
} from '@element-plus/icons-vue'
import api from '@/api'

// Import existing professional components
import CrmClientBlock from './components/CrmClientBlock.vue'
import CrmContactPanel from './components/CrmContactPanel.vue'

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
  lead_source_id: null,
  order_number: '',
  product_id: null,
  crm_stage: 'new',
  channel: 'Viber',
  city: '',
  phone: '',
  delivery_type: 'NP',
  delivery_method_id: null,
  attributes_values: {},
  total_amount: 0,
  prepayment_amount: 0,
  payment_status: 'unpaid',
  deadline_date: null,
  comment: '',
  next_contact_at: null,
  next_contact_comment: '',
})

// Dictionaries
const products = ref([])
const counterparties = ref([])
const leadSources = ref([])
const deliveryMethods = ref([])
const users = ref([])
const productAttributes = ref([])
const contactHistory = ref([])

const stages = [
  { key: 'new', label: 'НОВІ' },
  { key: 'payment', label: 'ОПЛАТА' },
  { key: 'processing', label: 'В РОБОТІ' },
  { key: 'production', label: 'ВИРОБНИЦТВО' },
  { key: 'done', label: 'ВИКОНАНО' }
]

// Contact Panel State
const commTypes = ref([
  { code: 'CALL', name: 'Дзвінок', icon: '📞' },
  { code: 'CHAT', name: 'Месенджер', icon: '💬' }
])
const contactResults = ref([
  { code: 'CONFIRMED', name: 'Підтвердив' },
  { code: 'THINKING', name: 'Думає' },
  { code: 'NO_ANSWER', name: 'Не відповів' },
  { code: 'REFUSED', name: 'Відмова' }
])
const contactResult = ref(null)
const contactCommType = ref('CALL')
const contactPlanReason = ref('first_touch')
const contactNextAt = ref(null)
const contactNote = ref('')
const savingContact = ref(false)

const nextTouchSummary = computed(() => {
  if (!form.next_contact_at) return 'Наступний контакт не заплановано'
  return `Наступний контакт: ${new Date(form.next_contact_at).toLocaleString('uk-UA')}`
})

// LOGIC
const isStagePast = (stageKey) => {
  const idx = stages.findIndex(s => s.key === stageKey)
  const currentIdx = stages.findIndex(s => s.key === form.crm_stage)
  return idx <= currentIdx
}

const prepaymentPercent = computed(() => {
  if (!form.total_amount) return 0
  return Math.round((form.prepayment_amount / form.total_amount) * 100)
})

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
}

const formatRelativeTime = (d) => {
  const diff = new Date() - new Date(d)
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}хв тому`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}год тому`
  return new Date(d).toLocaleDateString('uk-UA')
}

const getLogIcon = (type) => {
  const map = { CALL: 'Phone', CHAT: 'ChatDotRound', EMAIL: 'Message' }
  return map[type] || 'Clock'
}

const getResultHint = (code) => {
  const map = { CONFIRMED: 'Заявку підтверджено', THINKING: 'Потрібен повторний дотик', NO_ANSWER: 'Не взяв трубку', REFUSED: 'Клієнт відмовився' }
  return map[code] || ''
}

const handleContactPreset = (opts) => {
  const d = new Date()
  if (opts.minutes) d.setMinutes(d.getMinutes() + opts.minutes)
  if (opts.hours) d.setHours(d.getHours() + opts.hours)
  if (opts.tomorrow) { d.setDate(d.getDate() + 1); d.setHours(opts.h || 10, 0, 0, 0) }
  if (opts.days) { d.setDate(d.getDate() + opts.days); d.setHours(opts.h || 10, 0, 0, 0) }
  
  if (opts.syncContactLog) contactNextAt.ref = d.toISOString()
  else form.next_contact_at = d.toISOString()
  
  if (opts.reason) contactPlanReason.value = opts.reason
}

const searchCounterparties = async (query) => {
  if (!query || query.length < 2) return
  const res = await api.get(`/api/v1/counterparties?search=${query}&is_customer=true&limit=10`)
  counterparties.value = res.data
}

const onClientChange = async (id) => {
  if (!id) return
  try {
    const res = await api.get(`/api/v1/counterparties/${id}`)
    const c = res.data
    form.city = c.city || ''
    form.phone = c.phone || ''
    if (c.lead_source_id) form.lead_source_id = c.lead_source_id
    loadContacts()
  } catch (e) { console.error(e) }
}

const onProductChange = async (id) => {
  if (!id) return
  const res = await api.get(`/api/v1/products/${id}/attributes`)
  productAttributes.value = res.data
}

const loadContacts = async () => {
  if (!orderId.value) return
  const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
  contactHistory.value = res.data
}

const logContact = async () => {
  if (!orderId.value) return
  savingContact.value = true
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      note: contactNote.value,
      result: contactResult.value,
      communication_type: contactCommType.value,
      next_contact_at: contactNextAt.value
    })
    contactNote.value = ''
    contactResult.value = null
    loadContacts()
    ElMessage.success('Контакт зафіксовано')
  } catch (e) { ElMessage.error('Помилка логування') }
  finally { savingContact.value = false }
}

const save = async (action) => {
  saving.value = true
  try {
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Дані успішно збережено')
    if (!orderId.value) router.push(`/crm/order-master/${res.data.id}`)
  } catch (e) { ElMessage.error('Помилка при збереженні') }
  finally { saving.value = false }
}

// Client Dialog
const cpDialogVisible = ref(false)
const creatingCp = ref(false)
const newCp = reactive({ name: '', phone: '' })
const openCreateCounterparty = () => cpDialogVisible.value = true
const createCounterparty = async () => {
  creatingCp.value = true
  try {
    const res = await api.post('/api/v1/counterparties', { ...newCp, is_customer: true })
    counterparties.value.push(res.data)
    form.counterparty_id = res.data.id
    cpDialogVisible.value = false
  } finally { creatingCp.value = false }
}

const loadData = async () => {
  loading.value = true
  try {
    const [p, ls, dm, u] = await Promise.all([
      api.get('/api/v1/products?limit=200'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] })),
      api.get('/api/v1/warehouses').catch(() => ({ data: [] })), // Using warehouses as delivery methods placeholder if needed
      api.get('/api/v1/users/colleagues')
    ])
    products.value = p.data
    leadSources.value = ls.data
    deliveryMethods.value = dm.data
    users.value = u.data.map(u => ({ id: u.id, name: u.name || u.username }))
    
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}`)
      Object.assign(form, res.data)
      loadContacts()
      if (form.product_id) onProductChange(form.product_id)
    }
  } finally { loading.value = false }
}

watch(() => form.prepayment_amount, (val) => {
  if (val >= form.total_amount && form.total_amount > 0) form.payment_status = 'paid'
  else if (val > 0) form.payment_status = 'partial'
  else form.payment_status = 'unpaid'
})

onMounted(loadData)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.font-inter { font-family: 'Inter', sans-serif; }

.master-input {
  @apply w-full bg-white border border-slate-200 rounded-2xl px-5 py-3.5 text-sm font-medium 
         text-slate-700 outline-none transition-all focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500/30 placeholder:text-slate-300;
}

.master-select .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-2xl !px-4 !py-1 !shadow-sm !transition-all
         hover:!border-indigo-200 focus:!ring-4 focus:!ring-indigo-500/5 !h-[48px];
}

.master-select-mini .el-input__wrapper {
  @apply !bg-white !border-slate-100 !rounded-xl !px-3 !py-0 !shadow-none !h-[38px] !text-xs;
}

.master-datepicker .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-2xl !shadow-none !h-[48px] !w-full;
}

.master-dialog { @apply !rounded-[40px] !border-none !shadow-2xl overflow-hidden; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

/* Override existing component styles for seamless integration */
:deep(.crm-client-section-premium) {
  @apply !p-8 !bg-white !border !border-slate-100 !shadow-sm !rounded-[32px] !transition-all hover:!shadow-md;
}
:deep(.crm-section.control-card) {
  @apply !p-8 !bg-white !border !border-slate-100 !shadow-sm !rounded-[32px] !transition-all hover:!shadow-md;
}
</style>
