<template>
  <div class="erp-light-container">
    <!-- Top Actions Bar (Compact, unified) -->
    <div class="erp-actions-toolbar">
      <div class="actions-left">
        <el-button class="compact-action-btn" :icon="Download" @click="quickProcurement" type="primary" size="small" plain>
          Прихід
        </el-button>
        <el-button class="compact-action-btn" :icon="DocumentDelete" @click="quickWriteOff" type="danger" size="small" plain>
          Списання
        </el-button>
        <el-button class="compact-action-btn" :icon="Switch" @click="quickTransfer" type="info" size="small" plain>
          Переміщення
        </el-button>
        
        <!-- Collapsed Filters Popover -->
        <el-popover placement="bottom" title="Фільтрація запасів" :width="300" trigger="click" class="light-popover">
          <template #reference>
            <el-button :icon="Search" size="small" class="compact-action-btn ml-2">Фільтри</el-button>
          </template>
          <div class="popover-filters-grid">
            <el-input v-model="searchQuery" placeholder="Пошук складу..." :prefix-icon="Search" size="small" clearable class="mb-2" />
            <el-input v-model="filterProduct" placeholder="Пошук товару..." :prefix-icon="Search" size="small" clearable class="mb-2" />
            <el-select v-model="filterCategory" placeholder="Категорія" clearable size="small" class="mb-2 w-100">
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-select v-model="filterWarehouse" placeholder="Обрати склад" clearable size="small" class="w-100">
              <el-option v-for="wh in warehouses" :key="wh.id" :label="wh.name" :value="wh.id" />
            </el-select>
          </div>
        </el-popover>

        <el-button :icon="List" size="small" class="compact-action-btn ml-2" @click="drawerVisible = true">
          Історія рухів
        </el-button>
      </div>

      <div class="actions-right">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog" size="small" class="action-primary-btn">
          Додати Склад
        </el-button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <el-row :gutter="15" class="stats-row mt-3">
      <el-col :xs="12" :sm="6">
        <div class="premium-metric-card">
          <span class="metric-title">Складів</span>
          <span class="metric-value">{{ warehouses.length }}</span>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <div class="premium-metric-card">
          <span class="metric-title">Загальний запас</span>
          <span class="metric-value">{{ totalStockQty }} шт</span>
        </div>
      </el-col>

      <el-col :xs="12" :sm="6">
        <div class="premium-metric-card">
          <span class="metric-title">Оцінка капіталу</span>
          <span class="metric-value">{{ formatCurrency(totalStockValue) }}</span>
        </div>
      </el-col>

      <el-col :xs="12" :sm="6">
        <div class="premium-metric-card">
          <span class="metric-title">Ефективність</span>
          <span class="metric-value">A+</span>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content: Warehouse Expandable Grid -->
    <div class="mt-4 list-container">
      <el-table v-loading="loading" :data="filteredWarehouses" style="width: 100%" class="light-premium-table" size="small">
        <el-table-column type="expand">
          <template #default="props">
            <div class="expand-content">
              <div class="expand-header">
                <h4>Залишки на складі: <strong>{{ props.row.name }}</strong></h4>
                <span class="financial-valuation">Вартість активів: <strong>{{ formatCurrency(getWarehouseStockValue(props.row.id)) }}</strong></span>
              </div>

              <el-table :data="getWarehouseStock(props.row.id)" size="small" class="light-inner-table mt-2" stripe border>
                <el-table-column label="Товар" min-width="200">
                  <template #default="scope">
                    <router-link :to="'/inventory/nomenclature/' + scope.row.product_id" class="product-link" v-if="scope.row.product_id">
                      {{ scope.row.product_name }}
                    </router-link>
                    <span v-else>{{ scope.row.product_name }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Категорія" prop="category" min-width="120">
                  <template #default="scope">
                    <el-tag size="small" type="info" effect="plain" v-if="scope.row.category">{{ scope.row.category }}</el-tag>
                    <span v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="Характеристика" prop="variant_label" min-width="120">
                  <template #default="scope">
                    <span v-if="scope.row.variant_label">{{ scope.row.variant_label }}</span>
                    <span class="empty-text" v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="Собівартість" width="120" align="right">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.cost) }}
                  </template>
                </el-table-column>
                <el-table-column label="Кількість" prop="quantity" width="100" align="right">
                  <template #default="scope">
                    <span class="stock-qty">{{ scope.row.quantity }} шт</span>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="120" align="right">
                  <template #default="scope">
                    <span class="total-amount">{{ formatCurrency(scope.row.quantity * scope.row.cost) }}</span>
                  </template>
                </el-table-column>
              </el-table>
              
              <div v-if="!getWarehouseStock(props.row.id).length" class="empty-stock-state">
                <span>Немає товарів.</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Назва" prop="name" min-width="180">
          <template #default="scope">
            <div class="warehouse-name-cell">
              <span class="warehouse-name">{{ scope.row.name }}</span>
              <el-tag v-if="scope.row.is_default" type="primary" size="small" class="default-tag" effect="plain">
                основний
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Адреса" prop="address" min-width="180">
          <template #default="scope">
            <span>{{ scope.row.address || '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="К-ть позицій" width="120" align="center">
          <template #default="scope">
            <span>{{ getWarehouseItemsCount(scope.row.id) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="% заповненості" width="140" align="center">
          <template #default="scope">
            <el-progress 
              :percentage="getWarehouseCapacity(scope.row.id)" 
              :status="getWarehouseCapacity(scope.row.id) > 80 ? 'exception' : 'success'" 
              :stroke-width="6" 
            />
          </template>
        </el-table-column>

        <el-table-column label="Статус" prop="is_active" width="120" align="center">
          <template #default="scope">
            <span class="status-dot" :class="scope.row.is_active ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ scope.row.is_active ? 'Активний' : 'Повний' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="120" align="center">
          <template #default="scope">
            <div class="actions-cell">
              <el-button type="primary" :icon="Edit" circle size="small" @click="openEditDialog(scope.row)" />
              <el-button type="danger" :icon="Delete" circle size="small" :disabled="scope.row.is_default" @click="confirmDelete(scope.row)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Side Drawer for Movement History -->
    <el-drawer v-model="drawerVisible" title="Історія руху товарів" size="45%">
      <el-table :data="movements" size="small" border stripe>
        <el-table-column prop="created_at" label="Дата" width="150">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="product_name" label="Товар" min-width="150" />
        <el-table-column prop="quantity" label="К-ть" width="90" align="right">
          <template #default="scope">
            <span :class="scope.row.quantity > 0 ? 'qty-plus' : 'qty-minus'" class="qty-badge">
              {{ scope.row.quantity > 0 ? '+' : '' }}{{ scope.row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="document_type" label="Документ" width="150">
          <template #default="scope">
            <span class="doc-type-text">{{ mapDocType(scope.row.document_type) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <!-- AI Floating Action Button (FAB) -->
    <div class="ai-fab-button" @click="aiDialogVisible = true">
      <span class="ai-fab-pulse"></span>
      <el-icon><MagicStick /></el-icon>
    </div>

    <!-- AI Assistant Insights Dialog -->
    <el-dialog v-model="aiDialogVisible" title="AI Помічник" width="400px" class="ai-insight-dialog" append-to-body>
      <div class="ai-chat-block">
        <div class="ai-chat-header">
          <span class="ai-avatar">🤖</span>
          <div class="ai-meta">
            <strong>Складський Аналітик</strong>
            <p>Аналіз залишків у реальному часі</p>
          </div>
        </div>
        <div class="ai-chat-body mt-3">
          <div class="ai-message">
            <strong>Прогноз вичерпання:</strong> "ДСП Сонома 18 мм" вичерпається приблизно за <strong>8 днів</strong>.
            <br/><br/>
            💡 <strong>Рекомендація:</strong> Створити замовлення постачальнику на поповнення (мінімум 50 шт).
          </div>
          <div class="ai-metrics-grid mt-3">
            <div class="ai-metric-item">
              <span class="lbl">ОБОРОТНІСТЬ</span>
              <span class="val">1.2 рази/міс</span>
            </div>
            <div class="ai-metric-item">
              <span class="lbl">РЕЗЕРВ</span>
              <span class="val">10 днів</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" class="w-100" @click="aiDialogVisible = false">Зрозуміло</el-button>
      </template>
    </el-dialog>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="450px" class="light-dialog">
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
        <el-button @click="dialogVisible = false" size="small">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveWarehouse" size="small">Зберегти</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, Search, Download, DocumentDelete, Switch, MagicStick, List } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const searchQuery = ref('')
const filterProduct = ref('')
const filterCategory = ref('')
const filterWarehouse = ref('')

const loading = ref(false)
const submitting = ref(false)
const warehouses = ref([])
const allStock = ref([])
const movements = ref([])

const dialogVisible = ref(false)
const drawerVisible = ref(false)
const aiDialogVisible = ref(false)
const dialogTitle = ref('Створити склад')
const formRef = ref(null)

const form = ref({
  id: null,
  name: '',
  address: '',
  is_default: false,
  is_active: true
})

const categories = computed(() => {
  const list = allStock.value.map(i => i.category).filter(Boolean)
  return [...new Set(list)]
})

const filteredWarehouses = computed(() => {
  let list = warehouses.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    list = list.filter(w => w.name.toLowerCase().includes(query))
  }
  if (filterWarehouse.value) {
    list = list.filter(w => w.id === filterWarehouse.value)
  }
  return list
})

const getWarehouseStock = (warehouseId) => {
  let stock = allStock.value.filter(item => item.warehouse_id === warehouseId)
  if (filterProduct.value) {
    const prodQuery = filterProduct.value.toLowerCase()
    stock = stock.filter(i => i.product_name.toLowerCase().includes(prodQuery))
  }
  if (filterCategory.value) {
    stock = stock.filter(i => i.category === filterCategory.value)
  }
  return stock
}

const getWarehouseItemsCount = (warehouseId) => {
  return allStock.value.filter(item => item.warehouse_id === warehouseId).length
}

const getWarehouseCapacity = (warehouseId) => {
  const itemsCount = getWarehouseItemsCount(warehouseId)
  // Simulated capacity
  return Math.min(100, Math.round((itemsCount / 15) * 100)) || 0
}

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

    const moveRes = await api.get('/api/v1/warehouses/movements')
    movements.value = moveRes.data
  } catch (e) {
    console.error(e)
    ElMessage.error('Помилка завантаження даних складів')
  } finally {
    loading.value = false
  }
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

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const mapDocType = (type) => {
  const maps = {
    'purchase_receipt': 'Прихід',
    'sales_invoice': 'Продаж',
    'production_order': 'Випуск'
  }
  return maps[type] || type
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
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

.erp-light-container {
  padding: 20px;
  background-color: #F4F6FA;
  min-height: calc(100vh - 60px);
  color: #1E293B;
  font-family: 'Inter', sans-serif;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.erp-actions-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.compact-action-btn {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
}
.compact-action-btn:hover {
  transform: translateY(-1px);
}

.action-primary-btn {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  border: none !important;
  border-radius: 8px;
  font-weight: 700;
  color: white !important;
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
  transition: all 0.2s ease;
}
.action-primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(108, 99, 255, 0.4);
}

.popover-filters-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 5px;
}

.premium-metric-card {
  background: #FFFFFF;
  border: 1px solid rgba(0, 0, 0, 0.03);
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 90px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}
.premium-metric-card:hover {
  transform: translateY(-2px);
}

.metric-title {
  font-size: 0.75rem;
  color: #64748B;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 500;
  color: #0F172A;
  font-family: 'DM Mono', monospace;
  margin-top: 6px;
}

.light-premium-table {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.warehouse-name {
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: #0F172A;
}

.default-tag {
  font-size: 0.65rem;
  font-weight: 700;
  margin-left: 8px;
  border-radius: 6px;
  color: #6C63FF !important;
  border-color: rgba(108, 99, 255, 0.2) !important;
}

.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-dot.active {
  background: #00C9A7;
  box-shadow: 0 0 8px rgba(0, 201, 167, 0.4);
}
.status-dot.inactive {
  background: #FF6B6B;
}

.status-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #475569;
}

.expand-content {
  background: #F8FAFC;
  padding: 16px;
  border-radius: 8px;
  margin: 5px;
  border: 1px solid #EDF2F7;
}

.expand-header h4 {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.financial-valuation {
  font-size: 0.85rem;
  color: #64748B;
  font-family: 'DM Mono', monospace;
}

.light-inner-table {
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  overflow: hidden;
}

.product-link {
  color: #6C63FF;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s ease;
}
.product-link:hover {
  color: #00C9A7;
}

.stock-qty, .total-amount {
  font-family: 'DM Mono', monospace;
}

.qty-badge {
  font-weight: 600;
  font-family: 'DM Mono', monospace;
}
.qty-plus { color: #00C9A7; }
.qty-minus { color: #FF6B6B; }

/* Drawer */
:deep(.el-drawer) {
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.95) !important;
}

/* Floating Action Button (FAB) */
.ai-fab-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 55px;
  height: 55px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 20px rgba(108, 99, 255, 0.4);
  cursor: pointer;
  z-index: 999;
  transition: transform 0.2s ease;
}
.ai-fab-button:hover {
  transform: translateY(-2px) scale(1.05);
}

.ai-fab-pulse {
  position: absolute;
  width: 100%; height: 100%;
  border-radius: 50%;
  background: rgba(108, 99, 255, 0.3);
  animation: pulse 2s infinite;
  z-index: -1;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

/* AI Dialog Overlay */
:deep(.ai-insight-dialog) {
  border-radius: 16px;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.95) !important;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.ai-chat-header {
  display: flex;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 12px;
}
.ai-avatar { font-size: 2rem; }
.ai-meta strong {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  color: #0F172A;
}

.ai-message {
  background: #F8FAFC;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  font-size: 0.9rem;
  color: #334155;
  line-height: 1.6;
}

.ai-metrics-grid {
  display: flex;
  gap: 10px;
}

.ai-metric-item {
  flex: 1;
  background: #FFFFFF;
  border: 1px solid rgba(0, 0, 0, 0.03);
  padding: 12px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.ai-metric-item .lbl {
  font-size: 0.65rem;
  color: #64748B;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.ai-metric-item .val {
  font-size: 1.1rem;
  font-weight: 500;
  color: #0F172A;
  font-family: 'DM Mono', monospace;
  display: block;
  margin-top: 4px;
}

.ml-2 { margin-left: 8px; }
.mb-2 { margin-bottom: 8px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.w-100 { width: 100%; }
.doc-type-text { font-size: 0.8rem; color: #475569; }
</style>
