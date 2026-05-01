<template>
  <div class="min-h-screen bg-[#F0F2F5] p-4 lg:p-6 font-sans text-slate-900 antialiased">
    
    <!-- ─── COMMAND HEADER ─── -->
    <header class="max-w-[1800px] mx-auto mb-6 bg-white/70 backdrop-blur-md border border-white rounded-3xl p-4 shadow-sm flex items-center justify-between sticky top-0 z-50">
      <div class="flex items-center gap-6">
        <button @click="router.back()" class="p-2 hover:bg-slate-100 rounded-xl transition-colors">
          <el-icon :size="20"><ArrowLeft /></el-icon>
        </button>
        <div class="h-10 w-px bg-slate-200"></div>
        <div>
          <div class="text-[10px] font-black text-slate-400 uppercase tracking-[2px]">ORDER WORKSPACE</div>
          <h1 class="text-xl font-black flex items-center gap-2">
            {{ form.order_number || 'Нова заявка' }}
            <span class="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-md text-[10px] font-black uppercase">{{ form.crm_stage }}</span>
          </h1>
        </div>
      </div>

      <div class="hidden xl:flex items-center gap-12">
        <div class="flex flex-col items-center">
          <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Оплата</span>
          <div class="flex items-center gap-2">
            <div class="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-500 transition-all" :style="{ width: `${prepaymentPercent}%` }"></div>
            </div>
            <span class="text-xs font-black">{{ prepaymentPercent }}%</span>
          </div>
        </div>
        <div class="flex flex-col items-center border-l border-slate-100 pl-12">
          <span class="text-[9px] font-bold text-slate-400 uppercase mb-1">Матеріали</span>
          <div class="flex items-center gap-2">
            <div :class="['w-2 h-2 rounded-full animate-pulse', matStatusClass === 'mat-ok' ? 'bg-emerald-500' : 'bg-rose-500']"></div>
            <span class="text-xs font-black">{{ matStatusLabel }}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button @click="save('draft')" class="px-5 py-2.5 text-[11px] font-black uppercase text-slate-400 hover:text-slate-600 transition-colors">Чернетка</button>
        <button @click="save('production')" :disabled="saving" class="px-6 py-2.5 bg-slate-900 text-white rounded-2xl text-[11px] font-black uppercase hover:bg-slate-800 shadow-xl shadow-slate-200 flex items-center gap-2 transition-all active:scale-95">
          <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
          Запустити в роботу
        </button>
      </div>
    </header>

    <!-- ─── TRIPLE COLUMN WORKSPACE ─── -->
    <main class="max-w-[1800px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- LEFT: PRODUCTION & SPECS (Col 4) -->
      <div class="lg:col-span-4 space-y-6">
        <section class="bg-white rounded-[32px] p-8 border border-white shadow-sm overflow-hidden relative group">
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-indigo-50 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          
          <div class="flex items-center gap-3 mb-8">
            <div class="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
              <el-icon :size="20"><Box /></el-icon>
            </div>
            <h2 class="text-sm font-black uppercase tracking-widest text-slate-800">Конфігурація виробу</h2>
          </div>

          <div class="space-y-6">
            <div class="space-y-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Модель</label>
              <el-select v-model="form.product_id" filterable @change="onProductChange" class="workspace-select w-full" placeholder="Оберіть основу...">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </div>

            <!-- Attributes with Icons Grid -->
            <div v-if="productAttributes.length" class="grid grid-cols-2 gap-4">
              <div v-for="attr in productAttributes" :key="attr.id" class="p-4 bg-slate-50/50 rounded-2xl border border-slate-100 space-y-2 hover:bg-white hover:border-indigo-100 transition-all cursor-pointer">
                <div class="text-[9px] font-black text-slate-400 uppercase tracking-widest">{{ attr.name }}</div>
                <el-select v-model="form.attributes_values[attr.id]" class="workspace-select-mini w-full">
                  <el-option v-for="v in attr.values" :key="v" :label="v" :value="v" />
                </el-select>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Коментар до виробу</label>
              <textarea v-model="form.comment" class="workspace-input min-h-[100px]" placeholder="Особливості конструкції, упаковки..."></textarea>
            </div>
          </div>
        </section>

        <section class="bg-white rounded-[32px] p-8 border border-white shadow-sm">
          <div class="flex items-center gap-3 mb-8">
            <div class="p-3 bg-emerald-50 text-emerald-600 rounded-2xl">
              <el-icon :size="20"><Van /></el-icon>
            </div>
            <h2 class="text-sm font-black uppercase tracking-widest text-slate-800">Логістика</h2>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Тип доставки</label>
              <el-select v-model="form.delivery_type" class="workspace-select-mini w-full">
                <el-option label="Нова Пошта" value="NP" />
                <el-option label="Самовивіз" value="PICKUP" />
              </el-select>
            </div>
            <div class="space-y-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Склад</label>
              <el-select v-model="form.warehouse_id" class="workspace-select-mini w-full">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </div>
          </div>
        </section>
      </div>

      <!-- MIDDLE: TIMELINE & INTERACTION (Col 5) -->
      <div class="lg:col-span-5 space-y-6">
        <section class="bg-white rounded-[32px] p-8 border border-white shadow-sm flex flex-col h-[750px]">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-sm font-black uppercase tracking-widest text-slate-800 flex items-center gap-2">
              <el-icon class="text-slate-400"><ChatDotRound /></el-icon>
              Стрічка активності
            </h2>
            <span class="text-[10px] font-black text-emerald-500 uppercase px-2 py-0.5 bg-emerald-50 rounded">Live Feed</span>
          </div>

          <!-- Timeline Container -->
          <div class="flex-1 overflow-y-auto pr-2 space-y-6 scrollbar-hide">
            <div v-for="event in contactHistory" :key="event.id" class="relative pl-10 before:absolute before:left-3 before:top-2 before:bottom-0 before:w-px before:bg-slate-100">
              <div class="absolute left-0 top-1 w-6 h-6 rounded-full bg-white border border-slate-100 flex items-center justify-center shadow-sm z-10">
                <el-icon :size="12" class="text-slate-400"><component :is="getEventIcon(event.communication_type)" /></el-icon>
              </div>
              <div class="bg-slate-50/50 rounded-2xl p-4 border border-transparent hover:border-slate-100 transition-all">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-[11px] font-black uppercase tracking-tight text-slate-700">{{ event.result || 'КОНТАКТ' }}</span>
                  <span class="text-[9px] font-bold text-slate-400">{{ formatRelativeTime(event.contacted_at) }}</span>
                </div>
                <p class="text-xs text-slate-500 leading-relaxed">{{ event.note }}</p>
              </div>
            </div>
            <div v-if="!contactHistory.length" class="h-full flex flex-col items-center justify-center opacity-30">
              <el-icon :size="48"><ChatLineSquare /></el-icon>
              <p class="text-[10px] font-black uppercase mt-4 tracking-widest">Історія порожня</p>
            </div>
          </div>

          <!-- Quick Action Input -->
          <div class="mt-6 pt-6 border-t border-slate-100">
            <div class="relative group">
              <input 
                v-model="nextContactNote" 
                @keyup.enter="logQuickContact"
                class="workspace-input pr-12" 
                placeholder="Напишіть нотатку та натисніть Enter..." 
              />
              <button @click="logQuickContact" class="absolute right-2 top-2 p-2 bg-indigo-600 text-white rounded-xl shadow-lg shadow-indigo-100 opacity-0 group-focus-within:opacity-100 transition-all">
                <el-icon><Promotion /></el-icon>
              </button>
            </div>
          </div>
        </section>
      </div>

      <!-- RIGHT: FINANCE & CLIENT (Col 3) -->
      <div class="lg:col-span-3 space-y-6">
        
        <!-- Client Profile Card -->
        <section class="bg-slate-900 rounded-[32px] p-8 text-white shadow-2xl relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-32 h-32 bg-indigo-500 blur-[80px] opacity-20 group-hover:opacity-40 transition-opacity"></div>
          
          <div class="flex items-center justify-between mb-8 relative z-10">
            <div class="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center text-xl font-black">
              {{ clientInitials }}
            </div>
            <button @click="openCreateCounterparty" class="p-2 text-white/40 hover:text-white transition-colors">
              <el-icon :size="20"><Plus /></el-icon>
            </button>
          </div>

          <div class="space-y-1 mb-8 relative z-10">
            <el-select
              v-model="form.counterparty_id"
              filterable
              remote
              @change="onClientChange"
              class="workspace-select-dark w-full"
              placeholder="Оберіть клієнта..."
            >
              <el-option v-for="c in counterparties" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <div v-if="form.phone" class="text-xs text-slate-400 font-medium flex items-center gap-2 mt-2">
              <el-icon><Phone /></el-icon> {{ form.phone }}
            </div>
            <div v-if="form.city" class="text-xs text-slate-400 font-medium flex items-center gap-2">
              <el-icon><Position /></el-icon> {{ form.city }}
            </div>
          </div>

          <div class="pt-6 border-t border-white/5 space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-black text-white/30 uppercase tracking-widest">Джерело</span>
              <span class="text-[10px] font-black uppercase text-indigo-400">{{ activeSourceLabel }}</span>
            </div>
            <div class="flex gap-2">
              <button 
                v-for="src in leadSourceIcons.slice(0, 4)" 
                :key="src.id"
                @click="form.lead_source_id = src.id"
                :class="['p-2 rounded-lg border transition-all', form.lead_source_id === src.id ? 'bg-white text-slate-900 border-white' : 'bg-white/5 text-white/30 border-white/5 hover:border-white/20']"
              >
                <el-icon><component :is="src.icon" /></el-icon>
              </button>
            </div>
          </div>
        </section>

        <!-- Finance Intelligence -->
        <section class="bg-white rounded-[32px] p-8 border border-white shadow-sm">
          <div class="space-y-8">
            <div>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Сума замовлення</span>
              <div class="flex items-baseline gap-2">
                <input type="number" v-model="form.total_amount" class="text-3xl font-black text-slate-900 bg-transparent border-none p-0 w-32 focus:ring-0" />
                <span class="text-xl font-bold text-slate-300">₴</span>
              </div>
            </div>

            <div class="p-6 bg-slate-50 rounded-2xl border border-slate-100 space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black text-slate-500 uppercase">Предоплата</span>
                <span :class="['text-[10px] font-black px-2 py-0.5 rounded', form.payment_status === 'paid' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600']">
                  {{ form.payment_status === 'paid' ? 'СПЛАЧЕНО' : 'ОЧІКУЄ' }}
                </span>
              </div>
              <input type="number" v-model="form.prepayment_amount" class="text-xl font-black text-slate-700 bg-transparent border-none p-0 w-full focus:ring-0" />
              <div class="flex gap-2">
                <button v-for="pct in [30, 50, 100]" :key="pct" @click="setPrepayPercent(pct)" class="flex-1 py-1.5 bg-white border border-slate-200 rounded-lg text-[10px] font-black text-slate-500 hover:bg-slate-100 transition-all">{{ pct }}%</button>
              </div>
            </div>

            <button class="w-full py-4 bg-indigo-50 text-indigo-600 rounded-2xl text-[11px] font-black uppercase hover:bg-indigo-100 transition-all flex items-center justify-center gap-2">
              <el-icon><Document /></el-icon> Сформувати Рахунок
            </button>
          </div>
        </section>

        <!-- Deadline Info -->
        <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-[32px] p-8 text-white shadow-xl relative overflow-hidden group">
          <div class="absolute -left-10 -bottom-10 w-40 h-40 bg-white/10 blur-3xl rounded-full transition-all group-hover:scale-110"></div>
          <div class="flex items-center justify-between mb-4 relative z-10">
            <span class="text-[10px] font-black text-indigo-200 uppercase tracking-widest">Дедлайн</span>
            <el-icon :size="20"><Calendar /></el-icon>
          </div>
          <el-date-picker
            v-model="form.deadline_date"
            type="date"
            placeholder="Оберіть дату"
            format="DD MMMM"
            value-format="YYYY-MM-DD"
            class="workspace-datepicker-dark"
          />
          <div class="text-2xl font-black mt-2 relative z-10">{{ form.deadline_date ? formatDateShort(form.deadline_date) : 'Не встановлено' }}</div>
          <div class="text-[10px] font-bold text-indigo-200 uppercase mt-1 opacity-70">Залишилось: {{ getRemainingDays(form.deadline_date) }} дн.</div>
        </section>
      </div>

    </main>

    <!-- Dialogs -->
    <el-dialog v-model="cpDialogVisible" title="Новий Клієнт" width="400px" class="workspace-dialog">
      <div class="space-y-4">
        <div class="space-y-1">
          <label class="text-[10px] font-black uppercase text-slate-400 ml-1">Ім'я Клієнта</label>
          <input v-model="newCp.name" class="workspace-input" placeholder="Олександр П." />
        </div>
        <div class="space-y-1">
          <label class="text-[10px] font-black uppercase text-slate-400 ml-1">Телефон</label>
          <input v-model="newCp.phone" class="workspace-input" placeholder="+380..." />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-2">
          <button @click="cpDialogVisible = false" class="flex-1 py-3 text-[10px] font-black uppercase text-slate-400 hover:text-slate-600">Скасувати</button>
          <button @click="createCounterparty" :loading="creatingCp" class="flex-1 py-3 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase shadow-lg shadow-indigo-100">Створити Клієнта</button>
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
  ArrowLeft, Loading, Box, Van, Calendar, Wallet, Timer, Clock, 
  Promotion, ChatDotRound, Phone, Position, Document, Plus, ChatLineSquare, User
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
const nextContactNote = ref('')
const form = reactive({
  counterparty_id: null,
  lead_source_id:  null,
  order_number:    '',
  warehouse_id:    null,
  product_id:      null,
  crm_stage:       'new',
  channel:         'Viber',
  city:            '',
  phone:           '',
  delivery_type:   'NP',
  attributes_values: {},
  total_amount:     0,
  prepayment_amount: 0,
  payment_status:  'unpaid',
  deadline_date:   null,
  comment:         '',
})

