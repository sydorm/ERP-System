<template>
  <div class="crm-section crm-deadlines-block-premium">
    <div class="deadlines-header-compact">
      <div class="header-main">
        <div class="step-badge-mini">Крок 4</div>
        <h3 class="text-base font-extrabold text-slate-800">Терміни та пріоритет</h3>
      </div>
      <div class="header-status">
        <div class="status-pill-mini" :class="{ 'warning': !form.deadline_date }">
          <el-icon><Calendar /></el-icon>
          <span>{{ form.deadline_date || 'Очікує дату' }}</span>
        </div>
      </div>
    </div>

    <div class="deadlines-grid-compact">
      <!-- Date Picker Zone -->
      <div class="input-card-premium">
        <label><el-icon class="text-indigo-400"><Calendar /></el-icon> Бажаний дедлайн</label>
        <el-date-picker
          v-model="form.deadline_date"
          type="date"
          placeholder="Оберіть дату"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="compact-date-picker"
        />
      </div>

      <!-- Priority Zone -->
      <div class="input-card-premium">
        <label><el-icon class="text-indigo-400"><Flag /></el-icon> Пріоритет виконання</label>
        <div class="priority-row">
          <button
            v-for="p in priorities"
            :key="p.value"
            class="p-btn"
            :class="{ active: form.priority === p.value }"
            :title="p.label"
            @click="form.priority = p.value"
          >
            <span class="p-dot" :style="{ background: p.color }" />
            <span class="p-label">{{ p.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="deadlines-footer-compact">
      <div class="footer-info">
        <div class="info-item">
          <el-icon><Clock /></el-icon>
          Створено: <span class="font-bold ml-1 text-slate-700">{{ formatDate(form.order_date) }}</span>
        </div>
        <div class="info-item tip">
          <el-icon><InfoFilled /></el-icon>
          <span>Впливає на чергу у виробництві</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Calendar, Clock, InfoFilled, Flag } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
  priorities: { type: Array, required: true },
  formatDate: { type: Function, required: true },
})
</script>

<style scoped>
.crm-deadlines-block-premium {
  padding: 20px;
  background: #fff;
  border-radius: 24px;
}

.deadlines-header-compact {
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
  background: #1463FF;
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

.status-pill-mini.warning {
  background: #FFF1F2;
  color: #E11D48;
}

.deadlines-grid-compact {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 16px;
  margin-bottom: 20px;
}

/* Unified style with CrmClientBlock */
.input-card-premium {
  @apply flex flex-col gap-1 p-2.5 rounded-xl transition-all duration-200;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 64px;
}

.input-card-premium label {
  @apply flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 px-0.5;
}

.priority-row {
  display: flex;
  gap: 8px;
  margin-top: 2px;
}

.p-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.p-btn:hover {
  border-color: #6366F1;
}

.p-btn.active {
  border-color: #1E293B;
  background: #F8FAFC;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.p-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.p-label {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

:deep(.compact-date-picker) {
  width: 100% !important;
}

:deep(.el-input__wrapper) {
  @apply shadow-none bg-transparent border-none p-0 h-7 !important;
  box-shadow: none !important;
}

:deep(.el-input__inner) {
  @apply font-bold text-slate-700 text-[13px] !important;
}

.deadlines-footer-compact {
  padding-top: 16px;
  border-top: 1px solid #F1F5F9;
}

.footer-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748B;
  font-weight: 600;
}

.info-item.tip {
  color: #94A3B8;
  font-style: italic;
}

@media (max-width: 768px) {
  .deadlines-grid-compact { grid-template-columns: 1fr; }
  .footer-info { flex-direction: column; gap: 8px; align-items: flex-start; }
}
</style>
