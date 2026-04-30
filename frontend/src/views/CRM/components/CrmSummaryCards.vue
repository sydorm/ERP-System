<template>
  <div class="crm-insights-row">
    <div class="crm-insight-card metric-pipeline">
      <div class="insight-content">
        <span class="metric-label">Pipeline</span>
        <div class="insight-value-row">
          <strong class="metric-value">{{ formatCurrency(totalPipelineAmount) }} ₴</strong>
          <div class="insight-sparkline">
            <svg width="56" height="20" viewBox="0 0 64 28">
              <path d="M0 22C12 18 24 20 36 13C48 6 56 10 64 6" stroke="rgba(108,99,255,0.45)" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <small>{{ ordersCount }} активних замовлень</small>
      </div>
    </div>
    <div class="crm-insight-card metric-sla">
      <div class="insight-content">
        <span class="metric-label">Гарячі SLA</span>
        <strong class="metric-value">{{ hotSlaCount }}</strong>
        <small>потребують уваги</small>
      </div>
    </div>
    <div class="crm-insight-card metric-payment">
      <div class="insight-content">
        <span class="metric-label">Оплата</span>
        <strong class="metric-value">{{ paymentProgress }}%</strong>
        <small>сплачених замовлень</small>
      </div>
    </div>
    <div class="crm-insight-card metric-today">
      <div class="insight-content">
        <span class="metric-label">Сьогодні</span>
        <strong class="metric-value">{{ todayTasksCount }}</strong>
        <small>{{ overdueTasksCount }} прострочено</small>
      </div>
    </div>
  </div>
</template>

<script setup>
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
