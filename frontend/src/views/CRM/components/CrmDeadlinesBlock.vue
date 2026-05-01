<template>
  <div class="crm-section crm-deadlines-section">
    <div class="deadlines-block-head">
      <span class="deadlines-kicker">Крок 4 · Час</span>
      <h3>Терміни та пріоритет</h3>
    </div>

    <div class="deadlines-grid">
      <div class="crm-field">
        <label class="crm-label">Бажаний дедлайн</label>
        <el-date-picker
          v-model="form.deadline_date"
          type="date"
          placeholder="Оберіть дату"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="deadline-picker-modern"
        >
          <template #prefix><el-icon><Calendar /></el-icon></template>
        </el-date-picker>
        <transition name="fade">
          <span v-if="!form.deadline_date" class="deadline-warning">
            <el-icon><Warning /></el-icon>
            Вкажіть дату готовності замовлення
          </span>
        </transition>
      </div>

      <div class="crm-field">
        <label class="crm-label">Пріоритет виконання</label>
        <el-select v-model="form.priority" placeholder="Оберіть пріоритет" class="priority-select-modern">
          <template #prefix>
            <span
              v-if="selectedPriority?.color"
              class="priority-dot"
              :style="{ background: selectedPriority?.color }"
            />
            <el-icon v-else><Flag /></el-icon>
          </template>
          <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value">
            <div class="priority-option">
              <span class="priority-dot" :style="{ background: p.color || '#94a3b8' }" />
              {{ p.label }}
            </div>
          </el-option>
        </el-select>
      </div>
    </div>

    <div class="deadlines-footer">
      <div class="created-at-info">
        <el-icon><Clock /></el-icon>
        Дата створення: <span>{{ formatDate(form.order_date) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, Flag, Warning, Clock } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
  priorities: { type: Array, required: true },
  formatDate: { type: Function, required: true },
})

const selectedPriority = computed(() => props.priorities.find(p => p.value === props.form.priority))
</script>

<style scoped>
.crm-deadlines-section {
  padding: 24px;
}

.deadlines-block-head {
  margin-bottom: 24px;
}

.deadlines-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: #6366F1;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.deadlines-block-head h3 {
  margin: 0;
  color: #0F172A;
  font-size: 20px;
  font-weight: 800;
}

.deadlines-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.deadline-picker-modern, .priority-select-modern {
  width: 100%;
}

.deadline-warning {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 11px;
  color: #EF4444;
  font-weight: 600;
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.priority-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.deadlines-footer {
  padding-top: 16px;
  border-top: 1px solid #F1F5F9;
}

.created-at-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748B;
}

.created-at-info span {
  color: #0F172A;
  font-weight: 700;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
}

@media (max-width: 1024px) {
  .deadlines-grid {
    grid-template-columns: 1fr;
  }
}
</style>
