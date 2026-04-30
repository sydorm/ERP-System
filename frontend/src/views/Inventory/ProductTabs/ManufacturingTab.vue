<template>
  <div class="manufacturing-tab-content">
    <el-row :gutter="24">
      <!-- Ліва колонка: Параметри та Обмеження -->
      <el-col :span="14">
        
        <!-- Блок 1: Виробничі параметри -->
        <div class="section-card">
          <div class="section-header">
            <h3><el-icon><Setting /></el-icon> Виробничі параметри</h3>
            <span class="section-subtitle">Базові налаштування техпроцесу</span>
          </div>
          
          <el-form label-position="top" class="compact-form">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="Загальний час (год)">
                  <div class="flex-input-group">
                    <el-input-number 
                      v-model="modelValue.production_time_hours" 
                      :precision="1" 
                      :step="0.5" 
                      :min="0"
                      class="w-full"
                    />
                    <el-tooltip content="Розрахувати час із активної специфікації (BOM)" placement="top">
                      <el-button 
                        type="primary" 
                        plain 
                        :icon="Refresh"
                        @click="calculateTimeFromBom"
                        :loading="calculatingTime"
                      />
                    </el-tooltip>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Складність">
                  <el-select v-model="modelValue.complexity_code" class="w-full" clearable placeholder="Оберіть...">
                    <el-option label="Низька" value="low" />
                    <el-option label="Середня" value="medium" />
                    <el-option label="Висока" value="high" />
                    <el-option label="Експертна" value="expert" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="Мін. партія (шт)">
                  <el-input-number 
                    v-model="modelValue.min_production_batch" 
                    :min="1" 
                    :step="1"
                    class="w-full"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Макс. за день (шт)">
                  <el-input-number 
                    v-model="modelValue.max_production_per_day" 
                    :min="0" 
                    :step="1"
                    class="w-full"
                    placeholder="Без обмежень"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Особливі умови виробництва">
              <el-input 
                v-model="modelValue.special_production_conditions" 
                type="textarea" 
                :rows="3" 
                placeholder="Вкажіть специфічні вимоги, напр. 'Температурний режим 20°C'"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- Блок 2: Обмеження виконавця -->
        <div class="section-card mt-4">
          <div class="section-header">
            <h3><el-icon><UserFilled /></el-icon> Обмеження виконавця</h3>
            <span class="section-subtitle">Хто може виробляти цей товар</span>
          </div>
          
          <el-form label-position="top">
            <el-radio-group v-model="modelValue.performer_restriction_type" class="vertical-radio-group">
              <el-radio value="any_role">Будь-який майстер з відповідною роллю (З BOM)</el-radio>
              
              <div class="radio-with-select">
                <el-radio value="specific_brigade">Конкретна бригада</el-radio>
                <el-select 
                  v-model="modelValue.restricted_brigade_id" 
                  placeholder="Виберіть бригаду..."
                  :disabled="modelValue.performer_restriction_type !== 'specific_brigade'"
                  class="ml-6 w-full max-w-sm"
                  clearable
                >
                  <el-option v-for="b in brigades" :key="b.id" :label="b.name" :value="b.id" />
                </el-select>
              </div>

              <div class="radio-with-select mt-2">
                <el-radio value="specific_master">Конкретний майстер</el-radio>
                <el-select 
                  v-model="modelValue.restricted_employee_id" 
                  placeholder="Виберіть майстра..."
                  :disabled="modelValue.performer_restriction_type !== 'specific_master'"
                  class="ml-6 w-full max-w-sm"
                  clearable
                >
                  <el-option v-for="e in employees" :key="e.id" :label="e.full_name" :value="e.id" />
                </el-select>
              </div>
            </el-radio-group>
          </el-form>
        </div>
      </el-col>

      <!-- Права колонка: Статистика та Завдання -->
      <el-col :span="10">
        
        <!-- Блок 3: Статистика -->
        <div class="section-card stat-card bg-indigo-50 border-indigo-100">
          <div class="section-header mb-4">
            <h3 class="text-indigo-900"><el-icon><TrendCharts /></el-icon> Виробнича статистика</h3>
          </div>
          
          <div v-loading="loadingStats" class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Вироблено всього</span>
              <span class="stat-value text-indigo-700">{{ stats.total_produced || 0 }} <small>шт</small></span>
            </div>
            
            <div class="stat-item">
              <span class="stat-label">Середній час план.</span>
              <span class="stat-value">{{ stats.avg_time_planned || '0.0' }} <small>год</small></span>
            </div>
            
            <div class="stat-item">
              <span class="stat-label">Середній час факт.</span>
              <span class="stat-value">{{ stats.avg_time_actual || '0.0' }} <small>год</small></span>
            </div>
            
            <div class="stat-item">
              <span class="stat-label">Відхилення</span>
              <div class="deviation-box" :class="getDeviationClass(stats.deviation_percent)">
                <span class="dev-val">{{ stats.deviation_hours > 0 ? '+' : '' }}{{ stats.deviation_hours || '0.0' }} год</span>
                <el-tag size="small" :type="getDeviationTagType(stats.deviation_percent)" effect="dark">
                  {{ stats.deviation_percent > 0 ? '+' : '' }}{{ stats.deviation_percent || 0 }}%
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- Блок 4: Активні завдання -->
        <div class="section-card mt-4 tasks-card">
          <div class="section-header mb-3">
            <h3><el-icon><List /></el-icon> Активні завдання</h3>
          </div>
          
          <div v-loading="loadingStats">
            <el-empty v-if="!stats.active_tasks || stats.active_tasks.length === 0" description="Немає активних завдань" :image-size="60" />
            <div v-else class="task-list">
              <div v-for="task in stats.active_tasks" :key="task.id" class="task-item" @click="goToTask(task.id)">
                <div class="task-header">
                  <span class="task-number">{{ task.order_number }}</span>
                  <el-tag size="small" :type="getStatusType(task.status)">{{ getStatusLabel(task.status) }}</el-tag>
                </div>
                <div class="task-details">
                  <span class="task-qty">{{ task.produced_quantity }} / {{ task.quantity }} шт</span>
                  <span class="task-date" v-if="task.due_date"><el-icon><Clock /></el-icon> {{ formatDate(task.due_date) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Setting, UserFilled, TrendCharts, List, Refresh, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: { type: Object, required: true }
})

