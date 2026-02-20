<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? 'Замовлення №' + form.order_number : 'Нове замовлення' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveOrder">
          Зберегти замовлення
        </el-button>
      </div>
    </div>

    <div class="editor-content" v-loading="loading">
      <el-form :model="form" label-position="top" class="order-form">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="Номер замовлення">
              <el-input v-model="form.order_number" placeholder="ORD-0001" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Дата">
              <el-date-picker v-model="form.order_date" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Клієнт">
              <el-select v-model="form.counterparty_id" filterable placeholder="Оберіть клієнта" style="width: 100%">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Склад">
              <el-select v-model="form.warehouse_id" placeholder="Оберіть склад" style="width: 100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>Товари та послуги</el-divider>

        <el-table :data="form.lines" border style="width: 100%" class="lines-table">
          <el-table-column label="Товар" min-width="300">
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
                  <span style="float: right; color: #8492a6; font-size: 13px">{{ formatCurrencyShort(p.price) }}</span>
                </el-option>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Кількість" width="150">
            <template #default="scope">
              <el-input-number v-model="scope.row.quantity" :min="0.001" @change="updateLineTotal(scope.row)" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="Ціна" width="180">
            <template #default="scope">
              <el-input-number v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" :precision="2" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="Сума" width="180">
            <template #default="scope">
              <span class="line-total">{{ formatCurrency(scope.row.total) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="" width="60" align="center">
            <template #default="scope">
              <el-button type="danger" :icon="Delete" circle @click="removeLine(scope.$index)" />
            </template>
          </el-table-column>
        </el-table>

        <div class="form-footer">
          <el-button type="dashed" :icon="Plus" @click="addLine" class="add-line-btn">
            Додати рядок
          </el-button>
          
          <div class="summary-card">
            <div class="summary-row">
              <span class="label">Разом:</span>
              <span class="value">{{ formatCurrency(totalAmount) }}</span>
            </div>
          </div>
        </div>
      </el-form>
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
  order_date: new Date(),
  counterparty_id: '',
  warehouse_id: '',
  lines: []
})

// Options
const customers = ref([])
const warehouses = ref([])
const products = ref([])

const totalAmount = computed(() => {
  return form.lines.reduce((acc, line) => acc + (line.total || 0), 0)
})

const goBack = () => router.push('/sales/orders')

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
      if (typeof form.order_date === 'string') {
        form.order_date = new Date(form.order_date)
      }
    } else {
      // Add initial line
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
    ElMessage.warning('Заповніть обов’язкові поля та додайте товари')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...form,
      total_amount: totalAmount.value,
      // Format date for backend
      order_date: form.order_date.toISOString().split('T')[0]
    }
    
    if (isEditMode.value) {
      await api.put(`/api/v1/orders/${route.params.id}`, payload)
      ElMessage.success('Замовлення оновлено')
    } else {
      await api.post('/api/v1/orders', payload)
      ElMessage.success('Замовлення створено')
    }
    goBack()
  } catch (error) {
    ElMessage.error('Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val)
const formatCurrencyShort = (val) => new Intl.NumberFormat('uk-UA').format(val) + ' грн'

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8f9fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #eef0f2;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1d1f;
}

.editor-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.order-form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  max-width: 1200px;
  margin: 0 auto;
}

.lines-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.line-total {
  font-weight: 600;
  color: #1a1d1f;
}

.form-footer {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.add-line-btn {
  height: 44px;
  padding: 0 24px;
  border-style: dashed;
  color: #6f767e;
}

.summary-card {
  background: #fcfcfc;
  padding: 20px 30px;
  border-radius: 12px;
  border: 1px solid #eef0f2;
  min-width: 300px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-row .label {
  font-size: 16px;
  color: #6f767e;
}

.summary-row .value {
  font-size: 24px;
  font-weight: 700;
  color: #2a85ff;
}
</style>
