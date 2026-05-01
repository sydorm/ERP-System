<template>
  <div class="readiness-card-compact">
    <div class="readiness-header">
      <div class="title-block">
        <span class="kicker">Прогрес заповнення</span>
        <h3 class="text-sm font-extrabold text-slate-800">Готовність заявки</h3>
      </div>
      <div class="progress-percent" :class="{ complete: progress === 100 }">
        {{ progress }}%
      </div>
    </div>

    <div class="progress-bar-container">
      <div class="progress-bar-fill" :style="{ width: `${progress}%` }" />
    </div>

    <div class="checklist-items">
      <div v-for="item in items" :key="item.key" class="checklist-item" :class="{ done: item.done }">
        <div class="check-icon">
          <el-icon v-if="item.done" class="text-emerald-500"><CircleCheckFilled /></el-icon>
          <div v-else class="check-circle" />
        </div>
        <span class="item-label">{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CircleCheckFilled } from '@element-plus/icons-vue'
defineProps({
  progress: { type: Number, required: true },
  items: { type: Array, required: true },
})
</script>

<style scoped>
.readiness-card-compact {
  padding: 20px;
}

.readiness-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kicker {
  display: block;
  font-size: 9px;
  font-weight: 800;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.progress-percent {
  font-size: 20px;
  font-weight: 900;
  color: #6366F1;
}

.progress-percent.complete {
  color: #10B981;
}

.progress-bar-container {
  height: 6px;
  background: #F1F5F9;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-bar-fill {
  height: 100%;
  background: #6366F1;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.complete + .progress-bar-container .progress-bar-fill {
  background: #10B981;
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0.5;
  transition: all 0.2s;
}

.checklist-item.done {
  opacity: 1;
}

.check-icon {
  font-size: 16px;
  display: flex;
  align-items: center;
}

.check-circle {
  width: 14px;
  height: 14px;
  border: 1.5px solid #CBD5E1;
  border-radius: 50%;
}

.item-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
}

.done .item-label {
  color: #1E293B;
}
</style>
