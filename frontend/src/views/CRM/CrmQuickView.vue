<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { 
  Close, Phone, ChatDotRound, Position, Link, 
  Clock, CircleCheck, Warning, MagicStick, Star, Calendar
} from '@element-plus/icons-vue';
import api from '@/api';
import { ElMessage } from 'element-plus';

// Define Props
const props = defineProps({
  show: { type: Boolean, required: true },
  order: { type: Object, default: null }
});

// Define Emits
const emit = defineEmits(['close', 'openFull']);

const STEPS = ['new', 'processing', 'confirmed', 'payment', 'production', 'done'];

const STEP_LABELS = {
  'new': 'Нові',
  'processing': 'В роботі',
  'confirmed': 'Підтверджено',
  'payment': 'Оплата',
  'production': 'Виробництво',
  'done': 'Виконано'
};

const history = ref([]);
const loadingHistory = ref(false);
const contactForm = ref({
  type: '📞 Дзвінок',
  result: 'Не відповів',
  comment: '',
  next_contact: ''
});

const currentStepIndex = computed(() => {
  if (!props.order) return -1;
  return STEPS.indexOf(props.order.crm_stage);
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', { 
    style: 'currency', 
    currency: 'UAH',
    maximumFractionDigits: 0 
  }).format(value || 0);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const fetchHistory = async () => {
  if (!props.order?.id) return;
  loadingHistory.value = true;
  try {
    const res = await api.get(`/api/v1/crm/orders/${props.order.id}/contacts`);
    history.value = res.data;
  } catch (e) {
    console.error('Failed to fetch history', e);
  } finally {
    loadingHistory.value = false;
  }
};

const saveContact = async () => {
  if (!props.order?.id) return;
  try {
    await api.post(`/api/v1/crm/orders/${props.order.id}/contacts`, {
      type: contactForm.value.type,
      result: contactForm.value.result,
      comment: contactForm.value.comment,
      next_contact: contactForm.value.next_contact
    });
    ElMessage.success('Контакт збережено');
    fetchHistory();
    // Reset but keep type
    contactForm.value.comment = '';
    contactForm.value.next_contact = '';
  } catch (e) {
    ElMessage.error('Помилка збереження');
  }
};

