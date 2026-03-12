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
        :data="paginatedInvoices" 
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

      <!-- PAGINATION -->
      <div class="pagination-footer">
        <span class="total-hint">Показано {{ paginatedInvoices.length }} з {{ filteredInvoices.length }}</span>
        <div class="custom-pagination-container">
          <el-select v-model="pageSize" size="small" class="limit-select" @change="handleSizeChange">
            <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
          </el-select>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="filteredInvoices.length"
            background
            layout="prev, pager, next"
            class="custom-pagination-numeric"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
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

const currentPage = ref(1)
const pageSize = ref(20)

const filteredInvoices = computed(() => {
  let list = [...invoices.value]
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(i => 
      i.invoice_number?.toLowerCase().includes(q) ||
      getCounterpartyName(i.counterparty_id)?.toLowerCase().includes(q)
    )
  }
  return list
})

const paginatedInvoices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredInvoices.value.slice(start, start + pageSize.value)
})

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
  currentPage.value = 1
}

const handleCreate = () => router.push('/sales/invoices/new')
const handleEdit = (row) => router.push(`/sales/invoices/${row.id}`)

const handlePageChange = (p) => { currentPage.value = p }
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

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

/* ===== PAGINATION ===== */
.pagination-footer {
  display: flex; justify-content: space-between; align-items: center; padding: 12px 20px;
  border-top: 1px solid #e2e8f0; background: #fff; flex-shrink: 0;
  border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;
}
.total-hint { font-size: 13px; color: #64748b; }
.custom-pagination-container {
  display: flex;
  align-items: center;
  gap: 12px;
}
.limit-select {
  width: 64px !important;
}
.limit-select :deep(.el-input__wrapper) {
  border-radius: 6px;
  background: #ffffff !important;
}
.custom-pagination-numeric :deep(.el-pager li) { border-radius: 6px; min-width: 30px; height: 30px; line-height: 30px; font-weight: 500; }
.custom-pagination-numeric :deep(.el-pager li.is-active) { background: #4f46e5 !important; color: #fff !important; }
</style>
