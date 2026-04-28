<template>
  <div class="erp-light-container">
    <!-- Custom Scrollbar styles injected for layout criteria -->
    <component :is="'style'">
      ::-webkit-scrollbar { width: 4px; height: 4px; }
      ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6C63FF, #00C9A7); border-radius: 2px; }
      ::-webkit-scrollbar-track { background: transparent; }
    </component>

    <!-- Stats Dashboard -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="4" v-for="(card, index) in metricCards" :key="index">
        <div class="metric-card" :style="{ '--card-accent': card.color }">
          <div class="metric-card__label">{{ card.label }}</div>
          <span class="metric-card__trend" :class="card.trendUp ? 'metric-card__trend--up' : 'metric-card__trend--down'">
            {{ card.trendUp ? '↑' : '↓' }} {{ card.trend }}
          </span>
          <div class="metric-card__value dm-mono">{{ card.value }}</div>
          <div class="metric-card__sparkline">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <path :d="card.sparkline" fill="none" :stroke="card.color" stroke-width="2" />
            </svg>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content: Managers & Funnel -->
    <el-row :gutter="20" class="mt-4">
      <el-col :xs="24" :md="14">
        <div class="table-container">
          <h3 class="section-title">Ефективність менеджерів</h3>
          <el-table v-loading="loading" :data="managers" style="width: 100%" class="light-premium-table">
            <el-table-column prop="name" label="Менеджер" min-width="150">
              <template #default="scope">
                <span class="warehouse-name">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="orders_count" label="Замовлень" width="120" align="center">
              <template #default="scope">
                <span class="dm-mono">{{ scope.row.orders_count }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="Сума" width="180" align="right">
              <template #default="scope">
                <span class="total-amount dm-mono">{{ formatCurrency(scope.row.total_amount) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <el-col :xs="24" :md="10">
        <div class="table-container">
          <h3 class="section-title">Воронка продажів</h3>
          <el-table v-loading="loading" :data="funnel" style="width: 100%" class="light-premium-table">
            <el-table-column prop="stage" label="Етап" min-width="120">
              <template #default="scope">
                <el-tag size="small" :type="getStageTagType(scope.row.stage)" effect="plain">
                  {{ mapStageName(scope.row.stage) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="К-ть" width="100" align="center">
              <template #default="scope">
                <span class="dm-mono">{{ scope.row.count }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total" label="Сума" width="150" align="right">
              <template #default="scope">
                <span class="dm-mono">{{ formatCurrency(scope.row.total) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- Activity Feed -->
    <el-row class="mt-4">
      <el-col :span="24">
        <div class="table-container">
          <h3 class="section-title">Стрічка активності</h3>
          <el-table v-loading="loading" :data="activity" style="width: 100%" class="light-premium-table">
            <el-table-column prop="created_at" label="Час" width="180">
              <template #default="scope">
                <span class="dm-mono">{{ formatTime(scope.row.created_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="user" label="Користувач" width="200">
              <template #default="scope">
                <span class="warehouse-name">{{ scope.row.user }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="action" label="Дія" min-width="300" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const stats = ref({})
const managers = ref([])
const funnel = ref([])
const activity = ref([])
let refreshInterval = null

const metricCards = computed(() => {
  const s = stats.value
  return [
    { 
      label: 'ПРОДАЖІ', 
      value: formatCurrency(s.total_sales || 0), 
      trend: '+12%', 
      trendUp: true, 
      color: '#3B82F6',
      sparkline: 'M0 25 Q 25 5, 50 20 T 100 10'
    },
    { 
      label: 'ЗАМОВЛЕННЯ', 
      value: `${s.orders_count || 0} шт`, 
      trend: '+5%', 
      trendUp: true, 
      color: '#22C55E',
      sparkline: 'M0 15 Q 20 25, 40 5 T 80 20 T 100 5'
    },
    { 
      label: 'ВИРОБНИЦТВО', 
      value: `${s.active_production || 0} активних`, 
      trend: '-2%', 
      trendUp: false, 
      color: '#F59E0B',
      sparkline: 'M0 20 L 30 10 L 60 18 L 100 5'
    },
    { 
      label: 'ЗАКУПІВЛІ', 
      value: formatCurrency(s.total_purchases || 0), 
      trend: '+8%', 
      trendUp: true, 
      color: '#EF4444',
      sparkline: 'M0 20 Q 30 5, 60 25 T 100 15'
    },
    { 
      label: 'КЛІЄНТИ', 
      value: `${s.clients_count || 0}`, 
      trend: '+3%', 
      trendUp: true, 
      color: '#6C63FF',
      sparkline: 'M0 25 Q 25 15, 50 25 T 100 5'
    },
    { 
      label: 'ЗАДАЧІ CRM', 
      value: `${s.active_tasks || 0}`, 
      trend: '-10%', 
      trendUp: true, 
      color: '#00C9A7',
      sparkline: 'M0 5 Q 25 25, 50 5 T 100 25'
    }
  ]
})

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, managersRes, funnelRes, activityRes] = await Promise.all([
      api.get('/api/v1/dashboard/stats'),
      api.get('/api/v1/dashboard/managers'),
      api.get('/api/v1/dashboard/funnel'),
      api.get('/api/v1/dashboard/activity')
    ])
    
    stats.value = statsRes.data
    managers.value = managersRes.data
    funnel.value = funnelRes.data
    activity.value = activityRes.data
  } catch (e) {
    console.error(e)
    ElMessage.error('Помилка завантаження даних дашборду')
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency',
    currency: 'UAH',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

const formatTime = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const mapStageName = (stage) => {
  const maps = {
    'new': 'Нові',
    'payment': 'Оплата',
    'processing': 'Обробка',
    'production': 'Виробництво',
    'done': 'Завершено',
    'cancelled': 'Скасовано'
  }
  return maps[stage] || stage
}

const getStageTagType = (stage) => {
  const maps = {
    'new': 'info',
    'payment': 'warning',
    'processing': 'primary',
    'production': 'success',
    'done': 'success',
    'cancelled': 'danger'
  }
  return maps[stage] || 'info'
}

onMounted(() => {
  fetchData()
  refreshInterval = setInterval(fetchData, 60000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

.erp-light-container {
  padding: 25px;
  background-color: #F7F8FC;
  min-height: calc(100vh - 60px);
  color: #1E293B;
  font-family: 'Inter', sans-serif;
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.dm-mono {
  font-family: 'DM Mono', monospace;
}

.section-title {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 15px;
}

.table-container {
  background: #FFFFFF;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

/* Stats Dashboard */
.metric-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #F3F4F6;
  padding: 16px 20px;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

.metric-card__label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #9CA3AF;
  margin-bottom: 8px;
}

.metric-card__value {
  font-size: 22px;
  font-weight: 700;
  color: #18181B;
}

.metric-card__trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  font-weight: 600;
}

.metric-card__trend--up   { color: #22C55E; }
.metric-card__trend--down { color: #EF4444; }

.metric-card__sparkline {
  margin-top: 12px;
  height: 30px;
}

.metric-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--card-accent);
}

/* Table Styles */
.light-premium-table {
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.warehouse-name {
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: #0F172A;
}

.total-amount {
  color: #0F172A;
  font-weight: 600;
}
</style>
