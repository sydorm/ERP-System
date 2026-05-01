<template>
  <div class="min-h-screen bg-[#F3F4F6] font-inter text-slate-900 antialiased">
    
    <!-- ─── TOP GLOBAL BAR (Status Stepper) ─── -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-[100] shadow-sm">
      <div class="max-w-[1600px] mx-auto px-6 py-4">
        <div class="flex items-center justify-between gap-8">
          <div class="flex items-center gap-4">
            <button @click="router.back()" class="p-2 hover:bg-slate-100 rounded-lg transition-all text-slate-400">
              <el-icon :size="18"><ArrowLeft /></el-icon>
            </button>
            <div>
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">CRM / Order Management</div>
              <h1 class="text-xl font-bold flex items-center gap-3 leading-none">
                {{ form.order_number || 'New Order' }}
                <span class="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-[10px] font-bold uppercase">{{ form.crm_stage }}</span>
              </h1>
            </div>
          </div>
          
          <!-- Horizontal Stepper (SaaS Standard) -->
          <div class="hidden xl:flex items-center flex-1 max-w-3xl px-12">
            <div v-for="(stage, idx) in stages" :key="stage.key" class="flex-1 flex items-center relative group">
              <div 
                @click="form.crm_stage = stage.key"
                :class="[
                  'h-2 flex-1 rounded-full cursor-pointer transition-all',
                  isStagePast(stage.key) ? 'bg-blue-600' : (form.crm_stage === stage.key ? 'bg-blue-600 ring-4 ring-blue-50' : 'bg-slate-200 hover:bg-slate-300')
                ]"
              ></div>
              <div v-if="idx < stages.length - 1" class="w-1 h-1 bg-slate-300 rounded-full mx-1"></div>
              <div class="absolute -bottom-5 left-0 right-0 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-[9px] font-bold uppercase text-slate-400 tracking-tighter">{{ stage.label }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button @click="save('draft')" class="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-50 rounded-lg transition-all">DRAFT</button>
            <button @click="save('save')" :loading="saving" class="px-6 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 shadow-lg shadow-blue-100 transition-all flex items-center gap-2">
              <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
              SAVE CHANGES
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── MAIN CONTENT ─── -->
    <main class="max-w-[1600px] mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- LEFT: Primary Details (Col 8) -->
      <div class="lg:col-span-8 space-y-6">
        
        <!-- Section: Customer -->
        <section class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div class="px-6 py-4 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-[12px] font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <el-icon><User /></el-icon> Customer Information
            </h2>
            <button @click="openCreateCounterparty" class="text-[11px] font-bold text-blue-600 hover:underline">+ NEW CUSTOMER</button>
          </div>
          <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2 space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">Search Counterparty</label>
              <el-select
                v-model="form.counterparty_id"
                filterable
                remote
                placeholder="Name, Phone or Email..."
                :remote-method="searchCounterparties"
                @change="onClientChange"
                class="master-select w-full"
              >
                <el-option v-for="c in counterparties" :key="c.id" :label="`${c.name} (${c.phone || ''})`" :value="c.id" />
              </el-select>
            </div>
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">Lead Source</label>
              <el-select v-model="form.lead_source_id" class="master-select w-full">
                <el-option v-for="s in leadSources" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </div>
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">Phone Number</label>
              <input v-model="form.phone" class="master-input" placeholder="+380..." />
            </div>
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">City / Location</label>
              <input v-model="form.city" class="master-input" placeholder="Kyiv, Ukraine" />
            </div>
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">Preferred Channel</label>
              <el-select v-model="form.channel" class="master-select w-full">
                <el-option label="Viber" value="Viber" />
                <el-option label="Telegram" value="Telegram" />
                <el-option label="Instagram" value="Instagram" />
                <el-option label="Phone Call" value="Phone" />
              </el-select>
            </div>
          </div>
        </section>

        <!-- Section: Order Configuration -->
        <section class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div class="px-6 py-4 bg-slate-50/50 border-b border-slate-100">
            <h2 class="text-[12px] font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <el-icon><Box /></el-icon> Configuration & Items
            </h2>
          </div>
          <div class="p-6 space-y-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-400 uppercase">Base Product Model</label>
                <el-select v-model="form.product_id" filterable @change="onProductChange" class="master-select w-full" placeholder="Select base model...">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </div>
              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-400 uppercase">Shipping Method</label>
                <el-select v-model="form.delivery_type" class="master-select w-full">
                  <el-option label="Nova Poshta" value="NP" />
                  <el-option label="Local Pickup" value="PICKUP" />
                  <el-option label="Courier Delivery" value="COURIER" />
                </el-select>
              </div>
            </div>

            <!-- Specs Grid -->
            <div v-if="productAttributes.length" class="bg-slate-50 rounded-xl p-6 border border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="attr in productAttributes" :key="attr.id" class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">{{ attr.name }}</label>
                <el-select v-model="form.attributes_values[attr.id]" class="master-select-mini w-full">
                  <el-option v-for="v in attr.values" :key="v" :label="v" :value="v" />
                </el-select>
              </div>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase">Order Requirements / Notes</label>
              <textarea v-model="form.comment" class="master-input min-h-[120px] py-3" placeholder="Specific technical details, custom dimensions..."></textarea>
            </div>
          </div>
        </section>

      </div>

      <!-- RIGHT: Support Info & Actions (Col 4) -->
      <div class="lg:col-span-4 space-y-6">
        
        <!-- Financial Summary Card (ERP Style) -->
        <section class="bg-slate-900 rounded-xl p-8 text-white shadow-xl relative overflow-hidden">
          <div class="absolute -right-8 -top-8 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl"></div>
          
          <h2 class="text-[11px] font-bold uppercase tracking-[3px] text-blue-400/60 mb-8">Financial Overview</h2>
          
          <div class="space-y-6">
            <div class="flex items-baseline justify-between">
              <span class="text-xs text-slate-400 font-medium">Total Amount</span>
              <div class="flex items-center gap-1">
                <input type="number" v-model="form.total_amount" class="bg-transparent border-none p-0 text-2xl font-black text-white w-24 text-right focus:ring-0" />
                <span class="text-xl font-bold text-slate-500">₴</span>
              </div>
            </div>

            <div class="h-px bg-white/5"></div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-500 uppercase">Prepayment</span>
                <span :class="['text-[9px] font-black uppercase px-2 py-0.5 rounded', form.payment_status === 'paid' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400']">
                  {{ form.payment_status === 'paid' ? 'Settled' : 'Pending' }}
                </span>
              </div>
              <div class="flex items-center gap-3">
                <div class="flex-1 bg-white/5 rounded-lg p-3 border border-white/5 focus-within:border-blue-500 transition-all">
                  <input type="number" v-model="form.prepayment_amount" class="bg-transparent border-none p-0 text-lg font-bold text-white w-full focus:ring-0" />
                </div>
                <div class="flex flex-col gap-1">
                  <button v-for="pct in [30, 50, 100]" :key="pct" @click="setPrepayPercent(pct)" class="px-3 py-1 bg-white/5 hover:bg-white/10 rounded text-[9px] font-bold transition-all">{{ pct }}%</button>
                </div>
              </div>
            </div>

            <div class="pt-4">
              <button class="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-blue-900/40">
                Generate Invoice
              </button>
            </div>
          </div>
        </section>

        <!-- Deadline & Logistics -->
        <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm">
          <div class="space-y-6">
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-400 uppercase block mb-2">Production Deadline</label>
              <el-date-picker
                v-model="form.deadline_date"
                type="date"
                placeholder="Set Deadline"
                format="DD.MM.YYYY"
                value-format="YYYY-MM-DD"
                class="master-datepicker w-full"
              />
            </div>
            <div class="p-4 bg-blue-50 rounded-xl flex items-center justify-between">
              <div class="flex items-center gap-3">
                <el-icon class="text-blue-600"><Timer /></el-icon>
                <span class="text-[11px] font-bold text-blue-900 uppercase">Materials Status</span>
              </div>
              <span class="text-[10px] font-black text-blue-600 uppercase">Available</span>
            </div>
          </div>
        </section>

        <!-- Activity Feed (Right Side) -->
        <section class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm h-[500px] flex flex-col">
          <div class="px-6 py-4 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-[11px] font-bold uppercase tracking-widest text-slate-500">Interaction Log</h2>
            <el-icon class="text-slate-300"><ChatDotRound /></el-icon>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <div v-for="log in contactHistory" :key="log.id" class="flex gap-4">
              <div class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center shrink-0">
                <el-icon :size="14" class="text-slate-400"><component :is="getLogIcon(log.communication_type)" /></el-icon>
              </div>
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="text-[11px] font-bold text-slate-700">{{ log.result || 'Update' }}</span>
                  <span class="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">{{ formatTime(log.contacted_at) }}</span>
                </div>
                <p class="text-[13px] text-slate-500 leading-snug">{{ log.note }}</p>
              </div>
            </div>
          </div>
          <div class="p-4 bg-slate-50 border-t border-slate-100">
            <div class="relative">
              <input v-model="quickNote" @keyup.enter="postNote" class="master-input-mini pr-10" placeholder="Add note..." />
              <button @click="postNote" class="absolute right-2 top-2 p-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">
                <el-icon><Promotion /></el-icon>
              </button>
            </div>
          </div>
        </section>

      </div>
    </main>

    <!-- New Client Dialog -->
    <el-dialog v-model="cpDialogVisible" title="Create Profile" width="360px" class="master-dialog">
      <div class="space-y-4">
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Full Name</label>
          <input v-model="newCp.name" class="master-input" placeholder="John Doe" />
        </div>
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Phone Number</label>
          <input v-model="newCp.phone" class="master-input" placeholder="+380..." />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-2">
          <button @click="cpDialogVisible = false" class="flex-1 py-3 text-[10px] font-bold text-slate-400 uppercase">Cancel</button>
          <button @click="createCounterparty" :loading="creatingCp" class="flex-1 py-3 bg-blue-600 text-white rounded-lg text-[10px] font-bold uppercase shadow-lg">Create</button>
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
  Promotion, Phone, Position, Clock, Calendar, Message 
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const route = useRoute()

const orderId = computed(() => {
  const id = route.params.id
  return (id && id !== 'new') ? id : null
})

// STATE
const loading = ref(true)
const saving = ref(false)
const quickNote = ref('')
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
  attributes_values: {},
  total_amount: 0,
  prepayment_amount: 0,
  payment_status: 'unpaid',
  deadline_date: null,
  comment: '',
})

