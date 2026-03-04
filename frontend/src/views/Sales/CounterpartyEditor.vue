<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? form.name || 'Контрагент' : 'Новий контрагент' }}</h2>
        <div class="header-tags" v-if="isEditMode">
          <el-tag v-if="form.is_customer" type="success" size="small">Клієнт</el-tag>
          <el-tag v-if="form.is_supplier" type="warning" size="small">Постачальник</el-tag>
        </div>
      </div>
      <div class="header-actions">
        <el-button v-if="isEditMode" type="danger" @click="confirmDelete" plain>
          Видалити
        </el-button>
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveCounterparty">
          Зберегти
        </el-button>
      </div>
    </div>

    <div class="editor-content" v-loading="loading">
      <el-tabs v-model="activeTab" class="cp-tabs">
        <!-- 1. General Info -->
        <el-tab-pane label="Загальна інформація" name="general">
          <div class="tab-content">
            <div class="form-grid">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <span class="card-title">Основні дані</span>
                </template>
                <el-form :model="form" label-position="top" class="edit-form">
                  <el-form-item label="Назва (коротка)" required>
                    <el-input v-model="form.name" placeholder="Наприклад: ТОВ 'Атлант'" size="large" />
                  </el-form-item>
                  <el-form-item label="Юридична назва">
                    <el-input v-model="form.legal_name" placeholder="Повна юридична назва" size="large" />
                  </el-form-item>
                  <el-form-item label="ЄДРПОУ / ІПН">
                    <el-input v-model="form.tax_id" placeholder="8 або 10 цифр" size="large" />
                  </el-form-item>
                  <div class="form-row">
                    <el-form-item label="Це клієнт?">
                      <el-switch v-model="form.is_customer" />
                    </el-form-item>
                    <el-form-item label="Це постачальник?">
                      <el-switch v-model="form.is_supplier" />
                    </el-form-item>
                    <el-form-item label="Активний?">
                      <el-switch v-model="form.is_active" />
                    </el-form-item>
                  </div>
                </el-form>
              </el-card>

              <el-card shadow="never" class="form-card">
                <template #header>
                  <span class="card-title">Контактна інформація</span>
                </template>
                <el-form :model="form" label-position="top" class="edit-form">
                  <el-form-item label="Телефон">
                    <el-input v-model="form.phone" placeholder="+380..." size="large">
                      <template #prefix>
                        <el-icon><Phone /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="Email">
                    <el-input v-model="form.email" placeholder="example@mail.com" size="large">
                      <template #prefix>
                        <el-icon><Message /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="Адреса">
                    <el-input v-model="form.address" type="textarea" :rows="3" placeholder="Юридична або фактична адреса" />
                  </el-form-item>
                  <el-form-item label="Договір за замовчуванням">
                    <el-input v-model="form.default_contract" placeholder="№ договору для автопідстановки" size="large">
                      <template #prefix>
                        <el-icon><Document /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-form>
              </el-card>
            </div>
          </div>
        </el-tab-pane>

        <!-- 2. Sales History -->
        <el-tab-pane label="Історія продажів" name="sales" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <span class="card-title">Замовлення на продаж</span>
              </template>
              <el-table :data="salesOrders" style="width: 100%">
                <el-table-column prop="order_number" label="Номер" width="140" />
                <el-table-column prop="order_date" label="Дата" width="120" />
                <el-table-column prop="status" label="Статус" width="120">
                  <template #default="scope">
                    <el-tag :type="getStatusType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="total_amount" label="Сума" width="150" align="right">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.total_amount) }}
                  </template>
                </el-table-column>
                <el-table-column label="" min-width="100">
                  <template #default>
                    <!-- placeholder for future actions -->
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="salesOrders.length === 0" description="Немає замовлень на продаж" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 3. Purchase History -->
        <el-tab-pane label="Історія закупівель" name="purchases" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <span class="card-title">Прибуткові накладні</span>
              </template>
              <el-table :data="purchaseReceipts" style="width: 100%">
                <el-table-column prop="receipt_number" label="Номер" width="140" />
                <el-table-column prop="receipt_date" label="Дата" width="120" />
                <el-table-column prop="status" label="Статус" width="120">
                  <template #default="scope">
                    <el-tag :type="getStatusType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="total_amount" label="Сума" width="150" align="right">
                  <template #default="scope">
                    {{ formatCurrency(scope.row.total_amount) }}
                  </template>
                </el-table-column>
                <el-table-column label="" min-width="100">
                  <template #default>
                    <!-- placeholder for future actions -->
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="purchaseReceipts.length === 0" description="Немає прибуткових накладних" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 4. Finances -->
        <el-tab-pane label="Фінанси" name="finances" :disabled="!isEditMode">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-card shadow="never" class="stat-card-finance">
                  <div class="finance-stat">
                    <span class="finance-label">Загальна сума продажів</span>
                    <span class="finance-value text-success">{{ formatCurrency(financeSummary.totalSales) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-card shadow="never" class="stat-card-finance">
                  <div class="finance-stat">
                    <span class="finance-label">Загальна сума закупівель</span>
                    <span class="finance-value text-warning">{{ formatCurrency(financeSummary.totalPurchases) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-card shadow="never" class="stat-card-finance">
                  <div class="finance-stat">
                    <span class="finance-label">Баланс</span>
                    <span class="finance-value" :class="financeSummary.balance >= 0 ? 'text-success' : 'text-danger'">
                      {{ formatCurrency(financeSummary.balance) }}
                    </span>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            <el-card shadow="never" class="form-card" style="margin-top: 20px">
              <template #header>
                <span class="card-title">Фінансові операції</span>
              </template>
              <el-empty description="Фінансові операції будуть доступні після впровадження модуля Фінансів" />
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Phone, Message, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id)

const form = reactive({
  id: null,
  name: '',
  legal_name: '',
  tax_id: '',
  is_customer: true,
  is_supplier: false,
  phone: '',
  email: '',
  address: '',
  default_contract: '',
  is_active: true
})

// Related data (for tabs)
const salesOrders = ref([])
const purchaseReceipts = ref([])
const financeSummary = reactive({
  totalSales: 0,
  totalPurchases: 0,
  balance: 0
})

const goBack = () => {
  router.push('/sales/counterparties')
}

const fetchCounterparty = async () => {
  if (!isEditMode.value) return
  loading.value = true
  try {
    const res = await api.get(`/api/v1/counterparties/${route.params.id}`)
    Object.assign(form, res.data)
    // Fetch related data
    fetchSalesHistory()
    fetchPurchaseHistory()
  } catch (e) {
    ElMessage.error('Помилка завантаження контрагента')
  } finally {
    loading.value = false
  }
}

const fetchSalesHistory = async () => {
  try {
    const res = await api.get('/api/v1/orders', { 
      params: { counterparty_id: route.params.id, limit: 50 } 
    })
    salesOrders.value = res.data || []
  } catch (e) {
    console.error('Failed to load sales history', e)
  }
}

const fetchPurchaseHistory = async () => {
  try {
    const res = await api.get('/api/v1/purchase-receipts', { 
      params: { supplier_id: route.params.id, limit: 50 } 
    })
    purchaseReceipts.value = res.data || []
  } catch (e) {
    console.error('Failed to load purchase history', e)
  }
}

const saveCounterparty = async () => {
  if (!form.name) {
    ElMessage.warning('Вкажіть назву контрагента')
    return
  }
  
  // Clean empty strings → null for optional fields (Pydantic EmailStr rejects "")
  const payload = { ...form }
  const optionalFields = ['legal_name', 'tax_id', 'phone', 'email', 'address', 'default_contract']
  optionalFields.forEach(field => {
    if (payload[field] === '') payload[field] = null
  })

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/counterparties/${form.id}`, payload)
      ElMessage.success('Дані оновлено')
    } else {
      const res = await api.post('/api/v1/counterparties', payload)
      ElMessage.success('Контрагента додано')
      router.push(`/sales/counterparties/${res.data.id}`)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const confirmDelete = () => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити цього контрагента?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/counterparties/${form.id}`)
      ElMessage.success('Контрагента видалено')
      router.push('/sales/counterparties')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  })
}

