<template>
  <div class="page-container">
    <!-- ===== FIXED HEADER ===== -->
    <div class="sticky-header-wrapper">
      <div class="page-header">
        <div class="header-left">
          <h2>Номенклатура</h2>
          <p class="page-subtitle">Керуйте вашими товарами та відстежуйте запаси</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="goToCreate" class="btn-create">
            + Створити товар
          </el-button>
        </div>
      </div>

      <!-- ===== STAT CARDS ===== -->
      <div class="stats-row">
        <div class="stat-card total">
          <div class="stat-icon"><el-icon><Box /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_products }}</span>
            <span class="stat-label">Всього товарів</span>
          </div>
          <div class="stat-badge" :style="{background:'rgba(99,102,241,0.1)',color:'#6366f1'}">+0%</div>
        </div>
        <div class="stat-card in-stock">
          <div class="stat-icon"><el-icon><Coordinate /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.in_stock }}</span>
            <span class="stat-label">В наявності</span>
          </div>
          <div class="stat-badge" :style="{background:'rgba(16,185,129,0.1)',color:'#10b981'}">{{ stats.in_stock > 0 ? stats.in_stock + '%' : '0%' }}</div>
        </div>
        <div class="stat-card low-stock">
          <div class="stat-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.low_stock }}</span>
            <span class="stat-label">Закінчуються</span>
          </div>
        </div>
        <div class="stat-card out-of-stock">
          <div class="stat-icon"><el-icon><CircleClose /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.out_of_stock }}</span>
            <span class="stat-label">Немає</span>
          </div>
          <div class="stat-badge negative" v-if="stats.out_of_stock > 0">+{{ stats.out_of_stock }}</div>
        </div>
      </div>

      <!-- ===== FILTERS TOOLBAR ===== -->
      <div class="filters-toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук товарів..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <div class="category-chips">
          <div class="chip" :class="{ active: filterCategory === '' }" @click="handleCategorySelect('')">
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
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="list"><el-icon><Fold /></el-icon></el-radio-button>
            <el-radio-button value="grid"><el-icon><Grid /></el-icon></el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>

    <!-- ===== CONTENT AREA ===== -->
    <div class="content-container">
      <!-- Grid View -->
      <el-row v-if="viewMode === 'grid'" :gutter="20" v-loading="loading">
        <el-col v-for="product in products" :key="product.id" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card class="product-card" shadow="hover">
            <div class="product-image-container">
              <el-image :src="product.image_url" fit="cover" class="product-image">
                <template #error>
                  <div class="image-placeholder"><el-icon :size="48"><Picture /></el-icon></div>
                </template>
              </el-image>
              <div class="product-actions-overlay">
                <el-button circle :icon="Edit" size="small" @click.stop="handleEdit(product)" />
              </div>
            </div>
            <div class="product-details">
              <div class="category-tag">{{ getCategoryName(product.category) }}</div>
              <h4 class="product-title" @click="handleEdit(product)">{{ product.name }}</h4>
              <div class="price-row">
                <span class="price-value">{{ formatCurrency(product.price, product.currency) }}</span>
                <span class="price-unit">/ {{ product.unit_of_measure }}</span>
              </div>
              <div class="stock-row">
                <span class="stock-label">Запас:</span>
                <span class="stock-value" :class="getStockClass(product.stock_balance)">
                  {{ product.stock_balance }} {{ product.unit_of_measure }}
                </span>
              </div>
              <el-progress
                :percentage="getStockPercentage(product.stock_balance)"
                :status="getStockProgressStatus(product.stock_balance)"
                :show-text="false"
                style="margin-top: 6px;"
              />
            </div>
          </el-card>
        </el-col>
        <el-col :span="24" v-if="!loading && products.length === 0">
          <el-empty description="Товарів не знайдено" />
        </el-col>
      </el-row>

      <!-- List View -->
      <div v-else class="table-wrapper" v-loading="loading">
        <el-table
          :data="products"
          style="width: 100%"
          size="small"
          class="products-table"
          @row-click="handleEdit"
          row-class-name="product-row"
        >
          <!-- Photo -->
          <el-table-column width="60" align="center">
            <template #header><span class="col-header">Фото</span></template>
            <template #default="scope">
              <el-image :src="scope.row.image_url" class="list-image" fit="cover">
                <template #error>
                  <div class="list-image-placeholder"><el-icon><Picture /></el-icon></div>
                </template>
              </el-image>
            </template>
          </el-table-column>

          <!-- SKU -->
          <el-table-column width="130">
            <template #header><span class="col-header">Артикул</span></template>
            <template #default="scope">
              <span class="sku-link" @click.stop="handleEdit(scope.row)">{{ scope.row.sku }}</span>
            </template>
          </el-table-column>

          <!-- Name -->
          <el-table-column min-width="200">
            <template #header><span class="col-header">Назва</span></template>
            <template #default="scope">
              <span class="product-name-link" @click.stop="handleEdit(scope.row)">{{ scope.row.name }}</span>
            </template>
          </el-table-column>

          <!-- Category -->
          <el-table-column width="200">
            <template #header><span class="col-header">Категорія</span></template>
            <template #default="scope">
              <span class="category-text">{{ getCategoryName(scope.row.category) }}</span>
            </template>
          </el-table-column>

          <!-- Stock -->
          <el-table-column width="120" align="right">
            <template #header><span class="col-header">Запас</span></template>
            <template #default="scope">
              <span :class="['stock-val', getStockClass(scope.row.stock_balance)]">
                {{ scope.row.stock_balance }} {{ scope.row.unit_of_measure }}
              </span>
            </template>
          </el-table-column>

          <!-- Price -->
          <el-table-column width="120" align="right">
            <template #header><span class="col-header">Ціна</span></template>
            <template #default="scope">
              <span class="price-val">{{ formatCurrency(scope.row.price, scope.row.currency) }}</span>
            </template>
          </el-table-column>

          <!-- Actions -->
          <el-table-column width="60" align="center">
            <template #default="scope">
              <el-button :icon="Edit" circle size="small" @click.stop="handleEdit(scope.row)" />
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-bar">
          <span class="total-hint">Всього {{ total }} товарів</span>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="limit"
            :total="total"
            background
            layout="prev, pager, next"
            class="custom-pagination"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <!-- Grid pagination -->
      <div v-if="viewMode === 'grid'" class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, Edit, Picture,
  Box, Coordinate, Warning, CircleClose, Grid, Fold
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

