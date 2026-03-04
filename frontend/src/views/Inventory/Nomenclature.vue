<template>
  <div class="page-container">
    <div class="sticky-header-wrapper">
      <div class="page-header">
        <div class="header-left">
          <h2>Номенклатура</h2>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
            <el-breadcrumb-item>Склад</el-breadcrumb-item>
            <el-breadcrumb-item>Номенклатура</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- Buttons removed per user request: nomenclature will be added via documents -->
        </div>
      </div>

      <!-- Stats Bar -->
      <div class="stats-container">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="stat-card total">
              <div class="stat-icon"><Box /></div>
              <div class="stat-info">
                <span class="stat-label">Всього товарів</span>
                <span class="stat-value">{{ stats.total_products }}</span>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card in-stock">
              <div class="stat-icon"><Coordinate /></div>
              <div class="stat-info">
                <span class="stat-label">В наявності</span>
                <span class="stat-value">{{ stats.in_stock }}</span>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card low-stock">
              <div class="stat-icon"><Warning /></div>
              <div class="stat-info">
                <span class="stat-label">Закінчуються</span>
                <span class="stat-value text-warning">{{ stats.low_stock }}</span>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card out-of-stock">
              <div class="stat-icon"><CircleClose /></div>
              <div class="stat-info">
                <span class="stat-label">Немає</span>
                <span class="stat-value text-danger">{{ stats.out_of_stock }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Filters & Search -->
      <div class="filters-toolbar">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="Пошук товарів..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            class="search-input"
          />
        </div>
        <div class="category-chips">
          <div 
            class="chip" 
            :class="{ active: filterCategory === '' }" 
            @click="handleCategorySelect('')"
          >
            Всі
          </div>
          <div 
            v-for="cat in categoryOptions" 
            :key="cat.code" 
            class="chip" 
            :class="{ active: filterCategory === cat.code }"
            @click="handleCategorySelect(cat.code)"
          >
            {{ cat.name }}
          </div>
        </div>
        <div class="view-toggle">
          <el-radio-group v-model="viewMode" size="large">
            <el-radio-button value="grid">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
            <el-radio-button value="list">
              <el-icon><Fold /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>

    <!-- Product Grid/List -->
    <div class="content-container" v-loading="loading">
      <div v-if="products.length === 0 && !loading" class="empty-state">
        <el-empty description="Товарів не знайдено" />
      </div>
      
      <!-- Grid View -->
      <el-row v-if="viewMode === 'grid'" :gutter="20">
        <el-col 
          v-for="product in products" 
          :key="product.id" 
          :xs="24" :sm="12" :md="8" :lg="6" :xl="4"
        >
          <el-card shadow="hover" class="product-card" :body-style="{ padding: '0px' }">
            <div class="product-image-container">
              <el-image 
                :src="product.image_url" 
                fit="cover" 
                class="product-image"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon :size="40"><Picture /></el-icon>
                  </div>
                </template>
              <div class="product-actions-overlay">
                <el-button circle :icon="Edit" @click="handleEdit(product)" />
              </div>
            </div>
            
            <div class="product-details">
              <div class="category-tag">{{ getCategoryName(product.category) }}</div>
              <h3 class="product-title" @click="handleEdit(product)">{{ product.name }}</h3>
              
              <div class="product-price">
                <span class="price-value">{{ formatCurrency(product.price, product.currency) }}</span>
                <span class="price-unit">/ {{ product.unit_of_measure }}</span>
              </div>

              <div class="stock-status">
                <div class="stock-info">
                  <span class="stock-label">Запас:</span>
                  <span class="stock-value" :class="getStockClass(product.stock_balance)">
                    {{ product.stock_balance }} {{ product.unit_of_measure }}
                  </span>
                </div>
                <el-progress 
                  :percentage="getStockPercentage(product.stock_balance)" 
                  :status="getStockProgressStatus(product.stock_balance)"
                  :show-text="false"
                  class="stock-progress"
                />
              </div>

              <!-- Quick actions removed per user request: stock movements will be document-based -->
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- List View -->
      <div v-else class="list-view-container">
        <el-table :data="products" style="width: 100%" @row-click="handleEdit">
          <el-table-column width="80">
            <template #default="scope">
              <el-image :src="scope.row.image_url" class="list-image">
                <template #error>
                  <div class="list-image-placeholder"><Picture /></div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column prop="sku" label="Артикул" width="120" />
          <el-table-column prop="name" label="Назва" min-width="200" />
          <el-table-column label="Категорія" width="180">
            <template #default="scope">
              {{ getCategoryName(scope.row.category) }}
            </template>
          </el-table-column>
          <el-table-column label="Запас" width="150" align="right">
            <template #default="scope">
              <span :class="getStockClass(scope.row.stock_balance)" style="font-weight: bold">
                {{ scope.row.stock_balance }} {{ scope.row.unit_of_measure }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Ціна" width="150" align="right">
            <template #default="scope">
              {{ formatCurrency(scope.row.price, scope.row.currency) }}
            </template>
          </el-table-column>
          <el-table-column width="100" align="center">
            <template #default="scope">
              <el-button :icon="Edit" circle @click.stop="handleEdit(scope.row)" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Pagination -->
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Search, Edit, Delete, Picture, 
  Box, Coordinate, Warning, CircleClose,
  Printer, Minus, Grid, Fold
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const products = ref([])
const stats = ref({
  total_products: 0,
  in_stock: 0,
  low_stock: 0,
  out_of_stock: 0
})
const total = ref(0)
const skip = ref(0)
const limit = ref(12)
const currentPage = ref(1)

const searchQuery = ref('')
const filterCategory = ref('')
const viewMode = ref('grid') // 'grid' or 'list'

// Dictionaries
const categoryOptions = ref([])

const fetchDictionaries = async () => {
  try {
    const catRes = await api.get('/api/v1/dictionaries/PRODUCT_CATEGORY')
    categoryOptions.value = catRes.data
  } catch (error) {
    console.error('Failed to load dictionaries', error)
  }
}

const fetchStatistics = async () => {
  try {
    const res = await api.get('/api/v1/products/statistics')
    stats.value = res.data
  } catch (error) {
    console.error('Failed to fetch statistics', error)
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
    // Assuming API can provide count in headers or another way, 
    // for now we use total_products from stats if no filters
    if (!searchQuery.value && !filterCategory.value) {
      total.value = stats.value.total_products
    } else {
      total.value = products.value.length < limit.value ? skip.value + products.value.length : skip.value + limit.value + 1
    }
  } catch (error) {
    ElMessage.error('Помилка завантаження товарів')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  skip.value = (page - 1) * limit.value
  fetchProducts()
}

const handleCategorySelect = (code) => {
  filterCategory.value = code
  skip.value = 0
  currentPage.value = 1
  fetchProducts()
}

let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    skip.value = 0
    currentPage.value = 1
    fetchProducts()
  }, 300)
}

