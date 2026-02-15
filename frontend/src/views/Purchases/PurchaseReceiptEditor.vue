<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEditMode ? 'Прибуткова накладна №' + form.receipt_number : 'Нова прибуткова накладна' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveReceipt">
          Провести та зберегти
        </el-button>
      </div>
    </div>

    <div class="editor-content" v-loading="loading">
      <el-form :model="form" label-position="top" class="receipt-form">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="Номер накладної">
              <el-input v-model="form.receipt_number" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Дата">
              <el-date-picker v-model="form.receipt_date" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Постачальник">
              <el-select v-model="form.supplier_id" placeholder="Оберіть постачальника" style="width: 100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
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

        <el-divider>Товари</el-divider>

        <el-table :data="form.lines" border style="width: 100%">
          <el-table-column label="Товар" min-width="300">
            <template #default="scope">
              <el-select v-model="scope.row.product_id" filterable placeholder="Пошук товару..." style="width: 100%">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Кількість" width="150">
            <template #default="scope">
              <el-input-number v-model="scope.row.quantity" :min="0" @change="updateLineTotal(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column label="Ціна" width="180">
            <template #default="scope">
              <el-input-number v-model="scope.row.price" :min="0" @change="updateLineTotal(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column label="Сума" width="180">
            <template #default="scope">
              <span>{{ scope.row.total.toFixed(2) }} {{ form.currency }}</span>
            </template>
          </el-table-column>
          <el-table-column label="" width="60">
            <template #default="scope">
              <el-button type="danger" :icon="Delete" circle @click="removeLine(scope.$index)" />
            </template>
          </el-table-column>
        </el-table>

        <div class="form-footer">
          <el-button type="dashed" :icon="Plus" @click="addLine" class="add-line-btn">
            Додати товар
          </el-button>
          
          <div class="total-summary">
            <h3>Всього: {{ totalAmount.toFixed(2) }} {{ form.currency }}</h3>
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
  receipt_number: 'PR-' + Date.now().toString().slice(-6),
  receipt_date: new Date(),
  supplier_id: '',
  warehouse_id: '',
  currency: 'UAH',
  lines: []
})

// Options
const suppliers = ref([])
const warehouses = ref([])
const products = ref([])

const totalAmount = computed(() => {
  return form.lines.reduce((acc, line) => acc + (line.total || 0), 0)
})

const goBack = () => {
  router.push('/purchases/receipts')
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
  line.total = line.quantity * line.price
}

const fetchData = async () => {
  try {
    const [supRes, whRes, prodRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products')
    ])
    suppliers.value = supRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    
    if (isEditMode.value) {
      const res = await api.get(`/api/v1/purchase-receipts/${route.params.id}`)
      Object.assign(form, res.data)
    }
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  }
}

const saveReceipt = async () => {
  if (!form.supplier_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning('Заповніть усі обов’язкові поля та додайте товари')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...form,
      total_amount: totalAmount.value
    }
    
    if (isEditMode.value) {
      await api.put(`/api/v1/purchase-receipts/${route.params.id}`, payload)
      ElMessage.success('Накладну оновлено')
    } else {
      await api.post('/api/v1/purchase-receipts', payload)
      ElMessage.success('Накладна успішно проведена')
    }
    goBack()
  } catch (error) {
    ElMessage.error('Помилка збереження')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
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
.editor-content {
  flex: 1;
  padding: 24px;
  background: #f8f9fa;
  overflow-y: auto;
}
.receipt-form {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.form-footer {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.add-line-btn {
  width: 200px;
}
.total-summary {
  text-align: right;
}
</style>
