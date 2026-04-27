<script setup>
import { ref, computed, watch } from 'vue';
import { 
  Close, Phone, ChatDotRound, Position, Link, 
  Clock, CircleCheck, Warning, MagicStick, Star, Calendar, Share
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

const fullOrder = ref(null);
const history = ref([]);
const loading = ref(false);

const contactForm = ref({
  type: '📞 Дзвінок',
  result: 'Не відповів',
  comment: '',
  next_contact: ''
});

// Computed for current order (prefers fullOrder if loaded)
const activeOrder = computed(() => fullOrder.value || props.order);

const currentStepIndex = computed(() => {
  if (!activeOrder.value) return -1;
  return STEPS.indexOf(activeOrder.value.crm_stage);
});

const deadlineStatus = computed(() => {
  if (!activeOrder.value?.deadline) return null;
  const d = new Date(activeOrder.value.deadline);
  const now = new Date();
  const diffDays = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
  return {
    days: diffDays,
    isUrgent: diffDays >= 0 && diffDays <= 3,
    text: diffDays < 0 ? 'Протерміновано' : `${diffDays} дн. залишилось`
  };
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', { 
    style: 'currency', 
    currency: 'UAH',
    maximumFractionDigits: 0 
  }).format(value || 0);
};

const formatDate = (dateStr, full = false) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (full) return d.toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' });
};

const fetchData = async () => {
  if (!props.order?.id) return;
  loading.value = true;
  try {
    const [orderRes, historyRes] = await Promise.all([
      api.get(`/api/v1/orders/${props.order.id}`),
      api.get(`/api/v1/crm/orders/${props.order.id}/contacts`)
    ]);
    fullOrder.value = orderRes.data;
    history.value = historyRes.data;
  } catch (e) {
    console.error('Failed to fetch order details', e);
  } finally {
    loading.value = false;
  }
};

const saveContact = async () => {
  if (!activeOrder.value?.id) return;
  try {
    await api.post(`/api/v1/crm/orders/${activeOrder.value.id}/contacts`, {
      ...contactForm.value
    });
    ElMessage.success('Контакт збережено');
    fetchData();
    contactForm.value.comment = '';
    contactForm.value.next_contact = '';
  } catch (e) {
    ElMessage.error('Помилка збереження');
  }
};

