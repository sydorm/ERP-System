<template>
  <div class="orders-page">
    <div class="fixed-top-area">

      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <MetricCard 
          label="Всього товарів" 
          :value="stats.total_products" 
          accentColor="#3B82F6" 
          :sparklineData="[5, 10, 15, stats.total_products || 10]"
        />
        <MetricCard 
          label="В наявності" 
          :value="stats.in_stock" 
          trend="+5%"
          :trendUp="true"
          accentColor="#22C55E" 
          :sparklineData="[2, 4, 8, stats.in_stock || 8]"
        />
        <MetricCard 
          label="Закінчуються" 
          :value="stats.low_stock" 
          trend="-2%"
          :trendUp="false"
          accentColor="#F59E0B" 
          :sparklineData="[8, 6, 4, stats.low_stock || 2]"
        />
        <MetricCard 
          label="Немає" 
          :value="stats.out_of_stock" 
          trend="+12%"
          :trendUp="true"
          accentColor="#EF4444" 
          :sparklineData="[1, 3, 5, stats.out_of_stock || 12]"
        />
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
import MetricCard from '../../components/MetricCard.vue'

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
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

.orders-page {
  --bg: #F7F8FC;
  --surface: #FFFFFF;
  --text: #1E293B;
  --text-muted: #64748B;
  --border: rgba(0, 0, 0, 0.06);

  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--bg);
  color: var(--text);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

:global(html.dark) .orders-page {
  --bg: #0B0F19;
  --surface: #151A2D;
  --text: #F1F5F9;
  --text-muted: #94A3B8;
  --border: rgba(51, 65, 85, 0.6);
}

.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: var(--bg);
  padding: 12px 25px 0;
  display: flex;
  flex-direction: column;
}

/* ===== STAT CARDS ===== */
.kimi-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 12px;
}

.kimi-stat-card {
  background: #FFFFFF !important;
  border: none !important;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 85px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06) !important;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.kimi-stat-card:hover {
  transform: translateY(-3px);
}

.kimi-stat-label {
  font-size: 10px;
  color: #64748B;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.kimi-stat-value {
  font-size: 28px;
  font-weight: 500;
  color: #0F172A;
  font-family: 'DM Mono', monospace;
  margin-top: 4px;
  line-height: 1.2;
}

