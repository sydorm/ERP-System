<template>
  <div class="erp-page-container">
    <!-- Toolbar -->
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <h2 class="page-title">Управління складами</h2>
      </div>
      <div class="erp-toolbar-right">
        <el-button type="warning" :icon="Plus" @click="openCreateDialog" class="erp-btn-primary">
          Створити склад
        </el-button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <el-row :gutter="20" class="stats-row mt-4">
      <el-col :span="8">
        <el-card shadow="hover" class="stats-card purple-gradient">
          <div class="stats-content">
            <div class="stats-icon-wrapper">
              <el-icon class="stats-icon"><Box /></el-icon>
            </div>
            <div class="stats-data">
              <span class="stats-label">Всього складів</span>
              <span class="stats-value">{{ warehouses.length }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stats-card blue-gradient">
          <div class="stats-content">
            <div class="stats-icon-wrapper">
              <el-icon class="stats-icon"><Location /></el-icon>
            </div>
            <div class="stats-data">
              <span class="stats-label">Основний склад</span>
              <span class="stats-value">{{ defaultWarehouseName || 'Не призначено' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="stats-card orange-gradient">
          <div class="stats-content">
            <div class="stats-icon-wrapper">
              <el-icon class="stats-icon"><List /></el-icon>
            </div>
            <div class="stats-data">
              <span class="stats-label">Загальний запас</span>
              <span class="stats-value">{{ totalStockQty }} шт</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Content -->
    <div class="content-card mt-6">
      <el-table v-loading="loading" :data="warehouses" style="width: 100%" class="premium-table">
        <el-table-column type="expand">
          <template #default="props">
            <div class="expand-content">
              <h4>Товарні залишки на складі: <strong>{{ props.row.name }}</strong></h4>
              <el-table :data="getWarehouseStock(props.row.id)" size="small" border stripe class="mt-3">
                <el-table-column label="Товар" prop="product_name" min-width="200" />
                <el-table-column label="Характеристика" prop="variant_label" min-width="150">
                  <template #default="scope">
                    <span v-if="scope.row.variant_label">{{ scope.row.variant_label }}</span>
                    <span class="empty-text" v-else>—</span>
                  </template>
                </el-table-column>
                <el-table-column label="Залишок" prop="quantity" width="150" align="right">
                  <template #default="scope">
                    <span class="stock-qty">{{ scope.row.quantity }} шт</span>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="!getWarehouseStock(props.row.id).length" class="empty-stock-state">
                <el-icon class="empty-stock-icon"><InfoFilled /></el-icon>
                <span>На цьому складі немає товарів.</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Назва" prop="name" min-width="200">
          <template #default="scope">
            <div class="warehouse-name-cell">
              <span class="warehouse-name">{{ scope.row.name }}</span>
              <el-tag v-if="scope.row.is_default" type="success" size="small" class="default-tag" effect="dark">
                Основний
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Адреса" prop="address" min-width="250">
          <template #default="scope">
            <span>{{ scope.row.address || '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" prop="is_active" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? 'Активний' : 'Неактивний' }}
            </el-tag>
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

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="premium-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="small">
        <el-form-item label="Назва складу" prop="name">
          <el-input v-model="form.name" placeholder="Напр. Центральний склад" />
        </el-form-item>

        <el-form-item label="Адреса">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="Вкажіть повну адресу складу" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_default" label="Зробити цей склад основним за замовчуванням" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_active" label="Активний для використання в документах" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="small">Скасувати</el-button>
          <el-button type="warning" :loading="submitting" @click="saveWarehouse" size="small" class="erp-btn-primary">Зберегти</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Edit, Delete, Box, Location, List, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

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
.erp-page-container {
  padding: 20px;
  background: #f8fafc;
  min-height: calc(100vh - 64px);
}

.erp-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.stats-row {
  margin-top: 24px;
}

.stats-card {
  border-radius: 12px;
  border: none;
  color: white;
  overflow: hidden;
  position: relative;
}

.stats-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 80%);
  transform: rotate(30deg);
  pointer-events: none;
}

.purple-gradient {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
}

.blue-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
}

.orange-gradient {
  background: linear-gradient(135deg, #f97316 0%, #f59e0b 100%);
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 5px;
}

.stats-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-icon {
  font-size: 24px;
}

.stats-data {
  display: flex;
  flex-direction: column;
}

.stats-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.content-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.warehouse-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.warehouse-name {
  font-weight: 500;
  color: #1e293b;
}

.actions-cell {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.expand-content {
  padding: 16px 24px;
  background: #f8fafc;
  border-radius: 8px;
}

.expand-content h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #334155;
}

.stock-qty {
  font-weight: 600;
  color: #1e293b;
}

.empty-stock-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: #64748b;
  font-style: italic;
}

.empty-stock-icon {
  font-size: 18px;
}

.empty-text {
  color: #cbd5e1;
}

.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
</style>
