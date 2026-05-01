<template>
  <div class="crm-section readiness-card-modern">
    <div class="readiness-header">
      <div class="title-block">
        <span class="kicker">Прогрес заповнення</span>
        <h3>Готовність заявки</h3>
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
          <el-icon v-if="item.done"><CircleCheckFilled /></el-icon>
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
.readiness-card-modern {
  padding: 24px;
}

.readiness-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.kicker {
  display: block;
  font-size: 10px;
  font-weight: 800;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.title-block h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #0F172A;
}

.progress-percent {
  font-size: 24px;
  font-weight: 900;
  color: #6366F1;
  font-variant-numeric: tabular-nums;
}

.progress-percent.complete {
  color: #10B981;
}

.progress-bar-container {
  height: 8px;
  background: #F1F5F9;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 24px;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366F1 0%, #10B981 100%);
  border-radius: 4px;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  opacity: 0.6;
  transition: all 0.3s;
}

.checklist-item.done {
  opacity: 1;
}

.check-icon {
  font-size: 18px;
  color: #10B981;
}

.check-circle {
  width: 16px;
  height: 16px;
  border: 2px solid #CBD5E1;
  border-radius: 50%;
}

.item-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.done .item-label {
  color: #0F172A;
}
</style>