const goToCreate = () => router.push('/inventory/nomenclature/new')
const handleEdit = (row) => router.push(`/inventory/nomenclature/${row.id}`)

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
      fetchStatistics()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

const handleQuickAdjust = async (product, delta) => {
  // In a real system, this would create a StockAdjustment document
  // For now, it's a placeholder message
  ElMessage.info(`Можливість швидкої корекції (${delta}) в розробці. Створіть накладну.`)
}

// Helpers
const getCategoryName = (code) => {
  const cat = categoryOptions.value.find(c => c.code === code)
  return cat ? cat.name : 'Без категорії'
}

const formatCurrency = (value, currency) => {
  return new Intl.NumberFormat('uk-UA', { 
    style: 'currency', 
    currency: currency || 'UAH',
    maximumFractionDigits: 0
  }).format(value)
}

const getStockClass = (val) => {
  if (val > 5) return 'text-success'
  if (val > 0) return 'text-warning'
  return 'text-danger'
}

const getStockPercentage = (val) => {
  // Mock target of 30 for visualization
  const target = 30
  return Math.min(Math.round((val / target) * 100), 100)
}

const getStockProgressStatus = (val) => {
  if (val > 5) return 'success'
  if (val > 0) return 'warning'
  return 'exception'
}

onMounted(() => {
  fetchDictionaries()
  fetchStatistics()
  fetchProducts()
})

// Refresh when category changes might happen from somewhere else
watch(filterCategory, () => {
    fetchProducts()
})
</script>

<style scoped>
.page-container {
  padding: 0;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.sticky-header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #f8f9fa;
  padding: 24px 24px 0 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1d1f;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: #2a85ff;
  border: none;
  font-weight: 600;
  padding: 10px 20px;
}

/* Stats */
.stats-container {
  margin-bottom: 20px;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.total .stat-icon { background: rgba(42, 133, 255, 0.1); color: #2a85ff; }
.in-stock .stat-icon { background: rgba(122, 212, 114, 0.1); color: #7ad472; }
.low-stock .stat-icon { background: rgba(255, 188, 51, 0.1); color: #ffbc33; }
.out-of-stock .stat-icon { background: rgba(255, 107, 107, 0.1); color: #ff6b6b; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 12px;
  color: #6f767e;
  font-weight: 500;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #1a1d1f;
}

.text-warning { color: #ffbc33; }
.text-danger { color: #ff6b6b; }
.text-success { color: #7ad472; }

/* Filters */
.filters-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid #efefef;
  background: #f8f9fa;
}

.search-input {
  width: 260px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}

.category-chips {
  flex: 1;
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.chip {
  padding: 8px 16px;
  background: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #6f767e;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.chip:hover { background: #efefef; }
.chip.active { background: #1a1d1f; color: #fff; }

.view-toggle {
  margin-left: auto;
}

/* Content Area */
.content-container {
  padding: 24px;
}

.product-card {
  border-radius: 12px;
  overflow: hidden;
  border: none;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08) !important;
}

.product-image-container {
  position: relative;
  height: 180px;
  background: #f4f4f4;
}

.product-image { width: 100%; height: 100%; }

.image-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #d1d1d1;
}

.product-actions-overlay {
  position: absolute;
  top: 12px; right: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-actions-overlay { opacity: 1; }

.product-details { padding: 16px; }

.category-tag {
  font-size: 11px; font-weight: 700;
  color: #2a85ff; text-transform: uppercase;
  margin-bottom: 6px;
}

.product-title {
  margin: 0 0 12px 0;
  font-size: 16px; font-weight: 700;
  color: #1a1d1f; cursor: pointer;
  line-height: 1.4; height: 44px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.price-value { font-size: 18px; font-weight: 700; color: #1a1d1f; }
.price-unit { font-size: 14px; color: #6f767e; margin-left: 4px; }

.stock-status { margin-bottom: 16px; }
.stock-info { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
.stock-label { color: #6f767e; font-weight: 500; }
.stock-value { font-weight: 700; }

/* List View Styles */
.list-image { width: 48px; height: 48px; border-radius: 8px; }
.list-image-placeholder {
  width: 48px; height: 48px;
  background: #f4f4f4; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #d1d1d1;
}

.pagination-footer {
  display: flex; justify-content: center;
  padding: 20px 0;
}

@media (max-width: 640px) {
  .sticky-header-wrapper { padding: 16px 16px 0 16px; }
  .filters-toolbar { gap: 12px; }
  .search-input { width: 100%; }
}
</style>
