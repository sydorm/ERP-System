<template>
  <div class="erp-dark-container">
    <!-- Background glowing orbs -->
    <div class="glow-orb glow-orb-1"></div>
    <div class="glow-orb glow-orb-2"></div>

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
          class="dark-search-input mr-4"
          style="width: 250px;"
        />
        <el-button type="primary" :icon="Plus" @click="openCreateDialog" class="neon-btn">
          Додати Склад
        </el-button>
      </div>
    </div>

    <!-- Quick Actions Bar -->
    <div class="quick-actions-grid mt-4">
      <el-button class="glass-action-btn" :icon="Download" @click="quickProcurement">
        Прихід товару
      </el-button>
      <el-button class="glass-action-btn" :icon="DocumentDelete" @click="quickWriteOff">
        Списання
      </el-button>
      <el-button class="glass-action-btn" :icon="Switch" @click="quickTransfer">
        Переміщення
      </el-button>
    </div>

    <!-- Stats Dashboard -->
    <el-row :gutter="20" class="stats-row mt-4">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="glass-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Всього складів</span>
            <span class="metric-ai-opt">+2% AI Opt</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ warehouses.length }}</span>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="glass-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Загальний запас</span>
            <span class="metric-ai-opt live-sync">Live Sync</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ totalStockQty }} шт</span>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="glass-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Оцінка капіталу</span>
            <span class="metric-ai-opt">₴72.8k</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">{{ formatCurrency(totalStockValue) }}</span>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="glass-metric-card">
          <div class="metric-meta">
            <span class="metric-title">Ефективність місця</span>
            <span class="metric-ai-opt efficiency">84% Load</span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value">A+</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content: Warehouse Expandable Grid -->
    <div class="mt-6 list-container">
      <el-table v-loading="loading" :data="filteredWarehouses" style="width: 100%" class="dark-premium-table">
        <el-table-column type="expand">
          <template #default="props">
            <div class="expand-content">
              <div class="expand-header">
                <h4>Товарні залишки на складі: <strong>{{ props.row.name }}</strong></h4>
                <span class="financial-valuation">Вартість активів: <strong>{{ formatCurrency(getWarehouseStockValue(props.row.id)) }}</strong></span>
              </div>

              <el-table :data="getWarehouseStock(props.row.id)" size="small" class="dark-inner-table mt-3">
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
              <el-tag v-if="scope.row.is_default" type="primary" size="small" class="default-tag" effect="dark">
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
              <el-button type="primary" :icon="Edit" circle size="small" class="glass-icon-btn" @click="openEditDialog(scope.row)" />
              <el-button type="danger" :icon="Delete" circle size="small" class="glass-icon-btn" :disabled="scope.row.is_default" @click="confirmDelete(scope.row)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Bottom AI Storage Optimization Widget -->
    <div class="glass-card ai-reshuffle-card mt-6">
      <div class="ai-header">
        <div class="ai-icon-glow">⚡</div>
        <h3 class="ai-title">AI Storage Re-shuffling</h3>
      </div>
      <div class="ai-body mt-3">
        <p class="ai-desc">
          Наша інтелектуальна система аналізує частоту завантажень. Ми пропонуємо перемістити найбільш ходові товари ближче до зони відвантаження, що дозволить скоротити час обробки.
        </p>
        
        <el-row :gutter="24" class="mt-4 ai-stats-row">
          <el-col :span="12">
            <div class="ai-stat-box">
              <span class="ai-stat-lbl">TIME SAVED</span>
              <span class="ai-stat-val green">42 хв/день</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="ai-stat-box">
              <span class="ai-stat-lbl">ENERGY EFFICIENCY</span>
              <span class="ai-stat-val blue">98.2%</span>
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

        <el-button type="primary" class="ai-activate-btn mt-4">
          Активувати Оптимізацію
        </el-button>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="dark-premium-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="small">
        <el-form-item label="Назва складу" prop="name">
          <el-input v-model="form.name" placeholder="Напр. Центральний Хаб А1" />
        </el-form-item>

        <el-form-item label="Адреса">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="Вкажіть адресу" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_default" label="Зробити цей склад основним" class="dark-checkbox" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_active" label="Активний" class="dark-checkbox" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="small" class="glass-cancel-btn">Скасувати</el-button>
          <el-button type="primary" :loading="submitting" @click="saveWarehouse" size="small" class="neon-btn">Зберегти</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, Box, Location, List, InfoFilled, Money, Search, Download, DocumentDelete, Switch } from '@element-plus/icons-vue'
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
.erp-dark-container {
  padding: 30px;
  background-color: #090d16;
  min-height: 100vh;
  color: #e2e8f0;
  position: relative;
  overflow: hidden;
}

