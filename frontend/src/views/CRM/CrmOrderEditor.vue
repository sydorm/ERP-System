<template>
  <div class="min-h-screen bg-[#F8FAFC] p-4 md:p-8 font-sans antialiased text-slate-900">
    <div class="max-w-[1600px] mx-auto">
      
      <!-- ─── HEADER (Premium Action Bar) ─── -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 px-2">
        <div class="space-y-1">
          <nav class="flex gap-2 text-[10px] font-bold text-indigo-500/50 uppercase tracking-[2px] mb-2">
            <span>CRM</span>
            <span>/</span>
            <span>Заявка</span>
            <span v-if="orderId" class="text-indigo-600/30">#{{ form.order_number }}</span>
          </nav>
          <h1 class="text-3xl font-black tracking-tight text-slate-900 flex items-center gap-4">
            {{ orderId ? 'Редагування заявки' : 'Нова заявка' }}
            <span v-if="orderId" class="px-3 py-1 bg-white border border-gray-100 rounded-lg text-sm font-medium text-slate-400 shadow-sm">
              {{ form.order_number }}
            </span>
          </h1>
        </div>
        <div class="flex items-center gap-3">
          <button 
            @click="save('draft')"
            class="px-6 py-3 bg-white border border-gray-200 rounded-2xl text-xs font-bold text-gray-500 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm active:scale-95"
          >
            Записати чернетку
          </button>
          <button 
            @click="save('production')"
            :disabled="saving"
            class="px-8 py-3 bg-indigo-600 rounded-2xl text-xs font-bold text-white hover:bg-indigo-700 shadow-[0_10px_20px_rgba(79,70,229,0.2)] hover:shadow-[0_15px_30px_rgba(79,70,229,0.3)] transition-all active:scale-95 flex items-center gap-2"
          >
            <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
            Зберегти та передати
          </button>
        </div>
      </div>

      <!-- ─── MAIN LAYOUT (70/30 CSS Grid) ─── -->
      <div class="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-10 items-start">
        
        <!-- LEFT COLUMN: Main Workspace (70%) -->
        <div class="space-y-10">
          
          <!-- SECTION 1: Client Block -->
          <section id="section-client" class="bg-white/80 backdrop-blur-xl border border-gray-100 rounded-[32px] p-8 shadow-[0_8px_40px_rgba(0,0,0,0.02)] ring-1 ring-black/[0.03] transition-all hover:shadow-[0_12px_50px_rgba(0,0,0,0.04)]">
            <div class="flex items-center gap-4 mb-8">
              <div class="p-3 bg-indigo-50 rounded-2xl text-indigo-600 shadow-inner">
                <el-icon :size="20"><User /></el-icon>
              </div>
              <div class="space-y-0.5">
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest">Дані клієнта</h2>
                <p class="text-[11px] text-slate-400 font-medium">Основна інформація про замовника</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <!-- Autocomplete Client Search -->
              <div class="md:col-span-2 space-y-2">
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Пошук або створення</label>
                <div class="relative group">
                  <el-select
                    v-model="form.counterparty_id"
                    filterable
                    remote
                    placeholder="Введіть ім'я або телефон..."
                    :remote-method="searchCounterparties"
                    @change="onClientChange"
                    class="saas-select-premium w-full"
                  >
                    <el-option
                      v-for="item in counterparties"
                      :key="item.id"
                      :label="`${item.name} (${item.phone})`"
                      :value="item.id"
                    />
                    <template #footer>
                      <div class="p-2 border-t border-gray-50">
                        <button @click="openCreateCounterparty" class="w-full py-2 bg-indigo-50 text-indigo-600 text-[11px] font-bold rounded-lg hover:bg-indigo-100 transition-colors">
                          + СТВОРИТИ НОВОГО КЛІЄНТА
                        </button>
                      </div>
                    </template>
                  </el-select>
                </div>
              </div>

              <!-- Source Chips -->
              <div class="space-y-2">
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Джерело клієнта</label>
                <div class="flex flex-wrap gap-2">
                  <button 
                    v-for="src in leadSourceIcons" 
                    :key="src.id"
                    @click="form.lead_source_id = src.id"
                    :class="[
                      'flex items-center gap-2 px-3 py-2 rounded-xl border text-[11px] font-bold transition-all shadow-sm',
                      form.lead_source_id === src.id 
                        ? 'bg-indigo-600 border-indigo-600 text-white shadow-indigo-200' 
                        : 'bg-white border-gray-100 text-slate-500 hover:border-indigo-300'
                    ]"
                  >
                    <el-icon :size="14"><component :is="src.icon" /></el-icon>
                    <span>{{ src.name }}</span>
                  </button>
                </div>
              </div>

              <!-- Additional Client Fields -->
              <div class="space-y-2">
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Місто</label>
                <input v-model="form.city" class="saas-input-premium" placeholder="Київ" />
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Телефон (для швидкого зв'язку)</label>
                <input v-model="form.phone" class="saas-input-premium" placeholder="+38 (0XX) XXX-XX-XX" />
              </div>
            </div>
          </section>

          <!-- SECTION 2: Nomenclature Block -->
          <section id="section-product" class="bg-white/80 border border-gray-100 rounded-[32px] p-8 shadow-[0_8px_40px_rgba(0,0,0,0.02)] ring-1 ring-black/[0.03]">
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-4">
                <div class="p-3 bg-amber-50 rounded-2xl text-amber-600 shadow-inner">
                  <el-icon :size="20"><Box /></el-icon>
                </div>
                <div class="space-y-0.5">
                  <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest">Виріб та Характеристики</h2>
                  <p class="text-[11px] text-slate-400 font-medium">Конфігурація замовлення</p>
                </div>
              </div>
            </div>

            <div class="space-y-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="space-y-2">
                  <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Оберіть модель</label>
                  <el-select v-model="form.product_id" filterable @change="onProductChange" class="saas-select-premium w-full">
                    <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Коментар до замовлення</label>
                  <textarea v-model="form.comment" class="saas-input-premium min-h-[46px] py-2.5" placeholder="Додаткові побажання..."></textarea>
                </div>
              </div>

              <!-- Dynamic Attributes (Specs) -->
              <div v-if="productAttributes.length" class="p-6 bg-slate-50/50 rounded-3xl border border-slate-100/50 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="attr in productAttributes" :key="attr.id" class="space-y-2">
                  <label class="text-[10px] font-bold text-slate-400 uppercase ml-1">{{ attr.name }}</label>
                  <el-select v-model="form.attributes_values[attr.id]" class="saas-select-mini w-full">
                    <el-option v-for="v in attr.values" :key="v" :label="v" :value="v" />
                  </el-select>
                </div>
              </div>

              <!-- SECTION 3: Inventory Analysis -->
              <div class="p-6 bg-gradient-to-br from-indigo-900 to-slate-900 rounded-[28px] text-white shadow-xl relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-white/5 blur-3xl rounded-full -mr-32 -mt-32"></div>
                <div class="flex items-center justify-between mb-6 relative">
                  <div class="flex items-center gap-3">
                    <el-icon class="text-indigo-400 animate-pulse"><MagicStick /></el-icon>
                    <span class="text-[10px] font-black uppercase tracking-[2px]">Аналіз залишків BOM</span>
                  </div>
                  <div :class="['px-3 py-1 rounded-full text-[10px] font-black uppercase', matStatusClass === 'mat-ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400']">
                    {{ matStatusLabel }}
                  </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4 relative">
                  <div v-for="mat in materials" :key="mat.id" class="flex items-center justify-between group">
                    <span class="text-xs text-indigo-100/70 font-medium">{{ mat.name }}</span>
                    <div class="flex items-center gap-3">
                      <div class="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          class="h-full transition-all duration-1000" 
                          :style="{ width: mat.status === 'missing' ? '20%' : '100%', background: mat.status === 'missing' ? '#fb7185' : '#34d399' }"
                        ></div>
                      </div>
                      <span :class="['text-[9px] font-bold uppercase', mat.status === 'missing' ? 'text-rose-400' : 'text-emerald-400']">
                        {{ mat.status === 'missing' ? 'ДЕФІЦИТ' : 'ОК' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- SECTION 4: Logistics & Deadline Block -->
          <section id="section-analysis" class="bg-white/80 border border-gray-100 rounded-[32px] p-8 shadow-[0_8px_40px_rgba(0,0,0,0.02)] ring-1 ring-black/[0.03]">
            <div class="flex items-center gap-4 mb-8">
              <div class="p-3 bg-emerald-50 rounded-2xl text-emerald-600 shadow-inner">
                <el-icon :size="20"><Truck /></el-icon>
              </div>
              <div class="space-y-0.5">
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest">Логістика та Дедлайни</h2>
                <p class="text-[11px] text-slate-400 font-medium">Спосіб відвантаження та термін готовності</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div class="space-y-6">
                <div class="space-y-2">
                  <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Метод відвантаження</label>
                  <el-select v-model="form.delivery_type" class="saas-select-premium w-full">
                    <el-option label="Нова Пошта" value="NP" />
                    <el-option label="Самовивіз" value="PICKUP" />
                    <el-option label="Кур'єр" value="COURIER" />
                  </el-select>
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black text-slate-400 uppercase tracking-wider ml-1">Склад відправки</label>
                  <el-select v-model="form.warehouse_id" class="saas-select-premium w-full">
                    <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
                  </el-select>
                </div>
              </div>
              <div class="relative group cursor-pointer" @click="currentSection = 'deadline'">
                <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-500"></div>
                <div class="relative bg-white border border-gray-100 rounded-3xl p-6 h-full flex flex-col justify-between shadow-sm">
                  <div class="flex items-center justify-between">
                    <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest">Дедлайн виготовлення</span>
                    <el-icon class="text-indigo-200"><Calendar /></el-icon>
                  </div>
                  <el-date-picker
                    v-model="form.deadline_date"
                    type="date"
                    placeholder="Оберіть дату"
                    format="DD MMMM, YYYY"
                    value-format="YYYY-MM-DD"
                    class="saas-datepicker-invisible"
                  />
                  <div class="text-2xl font-black text-slate-800 mt-2">
                    {{ form.deadline_date ? formatDate(form.deadline_date) : 'Оберіть дату' }}
                  </div>
                  <div v-if="form.deadline_date" class="text-[10px] text-indigo-400 font-bold uppercase mt-2">
                    Залишилось: {{ getRemainingDays(form.deadline_date) }} роб. дні
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- RIGHT COLUMN: Sidebar (30%) -->
        <aside class="space-y-8 sticky top-8">
          
          <!-- SECTION 5: Finance Summary -->
          <div class="bg-slate-900 rounded-[40px] p-8 shadow-2xl text-white relative overflow-hidden border border-white/5">
            <div class="absolute top-0 right-0 w-48 h-48 bg-indigo-500/20 blur-3xl rounded-full -mr-24 -mt-24"></div>
            <div class="flex items-center gap-3 mb-10 opacity-60">
              <el-icon :size="16"><Wallet /></el-icon>
              <span class="text-[10px] font-black uppercase tracking-[3px]">Finance Summary</span>
            </div>
            
            <div class="space-y-8">
              <div>
                <label class="text-[11px] text-indigo-300/70 font-bold uppercase tracking-wider mb-2 block">Загальна сума</label>
                <div class="flex items-baseline gap-2">
                  <input 
                    type="number" 
                    v-model="form.total_amount" 
                    class="bg-transparent text-4xl font-black tracking-tight text-white border-none focus:ring-0 w-full p-0"
                  />
                  <span class="text-2xl opacity-30 font-light">₴</span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-white/5 rounded-2xl border border-white/10 group hover:bg-white/10 transition-all">
                  <label class="text-[10px] text-gray-500 uppercase font-black mb-1 block">Предоплата</label>
                  <div class="text-base font-bold">{{ formatCurrency(form.prepayment_amount) }} ₴</div>
                </div>
                <div :class="['p-4 rounded-2xl border transition-all', form.payment_status === 'paid' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-amber-500/10 border-amber-500/20']">
                  <label class="text-[10px] text-gray-500 uppercase font-black mb-1 block">Статус</label>
                  <div :class="['text-sm font-bold', form.payment_status === 'paid' ? 'text-emerald-400' : 'text-amber-400']">
                    {{ form.payment_status === 'paid' ? 'СПЛАЧЕНО' : 'ОЧІКУЄ' }}
                  </div>
                </div>
              </div>

              <!-- Prepayment Presets -->
              <div class="flex gap-2">
                <button 
                  v-for="pct in [30, 50, 100]" 
                  :key="pct"
                  @click="setPrepayPercent(pct)"
                  class="flex-1 py-2 rounded-xl border border-white/10 text-[10px] font-black uppercase hover:bg-white/5 transition-all"
                >
                  {{ pct }}%
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION 6: Communication Channel & History -->
          <div class="bg-white rounded-[40px] border border-gray-100 p-8 shadow-[0_15px_50px_rgba(0,0,0,0.02)] ring-1 ring-black/[0.02]">
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-2">
                <el-icon class="text-slate-400"><Timer /></el-icon>
                <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Activity Timeline</span>
              </div>
              <div class="flex gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-[10px] font-black text-slate-900 uppercase italic">{{ form.channel }}</span>
              </div>
            </div>

            <div class="space-y-6 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-px before:bg-slate-100">
              <div v-for="log in contactHistory.slice(0, 3)" :key="log.id" class="relative pl-10 group">
                <div class="absolute left-1.5 top-1 w-3 h-3 rounded-full bg-white border-2 border-slate-200 group-hover:border-indigo-500 transition-colors"></div>
                <div class="space-y-1">
                  <div class="flex items-center justify-between">
                    <span :class="['text-[11px] font-black uppercase tracking-tight', log.result === 'REFUSED' ? 'text-rose-500' : 'text-slate-800']">
                      {{ getResultHint(log.result) || log.result }}
                    </span>
                    <span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">{{ formatRelativeTime(log.contacted_at) }}</span>
                  </div>
                  <p class="text-[11px] text-slate-500 leading-relaxed font-medium line-clamp-2 italic">"{{ log.note }}"</p>
                </div>
              </div>
              <div v-if="!contactHistory.length" class="pl-10 text-[11px] text-slate-400 font-medium italic">
                Історія взаємодії порожня...
              </div>
            </div>
          </div>

          <!-- SECTION 8: Future Communication (Next Step) -->
          <div class="bg-indigo-600 rounded-[40px] p-8 text-white shadow-[0_20px_60px_rgba(79,70,229,0.35)] relative overflow-hidden group">
            <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-white/10 blur-3xl rounded-full transition-all group-hover:scale-150"></div>
            <div class="flex items-center gap-3 mb-6 relative">
              <el-icon class="text-indigo-200"><Clock /></el-icon>
              <span class="text-[10px] font-black uppercase tracking-widest">Наступний крок</span>
            </div>
            
            <textarea 
              v-model="form.next_contact_comment"
              class="w-full bg-white/10 border border-white/20 rounded-2xl p-4 text-xs font-medium placeholder:text-indigo-200 focus:outline-none focus:bg-white/20 transition-all resize-none h-24 mb-4 relative z-10"
              placeholder="Що потрібно зробити наступним кроком?"
            ></textarea>
            
            <div class="flex items-center justify-between relative z-10">
              <div class="space-y-1">
                <span class="text-[9px] font-bold text-indigo-200 uppercase tracking-widest block">Заплановано на:</span>
                <div class="text-xs font-black">{{ form.next_contact_at ? formatDate(form.next_contact_at) : 'Час не вказано' }}</div>
              </div>
              <button 
                @click="onLogContact"
                class="p-4 bg-white rounded-2xl text-indigo-600 hover:scale-105 active:scale-95 transition-all shadow-xl"
              >
                <el-icon :size="20"><Promotion /></el-icon>
              </button>
            </div>
          </div>

        </aside>
      </div>

    </div>

    <!-- CREATE CLIENT DIALOG (Premium Styling) -->
    <el-dialog v-model="cpDialogVisible" title="Новий Клієнт" width="420px" class="saas-dialog-premium">
      <div class="space-y-6 p-2">
        <div class="space-y-2">
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Ім'я та Прізвище</label>
          <input v-model="newCp.name" class="saas-input-premium" placeholder="Олександр Коваленко" />
        </div>
        <div class="space-y-2">
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Номер телефону</label>
          <input v-model="newCp.phone" class="saas-input-premium" placeholder="+38 (0XX) XXX-XX-XX" />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 px-2 pb-2">
          <button @click="cpDialogVisible = false" class="flex-1 py-3 bg-slate-50 text-slate-500 text-[11px] font-black uppercase rounded-2xl hover:bg-slate-100 transition-all">Скасувати</button>
          <button @click="createCounterparty" :loading="creatingCp" class="flex-1 py-3 bg-indigo-600 text-white text-[11px] font-black uppercase rounded-2xl hover:bg-indigo-700 shadow-lg transition-all">Створити</button>
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
  User, Box, MagicStick, Truck, Calendar, Wallet, Timer, Clock, 
  Promotion, Loading, Bell, ChatDotRound, Camera, Phone, MoreFilled, Star, Position, Refresh, ShoppingBag, More
} from '@element-plus/icons-vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { validateCrmOrderRequiredFields, collectMissingProductionFields } from './composables/useCrmOrderValidation'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const orderId = computed(() => {
  const id = route.params.id
  return (id && id !== 'new') ? id : null
})

