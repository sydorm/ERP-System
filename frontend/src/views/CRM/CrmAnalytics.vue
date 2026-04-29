<template>
  <div class="crm-analytics-container">
    <div class="analytics-header">
      <div class="crm-title-row">
        <h1 class="page-title">Аналітика CRM</h1>
      </div>
      <div class="header-right">
        <div class="crm-view-switch">
          <button class="view-btn" @click="router.push('/crm')">Kanban</button>
          <button class="view-btn active">Аналітика</button>
        </div>
        <el-button type="primary" plain @click="fetchData" style="margin-left: 16px;">
          <el-icon><Refresh /></el-icon> Оновити
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 1. FUNNEL -->
      <el-col :span="12">
        <el-card class="analytics-card funnel-card">
          <template #header>
            <div class="card-header">
              <span>Воронка продажів</span>
            </div>
          </template>
          <div class="funnel-body">
            <div 
              v-for="item in analytics.funnel" 
              :key="item.stage" 
              class="funnel-row"
            >
              <div class="funnel-label">{{ getStageLabel(item.stage) }}</div>
              <div class="funnel-bar-container">
                <div 
                  class="funnel-bar" 
                  :style="{ 
                    width: getBarWidth(item.count) + '%',
                    backgroundColor: getStageColor(item.stage) 
                  }"
                >
                  <span class="bar-count">{{ item.count }}</span>
                </div>
              </div>
              <div class="funnel-total">{{ formatCurrency(item.total) }} грн</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 2. CONVERSION -->
      <el-col :span="12">
        <el-card class="analytics-card conversion-card">
          <template #header>
            <div class="card-header">
              <span>Конверсія між етапами</span>
            </div>
          </template>
          <div class="conversion-body">
            <div 
              v-for="(conv, index) in analytics.conversion" 
              :key="index" 
              class="conversion-row"
            >
              <div class="conv-from">{{ getStageLabel(conv.from) }}</div>
              <div class="conv-arrow">
                <el-icon><Right /></el-icon>
                <span class="conv-percent" :style="{ color: getConversionColor(conv.percent) }">
                  {{ conv.percent }}%
                </span>
              </div>
              <div class="conv-to">{{ getStageLabel(conv.to) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 3. TOP MANAGERS -->
      <el-col :span="12">
        <el-card class="analytics-card managers-card">
          <template #header>
            <div class="card-header">
              <span>Топ-5 менеджерів (Закриті угоди)</span>
            </div>
          </template>
          <el-table :data="analytics.top_managers" style="width: 100%" size="default">
            <el-table-column label="#" width="60">
              <template #default="scope">
                <span v-if="scope.$index === 0" class="medal">🥇</span>
                <span v-else>{{ scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="Менеджер" />
            <el-table-column prop="count" label="Угод" width="80" align="center" />
            <el-table-column label="Сума" align="right">
              <template #default="scope">
                <strong>{{ formatCurrency(scope.row.total) }}</strong>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 4. AVG TIME -->
      <el-col :span="12">
        <el-card class="analytics-card time-card">
          <template #header>
            <div class="card-header">
              <span>Середній час у статусі (днів)</span>
            </div>
          </template>
          <div class="time-body">
            <div 
              v-for="item in analytics.avg_stage_days" 
              :key="item.stage" 
              class="time-row"
            >
              <div class="time-label">{{ getStageLabel(item.stage) }}</div>
              <div class="time-bar-container">
                <div 
                  class="time-bar" 
                  :style="{ 
                    width: (item.days * 10) + '%',
                    backgroundColor: getStageColor(item.stage)
                  }"
                >
                  <span class="bar-days">{{ item.days }}д</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { Refresh, Right } from '@element-plus/icons-vue'

const router = useRouter()

const analytics = ref({
  funnel: [],
  conversion: [],
  top_managers: [],
  avg_stage_days: []
})

const stages = [
  { key: 'new',        label: 'Нові',        color: '#3D3AA8' },
  { key: 'payment',    label: 'Оплата',     color: '#F97316' },
  { key: 'processing', label: 'В роботі',    color: '#F59E0B' },
  { key: 'production', label: 'Виробництво', color: '#8B5CF6' },
  { key: 'done',       label: 'Виконані',    color: '#22C55E' }
]

const getStageLabel = (key) => stages.find(s => s.key === key)?.label || key
const getStageColor = (key) => stages.find(s => s.key === key)?.color || '#94a3b8'

const fetchData = async () => {
  try {
    const res = await api.get('/api/v1/crm/analytics')
    analytics.value = res.data
  } catch (e) {
    console.error('Failed to fetch analytics', e)
  }
}

const getBarWidth = (count) => {
  const max = Math.max(...analytics.value.funnel.map(i => i.count), 1)
  return Math.max((count / max) * 100, 5)
}

const getConversionColor = (percent) => {
  if (percent < 30) return '#ef4444' // red
  if (percent < 60) return '#f59e0b' // yellow
  return '#22c55e' // green
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)

onMounted(fetchData)
</script>

<style scoped>
.crm-analytics-container {
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 64px);
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.crm-view-switch { background: #e2e8f0; padding: 2px; border-radius: 8px; display: flex; }
.view-btn { padding: 4px 10px; border: none; background: transparent; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: #64748b; }
.view-btn.active { background: #fff; color: #1e293b; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

.analytics-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 600;
  font-size: 16px;
  color: #334155;
}

/* Funnel Styles */
.funnel-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.funnel-row {
  display: grid;
  grid-template-columns: 120px 1fr 120px;
  align-items: center;
  gap: 16px;
}
.funnel-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}
.funnel-bar-container {
  height: 32px;
  background: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
}
.funnel-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  transition: width 0.6s ease;
}
.bar-count {
  color: white;
  font-weight: 700;
  font-size: 12px;
}
.funnel-total {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  text-align: right;
}

/* Conversion Styles */
.conversion-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.conversion-row {
  display: grid;
  grid-template-columns: 1fr 120px 1fr;
  align-items: center;
  text-align: center;
  padding: 8px;
  background: #f1f5f9;
  border-radius: 8px;
}
.conv-from, .conv-to {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}
.conv-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-weight: 700;
}
.conv-percent {
  font-size: 12px;
}

/* Time Styles */
.time-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.time-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 16px;
}
.time-label {
  font-size: 14px;
  color: #64748b;
}
.time-bar-container {
  height: 24px;
  background: #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}
.time-bar {
  height: 100%;
  display: flex;
  align-items: center;
  padding-left: 12px;
  transition: width 0.6s ease;
}
.bar-days {
  color: white;
  font-weight: 700;
  font-size: 11px;
}

.medal {
  font-size: 20px;
}
</style>