const router = useRouter()
const brigades = ref([])
const employees = ref([])
const stats = ref({
  total_produced: 0,
  avg_time_planned: 0,
  avg_time_actual: 0,
  deviation_hours: 0,
  deviation_percent: 0,
  active_tasks: []
})
const loadingStats = ref(false)
const calculatingTime = ref(false)

const loadDictionaries = async () => {
  try {
    const [brigadesRes, employeesRes] = await Promise.all([
      api.get('/api/v1/brigades'),
      api.get('/api/v1/employees')
    ])
    brigades.value = brigadesRes.data || []
    employees.value = employeesRes.data || []
  } catch (error) {
    console.error('Failed to load HR dictionaries', error)
  }
}

const loadStats = async () => {
  if (!props.modelValue.id) return
  loadingStats.value = true
  try {
    const res = await api.get(`/api/v1/products/${props.modelValue.id}/production-stats`)
    stats.value = res.data
  } catch (error) {
    console.error('Failed to load production stats', error)
  } finally {
    loadingStats.value = false
  }
}

const calculateTimeFromBom = async () => {
  if (!props.modelValue.id) {
    ElMessage.warning('Спочатку збережіть товар')
    return
  }
  calculatingTime.value = true
  try {
    // We can reuse the calculate-cost endpoint since it calculates stages_cost and duration
    // Actually, calculate-cost returns stages_cost, not raw duration. 
    // We can just fetch the active specification and sum up durations.
    const res = await api.get(`/api/v1/products/${props.modelValue.id}/specifications`)
    const specs = res.data || []
    const defaultSpec = specs.find(s => s.is_default && s.is_active) || specs.find(s => s.is_active)
    
    if (!defaultSpec) {
      ElMessage.warning('Не знайдено активної специфікації')
      return
    }

    const totalHours = (defaultSpec.stages || []).reduce((sum, stage) => sum + (parseFloat(stage.duration_hours) || 0), 0)
    props.modelValue.production_time_hours = totalHours
    ElMessage.success(`Час розраховано: ${totalHours} год`)
  } catch (error) {
    ElMessage.error('Помилка розрахунку часу')
  } finally {
    calculatingTime.value = false
  }
}

const goToTask = (taskId) => {
  router.push(`/production/orders/${taskId}`)
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('DD.MM.YYYY')
}

const getStatusType = (status) => {
  const map = { draft: 'info', released: 'primary', in_progress: 'warning', completed: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { draft: 'Чернетка', released: 'До роботи', in_progress: 'В процесі', completed: 'Готово' }
  return map[status] || status
}

const getDeviationClass = (percent) => {
  if (percent > 10) return 'text-danger'
  if (percent > 0) return 'text-warning'
  if (percent < 0) return 'text-success'
  return 'text-gray'
}

const getDeviationTagType = (percent) => {
  if (percent > 10) return 'danger'
  if (percent > 0) return 'warning'
  if (percent < 0) return 'success'
  return 'info'
}

onMounted(() => {
  loadDictionaries()
  loadStats()
})

watch(() => props.modelValue.performer_restriction_type, (newVal) => {
  if (newVal === 'any_role') {
    props.modelValue.restricted_brigade_id = null
    props.modelValue.restricted_employee_id = null
  } else if (newVal === 'specific_brigade') {
    props.modelValue.restricted_employee_id = null
  } else if (newVal === 'specific_master') {
    props.modelValue.restricted_brigade_id = null
  }
})
</script>

<style scoped>
.manufacturing-tab-content {
  padding: 0;
}

.section-card {
  background: #ffffff;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.section-header {
  margin-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-subtitle {
  font-size: 12px;
  color: #94a3b8;
  display: block;
  margin-top: 4px;
  margin-left: 24px;
}

.flex-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Form Styles */
.compact-form :deep(.el-form-item__label) {
  padding-bottom: 4px;
  font-weight: 500;
  color: #475569;
}

.compact-form :deep(.el-input__wrapper),
.compact-form :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px;
  background-color: #f8fafc;
}

.compact-form :deep(.el-input__wrapper:focus-within),
.compact-form :deep(.el-select__wrapper.is-focused) {
  border-color: #6366f1 !important;
  background-color: #ffffff;
}

/* Radio Group */
.vertical-radio-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  width: 100%;
}

.radio-with-select {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  background: #ffffff;
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid #e0e7ff;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value small {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}

.deviation-box {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.text-danger { color: #ef4444; }
.text-warning { color: #f59e0b; }
.text-success { color: #10b981; }
.text-gray { color: #64748b; }

/* Tasks */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.task-item:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
  transform: translateX(2px);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.task-number {
  font-weight: 600;
  color: #334155;
  font-size: 13px;
}

.task-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
}

.task-date {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
