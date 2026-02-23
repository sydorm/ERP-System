<template>
  <div class="page-container">
    <!-- === PAGE HEADER === -->
    <div class="page-header">
      <div class="header-left">
        <h2>Замовлення клієнтів</h2>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Продажі</el-breadcrumb-item>
          <el-breadcrumb-item>Замовлення</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-create">
          Створити замовлення
        </el-button>
      </div>
    </div>

    <!-- === UNIFIED CONTENT CARD === -->
    <div class="content-card">
      <!-- Filters bar inside card -->
      <div class="filters-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук замовлення..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <el-select v-model="filterStatus" placeholder="Будь-який статус" clearable @change="fetchOrders" class="status-select">
          <el-option label="Чернетка" value="draft" />
          <el-option label="Підтверджено" value="confirmed" />
          <el-option label="Відвантажено" value="shipped" />
          <el-option label="Завершено" value="completed" />
          <el-option label="Скасовано" value="cancelled" />
        </el-select>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="orders"
        style="width: 100%"
        class="orders-table"
      >
        <el-table-column prop="order_number" label="№ Замовлення" width="160" sortable />
        <el-table-column prop="order_date" label="Дата" width="120">
          <template #default="scope">{{ formatDate(scope.row.order_date) }}</template>
        </el-table-column>
        <el-table-column label="Клієнт" min-width="200">
          <template #default="scope">
            {{ getCounterpartyName(scope.row.counterparty_id) || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="Сума" width="160" align="right">
          <template #default="scope">{{ formatCurrency(scope.row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small" effect="plain" class="status-tag">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="90" align="right">
          <template #default="scope">
            <div class="row-actions">
              <el-button link :icon="Edit" @click="handleEdit(scope.row)" class="action-btn edit-btn" />
              <el-button link :icon="Delete" @click="handleDelete(scope.row)" class="action-btn delete-btn" />
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
          class="custom-pagination"
        />
      </div>
    </div>
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
const orders = ref([])
const counterparties = ref({}) // Cache for names
const total = ref(0)
const currentPage = ref(1)
const limit = ref(15)

const searchQuery = ref('')
const filterStatus = ref('')
const orderStatuses = ref([])

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
    
    // Fetch order statuses for labels/colors
    if (orderStatuses.value.length === 0) {
      const statusRes = await api.get('/api/v1/dictionaries/ORDER_STATUS')
      orderStatuses.value = statusRes.data
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
  const s = orderStatuses.value.find(item => item.code === status)
  return s?.color || 'info'
}

const getStatusLabel = (status) => {
  const s = orderStatuses.value.find(item => item.code === status)
  return s?.name || status
}

onMounted(fetchOrders)
onActivated(fetchOrders)
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f4f6f8;
  min-height: calc(100vh - 64px);
  box-sizing: border-box;
}

/* === PAGE HEADER === */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 2px;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}

.breadcrumb {
  margin-top: 4px;
}

.btn-create {
  background: #2563eb;
  border: none;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
  border-radius: 8px;
  padding: 8px 18px;
  height: 38px;
}

.btn-create:hover {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

/* === UNIFIED CARD === */
.content-card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f3f6;
  overflow: hidden;
}

/* === FILTERS BAR === */
.filters-bar {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  align-items: center;
}

.search-input {
  width: 280px;
}

.search-input :deep(.el-input__wrapper),
.status-select :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input :deep(.el-input__wrapper:hover),
.status-select :deep(.el-select__wrapper:hover) {
  border-color: #94a3b8;
}

.search-input :deep(.el-input__wrapper.is-focus),
.status-select :deep(.el-select__wrapper.is-focused) {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
  background: #fff;
}

.status-select {
  width: 180px;
}

/* === TABLE STYLES === */
.orders-table :deep(th.el-table__cell) {
  background: #f8fafc !important;
  color: #7c8db0;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 1px solid #eef2f7 !important;
  padding: 10px 12px;
}

.orders-table :deep(td.el-table__cell) {
  border-bottom: 1px solid #f1f5f9 !important;
  border-right: none !important;
  padding: 10px 12px;
  color: #1e293b;
  font-size: 14px;
}

.orders-table :deep(.el-table__body tr:hover > td) {
  background-color: #f8fafc !important;
}

.orders-table :deep(.el-table__inner-wrapper::before) {
  display: none; /* remove bottom border line */
}

/* Status tag */
.status-tag {
  border-radius: 20px;
  font-weight: 500;
  font-size: 12px;
}

/* Row action buttons */
.row-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.orders-table :deep(tr:hover) .row-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px;
  border-radius: 6px;
}

.edit-btn {
  color: #475569;
}

.edit-btn:hover {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.08);
}

.delete-btn {
  color: #475569;
}

.delete-btn:hover {
  color: #dc2626;
  background: rgba(220, 38, 38, 0.08);
}

/* === PAGINATION === */
.pagination-footer {
  display: flex;
  justify-content: flex-end;
  padding: 14px 20px;
  border-top: 1px solid #f1f5f9;
}

.custom-pagination :deep(.el-pager li) {
  border-radius: 6px;
  min-width: 32px;
  height: 32px;
  line-height: 32px;
  font-size: 13px;
}

.custom-pagination :deep(.btn-prev),
.custom-pagination :deep(.btn-next) {
  border-radius: 6px;
}

@media (max-width: 640px) {
  .page-container { padding: 12px; }
  .filters-bar { flex-wrap: wrap; }
  .search-input { width: 100%; }
  .status-select { width: 100%; }
  .header-left h2 { font-size: 18px; }
}
</style>