watch(() => props.show, (newVal) => {
  if (newVal) {
    fullOrder.value = null; // Clear previous
    fetchData();
  }
});
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 bg-slate-900/10 backdrop-blur-[2px] z-[45]" @click="emit('close')" />
    </Transition>

    <!-- Drawer Panel -->
    <Transition name="slide">
      <div v-if="show && activeOrder" class="fixed right-0 top-0 h-full w-[400px] bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col">
        
        <!-- HEADER -->
        <div class="sticky top-0 bg-white/95 backdrop-blur-md border-b border-slate-100 p-6 z-20">
          <div class="flex items-center justify-between mb-6">
            <span class="text-xs font-bold text-slate-400 tracking-widest">#{{ activeOrder.order_number }}</span>
            <button @click="emit('close')" class="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-900">
              <el-icon><Close /></el-icon>
            </button>
          </div>

          <!-- Stepper Dots -->
          <div class="flex items-center justify-between px-2 mb-6">
            <div v-for="(step, index) in STEPS" :key="step" class="flex flex-col items-center flex-1 relative">
              <div 
                class="w-2.5 h-2.5 rounded-full z-10 transition-all duration-300"
                :class="index <= currentStepIndex ? 'bg-indigo-600 ring-4 ring-indigo-50' : 'bg-slate-200'"
              />
              <span class="text-[8px] mt-2 font-black uppercase tracking-tighter" :class="index === currentStepIndex ? 'text-indigo-600' : 'text-slate-400'">
                {{ STEP_LABELS[step]?.substring(0, 3) }}
              </span>
              <div v-if="index < STEPS.length - 1" class="absolute top-[5px] left-[50%] w-full h-[1px] -z-0" :class="index < currentStepIndex ? 'bg-indigo-600' : 'bg-slate-100'" />
            </div>
          </div>

          <!-- Deadline Chip -->
          <div v-if="deadlineStatus" class="px-1">
             <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-[10px] font-black uppercase tracking-wide"
                  :class="deadlineStatus.isUrgent ? 'bg-rose-50 border-rose-100 text-rose-600' : 'bg-amber-50 border-amber-100 text-amber-600'">
               <el-icon><Clock /></el-icon>
               <span>Дедлайн: {{ formatDate(activeOrder.deadline) }} · {{ deadlineStatus.text }}</span>
             </div>
          </div>
        </div>

        <!-- CONTENT -->
        <div class="flex-1 overflow-y-auto p-6 space-y-10 scrollbar-hide">
          
          <!-- Section: Клієнт -->
          <section class="space-y-4">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Клієнт</h3>
            <div>
              <h2 @click="emit('openFull')" class="text-xl font-black text-slate-900 tracking-tight leading-tight hover:text-indigo-600 cursor-pointer transition-all flex items-center gap-2 group/name">
                {{ activeOrder.client_name || activeOrder.counterparty?.name || '—' }}
                <el-icon class="w-4 h-4 opacity-0 group-hover/name:opacity-100 translate-x-0 group-hover/name:translate-x-1 transition-all"><Link /></el-icon>
              </h2>
              <a :href="`tel:${activeOrder.client_phone}`" class="text-base font-bold text-indigo-600 hover:underline block mt-1">
                {{ activeOrder.client_phone || '—' }}
              </a>
            </div>
            
            <div class="flex gap-3">
               <div class="p-2.5 bg-indigo-50 rounded-xl cursor-pointer hover:bg-indigo-100 transition-colors"><el-icon class="text-indigo-600"><ChatDotRound /></el-icon></div>
               <div class="p-2.5 bg-sky-50 rounded-xl cursor-pointer hover:bg-sky-100 transition-colors"><el-icon class="text-sky-600"><Position /></el-icon></div>
               <div class="p-2.5 bg-pink-50 rounded-xl cursor-pointer hover:bg-pink-100 transition-colors"><el-icon class="text-pink-600"><Share /></el-icon></div>
            </div>
            
            <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              📍 {{ activeOrder.city || '—' }} · {{ activeOrder.delivery_service || 'Доставка не вказана' }}
            </p>
          </section>

          <!-- Section: Виріб -->
          <section class="space-y-4">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Виріб</h3>
            <p class="text-base font-bold text-slate-900">{{ activeOrder.product_name || activeOrder.product?.name || 'Індивідуальне замовлення' }}</p>
            <div class="flex flex-wrap gap-2">
               <span class="px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-lg text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                 ID: {{ activeOrder.product_id?.substring(0, 8) || 'NEW' }}
               </span>
               <span v-if="activeOrder.characteristics" class="px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-lg text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                 {{ activeOrder.characteristics }}
               </span>
            </div>
            <div v-if="activeOrder.comment" class="p-4 bg-slate-50 rounded-2xl border-l-4 border-slate-200">
               <p class="text-[13px] text-slate-500 italic">"{{ activeOrder.comment }}"</p>
            </div>
          </section>

          <!-- Section: Фінанси -->
          <section class="space-y-4">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Фінанси</h3>
            <div class="flex items-center gap-6">
              <div>
                <p class="text-[9px] font-black text-slate-400 uppercase mb-1">Сума</p>
                <span class="text-2xl font-black text-slate-900 tracking-tighter">{{ formatCurrency(activeOrder.total_amount) }}</span>
              </div>
              <div class="h-8 w-px bg-slate-100" />
              <div>
                <p class="text-[9px] font-black text-slate-400 uppercase mb-1">Аванс</p>
                <span class="text-xl font-bold text-slate-400">{{ formatCurrency(activeOrder.prepayment_amount) }}</span>
              </div>
            </div>
            <div class="inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase border" 
                 :class="{
                   'bg-emerald-50 text-emerald-700 border-emerald-100': activeOrder.payment_status === 'paid',
                   'bg-amber-50 text-amber-700 border-amber-100': activeOrder.payment_status === 'partial',
                   'bg-slate-50 text-slate-700 border-slate-100': activeOrder.payment_status === 'unpaid'
                 }">
              {{ activeOrder.payment_status === 'paid' ? 'ОПЛАЧЕНО' : activeOrder.payment_status === 'partial' ? 'ЧАСТКОВО' : 'НЕ ОПЛАЧЕНО' }}
            </div>
          </section>

          <!-- Section: Додати Контакт (LIGHT STYLE) -->
          <section class="bg-[#F8F9FF] border border-[#E8EAFF] rounded-[2rem] p-6 space-y-6">
            <h3 class="text-[10px] font-black uppercase text-indigo-400 tracking-[0.2em]">Додати контакт</h3>
            
            <div class="grid grid-cols-2 gap-2">
               <button v-for="ch in ['📞 Дзвінок', '💬 Viber', '✈ Telegram', '📸 Instagram']" 
                :key="ch" 
                @click="contactForm.type = ch"
                class="py-3 rounded-xl border text-[11px] font-bold transition-all"
                :class="contactForm.type === ch ? 'bg-indigo-600 border-indigo-600 text-white shadow-md' : 'bg-white border-indigo-100 text-indigo-600 hover:bg-indigo-50'"
               >
                 {{ ch }}
               </button>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <button v-for="res in ['Не відповів', 'Думає', 'Відмовився', '✓ Підтвердив']" :key="res" 
                @click="contactForm.result = res"
                class="py-3 rounded-xl border text-[10px] font-black uppercase transition-all"
                :class="contactForm.result === res ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-slate-200 text-slate-500 hover:border-indigo-300'"
              >
                {{ res }}
              </button>
            </div>

            <div class="p-4 bg-white rounded-2xl border border-indigo-50 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <el-icon class="text-indigo-400"><Clock /></el-icon>
                <div class="flex flex-col">
                  <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Нагадати</span>
                  <el-date-picker
                    v-model="contactForm.next_contact"
                    type="datetime"
                    size="small"
                    placeholder="Дата/час"
                    class="custom-dp"
                    format="DD.MM HH:mm"
                    value-format="YYYY-MM-DD HH:mm"
                  />
                </div>
              </div>
            </div>

            <button @click="saveContact" class="w-full py-4 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">
              Зберегти контакт
            </button>
          </section>

          <!-- History Timeline -->
          <section class="space-y-8 pb-10">
            <h3 class="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Історія контактів</h3>
            <div v-if="history.length" class="relative pl-8 space-y-8 border-l-2 border-slate-100 ml-2">
               <div v-for="item in history" :key="item.id" class="relative">
                  <div class="absolute -left-[39px] top-1 w-3.5 h-3.5 rounded-full ring-4 ring-white shadow-sm"
                       :class="item.result.includes('✓') ? 'bg-indigo-600' : 'bg-slate-200'" />
                  <p class="text-[13px] font-bold text-slate-900">{{ item.type }} · {{ item.result }}</p>
                  <p class="text-[10px] font-bold text-slate-300 uppercase mt-1">{{ formatDate(item.created_at, true) }}</p>
               </div>
            </div>
            <div v-else class="text-center py-6 border-2 border-dashed border-slate-50 rounded-2xl">
               <p class="text-[11px] font-black text-slate-300 uppercase tracking-widest">Контактів ще не було</p>
            </div>
          </section>
        </div>

        <!-- FOOTER -->
        <div class="sticky bottom-0 bg-white/95 backdrop-blur-md border-t border-slate-100 p-6 flex gap-4 z-30">
          <button @click="emit('openFull')" class="flex-1 py-4 text-slate-400 hover:text-slate-900 text-[10px] font-black uppercase tracking-widest transition-all">
            Відкрити повну картку →
          </button>
          <button class="flex-[1.2] py-4 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-100">
            <el-icon><CircleCheck /></el-icon>
            В роботу
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

.slide-enter-active, .slide-leave-active { transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

:deep(.custom-dp) {
  --el-input-bg-color: transparent;
  --el-input-border-color: transparent;
  --el-input-hover-border-color: transparent;
  --el-input-focus-border-color: transparent;
}
:deep(.el-input__wrapper) { box-shadow: none !important; padding: 0 !important; background: transparent !important; }
:deep(.el-input__inner) { font-weight: 800 !important; font-size: 11px !important; color: #3D3AA8 !important; }
</style>
