<template>
  <div class="metric-card" :style="{ borderBottomColor: accentColor }">
    <div class="metric-header">
      <!-- Component comment to force Docker container volume sync -->
      <span class="metric-label">{{ label }}</span>
      <span v-if="trend" :class="['metric-trend', trendUp ? 'trend-up' : 'trend-down']">
        {{ trendUp ? '↑' : '↓' }} {{ trend }}
      </span>
    </div>
    <span class="metric-value">{{ value }}</span>
    
    <div class="metric-sparkline-container" v-if="sparklineData && sparklineData.length">
      <svg class="metric-sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
        <path :d="sparklinePath" fill="none" :stroke="accentColor" stroke-width="2" />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  trend: { type: String, default: '' },
  trendUp: { type: Boolean, default: true },
  sparklineData: { type: Array, default: () => [] },
  accentColor: { type: String, default: '#3B82F6' }
})

const sparklinePath = computed(() => {
  if (!props.sparklineData || props.sparklineData.length < 2) return ''
  
  const data = props.sparklineData
  const maxVal = Math.max(...data)
  const minVal = Math.min(...data)
  const range = maxVal - minVal || 1
  
  // SVG is 100 width, 30 height
  const points = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * 100
    // SVG coordinates start top-left, invert Y axis
    const y = 28 - ((val - minVal) / range) * 26
    return `${x} ${y}`
  })
  
  return `M ${points.join(' L ')}`
})
</script>

<style scoped>
.metric-card {
  background: #FFFFFF;
  border: 1px solid #F3F4F6;
  border-bottom: 2px solid #3B82F6;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
  transform: translateY(-2px);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9CA3AF;
}

.metric-trend {
  font-size: 11px;
  font-weight: 600;
}
.trend-up {
  color: #22C55E;
}
.trend-down {
  color: #EF4444;
}

.metric-value {
  font-size: 28px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500;
  color: #18181B;
  margin-top: 10px;
  line-height: 1.2;
}

.metric-sparkline-container {
  position: absolute;
  bottom: 4px;
  left: 0;
  right: 0;
  height: 20px;
  z-index: 1;
  opacity: 0.5;
}

.metric-sparkline {
  width: 100%;
  height: 100%;
}
</style>
