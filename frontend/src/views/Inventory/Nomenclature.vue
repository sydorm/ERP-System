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
          <el-button type="primary" :icon="Plus" @click="goToCreate" class="btn-primary">
            Створити товар
          </el-button>
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
              </el-image>
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
        <el-table :data="products" style="width: 100%" size="small" @row-click="handleEdit" row-class-name="product-row">
          <el-table-column width="60">
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
import { ref, onMounted, onActivated, computed, watch } from 'vue'
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
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
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

onActivated(() => {
  if (products.value.length > 0) {
    fetchStatistics()
    fetchProducts()
  }
})

// Refresh when category changes might happen from somewhere else
watch(filterCategory, () => {
    fetchProducts()
})
</script>

<style scoped>
/* ===== PAGE ===== */
.page-container {
  padding: 0;
  background: #f4f5f9;
  min-height: 100vh;
  box-sizing: border-box;
}

/* ===== FIXED TOP AREA ===== */
.sticky-header-wrapper {
  position: sticky;
  top: -20px;  /* offset to compensate for global view-container padding */
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ===== HEADER ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.3px;
}
.breadcrumb { margin-top: 2px; }
.header-actions { display: flex; gap: 10px; }

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 9px;
  font-weight: 600;
  padding: 8px 16px;
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  transition: box-shadow 0.2s, transform 0.15s;
}
.btn-primary:hover {
  box-shadow: 0 6px 20px rgba(99,102,241,0.45);
  transform: translateY(-1px);
}

/* ===== STAT CARDS ===== */
.stats-container {
  margin-bottom: 12px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 0;
}
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover {
  box-shadow: 0 4px 12px rgba(99,102,241,0.08); 
  transform: translateY(-1px); 
}
.stat-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.total .stat-icon { background: #ede9fe; color: #6366f1; }
.in-stock .stat-icon { background: #d1fae5; color: #10b981; }
.low-stock .stat-icon { background: #fef3c7; color: #f59e0b; }
.out-of-stock .stat-icon { background: #fee2e2; color: #ef4444; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value { font-size: 18px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.stat-label { font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

.stat-dot {
  position: absolute; top: 10px; right: 10px;
  width: 6px; height: 6px; border-radius: 50%;
}
.total .stat-dot { background: #6366f1; }
.in-stock .stat-dot { background: #10b981; }
.low-stock .stat-dot { background: #f59e0b; }
.out-of-stock .stat-dot { background: #ef4444; }

.text-warning { color: #f59e0b; }
.text-danger { color: #ef4444; }
.text-success { color: #10b981; }

/* ===== FILTER BAR ===== */
.filters-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0px;
  background: transparent;
  padding-bottom: 0px;
}

.search-input {
  flex: 1;
  max-width: 320px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  background: #fff;
  height: 28px;
}

.search-input :deep(.el-input__inner) {
  font-size: 12px;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}

.category-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  padding: 4px 10px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chip:hover { border-color: #6366f1; color: #6366f1; }
.chip.active {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
  box-shadow: 0 2px 8px rgba(99,102,241,0.28);
}

.view-toggle {
  margin-left: auto;
}

.view-toggle :deep(.el-radio-button__inner) {
  padding: 5px 12px;
  font-size: 14px;
}

/* ===== CONTENT AREA ===== */
.content-container {
  padding: 20px;
}

.product-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  margin-bottom: 16px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
  border-color: #cbd5e1;
}

.product-image-container {
  position: relative;
  height: 140px; /* Reduced to make cards denser */
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
  top: 8px; right: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-actions-overlay { opacity: 1; }

.product-details { padding: 12px; }

.category-tag {
  font-size: 9px; font-weight: 700;
  color: #64748b; text-transform: uppercase;
  margin-bottom: 4px;
}

.product-title {
  margin: 0 0 8px 0;
  font-size: 13px; font-weight: 600;
  color: #1e293b; cursor: pointer;
  line-height: 1.3; height: 34px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.price-value { font-size: 14px; font-weight: 700; color: #1e293b; }
.price-unit { font-size: 12px; color: #64748b; margin-left: 2px; }

.stock-status { margin-bottom: 10px; }
.stock-info { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
.stock-label { color: #64748b; font-weight: 500; }
.stock-value { font-weight: 700; }

/* List View Styles */
.list-image { width: 32px; height: 32px; border-radius: 6px; }
.list-image-placeholder {
  width: 32px; height: 32px;
  background: #f4f4f4; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: #d1d1d1;
}

.list-view-container :deep(th.el-table__cell) {
  background: #f8fafc !important;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 6px 8px !important;
}

.list-view-container :deep(td.el-table__cell) {
  padding: 4px 8px !important;
  font-size: 12px;
}

.list-view-container :deep(.product-row) { cursor: pointer; transition: background 0.15s; }
.list-view-container :deep(.product-row:hover > td) { background: #f8fafc !important; }

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
