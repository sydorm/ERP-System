<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Номенклатура</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
        <el-breadcrumb-item>Склад</el-breadcrumb-item>
        <el-breadcrumb-item>Номенклатура</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-container class="view-layout">
      <!-- Left Sidebar: Categories Filter -->
      <el-aside width="240px" class="view-sidebar">
        <div class="sidebar-header">
             <span class="sidebar-title">Категорії</span>
             <el-button link type="primary" size="small" @click="fetchDictionaries">
                <el-icon><Refresh /></el-icon>
             </el-button>
        </div>
        <el-menu
          :default-active="filterCategory"
          class="category-menu"
          @select="handleCategorySelect"
        >
          <el-menu-item index="">
            <el-icon><Menu /></el-icon>
            <span>Всі товари</span>
          </el-menu-item>
          <el-menu-item 
            v-for="cat in categoryOptions" 
            :key="cat.code" 
            :index="cat.code"
          >
            <el-icon><Folder /></el-icon>
            <span>{{ cat.name }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- Main Content -->
      <el-main class="view-content">
        <el-card shadow="never" class="content-card">
          <!-- Toolbar -->
          <div class="toolbar">
             <div class="toolbar-left">
                <el-input
                  v-model="searchQuery"
                  placeholder="Пошук (Назва, Артикул)..."
                  prefix-icon="Search"
                  class="search-input"
                  clearable
                  @input="handleSearch"
                />
             </div>
             <div class="toolbar-right">
                <el-button type="primary" :icon="Plus" @click="goToCreate">
                    Додати товар
                </el-button>
             </div>
          </div>

          <!-- Data Table -->
          <el-table 
            :data="products" 
            stripe 
            style="width: 100%" 
            v-loading="loading"
            class="data-table"
           >
            <el-table-column width="60" label="">
                <template #default="scope">
                    <el-image 
                        style="width: 32px; height: 32px; border-radius: 4px"
                        :src="scope.row.image_url" 
                        :preview-src-list="scope.row.image_url ? [scope.row.image_url] : []"
                        fit="cover"
                    >
                        <template #error>
                            <div class="image-placeholder">
                                <el-icon><Picture /></el-icon>
                            </div>
                        </template>
                    </el-image>
                </template>
            </el-table-column>
            
            <el-table-column prop="sku" label="Артикул" width="120">
                <template #default="scope">
                    <span class="font-bold">{{ scope.row.sku }}</span>
                </template>
            </el-table-column>
            
            <el-table-column prop="name" label="Назва товару" min-width="200">
                 <template #default="scope">
                    <span class="product-name" @click="handleEdit(scope.row)">{{ scope.row.name }}</span>
                </template>
            </el-table-column>
            
            <el-table-column prop="unit_of_measure" label="Од." width="80" align="center" />
            
            <el-table-column prop="price" label="Ціна" width="120" align="right">
                <template #default="scope">
                    {{ formatCurrency(scope.row.price, scope.row.currency) }}
                </template>
            </el-table-column>

            <el-table-column label="Залишок" width="100" align="center">
                <template #default="scope">
                     <span class="text-gray">-</span> 
                </template>
            </el-table-column>

            <el-table-column label="Дії" width="100" align="right">
              <template #default="scope">
                <el-button link type="primary" :icon="Edit" @click="handleEdit(scope.row)"></el-button>
                <el-button link type="danger" :icon="Delete" @click="handleDelete(scope.row)"></el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="total"
              :page-size="limit"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Delete, Picture, Menu, Folder, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// State
const loading = ref(false)
const products = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(20)

const searchQuery = ref('')
const filterCategory = ref('')

// Dictionaries
const uomOptions = ref([])
const categoryOptions = ref([])
const currencyOptions = ref([])

const router = useRouter()

const fetchDictionaries = async () => {
    try {
        const catRes = await api.get('/api/v1/dictionaries/PRODUCT_CATEGORY')
        categoryOptions.value = catRes.data
        const uomRes = await api.get('/api/v1/dictionaries/UOM')
        uomOptions.value = uomRes.data
        const currencyRes = await api.get('/api/v1/dictionaries/CURRENCY')
        currencyOptions.value = currencyRes.data
    } catch (error) {
        console.error('Failed to load dictionaries', error)
    }
}

const fetchProducts = async () => {
    loading.value = true
    try {
        const params = {
            skip: skip.value,
            limit: limit.value,
            search: searchQuery.value || undefined,
            category: filterCategory.value || undefined
        }
        const response = await api.get('/api/v1/products', { params })
        products.value = response.data
        // Assume rough total for now as API response is simple list
        total.value = products.value.length < limit.value ? products.value.length + skip.value : 100 
    } catch (error) {
        ElMessage.error('Помилка завантаження товарів')
    } finally {
        loading.value = false
    }
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
            await api.delete(`/api/v1/products/${row.id}`)
            ElMessage.success('Товар видалено')
            fetchProducts()
        } catch (error) {
            ElMessage.error('Помилка видалення')
        }
    })
}