// Dictionaries
const products = ref([])
const counterparties = ref([])
const warehouses = ref([])
const productAttributes = ref([])
const contactHistory = ref([])

const leadSourceIcons = [
  { id: 'phone',       name: 'Дзвінок',       icon: 'Phone' },
  { id: 'instagram',   name: 'Instagram',     icon: 'Camera' },
  { id: 'viber',       name: 'Viber',         icon: 'ChatDotRound' },
  { id: 'telegram',    name: 'Telegram',      icon: 'Promotion' },
  { id: 'website',     name: 'Сайт',          icon: 'Position' },
  { id: 'marketplace', name: 'Market',        icon: 'ShoppingBag' }
]

// COMPUTED
const prepaymentPercent = computed(() => {
  if (!form.total_amount) return 0
  return Math.round((form.prepayment_amount / form.total_amount) * 100)
})

const clientInitials = computed(() => {
  const client = counterparties.value.find(c => c.id === form.counterparty_id)
  if (!client) return '?'
  return client.name.split(' ').map(n => n[0]).join('').toUpperCase()
})

const activeSourceLabel = computed(() => {
  const src = leadSourceIcons.find(s => s.id === form.lead_source_id)
  return src ? src.name : 'Джерело'
})

const matStatusClass = ref('mat-ok')
const matStatusLabel = ref('Матеріали в наявності')

