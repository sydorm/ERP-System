<template>
  <div class="page-container">
    <!-- === TOP BAR: Title + Save === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? 'Замовлення №' + form.order_number : 'Нове замовлення' }}</h2>
        <el-tag v-if="isEditMode && form.status" :type="statusType" size="small">{{ statusLabel }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrder">
          Зберегти замовлення
        </el-button>
      </div>
    </div>

    <!-- === STICKY: Order details panel === -->
    <div class="order-details-panel">
      <el-form :model="form" label-position="top" size="default" class="details-form">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="4">
            <el-form-item label="Номер">
              <el-input v-model="form.order_number" placeholder="ORD-0001" />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="12" :md="4">
            <el-form-item label="Дата створення">
              <el-date-picker v-model="form.order_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="12" :md="4">
            <el-form-item label="Дата відвантаження">
              <el-date-picker v-model="form.shipping_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" placeholder="Планова" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="4">
            <el-form-item label="Клієнт" required>
              <el-select v-model="form.counterparty_id" filterable placeholder="Оберіть клієнта" style="width: 100%" @change="onClientChange">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="4">
            <el-form-item label="Договір">
              <el-input v-model="form.contract" placeholder="№ договору" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="4">
            <el-form-item label="Склад" required>
              <el-select v-model="form.warehouse_id" placeholder="Оберіть склад" style="width: 100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- === MIDDLE: Scrollable product lines === -->
    <div class="lines-section" v-loading="loading">
      <div class="lines-header">
        <h3>Товари та послуги</h3>
        <el-button type="primary" :icon="Plus" @click="addLine" size="small">Додати рядок</el-button>
      </div>

      <el-table :data="form.lines" border style="width: 100%" class="lines-table">
        <el-table-column type="index" label="№" width="50" align="center" />
        <el-table-column label="Товар" min-width="280">
          <template #default="scope">
            <el-select 
              v-model="scope.row.product_id" 
              filterable 
              placeholder="Пошук товару..." 
              style="width: 100%"
              @change="(val) => handleProductChange(val, scope.row)"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id">
                <span style="float: left">{{ p.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ formatShort(p.price) }}</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Кількість" width="130">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="0.001" @change="updateLineTotal(scope.row)" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Ціна" width="140">
          <template #default="scope">
            <el-input-number v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" :precision="2" style="width: 100%" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="130" align="right">
          <template #default="scope">
            <span class="line-total">{{ formatCurrency(scope.row.total) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="" width="50" align="center">
          <template #default="scope">
            <el-button type="danger" :icon="Delete" link @click="removeLine(scope.$index)" />
          </template>
        </el-table-column>
      </el-table>

      <div v-if="form.lines.length === 0" class="empty-lines">
        <el-empty description="Додайте товари до замовлення" :image-size="60">
          <el-button type="primary" :icon="Plus" @click="addLine">Додати рядок</el-button>
        </el-empty>
      </div>
    </div>

    <!-- === FIXED BOTTOM: Comments, discount, total === -->
    <div class="order-footer">
      <div class="footer-left">
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="2"
          placeholder="Коментар до замовлення..."
          class="comment-input"
        />
      </div>
      <div class="footer-right">
        <div class="summary-rows">
          <div class="summary-row">
            <span class="s-label">Сума:</span>
            <span class="s-value">{{ formatCurrency(subtotal) }}</span>
          </div>
          <div class="summary-row discount-row">
            <span class="s-label">Знижка (%):</span>
            <el-input-number
              v-model="form.discount_percent"
              :min="0"
              :max="100"
              :precision="1"
              :step="1"
              controls-position="right"
              size="small"
              style="width: 100px"
            />
          </div>
          <div class="summary-row total-row" v-if="discountAmount > 0">
            <span class="s-label">Знижка:</span>
            <span class="s-value text-danger">-{{ formatCurrency(discountAmount) }}</span>
          </div>
          <div class="summary-row total-row">
            <span class="s-label total-label">Разом:</span>
            <span class="s-value total-value">{{ formatCurrency(totalAmount) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// State
const loading = ref(false)
const submitting = ref(false)
const isEditMode = computed(() => !!route.params.id)

const form = reactive({
  order_number: 'ORD-' + Date.now().toString().slice(-6),
  order_date: new Date().toISOString().split('T')[0],
  shipping_date: null,
  counterparty_id: '',
  warehouse_id: '',
  contract: '',
  comment: '',
  discount_percent: 0,
  status: 'draft',
  lines: []
})

// Options
const customers = ref([])
const warehouses = ref([])
const products = ref([])

// Computed
const subtotal = computed(() => {
  return form.lines.reduce((acc, line) => acc + (line.total || 0), 0)
})

const discountAmount = computed(() => {
  return subtotal.value * (form.discount_percent || 0) / 100
})

const totalAmount = computed(() => {
  return subtotal.value - discountAmount.value
})

const statusType = computed(() => {
  const map = { draft: 'info', confirmed: '', shipped: 'warning', completed: 'success', cancelled: 'danger' }
  return map[form.status] || 'info'
})

const statusLabel = computed(() => {
  const map = { draft: 'Чернетка', confirmed: 'Підтверджено', shipped: 'Відвантажено', completed: 'Завершено', cancelled: 'Скасовано' }
  return map[form.status] || form.status
})

const goBack = () => router.push('/sales/orders')

const onClientChange = (clientId) => {
  // Auto-fill contract from client if available (future enhancement)
  console.log('Client changed:', clientId)
}

const addLine = () => {
  form.lines.push({
    product_id: '',
    quantity: 1,
    price: 0,
    total: 0
  })
}

const removeLine = (index) => {
  form.lines.splice(index, 1)
}

const updateLineTotal = (line) => {
  line.total = parseFloat((line.quantity * line.price).toFixed(2))
}

const handleProductChange = (productId, line) => {
  const product = products.value.find(p => p.id === productId)
  if (product) {
    line.price = product.price
    updateLineTotal(line)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [custRes, whRes, prodRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_customer: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products')
    ])
    customers.value = custRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    
    if (isEditMode.value) {
      const res = await api.get(`/api/v1/orders/${route.params.id}`)
      Object.assign(form, res.data)
    } else {
      addLine()
    }
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const saveOrder = async () => {
  if (!form.counterparty_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля та додайте товари")
    return
  }

  // Clean empty optional fields
  const payload = {
    ...form,
    total_amount: totalAmount.value,
    shipping_date: form.shipping_date || null,
    contract: form.contract || null,
    comment: form.comment || null,
    discount_percent: form.discount_percent || 0
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/orders/${route.params.id}`, payload)
      ElMessage.success('Замовлення оновлено')
    } else {
      await api.post('/api/v1/orders', payload)
      ElMessage.success('Замовлення створено')
    }
    goBack()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)
const formatShort = (val) => new Intl.NumberFormat('uk-UA').format(val) + ' грн'

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f8f9fa;
}

/* === TOP BAR === */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: white;
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
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1d1f;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* === STICKY DETAILS PANEL === */
.order-details-panel {
  background: white;
  padding: 16px 20px 4px;
  border-bottom: 1px solid #eef0f2;
  flex-shrink: 0;
}

.details-form :deep(.el-form-item) {
  margin-bottom: 12px;
}

.details-form :deep(.el-form-item__label) {
  font-size: 12px;
  color: #6f767e;
  padding-bottom: 2px;
}

/* === SCROLLABLE LINES === */
.lines-section {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.lines-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a1d1f;
}

.lines-table {
  border-radius: 8px;
  overflow: hidden;
}

.line-total {
  font-weight: 600;
  color: #1a1d1f;
}

.empty-lines {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 8px;
}

/* === FIXED FOOTER === */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #eef0f2;
  flex-shrink: 0;
  gap: 20px;
}

.footer-left {
  flex: 1;
  max-width: 500px;
}

.comment-input :deep(.el-textarea__inner) {
  border-radius: 8px;
}

.footer-right {
  flex-shrink: 0;
  min-width: 280px;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.s-label {
  font-size: 14px;
  color: #6f767e;
}

.s-value {
  font-size: 14px;
  font-weight: 600;
  color: #1a1d1f;
}

.text-danger {
  color: #ff6b6b;
}

.discount-row {
  padding: 4px 0;
}

.total-row {
  padding-top: 8px;
  border-top: 1px solid #eef0f2;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
  color: #1a1d1f;
}

.total-value {
  font-size: 22px;
  font-weight: 700;
  color: #2a85ff;
}

/* Responsive */
@media (max-width: 768px) {
  .order-footer {
    flex-direction: column;
  }
  .footer-left {
    max-width: 100%;
  }
  .footer-right {
    width: 100%;
    min-width: auto;
  }
  .page-header {
    padding: 8px 16px;
  }
}
</style>
