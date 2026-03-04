<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Контрагенти</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Продажі</el-breadcrumb-item>
          <el-breadcrumb-item>Контрагенти</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleCreate" class="btn-primary">
          Додати контрагента
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук за назвою або ЄДРПОУ..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
      </div>
      <div class="type-filter">
        <el-radio-group v-model="filterType" @change="fetchCounterparties">
          <el-radio-button value="all">Всі</el-radio-button>
          <el-radio-button value="customer">Клієнти</el-radio-button>
          <el-radio-button value="supplier">Постачальники</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- Data Table -->
    <el-card shadow="never" class="content-card">
      <el-table 
        v-loading="loading" 
        :data="counterparties" 
        stripe 
        style="width: 100%"
        class="custom-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="name" label="Назва" min-width="200">
          <template #default="scope">
            <div class="counterparty-info">
              <span class="cp-name">{{ scope.row.name }}</span>
              <span class="cp-legal">{{ scope.row.legal_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="tax_id" label="ЄДРПОУ/ІПН" width="120" />
        
        <el-table-column label="Тип" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.is_customer" type="success" size="small" class="m-1">Клієнт</el-tag>
            <el-tag v-if="scope.row.is_supplier" type="warning" size="small" class="m-1">Постачальник</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="phone" label="Телефон" width="150" />
        <el-table-column prop="email" label="Email" min-width="150" />
        
        <el-table-column label="Дії" width="100" align="right">
          <template #default="scope">
            <el-button link type="primary" :icon="Edit" @click.stop="handleEdit(scope.row)" />
            <el-button link type="danger" :icon="Delete" @click.stop="handleDelete(scope.row)" />
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
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const counterparties = ref([])
const total = ref(0)
const currentPage = ref(1)
const limit = ref(15)

const searchQuery = ref('')
const filterType = ref('all')

const fetchCounterparties = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * limit.value,
      limit: limit.value,
      search: searchQuery.value || undefined,
      is_customer: filterType.value === 'customer' ? true : (filterType.value === 'all' ? undefined : false),
      is_supplier: filterType.value === 'supplier' ? true : (filterType.value === 'all' ? undefined : false)
    }
    const res = await api.get('/api/v1/counterparties', { params })
    counterparties.value = res.data
    // Mock total for now
    total.value = counterparties.value.length < limit.value ? counterparties.value.length : 100
  } catch (error) {
    ElMessage.error('Помилка завантаження контрагентів')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchCounterparties()
}

let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchCounterparties()
  }, 300)
}

const handleCreate = () => {
  router.push('/sales/counterparties/new')
}

const handleEdit = (row) => {
  router.push(`/sales/counterparties/${row.id}`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити ${row.name}?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/counterparties/${row.id}`)
      ElMessage.success('Контрагента видалено')
      fetchCounterparties()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  })
}

const handleRowClick = (row) => {
  router.push(`/sales/counterparties/${row.id}`)
}

onMounted(fetchCounterparties)
onActivated(() => {
  if (counterparties.value.length > 0) {
    fetchCounterparties()
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.search-input {
  width: 350px;
}

.content-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.counterparty-info {
  display: flex;
  flex-direction: column;
}

.cp-name {
  font-weight: 600;
  color: #1a1d1f;
}

.cp-legal {
  font-size: 12px;
  color: #6f767e;
}

.pagination-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.m-1 {
  margin: 2px;
}

.custom-table {
  cursor: pointer;
}
</style>
