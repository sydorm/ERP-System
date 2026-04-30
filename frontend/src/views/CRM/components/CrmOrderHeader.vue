<template>
  <div class="crm-top-bar">
    <button class="crm-back-btn" @click="$emit('back')">
      <el-icon><ArrowLeft /></el-icon>
    </button>

    <CrmOrderStageStepper
      :stages="stages"
      :active-stage="activeStage"
      :is-passed-stage="isPassedStage"
      @set-stage="$emit('set-stage', $event)"
    />

    <div class="crm-top-actions">
      <el-button
        v-if="orderId"
        type="info"
        circle
        :icon="Printer"
        @click="$emit('print')"
        style="margin-right: 12px;"
        title="Друк рахунку"
      />
      <button class="crm-draft-btn" @click="$emit('save-draft')" :disabled="saving">
        Записати чернетку
      </button>
      <button class="crm-save-btn" @click="$emit('save-production')" :disabled="saving">
        <el-icon><Promotion /></el-icon>
        Зберегти та передати у виробництво
      </button>
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
