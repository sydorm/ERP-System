<template>
  <div class="crm-finalization-card bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
    <div class="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-100">
      
      <!-- LEFT COLUMN: COST CALCULATION -->
      <div class="p-8 space-y-8">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
            <el-icon class="text-blue-600"><Money /></el-icon>
            Розрахунок вартості
          </h3>
          <div class="text-[10px] font-bold px-2 py-1 bg-blue-50 text-blue-600 rounded-md">SALES CALL MODE</div>
        </div>

        <!-- 1. Automatic & Override Price -->
        <div class="price-section space-y-3">
          <div class="flex items-center justify-between">
            <div class="calculated-price text-slate-500">
              <span class="text-xs">Розрахункова ціна:</span>
              <span class="font-mono font-bold ml-1 text-slate-700">{{ formatCurrency(basePrice) }} грн</span>
              <span class="text-[10px] text-slate-400 ml-1">(згідно номенклатури)</span>
            </div>
            <button 
              v-if="!editPrice"
              @click="enableOverride" 
              class="text-[#2563EB] text-xs font-bold hover:underline flex items-center gap-1"
            >
              <el-icon><EditPen /></el-icon> Виправити
            </button>
          </div>

          <transition name="el-zoom-in-top">
            <div v-if="editPrice" class="override-block p-4 bg-amber-50/50 border border-amber-200 rounded-xl space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-xs font-black text-amber-700 uppercase">Ручна поправка</label>
                <button @click="disableOverride" class="text-amber-600 hover:text-amber-800"><el-icon><Close /></el-icon></button>
              </div>
              <div class="flex items-center gap-3">
                <div class="relative flex-1">
                  <el-input-number 
                    v-model="form.manual_price" 
                    :min="0" 
                    controls-position="right"
                    class="!w-full master-price-input"
                    placeholder="Нова сума"
                  />
                </div>
                <div v-if="basePrice" class="text-right">
                  <span class="line-through text-slate-400 text-xs block">Було: {{ formatCurrency(basePrice) }}</span>
                  <span class="text-[10px] font-bold" :class="priceDiff >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ priceDiff >= 0 ? '+' : '' }}{{ formatCurrency(priceDiff) }}
                  </span>
                </div>
              </div>
              <el-input 
                v-model="form.price_override_reason" 
                placeholder="Причина зміни (обов'язково)" 
                class="override-reason-input"
              />
            </div>
          </transition>
        </div>

        <!-- 2. Fast Discount Chips -->
        <div class="discount-section space-y-4">
          <label class="text-xs font-black text-gray-400 uppercase tracking-wider">Знижка клієнту</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="pct in [5, 10, 15]"
              :key="pct"
              @click="setDiscountPct(pct)"
              class="px-4 py-2 rounded-xl border font-bold text-xs transition-all"
              :class="form.discount_percent === pct ? 'bg-[#2563EB] border-[#2563EB] text-white shadow-lg shadow-blue-100' : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'"
            >
              {{ pct }}%
            </button>
            <button
              @click="showCustomDiscount = !showCustomDiscount"
              class="px-4 py-2 rounded-xl border border-gray-200 text-xs font-bold text-gray-600 hover:bg-gray-50"
            >
              Інша...
            </button>
            <button
              v-if="form.discount_percent > 0 || form.discount_amount > 0"
              @click="resetDiscount"
              class="px-4 py-2 text-xs font-bold text-red-500 hover:bg-red-50 rounded-xl"
            >
              Скинути
            </button>
          </div>

          <transition name="el-zoom-in-top">
            <div v-if="showCustomDiscount" class="p-3 bg-gray-50 rounded-xl flex items-center gap-3">
              <el-input-number v-model="form.discount_percent" :min="0" :max="100" placeholder="%" class="!w-24" />
              <span class="text-gray-400">або</span>
              <el-input-number v-model="form.discount_amount" :min="0" placeholder="Сума" class="flex-1" />
            </div>
          </transition>

          <el-input 
            v-model="form.discount_reason" 
            placeholder="Причина знижки (наприклад: покупка 2 годинників)"
            :status="(form.discount_percent > 0 || form.discount_amount > 0) && !form.discount_reason ? 'error' : ''"
            class="discount-reason-input"
          />
        </div>

        <!-- 3. Final Summary Table -->
        <div class="summary-box p-6 bg-[#F9FAFB] rounded-2xl border border-gray-100 space-y-3">
          <div class="flex justify-between text-sm text-gray-500">
            <span>Виріб (база)</span>
            <span>{{ formatCurrency(basePrice) }} грн</span>
          </div>
          <div v-if="editPrice" class="flex justify-between text-sm">
            <span class="text-amber-600 font-medium">Ручна поправка</span>
            <span class="text-amber-600 font-bold">{{ priceDiff > 0 ? '+' : '' }}{{ formatCurrency(priceDiff) }} грн</span>
          </div>
          <div v-if="form.discount_amount > 0" class="flex justify-between text-sm">
            <span class="text-green-600 font-medium">Знижка ({{ form.discount_percent }}%)</span>
            <span class="text-green-600 font-bold">- {{ formatCurrency(form.discount_amount) }} грн</span>
          </div>
          <div class="h-px bg-gray-200 my-2"></div>
          <div class="flex justify-between items-end pt-2">
            <div>
              <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Загалом до сплати</div>
              <div class="text-3xl font-black text-[#2563EB] leading-none">{{ formatCurrency(form.total_amount) }} <span class="text-lg">₴</span></div>
            </div>
            <div class="text-right">
              <div class="text-[10px] font-bold text-gray-400">ПЕРЕДОПЛАТА</div>
              <div class="text-lg font-bold text-gray-700">{{ formatCurrency(form.prepayment_amount) }} ₴</div>
            </div>
          </div>
        </div>

        <!-- 4. Prepayment Segments -->
        <div class="prepayment-section space-y-4">
          <div class="flex items-center justify-between">
            <label class="text-xs font-black text-gray-400 uppercase">Розмір передоплати</label>
            <span class="text-xs font-bold text-[#2563EB] bg-blue-50 px-2 py-0.5 rounded">{{ prepaymentPct }}%</span>
          </div>
          <div class="grid grid-cols-5 gap-1.5 p-1 bg-gray-100 rounded-xl">
            <button
              v-for="p in [20, 30, 50, 100, 0]"
              :key="p"
              @click="$emit('set-prepay-pct', p)"
              class="py-2 rounded-lg text-xs font-black transition-all"
              :class="prepaymentPct === p ? 'bg-white text-[#2563EB] shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            >
              {{ p === 0 ? 'Без' : p + '%' }}
            </button>
          </div>
          <div class="flex justify-between text-[11px] font-bold text-gray-400 px-1">
            <span>Залишок до сплати:</span>
            <span>{{ formatCurrency(form.total_amount - form.prepayment_amount) }} ₴</span>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: TERMS & PRODUCTION -->
      <div class="p-8 space-y-8 bg-slate-50/30">
        <h3 class="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
          <el-icon class="text-blue-600"><Calendar /></el-icon>
          Терміни та виробництво
        </h3>

        <!-- 1. Production Slots (Hints) -->
        <div class="deadline-hints-section space-y-4">
          <label class="text-xs font-black text-gray-400 uppercase tracking-wider">Слоти виробництва (підказки)</label>
          <div class="grid grid-cols-2 gap-3">
            <button 
              @click="setDeadlineSlot(7)" 
              class="flex flex-col items-start p-4 rounded-2xl border bg-green-50/50 border-green-200 hover:bg-green-100 transition-all text-left group"
            >
              <span class="text-[10px] font-black text-green-600 uppercase mb-1 flex items-center gap-1">
                <el-icon class="group-hover:animate-bounce"><Promotion /></el-icon> Стандарт
              </span>
              <span class="text-sm font-bold text-green-900">+7 роб. днів</span>
              <span class="text-xs font-medium text-green-700 mt-1">до {{ formatDate(slot7) }}</span>
            </button>

            <button 
              @click="setDeadlineSlot(14)" 
              class="flex flex-col items-start p-4 rounded-2xl border bg-blue-50/50 border-blue-200 hover:bg-blue-100 transition-all text-left group"
            >
              <span class="text-[10px] font-black text-blue-600 uppercase mb-1 flex items-center gap-1">
                <el-icon><Calendar /></el-icon> Плановий
              </span>
              <span class="text-sm font-bold text-blue-900">+14 роб. днів</span>
              <span class="text-xs font-medium text-blue-700 mt-1">до {{ formatDate(slot14) }}</span>
            </button>
          </div>
        </div>

        <!-- 2. Manual Date Picker -->
        <div class="manual-deadline space-y-4">
          <label class="text-xs font-black text-gray-400 uppercase tracking-wider">Бажаний дедлайн</label>
          <div class="relative group">
            <el-date-picker
              v-model="form.deadline_date"
              type="date"
              placeholder="Оберіть дату"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="!w-full master-date-picker"
              :class="{ 'urgent-mode': isUrgent }"
            />
            <div v-if="isUrgent" class="mt-2 flex items-center gap-2 p-3 bg-orange-50 border border-orange-200 rounded-xl">
              <el-icon class="text-orange-600 animate-pulse"><WarningFilled /></el-icon>
              <div class="text-[11px] font-bold text-orange-700">
                Термінове виробництво. Вимагає підтвердження керівника цеху.
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Priority -->
        <div class="priority-section space-y-4">
          <label class="text-xs font-black text-gray-400 uppercase tracking-wider">Пріоритет замовлення</label>
          <div class="flex gap-2">
            <button
              v-for="p in priorities"
              :key="p.value"
              @click="handlePriorityChange(p.value)"
              class="flex-1 py-3 rounded-xl border text-[11px] font-black transition-all flex flex-col items-center gap-1.5"
              :class="form.priority === p.value ? 'bg-white border-[#2563EB] text-[#2563EB] shadow-md ring-2 ring-blue-50' : 'bg-white border-gray-200 text-gray-500'"
            >
              <span class="w-2.5 h-2.5 rounded-full" :style="{ background: p.color }"></span>
              {{ p.label.toUpperCase() }}
            </button>
          </div>
        </div>

        <!-- 4. Production Comment -->
        <div class="production-comment space-y-4">
          <label class="text-xs font-black text-gray-400 uppercase tracking-wider">Коментар для виробництва (цеху)</label>
          <el-input
            v-model="form.production_comment"
            type="textarea"
            :rows="3"
            placeholder="Вкажіть особливі побажання для майстрів..."
            class="premium-textarea"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Money, Calendar, EditPen, Close, Promotion, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
  basePrice: { type: Number, default: 0 },
  priorities: { type: Array, required: true },
  formatCurrency: { type: Function, required: true },
  formatDate: { type: Function, required: true },
})

