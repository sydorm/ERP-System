<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Видаткові накладні</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Продажі</el-breadcrumb-item>
          <el-breadcrumb-item>Накладні</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-primary">
          Створити накладну
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="Номер накладної..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
      </div>
    </div>

    <!-- Data Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        v-loading="loading" 
        :data="invoices" 
        stripe 
        style="width: 100%"
        class="custom-table"
      >
        <el-table-column prop="invoice_number" label="№ Накладної" width="150" sortable />
        <el-table-column prop="invoice_date" label="Дата" width="120">
          <template #default="scope">{{ formatDate(scope.row.invoice_date) }}</template>
        </el-table-column>
        
        <el-table-column label="Клієнт" min-width="200">
          <template #default="scope">
            {{ getCounterpartyName(scope.row.counterparty_id) || 'Завантаження...' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="total_amount" label="Сума" width="150" align="right">
          <template #default="scope">{{ formatCurrency(scope.row.total_amount) }}</template>
        </el-table-column>
        
        <el-table-column prop="status" label="Статус" width="150" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'posted' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'posted' ? 'Проведено' : 'Чернетка' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Дії" width="120" align="right">
          <template #default="scope">
            <el-button link type="primary" :icon="Edit" @click="handleEdit(scope.row)" />
            <el-button link type="danger" :icon="Delete" @click="handleDelete(scope.row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const invoices = ref([])
const counterparties = ref({})
const searchQuery = ref('')

const fetchInvoices = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/sales-invoices')
    invoices.value = res.data
    
    // Fetch customer names
    const cpIds = [...new Set(invoices.value.map(i => i.counterparty_id))].filter(id => !counterparties.value[id])
    for (const id of cpIds) {
      try {
        const cpRes = await api.get(`/api/v1/counterparties/${id}`)
        counterparties.value[id] = cpRes.data.name
      } catch (e) {
        counterparties.value[id] = 'Н/Д'
      }
    }
  } catch (error) {
    ElMessage.error('Помилка завантаження накладних')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
    // Basic local filtering if needed or server-side
    // For now, let's just refetch if we hit enter or search button
}

const handleCreate = () => router.push('/sales/invoices/new')
const handleEdit = (row) => router.push(`/sales/invoices/${row.id}`)

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити накладну ${row.invoice_number}?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/sales-invoices/${row.id}`)
      ElMessage.success('Видалено')
      fetchInvoices()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

// Helpers
const formatDate = (dateStr) => dateStr ? new Date(dateStr).toLocaleDateString('uk-UA') : ''
const getCounterpartyName = (id) => counterparties.value[id]
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val)

onMounted(fetchInvoices)
onActivated(() => {
  if (invoices.value.length > 0) {
    fetchInvoices()
  }
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1d1f;
}

.btn-primary {
  background: #2a85ff;
  border: none;
  font-weight: 600;
}

.filters-toolbar {
  margin-bottom: 24px;
}

.search-input {
  width: 300px;
}

.content-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}
</style>
