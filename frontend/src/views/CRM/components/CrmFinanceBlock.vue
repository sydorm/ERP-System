<template>
  <div class="crm-section crm-finance-block-premium">
    <div class="space-y-6">
      <div class="grid grid-cols-2 gap-4">
      <!-- Total Amount Card -->
      <div
        class="amount-card-compact total"
        :class="{ editing: editTotalAmount }"
        @click="focusTotalAmount"
      >
        <div class="card-label">Загальна вартість</div>
        <div class="amount-line">
          <span v-if="!editTotalAmount" class="val">{{ formatCurrency(form.total_amount) }}</span>
          <input
            v-else
            ref="totalAmountInput"
            v-model.number="form.total_amount"
            type="number"
            class="val-input"
            @input="$emit('calc-prepayment')"
            @blur="editTotalAmount = false"
            @keyup.enter="editTotalAmount = false"
          />
          <span class="curr">грн</span>
        </div>
      </div>

      <!-- Prepayment Card -->
      <div
        class="amount-card-compact prepay"
        :class="{ editing: editPrepaymentAmount }"
        @click="focusPrepaymentAmount"
      >
        <div class="card-label">
          Сума передоплати
          <span v-if="form.total_amount > 0" class="pct-tag">
            {{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%
          </span>
        </div>
        <div class="amount-line">
          <span v-if="!editPrepaymentAmount" class="val">{{ formatCurrency(form.prepayment_amount) }}</span>
          <input
            v-else
            ref="prepaymentAmountInput"
            v-model.number="form.prepayment_amount"
            type="number"
            class="val-input"
            @input="$emit('prepayment-input')"
            @blur="editPrepaymentAmount = false"
            @keyup.enter="editPrepaymentAmount = false"
          />
          <span class="curr">грн</span>
        </div>
      </div>
    </div>

    <div class="finance-actions-compact">
      <div class="quick-pct-row">
        <button
          v-for="pct in [20, 30, 50, 100]"
          :key="pct"
          class="pct-btn"
          :class="{ active: form.prepayment_percent === pct }"
          @click="$emit('set-prepay-pct', pct)"
        >
          {{ pct }}%
        </button>
        <button
          class="pct-btn"
          :class="{ active: form.prepayment_percent === 0 }"
          @click="$emit('set-prepay-pct', 0)"
        >
          Без
        </button>
      </div>

      <div class="bank-select-wrapper" v-if="form.payment_status !== 'unpaid'">
        <el-select v-model="form.bank_account_id" placeholder="Оберіть рахунок" class="compact-select">
          <template #prefix>
            <el-icon class="text-indigo-400"><Wallet /></el-icon>
          </template>
          <el-option
            v-for="acc in bankAccounts"
            :key="acc.id"
            :label="`${acc.bank_name} (..${acc.iban.slice(-4)})`"
            :value="acc.id"
          />
        </el-select>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { Wallet } from '@element-plus/icons-vue'

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
</script>

<style scoped>
.crm-finance-block-premium {
  padding: 0;
}
.amount-card-compact {
  @apply p-4 rounded-xl border border-gray-200 bg-[#F9FAFB] transition-all cursor-pointer;
}
.amount-card-compact:hover, .amount-card-compact.editing {
  @apply border-[#2563EB] bg-white shadow-md;
}
.card-label {
  @apply text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1;
}
.val {
  @apply text-2xl font-black text-gray-900;
}
.prepay .val {
  @apply text-[#2563EB];
}
.pct-btn {
  @apply px-4 py-2 rounded-lg border border-gray-200 text-xs font-bold transition-all;
}
.pct-btn.active {
  @apply bg-[#2563EB] border-[#2563EB] text-white shadow-lg shadow-blue-100;
}
</style>