// State
const loading = ref(false)
const products = ref([])
const stats = ref({ total_products: 0, in_stock: 0, low_stock: 0, out_of_stock: 0 })
const total = ref(0)
const skip = ref(0)
const limit = ref(20)
const currentPage = ref(1)
const searchQuery = ref('')
const filterCategory = ref('')
const viewMode = ref('list') // default to list
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

let searchTimer = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    skip.value = 0
    currentPage.value = 1
    fetchProducts()
  }, 400)
}

const handleCategorySelect = (code) => {
  filterCategory.value = code
  skip.value = 0
  currentPage.value = 1
  fetchProducts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  skip.value = (page - 1) * limit.value
  fetchProducts()
}

const handleEdit = (row) => {
  router.push(`/inventory/nomenclature/${row.id}`)
}

const goToCreate = () => {
  router.push('/inventory/nomenclature/new')
}

// Helpers
const getCategoryName = (code) => {
  return categoryOptions.value.find(c => c.code === code)?.name || code || '—'
}

const getStockClass = (qty) => {
  if (qty <= 0) return 'stock-none'
  if (qty <= 5) return 'stock-low'
  return 'stock-ok'
}

const getStockProgressStatus = (qty) => {
  if (qty <= 0) return 'exception'
  if (qty <= 5) return 'warning'
  return 'success'
}

const getStockPercentage = (qty) => {
  return Math.min(100, Math.round((qty / 100) * 100))
}

const formatCurrency = (amount, currency = 'UAH') => {
  if (amount == null) return '—'
  const c = currency || 'UAH'
  const sym = c === 'UAH' ? 'грн' : c === 'USD' ? '$' : c
  return `${parseFloat(amount).toFixed(0)} ${sym}`
}

onMounted(() => {
  fetchDictionaries()
  fetchStatistics().then(() => fetchProducts())
})

onActivated(() => {
  fetchStatistics().then(() => fetchProducts())
})
</script>

<style scoped>
/* ===== PAGE ===== */
.page-container {
  padding: 0;
  background: #f4f5f9;
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== HEADER (fixed, non-scrolling) ===== */
.sticky-header-wrapper {
  flex-shrink: 0;
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ===== PAGE HEADER ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}
.header-left h2 {
  margin: 0 0 2px;
  font-size: 22px;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.3px;
}
.page-subtitle {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  font-weight: 400;
}
.header-actions { display: flex; gap: 10px; }
.btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 9px;
  font-weight: 600;
  padding: 8px 18px;
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  transition: box-shadow 0.2s, transform 0.15s;
}
.btn-create:hover {
  box-shadow: 0 6px 20px rgba(99,102,241,0.5);
  transform: translateY(-1px);
}

