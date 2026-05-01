<template>
  <div class="crm-section crm-finance-section-premium">
    <div class="finance-block-header">
      <div class="header-main">
        <div class="step-badge">Крок 3</div>
        <div class="title-group">
          <h3>Розрахунок вартості</h3>
          <p>Керування бюджетом та передоплатою замовлення</p>
        </div>
      </div>
      <div class="header-status">
        <div class="glass-pill" :class="autoPaymentStatus.key">
          <span class="status-dot" />
          <span>{{ autoPaymentStatus.label }}</span>
        </div>
      </div>
    </div>

    <div class="finance-interactive-grid">
      <div
        class="finance-card-premium total-amount"
        :class="{ editing: editTotalAmount }"
        @click="focusTotalAmount"
      >
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="amount-wrapper">
            <span v-if="!editTotalAmount" class="display-val">
              {{ formatCurrency(form.total_amount) }}
            </span>
            <input
              v-else
              ref="totalAmountInput"
              v-model.number="form.total_amount"
              type="number"
              class="premium-amount-input"
              @input="$emit('calc-prepayment')"
              @blur="editTotalAmount = false"
              @keyup.enter="editTotalAmount = false"
            />
            <span class="currency-label">грн</span>
          </div>
          <div class="meta-label">Загальна вартість</div>
        </div>
      </div>

      <div
        class="finance-card-premium prepay-amount"
        :class="{ editing: editPrepaymentAmount }"
        @click="focusPrepaymentAmount"
      >
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="amount-wrapper">
            <span v-if="!editPrepaymentAmount" class="display-val">
              {{ formatCurrency(form.prepayment_amount) }}
            </span>
            <input
              v-else
              ref="prepaymentAmountInput"
              v-model.number="form.prepayment_amount"
              type="number"
              class="premium-amount-input"
              @input="$emit('prepayment-input')"
              @blur="editPrepaymentAmount = false"
              @keyup.enter="editPrepaymentAmount = false"
            />
            <span class="currency-label">грн</span>
          </div>
          <div class="meta-label">
            Сума передоплати
            <span v-if="form.total_amount > 0" class="percent-badge">
              {{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="finance-controls-row">
      <div class="quick-prepay-pills">
        <button
          v-for="pct in [20, 30, 50, 100]"
          :key="pct"
          class="pill-btn-modern"
          :class="{ active: form.prepayment_percent === pct }"
          @click="$emit('set-prepay-pct', pct)"
        >
          {{ pct }}%
        </button>
        <button
          class="pill-btn-modern"
          :class="{ active: form.prepayment_percent === 0 }"
          @click="$emit('set-prepay-pct', 0)"
        >
          Без
        </button>
      </div>

      <div class="bank-account-zone" v-if="form.payment_status !== 'unpaid'">
        <el-select v-model="form.bank_account_id" placeholder="Оберіть рахунок" class="premium-bank-select">
          <template #prefix>
            <el-icon><Wallet /></el-icon>
          </template>
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
.crm-finance-section-premium {
  padding: 32px;
  background: #fff;
  border-radius: 24px;
}

.finance-block-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-main {
  display: flex;
  gap: 16px;
  align-items: center;
}

.step-badge {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #fff;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.title-group h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 850;
  color: #0F172A;
  letter-spacing: -0.02em;
}

.title-group p {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
}

.glass-pill.paid { background: #ECFDF5; color: #059669; }
.glass-pill.partial { background: #FFFBEB; color: #D97706; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94A3B8;
}
.paid .status-dot { background: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
.partial .status-dot { background: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }

.finance-interactive-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;
}

.finance-card-premium {
  position: relative;
  background: #F8FAFC;
  border: 1px solid #F1F5F9;
  border-radius: 20px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  overflow: hidden;
}

.finance-card-premium:hover {
  transform: translateY(-4px);
  background: #fff;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

.finance-card-premium.editing {
  background: #fff;
  border-color: #6366F1;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.1);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: transparent;
}

.total-amount .card-glow { background: #0F172A; }
.prepay-amount .card-glow { background: #6366F1; }

.amount-wrapper {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
}

.display-val {
  font-size: 32px;
  font-weight: 900;
  color: #0F172A;
  letter-spacing: -0.02em;
}

.prepay-amount .display-val {
  color: #6366F1;
}

.premium-amount-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 32px;
  font-weight: 900;
  text-align: center;
  color: inherit;
  outline: none;
}

.currency-label {
  font-size: 16px;
  font-weight: 800;
  color: #94A3B8;
}

.meta-label {
  font-size: 13px;
  font-weight: 700;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.percent-badge {
  background: #E0E7FF;
  color: #4338CA;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
}

.finance-controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.quick-prepay-pills {
  display: flex;
  gap: 10px;
}

.pill-btn-modern {
  padding: 10px 20px;
  border-radius: 14px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn-modern:hover {
  border-color: #6366F1;
  color: #4F46E5;
}

.pill-btn-modern.active {
  background: #6366F1;
  color: #fff;
  border-color: #6366F1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.bank-account-zone {
  flex: 1;
  max-width: 400px;
}

:deep(.premium-bank-select) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 14px;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 12px;
}

@media (max-width: 992px) {
  .finance-interactive-grid { grid-template-columns: 1fr; }
  .finance-controls-row { flex-direction: column; align-items: flex-start; }
  .bank-account-zone { max-width: 100%; width: 100%; }
}
</style>
