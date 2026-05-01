<template>
  <div class="crm-header-modern saas-glass-card">
    <div class="header-left">
      <button class="back-pill" @click="$emit('back')" title="Назад">
        <el-icon><ArrowLeft /></el-icon>
      </button>
    </div>

    <div class="header-center">
      <CrmOrderStageStepper
        :stages="stages"
        :active-stage="activeStage"
        :is-passed-stage="isPassedStage"
        @set-stage="$emit('set-stage', $event)"
      />
    </div>

    <div class="header-right">
      <div class="action-group">
        <el-button
          v-if="orderId"
          class="icon-btn-modern"
          :icon="Printer"
          @click="$emit('print')"
          title="Друк рахунку"
        />
        <button class="btn-draft-modern" @click="$emit('save-draft')" :disabled="saving">
          Записати чернетку
        </button>
        <button class="btn-primary-modern" @click="$emit('save-production')" :disabled="saving">
          <el-icon><Promotion /></el-icon>
          <span>Зберегти та передати</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft, Printer, Promotion } from '@element-plus/icons-vue'
import CrmOrderStageStepper from './CrmOrderStageStepper.vue'

defineProps({
  stages: { type: Array, required: true },
  activeStage: { type: String, required: true },
  isPassedStage: { type: Function, required: true },
  orderId: { type: [String, Number, null], default: null },
  saving: { type: Boolean, default: false },
})

defineEmits(['back', 'set-stage', 'print', 'save-draft', 'save-production'])
</script>

<style scoped>
.crm-header-modern {
  border-radius: 0 !important;
  margin-bottom: 0;
  padding: 12px 32px;
  position: sticky;
  top: 0;
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  border-left: none !important;
  border-right: none !important;
  border-top: none !important;
  background: rgba(255, 255, 255, 0.9) !important;
}

.back-pill {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s;
}

.back-pill:hover {
  background: #F8FAFC;
  color: #0F172A;
  border-color: #CBD5E1;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn-modern {
  width: 40px !important;
  height: 40px !important;
  border-radius: 12px !important;
  border-color: #E2E8F0 !important;
  color: #64748B !important;
}

.btn-draft-modern {
  padding: 0 20px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-draft-modern:hover {
  background: #F8FAFC;
  border-color: #CBD5E1;
}

.btn-primary-modern {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #1463FF 0%, #0047D1 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.2);
}

.btn-primary-modern:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(20, 99, 255, 0.3);
}

.btn-primary-modern:disabled, .btn-draft-modern:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