// Helpers
const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', { 
    style: 'currency', 
    currency: 'UAH',
    maximumFractionDigits: 2
  }).format(value || 0)
}

const getStatusType = (status) => {
  const map = {
    'draft': 'info',
    'confirmed': '',
    'posted': 'success',
    'shipped': 'warning',
    'completed': 'success',
    'cancelled': 'danger',
    'DRAFT': 'info',
    'POSTED': 'success',
    'CANCELLED': 'danger'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchCounterparty()
})
</script>

<style scoped>
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 20px;
  border-bottom: 1px solid #eef0f2;
  flex-shrink: 0;
  gap: 12px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-tags {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
}

.cp-tabs {
  height: 100%;
}

:deep(.el-tabs__header) {
  background: white;
  padding: 0 20px;
  margin-bottom: 0;
}

:deep(.el-tabs__nav-wrap) {
  overflow-x: auto;
}

.tab-content {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1d1f;
}

.form-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

/* Finance stats */
.stat-card-finance {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.finance-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
}

.finance-label {
  font-size: 13px;
  color: #6f767e;
  font-weight: 500;
  margin-bottom: 8px;
  text-align: center;
}

.finance-value {
  font-size: 22px;
  font-weight: 700;
}

.text-success { color: #7ad472; }
.text-warning { color: #ffbc33; }
.text-danger { color: #ff6b6b; }

/* Responsive: sidebar takes ~220px, so content area is smaller */
@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 10px 16px;
  }
  .tab-content {
    padding: 16px;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .header-left h2 {
    font-size: 16px;
  }
  .finance-value {
    font-size: 18px;
  }
}
</style>

