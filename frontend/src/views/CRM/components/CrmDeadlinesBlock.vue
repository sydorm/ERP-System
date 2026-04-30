<template>
  <div class="crm-section" style="background: white; border: 1px solid #EBEBEB; border-radius: 12px; padding: 16px; margin-top: 16px;">
    <div style="font-size: 10px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;">
      ТЕРМІНИ ТА ПРІОРИТЕТ
    </div>

    <div class="crm-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
      <div class="crm-field">
        <label class="crm-label">Бажаний дедлайн (обов'язково)</label>
        <el-date-picker
          v-model="form.deadline_date"
          type="date"
          placeholder="Оберіть дату"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
        <span v-if="!form.deadline_date" style="font-size: 11px; color: #EF4444; margin-top: 2px; display: inline-block;">
          ⚠️ Будь ласка, вкажіть дату готовності
        </span>
      </div>

      <div class="crm-field">
        <label class="crm-label">Пріоритет</label>
        <el-select v-model="form.priority" placeholder="Оберіть пріоритет" style="width: 100%">
          <template #prefix>
            <span
              v-if="selectedPriority?.color"
              style="width: 8px; height: 8px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 2px;"
              :style="{ background: selectedPriority?.color }"
            />
          </template>
          <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span style="width: 8px; height: 8px; border-radius: 50%; display: inline-block;" :style="{ background: p.color || '#94a3b8' }" />
              {{ p.label }}
            </div>
          </el-option>
        </el-select>
      </div>
    </div>

    <div class="crm-date-row" style="font-size: 12px; color: #475569;">
      <div class="date-item">Дата створення: <span class="date-val" style="font-weight: 600; color: #1E293B;">{{ formatDate(form.order_date) }}</span></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  priorities: { type: Array, required: true },
  formatDate: { type: Function, required: true },
})

const selectedPriority = computed(() => props.priorities.find(p => p.value === props.form.priority))
</script>
