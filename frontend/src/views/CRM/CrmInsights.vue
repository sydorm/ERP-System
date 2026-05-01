<template>
  <div class="crm-insights-page">
    <!-- Header with Dynamic Glassmorphism -->
    <header class="insights-header">
      <div class="header-content">
        <div class="title-section">
          <span class="kicker">CRM Intelligence 2026</span>
          <h1>Аналітичний центр</h1>
          <p>Повний огляд воронки продажів, фінансів та стратегічних цілей</p>
        </div>
        <div class="header-actions">
          <div class="date-picker-compact">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="—"
              start-placeholder="Початок"
              end-placeholder="Кінець"
              size="large"
              class="premium-date-picker"
            />
          </div>
          <button class="refresh-glow-btn" @click="fetchData">
            <el-icon :class="{ 'is-loading': loading }"><Refresh /></el-icon>
            Оновити дані
          </button>
        </div>
      </div>
    </header>

    <!-- Main Navigation Tabs -->
    <div class="insights-tabs-container">
      <el-tabs v-model="activeTab" class="premium-tabs">
        <!-- TAB 1: FUNNEL & CONVERSION -->
        <el-tab-pane name="funnel">
          <template #label>
            <div class="tab-label">
              <el-icon><Filter /></el-icon>
              <span>Воронка та Конверсія</span>
            </div>
          </template>
          
          <div class="tab-content fade-in">
            <div class="insights-grid">
              <!-- Funnel Visualization -->
              <div class="grid-card funnel-visualization">
                <div class="card-title">
                  <h3>Динамічна воронка</h3>
                  <span class="subtitle">Розподіл угод за етапами</span>
                </div>
                <div class="funnel-container">
                  <div v-for="(stage, idx) in funnelData" :key="stage.key" class="funnel-step" :style="{ '--width': stage.width + '%' }">
                    <div class="step-label">
                      <span class="name">{{ stage.label }}</span>
                      <span class="count">{{ stage.count }} угод</span>
                    </div>
                    <div class="step-bar" :style="{ backgroundColor: stage.color }">
                      <div class="step-value">{{ formatCurrency(stage.total) }} грн</div>
                      <!-- Conversion Indicator -->
                      <div v-if="idx < funnelData.length - 1" class="conversion-badge">
                        <el-icon><Bottom /></el-icon>
                        {{ calculateConversion(stage.count, funnelData[idx+1].count) }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Conversion Insights -->
              <div class="grid-card insights-summary">
                <div class="card-title">
                  <h3>Розумні інсайти</h3>
                </div>
                <div class="insight-items">
                  <div class="insight-item warning">
                    <div class="insight-icon">⚠️</div>
                    <div class="insight-text">
                      <b>Вузьке місце виявлено</b>
                      <p>Конверсія з етапу "КП" до "Договір" впала на 12%. Рекомендуємо переглянути шаблони пропозицій.</p>
                    </div>
                  </div>
                  <div class="insight-item success">
                    <div class="insight-icon">🚀</div>
                    <div class="insight-text">
                      <b>Ріст швидкості</b>
                      <p>Середній час закриття угоди скоротився на 2 дні завдяки автоматизації сповіщень.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- TAB 2: FINANCIAL PERFORMANCE -->
        <el-tab-pane name="finance">
          <template #label>
            <div class="tab-label">
              <el-icon><Money /></el-icon>
              <span>Фінансові KPI</span>
            </div>
          </template>

          <div class="tab-content fade-in">
            <div class="kpi-cards-grid">
              <div class="kpi-glass-card revenue">
                <div class="kpi-icon"><el-icon><TrendCharts /></el-icon></div>
                <div class="kpi-info">
                  <span class="label">Загальна виручка</span>
                  <h2 class="value">{{ formatCurrency(financeData.revenue) }} грн</h2>
                  <div class="trend up">+15.4% <span>vs мин. місяць</span></div>
                </div>
              </div>
              <div class="kpi-glass-card profit">
                <div class="kpi-icon"><el-icon><Wallet /></el-icon></div>
                <div class="kpi-info">
                  <span class="label">Маржинальний прибуток</span>
                  <h2 class="value">{{ formatCurrency(financeData.profit) }} грн</h2>
                  <div class="trend up">+8.2% <span>vs мин. місяць</span></div>
                </div>
              </div>
              <div class="kpi-glass-card aov">
                <div class="kpi-icon"><el-icon><Ticket /></el-icon></div>
                <div class="kpi-info">
                  <span class="label">Середній чек (AOV)</span>
                  <h2 class="value">{{ formatCurrency(financeData.aov) }} грн</h2>
                  <div class="trend down">-2.1% <span>vs мин. місяць</span></div>
                </div>
              </div>
              <div class="kpi-glass-card cac">
                <div class="kpi-icon"><el-icon><UserFilled /></el-icon></div>
                <div class="kpi-info">
                  <span class="label">Вартість ліда (CAC)</span>
                  <h2 class="value">{{ formatCurrency(financeData.cac) }} грн</h2>
                  <div class="trend stable">Стабільно <span>0%</span></div>
                </div>
              </div>
            </div>

            <div class="finance-detailed-grid">
              <div class="grid-card ltv-analysis">
                <h3>LTV Аналіз (Lifetime Value)</h3>
                <div class="ltv-chart-placeholder">
                  <!-- Simulated chart with CSS -->
                  <div class="ltv-bars">
                    <div v-for="i in 6" :key="i" class="ltv-bar" :style="{ height: (40 + Math.random() * 60) + '%' }">
                      <span class="month">М{{ i }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="grid-card payment-status">
                <h3>Статус оплат</h3>
                <div class="payment-pie">
                  <el-progress type="circle" :percentage="85" color="#22C55E">
                    <template #default>
                      <div class="progress-label">
                        <b>85%</b>
                        <span>Оплачено</span>
                      </div>
                    </template>
                  </el-progress>
                  <div class="payment-legend">
                    <div class="legend-item"><span class="dot paid"></span> Оплачено: 4.2M</div>
                    <div class="legend-item"><span class="dot debt"></span> Дебіторка: 0.8M</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- TAB 3: PLANNING & FORECAST -->
        <el-tab-pane name="planning">
          <template #label>
            <div class="tab-label">
              <el-icon><Calendar /></el-icon>
              <span>Планування та Цілі</span>
            </div>
          </template>

          <div class="tab-content fade-in">
            <div class="planning-layout">
              <div class="goals-section">
                <div class="grid-card goal-card">
                  <div class="goal-header">
                    <h3>План продажів на місяць</h3>
                    <span class="target-val">Ціль: 5,000,000 грн</span>
                  </div>
                  <div class="goal-progress-wrap">
                    <div class="progress-meta">
                      <span>Виконано: {{ formatCurrency(3250000) }} грн</span>
                      <span class="perc">65%</span>
                    </div>
                    <el-progress :percentage="65" :stroke-width="24" :color="goalGradient" />
                  </div>
                  <div class="forecast-box">
                    <el-icon><MagicStick /></el-icon>
                    <span>Прогноз до кінця місяця: <b>4,850,000 грн</b> (97%)</span>
                  </div>
                </div>

                <div class="grid-card managers-leaderboard">
                  <h3>Топ перформери</h3>
                  <div class="leaderboard-list">
                    <div v-for="(m, i) in managers" :key="m.name" class="leader-item">
                      <div class="rank">{{ i + 1 }}</div>
                      <div class="m-info">
                        <b>{{ m.name }}</b>
                        <span>{{ m.deals }} угод закрита</span>
                      </div>
                      <div class="m-stats">
                        <div class="m-total">{{ formatCurrency(m.total) }} грн</div>
                        <el-progress :percentage="m.progress" :show-text="false" size="small" :color="m.color" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  Refresh, Filter, Money, Calendar, 
  TrendCharts, Wallet, Ticket, UserFilled,
  Bottom, MagicStick 
} from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('funnel')
const loading = ref(false)
const dateRange = ref([])

const goalGradient = [
  { color: '#1463FF', percentage: 0 },
  { color: '#00D1FF', percentage: 100 }
]

const funnelData = ref([
  { key: 'leads', label: 'Ліди / Вхідні', count: 1200, total: 15400000, width: 100, color: '#1463FF' },
  { key: 'contact', label: 'Контакт / Кваліфікація', count: 850, total: 11200000, width: 85, color: '#00D1FF' },
  { key: 'proposal', label: 'КП / Пропозиція', count: 420, total: 6800000, width: 65, color: '#8B5CF6' },
  { key: 'contract', label: 'Договір / Рахунок', count: 210, total: 4100000, width: 45, color: '#F59E0B' },
  { key: 'closed', label: 'Закрита угода', count: 145, total: 3250000, width: 30, color: '#22C55E' }
])

const financeData = reactive({
  revenue: 3250000,
  profit: 1420000,
  aov: 22400,
  cac: 450
})

const managers = ref([
  { name: 'Олександр Вернигора', deals: 42, total: 1250000, progress: 85, color: '#1463FF' },
  { name: 'Марія Ковальчук', deals: 38, total: 980000, progress: 78, color: '#00D1FF' },
  { name: 'Дмитро Сорока', deals: 31, total: 720000, progress: 62, color: '#8B5CF6' }
])

const calculateConversion = (top, bottom) => {
  if (!top) return 0
  return ((bottom / top) * 100).toFixed(1)
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat('uk-UA').format(val)
}

const fetchData = async () => {
  loading.value = true
  // In a real app, we would fetch from API
  setTimeout(() => {
    loading.value = false
  }, 800)
}

onMounted(() => {
  // Set default range to current month
  const end = new Date()
  const start = new Date()
  start.setMonth(start.getMonth() - 1)
  dateRange.value = [start, end]
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.crm-insights-page {
  font-family: 'Inter', sans-serif;
  background: #F1F5F9;
  min-height: 100vh;
  padding-bottom: 50px;
}

/* Header */
.insights-header {
  background: #fff;
  padding: 40px 48px;
  border-bottom: 1px solid #E2E8F0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.kicker {
  color: #1463FF;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: 8px;
}

.title-section h1 {
  font-size: 32px;
  font-weight: 900;
  color: #0F172A;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.title-section p {
  color: #64748B;
  font-size: 16px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.refresh-glow-btn {
  height: 48px;
  padding: 0 24px;
  border-radius: 14px;
  border: none;
  background: #1463FF;
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(20, 99, 255, 0.2);
  transition: all 0.3s;
}

.refresh-glow-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(20, 99, 255, 0.3);
  background: #0047D1;
}

/* Tabs */
.insights-tabs-container {
  max-width: 1600px;
  margin: 32px auto;
  padding: 0 48px;
}

:deep(.premium-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.premium-tabs .el-tabs__header) {
  margin-bottom: 32px;
}

:deep(.premium-tabs .el-tabs__item) {
  height: auto;
  padding: 12px 24px;
  border-radius: 16px;
  transition: all 0.3s;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  font-size: 15px;
}

.tab-label .el-icon {
  font-size: 20px;
}

/* Grid & Cards */
.insights-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.grid-card {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #0F172A;
}

.card-title .subtitle {
  font-size: 14px;
  color: #64748B;
}

/* Funnel Visual */
.funnel-container {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.funnel-step {
  width: var(--width);
  margin: 0 auto;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  padding: 0 10px;
}

.step-label .name { font-size: 13px; font-weight: 700; color: #475569; }
.step-label .count { font-size: 12px; font-weight: 800; color: #94A3B8; }

.step-bar {
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.05);
}

.step-value {
  color: #fff;
  font-weight: 800;
  font-size: 14px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.conversion-badge {
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border: 1px solid #E2E8F0;
  padding: 2px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 800;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 2;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* Insight Items */
.insight-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.insight-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
}

.insight-item.warning { background: #FFF7ED; border: 1px solid #FFEDD5; }
.insight-item.success { background: #F0FDF4; border: 1px solid #DCFCE7; }

.insight-icon { font-size: 24px; }
.insight-text b { display: block; font-size: 15px; color: #0F172A; margin-bottom: 4px; }
.insight-text p { margin: 0; font-size: 13px; color: #475569; line-height: 1.5; }

/* KPI Cards */
.kpi-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.kpi-glass-card {
  background: #fff;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid #E2E8F0;
  display: flex;
  gap: 20px;
  align-items: center;
  transition: transform 0.3s;
}

.kpi-glass-card:hover {
  transform: translateY(-5px);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 24px;
}

.revenue .kpi-icon { background: #EEF2FF; color: #1463FF; }
.profit .kpi-icon { background: #F0FDF4; color: #22C55E; }
.aov .kpi-icon { background: #FAF5FF; color: #8B5CF6; }
.cac .kpi-icon { background: #FFF7ED; color: #F59E0B; }

.kpi-info .label { font-size: 13px; font-weight: 700; color: #64748B; display: block; margin-bottom: 4px; }
.kpi-info h2 { margin: 0 0 6px 0; font-size: 22px; font-weight: 900; color: #0F172A; }

.trend { font-size: 12px; font-weight: 800; display: flex; align-items: center; gap: 4px; }
.trend.up { color: #22C55E; }
.trend.down { color: #EF4444; }
.trend.stable { color: #64748B; }
.trend span { color: #94A3B8; font-weight: 500; margin-left: 4px; }

/* Planning */
.goal-progress-wrap {
  margin: 24px 0;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: 700;
  font-size: 14px;
}

.forecast-box {
  background: #F8FAFC;
  padding: 16px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #475569;
  font-size: 14px;
}

.forecast-box b { color: #1463FF; }

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.leader-item {
  display: grid;
  grid-template-columns: 40px 1fr 140px;
  align-items: center;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 16px;
  gap: 12px;
}

.rank { font-weight: 900; color: #94A3B8; font-size: 16px; }
.m-info b { display: block; font-size: 14px; color: #0F172A; }
.m-info span { font-size: 12px; color: #64748B; }
.m-total { text-align: right; font-weight: 800; font-size: 14px; color: #0F172A; margin-bottom: 4px; }

/* Animations */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.is-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
