<template>
  <div class="erp-light-container">
    <!-- Toolbar -->
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <h2 class="page-title">Керування Складами</h2>
      </div>
      <div class="erp-toolbar-right">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук складу..."
          :prefix-icon="Search"
          clearable
          class="light-search-input mr-4"
          style="width: 250px;"
        />
        <el-button type="primary" :icon="Plus" @click="openCreateDialog" class="action-primary-btn">
          Додати Склад
        </el-button>
      </div>
    </div>

    <!-- Quick Actions Bar -->
    <div class="quick-actions-grid mt-4">
      <el-button class="soft-action-btn" :icon="Download" @click="quickProcurement" type="primary" plain>
        Прихід товару
      </el-button>
      <el-button class="soft-action-btn" :icon="DocumentDelete" @click="quickWriteOff" type="danger" plain>
        Списання
      </el-button>
      <el-button class="soft-action-btn" :icon="Switch" @click="quickTransfer" type="info" plain>
        Переміщення
      </el-button>
    </div>

    <!-- Stats Dashboard -->
    <el-row :gutter="20" class="stats-row mt-4">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="premium-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Всього складів</span>
            <span class="metric-badge blue">+2% AI Opt</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ warehouses.length }}</span>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="premium-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Загальний запас</span>
            <span class="metric-badge purple">Live Sync</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ totalStockQty }} шт</span>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="premium-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Оцінка капіталу</span>
            <span class="metric-badge green">Ціна закупівлі</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ formatCurrency(totalStockValue) }}</span>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="premium-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Ефективність місця</span>
            <span class="metric-badge orange">84% Load</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">A+</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content: Warehouse Expandable Grid -->
    <div class="mt-6 list-container">
      <el-table v-loading="loading" :data="filteredWarehouses" style="width: 100%" class="light-premium-table">
        <el-table-column type="expand">
          <template #default="props">
            <div class="expand-content">
              <div class="expand-header">
                <h4>Товарні залишки на складі: <strong>{{ props.row.name }}</strong></h4>
                <span class="financial-valuation">Вартість активів: <strong>{{ formatCurrency(getWarehouseStockValue(props.row.id)) }}</strong></span>
              </div>

              <el-table :data="getWarehouseStock(props.row.id)" size="small" class="light-inner-table mt-3" stripe border>
                <el-table-column label="Товар" min-width="220">
                  <template #default="scope">
                    <router-link :to="'/inventory/nomenclature/' + scope.row.product_id" class="product-link" v-if="scope.row.product_id">
                      {{ scope.row.product_name }}
                    </router-link>
                    <span v-else>{{ scope.row.product_name }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Характеристика" prop="variant_label" min-width="150">
                  <template #default="scope">
                    <span v-if="scope.row.variant_label">{{ scope.row.variant_label }}</span>
                    <span class="empty-text" v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="Собівартість" width="130" align="right">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.cost) }}
                  </template>
                </el-table-column>
                <el-table-column label="Кількість" prop="quantity" width="120" align="right">
                  <template #default="scope">
                    <span class="stock-qty">{{ scope.row.quantity }} шт</span>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="140" align="right">
                  <template #default="scope">
                    <span class="total-amount">{{ formatCurrency(scope.row.quantity * scope.row.cost) }}</span>
                  </template>
                </el-table-column>
              </el-table>
              
              <div v-if="!getWarehouseStock(props.row.id).length" class="empty-stock-state">
                <span>На цьому складі немає товарів.</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Назва" prop="name" min-width="250">
          <template #default="scope">
            <div class="warehouse-name-cell">
              <span class="warehouse-name">{{ scope.row.name }}</span>
              <el-tag v-if="scope.row.is_default" type="primary" size="small" class="default-tag" effect="plain">
                основний
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Адреса" prop="address" min-width="250">
          <template #default="scope">
            <span>{{ scope.row.address || '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" prop="is_active" width="150" align="center">
          <template #default="scope">
            <span class="status-dot" :class="scope.row.is_active ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ scope.row.is_active ? 'Активний' : 'Заповнений' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="150" align="center">
          <template #default="scope">
            <div class="actions-cell">
              <el-button type="primary" :icon="Edit" circle size="small" @click="openEditDialog(scope.row)" />
              <el-button type="danger" :icon="Delete" circle size="small" :disabled="scope.row.is_default" @click="confirmDelete(scope.row)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Bottom AI Storage Optimization Widget -->
    <div class="premium-ai-card mt-6">
      <div class="ai-header">
        <el-icon class="ai-icon" color="#6366f1"><MagicStick /></el-icon>
        <h3 class="ai-title">AI Storage Re-shuffling</h3>
      </div>
      <div class="ai-body mt-3">
        <p class="ai-desc">
          Наша інтелектуальна система аналізує частоту завантажень. Ми пропонуємо перемістити найбільш ходові товари ближче до зони відвантаження, що дозволить скоротити час обробки.
        </p>
        
        <el-row :gutter="24" class="mt-4 ai-stats-row">
          <el-col :span="12">
            <div class="ai-stat-box blue">
              <span class="ai-stat-lbl">TIME SAVED</span>
              <span class="ai-stat-val">42 хв/день</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="ai-stat-box purple">
              <span class="ai-stat-lbl">ENERGY EFFICIENCY</span>
              <span class="ai-stat-val">98.2%</span>
            </div>
          </el-col>
        </el-row>

        <div class="simulation-monitor mt-4">
          <h5 class="sim-title">SIMULATION MONITOR</h5>
          <div class="sim-row">
            <span class="sim-dot success"></span>
            <span class="sim-txt">Розрахунок вектору руху WH-01...</span>
            <span class="sim-res">SUCCESS</span>
          </div>
          <div class="sim-row">
            <span class="sim-dot success"></span>
            <span class="sim-txt">Аналіз оптимізації вантажопотоку...</span>
            <span class="sim-res">SUCCESS</span>
          </div>
        </div>

        <el-button type="primary" class="ai-activate-btn mt-4" disabled>
          Активувати Оптимізацію
        </el-button>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="light-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="small">
        <el-form-item label="Назва складу" prop="name">
          <el-input v-model="form.name" placeholder="Напр. Центральний Хаб А1" />
        </el-form-item>

        <el-form-item label="Адреса">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="Вкажіть адресу складу" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_default" label="Зробити цей склад основним" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_active" label="Активний для використання" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="small">Скасувати</el-button>
          <el-button type="primary" :loading="submitting" @click="saveWarehouse" size="small">Зберегти</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, Search, Download, DocumentDelete, Switch, MagicStick } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const submitting = ref(false)
const warehouses = ref([])
const allStock = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('Створити склад')
const formRef = ref(null)

const form = ref({
  id: null,
  name: '',
  address: '',
  is_default: false,
  is_active: true
})

const filteredWarehouses = computed(() => {
  if (!searchQuery.value) return warehouses.value
  const query = searchQuery.value.toLowerCase()
  return warehouses.value.filter(w => 
    w.name.toLowerCase().includes(query) || 
    (w.address && w.address.toLowerCase().includes(query))
  )
})

const quickProcurement = () => {
  router.push('/purchases/receipts/new')
}

const quickWriteOff = () => {
  ElMessage.info('Модуль списання запасів знаходиться в розробці')
}

const quickTransfer = () => {
  ElMessage.info('Модуль переміщення між складами знаходиться в розробці')
}

const rules = {
  name: [
    { required: true, message: 'Введіть назву складу', trigger: 'blur' }
  ]
}

const defaultWarehouseName = computed(() => {
  const def = warehouses.value.find(w => w.is_default)
  return def ? def.name : ''
})

const totalStockQty = computed(() => {
  return allStock.value.reduce((sum, item) => sum + item.quantity, 0)
})

const totalStockValue = computed(() => {
  return allStock.value.reduce((sum, item) => sum + (item.quantity * item.cost), 0)
})

const fetchData = async () => {
  loading.value = true
  try {
    const whRes = await api.get('/api/v1/warehouses')
    warehouses.value = whRes.data

    const stockRes = await api.get('/api/v1/warehouses/stock')
    allStock.value = stockRes.data
  } catch (e) {
    console.error(e)
    ElMessage.error('Помилка завантаження даних складів')
  } finally {
    loading.value = false
  }
}

const getWarehouseStock = (warehouseId) => {
  return allStock.value.filter(item => item.warehouse_id === warehouseId)
}

const getWarehouseStockValue = (warehouseId) => {
  return getWarehouseStock(warehouseId).reduce((sum, item) => sum + (item.quantity * item.cost), 0)
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency',
    currency: 'UAH',
    minimumFractionDigits: 2
  }).format(value || 0)
}

