<template>
  <div class="crm-section crm-deadlines-section-premium">
    <div class="deadlines-block-header">
      <div class="header-main">
        <div class="step-badge">Крок 4</div>
        <div class="title-group">
          <h3>Терміни та пріоритет</h3>
          <p>Планування дати готовності та черговості виконання</p>
        </div>
      </div>
      <div class="header-status">
        <div class="glass-pill" :class="{ 'warning-glow': !form.deadline_date }">
          <el-icon><Calendar /></el-icon>
          <span>{{ form.deadline_date || 'Очікує дату' }}</span>
        </div>
      </div>
    </div>

    <div class="deadlines-interactive-grid">
      <div class="deadline-input-zone">
        <label class="premium-label">Бажаний дедлайн</label>
        <el-date-picker
          v-model="form.deadline_date"
          type="date"
          placeholder="Оберіть дату дедлайну"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="premium-date-picker"
        >
          <template #prefix>
            <el-icon class="picker-icon-modern"><Calendar /></el-icon>
          </template>
        </el-date-picker>
        <transition name="fade">
          <div v-if="!form.deadline_date" class="deadline-warning-modern">
            <el-icon><Warning /></el-icon>
            Вкажіть дату готовності замовлення
          </div>
        </transition>
      </div>

      <div class="priority-selection-zone">
        <label class="premium-label">Пріоритет виконання</label>
        <div class="priority-pills-modern">
          <button
            v-for="p in priorities"
            :key="p.value"
            class="priority-pill-btn"
            :class="{ active: form.priority === p.value }"
            @click="form.priority = p.value"
          >
            <span class="p-dot" :style="{ background: p.color || '#94a3b8' }" />
            {{ p.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="deadlines-footer-premium">
      <div class="history-info">
        <div class="info-item">
          <el-icon><Clock /></el-icon>
          Заявку створено: <span>{{ formatDate(form.order_date) }}</span>
        </div>
      </div>
      <div class="footer-tip">
        <el-icon><InfoFilled /></el-icon>
        <span>Дедлайн впливає на чергу у виробничому календарі</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, Warning, Clock, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
  priorities: { type: Array, required: true },
  formatDate: { type: Function, required: true },
})

const selectedPriority = computed(() => props.priorities.find(p => p.value === props.form.priority))
</script>

<style scoped>
.crm-deadlines-section-premium {
  padding: 32px;
  background: #fff;
  border-radius: 24px;
}

.deadlines-block-header {
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
  border: 1px solid #E2E8F0;
}

.warning-glow {
  background: #FFF1F2;
  color: #E11D48;
  border-color: #FECDD3;
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.2); }
  70% { box-shadow: 0 0 0 10px rgba(225, 29, 72, 0); }
  100% { box-shadow: 0 0 0 0 rgba(225, 29, 72, 0); }
}

.deadlines-interactive-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 40px;
  margin-bottom: 32px;
}

.premium-label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 12px;
}

:deep(.premium-date-picker) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 16px;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 12px 16px;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #CBD5E1 inset !important;
}

.deadline-warning-modern {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 12px;
  color: #E11D48;
  font-weight: 600;
}

.priority-pills-modern {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.priority-pill-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: #F8FAFC;
  border: 1.5px solid #F1F5F9;
  border-radius: 16px;
  color: #1E293B;
  font-size: 14px;
  font-weight: 750;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.priority-pill-btn:hover {
  background: #fff;
  border-color: #E2E8F0;
  transform: translateY(-2px);
}

.priority-pill-btn.active {
  background: #fff;
  border-color: #0F172A;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.p-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.deadlines-footer-premium {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid #F1F5F9;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748B;
  font-weight: 600;
}

.info-item span {
  color: #1E293B;
  font-weight: 800;
}

.footer-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94A3B8;
  font-style: italic;
}

@media (max-width: 992px) {
  .deadlines-interactive-grid { grid-template-columns: 1fr; gap: 24px; }
  .deadlines-footer-premium { flex-direction: column; gap: 16px; text-align: center; }
}
</style>