// ─── STATE ───
const loading = ref(true)
const saving = ref(false)
const currentSection = ref('client')

const form = reactive({
  counterparty_id: null,
  lead_source_id:  null,
  order_number:    '',
  warehouse_id:    null,
  product_id:      null,
  crm_stage:       'new',
  channel:         'Viber',
  city:            '',
  delivery_type:   'NP',
  attributes_values: {},
  total_amount:     0,
  prepayment_amount: 0,
  payment_status:  'unpaid',
  deadline_date:   null,
  next_contact_at: null,
  next_contact_comment: '',
  comment:         '',
})

// Dictionaries
const products = ref([])
const counterparties = ref([])
const warehouses = ref([])
const productAttributes = ref([])
const materials = ref([])
const contactHistory = ref([])

const leadSourceIcons = [
  { id: 'phone',       name: 'Дзвінок',       icon: 'Phone' },
  { id: 'instagram',   name: 'Instagram',     icon: 'Camera' },
  { id: 'viber',       name: 'Viber',         icon: 'ChatDotRound' },
  { id: 'telegram',    name: 'Telegram',      icon: 'Promotion' },
  { id: 'website',     name: 'Сайт',          icon: 'Position' },
  { id: 'marketplace', name: 'Market',        icon: 'ShoppingBag' }
]