const openCreateDialog = () => {
  dialogTitle.value = 'Створити склад'
  form.value = {
    id: null,
    name: '',
    address: '',
    is_default: false,
    is_active: true
  }
  dialogVisible.value = true
  if (formRef.value) formRef.value.clearValidate()
}

const openEditDialog = (row) => {
  dialogTitle.value = 'Редагувати склад'
  form.value = { ...row }
  dialogVisible.value = true
  if (formRef.value) formRef.value.clearValidate()
}

const saveWarehouse = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const payload = {
        name: form.value.name,
        address: form.value.address || '',
        is_default: form.value.is_default,
        is_active: form.value.is_active
      }

      if (form.value.id) {
        await api.put(`/api/v1/warehouses/${form.value.id}`, payload)
        ElMessage.success('Дані складу успішно оновлено')
      } else {
        await api.post('/api/v1/warehouses', payload)
        ElMessage.success('Склад успішно створено')
      }
      
      dialogVisible.value = false
      await fetchData()
    } catch (e) {
      console.error(e)
      ElMessage.error(e.response?.data?.detail || 'Помилка при збереженні складу')
    } finally {
      submitting.value = false
    }
  })
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `Ви дійсно бажаєте видалити склад "${row.name}"? Це можливо лише якщо на ньому немає залишків.`,
    'Видалення складу',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/warehouses/${row.id}`)
      ElMessage.success('Склад успішно видалено')
      await fetchData()
    } catch (e) {
      console.error(e)
      ElMessage.error(e.response?.data?.detail || 'Помилка видалення складу')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.erp-light-container {
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 64px);
  color: #1e293b;
}

.erp-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.light-search-input :deep(.el-input__wrapper) {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px;
}

.action-primary-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
  border: none !important;
  border-radius: 8px;
  font-weight: 600;
}
.action-primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.quick-actions-grid {
  display: flex;
  gap: 12px;
}

.soft-action-btn {
  border-radius: 8px;
  font-weight: 500;
}

/* Stats Metric Cards (Light Mode) */
.premium-metric-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 110px;
  box-shadow: 0 1px 3px 0 rgba(0,0,0,0.02);
  transition: all 0.2s ease;
}
.premium-metric-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateY(-2px);
}

.metric-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-title {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.metric-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.metric-badge.blue { color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
.metric-badge.purple { color: #8b5cf6; background: rgba(139, 92, 246, 0.1); }
.metric-badge.green { color: #10b981; background: rgba(16, 185, 129, 0.1); }
.metric-badge.orange { color: #f59e0b; background: rgba(245, 158, 11, 0.1); }

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 10px;
}

/* Main table adjustments */
.light-premium-table {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  box-shadow: 0 1px 3px 0 rgba(0,0,0,0.02);
}

.warehouse-name {
  font-weight: 600;
  color: #0f172a;
}

.default-tag {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-left: 8px;
  border-radius: 4px;
}

.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-dot.active { background: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.4); }
.status-dot.inactive { background: #f43f5e; }

.status-text {
  font-size: 0.85rem;
  color: #334155;
}

.expand-content {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  margin: 5px;
  border: 1px solid #edf2f7;
}

.expand-header h4 {
  margin: 0;
  color: #334155;
}
.financial-valuation {
  font-size: 0.85rem;
  color: #64748b;
}

.light-inner-table {
  border-radius: 6px;
  overflow: hidden;
}

.product-link {
  color: #4f46e5;
  font-weight: 500;
  text-decoration: none;
}
.product-link:hover {
  text-decoration: underline;
}

.empty-stock-state {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-style: italic;
}

/* Premium AI Widget */
.premium-ai-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-icon {
  font-size: 1.4rem;
}
.ai-title {
  margin: 0;
  font-size: 1.2rem;
  color: #0f172a;
}

.ai-desc {
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.6;
}

.ai-stat-box {
  padding: 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}
.ai-stat-box.blue { background: #eff6ff; border-left: 4px solid #3b82f6; }
.ai-stat-box.purple { background: #faf5ff; border-left: 4px solid #8b5cf6; }

.ai-stat-lbl {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 1px;
}
.ai-stat-val {
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 4px;
}
.ai-stat-box.blue .ai-stat-val { color: #1d4ed8; }
.ai-stat-box.purple .ai-stat-val { color: #6d28d9; }

.simulation-monitor {
  background: #f8fafc;
  border: 1px solid #edf2f7;
  padding: 16px;
  border-radius: 12px;
}

.sim-title {
  margin: 0 0 10px 0;
  font-size: 0.75rem;
  color: #64748b;
  letter-spacing: 0.5px;
}

.sim-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #334155;
  margin-bottom: 8px;
}

.sim-dot.success {
  width: 6px; height: 6px; border-radius: 50%;
  background: #10b981;
}

.sim-res {
  margin-left: auto;
  color: #059669;
  font-weight: 600;
}

.ai-activate-btn {
  width: 100%;
  border-radius: 8px;
  background: #f1f5f9 !important;
  border: 1px solid #cbd5e1 !important;
  color: #64748b !important;
}

.mr-4 { margin-right: 16px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
</style>
