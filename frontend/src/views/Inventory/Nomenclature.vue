<template>
  <div class="orders-page">
    <div class="fixed-top-area">

      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <!-- Всього товарів -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Всього товарів</p>
              <h3 class="kimi-stat-value text-indigo-600">{{ stats.total_products }}</h3>
            </div>
            <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
              <el-icon><Box /></el-icon>
            </div>
          </div>
        </div>

        <!-- В наявності -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">В наявності</p>
              <h3 class="kimi-stat-value text-emerald-600">{{ stats.in_stock }}</h3>
            </div>
            <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
              <el-icon><Coordinate /></el-icon>
            </div>
          </div>
        </div>

        <!-- Закінчуються -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Закінчуються</p>
              <h3 class="kimi-stat-value text-amber-600">{{ stats.low_stock }}</h3>
            </div>
            <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
              <el-icon><Warning /></el-icon>
            </div>
          </div>
        </div>

        <!-- Немає -->
        <div class="kimi-stat-card kimi-stat-rose">
          <div class="kimi-stat-content">
            <div>
              <p class="kimi-stat-label">Немає</p>
              <h3 class="kimi-stat-value text-rose-600">{{ stats.out_of_stock }}</h3>
            </div>
            <div class="kimi-stat-icon-wrapper bg-rose-100 text-rose-600">
              <el-icon><CircleClose /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== FILTERS TOOLBAR ===== -->
      <div class="kimi-filter-bar">
        <div class="kimi-filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="Пошук товарів..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            class="kimi-search-input"
          />
          <el-select
            v-model="filterCategory"
            placeholder="Всі категорії"
            clearable
            style="width:200px"
            @change="handleCategorySelect"
            class="kimi-status-select"
          >
            <el-option
              v-for="cat in categoryOptions"
              :key="cat.code"
              :label="cat.name"
              :value="cat.code"
            />
          </el-select>
          <el-select
            v-model="filterStock"
            placeholder="Наявність"
            clearable
            style="width:160px"
            @change="handleFilterChange"
            class="kimi-status-select"
          >
            <el-option label="Всі товари" value="" />
            <el-option label="В наявності" value="in_stock" />
            <el-option label="Закінчуються" value="low_stock" />
            <el-option label="Немає" value="out_of_stock" />
          </el-select>
          <el-radio-group v-model="viewMode" size="small" class="kimi-view-toggle">
            <el-radio-button value="list"><el-icon><Fold /></el-icon></el-radio-button>
            <el-radio-button value="grid"><el-icon><Grid /></el-icon></el-radio-button>
          </el-radio-group>
        </div>
        <div class="kimi-filter-right">
          <button class="kimi-primary-btn" @click="goToCreate">
            <el-icon><Plus /></el-icon> Створити товар
          </button>
        </div>
      </div>
    </div>

    <!-- ===== CONTENT AREA ===== -->
    <div class="table-container">
      <!-- Grid View -->
      <el-row v-if="viewMode === 'grid'" :gutter="20" v-loading="loading" style="padding: 16px; overflow-y: auto; flex: 1; margin: 0; display: block; height: 100%;">
        <div style="display: flex; flex-wrap: wrap; margin: -10px;">
        <el-col v-for="product in products" :key="product.id" :xs="24" :sm="12" :md="8" :lg="6" style="padding: 10px;">
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
        
        </div>
        
        <!-- Grid pagination -->
        <el-col :span="24" v-if="total > 0" style="padding: 10px;">
          <div class="pagination-footer" style="border-top: none; margin-top: 20px;">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="limit"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              background
              layout="prev, pager, next"
              class="custom-pagination"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </el-col>
      </el-row>

      <!-- List View -->
      <div v-else class="table-wrapper" v-loading="loading">
        <el-table
          :data="products"
          height="100%"
          style="width: 100%"
          class="kimi-table"
          @row-click="handleEdit"
          row-class-name="kimi-row"
          header-row-class-name="kimi-header-row"
        >
          <!-- Photo -->
          <el-table-column width="80" align="center">
            <template #header>ФОТО</template>
            <template #default="scope">
              <div @click.stop>
                <el-image 
                  :src="scope.row.image_url" 
                  class="list-image" 
                  fit="cover"
                  :preview-src-list="scope.row.image_url ? [scope.row.image_url] : []"
                  :preview-teleported="true"
                  :hide-on-click-modal="true"
                >
                  <template #error>
                    <div class="list-image-placeholder"><el-icon><Picture /></el-icon></div>
                  </template>
                </el-image>
              </div>
            </template>
          </el-table-column>

          <!-- SKU -->
          <el-table-column width="130">
            <template #header>АРТИКУЛ</template>
            <template #default="scope">
              <span class="kimi-text-indigo-600 kimi-font-medium kimi-text-sm">{{ scope.row.sku }}</span>
            </template>
          </el-table-column>

          <!-- Name -->
          <el-table-column min-width="200">
            <template #header>НАЗВА</template>
            <template #default="scope">
              <span class="kimi-text-sm kimi-font-medium">{{ scope.row.name }}</span>
            </template>
          </el-table-column>

          <!-- Category -->
          <el-table-column width="200">
            <template #header>КАТЕГОРІЯ</template>
            <template #default="scope">
              <span class="kimi-text-slate-400 kimi-text-sm">{{ getCategoryName(scope.row.category) }}</span>
            </template>
          </el-table-column>

          <!-- Stock -->
          <el-table-column width="140" align="right">
            <template #header>ЗАПАС</template>
            <template #default="scope">
              <span :class="['kimi-text-sm kimi-font-medium', getStockColorClass(scope.row.stock_balance)]">
                {{ scope.row.stock_balance }} {{ scope.row.unit_of_measure }}
              </span>
            </template>
          </el-table-column>

          <!-- Price -->
          <el-table-column width="120" align="right">
            <template #header>ЦІНА</template>
            <template #default="scope">
              <span class="kimi-text-sm kimi-font-medium">{{ formatCurrency(scope.row.price, scope.row.currency) }}</span>
            </template>
          </el-table-column>

          <!-- Actions -->
          <el-table-column width="80" align="center">
            <template #header>ДІЇ</template>
            <template #default="scope">
              <div class="kimi-actions-col">
                <button class="kimi-ghost-btn" @click.stop="handleEdit(scope.row)">
                  <el-icon><Edit /></el-icon>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-footer">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="limit"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            background
            layout="prev, pager, next"
            class="custom-pagination"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
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
const filterStock = ref('')
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
    let results = response.data
    
    // Front-end filter for stock status since backend doesn't support it directly yet
    if (filterStock.value) {
      if (filterStock.value === 'in_stock') {
        results = results.filter(p => p.stock_balance > 0)
      } else if (filterStock.value === 'low_stock') {
        results = results.filter(p => p.stock_balance > 0 && p.stock_balance <= 5)
      } else if (filterStock.value === 'out_of_stock') {
        results = results.filter(p => p.stock_balance <= 0)
      }
    }
    products.value = results

    if (!searchQuery.value && !filterCategory.value && !filterStock.value) {
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

const handleFilterChange = () => {
  skip.value = 0
  currentPage.value = 1
  fetchProducts()
}

const handleSizeChange = (size) => {
  limit.value = size
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

const getStockColorClass = (qty) => {
  if (qty <= 0) return 'text-rose-600'
  if (qty <= 5) return 'text-amber-600'
  return 'text-emerald-600'
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
.orders-page {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #f4f5f9;
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== HEADER (fixed, non-scrolling) ===== */
.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 0;
  display: flex;
  flex-direction: column;
}

/* ===== STAT CARDS ===== */
.kimi-stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.kimi-stat-card {
  background: #fff; border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}
.kimi-stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.kimi-stat-indigo { background: linear-gradient(to bottom right, #f5f7ff, #fff); border-color: #e0e7ff; }
.kimi-stat-emerald { background: linear-gradient(to bottom right, #f0fdf4, #fff); border-color: #d1fae5; }
.kimi-stat-amber { background: linear-gradient(to bottom right, #fffbeb, #fff); border-color: #fef3c7; }
.kimi-stat-rose { background: linear-gradient(to bottom right, #fff1f2, #fff); border-color: #ffe4e6; }

.kimi-stat-content { display: flex; align-items: center; justify-content: space-between; }
.kimi-stat-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin: 0 0 4px 0; }
.kimi-stat-value { font-size: 24px; font-weight: 800; margin: 0; line-height: 1; }

.text-indigo-600 { color: #4f46e5; }
.text-emerald-600 { color: #059669; }
.text-amber-600 { color: #d97706; }
.text-rose-600 { color: #e11d48; }

.kimi-stat-icon-wrapper {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.bg-indigo-100 { background: #e0e7ff; }
.bg-emerald-100 { background: #d1fae5; }
.bg-amber-100 { background: #fef3c7; }
.bg-rose-100 { background: #ffe4e6; }

/* ===== FILTERS TOOLBAR ===== */
.kimi-filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.kimi-filter-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.kimi-search-input { width: 300px; max-width: 100%; flex-shrink: 0; margin-right: 12px; }
.kimi-search-input :deep(.el-input__wrapper) { 
  border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); height: 36px;
  border: 1px solid #e2e8f0;
}
.kimi-search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

.kimi-status-select :deep(.el-input__wrapper) {
  border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); height: 36px;
  border: 1px solid #e2e8f0;
}
.kimi-status-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

.kimi-view-toggle { margin-left: auto; flex-shrink: 0; }

.kimi-primary-btn {
  background: #4f46e5; color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 500;
  padding: 0 20px; height: 36px; cursor: pointer; display: flex; align-items: center; gap: 6px;
  box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3); transition: background 0.2s, transform 0.1s;
  white-space: nowrap; flex-shrink: 0;
}
.kimi-primary-btn:hover { background: #4338ca; transform: translateY(-1px); }

/* ===== CONTENT ===== */
.table-container {
  flex: 1; background: #fff; border-top-left-radius: 12px; border-top-right-radius: 12px;
  display: flex; flex-direction: column; margin: 0 20px; border: 1px solid #e2e8f0; border-bottom: none;
  overflow: hidden; box-shadow: 0 -4px 10px rgba(0,0,0,0.02);
}

.table-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Kimi Table classes */
.kimi-table :deep(th.el-table__cell) { 
  background: #f8fafc !important; color: #64748b; font-size: 10px; font-weight: 700; 
  border-bottom: 1px solid #e2e8f0 !important; text-transform: uppercase; letter-spacing: 0.4px;
  padding: 6px 8px !important;
}
.kimi-table :deep(td.el-table__cell) { padding: 4px 8px !important; border-bottom: 1px solid #f1f5f9 !important; border-right: none !important; }
.kimi-table :deep(.el-table__inner-wrapper::before) { display: none; }
.kimi-table :deep(.kimi-row) { cursor: pointer; transition: background 0.15s; }
.kimi-table :deep(.kimi-row:hover > td) { background-color: #f8fafc !important; }

/* Typography */
.kimi-text-sm { font-size: 14px; }
.kimi-text-xs { font-size: 12px; }
.kimi-text-xxs { font-size: 10px; }
.kimi-font-medium { font-weight: 500; color: #1e293b; }
.kimi-text-slate-400 { color: #64748b; }
.kimi-text-indigo-600 { color: #4f46e5; }
.kimi-text-emerald-600 { color: #059669; }
.kimi-text-amber-600 { color: #d97706; }
.kimi-text-rose-600 { color: #e11d48; }

/* Table cell styles */
.list-image { width: 40px; height: 40px; border-radius: 8px; display: block; border: 1px solid #f1f5f9; cursor: zoom-in; transition: transform 0.2s; }
.list-image:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.list-image-placeholder {
  width: 40px; height: 40px; background: #f8fafc; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; color: #cbd5e1; font-size: 20px;
  border: 1px solid #f1f5f9;
}

/* Actions */
.kimi-actions-col { display: flex; align-items: center; justify-content: center; gap: 4px; }
.kimi-ghost-btn {
  background: none; border: none; cursor: pointer; width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; color: #94a3b8; transition: all 0.2s;
}
.kimi-ghost-btn:hover { background: #f1f5f9; color: #4f46e5; }
.kimi-ghost-btn .el-icon { font-size: 16px; }

/* ===== PAGINATION ===== */
.pagination-footer {
  display: flex; justify-content: space-between; align-items: center; padding: 12px 20px;
  border-top: 1px solid #e2e8f0; background: #f8fafc; flex-shrink: 0;
}
.total-hint { font-size: 13px; color: #64748b; }
.custom-pagination :deep(.el-pager li) { border-radius: 6px; min-width: 30px; height: 30px; line-height: 30px; font-weight: 500; }
.custom-pagination :deep(.el-pager li.is-active) { background: #4f46e5 !important; color: #fff !important; }

/* ===== GRID PRODUCT CARD ===== */
.product-card { border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px; overflow: hidden; transition: all 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.product-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important; border-color: #c7d2fe; }
.product-image-container { position: relative; height: 160px; background: #f8fafc; border-bottom: 1px solid #f1f5f9; }
.product-image { width: 100%; height: 100%; }
.image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #cbd5e1; }
.product-actions-overlay { position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.2s; }
.product-card:hover .product-actions-overlay { opacity: 1; }
.product-details { padding: 14px; background: #fff; }
.category-tag { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; display: inline-block; padding: 2px 6px; background: #f1f5f9; border-radius: 4px; }
.product-title { margin: 0 0 10px; font-size: 14px; font-weight: 600; color: #1e293b; cursor: pointer; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.product-title:hover { color: #4f46e5; }
.price-row { margin-bottom: 8px; }
.price-value { font-size: 16px; font-weight: 700; color: #1e293b; }
.price-unit { font-size: 12px; color: #94a3b8; }
.stock-row { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
.stock-label { color: #64748b; }
.stock-value { font-weight: 600; }

@media (max-width: 768px) {
  .kimi-stats-row { grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 12px; }
  .kimi-filter-bar { flex-direction: column; align-items: stretch; gap: 12px; }
  .kimi-filter-left { flex-direction: column; align-items: stretch; gap: 12px; }
  .kimi-search-input { width: 100%; margin: 0; }
  .kimi-category-chips { padding-bottom: 8px; }
  .kimi-primary-btn { width: 100%; justify-content: center; }
  .table-container { margin: 0 12px; }
}
</style>
