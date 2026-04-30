<template>
  <div class="crm-section" style="background: white; border: 1px solid #EBEBEB; border-radius: 12px; padding: 16px; margin-top: 16px;">
    <div style="font-size: 10px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;">
      ФІНАНСИ
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px;">
      <div
        style="border-radius: 10px; padding: 10px; text-align: center; cursor: pointer; transition: all 0.2s;"
        :style="{ background: '#F8F9FF', border: editTotalAmount ? '2px solid #3D3AA8' : '2px solid transparent' }"
        @click="focusTotalAmount"
      >
        <div v-if="!editTotalAmount" style="font-size: 22px; font-weight: 700; color: #111827;">
          {{ formatCurrency(form.total_amount) }}
        </div>
        <input
          v-else
          ref="totalAmountInput"
          v-model.number="form.total_amount"
          type="number"
          style="font-size: 18px; font-weight: 700; color: #111827; border: none; background: transparent; width: 100%; text-align: center; outline: none;"
          @input="$emit('calc-prepayment')"
          @blur="editTotalAmount = false"
          @keyup.enter="editTotalAmount = false"
        />
        <div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">сума грн</div>
      </div>

      <div
        style="border-radius: 10px; padding: 10px; text-align: center; cursor: pointer; transition: all 0.2s;"
        :style="{ background: '#F8F9FF', border: editPrepaymentAmount ? '2px solid #3D3AA8' : '2px solid transparent' }"
        @click="focusPrepaymentAmount"
      >
        <div v-if="!editPrepaymentAmount" style="font-size: 22px; font-weight: 700; color: #3D3AA8;">
          {{ formatCurrency(form.prepayment_amount) }}
        </div>
        <input
          v-else
          ref="prepaymentAmountInput"
          v-model.number="form.prepayment_amount"
          type="number"
          style="font-size: 18px; font-weight: 700; color: #3D3AA8; border: none; background: transparent; width: 100%; text-align: center; outline: none;"
          @input="$emit('prepayment-input')"
          @blur="editPrepaymentAmount = false"
          @keyup.enter="editPrepaymentAmount = false"
        />
        <div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">
          передоплата
          <span v-if="form.total_amount > 0">
            ({{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%)
          </span>
        </div>
      </div>
    </div>

    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
      <button
        v-for="pct in [20, 30, 50, 100]"
        :key="pct"
        :style="prepayButtonStyle(pct)"
        @click="$emit('set-prepay-pct', pct)"
      >{{ pct }}%</button>
      <button :style="prepayButtonStyle(0)" @click="$emit('set-prepay-pct', 0)">Без</button>
    </div>

    <div
      class="payment-badge-new"
      style="border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 600; width: 100%; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px;"
      :style="paymentBadgeStyle"
    >
      <span class="status-dot-new" style="width: 8px; height: 8px; border-radius: 50%;" :style="paymentDotStyle" />
      {{ autoPaymentStatus.label }}
    </div>

    <div class="crm-field" v-if="form.payment_status !== 'unpaid'" style="margin-bottom: 12px;">
      <el-select v-model="form.bank_account_id" placeholder="Оберіть банк" style="width:100%">
        <el-option
          v-for="acc in bankAccounts"
          :key="acc.id"
          :label="`${acc.bank_name} (${acc.iban.slice(-4)})`"
          :value="acc.id"
        />
      </el-select>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  bankAccounts: { type: Array, required: true },
  autoPaymentStatus: { type: Object, required: true },
  formatCurrency: { type: Function, required: true },
})

defineEmits(['calc-prepayment', 'prepayment-input', 'set-prepay-pct'])

const editTotalAmount = ref(false)
const editPrepaymentAmount = ref(false)
const totalAmountInput = ref(null)
const prepaymentAmountInput = ref(null)

const focusTotalAmount = () => {
  editTotalAmount.value = true
  nextTick(() => totalAmountInput.value?.focus())
}

const focusPrepaymentAmount = () => {
  editPrepaymentAmount.value = true
  nextTick(() => prepaymentAmountInput.value?.focus())
}

const prepayButtonStyle = (pct) => ({
  border: '1.5px solid #E0E0FF',
  borderRadius: '20px',
  padding: '5px 12px',
  fontSize: '12px',
  fontWeight: '600',
  cursor: 'pointer',
  transition: 'all 0.2s',
  background: props.form.prepayment_percent === pct ? '#3D3AA8' : 'white',
  color: props.form.prepayment_percent === pct ? 'white' : '#3D3AA8',
  borderColor: props.form.prepayment_percent === pct ? '#3D3AA8' : '#E0E0FF',
})

const paymentBadgeStyle = computed(() => ({
  background: props.autoPaymentStatus.key === 'unpaid' ? '#F9FAFB' : props.autoPaymentStatus.key === 'partial' ? '#FFFBEB' : '#ECFDF5',
  color: props.autoPaymentStatus.key === 'unpaid' ? '#6B7280' : props.autoPaymentStatus.key === 'partial' ? '#92400E' : '#065F46',
}))

const paymentDotStyle = computed(() => ({
  background: props.autoPaymentStatus.key === 'unpaid' ? '#9CA3AF' : props.autoPaymentStatus.key === 'partial' ? '#F59E0B' : '#10B981',
}))
</script>