const stages = [
  { key: 'new', label: 'Inquiry' },
  { key: 'negotiation', label: 'Negotiation' },
  { key: 'payment', label: 'Pending Payment' },
  { key: 'processing', label: 'Production' },
  { key: 'delivery', label: 'Shipping' },
  { key: 'done', label: 'Completed' }
]

const products = ref([])
const counterparties = ref([])
const leadSources = ref([])
const productAttributes = ref([])
const contactHistory = ref([])

// LOGIC
const isStagePast = (stageKey) => {
  const idx = stages.findIndex(s => s.key === stageKey)
  const currentIdx = stages.findIndex(s => s.key === form.crm_stage)
  return idx < currentIdx
}

const prepaymentPercent = computed(() => {
  if (!form.total_amount) return 0
  return Math.round((form.prepayment_amount / form.total_amount) * 100)
})

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
}

const formatTime = (d) => new Date(d).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
const getLogIcon = (type) => {
  const map = { CALL: 'Phone', CHAT: 'ChatDotRound', EMAIL: 'Message' }
  return map[type] || 'Clock'
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

const postNote = async () => {
  if (!quickNote.value || !orderId.value) return
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      note: quickNote.value,
      communication_type: 'CHAT'
    })
    quickNote.value = ''
    loadContacts()
  } catch (e) { ElMessage.error('Error adding note') }
}

