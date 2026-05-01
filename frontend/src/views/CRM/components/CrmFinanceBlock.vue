<template>
  <div class="crm-section crm-finance-block-premium">
    <div class="finance-header-compact">
      <div class="header-main">
        <div class="step-badge-mini">Крок 3</div>
        <h3 class="text-base font-extrabold text-slate-800">Розрахунок вартості</h3>
      </div>
      <div class="header-status">
        <div class="status-pill-mini" :class="autoPaymentStatus.key">
          <span class="status-dot" />
          <span>{{ autoPaymentStatus.label }}</span>
        </div>
      </div>
    </div>

    <div class="finance-grid-compact">
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
  padding: 20px;
  background: #fff;
  border-radius: 24px;
}

.finance-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-badge-mini {
  background: #F59E0B;
  color: #fff;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
}

.status-pill-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
}

.status-pill-mini.paid { background: #ECFDF5; color: #059669; }
.status-pill-mini.partial { background: #FFFBEB; color: #D97706; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94A3B8;
}
.paid .status-dot { background: #10B981; }
.partial .status-dot { background: #F59E0B; }

.finance-grid-compact {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.amount-card-compact {
  background: #F8FAFC;
  border: 1px solid #E5EAF2;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.amount-card-compact:hover {
  background: #fff;
  border-color: #6366F1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05);
}

.amount-card-compact.editing {
  background: #fff;
  border-color: #6366F1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.05);
}

.card-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748B;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pct-tag {
  background: #EEF2FF;
  color: #6366F1;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.amount-line {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.val {
  font-size: 24px;
  font-weight: 800;
  color: #1E293B;
  letter-spacing: -0.01em;
}

.prepay .val { color: #6366F1; }

.val-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 24px;
  font-weight: 800;
  color: inherit;
  outline: none;
  padding: 0;
}

.curr {
  font-size: 12px;
  font-weight: 700;
  color: #94A3B8;
}

.finance-actions-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.quick-pct-row {
  display: flex;
  gap: 8px;
}

.pct-btn {
  padding: 6px 14px;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.pct-btn:hover {
  border-color: #6366F1;
  color: #6366F1;
}

.pct-btn.active {
  background: #6366F1;
  color: #fff;
  border-color: #6366F1;
}

.bank-select-wrapper {
  flex: 1;
  max-width: 240px;
}

:deep(.compact-select .el-select__wrapper) {
  border-radius: 10px !important;
  background: #F8FAFC !important;
  border: 1px solid #E2E8F0 !important;
  height: 34px !important;
  box-shadow: none !important;
}

@media (max-width: 768px) {
  .finance-grid-compact { grid-template-columns: 1fr; }
  .finance-actions-compact { flex-direction: column; align-items: stretch; }
  .bank-select-wrapper { max-width: 100%; }
}
</style>