/* Glowing dynamic backgrounds */
.glow-orb {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(130px);
  opacity: 0.1;
  pointer-events: none;
  z-index: 0;
}
.glow-orb-1 {
  background: #3b82f6;
  top: -10%;
  right: -5%;
}
.glow-orb-2 {
  background: #a855f7;
  bottom: -10%;
  left: -5%;
}

.erp-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

/* Dark search input overrides */
.dark-search-input :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
}
.dark-search-input :deep(.el-input__inner) {
  color: white !important;
}
.dark-search-input :deep(.el-input__inner::placeholder) {
  color: #64748b;
}

/* Action buttons */
.neon-btn {
  background: linear-gradient(135deg, #a855f7, #6366f1) !important;
  border: none !important;
  color: white !important;
  font-weight: 600;
  border-radius: 8px;
  transition: transform 0.2s ease;
}
.neon-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
}

.quick-actions-grid {
  display: flex;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.glass-action-btn {
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #94a3b8 !important;
  border-radius: 8px;
}
.glass-action-btn:hover {
  color: white !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  background: rgba(255, 255, 255, 0.07) !important;
}

/* Stats Metric Cards */
.glass-metric-card {
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 120px;
  transition: all 0.3s ease;
}
.glass-metric-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.5);
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
}
.metric-ai-opt {
  font-size: 0.75rem;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}
.metric-ai-opt.live-sync {
  color: #a855f7;
  background: rgba(168, 85, 247, 0.1);
}
.metric-ai-opt.efficiency {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-top: 12px;
}

/* Table overrides for dark theme */
.list-container {
  position: relative;
  z-index: 1;
}
.dark-premium-table {
  background-color: rgba(17, 24, 39, 0.6) !important;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}
.dark-premium-table :deep(th), .dark-premium-table :deep(td) {
  background-color: transparent !important;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.dark-premium-table :deep(tr:hover td) {
  background-color: rgba(255, 255, 255, 0.02) !important;
}

.warehouse-name {
  font-weight: 600;
  font-size: 1rem;
}

.default-tag {
  background: rgba(59, 130, 246, 0.2) !important;
  color: #60a5fa !important;
  border: 1px solid rgba(59, 130, 246, 0.3) !important;
  border-radius: 4px;
  text-transform: uppercase;
  font-size: 0.65rem;
}

.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-dot.active { background: #10b981; }
.status-dot.inactive { background: #f43f5e; }

.glass-icon-btn {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #cbd5e1 !important;
}
.glass-icon-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.expand-content {
  background: rgba(15, 23, 42, 0.6);
  padding: 20px;
  border-radius: 8px;
  margin: 10px;
}

.dark-inner-table {
  background-color: transparent !important;
}
.dark-inner-table :deep(th) {
  background-color: rgba(255, 255, 255, 0.02) !important;
  color: #94a3b8 !important;
}
.dark-inner-table :deep(td) {
  background-color: transparent !important;
  color: #e2e8f0;
}

.product-link {
  color: #60a5fa;
  text-decoration: none;
}
.product-link:hover {
  text-decoration: underline;
}

/* AI Card Widget */
.ai-reshuffle-card {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.4));
  border-left: 4px solid #6366f1 !important;
  position: relative;
  z-index: 1;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon-glow {
  font-size: 1.5rem;
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.8);
}

.ai-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.ai-desc {
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.6;
}

.ai-stats-row {
  margin-top: 16px;
}

.ai-stat-box {
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.ai-stat-lbl {
  font-size: 0.7rem;
  color: #64748b;
  letter-spacing: 1px;
}

.ai-stat-val {
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 4px;
}
.ai-stat-val.green { color: #10b981; }
.ai-stat-val.blue { color: #3b82f6; }

.simulation-monitor {
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}

.sim-title {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0 0 10px 0;
  letter-spacing: 1px;
}

.sim-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-bottom: 6px;
}

.sim-dot {
  width: 6px; height: 6px; border-radius: 50%;
}
.sim-dot.success {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.sim-res {
  margin-left: auto;
  color: #10b981;
  font-weight: 600;
  font-size: 0.75rem;
}

.ai-activate-btn {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  width: 100%;
  font-weight: 600;
}
.ai-activate-btn:hover {
  background: rgba(99, 102, 241, 0.2) !important;
  border-color: #6366f1 !important;
}

/* Dialog overrides */
.dark-premium-dialog :deep(.el-dialog) {
  background: #0f172a !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}
.dark-premium-dialog :deep(.el-dialog__title) {
  color: white !important;
}
.dark-premium-dialog :deep(.el-form-item__label) {
  color: #94a3b8 !important;
}

.dark-checkbox :deep(.el-checkbox__label) {
  color: #cbd5e1 !important;
}

.glass-cancel-btn {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #94a3b8 !important;
}
.glass-cancel-btn:hover {
  color: white !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.mr-4 { margin-right: 16px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
</style>
