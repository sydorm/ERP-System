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
  border-radius: 0;
  margin-bottom: 0;
  padding: 16px 32px;
  position: sticky;
  top: 0;
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: #fff !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
  border-top: none !important;
  box-shadow: none;
}

.back-pill {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  background: #fff;
  color: #64748B;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.back-pill:hover {
  background: #fff;
  color: #4F46E5;
  border-color: #6366F1;
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12);
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
  width: 44px !important;
  height: 44px !important;
  border-radius: 14px !important;
  border-color: rgba(226, 232, 240, 0.8) !important;
  color: #64748B !important;
  transition: all 0.2s !important;
}

.icon-btn-modern:hover {
  border-color: #6366F1 !important;
  color: #6366F1 !important;
  background: #F5F7FF !important;
}

.btn-draft-modern {
  padding: 0 22px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
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
  color: #1E293B;
}

.btn-primary-modern {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0 28px;
  height: 44px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25);
  letter-spacing: -0.01em;
}

.btn-primary-modern:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%);
}

.btn-primary-modern:active {
  transform: translateY(0) scale(0.98);
}

.btn-primary-modern:disabled, .btn-draft-modern:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(1);
}
</style>
