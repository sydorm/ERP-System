<template>
  <div class="orders-page erp-light-container">
    <!-- ===== STAT CARDS ===== -->
    <div class="stats-row kimi-mb-6">
      <!-- Всього товарів -->
      <div class="stats-card">
        <div class="stats-card__icon total">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stats-card__content">
          <span class="stats-card__label">Всього товарів</span>
          <span class="stats-card__value">{{ stats.total_products }}</span>
        </div>
      </div>

      <!-- В наявності -->
      <div class="stats-card">
        <div class="stats-card__icon success">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stats-card__content">
          <span class="stats-card__label">В наявності</span>
          <span class="stats-card__value">{{ stats.in_stock }}</span>
        </div>
      </div>

      <!-- Закінчуються -->
      <div class="stats-card">
        <div class="stats-card__icon warning">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stats-card__content">
          <span class="stats-card__label">Закінчуються</span>
          <span class="stats-card__value">{{ stats.low_stock }}</span>
        </div>
      </div>

      <!-- Немає -->
      <div class="stats-card">
        <div class="stats-card__icon danger">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stats-card__content">
          <span class="stats-card__label">Немає</span>
          <span class="stats-card__value">{{ stats.out_of_stock }}</span>
        </div>
      </div>
    </div>

    <!-- ===== FILTERS TOOLBAR ===== -->
    <div class="toolbar kimi-mb-6">
      <div class="toolbar-left">
        <div class="search-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <input
            v-model="searchQuery"
            placeholder="Пошук за назвою або артикулом..."
            class="search-input"
            @input="handleSearch"
          />
        </div>
        
        <el-select
          v-model="filterCategory"
          placeholder="Всі категорії"
          clearable
          @change="handleCategorySelect"
          class="filter-select"
          style="width: 160px;"
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
          @change="handleFilterChange"
          class="filter-select"
          style="width: 160px;"
        >
          <el-option label="Всі товари" value="" />
          <el-option label="В наявності" value="in_stock" />
          <el-option label="Закінчуються" value="low_stock" />
          <el-option label="Немає" value="out_of_stock" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <button class="primary-button" @click="goToCreate">
          <el-icon><Plus /></el-icon> Створити товар
        </button>
      </div>
    </div>

    <!-- ===== TABLE ===== -->
    <div class="table-card" v-loading="loading">
      <el-table
        :data="products"
        style="width: 100%"
        :row-class-name="() => 'table-row'"
        :header-row-class-name="() => 'table-header'"
        @row-click="handleEdit"
      >
        <!-- Photo -->
        <el-table-column width="80" class-name="table-cell">
          <template #default="{ row }">
            <div @click.stop>
              <el-image 
                v-if="row.image_url"
                :src="row.image_url" 
                class="product-thumb" 
                fit="cover"
                :preview-src-list="[row.image_url]"
                :preview-teleported="true"
                :hide-on-click-modal="true"
              />
              <div v-else class="product-thumb">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Name & SKU -->
        <el-table-column min-width="240" class-name="table-cell">
          <template #header>Назва</template>
          <template #default="{ row }">
            <div class="product-title-block">
              <div class="product-title">{{ row.name }}</div>
              <div class="product-sku">{{ row.sku }}</div>
            </div>
          </template>
        </el-table-column>

        <!-- Category -->
        <el-table-column width="180" class-name="table-cell">
          <template #header>Категорія</template>
          <template #default="{ row }">
            <span class="category-badge">{{ getCategoryName(row.category) }}</span>
          </template>
        </el-table-column>

        <!-- Stock -->
        <el-table-column width="160" align="center" class-name="table-cell">
          <template #header>Запас</template>
          <template #default="{ row }">
            <span class="stock-badge" :class="getStockBadgeClass(row.stock_balance)">
              {{ row.stock_balance }} {{ getUomName(row.unit_of_measure) }}
            </span>
          </template>
        </el-table-column>

        <!-- Price -->
        <el-table-column width="140" align="right" class-name="table-cell">
          <template #header>Ціна</template>
          <template #default="{ row }">
            <span class="price-cell" :class="{ 'empty': !row.price }">
              {{ formatCurrency(row.price, row.currency) }}
            </span>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column width="100" align="center" class-name="table-cell">
          <template #header>Дії</template>
          <template #default="{ row }">
            <div class="actions-cell" @click.stop>
              <button class="icon-button" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-select v-model="limit" size="small" style="width: 80px;" @change="handleSizeChange">
          <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
        </el-select>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="limit"
          :total="total"
          background
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
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

