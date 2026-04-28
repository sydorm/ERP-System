<template>
  <div class="orders-page">
    <div class="fixed-top-area">

      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <!-- Всього товарів -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Всього товарів</p>
            <h3 class="kimi-stat-value text-indigo-600">{{ stats.total_products }}</h3>
          </div>
          <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
            <el-icon><Box /></el-icon>
          </div>
        </div>

        <!-- В наявності -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">В наявності</p>
            <h3 class="kimi-stat-value text-emerald-600">{{ stats.in_stock }}</h3>
          </div>
          <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
            <el-icon><Coordinate /></el-icon>
          </div>
        </div>

        <!-- Закінчуються -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Закінчуються</p>
            <h3 class="kimi-stat-value text-amber-600">{{ stats.low_stock }}</h3>
          </div>
          <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
            <el-icon><Warning /></el-icon>
          </div>
        </div>

        <!-- Немає -->
        <div class="kimi-stat-card kimi-stat-rose">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Немає</p>
            <h3 class="kimi-stat-value text-rose-600">{{ stats.out_of_stock }}</h3>
          </div>
          <div class="kimi-stat-icon-wrapper bg-rose-100 text-rose-600">
            <el-icon><CircleClose /></el-icon>
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
                <span class="price-unit">/ {{ getUomName(product.unit_of_measure) }}</span>
              </div>
              <div class="stock-row">
                <span class="stock-label">Запас:</span>
                <span class="stock-value" :class="getStockClass(product.stock_balance)">
                  {{ product.stock_balance }} {{ getUomName(product.unit_of_measure) }}
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
            <div class="custom-pagination-container">
              <el-select v-model="limit" size="small" class="limit-select" @change="handleSizeChange">
                <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
              </el-select>
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="limit"
                :total="total"
                background
                layout="prev, pager, next"
                class="custom-pagination-numeric"
                @current-change="handlePageChange"
              />
            </div>
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
                {{ scope.row.stock_balance }} {{ getUomName(scope.row.unit_of_measure) }}
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
          <div class="custom-pagination-container">
            <el-select v-model="limit" size="small" class="limit-select" @change="handleSizeChange">
              <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
            </el-select>
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="limit"
              :total="total"
              background
              layout="prev, pager, next"
              class="custom-pagination-numeric"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, Edit, Picture,
  Box, Coordinate, Warning, CircleClose, Grid, Fold
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'

const dictStore = useDictionaryStore()

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

const categoryOptions = computed(() => dictStore.getCategory('PRODUCT_CATEGORY'))
const uomOptions = computed(() => dictStore.getCategory('UOM'))

const fetchDictionaries = async () => {
  try {
    await dictStore.fetchMultiple(['PRODUCT_CATEGORY', 'UOM'])
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
  return dictStore.getName('PRODUCT_CATEGORY', code)
}

const getUomName = (code) => {
  return dictStore.getShortName('UOM', code)
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
.orders-page {
  --bg: #FFFFFF;
  --surface: #F9FAFB;
  --text: #18181B;
  --text-muted: #6B7280;
  --border: #E5E7EB;
  
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--bg);
  color: var(--text);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Space Grotesk', sans-serif;
}

:global(html.dark) .orders-page {
  --bg: #0F1117;
  --surface: #1A1D27;
  --text: #F9FAFB;
  --text-muted: #9CA3AF;
  --border: #2D313E;
}

.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: var(--bg);
  padding: 16px 20px 0;
  display: flex;
  flex-direction: column;
}

/* ===== STAT CARDS ===== */
.kimi-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.kimi-stat-card {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px;
  padding: 14px;
  height: 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: none !important;
}

