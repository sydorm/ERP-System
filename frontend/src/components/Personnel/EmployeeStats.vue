<template>
  <div class="kpi-grid-modern">
    <div v-for="stat in stats" :key="stat.title" class="kpi-card-modern">
      <div class="kpi-header-row">
        <div class="kpi-icon-wrapper" :style="{ backgroundColor: stat.colorBg, color: stat.colorIcon }">
          <el-icon><component :is="stat.icon" /></el-icon>
        </div>
        <div :class="['kpi-trend', stat.trend >= 0 ? 'trend-up' : 'trend-down']">
          {{ stat.trend >= 0 ? '+' : '' }}{{ stat.trend }}%
        </div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stat.value }}</div>
        <div class="kpi-label">{{ stat.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * @typedef {Object} StatCard
 * @property {string} title - The title of the stat
 * @property {string|number} value - The display value
 * @property {number} trend - Percentage trend (positive or negative)
 * @property {string} icon - Element Plus icon name
 * @property {string} colorIcon - Hex color for the icon
 * @property {string} colorBg - RGBA color for the icon background
 * @property {boolean} trendUp - Whether the trend is positive
 */

defineProps({
  /** @type {StatCard[]} */
  stats: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>

<style scoped>
.kpi-grid-modern {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.kpi-card-modern {
  background: var(--nexora-bg-card);
  padding: 20px;
  border-radius: var(--nexora-radius-xl);
  box-shadow: var(--nexora-shadow-sm);
  border: 1px solid var(--nexora-border-light);
  transition: all 0.3s ease;
}

.kpi-card-modern:hover {
  transform: translateY(-4px);
  box-shadow: var(--nexora-shadow-md);
}

.kpi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.kpi-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: var(--nexora-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.kpi-trend {
  font-size: 13px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: var(--nexora-radius-md);
}

.trend-up {
  background: rgba(40, 199, 111, 0.12);
  color: var(--nexora-success);
}

.trend-down {
  background: rgba(234, 84, 85, 0.12);
  color: var(--nexora-danger);
}

.kpi-value {
  font-size: 26px;
  font-weight: 800;
  color: var(--nexora-text-heading);
  line-height: 1.2;
}

.kpi-label {
  font-size: 14px;
  color: var(--nexora-text-muted);
  font-weight: 600;
  margin-top: 4px;
}
</style>
