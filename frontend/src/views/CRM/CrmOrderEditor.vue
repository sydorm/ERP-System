<template>
  <div class="min-h-screen bg-[#F8FAFC] p-8 font-inter text-slate-900 antialiased">
    <div class="max-w-[1440px] mx-auto">
      
      <!-- HEADER -->
      <header class="flex items-center justify-between mb-8">
        <div>
          <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Редагування заявки</div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            ORD-00004 
            <span v-if="orderId" class="px-2 py-0.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-indigo-600 shadow-sm">
              {{ form.order_number }}
            </span>
          </h1>
        </div>
        <div class="flex gap-3">
          <button @click="router.back()" class="px-5 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-all shadow-sm">Скасувати</button>
          <button @click="save('production')" :disabled="saving" class="px-6 py-2 bg-[#2563EB] text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-all shadow-sm shadow-blue-200 flex items-center gap-2">
            <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
            Зберегти зміни
          </button>
        </div>
      </header>

      <!-- MAIN GRID -->
      <div class="grid grid-cols-1 lg:grid-cols-[1fr_480px] gap-8">
        
        <!-- LEFT COLUMN (60%) -->
        <div class="space-y-8">
          
          <!-- CARD: Client Data -->
          <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm transition-shadow hover:shadow-md">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-base font-bold text-slate-800 uppercase tracking-tight">Дані клієнта</h2>
              <button @click="openCreateCounterparty" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                <el-icon :size="18"><Plus /></el-icon>
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="md:col-span-2 space-y-1.5">
                <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1 tracking-wider">Пошук клієнта</label>
                <el-select
                  v-model="form.counterparty_id"
                  filterable
                  remote
                  clearable
                  placeholder="Введіть ПІБ або номер телефону..."
                  :remote-method="searchCounterparties"
                  @change="onClientChange"
                  class="minimal-select w-full"
                >
                  <el-option v-for="c in counterparties" :key="c.id" :label="`${c.name} (${c.phone || ''})`" :value="c.id" />
                </el-select>
              </div>
              <div class="space-y-1.5">
                <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1 tracking-wider">Місто</label>
                <input v-model="form.city" class="minimal-input" placeholder="Київ" />
              </div>
              <div class="space-y-1.5">
                <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1 tracking-wider">Телефон</label>
                <input v-model="form.phone" class="minimal-input" placeholder="+380..." />
              </div>
            </div>
          </section>

          <!-- CARD: Product & Specs -->
          <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm transition-shadow hover:shadow-md">
            <h2 class="text-base font-bold text-slate-800 mb-6 uppercase tracking-tight">Виріб та Характеристики</h2>
            <div class="space-y-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-1.5">
                  <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1 tracking-wider">Модель</label>
                  <el-select v-model="form.product_id" filterable @change="onProductChange" class="minimal-select w-full" placeholder="Оберіть модель...">
                    <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </div>
                <div class="space-y-1.5">
                  <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1 tracking-wider">Коментар</label>
                  <textarea v-model="form.comment" class="minimal-input min-h-[42px] py-2" placeholder="Додаткові побажання..."></textarea>
                </div>
              </div>

              <!-- Dynamic Attributes -->
              <div v-if="productAttributes.length" class="grid grid-cols-1 md:grid-cols-3 gap-4 p-5 bg-slate-50 rounded-xl border border-slate-100">
                <div v-for="attr in productAttributes" :key="attr.id" class="space-y-1.5">
                  <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{{ attr.name }}</label>
                  <el-select v-model="form.attributes_values[attr.id]" class="minimal-select-mini w-full">
                    <el-option v-for="v in attr.values" :key="v" :label="v" :value="v" />
                  </el-select>
                </div>
              </div>

              <!-- BOM Status -->
              <div class="flex items-center justify-between p-4 bg-slate-900 rounded-xl text-white">
                <div class="flex items-center gap-3">
                  <el-icon class="text-blue-400"><MagicStick /></el-icon>
                  <span class="text-[11px] font-bold uppercase tracking-wider">Аналіз матеріалів</span>
                </div>
                <span :class="['text-[10px] font-black uppercase px-2 py-0.5 rounded', matStatusClass === 'mat-ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400']">
                  {{ matStatusLabel }}
                </span>
              </div>
            </div>
          </section>
        </div>

        <!-- RIGHT COLUMN (40%) -->
        <div class="space-y-8">
          
          <!-- CARD: Source Selection (Segmented Control) -->
          <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm transition-shadow hover:shadow-md">
            <h2 class="text-base font-bold text-slate-800 mb-6 uppercase tracking-tight">Джерело клієнта</h2>
            <div class="grid grid-cols-3 gap-2">
              <button 
                v-for="src in leadSources" :key="src.id"
                @click="form.lead_source_id = src.id"
                :class="[
                  'flex flex-col items-center gap-2 py-3 rounded-lg border transition-all',
                  form.lead_source_id === src.id 
                    ? 'bg-blue-50 border-blue-500 text-blue-600 shadow-sm ring-1 ring-blue-500' 
                    : 'bg-white border-slate-100 text-slate-400 hover:border-slate-300 hover:bg-slate-50'
                ]"
              >
                <el-icon :size="18"><component :is="src.icon" /></el-icon>
                <span class="text-[10px] font-bold uppercase tracking-wider">{{ src.name }}</span>
              </button>
            </div>
          </section>

          <!-- CARD: Sales Progress -->
          <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm transition-shadow hover:shadow-md">
            <div class="flex items-end justify-between mb-6">
              <div>
                <h2 class="text-base font-bold text-slate-800 uppercase tracking-tight mb-1">Продаж</h2>
                <div class="flex items-baseline gap-1">
                  <input type="number" v-model="form.total_amount" class="text-24 font-black text-[#2563EB] bg-transparent border-none p-0 w-32 focus:ring-0" />
                  <span class="text-lg font-bold text-blue-300">₴</span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Оплачено</div>
                <div class="text-lg font-bold text-slate-700">{{ prepaymentPercent }}%</div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full bg-[#2563EB] transition-all duration-500 shadow-[0_0_12px_rgba(37,99,235,0.4)]" :style="{ width: `${prepaymentPercent}%` }"></div>
              </div>
              
              <div class="flex items-center gap-3">
                <div class="flex-1 space-y-1.5">
                  <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Предоплата</label>
                  <input type="number" v-model="form.prepayment_amount" class="minimal-input font-bold" />
                </div>
                <div class="flex flex-wrap gap-1 pt-5">
                  <button v-for="pct in [20, 30, 50, 100]" :key="pct" @click="setPrepayPercent(pct)" class="px-2 py-1 bg-slate-50 border border-slate-200 rounded text-[10px] font-bold text-slate-500 hover:bg-slate-100 transition-all">{{ pct }}%</button>
                </div>
              </div>
            </div>
          </section>

          <!-- CARD: Activity Timeline -->
          <section class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm transition-shadow hover:shadow-md">
            <h2 class="text-base font-bold text-slate-800 mb-8 uppercase tracking-tight">Activity Timeline</h2>
            <div class="space-y-8 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-px before:bg-slate-100">
              <div v-for="event in contactHistory.slice(0, 5)" :key="event.id" class="relative pl-8 group">
                <div class="absolute left-0 top-1.5 w-4 h-4 rounded-full bg-white border-2 border-emerald-500 z-10 transition-transform group-hover:scale-125">
                  <div class="w-full h-full bg-emerald-500 rounded-full scale-0 group-hover:scale-50 transition-transform"></div>
                </div>
                <div class="space-y-1">
                  <div class="flex items-center gap-3">
                    <span class="px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded text-[9px] font-black uppercase tracking-widest">Підтверджено</span>
                    <span class="text-[10px] font-bold text-slate-400">{{ formatRelativeTime(event.contacted_at) }}</span>
                  </div>
                  <div class="text-[13px] font-medium text-slate-600 leading-snug">{{ event.note }}</div>
                </div>
              </div>
              <div v-if="!contactHistory.length" class="pl-8 text-xs text-slate-400 italic">Історія порожня...</div>
            </div>
          </section>

        </div>
      </div>
    </div>

    <!-- Create Client Dialog -->
    <el-dialog v-model="cpDialogVisible" title="Новий Клієнт" width="400px" class="minimal-dialog">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1">Ім'я</label>
          <input v-model="newCp.name" class="minimal-input" placeholder="ПІБ Клієнта" />
        </div>
        <div class="space-y-1.5">
          <label class="text-[11px] font-semibold text-slate-500 uppercase ml-1">Телефон</label>
          <input v-model="newCp.phone" class="minimal-input" placeholder="+380..." />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-2">
          <button @click="cpDialogVisible = false" class="flex-1 py-2 text-slate-500 font-bold uppercase text-[11px]">Скасувати</button>
          <button @click="createCounterparty" :loading="creatingCp" class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold uppercase text-[11px] shadow-lg shadow-blue-100">Створити</button>
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
  Phone, Camera, ChatDotRound, Promotion, Position, ShoppingBag, 
  Plus, Loading, MagicStick, Timer, Clock, Wallet, Van, Calendar 
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
const form = reactive({
  counterparty_id: null,
  lead_source_id: 'instagram',
  city: '',
  phone: '',
  product_id: null,
  attributes_values: {},
  total_amount: 0,
  prepayment_amount: 0,
  comment: '',
  crm_stage: 'new',
  order_number: ''
})

const products = ref([])
const counterparties = ref([])
const productAttributes = ref([])
const materials = ref([])
const contactHistory = ref([])

const leadSources = [
  { id: 'phone', name: 'Дзвінок', icon: 'Phone' },
  { id: 'instagram', name: 'Instagram', icon: 'Camera' },
  { id: 'viber', name: 'Viber', icon: 'ChatDotRound' },
  { id: 'telegram', name: 'Telegram', icon: 'Promotion' },
  { id: 'website', name: 'Сайт', icon: 'Position' },
  { id: 'marketplace', name: 'Market', icon: 'ShoppingBag' }
]

// LOGIC
const prepaymentPercent = computed(() => {
  if (!form.total_amount) return 0
  return Math.round((form.prepayment_amount / form.total_amount) * 100)
})

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
}

