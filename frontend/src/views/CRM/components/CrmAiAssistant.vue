<template>
  <div class="crm-section ai-assistant-modern">
    <div class="ai-header">
      <div class="ai-brand">
        <div class="ai-icon-wrapper">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="ai-title-block">
          <span class="ai-kicker">Розумні підказки</span>
          <h3>AI Асистент</h3>
        </div>
      </div>
      <button class="ai-refresh-btn" @click="$emit('check')" title="Оновити аналіз">
        <el-icon><Refresh /></el-icon>
      </button>
    </div>

    <div class="ai-insights-container">
      <transition-group name="list">
        <div class="ai-insight-card" v-if="readinessProgress < 100" key="readiness" class-name="warning">
          <div class="insight-icon"><el-icon><Warning /></el-icon></div>
          <div class="insight-content">
            <p>Заявка готова на <b>{{ readinessProgress }}%</b>. Заповніть відсутні поля для успішного запуску.</p>
          </div>
        </div>

        <div class="ai-insight-card error" v-if="['new', 'payment'].includes(form.crm_stage) && !form.next_contact_at" key="contact">
          <div class="insight-icon"><el-icon><Calendar /></el-icon></div>
          <div class="insight-content">
            <p><b>Контакт не заплановано!</b> Клієнт може «охолонути». Вкажіть дату наступного кроку.</p>
          </div>
        </div>

        <div class="ai-insight-card info" v-if="form.total_amount > 0 && (form.prepayment_amount || 0) < (form.total_amount * 0.2)" key="prepay">
          <div class="insight-icon"><el-icon><Money /></el-icon></div>
          <div class="insight-content">
            <p>Передоплата менше 20%. Спробуйте погодити вищий аванс для фіксації замовлення.</p>
          </div>
        </div>

        <div class="ai-insight-card success" v-if="readinessProgress === 100" key="success">
          <div class="insight-icon"><el-icon><SuccessFilled /></el-icon></div>
          <div class="insight-content">
            <p>Чудова робота! Всі дані зібрані. Можна передавати замовлення у виробництво.</p>
          </div>
        </div>
      </transition-group>
    </div>

    <div class="ai-footer">
      <span class="ai-sam-tip">Креативність від Сема: «Спілкування — це ключ. Спробуйте запропонувати клієнту невелику знижку за 100% оплату сьогодні.»</span>
    </div>
  </div>
</template>

<script setup>
import { Calendar, MagicStick, Money, SuccessFilled, Warning, Refresh } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
  readinessProgress: { type: Number, required: true },
})

defineEmits(['check'])
</script>

<style scoped>
.ai-assistant-modern {
  background: linear-gradient(135deg, #F0FDFA 0%, #E6FFFA 100%);
  border: 1px solid #CCFBF1 !important;
  padding: 24px;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ai-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon-wrapper {
  width: 36px;
  height: 36px;
  background: #14B8A6;
  color: #fff;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 20px;
  box-shadow: 0 4px 10px rgba(20, 184, 166, 0.3);
}

.ai-kicker {
  display: block;
  font-size: 10px;
  font-weight: 800;
  color: #0D9488;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.ai-title-block h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #0F172A;
}

.ai-refresh-btn {
  background: transparent;
  border: none;
  color: #0D9488;
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.3s ease;
}

.ai-refresh-btn:hover { transform: rotate(180deg); }

.ai-insights-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-insight-card {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  font-size: 13px;
  line-height: 1.4;
  color: #374151;
}

.insight-icon {
  font-size: 18px;
  margin-top: 1px;
}

.ai-insight-card.error { border-left: 4px solid #EF4444; }
.ai-insight-card.warning { border-left: 4px solid #F59E0B; }
.ai-insight-card.info { border-left: 4px solid #6366F1; }
.ai-insight-card.success { border-left: 4px solid #10B981; }

.insight-content p { margin: 0; }
.insight-content b { color: #0F172A; font-weight: 700; }

.ai-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(20, 184, 166, 0.1);
}

.ai-sam-tip {
  font-size: 11px;
  font-style: italic;
  color: #0D9488;
  line-height: 1.4;
  display: block;
}

.list-enter-active, .list-leave-active { transition: all 0.4s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(20px); }
</style>
