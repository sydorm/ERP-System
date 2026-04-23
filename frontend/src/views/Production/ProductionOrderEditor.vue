<template>
  <div class="erp-page-container">
    <!-- TOOLBAR (CRM Style) -->
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button 
          v-if="form.status === 'draft'"
          type="warning" 
          size="small" 
          :loading="submitting" 
          @click="saveOrder('in_progress')" 
          class="erp-btn-primary"
        >
          Запустити у виробництво →
        </el-button>
        <el-button 
          v-if="form.status === 'in_progress'"
          type="success" 
          size="small" 
          :loading="submitting" 
          @click="saveOrder('completed')" 
          class="erp-btn-primary"
          :disabled="!allStagesCompleted"
        >
          Прийняти на склад / Готово
        </el-button>
        <el-button size="small" @click="saveOrder()" class="erp-btn" :loading="submitting">Зберегти зміни</el-button>
        
        <div class="erp-doc-info">
          <span class="erp-doc-title">
            {{ isEditMode ? 'Виробниче завдання №' + form.order_number : 'Нове завдання на виробництво' }}
          </span>
        </div>
      </div>
      <div class="erp-toolbar-right">
        <el-dropdown trigger="click" size="small">
          <el-button size="small" class="erp-btn-icon" :icon="MoreFilled" title="Більше дій" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handlePrint"><el-icon><Printer /></el-icon> Друк завдання</el-dropdown-item>
              <el-dropdown-item v-if="isEditMode" @click="handleCancel" class="text-red-600"><el-icon><CircleClose /></el-icon> Скасувати завдання</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- STATUS STEPPER -->
    <div class="erp-stepper-container">
      <el-steps :active="statusStepIndex" finish-status="success" simple>
        <el-step title="Заплановано" />
        <el-step title="В роботі" />
        <el-step title="Готово" />
        <el-step title="Передано" />
      </el-steps>
    </div>

    <div class="production-body">
      <!-- LEFT SIDE: MAIN CARD WITH TABS -->
      <div class="production-main">
        
        <div class="form-section-card info-summary-bar">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="summary-item">
                <span class="label">Замовлення:</span>
                <span class="value">{{ form.source_id ? '№' + form.order_number : 'Вручну' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-item">
                <span class="label">Виріб:</span>
                <span class="value">{{ activeProductName }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-item">
                <span class="label">Пріоритет:</span>
                <el-tag :type="getPriorityType(form.priority)" size="small" effect="dark">{{ priorityLabel }}</el-tag>
              </div>
            </el-col>
          </el-row>
        </div>

        <el-tabs v-model="activeSubTab" class="mt-4 production-tabs custom-tabs-card">
          <!-- TAB: Production Stages -->
          <el-tab-pane name="stages">
            <template #label>
              <el-badge :value="pendingStagesCount" :hidden="pendingStagesCount === 0" type="warning">
                <el-icon><Tools /></el-icon>&nbsp;Етапи
              </el-badge>
            </template>
            <div class="tab-content-card">
              <el-table :data="form.assignments" border size="default" :row-class-name="getStageRowClass">
                <el-table-column label="Етап" min-width="150">
                  <template #default="scope">
                    <div class="stage-cell">
                      <el-icon v-if="scope.row.status === 'completed'" color="#67C23A"><SuccessFilled /></el-icon>
                      <el-icon v-else-if="isCurrentStage(scope.$index)" color="#E6A23C" class="is-loading"><Loading /></el-icon>
                      <el-icon v-else color="#909399"><Clock /></el-icon>
                      <span class="ml-2 font-bold">{{ scope.row.stage_label || scope.row.stage?.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                
                <el-table-column label="Майстер" min-width="180">
                  <template #default="scope">
                    <el-select 
                      v-model="scope.row.employee_id" 
                      filterable 
                      size="small" 
                      placeholder="Призначити..." 
                      class="w-full"
                      :disabled="scope.row.status === 'completed'"
                    >
                      <el-option 
                        v-for="e in getQualifiedEmployees(scope.row.stage_id)" 
                        :key="e.id" 
                        :label="e.full_name" 
                        :value="e.id"
                      />
                    </el-select>
                  </template>
                </el-table-column>

                <el-table-column label="Час" width="100" align="center">
                  <template #default="scope">
                    <span class="text-gray-600">{{ scope.row.planned_hours || 0 }} год</span>
                  </template>
                </el-table-column>

                <el-table-column label="Статус" width="130" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.status === 'completed'" type="success" effect="plain" size="small">✅ Готово</el-tag>
                    <el-tag v-else-if="isCurrentStage(scope.$index)" type="warning" effect="dark" size="small">🟡 В роботі</el-tag>
                    <el-tag v-else type="info" effect="plain" size="small">⏳ Очікує</el-tag>
                  </template>
                </el-table-column>

                <el-table-column label="Дії" width="120" align="center">
                  <template #default="scope">
                    <el-button 
                      v-if="scope.row.status !== 'completed' && isCurrentStage(scope.$index)"
                      type="success" 
                      size="small" 
                      @click="completeStage(scope.$index)"
                    >
                      Закрити
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- TAB: Materials -->
          <el-tab-pane name="materials">
            <template #label>
              <el-icon><List /></el-icon>&nbsp;Матеріали
            </template>
            <div class="tab-content-card">
              <el-table :data="form.materials" border size="default">
                <el-table-column label="Матеріал" prop="component_name" min-width="200" />
                <el-table-column label="Потрібно" width="120" align="right">
                  <template #default="scope">
                    {{ Number(scope.row.required_quantity).toFixed(2) }} {{ scope.row.unit_of_measure }}
                  </template>
                </el-table-column>
                <el-table-column label="На складі" width="120" align="right">
                  <template #default="scope">
                    <span :class="getStockClass(scope.row)">{{ Number(scope.row.stock_qty || 0).toFixed(2) }} {{ scope.row.unit_of_measure }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Статус" width="120" align="center">
                  <template #default="scope">
                    <el-tag v-if="parseFloat(scope.row.stock_qty || 0) >= parseFloat(scope.row.required_quantity)" type="success" size="small">✅ є</el-tag>
                    <el-tag v-else-if="parseFloat(scope.row.stock_qty || 0) > 0" type="warning" size="small">🟡 мало</el-tag>
                    <el-tag v-else type="danger" size="small">🔴 немає</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- TAB: History -->
          <el-tab-pane name="history">
            <template #label>
              <el-icon><Calendar /></el-icon>&nbsp;Історія
            </template>
            <div class="tab-content-card p-6">
              <el-timeline>
                <el-timeline-item
                  v-for="(activity, index) in activities"
                  :key="index"
                  :timestamp="formatDateTime(activity.timestamp)"
                  :type="activity.type"
                  :color="activity.color"
                >
                  <div class="history-content">
                    <strong>{{ activity.content }}</strong>
                    <p v-if="activity.user" class="text-xs text-gray-500">Виконавець: {{ activity.user }}</p>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- Basic Info (Hidden in tabs but available for creation) -->
        <div v-if="!isEditMode || activeSubTab === 'stages'" class="form-section-card mt-4">
          <div class="section-header">
            <el-icon><InfoFilled /></el-icon>
            <span>Основні дані</span>
          </div>
          <div class="section-body">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="field-block">
                  <span class="field-label">Джерело:</span>
                  <el-radio-group v-model="form.source_type" @change="onSourceTypeChange" :disabled="isEditMode">
                    <el-radio label="crm">Замовлення CRM</el-radio>
                    <el-radio label="quick">Швидке (вручну)</el-radio>
                  </el-radio-group>
                </div>
              </el-col>
              <el-col :span="12" v-if="form.source_type === 'crm'">
                <div class="field-block">
                  <el-select v-model="form.source_id" placeholder="Оберіть замовлення CRM..." class="w-full" @change="onSourceOrderChange" :disabled="isEditMode">
                    <el-option v-for="o in salesOrders" :key="o.id" :label="'№' + o.order_number" :value="o.id" />
                  </el-select>
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="20" class="mt-4">
               <el-col :span="12">
                  <span class="field-label req">Виріб:</span>
                  <el-select v-model="activeProductId" filterable placeholder="Вибрати виріб..." class="w-full mt-1" @change="onProductSelect" :disabled="isEditMode">
                    <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
               </el-col>
               <el-col :span="6">
                  <span class="field-label req">К-сть:</span>
                  <el-input-number v-model="activeQuantity" :min="1" class="w-full mt-1" @change="recalculateEverything" :disabled="isEditMode" />
               </el-col>
               <el-col :span="6">
                  <span class="field-label">Пріоритет:</span>
                  <el-select v-model="form.priority" class="w-full mt-1">
                    <el-option label="Звичайний" value="normal" />
                    <el-option label="Терміновий" value="urgent" />
                    <el-option label="Критичний" value="critical" />
                  </el-select>
               </el-col>
            </el-row>
            <div class="mt-4">
              <span class="field-label">Коментар до завдання:</span>
              <el-input v-model="form.comment" type="textarea" :rows="2" class="mt-1" placeholder="Замітка для майстрів..." />
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDE: SUMMARY & ACTIONS -->
      <div class="production-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">Виконання</div>
          <div class="sidebar-body">
            <div class="field-block">
              <span class="field-label">Дедлайн:</span>
              <el-date-picker 
                v-model="form.due_date" 
                type="date" 
                class="w-full mt-1" 
                format="DD.MM.YYYY"
                value-format="YYYY-MM-DD"
              />
            </div>
            
            <div class="field-block mt-4">
              <span class="field-label text-xs uppercase text-gray-400">Прогрес:</span>
              <el-progress :percentage="totalProgress" :status="totalProgress === 100 ? 'success' : ''" class="mt-2" />
            </div>
          </div>
        </div>

        <div class="sidebar-card mt-4 summary-box" :class="priorityClass">
          <div class="summary-rows">
            <div class="sum-row">
               <span>Загальний час:</span>
               <span class="val">{{ totalPlannedHours }} год</span>
            </div>
            <div class="sum-row">
               <span>Виконано:</span>
               <span class="val">{{ completedHours }} год</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Plus, MoreFilled, Printer, CircleClose, Loading,
  Tools, List, Calendar, InfoFilled, Clock, SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const isEditMode = computed(() => !!route.params.id)
const submitting = ref(false)
const activeSubTab = ref('stages')

// --- DATA ---
const products = ref([])
const warehouses = ref([])
const employees = ref([])
const salesOrders = ref([])
const productionStages = ref([])
const currentSpecs = ref([])
const employeeRoles = ref([])

const form = reactive({
  order_number: 'Авто',
  order_date: new Date().toISOString(),
  due_date: null,
  status: 'draft',
  source_type: 'quick',
  source_id: null,
  client_id: null,
  priority: 'normal',
  company_id: null,
  warehouse_id: null,
  comment: '',
  lines: [],
  materials: [],
  assignments: []
})

const activeProductId = ref(null)
const activeQuantity = ref(1)
const activeSpecId = ref(null)
const activities = ref([])

// --- COMPUTED ---
const activeProductName = computed(() => {
  const p = products.value.find(x => x.id === activeProductId.value)
  return p ? p.name : 'Виріб не обрано'
})

const statusStepIndex = computed(() => {
  const map = { draft: 1, in_progress: 2, completed: 3, shipped: 4 }
  return map[form.status] || 0
})

const pendingStagesCount = computed(() => {
  return form.assignments.filter(a => a.status !== 'completed').length
})

const allStagesCompleted = computed(() => {
  return form.assignments.length > 0 && pendingStagesCount.value === 0
})

const totalProgress = computed(() => {
  if (form.assignments.length === 0) return 0
  const done = form.assignments.filter(a => a.status === 'completed').length
  return Math.round((done / form.assignments.length) * 100)
})

const totalPlannedHours = computed(() => form.assignments.reduce((sum, a) => sum + (a.planned_hours || 0), 0))
const completedHours = computed(() => form.assignments.filter(a => a.status === 'completed').reduce((sum, a) => sum + (a.planned_hours || 0), 0))

const priorityLabel = computed(() => ({ normal: 'Звичайний', urgent: 'Терміновий', critical: 'Критичний' }[form.priority]))
const priorityClass = computed(() => `priority-${form.priority}`)

// --- METHODS ---
const goBack = () => router.push('/production/orders')

const isCurrentStage = (index) => {
  if (form.status !== 'in_progress') return false
  const firstPendingIndex = form.assignments.findIndex(a => a.status !== 'completed')
  return index === firstPendingIndex
}

const getStageRowClass = ({ row, rowIndex }) => {
  if (row.status === 'completed') return 'stage-completed'
  if (isCurrentStage(rowIndex)) return 'stage-active'
  return ''
}

const completeStage = async (index) => {
  const stage = form.assignments[index]
  stage.status = 'completed'
  
  activities.value.unshift({
    content: `Етап "${stage.stage_label || stage.stage?.name}" закрито`,
    timestamp: new Date().toISOString(),
    type: 'success',
    user: employees.value.find(e => e.id === stage.employee_id)?.full_name || 'Невідомий'
  })

  // Auto-activate next stage info message
  if (index < form.assignments.length - 1) {
    ElMessage.success(`Етап закрито. Наступний: ${form.assignments[index+1].stage_label || form.assignments[index+1].stage?.name}`)
  } else {
    ElMessage.success('Всі етапи завершено! Можна закривати завдання.')
  }
  
  // Save changes locally and potentially to server
  if (isEditMode.value) await saveOrder()
}

const onSourceTypeChange = () => {
  form.source_id = null
  form.client_id = null
}

const onSourceOrderChange = (orderId) => {
  const order = salesOrders.value.find(o => o.id === orderId)
  if (order && order.lines?.length > 0) {
    activeProductId.value = order.lines[0].product_id
    activeQuantity.value = order.lines[0].quantity
    onProductSelect()
  }
}

const onProductSelect = async () => {
  if (!activeProductId.value) return
  try {
    const res = await api.get(`/api/v1/products/${activeProductId.value}/specifications`)
    currentSpecs.value = res.data
    activeSpecId.value = res.data.find(s => s.is_default)?.id || res.data[0]?.id
    recalculateEverything()
  } catch (e) { ElMessage.error('Помилка завантаження специфікацій') }
}

const recalculateEverything = () => {
  if (!activeProductId.value) return
  
  const spec = currentSpecs.value.find(s => s.id === activeSpecId.value)
  
  form.lines = [{ 
    product_id: activeProductId.value, 
    quantity: activeQuantity.value, 
    specification_id: activeSpecId.value 
  }]
  
  if (spec) {
    // 1. Recalculate Materials
    form.materials = (spec.items || []).map(item => ({
      component_id: item.component_id,
      component_name: item.component?.name || 'Матеріал',
      required_quantity: item.quantity * activeQuantity.value,
      unit_of_measure: item.unit_of_measure,
      stock_qty: 0
    }))

    // 2. Recalculate Production Stages (v2 integration)
    if (spec.stages && spec.stages.length > 0) {
      form.assignments = spec.stages.map(s => ({
        stage_id: s.stage_id,
        stage_label: s.stage?.name || 'Етап',
        employee_id: findBestMaster(s.role_id || s.stage_id),
        planned_hours: parseFloat(s.duration_hours || 0) * activeQuantity.value,
        status: 'pending'
      }))
    } else {
      // Fallback: Generate generic stages if BOM has no stages defined
      const stages = productionStages.value.slice(0, 4)
      form.assignments = stages.map(s => ({
        stage_id: s.id,
        stage_label: s.name,
        employee_id: findBestMaster(s.id),
        planned_hours: 1.0 * activeQuantity.value,
        status: 'pending'
      }))
    }
  }
}

const findBestMaster = (stageId) => {
  const qualified = employees.value.filter(e => employeeRoles.value.some(r => r.employee_id === e.id && r.role_id === stageId))
  return qualified.length > 0 ? qualified[0].id : null
}

const getQualifiedEmployees = (stageId) => employees.value.filter(e => employeeRoles.value.some(r => r.employee_id === e.id && r.role_id === stageId))

const getStockClass = (row) => parseFloat(row.stock_qty || 0) >= parseFloat(row.required_quantity) ? 'text-green-600' : 'text-red-600'

const saveOrder = async (targetStatus) => {
  if (targetStatus) form.status = targetStatus
  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/production/${route.params.id}`, form)
      ElMessage.success('Збережено')
    } else {
      const res = await api.post('/api/v1/production/', form)
      ElMessage.success('Коментар: Завдання створено')
      router.push(`/production/orders/${res.data.id}`)
    }
  } catch (e) { ElMessage.error('Помилка збереження') }
  finally { submitting.value = false }
}

const handleCancel = () => ElMessageBox.confirm('Скасувати завдання?', 'Увага', { type: 'warning' }).then(() => saveOrder('cancelled'))
const handlePrint = () => window.print()
const formatDateTime = (d) => d ? dayjs(d).format('DD.MM HH:mm') : ''

const initData = async () => {
  try {
    const [pRes, wRes, eRes, sRes, dRes, rolesRes] = await Promise.all([
      api.get('/api/v1/products'), api.get('/api/v1/warehouses'),
      api.get('/api/v1/employees'), api.get('/api/v1/orders'),
      api.get('/api/v1/dictionaries/PRODUCTION_STAGE'), api.get('/api/v1/employees/roles')
    ])
    products.value = pRes.data; warehouses.value = wRes.data; employees.value = eRes.data;
    salesOrders.value = sRes.data; productionStages.value = dRes.data?.items || [];
    employeeRoles.value = rolesRes.data || []

    if (isEditMode.value) {
      const res = await api.get(`/api/v1/production/${route.params.id}`)
      Object.assign(form, res.data)
      activeProductId.value = form.lines[0]?.product_id
      activeQuantity.value = form.lines[0]?.quantity
      activities.value = [{ content: 'Завдання створено', timestamp: form.created_at, type: 'info' }]
    }
  } catch (e) { ElMessage.error('Помилка завантаження') }
}

onMounted(initData)
</script>

<style scoped>
.production-body { display: grid; grid-template-columns: 1fr 300px; gap: 20px; margin-top: 20px; }
.form-section-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.info-summary-bar { padding: 15px 20px; border-bottom: 2px solid #409EFF; }
.summary-item .label { font-size: 11px; color: #909399; text-transform: uppercase; display: block; }
.summary-item .value { font-weight: 700; color: #303133; font-size: 16px; }

.section-header { padding: 10px 16px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.section-body { padding: 16px; }

.tab-content-card { background: #fff; padding: 0; border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px; border-top: none; }

.stage-cell { display: flex; align-items: center; }
.stage-active { background-color: #fdf6ec !important; }
.stage-completed { opacity: 0.7; background-color: #f0f9eb !important; }

.sidebar-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
.sidebar-card-title { font-size: 14px; font-weight: 600; margin-bottom: 12px; border-bottom: 1px solid #f3f4f6; padding-bottom: 8px; }

.priority-critical { border: 2px solid #ef4444 !important; animation: pulse-red 2s infinite; }
@keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }

.field-label { font-size: 12px; color: #6b7280; font-weight: 500; }
.req::after { content: '*'; color: #ef4444; }

.custom-tabs-card :deep(.el-tabs__header) { margin-bottom: 0; }
.history-content p { margin: 4px 0 0 0; }
</style>
