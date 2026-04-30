<template>
  <div class="crm-insights-row">
    <div class="crm-insight-card primary">
      <div class="insight-content">
        <span class="insight-label">Pipeline</span>
        <div class="insight-value-row">
          <strong>{{ formatCurrency(totalPipelineAmount) }} ₴</strong>
          <div class="insight-sparkline">
            <svg width="56" height="20" viewBox="0 0 64 28">
              <path d="M0 22C12 18 24 20 36 13C48 6 56 10 64 6" stroke="rgba(255,255,255,0.6)" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <small>{{ ordersCount }} активних замовлень</small>
      </div>
    </div>
    <div class="crm-insight-card warning">
      <div class="insight-content">
        <span class="insight-label">Гарячі SLA</span>
        <strong>{{ hotSlaCount }}</strong>
        <small>потребують уваги</small>
      </div>
    </div>
    <div class="crm-insight-card info">
      <div class="insight-content">
        <span class="insight-label">Оплата</span>
        <strong>{{ paymentProgress }}%</strong>
        <small>сплачених замовлень</small>
      </div>
    </div>
    <div class="crm-insight-card danger">
      <div class="insight-content">
        <span class="insight-label">Сьогодні</span>
        <strong>{{ todayTasksCount }}</strong>
        <small>{{ overdueTasksCount }} прострочено</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Bell, Calendar, TrendCharts, Money } from '@element-plus/icons-vue'

defineProps({
  ordersCount: { type: Number, default: 0 },
  totalPipelineAmount: { type: Number, default: 0 },
  hotSlaCount: { type: Number, default: 0 },
  paymentProgress: { type: Number, default: 0 },
  todayTasksCount: { type: Number, default: 0 },
  overdueTasksCount: { type: Number, default: 0 },
  formatCurrency: { type: Function, required: true }
})
</script>
