<template>
  <div class="crm-insights-row">
    <!-- Всього позицій -->
    <div class="crm-insight-card metric-pipeline">
      <div class="insight-content">
        <span class="metric-label">Всього позицій</span>
        <div class="insight-value-row">
          <strong class="metric-value">{{ stats.total_products }}</strong>
          <div class="insight-sparkline">
            <svg width="56" height="20" viewBox="0 0 64 28">
              <path d="M0 22C12 18 24 20 36 13C48 6 56 10 64 6" stroke="rgba(20,99,255,0.4)" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <small>Зареєстровано в системі</small>
      </div>
    </div>

    <!-- Низький запас -->
    <div class="crm-insight-card metric-sla">
      <div class="insight-content">
        <span class="metric-label">Низький запас</span>
        <strong class="metric-value">{{ stats.low_stock }}</strong>
        <small>потребують дозамовлення</small>
      </div>
    </div>

    <!-- В наявності -->
    <div class="crm-insight-card metric-payment">
      <div class="insight-content">
        <span class="metric-label">В наявності</span>
        <strong class="metric-value">{{ stats.in_stock }}</strong>
        <small>доступно для продажу</small>
      </div>
    </div>

    <!-- Немає в наявності -->
    <div class="crm-insight-card metric-today">
      <div class="insight-content">
        <span class="metric-label">Дефіцит</span>
        <strong class="metric-value">{{ stats.out_of_stock }}</strong>
        <small>критичні відсутності</small>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      total_products: 0,
      in_stock: 0,
      low_stock: 0,
      out_of_stock: 0
    })
  }
})
</script>

<style scoped>
.crm-insights-row {
  display: grid;
  grid-template-columns: 1.25fr repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.crm-insight-card {
  background: #FFFFFF;
  border: 0.5px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 18px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
  display: flex;
  align-items: center;
  gap: 12px;
  transition: transform 0.18s, box-shadow 0.18s;
  height: 80px;
  box-sizing: border-box;
}

.crm-insight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}

/* Indicator rails matching CRM */
.crm-insight-card.metric-pipeline { border-left: 4px solid #1463FF; }
.crm-insight-card.metric-sla      { border-left: 4px solid #F59E0B; }
.crm-insight-card.metric-payment  { border-left: 4px solid #15B97A; }
.crm-insight-card.metric-today    { border-left: 4px solid #EF4444; }

.insight-content { flex: 1; min-width: 0; }

.metric-label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94A3B8;
  margin-bottom: 2px;
}

.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px;
  font-weight: 800;
  color: #0F172A;
  display: block;
  line-height: 1.1;
}

.insight-value-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 4px;
}

.insight-sparkline { opacity: 0.6; }

.crm-insight-card small {
  display: block;
  font-size: 11px;
  color: #64748B;
  font-weight: 500;
  margin-top: 2px;
}
</style>
