<template>
  <div class="crm-section crm-finance-section">
    <div class="finance-block-head">
      <span class="finance-kicker">Крок 3 · Фінанси</span>
      <h3>Розрахунок вартості</h3>
    </div>

    <div class="finance-main-grid">
      <div
        class="finance-card amount-total"
        :class="{ editing: editTotalAmount }"
        @click="focusTotalAmount"
      >
        <div class="amount-display">
          <span v-if="!editTotalAmount" class="amount-val">
            {{ formatCurrency(form.total_amount) }}
          </span>
          <input
            v-else
            ref="totalAmountInput"
            v-model.number="form.total_amount"
            type="number"
            class="amount-input"
            @input="$emit('calc-prepayment')"
            @blur="editTotalAmount = false"
            @keyup.enter="editTotalAmount = false"
          />
          <span class="amount-unit">грн</span>
        </div>
        <div class="amount-label">загальна сума</div>
      </div>

      <div
        class="finance-card amount-prepay"
        :class="{ editing: editPrepaymentAmount }"
        @click="focusPrepaymentAmount"
      >
        <div class="amount-display">
          <span v-if="!editPrepaymentAmount" class="amount-val">
            {{ formatCurrency(form.prepayment_amount) }}
          </span>
          <input
            v-else
            ref="prepaymentAmountInput"
            v-model.number="form.prepayment_amount"
            type="number"
            class="amount-input"
            @input="$emit('prepayment-input')"
            @blur="editPrepaymentAmount = false"
            @keyup.enter="editPrepaymentAmount = false"
          />
          <span class="amount-unit">грн</span>
        </div>
        <div class="amount-label">
          передоплата
          <span v-if="form.total_amount > 0" class="pct-badge">
            {{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%
          </span>
        </div>
      </div>
    </div>

    <div class="prepay-pills-container">
      <button
        v-for="pct in [20, 30, 50, 100]"
        :key="pct"
        class="prepay-pill-modern"
        :class="{ active: form.prepayment_percent === pct }"
        @click="$emit('set-prepay-pct', pct)"
      >{{ pct }}%</button>
      <button
        class="prepay-pill-modern"
        :class="{ active: form.prepayment_percent === 0 }"
        @click="$emit('set-prepay-pct', 0)"
      >Без</button>
    </div>

    <div class="finance-status-row">
      <div class="payment-badge-modern" :class="autoPaymentStatus.key">
        <span class="status-dot-modern" />
        {{ autoPaymentStatus.label }}
      </div>

      <div v-if="form.payment_status !== 'unpaid'" class="bank-select-wrapper">
        <el-select v-model="form.bank_account_id" placeholder="Рахунок для оплати" class="bank-select-modern">
          <template #prefix><el-icon><CreditCard /></el-icon></template>
          <el-option
            v-for="acc in bankAccounts"
            :key="acc.id"
            :label="`${acc.bank_name} (${acc.iban.slice(-4)})`"
            :value="acc.id"
          />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { CreditCard } from '@element-plus/icons-vue'

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
.crm-finance-section {
  padding: 24px;
}

.finance-block-head {
  margin-bottom: 24px;
}

.finance-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: #3D3AA8;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.finance-block-head h3 {
  margin: 0;
  color: #0F172A;
  font-size: 20px;
  font-weight: 800;
}

.finance-main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.finance-card {
  background: #F8FAFC;
  border-radius: 16px;
  padding: 20px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.finance-card:hover {
  background: #F1F5F9;
}

.finance-card.editing {
  background: #fff;
  border-color: #3D3AA8;
  box-shadow: 0 10px 15px -3px rgba(61, 58, 168, 0.1);
}

.amount-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.amount-val {
  font-size: 28px;
  font-weight: 800;
  color: #0F172A;
}

.amount-total .amount-val { color: #0F172A; }
.amount-prepay .amount-val { color: #3D3AA8; }

.amount-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 28px;
  font-weight: 800;
  text-align: center;
  color: inherit;
  outline: none;
}

.amount-unit {
  font-size: 14px;
  font-weight: 700;
  color: #94A3B8;
}

.amount-label {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.pct-badge {
  background: #E0E0FF;
  color: #3D3AA8;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 10px;
}

.prepay-pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.prepay-pill-modern {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #3D3AA8;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.prepay-pill-modern:hover {
  border-color: #3D3AA8;
}

.prepay-pill-modern.active {
  background: #3D3AA8;
  color: #fff;
  border-color: #3D3AA8;
}

.finance-status-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.payment-badge-modern {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}

.payment-badge-modern.unpaid { background: #F8FAFC; color: #64748B; }
.payment-badge-modern.partial { background: #FFFBEB; color: #92400E; }
.payment-badge-modern.paid { background: #ECFDF5; color: #065F46; }

.status-dot-modern {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.unpaid .status-dot-modern { background: #94A3B8; }
.partial .status-dot-modern { background: #F59E0B; }
.paid .status-dot-modern { background: #10B981; }

.bank-select-wrapper {
  flex: 1.5;
}

.bank-select-modern {
  width: 100%;
}
</style>