const emit = defineEmits(['set-prepay-pct', 'update-total'])

const editPrice = ref(false)
const showCustomDiscount = ref(false)

// Prices Logic
const priceDiff = computed(() => {
  if (!editPrice.value) return 0
  return (props.form.manual_price || 0) - props.basePrice
})

const enableOverride = () => {
  editPrice.value = true
  if (!props.form.manual_price) props.form.manual_price = props.basePrice
}

const disableOverride = () => {
  editPrice.value = false
  props.form.manual_price = null
  props.form.price_override_reason = ''
}

// Discount Logic
const setDiscountPct = (pct) => {
  props.form.discount_percent = pct
  updateDiscountAmount()
}

const updateDiscountAmount = () => {
  const targetPrice = props.form.manual_price || props.basePrice
  props.form.discount_amount = Math.round(targetPrice * (props.form.discount_percent / 100))
}

const resetDiscount = () => {
  props.form.discount_percent = 0
  props.form.discount_amount = 0
  props.form.discount_reason = ''
}

// Deadlines Logic
const slot7 = computed(() => addBusinessDays(new Date(), 7))
const slot14 = computed(() => addBusinessDays(new Date(), 14))

const isUrgent = computed(() => {
  if (!props.form.deadline_date) return false
  const deadline = new Date(props.form.deadline_date)
  const today = new Date()
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
  return diffDays < 7 || props.form.priority === 'critical'
})