// ─── LOGIC ───
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatDate = (d) => new Date(d).toLocaleDateString('uk-UA', { day: '2-digit', month: 'long' })

const getRemainingDays = (dateStr) => {
  const diff = new Date(dateStr) - new Date()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

const formatRelativeTime = (d) => {
  const diff = new Date() - new Date(d)
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins} хв тому`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} год тому`
  return formatDate(d)
}

const getResultHint = (res) => {
  const map = { REFUSED: 'Відмова', CONFIRMED: 'Підтверджено', THINKING: 'Думає', NO_ANSWER: 'Не відповів' }
  return map[res] || res
}

const setPrepayPercent = (pct) => {
  form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
}

const searchCounterparties = async (query) => {
  if (!query || query.length < 2) return
  const res = await api.get(`/api/v1/counterparties?search=${query}&is_customer=true&limit=10`)
  counterparties.value = res.data
}

const onClientChange = (id) => {
  if (id) loadContacts()
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
const matStatusLabel = computed(() => materials.value.some(m => m.status === 'missing') ? 'Дефіцит матеріалів' : 'Матеріали в наявності')

const loadContacts = async () => {
  if (!orderId.value) return
  const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
  contactHistory.value = res.data
}

const save = async (action) => {
  saving.value = true
  try {
    if (action === 'production') form.crm_stage = 'production'
    const method = orderId.value ? 'patch' : 'post'
    const url = orderId.value ? `/api/v1/orders/${orderId.value}` : '/api/v1/orders'
    const res = await api[method](url, form)
    ElMessage.success('Заявку збережено успішно')
    if (!orderId.value) router.push(`/crm/orders/${res.data.id}`)
  } catch (e) {
    ElMessage.error('Помилка при збереженні')
  } finally {
    saving.value = false
  }
}

// Create CP
const cpDialogVisible = ref(false)
const creatingCp = ref(false)
const newCp = reactive({ name: '', phone: '' })
const openCreateCounterparty = () => { cpDialogVisible.value = true }
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
      const o = res.data
      Object.assign(form, o)
      
      // Fix types for numeric fields
      form.total_amount = Number(o.total_amount)
      form.prepayment_amount = Number(o.prepayment_amount || 0)

      loadContacts()
      if (form.product_id) onProductChange(form.product_id)
    }
  } finally { loading.value = false }
}

