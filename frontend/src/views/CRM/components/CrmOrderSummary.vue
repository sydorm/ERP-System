<template>
  <div class="crm-section crm-order-summary-premium">
    <div class="inline-edit-amounts">
      <div class="inline-amount-box">
        <div class="inline-amount-input-wrapper">
          <input
            v-model.number="form.total_amount"
            type="number"
            class="inline-amount-input"
            placeholder="0"
            @input="onTotalChange"
          />
          <span class="currency-symbol">₴</span>
        </div>
        <div class="inline-amount-label">Сума замовлення</div>
      </div>

      <div class="inline-amount-box">
        <div class="inline-amount-input-wrapper">
          <input
            v-model.number="form.prepayment_amount"
            type="number"
            class="inline-amount-input prepay"
            placeholder="0"
          />
          <span class="currency-symbol">₴</span>
        </div>
        <div class="inline-amount-label">
          Передоплата 
          <span class="prepay-pct-hint" v-if="form.total_amount > 0">
            ({{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%)
          </span>
        </div>
      </div>
    </div>

    <div class="prepay-pills-new">
      <button 
        v-for="pct in [0, 30, 50, 100]" 
        :key="pct"
        class="pill-new"
        :class="{ active: isPercentActive(pct) }"
        @click="setPrepayPercent(pct)"
      >
        {{ pct === 0 ? 'Без' : pct + '%' }}
      </button>
    </div>

    <div class="payment-badge-new" :class="paymentStatusClass">
      <span class="status-dot-new"></span>
      <span>{{ paymentStatusLabel }}</span>
    </div>

    <div class="crm-field">
      <label class="crm-label">Приорітет</label>
      <div class="priority-pills">
        <div 
          v-for="p in priorities" 
          :key="p.id"
          class="priority-pill"
          :class="[`pp-${p.id}`, { active: form.priority === p.id }]"
          @click="form.priority = p.id"
        >
          {{ p.name }}
        </div>
      </div>
    </div>

    <div class="crm-field" style="margin-top: 16px;">
      <label class="crm-label">Менеджер</label>
      <el-select v-model="form.manager_id" placeholder="Оберіть відповідального" class="modern-select">
        <el-option v-for="u in managers" :key="u.id" :label="u.name || u.full_name" :value="u.id" />
      </el-select>
    </div>

    <div class="crm-date-row">
      <div class="date-item">
        <span>Створено:</span>
        <span class="date-val gray">{{ formatDate(form.created_at) }}</span>
      </div>
      <div class="date-item">
        <span>Дедлайн:</span>
        <span class="date-val blue">{{ form.deadline ? formatDate(form.deadline) : 'Не встановлено' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  priorities: { type: Array, required: true },
  managers: { type: Array, required: true },
  formatCurrency: { type: Function, required: true }
})

const emit = defineEmits(['update-amount'])

const onTotalChange = () => {
  emit('update-amount', props.form.total_amount)
}

const isPercentActive = (pct) => {
  if (props.form.total_amount <= 0) return false
  const currentPct = Math.round((props.form.prepayment_amount || 0) / props.form.total_amount * 100)
  return currentPct === pct
}

const setPrepayPercent = (pct) => {
  if (props.form.total_amount > 0) {
    props.form.prepayment_amount = Math.round(props.form.total_amount * (pct / 100))
  }
}

const paymentStatusClass = computed(() => {
  if (!props.form.total_amount) return 'unpaid'
  const paid = props.form.prepayment_amount || 0
  if (paid >= props.form.total_amount) return 'paid'
  if (paid > 0) return 'partial'
  return 'unpaid'
})

const paymentStatusLabel = computed(() => {
  const cls = paymentStatusClass.value
  if (cls === 'paid') return 'Оплачено повністю'
  if (cls === 'partial') return 'Часткова оплата'
  return 'Очікує оплати'
})

const formatDate = (val) => {
  if (!val) return '—'
  return new Date(val).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.inline-amount-input-wrapper {
  position: relative;
  display: flex;
  align-items: baseline;
}
.currency-symbol {
  font-size: 18px;
  font-weight: 700;
  color: #94A3B8;
  margin-left: 4px;
}
</style>