watch(() => props.show, (newVal) => {
  if (newVal && props.order) {
    fetchHistory();
  }
});
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="show" 
        class="fixed inset-0 bg-slate-900/10 backdrop-blur-[2px] z-[45]" 
        @click="emit('close')"
      />
    </Transition>

    <!-- Drawer Panel -->
    <Transition
      enter-active-class="transition-transform duration-500 ease-out"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-500 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div 
        v-if="show && order" 
        class="fixed right-0 top-0 h-full w-[380px] bg-white shadow-[-20px_0_60px_rgba(0,0,0,0.15)] z-50 border-l border-slate-200 overflow-y-auto flex flex-col"
      >
        <!-- HEADER -->
        <div class="sticky top-0 bg-white/90 backdrop-blur-md border-b border-slate-100 p-5 z-20">
          <div class="flex items-center justify-between mb-6">
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">#{{ order.order_number }}</span>
            <button @click="emit('close')" class="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-900">
              <el-icon class="w-5 h-5"><Close /></el-icon>
            </button>
          </div>

          <!-- Mini Status Stepper -->
          <div class="flex items-center justify-between px-2 mb-6">
            <div v-for="(step, index) in STEPS" :key="step" class="flex flex-col items-center flex-1 relative">
              <div 
                class="w-2 h-2 rounded-full z-10 transition-all duration-300"
                :class="index <= currentStepIndex ? 'bg-indigo-600 ring-4 ring-indigo-50' : 'bg-slate-200'"
              />
              <span 
                class="text-[8px] mt-2 font-black uppercase tracking-tighter"
                :class="index === currentStepIndex ? 'text-indigo-600' : 'text-slate-400'"
              >
                {{ STEP_LABELS[step]?.substring(0, 3) }}
              </span>
              <!-- Line Connector -->
              <div 
                v-if="index < STEPS.length - 1"
                class="absolute top-[4px] left-[50%] w-full h-[1px] -z-0"
                :class="index < currentStepIndex ? 'bg-indigo-600' : 'bg-slate-100'"
              />
            </div>
          </div>

          <!-- Deadline Chip -->
          <div class="px-1">
             <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-100 text-amber-600">
               <el-icon class="w-3.5 h-3.5"><Clock /></el-icon>
               <span class="text-[10px] font-black uppercase tracking-wide">Дедлайн: {{ formatDate(order.deadline)?.split(',')[0] || '—' }}</span>
             </div>
          </div>
        </div>

        <!-- CONTENT SCROLL AREA -->
        <div class="flex-1 p-6 space-y-10">
          <!-- Section: Клієнт -->
          <section class="space-y-3">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Клієнт</h3>
            <h2 @click="emit('openFull')" class="text-2xl font-black text-slate-900 tracking-tight leading-tight hover:text-indigo-600 cursor-pointer transition-all flex items-center gap-2 group/name">
              {{ order.client_name || '—' }}
              <el-icon class="w-4 h-4 opacity-0 group-hover/name:opacity-100 group-hover/name:translate-x-1 transition-all"><Link /></el-icon>
            </h2>
            <div class="flex flex-col gap-2">
              <a :href="`tel:${order.client_phone}`" class="text-base font-black text-indigo-600 hover:scale-[1.02] origin-left transition-transform w-fit">{{ order.client_phone || '—' }}</a>
              <div class="flex gap-4 mt-1">
                 <div class="p-2 bg-emerald-50 rounded-lg cursor-pointer hover:bg-emerald-100 transition-colors"><el-icon class="w-4 h-4 text-emerald-600"><Phone /></el-icon></div>
                 <div class="p-2 bg-indigo-50 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors"><el-icon class="w-4 h-4 text-indigo-600"><ChatDotRound /></el-icon></div>
                 <div class="p-2 bg-sky-50 rounded-lg cursor-pointer hover:bg-sky-100 transition-colors"><el-icon class="w-4 h-4 text-sky-600"><Position /></el-icon></div>
                 <div class="p-2 bg-pink-50 rounded-lg cursor-pointer hover:bg-pink-100 transition-colors"><el-icon class="w-4 h-4 text-pink-600"><Star /></el-icon></div>
              </div>
            </div>
            <p class="text-[11px] font-black text-slate-400 uppercase tracking-wider">📍 {{ order.city || 'Київ' }} · Доставка: {{ order.delivery_service || 'НП' }}</p>
          </section>

          <!-- Section: Виріб -->
          <section class="space-y-4">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Виріб</h3>
            <p class="text-base font-black text-slate-900">{{ order.product_name || 'Індивідуальне замовлення' }}</p>
            <div class="flex gap-2">
               <span class="px-3 py-1 bg-slate-50 border border-slate-100 rounded-lg text-[10px] font-black text-slate-500 uppercase tracking-widest">Виріб #{{ order.id }}</span>
            </div>
            <div v-if="order.comment" class="p-5 bg-slate-50 rounded-3xl border-l-4 border-slate-200">
               <p class="text-[13px] text-slate-500 italic font-medium">"{{ order.comment }}"</p>
            </div>
          </section>

          <!-- Section: Фінанси -->
          <section class="space-y-4">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Фінанси</h3>
            <div class="flex items-baseline gap-4 px-1">
              <span class="text-3xl font-black text-slate-900 tracking-tighter">{{ formatCurrency(order.total_amount) }}</span>
              <div class="h-6 w-px bg-slate-200" />
              <span class="text-lg font-bold text-slate-400">{{ formatCurrency(order.prepayment_amount) }} <span class="text-[10px]">(Аванс)</span></span>
            </div>
            <div class="inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase border" 
                 :class="{
                   'bg-emerald-50 text-emerald-700 border-emerald-100': order.payment_status === 'paid',
                   'bg-amber-50 text-amber-700 border-amber-100': order.payment_status === 'partial',
                   'bg-slate-50 text-slate-700 border-slate-100': order.payment_status === 'unpaid'
                 }">
              {{ order.payment_status === 'paid' ? 'ОПЛАЧЕНО' : order.payment_status === 'partial' ? 'ЧАСТКОВО' : 'НЕ ОПЛАЧЕНО' }}
            </div>
          </section>

          <!-- Section: Додати Контакт (CRM Action Cards) -->
          <section class="bg-slate-900 rounded-[2.5rem] p-8 space-y-8 shadow-2xl shadow-indigo-100">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Додати контакт</h3>
            
            <div class="grid grid-cols-2 gap-2">
               <button v-for="ch in ['📞 Дзвінок', '💬 Viber', '✈ Telegram', '📸 Instagram']" 
                :key="ch" 
                @click="contactForm.type = ch"
                class="py-4 rounded-2xl border border-white/10 text-white bg-white/5 text-[11px] font-black hover:bg-white/10 transition-all"
                :class="{ 'bg-white/20 border-white/40': contactForm.type === ch }"
               >
                 {{ ch }}
               </button>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <button v-for="res in ['Не відповів', 'Думає', 'Відмовився', '✓ Підтвердив']" :key="res" 
                @click="contactForm.result = res"
                class="py-3.5 rounded-2xl text-[10px] font-black uppercase border transition-all"
                :class="contactForm.result === res ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' : 'bg-white/5 border-white/10 text-white/60 hover:text-white'"
              >
                {{ res }}
              </button>
            </div>

            <div class="p-5 bg-white/5 rounded-3xl border border-white/10 flex items-center justify-between">
              <div class="flex items-center gap-3 text-white">
                <el-icon class="w-4 h-4 text-indigo-400"><Clock /></el-icon>
                <div class="flex flex-col">
                  <span class="text-[9px] font-black text-indigo-400 uppercase tracking-widest">🔔 Нагадати</span>
                  <el-date-picker
                    v-model="contactForm.next_contact"
                    type="datetime"
                    size="small"
                    placeholder="Дата/час"
                    class="bg-transparent border-none text-white text-xs"
                    popper-class="crm-date-picker"
                    value-format="YYYY-MM-DD HH:mm"
                  />
                </div>
              </div>
            </div>

            <button @click="saveContact" class="w-full py-5 bg-white text-slate-900 rounded-[1.5rem] text-xs font-black uppercase tracking-[0.25em] hover:bg-slate-100 transition-all">
              Зберегти контакт
            </button>
          </section>

          <!-- History Timeline -->
          <section class="space-y-10 pb-12">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Історія контактів</h3>
            <div v-if="loadingHistory" class="text-center py-4"><el-icon class="is-loading"><MagicStick /></el-icon></div>
            <div v-else class="relative pl-8 space-y-10 border-l-2 border-slate-100 ml-1">
               <div v-for="item in history" :key="item.id" class="relative">
                  <div class="absolute -left-[37px] top-1 w-4 h-4 rounded-full ring-4 ring-white shadow-sm"
                       :class="item.result.includes('✓') ? 'bg-indigo-600' : 'bg-slate-200'" />
                  <p class="text-[13px] font-black text-slate-900">{{ item.type }} · {{ item.result }}</p>
                  <p class="text-[10px] font-bold text-slate-300 uppercase mt-2">{{ formatDate(item.created_at) }}</p>
                  <p v-if="item.comment" class="text-xs text-slate-500 mt-1">{{ item.comment }}</p>
               </div>
               <p v-if="!history.length" class="text-[11px] font-black text-slate-300 uppercase tracking-widest">Поки немає записів</p>
            </div>
          </section>
        </div>

        <!-- FOOTER -->
        <div class="sticky bottom-0 bg-white/95 backdrop-blur-md border-t border-slate-100 p-6 flex gap-4 z-30 shadow-[0_-10px_30px_rgba(0,0,0,0.02)]">
          <button @click="emit('openFull')" class="flex-1 py-4 text-slate-400 hover:text-slate-900 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all">
            Відкрити повну картку →
          </button>
          <button class="flex-[1.2] py-4 bg-indigo-600 text-white rounded-[1.2rem] text-[10px] font-black uppercase tracking-widest hover:bg-indigo-700 transition-all flex items-center justify-center gap-2">
            <el-icon class="w-3.5 h-3.5"><CircleCheck /></el-icon>
            В роботу
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
/* Reset some element-plus styles for the dark section */
.crm-date-picker {
  background: #0f172a !important;
  border-color: #1e293b !important;
}
.crm-date-picker .el-picker-panel__body {
  color: white !important;
}
</style>

<style scoped>
/* Hide scrollbar but allow scrolling */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Transitions for Element Plus Date Picker override */
:deep(.el-input__wrapper) {
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}
:deep(.el-input__inner) {
  color: white !important;
  font-weight: 900 !important;
  font-size: 12px !important;
}
</style>