const onLogContact = async () => {
  if (!orderId.value) return
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      note: form.next_contact_comment,
      next_contact_at: form.next_contact_at,
      communication_type: 'CALL'
    })
    ElMessage.success('Заплановано')
    loadContacts()
  } catch (e) {
    ElMessage.error('Помилка планування')
  }
}

onMounted(loadData)
</script>

<style>
/* ─── Premium SaaS Styling ─── */

.saas-input-premium {
  @apply w-full bg-white border border-gray-100 rounded-2xl px-5 py-3 text-sm font-medium 
         text-slate-700 shadow-sm transition-all outline-none 
         focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500/50 placeholder:text-slate-300;
}

.saas-select-premium .el-input__wrapper {
  @apply !bg-white !border-gray-100 !rounded-2xl !px-4 !py-1 !shadow-sm !transition-all
         hover:!border-indigo-300 focus:!ring-4 focus:!ring-indigo-500/5 !h-[48px];
}

.saas-select-mini .el-input__wrapper {
  @apply !bg-white/50 !border-gray-100 !rounded-xl !px-3 !py-0 !shadow-none !h-[36px];
}

.saas-datepicker-invisible {
  @apply !absolute !inset-0 !opacity-0 !cursor-pointer !w-full !h-full;
}

.saas-dialog-premium {
  @apply !rounded-[32px] !border-none !shadow-2xl overflow-hidden;
}

.saas-dialog-premium .el-dialog__header {
  @apply !pt-8 !px-8 !m-0;
}
.saas-dialog-premium .el-dialog__title {
  @apply !text-sm !font-black !uppercase !tracking-[2px] !text-slate-800;
}

/* Hide original Element Plus styles we override */
.el-select-dropdown__item.selected { @apply !text-indigo-600 !font-bold; }
</style>
