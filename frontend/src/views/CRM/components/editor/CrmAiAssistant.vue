<template>
  <div class="crm-section ai-assistant-card" style="background: #F0FDFA; border: 1px solid #CCFBF1; border-radius: 12px; padding: 16px; margin-top: 12px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
      <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #0D9488; text-transform: uppercase; letter-spacing: 0.8px;">
        <el-icon><MagicStick /></el-icon>
        <span>AI Помічник</span>
      </div>
      <el-button type="primary" size="small" plain @click="$emit('check')">Перевірити</el-button>
    </div>

    <div class="ai-insights-list" style="display: flex; flex-direction: column; gap: 8px; font-size: 12px; color: #1F2937;">
      <div class="ai-insight-item" v-if="readinessProgress < 100" style="display: flex; align-items: flex-start; gap: 6px;">
        <el-icon style="color: #F59E0B; margin-top: 2px;"><Warning /></el-icon>
        <span>Заявку заповнено на {{ readinessProgress }}%. Дозаповніть обов'язкові параметри для запуску.</span>
      </div>

      <template v-if="['new', 'payment'].includes(form.crm_stage)">
        <div class="ai-insight-item" v-if="!form.next_contact_at" style="display: flex; align-items: flex-start; gap: 6px;">
          <el-icon style="color: #EF4444; margin-top: 2px;"><Calendar /></el-icon>
          <span>Наступний контакт не заплановано. Ризик втрати клієнта!</span>
        </div>
      </template>

      <div class="ai-insight-item" style="display: flex; align-items: flex-start; gap: 6px;" v-if="form.total_amount > 0 && (form.prepayment_amount || 0) < (form.total_amount * 0.2)">
        <el-icon style="color: #3D3AA8; margin-top: 2px;"><Money /></el-icon>
        <span>Низький рівень передоплати (менше 20%). Рекомендовано отримати завдаток.</span>
      </div>

      <div class="ai-insight-item" style="display: flex; align-items: flex-start; gap: 6px;" v-if="readinessProgress === 100">
        <el-icon style="color: #10B981; margin-top: 2px;"><SuccessFilled /></el-icon>
        <span>Всі дані зібрані. Можна сміливо передавати заявку в роботу!</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Calendar, MagicStick, Money, SuccessFilled, Warning } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
  readinessProgress: { type: Number, default: 0 }
})

defineEmits(['check'])
</script>