// LOGIC
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatDateShort = (d) => new Date(d).toLocaleDateString('uk-UA', { day: '2-digit', month: 'long' })

const formatRelativeTime = (d) => {
  const diff = new Date() - new Date(d)
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}хв тому`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}год тому`
  return formatDateShort(d)
}

const getEventIcon = (type) => {
  const map = { CALL: 'Phone', CHAT: 'ChatDotRound', SYSTEM: 'Clock' }
  return map[type] || 'Promotion'
}

const getRemainingDays = (dateStr) => {
  if (!dateStr) return 0
  const diff = new Date(dateStr) - new Date()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
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

const logQuickContact = async () => {
  if (!nextContactNote.value || !orderId.value) return
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      note: nextContactNote.value,
      communication_type: 'CHAT'
    })
    nextContactNote.value = ''
    loadContacts()
    ElMessage.success('Нотатку додано')
  } catch (e) { ElMessage.error('Помилка') }
}

const save = async (action) => {
  saving.value = true
  try {
    if (action === 'production') form.crm_stage = 'production'
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Дані збережено')
    if (!orderId.value) router.push(`/crm/order-workspace/${res.data.id}`)
  } catch (e) { ElMessage.error('Помилка') }
  finally { saving.value = false }
}

// Dialog Logic
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
    const [p, wh] = await Promise.all([
      api.get('/api/v1/products?limit=200'),
      api.get('/api/v1/warehouses')
    ])
    products.value = p.data
    warehouses.value = wh.data
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
.workspace-input {
  @apply w-full bg-white border border-slate-100 rounded-2xl px-5 py-3.5 text-sm font-medium 
         text-slate-700 shadow-sm transition-all outline-none 
         focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500/30 placeholder:text-slate-300;
}

.workspace-select .el-input__wrapper {
  @apply !bg-white !border-slate-100 !rounded-2xl !px-4 !py-1 !shadow-sm !transition-all
         hover:!border-indigo-200 focus:!ring-4 focus:!ring-indigo-500/5 !h-[52px];
}

.workspace-select-mini .el-input__wrapper {
  @apply !bg-white/50 !border-slate-50 !rounded-xl !px-3 !py-0 !shadow-none !h-[38px] !text-xs;
}

.workspace-select-dark .el-input__wrapper {
  @apply !bg-white/5 !border-white/5 !rounded-xl !px-4 !py-1 !shadow-none !transition-all
         hover:!border-white/20 !h-[48px] !text-white;
}
.workspace-select-dark .el-input__inner { @apply !text-white !font-black; }

.workspace-datepicker-dark { @apply !w-full !opacity-0 !absolute !inset-0 !cursor-pointer !z-20; }

.workspace-dialog { @apply !rounded-[40px] !border-none !shadow-2xl overflow-hidden; }

.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
