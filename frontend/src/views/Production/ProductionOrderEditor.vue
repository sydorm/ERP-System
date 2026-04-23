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
          @click="saveOrder('released')" 
          class="erp-btn-primary"
        >
          Передати в роботу →
        </el-button>
        <el-button 
          v-if="['released', 'in_progress'].includes(form.status)"
          type="success" 
          size="small" 
          :loading="submitting" 
          @click="saveOrder('completed')" 
          class="erp-btn-primary"
        >
          Оприбуткувати / Завершити
        </el-button>
        <el-button size="small" @click="saveOrder()" class="erp-btn" :loading="submitting">Записати чернетку</el-button>
        
        <div class="erp-doc-info">
          <span class="erp-doc-title">
            {{ isEditMode ? 'Завдання на виробництво №' + form.order_number : 'Нове завдання на виробництво' }}
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
        <el-step title="Чернетка" />
        <el-step title="В роботі" />
        <el-step title="Готово" />
        <el-step title="Відвантажено" />
      </el-steps>
    </div>

    <div class="production-body">
      <!-- LEFT SIDE: MAIN FORM -->
      <div class="production-main">
        
        <!-- BLOCK: Source -->
        <div class="form-section-card">
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>Джерело</span>
          </div>
          <div class="section-body">
            <div class="source-selector">
              <el-radio-group v-model="form.source_type" @change="onSourceTypeChange">
                <el-radio label="crm">З CRM замовлення</el-radio>
                <el-radio label="quick">Швидке замовлення (вручну)</el-radio>
              </el-radio-group>
              
              <div v-if="form.source_type === 'crm'" class="mt-4 source-link-fields">
                <el-select 
                  v-model="form.source_id" 
                  filterable 
                  placeholder="Оберіть замовлення CRM..." 
                  class="w-full"
                  @change="onSourceOrderChange"
                >
                  <el-option 
                    v-for="o in salesOrders" 
                    :key="o.id" 
                    :label="`Замовлення №${o.order_number} від ${formatDate(o.order_date)}`" 
                    :value="o.id"
                  />
                </el-select>
              </div>
            </div>
            
            <div class="mt-6 client-selection">
              <span class="field-label req">Клієнт (Контрагент):</span>
              <el-select 
                v-model="form.client_id" 
                filterable 
                placeholder="Пошук по контрагентах..." 
                class="w-full mt-1"
                :disabled="form.source_type === 'crm'"
              >
                <el-option v-for="c in counterparties" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- BLOCK: Product -->
        <div class="form-section-card mt-4">
          <div class="section-header">
            <el-icon><Box /></el-icon>
            <span>Виріб та специфікація</span>
          </div>
          <div class="section-body">
            <div class="product-grid">
              <div class="field-block">
                <span class="field-label req">Виріб:</span>
                <el-select 
                  v-model="activeProductId" 
                  filterable 
                  placeholder="Вибрати з номенклатури..." 
                  class="w-full mt-1"
                  @change="onProductSelect"
                >
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </div>
              <div class="field-block">
                <span class="field-label">Характеристики:</span>
                <div class="char-display mt-2">
                  <el-tag v-if="selectedVariantLabel" type="info" size="small">{{ selectedVariantLabel }}</el-tag>
                  <span v-else class="text-xs text-gray-400 italic">підтягуються автоматично</span>
                </div>
              </div>
            </div>

            <div class="product-grid mt-4">
              <div class="field-block">
                <span class="field-label">Специфікація (BOM):</span>
                <el-select 
                  v-model="activeSpecId" 
                  placeholder="Основна" 
                  class="w-full mt-1"
                  @change="recalculateEverything"
                >
                  <el-option 
                    v-for="s in currentSpecs" 
                    :key="s.id" 
                    :label="s.name + (s.is_default ? ' (Авто)' : '')" 
                    :value="s.id" 
                  />
                </el-select>
              </div>
              <div class="field-block" style="max-width: 120px;">
                <span class="field-label req">К-сть:</span>
                <el-input-number 
                  v-model="activeQuantity" 
                  :min="0.001" 
                  class="w-full mt-1" 
                  :controls="false"
                  @change="recalculateEverything"
                />
              </div>
            </div>

            <div class="field-block mt-4">
              <span class="field-label">Коментар до завдання:</span>
              <el-input 
                v-model="form.comment" 
                type="textarea" 
                :rows="2" 
                placeholder="Особливі побажання майстру..." 
                class="mt-1"
              />
            </div>
          </div>
        </div>

        <el-tabs v-model="activeSubTab" class="mt-4 production-tabs">
          <!-- TAB: Production Stages -->
          <el-tab-pane name="stages">
            <template #label>
              <el-icon><Tools /></el-icon>&nbsp;Виробничі етапи
            </template>
            <div class="tab-content-card">
              <el-table :data="form.assignments" border size="small" :empty-text="'Немає даних. Виберіть виріб для автоматичного заповнення етапів.'">
                <el-table-column label="Етап" prop="stage_label" min-width="150">
                  <template #default="scope">
                    <span class="font-medium">{{ scope.row.stage_label }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Майстер" min-width="200">
                  <template #default="scope">
                    <el-select v-model="scope.row.employee_id" filterable size="small" placeholder="Виберіть майстра..." class="w-full">
                      <el-option 
                        v-for="e in getQualifiedEmployees(scope.row.stage_id)" 
                        :key="e.id" 
                        :label="e.full_name" 
                        :value="e.id"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="Час" width="120" align="center">
                  <template #default="scope">
                    <span class="text-gray-600">{{ scope.row.planned_hours || 0 }} год</span>
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
              <el-table :data="form.materials" border size="small" :empty-text="'Немає даних. Виберіть виріб зі специфікацією.'">
                <el-table-column label="Матеріал" prop="component_name" min-width="200" />
                <el-table-column label="Потрібно" width="120" align="right">
                  <template #default="scope">
                    {{ Number(scope.row.required_quantity).toFixed(3) }} {{ scope.row.unit_of_measure }}
                  </template>
                </el-table-column>
                <el-table-column label="На складі" width="120" align="right">
                  <template #default="scope">
                    <span :class="getStockClass(scope.row)">{{ Number(scope.row.stock_qty || 0).toFixed(3) }} {{ scope.row.unit_of_measure }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Статус" width="100" align="center">
                  <template #default="scope">
                    <el-tooltip v-if="Number(scope.row.stock_qty || 0) < Number(scope.row.required_quantity)" content="Треба замовити" placement="top">
                      <el-icon color="#F56C6C" size="18"><CircleCloseFilled /></el-icon>
                    </el-tooltip>
                    <el-icon v-else color="#67C23A" size="18"><SuccessFilled /></el-icon>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- RIGHT SIDE: SUMMARY PANELS -->
      <div class="production-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">Параметри виконання</div>
          <div class="sidebar-body">
            <div class="field-block">
              <span class="field-label">Дедлайн (завершити до):</span>
              <el-date-picker 
                v-model="form.due_date" 
                type="date" 
                placeholder="Оберіть дату..." 
                class="w-full mt-1" 
                format="DD.MM.YYYY"
                value-format="YYYY-MM-DD"
              />
            </div>
            
            <div class="field-block mt-4">
              <span class="field-label">Пріоритет замовлення:</span>
              <el-select v-model="form.priority" class="w-full mt-1">
                <el-option label="Звичайний" value="normal" />
                <el-option label="Терміновий" value="urgent" />
                <el-option label="Критичний" value="critical" />
              </el-select>
            </div>

            <div class="field-block mt-4">
              <span class="field-label">Склад виробництва:</span>
              <el-select v-model="form.warehouse_id" class="w-full mt-1">
                <el-option v-for="wh in warehouses" :key="wh.id" :label="wh.name" :value="wh.id" />
              </el-select>
            </div>
          </div>
        </div>

        <div class="sidebar-card mt-4 summary-box" :class="priorityClass">
          <div class="summary-rows">
            <div class="sum-row">
              <span>Всього часу:</span>
              <span class="val">{{ totalPlannedHours || 0 }} год</span>
            </div>
            <div class="sum-row">
              <span>Матеріали:</span>
              <span v-if="hasMaterialShortage" class="val text-orange-600">⚠️ не всі є</span>
              <span v-else class="val text-green-600">✅ в наявності</span>
            </div>
          </div>
          <div class="sum-divider"></div>
          <div class="priority-indicator">
            Пріоритет: <strong>{{ priorityLabel }}</strong>
          </div>
        </div>

        <div class="sidebar-card mt-4 history-card">
          <div class="sidebar-card-title">Історія подій</div>
          <el-timeline class="mt-4">
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :timestamp="formatDateTime(activity.timestamp)"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Plus, MoreFilled, Printer, CircleClose, 
  Link, Box, Tools, List, SuccessFilled, CircleCloseFilled
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
const counterparties = ref([])
const warehouses = ref([])
const employees = ref([])
const salesOrders = ref([])
const productionStages = ref([])
const currentSpecs = ref([])
const employeeRoles = ref([])

// Form state
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

// UI-helper refs for active product
const activeProductId = ref(null)
const activeVariantId = ref(null)
const activeSpecId = ref(null)
const activeQuantity = ref(1)

const activities = ref([
  { content: 'Завдання створено', timestamp: new Date().toISOString(), type: 'primary' }
])

// --- COMPUTED ---
const statusStepIndex = computed(() => {
  const s = form.status
  if (s === 'draft') return 1
  if (['released', 'in_progress'].includes(s)) return 2
  if (s === 'completed') return 3
  if (s === 'shipped') return 4
  return 0
})

const selectedVariantLabel = computed(() => {
  if (!activeVariantId.value) return null
  const p = products.value.find(x => x.id === activeProductId.value)
  if (!p || !p.variants) return null
  const v = p.variants.find(x => x.id === activeVariantId.value)
  return v ? (v.name || v.sku) : null
})

const totalPlannedHours = computed(() => {
  return form.assignments.reduce((sum, a) => sum + (a.planned_hours || 0), 0)
})

const hasMaterialShortage = computed(() => {
  return form.materials.some(m => Number(m.stock_qty || 0) < Number(m.required_quantity))
})

const priorityLabel = computed(() => {
  const map = { normal: 'Звичайний', urgent: 'Терміновий', critical: 'Критичний' }
  return map[form.priority] || 'Звичайний'
})

const priorityClass = computed(() => {
  return `priority-${form.priority}`
})

// --- METHODS ---
const goBack = () => router.push('/production/orders')

const onSourceTypeChange = () => {
  form.source_id = null
  if (form.source_type === 'quick') form.client_id = null
}

const onSourceOrderChange = (orderId) => {
  const order = salesOrders.value.find(o => o.id === orderId)
  if (order) {
    form.client_id = order.counterparty_id
    if (order.lines && order.lines.length > 0) {
      const line = order.lines[0]
      activeProductId.value = line.product_id
      activeVariantId.value = line.variant_id
      activeQuantity.value = line.quantity
      onProductSelect()
    }
  }
}

const onProductSelect = async () => {
  if (!activeProductId.value) return
  try {
    const res = await api.get(`/api/v1/specifications/product/${activeProductId.value}`)
    currentSpecs.value = res.data
    if (res.data.length > 0) {
      const def = res.data.find(s => s.is_default) || res.data[0]
      activeSpecId.value = def.id
    }
    recalculateEverything()
  } catch (e) {
    ElMessage.error('Помилка завантаження специфікацій')
  }
}

const recalculateEverything = () => {
  if (!activeProductId.value || !activeSpecId.value) return
  
  const spec = currentSpecs.value.find(s => s.id === activeSpecId.value)
  if (!spec) return

  // 1. Line
  form.lines = [{
    product_id: activeProductId.value,
    variant_id: activeVariantId.value,
    specification_id: activeSpecId.value,
    quantity: activeQuantity.value,
    produced_quantity: 0
  }]

  // 2. Materials
  form.materials = (spec.items || []).map(item => ({
    component_id: item.component_id,
    component_name: item.component?.name || 'Компонент',
    required_quantity: (item.quantity || 1) * activeQuantity.value,
    unit_of_measure: item.unit_of_measure || 'шт',
    stock_qty: 0
  }))

  // 3. Stages & Assignments
  const stages = productionStages.value.filter(s => s.is_active)
  form.assignments = stages.map(s => {
    const stageId = s.id
    const assignedEmpId = findBestMaster(stageId)
    return {
      stage_id: stageId,
      stage_label: s.name,
      employee_id: assignedEmpId,
      planned_hours: 1.0
    }
  })
}

const findBestMaster = (stageId) => {
  const qualified = getQualifiedEmployees(stageId)
  if (qualified.length === 1) return qualified[0].id
  
  // Try to find by Main role (using placeholder is_main for now)
  const mainRole = qualified.find(e => {
    const roles = employeeRoles.value.filter(r => r.employee_id === e.id && r.role_id === stageId)
    // Here we should check the ROLE_TYPE dictionary, but for simplicity:
    return roles.length > 0 && roles[0].is_active
  })
  return mainRole ? mainRole.id : null
}

const getQualifiedEmployees = (stageId) => {
  return employees.value.filter(e => {
    return employeeRoles.value.some(r => r.employee_id === e.id && r.role_id === stageId)
  })
}

const getStockClass = (row) => {
  if (Number(row.stock_qty || 0) >= Number(row.required_quantity)) return 'text-green-600 font-bold'
  return 'text-red-600 font-bold'
}

const formatDate = (d) => d ? dayjs(d).format('DD.MM.YYYY') : ''
const formatDateTime = (d) => d ? dayjs(d).format('DD.MM.YYYY HH:mm') : ''

const saveOrder = async (targetStatus) => {
  if (!activeProductId.value) {
    ElMessage.warning('Оберіть виріб для виробництва')
    return
  }
  
  if (targetStatus) form.status = targetStatus
  
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEditMode.value) {
      await api.put(`/api/v1/production/${route.params.id}`, payload)
      ElMessage.success('Завдання збережено')
    } else {
      const res = await api.post('/api/v1/production/', payload)
      ElMessage.success('Завдання створено')
      router.push(`/production/orders/${res.data.id}`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Помилка системи')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  ElMessageBox.confirm('Ви впевнені, що хочете скасувати це завдання?', 'Попередження', {
    confirmButtonText: 'Так, скасувати',
    cancelButtonText: 'Ні',
    type: 'warning'
  }).then(async () => {
    await saveOrder('cancelled')
    ElMessage.info('Завдання скасовано')
  })
}

const handlePrint = () => window.print()

const initData = async () => {
  try {
    const [pRes, cRes, wRes, eRes, sRes, dRes, rolesRes] = await Promise.all([
      api.get('/api/v1/products?limit=1000'),
      api.get('/api/v1/counterparties'),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/employees'),
      api.get('/api/v1/orders?limit=100'),
      api.get('/api/v1/dictionaries/PRODUCTION_STAGE'),
      api.get('/api/v1/employees/roles')
    ])
    products.value = pRes.data
    counterparties.value = cRes.data
    warehouses.value = wRes.data
    employees.value = eRes.data
    salesOrders.value = sRes.data
    productionStages.value = dRes.data?.items || []
    employeeRoles.value = rolesRes.data || []

    if (isEditMode.value) {
      const orderRes = await api.get(`/api/v1/production/${route.params.id}`)
      Object.assign(form, orderRes.data)
      if (form.lines.length > 0) {
        activeProductId.value = form.lines[0].product_id
        activeVariantId.value = form.lines[0].variant_id
        activeSpecId.value = form.lines[0].specification_id
        activeQuantity.value = form.lines[0].quantity
        await onProductSelect()
      }
    } else {
      if (warehouses.value.length > 0) form.warehouse_id = warehouses.value[0].id
      if (products.value.length > 0 && route.query.company_id) form.company_id = route.query.company_id
      
      const qBase = route.query.base_order
      if (qBase) {
        form.source_type = 'crm'
        form.source_id = qBase
        onSourceOrderChange(qBase)
      }
    }
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  }
}

onMounted(initData)
</script>

<style scoped>
.production-body {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
  align-items: start;
  margin-top: 20px;
}

.form-section-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  padding: 10px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
}

.section-body {
  padding: 16px;
}

.product-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.field-block {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.req::after {
  content: '*';
  color: #ef4444;
  margin-left: 2px;
}

.sidebar-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.sidebar-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 8px;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sum-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #4b5563;
}

.sum-row .val {
  font-weight: 600;
  color: #111827;
}

.sum-divider {
  height: 1px;
  background: #f3f4f6;
  margin: 12px 0;
}

.priority-indicator {
  font-size: 13px;
}

/* Pulsating animation for critical priority */
@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.priority-critical {
  border: 2px solid #ef4444 !important;
  animation: pulse-red 2s infinite;
}

.priority-urgent {
  border: 1px solid #f59e0b !important;
}

.priority-normal {
  border: 1px solid #3b82f6 !important;
}

.erp-stepper-container {
  background: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-top: 20px;
}

.tab-content-card {
  background: #fff;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 0 0 8px 8px;
  border-top: none;
}

:deep(.el-steps--simple) {
  padding: 0;
  background: transparent;
}
</style>
