<template>
  <div class="erp-light-container">
    <!-- Custom Scrollbar styles injected for layout criteria -->
    <component :is="'style'">
      ::-webkit-scrollbar { width: 4px; height: 4px; }
      ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6C63FF, #00C9A7); border-radius: 2px; }
      ::-webkit-scrollbar-track { background: transparent; }
    </component>

    <!-- Top Actions Bar -->
    <div class="erp-actions-toolbar">
      <div class="actions-left">
        <el-button class="action-header-btn btn-receipt" :icon="Download" @click="quickProcurement" plain>
          Прихід
        </el-button>
        <el-button class="action-header-btn btn-writeoff" :icon="DocumentDelete" @click="quickWriteOff" plain>
          Списання
        </el-button>
        <el-button class="action-header-btn btn-transfer" :icon="Switch" @click="quickTransfer" plain>
          Переміщення
        </el-button>
        
        <!-- Collapsed Filters Popover -->
        <el-popover placement="bottom" title="Параметри фільтрації" :width="320" trigger="click" class="light-popover">
          <template #reference>
            <el-button :icon="Search" class="ghost-btn ml-2">Фільтри</el-button>
          </template>
          <div class="popover-filters-grid">
            <el-input v-model="searchQuery" placeholder="Пошук складу..." :prefix-icon="Search" clearable class="mb-2" />
            <el-input v-model="filterProduct" placeholder="Пошук товару..." :prefix-icon="Search" clearable class="mb-2" />
            <el-select v-model="filterCategory" placeholder="Категорія" clearable class="mb-2 w-100">
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-select v-model="filterWarehouse" placeholder="Обрати склад" clearable class="w-100">
              <el-option v-for="wh in warehouses" :key="wh.id" :label="wh.name" :value="wh.id" />
            </el-select>
          </div>
        </el-popover>

        <el-button :icon="List" class="ghost-btn ml-2" @click="drawerVisible = true">
          Історія рухів
        </el-button>
      </div>

      <div class="actions-right">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog" class="action-primary-btn">
          + Додати Склад
        </el-button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <el-row :gutter="20" class="stats-row mt-4">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card" style="--card-accent: #3B82F6;">
          <div class="metric-card__label">СКЛАДІВ</div>
          <span class="metric-card__trend metric-card__trend--up">↑ +5%</span>
          <div class="metric-card__value">{{ warehouses.length }}</div>
          <div class="metric-card__sparkline">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <path d="M0 25 Q 25 5, 50 20 T 100 10" fill="none" stroke="#3B82F6" stroke-width="2" />
            </svg>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card" style="--card-accent: #22C55E;">
          <div class="metric-card__label">ЗАГАЛЬНИЙ ЗАПАС</div>
          <span class="metric-card__trend metric-card__trend--up">↑ +12%</span>
          <div class="metric-card__value">{{ totalStockQty }} шт</div>
          <div class="metric-card__sparkline">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <path d="M0 15 Q 20 25, 40 5 T 80 20 T 100 5" fill="none" stroke="#22C55E" stroke-width="2" />
            </svg>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card" style="--card-accent: #F59E0B;">
          <div class="metric-card__label">ОЦІНКА КАПІТАЛУ</div>
          <span class="metric-card__trend metric-card__trend--up">↑ +2.4%</span>
          <div class="metric-card__value">{{ formatCurrency(totalStockValue) }}</div>
          <div class="metric-card__sparkline">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <path d="M0 20 L 30 10 L 60 18 L 100 5" fill="none" stroke="#F59E0B" stroke-width="2" />
            </svg>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card" style="--card-accent: #EF4444;">
          <div class="metric-card__label">ЕФЕКТИВНІСТЬ</div>
          <span class="metric-card__trend metric-card__trend--up">↑ +1%</span>
          <div class="metric-card__value">85%</div>
          <div class="metric-card__sparkline">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <path d="M0 20 Q 30 5, 60 25 T 100 15" fill="none" stroke="#EF4444" stroke-width="2" />
            </svg>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- SVG Gradients for Sparklines -->
    <svg style="width:0; height:0; position:absolute;">
      <defs>
        <linearGradient id="violetMint" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#6C63FF" />
          <stop offset="100%" stop-color="#00C9A7" />
        </linearGradient>
      </defs>
    </svg>

    <!-- Main Content: Warehouse Grid -->
    <div class="mt-5 list-container">
      <el-table v-loading="loading" :data="filteredWarehouses" style="width: 100%" class="light-premium-table">
        <el-table-column type="expand">
          <template #default="props">
            <div class="expand-content">
              <div class="expand-header">
                <h4>Залишки на складі: <strong>{{ props.row.name }}</strong></h4>
                <span class="financial-valuation">Вартість активів: <strong>{{ formatCurrency(getWarehouseStockValue(props.row.id)) }}</strong></span>
              </div>

              <el-table :data="getWarehouseStock(props.row.id)" size="small" class="light-inner-table mt-3" stripe border>
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
                <el-table-column label="Характеристика" min-width="120">
                  <template #default="scope">
                    <span v-if="scope.row.characteristic_value">{{ scope.row.characteristic_value }}</span>
                    <span v-else-if="scope.row.variant_name">{{ scope.row.variant_name }}</span>
                    <span v-else-if="scope.row.variant_label">{{ scope.row.variant_label }}</span>
                    <span class="empty-text" v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="Собівартість" width="130" align="right">
                  <template #default="scope">
                    <span class="dm-mono">{{ formatCurrency(scope.row.cost) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Кількість" prop="quantity" width="120" align="right">
                  <template #default="scope">
                    <span class="stock-qty dm-mono">{{ scope.row.quantity }} шт</span>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="140" align="right">
                  <template #default="scope">
                    <span class="total-amount dm-mono">{{ formatCurrency(scope.row.quantity * scope.row.cost) }}</span>
                  </template>
                </el-table-column>
              </el-table>
              
              <div v-if="!getWarehouseStock(props.row.id).length" class="empty-illustration-state">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M20 7v10M4 7v10M22 5H2v4h20V5zM22 15H2v4h20v-4z" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <p>Товарних запасів за вашими критеріями не виявлено.</p>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Назва" prop="name" min-width="200">
          <template #default="scope">
            <div class="warehouse-name-cell">
              <span class="warehouse-name">{{ scope.row.name }}</span>
              <span v-if="scope.row.is_default" class="gradient-badge ml-2">основний</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Адреса" prop="address" min-width="200">
          <template #default="scope">
            <span>{{ scope.row.address || '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="К-ть позицій" width="130" align="center">
          <template #default="scope">
            <span class="dm-mono">{{ getWarehouseItemsCount(scope.row.id) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="% заповненості" width="160" align="center">
          <template #default="scope">
            <el-progress 
              :percentage="getWarehouseCapacity(scope.row.id)" 
              class="gradient-progress"
              :status="getWarehouseCapacity(scope.row.id) > 80 ? 'exception' : 'success'" 
              :stroke-width="8" 
            />
          </template>
        </el-table-column>

        <el-table-column label="Статус" prop="is_active" width="130" align="center">
          <template #default="scope">
            <span class="status-dot" :class="scope.row.is_active ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ scope.row.is_active ? 'Активний' : 'Повний' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="120" align="center">
          <template #default="scope">
            <div class="row-hover-actions">
              <el-button type="primary" :icon="Edit" circle size="small" @click="openEditDialog(scope.row)" />
              <el-button type="danger" :icon="Delete" circle size="small" :disabled="scope.row.is_default" @click="confirmDelete(scope.row)" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Side Drawer for Movement History -->
    <el-drawer v-model="drawerVisible" title="Історія руху товарів" size="45%">
      <el-table :data="movements" size="small" border stripe class="mt-2">
        <el-table-column prop="created_at" label="Дата" width="150">
          <template #default="scope">
            <span class="dm-mono">{{ formatDate(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="Товар" min-width="150" />
        <el-table-column prop="quantity" label="К-ть" width="90" align="right">
          <template #default="scope">
            <span :class="scope.row.quantity > 0 ? 'qty-plus' : 'qty-minus'" class="qty-badge dm-mono">
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

    <!-- AI Floating Menu (FAB) -->
    <div class="ai-fab-wrapper">
      <el-dropdown trigger="hover" placement="top-end">
        <div class="ai-fab-button">
          <span class="ai-fab-pulse"></span>
          <el-icon class="thin-icon"><MagicStick /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="fab-dropdown-menu">
            <el-dropdown-item :icon="MagicStick" @click="aiDialogVisible = true">Аналітика AI</el-dropdown-item>
            <el-dropdown-item :icon="Download" @click="quickProcurement">Прихід</el-dropdown-item>
            <el-dropdown-item :icon="DocumentDelete" @click="quickWriteOff">Списання</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- AI Assistant Insights Dialog -->
    <el-dialog v-model="aiDialogVisible" title="AI Помічник" width="420px" class="ai-insight-dialog" append-to-body>
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
        <el-button type="primary" class="w-100 action-primary-btn" @click="aiDialogVisible = false">Зрозуміло</el-button>
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
        <el-button type="primary" :loading="submitting" @click="saveWarehouse" size="small" class="action-primary-btn">Зберегти</el-button>
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

.thin-icon {
  stroke-width: 1.5;
}

.dm-mono {
  font-family: 'DM Mono', monospace;
}

/* Actions Toolbar */
.erp-actions-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  padding: 15px 20px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-header-btn {
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.action-header-btn.btn-receipt { border-left: 4px solid #6C63FF; }
.action-header-btn.btn-writeoff { border-left: 4px solid #FF6B6B; }
.action-header-btn.btn-transfer { border-left: 4px solid #00C9A7; }

.action-header-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.ghost-btn {
  border-radius: 10px;
  background: transparent !important;
  border: 1px solid #E2E8F0 !important;
  color: #475569 !important;
  font-weight: 500;
}
.ghost-btn:hover {
  background: #F1F5F9 !important;
  color: #1E293B !important;
}

.action-primary-btn {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  border: none !important;
  border-radius: 10px;
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: white !important;
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.action-primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(108, 99, 255, 0.35);
}

.popover-filters-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 5px;
}

/* Stats Dashboard */
.metric-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #F3F4F6;
  padding: 16px 20px;
  position: relative;
  overflow: hidden;
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
  font-family: 'JetBrains Mono', monospace;
  font-size: 28px;
  font-weight: 500;
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
  height: 40px;
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

.metric-value-sub {
  font-size: 0.8rem;
  color: #64748B;
  font-weight: 600;
}

/* Progress Bar Gradients */
:deep(.gradient-progress .el-progress-bar__inner) {
  background: linear-gradient(90deg, #6C63FF, #00C9A7) !important;
}

/* Warehouses Table */
.light-premium-table {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

:deep(.el-table__row) {
  position: relative;
}
:deep(.el-table__row:hover) {
  background: linear-gradient(90deg, rgba(108, 99, 255, 0.03), rgba(0, 201, 167, 0.02)) !important;
}

.warehouse-name {
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: #0F172A;
}

.gradient-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 8px;
  color: white;
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  box-shadow: 0 2px 8px rgba(108, 99, 255, 0.2);
}

.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-dot.active {
  background: #00C9A7;
  box-shadow: 0 0 8px rgba(0, 201, 167, 0.5);
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
  background: #FFFFFF;
  padding: 20px;
  border-radius: 12px;
  margin: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid #F1F5F9;
}

.expand-header h4 {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
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

.empty-illustration-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: #94A3B8;
}
.empty-icon {
  width: 40px; height: 40px;
  color: #CBD5E1;
  margin-bottom: 10px;
}

/* Actions on Row Hover */
.row-hover-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}
:deep(.el-table__row:hover) .row-hover-actions {
  opacity: 1;
}

/* Floating Action Button (FAB Menu) */
.ai-fab-wrapper {
  position: fixed;
  bottom: 35px;
  right: 35px;
  z-index: 9999;
}

.ai-fab-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  box-shadow: 0 6px 20px rgba(108, 99, 255, 0.35);
  cursor: pointer;
  position: relative;
  transition: transform 0.2s ease;
}

.ai-fab-button:hover {
  transform: scale(1.05);
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
  100% { transform: scale(1.4); opacity: 0; }
}

.fab-dropdown-menu {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* AI Assistant Dialog */
:deep(.ai-insight-dialog) {
  border-radius: 16px;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.96) !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
}

.ai-message {
  background: #F8FAFC;
  padding: 16px;
  border-radius: 14px;
  border: 1px solid #E2E8F0;
  line-height: 1.6;
}

.ai-metric-item {
  background: #FFFFFF;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

/* Helper margins */
.ml-2 { margin-left: 8px; }
.mb-2 { margin-bottom: 8px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-5 { margin-top: 20px; }
.w-100 { width: 100%; }
</style>
