<template>
  <div class="reports-container">
    <!-- Summary Header -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :span="8">
        <el-card shadow="hover" class="card-accrued">
          <template #header>
            <div class="card-header">
              <span>Всього нараховано</span>
              <el-icon><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(totalAccrued) }} ₴</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="card-paid">
          <template #header>
            <div class="card-header">
              <span>Всього виплачено</span>
              <el-icon><Wallet /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(totalPaid) }} ₴</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="card-balance" :class="{ 'negative': overallBalance > 0 }">
          <template #header>
            <div class="card-header">
              <span>Загальний борг</span>
              <el-icon><Money /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overallBalance) }} ₴</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-row :gutter="20" class="mt-4">
      <!-- Period summary (Simple Bar Chart Substitute) -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Динаміка по місяцях</span>
              <el-select v-model="selectedYear" size="small" style="width: 100px">
                <el-option label="2024" value="2024" />
                <el-option label="2023" value="2023" />
              </el-select>
            </div>
          </template>
          
          <div class="period-chart">
            <div v-for="item in summaryData" :key="item.period" class="chart-row">
              <div class="row-label">{{ item.period }}</div>
              <div class="row-bars">
                <div class="bar-accrued" :style="{ width: getBarWidth(item.total_accrued) + '%' }">
                  <span v-if="getBarWidth(item.total_accrued) > 15">{{ formatCurrency(item.total_accrued) }}</span>
                </div>
                <div class="bar-paid" :style="{ width: getBarWidth(item.total_paid) + '%' }">
                  <span v-if="getBarWidth(item.total_paid) > 15">{{ formatCurrency(item.total_paid) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><i class="dot accrued"></i> Нараховано</span>
            <span class="legend-item"><i class="dot paid"></i> Виплачено</span>
          </div>
        </el-card>
      </el-col>

      <!-- Department Distribution -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Витрати по підрозділах</span>
            </div>
          </template>
          <el-table :data="deptData" stripe style="width: 100%">
            <el-table-column prop="department_name" label="Підрозділ" />
            <el-table-column label="Нараховано" align="right">
              <template #default="{ row }">
                {{ formatCurrency(row.total_accrued) }}
              </template>
            </el-table-column>
            <el-table-column label="Доля" align="right">
              <template #default="{ row }">
                <el-progress 
                  :percentage="getDeptPercentage(row.total_accrued)" 
                  :stroke-width="15"
                  striped
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { TrendCharts, Wallet, Money } from '@element-plus/icons-vue'

const summaryData = ref([])
const deptData = ref([])
const selectedYear = ref('2024')
const loading = ref(false)

const totalAccrued = computed(() => {
  return summaryData.value.reduce((sum, item) => sum + Number(item.total_accrued || 0), 0)
})

const totalPaid = computed(() => {
  return summaryData.value.reduce((sum, item) => sum + Number(item.total_paid || 0), 0)
})

const overallBalance = computed(() => {
  return totalAccrued.value - totalPaid.value
})

const maxAmount = computed(() => {
  const allValues = summaryData.value.flatMap(i => [Number(i.total_accrued), Number(i.total_paid)])
  return Math.max(...allValues, 1)
})

const getBarWidth = (val) => {
  return (Number(val) / maxAmount.value) * 100
}

const getDeptPercentage = (val) => {
  if (totalAccrued.value === 0) return 0
  return Math.round((Number(val) / totalAccrued.value) * 100)
}

const fetchReports = async () => {
  loading.value = true
  try {
    const [summaryRes, deptRes] = await Promise.all([
      api.get('/api/v1/reports/summary'),
      api.get('/api/v1/reports/by-department')
    ])
    summaryData.value = summaryRes.data
    deptData.value = deptRes.data
  } catch (error) {
    console.error('Failed to fetch reports:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchReports()
})

const formatCurrency = (val) => {
  return new Number(val || 0).toLocaleString('uk-UA', { minimumFractionDigits: 2 })
}
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.summary-cards .el-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  margin-top: 5px;
}

.card-accrued { border-left: 5px solid #409EFF; }
.card-paid { border-left: 5px solid #67C23A; }
.card-balance { border-left: 5px solid #909399; }
.card-balance.negative { border-left-color: #F56C6C; }

.mt-4 { margin-top: 20px; }

.period-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.chart-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.row-label {
  width: 80px;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
}

.row-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-accrued, .bar-paid {
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 11px;
  color: white;
  min-width: 2px;
  transition: width 0.5s ease;
}

.bar-accrued { background: linear-gradient(90deg, #409EFF, #79bbff); }
.bar-paid { background: linear-gradient(90deg, #67C23A, #95d475); }

.chart-legend {
  margin-top: 20px;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.accrued { background-color: #409EFF; }
.dot.paid { background-color: #67C23A; }
</style>