const formatDate = (d) => new Date(d).toLocaleDateString('uk-UA', { day: '2-digit', month: 'short' })
const formatRelativeTime = (d) => {
  const diff = new Date() - new Date(d)
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}хв тому`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}год тому`
  return formatDate(d)
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
  checkMaterials()
}

const checkMaterials = async () => {
  if (!form.product_id) return
  const res = await api.get(`/api/v1/crm/orders/check-materials?product_id=${form.product_id}`)
  materials.value = res.data.items || []
}

const matStatusClass = computed(() => materials.value.some(m => m.status === 'missing') ? 'mat-error' : 'mat-ok')
const matStatusLabel = computed(() => materials.value.some(m => m.status === 'missing') ? 'Дефіцит матеріалів' : 'Все в наявності')

const loadContacts = async () => {
  if (!orderId.value) return
  const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
  contactHistory.value = res.data
}

const save = async (action) => {
  saving.value = true
  try {
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Заявку оновлено')
    if (!orderId.value) router.push(`/crm/orders/${res.data.id}`)
  } catch (e) { ElMessage.error('Помилка збереження') }
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
    const p = await api.get('/api/v1/products?limit=200')
    products.value = p.data
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}`)
      Object.assign(form, res.data)
      loadContacts()
      if (form.product_id) onProductChange(form.product_id)
    }
  } finally { loading.value = false }
}

onMounted(loadData)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.font-inter { font-family: 'Inter', sans-serif; }

.minimal-input {
  @apply w-full bg-white border border-slate-200 rounded-lg px-4 py-2.5 text-sm 
         text-slate-700 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-50/50 placeholder:text-slate-300;
}

.minimal-select .el-input__wrapper {
  @apply !bg-white !border-slate-200 !rounded-lg !px-4 !py-1 !shadow-none !transition-all
         hover:!border-slate-300 focus:!border-blue-500 focus:!ring-4 focus:!ring-blue-50/50 !h-[44px];
}

.minimal-select-mini .el-input__wrapper {
  @apply !bg-white !border-slate-100 !rounded-md !px-2 !py-0 !shadow-none !h-[34px];
}

.minimal-dialog { @apply !rounded-2xl !border-none !shadow-2xl; }

.text-24 { font-size: 24px; }
</style>
