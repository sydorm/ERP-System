<template>
  <div class="premium-dashboard">
    <!-- Background glowing decorations -->
    <div class="glow-orb glow-orb-1"></div>
    <div class="glow-orb glow-orb-2"></div>

    <div class="dashboard-header">
      <div class="title-block">
        <h1 class="main-title">Smart Warehouse Analytics</h1>
        <p class="sub-title">Оперативний моніторинг та аналіз логістики за 2026 рік</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="glass-btn" @click="refreshAll">
          Оновити дані
        </el-button>
      </div>
    </div>

    <!-- Top Metrics Row -->
    <el-row :gutter="24" class="metrics-grid">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in stats" :key="index">
        <div class="glass-card metric-card" :style="'--border-color: ' + stat.color">
          <div class="card-icon" :style="{ background: stat.color }">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="card-data">
            <span class="metric-label">{{ stat.label }}</span>
            <span class="metric-value">{{ stat.value }}</span>
            <span class="metric-trend" :class="stat.trendClass">
              {{ stat.trend }}
            </span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Central Visualization Hub -->
    <el-row :gutter="24" class="mt-6">
      <el-col :xs="24" :md="16">
        <div class="glass-card visual-card main-chart-card">
          <h3 class="card-title">Завантаженість Складських Зон</h3>
          
          <div class="chart-container mt-4">
            <!-- Premium SVG Chart Representation -->
            <div class="custom-bars">
              <div class="bar-group" v-for="zone in storageZones" :key="zone.name">
                <div class="bar-header">
                  <span class="zone-name">{{ zone.name }}</span>
                  <span class="zone-percentage">{{ zone.filled }}%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: zone.filled + '%', background: zone.color }">
                    <div class="bar-glow" :style="{ background: zone.color }"></div>
                  </div>
                </div>
                <div class="bar-footer">
                  <span>Вільно: {{ zone.free }} м²</span>
                  <span>Всього: {{ zone.capacity }} м²</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :md="8">
        <div class="glass-card visual-card pie-card">
          <h3 class="card-title">Структура Запасів</h3>
          
          <!-- SVG Interactive Donut Chart -->
          <div class="donut-container mt-4">
            <svg class="donut-svg" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1e293b" stroke-width="12"></circle>
              <circle 
                cx="50" 
                cy="50" 
                r="40" 
                fill="transparent" 
                stroke="url(#purple-grad)" 
                stroke-width="12" 
                stroke-dasharray="125.6 251.2" 
                stroke-dashoffset="0"
                class="animated-circle"
              ></circle>
              <circle 
                cx="50" 
                cy="50" 
                r="40" 
                fill="transparent" 
                stroke="url(#blue-grad)" 
                stroke-width="12" 
                stroke-dasharray="75.3 251.2" 
                stroke-dashoffset="-125.6"
                class="animated-circle delay-1"
              ></circle>
              <circle 
                cx="50" 
                cy="50" 
                r="40" 
                fill="transparent" 
                stroke="url(#orange-grad)" 
                stroke-width="12" 
                stroke-dasharray="50.2 251.2" 
                stroke-dashoffset="-200.9"
                class="animated-circle delay-2"
              ></circle>
              
              <!-- Gradients -->
              <defs>
                <linearGradient id="purple-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#a855f7" />
                  <stop offset="100%" stop-color="#6366f1" />
                </linearGradient>
                <linearGradient id="blue-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#3b82f6" />
                  <stop offset="100%" stop-color="#06b6d4" />
                </linearGradient>
                <linearGradient id="orange-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#f97316" />
                  <stop offset="100%" stop-color="#e11d48" />
                </linearGradient>
              </defs>
            </svg>
            <div class="donut-center">
              <span class="donut-total">{{ totalStockQty }}</span>
              <span class="donut-label">од. товару</span>
            </div>
          </div>

          <div class="donut-legend mt-4">
            <div class="legend-item"><span class="dot purple"></span> Сировина (50%)</div>
            <div class="legend-item"><span class="dot blue"></span> Напівфабрикати (30%)</div>
            <div class="legend-item"><span class="dot orange"></span> Готові вироби (20%)</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Bottom Status Board -->
    <div class="glass-card mt-6 data-table-card">
      <div class="expand-header">
        <h3 class="card-title">Поточний стан операцій на складах</h3>
      </div>
      
      <el-table :data="recentOperations" style="width: 100%; background: transparent;" class="glass-table mt-4">
        <el-table-column prop="time" label="Час" width="120" />
        <el-table-column prop="type" label="Операція" width="150">
          <template #default="scope">
            <el-tag :type="scope.row.typeClass" effect="dark" size="small">{{ scope.row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="document" label="Документ" min-width="150" />
        <el-table-column prop="status" label="Статус" width="120">
          <template #default="scope">
            <span class="pulse-status" :class="scope.row.statusClass">{{ scope.row.status }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Box, Location, List, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const totalStockQty = ref(2480)

const stats = ref([
  { label: 'Загальний обсяг', value: '2,480 шт', trend: '▲ +12% з минулого тижня', trendClass: 'trend-up', icon: Box, color: 'linear-gradient(135deg, #6366f1, #a855f7)' },
  { label: 'Фінансова оцінка', value: '1,204,500 ₴', trend: '▲ +4.5% закупівель', trendClass: 'trend-up', icon: Money, color: 'linear-gradient(135deg, #10b981, #059669)' },
  { label: 'Задіяні локації', value: '3 склади', trend: 'Без змін', trendClass: 'trend-neutral', icon: Location, color: 'linear-gradient(135deg, #3b82f6, #06b6d4)' },
  { label: 'Критичні залишки', value: '14 позицій', trend: '▼ -2 дефіцити', trendClass: 'trend-down', icon: List, color: 'linear-gradient(135deg, #f97316, #e11d48)' }
])

const storageZones = ref([
  { name: 'Зона Сировини (A1)', filled: 85, free: 45, capacity: 300, color: 'linear-gradient(90deg, #6366f1, #a855f7)' },
  { name: 'Зона Пакування (B2)', filled: 40, free: 120, capacity: 200, color: 'linear-gradient(90deg, #3b82f6, #06b6d4)' },
  { name: 'Готова Продукція (C3)', filled: 68, free: 160, capacity: 500, color: 'linear-gradient(90deg, #10b981, #059669)' }
])

const recentOperations = ref([
  { time: '10:45', type: 'Прибуття', document: 'ПН-000456 (ТОВ МеталБуд)', status: 'Виконується', statusClass: 'status-active', typeClass: 'primary' },
  { time: '09:20', type: 'Відвантаження', document: 'РН-000112 (Нова Пошта)', status: 'Завершено', statusClass: 'status-done', typeClass: 'success' },
  { time: 'Вчора', type: 'Списання', document: 'АКТ-000014 (Брак виробництва)', status: 'Архів', statusClass: 'status-archive', typeClass: 'danger' }
])

const refreshAll = () => {
  ElMessage.success('Аналітика оновлена!')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Outfit:wght@300;500;700&display=swap');

.premium-dashboard {
  font-family: 'Outfit', sans-serif;
  padding: 30px;
  background: #0f172a;
  color: #e2e8f0;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* Background orbs */
.glow-orb {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
  pointer-events: none;
  z-index: 0;
}
.glow-orb-1 {
  background: #6366f1;
  top: -10%;
  right: -10%;
}
.glow-orb-2 {
  background: #06b6d4;
  bottom: -10%;
  left: -10%;
}

.dashboard-header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.main-title {
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 2.2rem;
  background: linear-gradient(to right, #fff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.sub-title {
  color: #94a3b8;
  margin-top: 5px;
}

.glass-card {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
  z-index: 1;
  position: relative;
}

.glass-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 20px;
  border-left: 4px solid var(--border-color, transparent);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.card-data {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.85rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: white;
  margin: 5px 0;
}

.metric-trend {
  font-size: 0.75rem;
}
.trend-up { color: #10b981; }
.trend-down { color: #f43f5e; }
.trend-neutral { color: #64748b; }

.card-title {
  font-size: 1.1rem;
  font-weight: 500;
  color: #f1f5f9;
  margin: 0;
}

/* Zone capacity custom bars */
.custom-bars {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.bar-header, .bar-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}
.bar-header { color: #e2e8f0; font-weight: 500; }
.bar-footer { color: #64748b; margin-top: 5px; }

.bar-track {
  height: 12px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 6px;
  position: relative;
  overflow: visible;
}

.bar-fill {
  height: 100%;
  border-radius: 6px;
  position: relative;
  transition: width 1.5s ease-in-out;
}

.bar-glow {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: 6px;
  filter: blur(4px);
  opacity: 0.6;
}

/* Donut representation */
.donut-container {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto;
}

.donut-center {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.donut-total {
  font-size: 1.8rem;
  font-weight: 700;
}
.donut-label {
  font-size: 0.75rem;
  color: #64748b;
}

.animated-circle {
  transform-origin: center;
  transform: rotate(-90deg);
  transition: stroke-dashoffset 1.5s ease;
}

.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 20px;
}

.legend-item {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 10px; height: 10px; border-radius: 50%;
}
.purple { background: #a855f7; }
.blue { background: #3b82f6; }
.orange { background: #f97316; }

/* Pulse active status */
.pulse-status {
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.status-active::before {
  content: '';
  width: 8px; height: 8px; border-radius: 50%;
  background: #3b82f6;
  box-shadow: 0 0 0 0 rgba(59, 130, 246, 1);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
  100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

.status-done { color: #10b981; }
.status-archive { color: #64748b; }

.glass-table {
  border-radius: 8px;
  overflow: hidden;
}

.glass-table :deep(th), .glass-table :deep(td) {
  background-color: transparent !important;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-table :deep(tr:hover td) {
  background-color: rgba(255, 255, 255, 0.02) !important;
}

.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
</style>
