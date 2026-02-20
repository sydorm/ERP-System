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
          <el-radio-button label="all">Всі</el-radio-button>
          <el-radio-button label="customer">Клієнти</el-radio-button>
          <el-radio-button label="supplier">Постачальники</el-radio-button>
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

    <!-- Post-MVP: Drawer/Dialog for Create/Edit -->
    <el-drawer
      v-model="drawerVisible"
      :title="editForm.id ? 'Редагування контрагента' : 'Новий контрагент'"
      size="500px"
    >
      <el-form :model="editForm" label-position="top" class="edit-form">
        <el-form-item label="Назва (коротка)" required>
          <el-input v-model="editForm.name" placeholder="Наприклад: ТОВ 'Атлант'" />
        </el-form-item>
        <el-form-item label="Юридична назва">
          <el-input v-model="editForm.legal_name" placeholder="Повна юридична назва" />
        </el-form-item>
        <el-form-item label="ЄДРПОУ / ІПН">
          <el-input v-model="editForm.tax_id" placeholder="8 або 10 цифр" />
        </el-form-item>
        
        <div class="form-row">
          <el-form-item label="Це клієнт?">
            <el-switch v-model="editForm.is_customer" />
          </el-form-item>
          <el-form-item label="Це постачальник?">
            <el-switch v-model="editForm.is_supplier" />
          </el-form-item>
        </div>

        <el-divider>Контакти</el-divider>
        
        <el-form-item label="Телефон">
          <el-input v-model="editForm.phone" placeholder="+380..." />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="editForm.email" placeholder="example@mail.com" />
        </el-form-item>
        <el-form-item label="Адреса">
          <el-input v-model="editForm.address" type="textarea" placeholder="Юридична або фактична адреса" />
        </el-form-item>

        <div class="drawer-actions">
          <el-button @click="drawerVisible = false">Скасувати</el-button>
          <el-button type="primary" :loading="saving" @click="saveCounterparty">Зберегти</el-button>
        </div>
      </el-form>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// State
const loading = ref(false)
const saving = ref(false)
const counterparties = ref([])
const total = ref(0)
const currentPage = ref(1)
const limit = ref(15)

const searchQuery = ref('')
const filterType = ref('all')

const drawerVisible = ref(false)
const editForm = reactive({
  id: null,
  name: '',
  legal_name: '',
  tax_id: '',
  is_customer: true,
  is_supplier: false,
  phone: '',
  email: '',
  address: '',
  is_active: true
})

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
  Object.assign(editForm, {
    id: null,
    name: '',
    legal_name: '',
    tax_id: '',
    is_customer: true,
    is_supplier: false,
    phone: '',
    email: '',
    address: '',
    is_active: true
  })
  drawerVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(editForm, row)
  drawerVisible.value = true
}

const saveCounterparty = async () => {
  if (!editForm.name) {
    ElMessage.warning('Вкажіть назву контрагента')
    return
  }
  
  saving.value = true
  try {
    if (editForm.id) {
      await api.put(`/api/v1/counterparties/${editForm.id}`, editForm)
      ElMessage.success('Дані оновлено')
    } else {
      await api.post('/api/v1/counterparties', editForm)
      ElMessage.success('Контрагента додано')
    }
    drawerVisible.value = false
    fetchCounterparties()
  } catch (error) {
    ElMessage.error('Помилка збереження')
  } finally {
    saving.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити контрагента ${row.name}?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/counterparties/${row.id}`)
      ElMessage.success('Видалено')
      fetchCounterparties()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

onMounted(fetchCounterparties)
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

.drawer-actions {
  margin-top: 40px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-row {
  display: flex;
  gap: 24px;
}

.m-1 {
  margin: 2px;
}
</style>
