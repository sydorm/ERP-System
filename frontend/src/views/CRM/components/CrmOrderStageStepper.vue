<template>
  <div class="crm-stepper-premium">
    <div
      v-for="(stage, idx) in stages"
      :key="stage.key"
      class="stage-block"
      :class="{ 
        'active': activeStage === stage.key, 
        'past': isPassedStage(stage.key),
        'last': idx === stages.length - 1
      }"
      @click="$emit('set-stage', stage.key)"
    >
      <div class="block-content">
        <div class="stage-icon-box">
          <span v-if="isPassedStage(stage.key) && activeStage !== stage.key" class="check-icon">
            <el-icon><Check /></el-icon>
          </span>
          <span v-else class="stage-num">{{ idx + 1 }}</span>
        </div>
        <div class="stage-label">{{ stage.label }}</div>
      </div>
      <div v-if="idx < stages.length - 1" class="stage-connector">
        <div class="connector-line"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check } from '@element-plus/icons-vue'

defineProps({
  stages: { type: Array, required: true },
  activeStage: { type: String, required: true },
  isPassedStage: { type: Function, required: true },
})

defineEmits(['set-stage'])
</script>

<style scoped>
.crm-stepper-premium {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F8FAFC;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #E2E8F0;
}

.stage-block {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 6px 4px;
}

.block-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 14px;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.stage-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #E2E8F0;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 900;
  transition: all 0.3s;
}

.stage-label {
  font-size: 13px;
  font-weight: 750;
  color: #64748B;
  white-space: nowrap;
  transition: all 0.3s;
}

/* ACTIVE STATE */
.stage-block.active .block-content {
  background: #fff;
  border-color: #6366F1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}
.stage-block.active .stage-icon-box {
  background: #6366F1;
  color: #fff;
}
.stage-block.active .stage-label {
  color: #1E293B;
  font-weight: 850;
}

/* PAST STATE */
.stage-block.past:not(.active) .stage-icon-box {
  background: #ECFDF5;
  color: #10B981;
}
.stage-block.past:not(.active) .stage-label {
  color: #10B981;
}

/* CONNECTOR */
.stage-connector {
  margin-left: 8px;
  width: 24px;
  display: flex;
  align-items: center;
}
.connector-line {
  height: 2px;
  width: 100%;
  background: #E2E8F0;
  border-radius: 1px;
}
.stage-block.past .connector-line {
  background: #10B981;
}

.stage-block:hover:not(.active) .block-content {
  background: rgba(255, 255, 255, 0.5);
}
</style>