.kimi-stat-indigo { border-left: 3px solid #3B82F6 !important; }
.kimi-stat-emerald { border-left: 3px solid #22C55E !important; }
.kimi-stat-amber { border-left: 3px solid #F59E0B !important; }
.kimi-stat-rose { border-left: 3px solid #EF4444 !important; }

.kimi-stat-label {
  font-size: 11px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.kimi-stat-value {
  font-size: 32px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  margin: 4px 0 0;
  line-height: 1;
}

.kimi-stat-indigo .kimi-stat-value { color: #3B82F6 !important; }
.kimi-stat-emerald .kimi-stat-value { color: #22C55E !important; }
.kimi-stat-amber .kimi-stat-value { color: #F59E0B !important; }
.kimi-stat-rose .kimi-stat-value { color: #EF4444 !important; }

.kimi-stat-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.kimi-stat-indigo .kimi-stat-icon-wrapper { background: rgba(59, 130, 246, 0.15) !important; color: #3B82F6 !important; }
.kimi-stat-emerald .kimi-stat-icon-wrapper { background: rgba(34, 197, 94, 0.15) !important; color: #22C55E !important; }
.kimi-stat-amber .kimi-stat-icon-wrapper { background: rgba(245, 158, 11, 0.15) !important; color: #F59E0B !important; }
.kimi-stat-rose .kimi-stat-icon-wrapper { background: rgba(239, 68, 68, 0.15) !important; color: #EF4444 !important; }

/* ===== FILTERS TOOLBAR ===== */
.kimi-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.kimi-filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-input__wrapper) {
  background-color: var(--surface) !important;
  border-radius: 10px !important;
  height: 38px !important;
  border: 1.5px solid #E5E7EB !important;
  box-shadow: none !important;
}
:deep(.el-input__wrapper.is-focus) {
  border-color: #3B82F6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}
:deep(.el-input__icon) {
  color: #9CA3AF !important;
  font-size: 16px !important;
}

/* Hide view toggle buttons entirely */
.kimi-view-toggle {
  display: none !important;
}

.kimi-primary-btn {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  border: none !important;
  border-radius: 10px;
  font-weight: 600;
  font-family: 'Space Grotesk', sans-serif;
  color: #FFFFFF !important;
  padding: 0 20px;
  height: 38px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}
.kimi-primary-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* ===== CONTENT AREA ===== */
.table-container {
  flex: 1;
  background: var(--bg);
  border-radius: 12px 12px 0 0;
  display: flex;
  flex-direction: column;
  margin: 0 20px;
  border: 1px solid var(--border) !important;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header styling */
.kimi-table :deep(th.el-table__cell) {
  background: linear-gradient(135deg, rgba(108,99,255,0.06), rgba(0,201,167,0.06)) !important;
  color: #374151;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 2px solid rgba(108,99,255,0.15) !important;
  padding: 10px 8px !important;
}

/* Table Row Highlighting Rules */
.kimi-table :deep(.el-table__row) {
  height: 48px !important;
}

.kimi-table :deep(.el-table__row td) {
  border-left: none !important;
  border-right: none !important;
  border-bottom: 1px solid #F3F4F6 !important;
}

/* Stock 0 formatting */
:deep(.kimi-row[class*="out_of_stock"] td) {
  background-color: rgba(239, 68, 68, 0.02) !important;
}
:deep(.kimi-row[class*="out_of_stock"] td:first-child) {
  border-left: 2px solid #EF4444 !important;
}

/* Stock > 0 formatting */
:deep(.kimi-row:not([class*="out_of_stock"]) td) {
  background-color: rgba(34, 197, 94, 0.02) !important;
}
:deep(.kimi-row:not([class*="out_of_stock"]) td:first-child) {
  border-left: 2px solid #22C55E !important;
}

/* Hover state */
:deep(.kimi-row:hover td) {
  background: linear-gradient(90deg, rgba(108, 99, 255, 0.04), transparent) !important;
}
:deep(.kimi-row:hover td:first-child) {
  border-left: 2px solid #6C63FF !important;
}

/* SKU and Name */
.kimi-text-indigo-600 {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 12px !important;
  color: #6B7280 !important;
}

.kimi-text-sm {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

/* Specific price styling */
.kimi-table :deep(.kimi-row) span.text-rose-600 {
  color: #EF4444 !important;
  font-weight: 600 !important;
}
.kimi-table :deep(.kimi-row) span.text-amber-600 {
  color: #EF4444 !important;
  font-weight: 600 !important;
}
.kimi-table :deep(.kimi-row) span.text-emerald-600 {
  color: #16A34A !important;
  font-weight: 600 !important;
}

/* Category Pill badges mapping */
.kimi-table :deep(td.el-table__cell:nth-child(4) span) {
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  display: inline-block;
  background: #F3F4F6;
  color: #374151;
}

/* Fallback alphabetical circle */
.list-image-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #EFF6FF;
  color: #3B82F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}

/* Pagination overrides */
.pagination-footer {
  background: #FFFFFF;
  padding: 16px 20px;
  border-top: 1px solid #F3F4F6;
}

:deep(.limit-select .el-input__wrapper) {
  border: 1px solid #E5E7EB !important;
  border-radius: 8px !important;
  padding: 4px 10px !important;
  height: 30px !important;
  width: auto !important;
}
:deep(.limit-select .el-input__inner) {
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 13px !important;
}

:deep(.el-pager li) {
  width: 32px;
  height: 32px;
  border-radius: 8px !important;
  border: 1px solid #E5E7EB !important;
  background: #FFFFFF !important;
  color: #18181B !important;
  margin: 0 4px;
  line-height: 32px;
}
:deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  color: #FFFFFF !important;
  border: none !important;
}
:deep(.el-pager li:hover:not(.is-active)) {
  background: #F3F4F6 !important;
}
</style>
