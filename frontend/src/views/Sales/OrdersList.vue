<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Замовлення клієнтів</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Продажі</el-breadcrumb-item>
          <el-breadcrumb-item>Замовлення</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-primary">
          Створити замовлення
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="Номер замовлення..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
      </div>
      <div class="status-filter">
        <el-select v-model="filterStatus" placeholder="Статус" clearable @change="fetchOrders">
          <el-option label="Чернетка" value="draft" />
          <el-option label="Підтверджено" value="confirmed" />
          <el-option label="Відвантажено" value="shipped" />
          <el-option label="Завершено" value="completed" />
          <el-option label="Скасовано" value="cancelled" />
        </el-select>
      </div>
    </div>

    <!-- Data Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        v-loading="loading" 
        :data="orders" 
        stripe 
        style="width: 100%"
        class="custom-table"
      >
        <el-table-column prop="order_number" label="№ Замовлення" width="150" sortable />
        <el-table-column prop="order_date" label="Дата" width="120">
          <template #default="scope">{{ formatDate(scope.row.order_date) }}</template>
        </el-table-column>
        
        <el-table-column label="Клієнт" min-width="200">
          <template #default="scope">
            {{ getCounterpartyName(scope.row.counterparty_id) || 'Завантаження...' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="total_amount" label="Сума" width="150" align="right">
          <template #default="scope">{{ formatCurrency(scope.row.total_amount) }}</template>
        </el-table-column>
        
        <el-table-column prop="status" label="Статус" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small" effect="dark">
              {{ getStatusLabel(scope.row.status) }}
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

      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          background
          layout="total, prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const orders = ref([])
const counterparties = ref({}) // Cache for names
const total = ref(0)
const currentPage = ref(1)
const limit = ref(15)

const searchQuery = ref('')
const filterStatus = ref('')

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * limit.value,
      limit: limit.value,
      search: searchQuery.value || undefined,
      status: filterStatus.value || undefined
    }
    const res = await api.get('/api/v1/orders', { params })
    orders.value = res.data
    total.value = orders.value.length < limit.value ? orders.value.length : 100
    
    // Fetch unique counterparty names if not in cache
    const cpIds = [...new Set(orders.value.map(o => o.counterparty_id))].filter(id => !counterparties.value[id])
    for (const id of cpIds) {
      try {
        const cpRes = await api.get(`/api/v1/counterparties/${id}`)
        counterparties.value[id] = cpRes.data.name
      } catch (e) {
        counterparties.value[id] = 'Н/Д'
      }
    }
  } catch (error) {
    ElMessage.error('Помилка завантаження замовлень')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchOrders()
}

let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchOrders()
  }, 300)
}

const handleCreate = () => router.push('/sales/orders/new')
const handleEdit = (row) => router.push(`/sales/orders/${row.id}`)

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити замовлення ${row.order_number}?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/orders/${row.id}`)
      ElMessage.success('Видалено')
      fetchOrders()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

// Helpers
const formatDate = (dateStr) => dateStr ? new Date(dateStr).toLocaleDateString('uk-UA') : ''
const getCounterpartyName = (id) => counterparties.value[id]
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val)

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    confirmed: 'primary',
    shipped: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    draft: 'Чернетка',
    confirmed: 'Підтверджено',
    shipped: 'Відвантажено',
    completed: 'Завершено',
    cancelled: 'Скасовано'
  }
  return map[status] || status
}

onMounted(fetchOrders)
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
  display: flex;
  gap: 16px;
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

.pagination-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