const getStockBadgeClass = (qty) => {
  if (qty <= 0) return 'danger'
  if (qty <= 5) return 'warning'
  return 'success'
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
  --page-bg: #f6f8fb;
  --card-bg: #ffffff;
  --text-main: #0f172a;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e5e7eb;

  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-gradient-start: #5b5cf6;
  --primary-gradient-end: #7c3aed;

  --success-bg: #dcfce7;
  --success-text: #16a34a;

  --warning-bg: #fef3c7;
  --warning-text: #d97706;

  --danger-bg: #fee2e2;
  --danger-text: #dc2626;

  --category-bg: #eef2ff;
  --category-text: #6366f1;

  background-color: var(--page-bg);
  padding: 24px 28px;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', 'Manrope', system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.45;
  color: var(--text-main);
}

/* ===== STAT CARDS ===== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stats-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.stats-card__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stats-card__icon.total { background: #EFF6FF; color: #3B82F6; }
.stats-card__icon.success { background: var(--success-bg); color: var(--success-text); }
.stats-card__icon.warning { background: var(--warning-bg); color: var(--warning-text); }
.stats-card__icon.danger { background: var(--danger-bg); color: var(--danger-text); }

.stats-card__content {
  display: flex;
  flex-direction: column;
}

.stats-card__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.stats-card__value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'DM Mono', monospace;
}

/* ===== TOOLBAR ===== */
.toolbar {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 16px;
}

.search-input {
  width: 100%;
  height: 44px;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 0 14px 0 40px;
  background: var(--card-bg);
  color: var(--text-main);
  font-size: 14px;
  transition: all 0.16s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.filter-select {
  height: 40px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: #f8fafc;
  font-size: 14px;
  color: var(--text-secondary);
  width: 160px;
}

.primary-button {
  height: 44px;
  padding: 0 18px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(91, 92, 246, 0.25);
  cursor: pointer;
  transition: all 0.18s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(91, 92, 246, 0.32);
  filter: brightness(1.05);
}

.primary-button:active {
  transform: translateY(0);
}

/* ===== TABLE ===== */
.table-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
  margin-top: 16px;
}

:deep(.table-header) th {
  background: #f8fafc !important;
  color: var(--text-secondary) !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 16px 18px !important;
  border-bottom: 1px solid var(--border) !important;
}

:deep(.table-row) {
  background: var(--card-bg);
  transition: all 0.16s ease;
}

:deep(.table-row:hover) td {
  background: #f8fafc !important;
}

:deep(.table-cell) {
  padding: 16px 18px !important;
  vertical-align: middle;
  border-bottom: 1px solid #eef2f7 !important;
}

.product-title-block {
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}

.product-sku {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.product-thumb {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: #f1f5f9;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  object-fit: cover;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--category-bg);
  color: var(--category-text);
  font-size: 12px;
  font-weight: 700;
}

.stock-badge {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.stock-badge.danger {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.stock-badge.warning {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.stock-badge.success {
  background: var(--success-bg);
  color: var(--success-text);
}

.price-cell {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'DM Mono', monospace;
}

.price-cell.empty {
  color: var(--text-muted);
}

.icon-button {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.16s ease;
}

.icon-button:hover {
  background: #eef2ff;
  color: var(--primary);
  border-color: #c7d2fe;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: var(--card-bg);
  border-top: 1px solid #eef2f7;
}

:deep(.el-pagination.is-background .el-pager li) {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--border) !important;
  background: var(--card-bg) !important;
  color: var(--text-secondary) !important;
  font-weight: 700;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--primary) !important;
  color: white !important;
  border-color: var(--primary) !important;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
  }

  .table-card {
    overflow-x: auto;
  }
}
</style>