const save = async (action) => {
  saving.value = true
  try {
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Changes saved successfully')
    if (!orderId.value) router.push(`/crm/order-master/${res.data.id}`)
  } catch (e) { ElMessage.error('Failed to save changes') }
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
    const [p, ls] = await Promise.all([
      api.get('/api/v1/products?limit=200'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] }))
    ])
    products.value = p.data
    leadSources.value = ls.data
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
  @apply w-full bg-white border border-slate-200 rounded-lg px-4 py-2.5 text-sm 
         text-slate-700 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-50/50 placeholder:text-slate-300;
}

.master-input-mini {
  @apply w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs 
         text-slate-700 outline-none transition-all focus:border-blue-500;
}

.master-select .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-lg !px-4 !py-1 !shadow-none !transition-all
         hover:!border-slate-300 focus:!border-blue-500 focus:!ring-4 focus:!ring-blue-50/50 !h-[42px];
}

.master-select-mini .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-lg !px-3 !py-0 !shadow-none !h-[36px] !text-xs;
}

.master-datepicker .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-lg !shadow-none !h-[42px] !w-full;
}

.master-dialog { @apply !rounded-2xl !border-none !shadow-2xl overflow-hidden; }
.master-dialog .el-dialog__header { @apply !p-6 !pb-2; }
.master-dialog .el-dialog__title { @apply !text-xs !font-black !uppercase !tracking-widest; }

/* Custom Overrides for Element Plus */
.el-select-dropdown__item.selected { @apply !text-blue-600 !font-bold; }
</style>