const goToCreate = () => {
    router.push('/inventory/nomenclature/new')
}
 
const handleEdit = (row) => {
    router.push(`/inventory/nomenclature/${row.id}`)
}

// UI Handlers
const handleCategorySelect = (index) => {
    filterCategory.value = index
    skip.value = 0
    fetchProducts()
}

const handleSearch = () => {
    skip.value = 0
    setTimeout(() => {
        fetchProducts()
    }, 500)
}

const handlePageChange = (page) => {
    skip.value = (page - 1) * limit.value
    fetchProducts()
}

const formatCurrency = (value, currency) => {
    try {
        return new Intl.NumberFormat('uk-UA', { 
            style: 'currency', 
            currency: currency && currency.length === 3 ? currency.toUpperCase() : 'UAH' 
        }).format(value)
    } catch (e) {
        console.warn('Currency formatting error:', e)
        return `${value} ${currency || ''}`
    }
}

onMounted(() => {
    fetchDictionaries()
    fetchProducts()
})
</script>

<style scoped>
.page-container {
    height: calc(100vh - 84px);
    display: flex;
    flex-direction: column;
}

.page-header {
    margin-bottom: 20px;
    flex-shrink: 0;
}
.page-header h2 {
    margin: 0 0 10px 0;
    color: #303133;
}

.view-layout {
    flex: 1;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    overflow: hidden;
}

@media (max-width: 768px) {
    .view-layout {
        flex-direction: column;
        overflow-y: auto;
    }
    .view-sidebar {
        width: 100% !important;
        height: auto;
        border-right: none !important;
        border-bottom: 1px solid var(--el-border-color-light);
    }
}

.view-sidebar {
    background-color: var(--el-bg-color-page);
    border-right: 1px solid var(--el-border-color-light);
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 16px 20px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    border-bottom: 1px solid var(--el-border-color-lighter);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.category-menu {
    border-right: none;
    background: transparent;
    flex: 1;
    overflow-y: auto;
}

.view-content {
    padding: 0;
    background-color: var(--el-bg-color);
    display: flex;
    flex-direction: column;
}

@media (max-width: 640px) {
    .toolbar {
        flex-direction: column;
        gap: 12px;
    }
    .search-input {
        width: 100% !important;
    }
    .toolbar-right {
        width: 100%;
    }
    .toolbar-right .el-button {
        width: 100%;
    }
}

.content-card {
    border: none;
    box-shadow: none !important;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.content-card :deep(.el-card__body) {
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.search-input {
    width: 300px;
}

.data-table {
    flex: 1;
}

.product-name {
    font-weight: 500;
    color: #409eff;
    cursor: pointer;
}
.product-name:hover {
    text-decoration: underline;
}

.font-bold {
    font-weight: 600;
}

.text-gray {
    color: #909399;
}

.image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f5f7fa;
    color: #909399;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style>
