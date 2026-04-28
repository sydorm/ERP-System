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
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #F9FAFB;
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Space Grotesk', sans-serif;
}

.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: #F9FAFB;
  padding: 20px 20px 0;
  display: flex;
  flex-direction: column;
}

/* ===== STAT CARDS ===== */
.kimi-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.kimi-stat-card {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: none !important;
  transition: transform 0.15s ease-in-out;
}

.kimi-stat-card:hover {
  transform: translateY(-1px);
}

.kimi-stat-label {
  font-size: 11px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.kimi-stat-value {
  font-size: 36px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #18181B !important;
  margin: 8px 0;
  line-height: 1;
}

/* "НЕМАЄ" special color */
.kimi-stat-rose .kimi-stat-value {
  color: #EF4444 !important;
}

/* Subtle sub-labels */
.kimi-stat-info::after {
  content: 'залишки в реальному часі';
  display: block;
  font-size: 12px;
  color: #9CA3AF;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 400;
}

.kimi-stat-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent !important;
  color: #D1D5DB !important;
  font-size: 24px;
}

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
  border-radius: 8px !important;
  height: 38px !important;
  border: 1px solid #E5E7EB !important;
  box-shadow: none !important;
  font-family: 'Space Grotesk', sans-serif;
}
:deep(.el-input__wrapper.is-focus) {
  border-color: #18181B !important;
}

.kimi-primary-btn {
  background: #18181B !important;
  border: none !important;
  border-radius: 8px;
  font-weight: 600;
  font-family: 'Space Grotesk', sans-serif;
  color: #FFFFFF !important;
  padding: 0 20px;
  height: 38px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}
.kimi-primary-btn:hover {
  background: #27272A !important;
}

/* ===== CONTENT AREA ===== */
.table-container {
  flex: 1;
  background: #FFFFFF;
  border-radius: 12px 12px 0 0;
  display: flex;
  flex-direction: column;
  margin: 0 20px;
  border: 1px solid #E5E7EB !important;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* el-table visual styles */
.kimi-table :deep(th.el-table__cell) {
  background: #F3F4F6 !important;
  color: #6B7280;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #F3F4F6 !important;
  padding: 10px 8px !important;
}

.kimi-table :deep(td.el-table__cell) {
  border-bottom: 1px solid #F3F4F6 !important;
  padding: 12px 8px !important;
}

:deep(.kimi-row:hover td) {
  background-color: #F9FAFB !important;
}

/* Photo placeholder fallback */
.list-image {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #E5E7EB;
}

.list-image-placeholder {
  width: 32px;
  height: 32px;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}

/* Text styles */
.kimi-text-indigo-600 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #6B7280;
}

.kimi-text-sm {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 14px;
  color: #18181B;
  font-weight: 500;
}

/* Stock balance color styles */
.kimi-table :deep(.kimi-row) span {
  font-family: 'JetBrains Mono', monospace;
}

/* Dynamic classes generated by original codebase helpers */
:deep(.kimi-text-rose-600), :deep(.text-rose-600) {
  color: #EF4444 !important;
  font-family: 'JetBrains Mono', monospace !important;
}
:deep(.kimi-text-emerald-600), :deep(.text-emerald-600) {
  color: #16A34A !important;
  font-family: 'JetBrains Mono', monospace !important;
}

.kimi-ghost-btn {
  background: #F3F4F6;
  border: none;
  cursor: pointer;
  width: 32px; height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  transition: all 0.2s;
}
.kimi-ghost-btn:hover {
  background: #18181B;
  color: #FFFFFF;
}

.pagination-footer {
  background: #FFFFFF;
  padding: 16px 20px;
  border-top: 1px solid #F3F4F6;
}

/* Toggle buttons */
.kimi-view-toggle :deep(.el-radio-button__inner) {
  font-family: 'Space Grotesk', sans-serif;
}
</style>