const setDeadlineSlot = (days) => {
  const date = addBusinessDays(new Date(), days)
  props.form.deadline_date = date.toISOString().split('T')[0]
}

const handlePriorityChange = (val) => {
  props.form.priority = val
  if (val === 'critical') setDeadlineSlot(7)
}

function addBusinessDays(date, days) {
  let result = new Date(date)
  let added = 0
  while (added < days) {
    result.setDate(result.getDate() + 1)
    if (result.getDay() !== 0 && result.getDay() !== 6) added++
  }
  return result
}

const prepaymentPct = computed(() => {
  if (!props.form.total_amount) return 0
  return Math.round((props.form.prepayment_amount / props.form.total_amount) * 100)
})

// Final Recalculation
const recalculateTotal = () => {
  const base = props.form.manual_price || props.basePrice
  const total = base - (props.form.discount_amount || 0)
  props.form.total_amount = total
  emit('update-total', total)
}

watch(() => props.form.manual_price, recalculateTotal)
watch(() => props.form.discount_amount, recalculateTotal)
watch(() => props.form.discount_percent, updateDiscountAmount)
watch(() => props.basePrice, recalculateTotal, { immediate: true })

</script>

<style scoped>
.crm-finalization-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.master-price-input .el-input__wrapper) {
  height: 52px !important;
  background: #fff !important;
  border: 2px solid #FCD34D !important;
  font-size: 18px !important;
  font-weight: 800 !important;
}

:deep(.override-reason-input .el-input__wrapper) {
  background: #FFFBEB !important;
  border: 1px dashed #FCD34D !important;
}

:deep(.discount-reason-input .el-input__wrapper) {
  background: #F8FAFC !important;
  border: 1px dashed #CBD5E1 !important;
}

:deep(.master-date-picker .el-input__wrapper) {
  height: 52px !important;
  border-radius: 16px !important;
  background: #fff !important;
  border: 1px solid #E2E8F0 !important;
}

:deep(.urgent-mode .el-input__wrapper) {
  border: 2px solid #F97316 !important;
  background: #FFF7ED !important;
}

.premium-textarea :deep(.el-textarea__inner) {
  border-radius: 16px !important;
  background: #fff !important;
  border: 1px solid #E2E8F0 !important;
  padding: 12px 16px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

.premium-textarea :deep(.el-textarea__inner:focus) {
  border-color: #2563EB !important;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.05) !important;
}
</style>