/* ===== STAT CARDS ===== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  border: 1px solid #e4e8f0;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover { box-shadow: 0 4px 14px rgba(99,102,241,0.1); transform: translateY(-1px); }

.stat-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.total .stat-icon { background: #ede9fe; color: #6366f1; }
.in-stock .stat-icon { background: #d1fae5; color: #10b981; }
.low-stock .stat-icon { background: #fef3c7; color: #f59e0b; }
.out-of-stock .stat-icon { background: #fee2e2; color: #ef4444; }

.stat-info { display: flex; flex-direction: column; gap: 1px; }
.stat-value { font-size: 20px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.stat-label { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; }

.stat-badge {
  margin-left: auto;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 7px;
  border-radius: 20px;
}
.stat-badge.negative { background: rgba(239,68,68,0.1); color: #ef4444; }

/* ===== FILTERS TOOLBAR ===== */
.filters-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
}
.search-input { width: 220px; flex-shrink: 0; }
.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e4e8f0;
  box-shadow: none !important;
  background: #fff;
  height: 30px;
}
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}
.category-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  flex: 1;
}
.chip {
  padding: 4px 12px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
}
.chip:hover { border-color: #6366f1; color: #6366f1; }
.chip.active { background: #6366f1; color: #fff; border-color: #6366f1; box-shadow: 0 2px 8px rgba(99,102,241,0.28); }

.view-toggle { margin-left: auto; }
.view-toggle :deep(.el-radio-button__inner) { padding: 5px 10px; font-size: 13px; }

/* ===== CONTENT ===== */
.content-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px 20px;
}

/* ===== TABLE WRAPPER ===== */
.table-wrapper {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e4e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  overflow: hidden;
}

.products-table :deep(th.el-table__cell) {
  background: #f8fafc !important;
  padding: 6px 8px !important;
  border-bottom: 1px solid #e4e8f0 !important;
}
.col-header {
  font-size: 10px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.products-table :deep(td.el-table__cell) {
  padding: 5px 8px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  border-right: none !important;
}
.products-table :deep(.el-table__inner-wrapper::before) { display: none; }
.products-table :deep(.product-row) { cursor: pointer; transition: background 0.12s; }
.products-table :deep(.product-row:hover > td) { background: #f8f7ff !important; }

/* Table cell styles */
.list-image { width: 36px; height: 36px; border-radius: 8px; display: block; }
.list-image-placeholder {
  width: 36px; height: 36px;
  background: #f1f5f9; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #94a3b8; font-size: 16px;
}
.sku-link { color: #6366f1; font-weight: 600; font-size: 12px; cursor: pointer; }
.sku-link:hover { text-decoration: underline; }
.product-name-link { color: #1e293b; font-weight: 500; font-size: 13px; cursor: pointer; }
.product-name-link:hover { color: #6366f1; }
.category-text { color: #64748b; font-size: 12px; }
.stock-val { font-size: 12px; font-weight: 600; }
.stock-ok { color: #10b981; }
.stock-low { color: #f59e0b; }
.stock-none { color: #ef4444; }
.price-val { font-size: 12px; font-weight: 600; color: #1e293b; }

/* Pagination */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-top: 1px solid #f1f5f9;
}
.total-hint { font-size: 12px; color: #94a3b8; }
.custom-pagination :deep(.el-pager li) { border-radius: 6px; min-width: 28px; height: 28px; line-height: 28px; }
.custom-pagination :deep(.el-pager li.is-active) { background: #6366f1 !important; color: #fff !important; }

/* Grid card */
.product-card {
  border-radius: 10px;
  border: 1px solid #e4e8f0;
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.2s;
}
.product-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99,102,241,0.1) !important; border-color: #c7d2fe; }
.product-image-container { position: relative; height: 150px; background: #f4f5f9; }
.product-image { width: 100%; height: 100%; }
.image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #d1d5db; }
.product-actions-overlay { position: absolute; top: 8px; right: 8px; opacity: 0; transition: opacity 0.2s; }
.product-card:hover .product-actions-overlay { opacity: 1; }
.product-details { padding: 12px; }
.category-tag { font-size: 9px; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.product-title { margin: 0 0 8px; font-size: 13px; font-weight: 600; color: #1e293b; cursor: pointer; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.price-row { margin-bottom: 4px; }
.price-value { font-size: 14px; font-weight: 700; color: #1e293b; }
.price-unit { font-size: 12px; color: #94a3b8; }
.stock-row { display: flex; justify-content: space-between; font-size: 11px; }
.stock-label { color: #94a3b8; }

@media (max-width: 640px) {
  .sticky-header-wrapper { padding: 12px 12px 8px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .search-input { width: 100%; }
}
</style>