.kimi-stat-indigo .kimi-stat-value { color: #0F172A !important; }
.kimi-stat-emerald .kimi-stat-value { color: #0F172A !important; }
.kimi-stat-amber .kimi-stat-value { color: #0F172A !important; }
.kimi-stat-rose .kimi-stat-value { color: #0F172A !important; }

/* Sparkline emulation line */
.kimi-stat-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
}
.kimi-stat-indigo::after { background: #3B82F6; }
.kimi-stat-emerald::after { background: #22C55E; }
.kimi-stat-amber::after { background: #F59E0B; }
.kimi-stat-rose::after { background: #EF4444; }

/* Trend percentages via pseudo content */
.kimi-stat-card::before {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 11px;
  font-weight: 600;
}
.kimi-stat-indigo::before { content: '↑ +5%'; color: #22C55E; }
.kimi-stat-emerald::before { content: '↑ +5%'; color: #22C55E; }
.kimi-stat-amber::before { content: '↓ -2%'; color: #F59E0B; }
.kimi-stat-rose::before { content: '↑ +12%'; color: #EF4444; }

.kimi-stat-icon-wrapper {
  display: none !important;
}

/* ===== FILTERS TOOLBAR ===== */
.kimi-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  padding: 15px 20px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}
.kimi-filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-input__wrapper) {
  background-color: #FFFFFF !important;
  border-radius: 10px !important;
  height: 38px !important;
  border: 1px solid #E2E8F0 !important;
  box-shadow: none !important;
}
:deep(.el-input__icon) {
  color: #64748B !important;
}

.kimi-view-toggle {
  display: none !important;
}

.kimi-primary-btn {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  border: none !important;
  border-radius: 10px;
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: white !important;
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25);
  padding: 0 20px;
  height: 38px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.kimi-primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(108, 99, 255, 0.35);
  opacity: 1 !important;
}

/* ===== CONTENT AREA ===== */
.table-container {
  flex: 1;
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  margin: 0 25px 25px;
  border: none !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
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
  background: #FFFFFF !important;
  color: #64748B !important;
  font-family: 'Syne', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-top: none !important;
  border-bottom: 1px solid #F1F5F9 !important;
  padding: 14px 10px !important;
}

/* Table Row styling */
.kimi-table :deep(.el-table__row) {
  height: 52px !important;
}

.kimi-table :deep(.el-table__row td) {
  border-left: none !important;
  border-right: none !important;
  border-bottom: 1px solid #F1F5F9 !important;
}

/* Zebra Effect and Hover matching Warehouses.vue */
.kimi-table :deep(.el-table__row:nth-child(even) td) {
  background-color: #FAFBFF !important;
}

.kimi-table :deep(.el-table__row:nth-child(odd) td) {
  background-color: #FFFFFF !important;
}

:deep(.kimi-row:hover td) {
  background: linear-gradient(90deg, rgba(108, 99, 255, 0.03), rgba(0, 201, 167, 0.02)) !important;
}

/* Column typography mapped */
.kimi-text-indigo-600 {
  font-family: 'DM Mono', monospace !important;
  font-size: 0.85rem !important;
  color: #64748B !important;
}

.kimi-text-sm {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  color: #0F172A;
}

/* Specific price styling */
.kimi-table :deep(.kimi-row) span.text-rose-600 {
  color: #EF4444 !important;
  font-weight: 600 !important;
  font-family: 'DM Mono', monospace !important;
}
.kimi-table :deep(.kimi-row) span.text-amber-600 {
  color: #EF4444 !important;
  font-weight: 600 !important;
  font-family: 'DM Mono', monospace !important;
}
.kimi-table :deep(.kimi-row) span.text-emerald-600 {
  color: #16A34A !important;
  font-weight: 600 !important;
  font-family: 'DM Mono', monospace !important;
}

/* Category Pill badges mapping */
.kimi-table :deep(td.el-table__cell:nth-child(4) span) {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  display: inline-block;
  background: rgba(108, 99, 255, 0.06);
  color: #6C63FF;
}

/* Fallback alphabetical circle */
.list-image-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'DM Mono', monospace;
  font-size: 14px;
  font-weight: 700;
}

/* Dropdown menu styling (10 / 20 / 50 / 100) */
:global(.el-select__popper) {
  width: 80px !important;
  min-width: 80px !important;
  max-width: 80px !important;
  border-radius: 8px !important;
}

:global(.el-select-dropdown) {
  width: 80px !important;
  min-width: 80px !important;
}

:global(.el-select-dropdown__item) {
  padding: 6px 12px !important;
  font-size: 13px !important;
}

:global(.el-select-dropdown__item.is-selected) {
  color: #6C63FF !important;
  font-weight: 600 !important;
  background-color: rgba(108,99,255,0.06) !important;
}

:global(.el-select-dropdown__item:hover) {
  background-color: #F5F3FF !important;
}

/* Pagination overrides */
.pagination-footer {
  background: #FFFFFF;
  padding: 16px 20px;
  border-top: 1px solid #F1F5F9;
}

:deep(.limit-select),
:deep(.limit-select .el-input__wrapper),
:deep(.limit-select .el-select__wrapper) {
  width: 70px !important;
  min-width: 70px !important;
  max-width: 70px !important;
}

:deep(.limit-select .el-input__wrapper) {
  border: 1px solid #E2E8F0 !important;
  border-radius: 8px !important;
  padding: 4px 8px !important;
  height: 30px !important;
}

/* Parent container size limit checks */
.custom-pagination-container {
  width: auto !important;
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-pager li) {
  width: 32px;
  height: 32px;
  border-radius: 8px !important;
  border: 1px solid #E2E8F0 !important;
  background: #FFFFFF !important;
  color: #475569 !important;
  margin: 0 4px;
  line-height: 32px;
}
:deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  color: #FFFFFF !important;
  border: none !important;
}
</style>
