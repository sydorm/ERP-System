<template>
  <div class="orders-page erp-dense-container">
    <!-- ===== STAT CARDS ===== -->
    <div class="stats-row-dense kimi-mb-4">
      <!-- Всього товарів -->
      <div class="stats-card-dense">
        <div class="stats-card-dense__icon total">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stats-card-dense__content">
          <span class="stats-card-dense__label">Всього товарів</span>
          <span class="stats-card-dense__value">{{ stats.total_products }}</span>
        </div>
      </div>

      <!-- В наявності -->
      <div class="stats-card-dense">
        <div class="stats-card-dense__icon success">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stats-card-dense__content">
          <span class="stats-card-dense__label">В наявності</span>
          <span class="stats-card-dense__value">{{ stats.in_stock }}</span>
        </div>
      </div>

      <!-- Закінчуються -->
      <div class="stats-card-dense">
        <div class="stats-card-dense__icon warning">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stats-card-dense__content">
          <span class="stats-card-dense__label">Закінчуються</span>
          <span class="stats-card-dense__value">{{ stats.low_stock }}</span>
        </div>
      </div>

      <!-- Немає -->
      <div class="stats-card-dense">
        <div class="stats-card-dense__icon danger">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stats-card-dense__content">
          <span class="stats-card-dense__label">Немає</span>
          <span class="stats-card-dense__value">{{ stats.out_of_stock }}</span>
        </div>
      </div>
    </div>

    <!-- ===== FILTERS TOOLBAR ===== -->
    <div class="toolbar-dense kimi-mb-4">
      <div class="toolbar-dense__left">
        <div class="search-dense-wrapper">
          <el-icon class="search-dense-icon"><Search /></el-icon>
          <input
            v-model="searchQuery"
            placeholder="Пошук за назвою або артикулом..."
            class="search-dense-input"
            @input="handleSearch"
          />
        </div>
        
        <el-select
          v-model="filterCategory"
          placeholder="Всі категорії"
          clearable
          @change="handleCategorySelect"
          class="filter-dense-select"
          style="width: 180px;"
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
          class="filter-dense-select"
          style="width: 160px;"
        >
          <el-option label="Всі товари" value="" />
          <el-option label="В наявності" value="in_stock" />
          <el-option label="Закінчуються" value="low_stock" />
          <el-option label="Немає" value="out_of_stock" />
        </el-select>
      </div>
      
      <div class="toolbar-dense__right">
        <button class="primary-dense-button" @click="goToCreate">
          <el-icon><Plus /></el-icon> Створити товар
        </button>
      </div>
    </div>

    <!-- ===== TABLE ===== -->
    <div class="table-dense-card" v-loading="loading">
      <el-table
        :data="products"
        style="width: 100%"
        height="calc(100vh - 220px)"
        :row-class-name="() => 'table-row-dense'"
        :header-row-class-name="() => 'table-header-dense'"
        @row-click="handleEdit"
      >
        <!-- Name & SKU Block -->
        <el-table-column min-width="280" class-name="table-cell-dense">
          <template #header>Товар</template>
          <template #default="{ row }">
            <div class="product-item-block">
              <div @click.stop>
                <el-image 
                  v-if="row.image_url"
                  :src="row.image_url" 
                  class="product-thumb-compact" 
                  fit="cover"
                  :preview-src-list="[row.image_url]"
                  :preview-teleported="true"
                  :hide-on-click-modal="true"
                />
                <div v-else class="product-thumb-compact">
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
              <div class="product-info-compact">
                <div class="product-title-compact">{{ row.name }}</div>
                <div class="product-sku-compact">{{ row.sku }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Category -->
        <el-table-column width="160" class-name="table-cell-dense">
          <template #header>Категорія</template>
          <template #default="{ row }">
            <span class="category-badge-compact" :title="getCategoryName(row.category)">
              {{ getCategoryName(row.category) }}
            </span>
          </template>
        </el-table-column>

        <!-- Stock -->
        <el-table-column width="140" align="center" class-name="table-cell-dense">
          <template #header>Запас</template>
          <template #default="{ row }">
            <span class="stock-badge-compact" :class="getStockBadgeClass(row.stock_balance)">
              {{ row.stock_balance }} {{ getUomName(row.unit_of_measure) }}
            </span>
          </template>
        </el-table-column>

        <!-- Price -->
        <el-table-column width="120" align="right" class-name="table-cell-dense">
          <template #header>Ціна</template>
          <template #default="{ row }">
            <span class="price-cell-dense" :class="{ 'empty': !row.price }">
              {{ formatCurrency(row.price, row.currency) }}
            </span>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column width="140" align="right" class-name="table-cell-dense">
          <template #header>Дії</template>
          <template #default="{ row }">
            <div class="actions-cell-dense" @click.stop>
              <el-tooltip content="Редагувати" placement="top">
                <button class="action-btn-dense edit" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="Залишки" placement="top">
                <button class="action-btn-dense stock" @click="handleViewStock(row)">
                  <el-icon><Box /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="Рух" placement="top">
                <button class="action-btn-dense movement" @click="handleViewMovement(row)">
                  <el-icon><Coordinate /></el-icon>
                </button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-dense">
        <el-select v-model="limit" size="small" style="width: 70px;" @change="handleSizeChange">
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

const handleViewStock = (row) => {
  ElMessage.info(`Залишки для ${row.name}`)
}

const handleViewMovement = (row) => {
  ElMessage.info(`Рух товару для ${row.name}`)
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
  --page-bg: #f8fafc;
  --card-bg: #ffffff;
  --text-main: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --border-dense: #e2e8f0;

  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-gradient-start: #5b5cf6;
  --primary-gradient-end: #7c3aed;

  --success-bg: #dcfce7;
  --success-text: #15803d;

  --warning-bg: #fef3c7;
  --warning-text: #b45309;

  --danger-bg: #fee2e2;
  --danger-text: #b91c1c;

  --category-bg: #f1f5f9;
  --category-text: #475569;

  background-color: var(--page-bg);
  padding: 16px 20px;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--text-main);
  font-size: 13px;
}

/* ===== STAT CARDS COMPACT ===== */
.stats-row-dense {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.stats-card-dense {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02);
  transition: all 0.15s ease;
}

.stats-card-dense:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

.stats-card-dense__icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.stats-card-dense__icon.total { background: #eff6ff; color: #2563eb; }
.stats-card-dense__icon.success { background: var(--success-bg); color: var(--success-text); }
.stats-card-dense__icon.warning { background: var(--warning-bg); color: var(--warning-text); }
.stats-card-dense__icon.danger { background: var(--danger-bg); color: var(--danger-text); }

.stats-card-dense__content {
  display: flex;
  flex-direction: column;
}

.stats-card-dense__label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.stats-card-dense__value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'DM Mono', monospace;
  line-height: 1.2;
}

/* ===== DENSE TOOLBAR ===== */
.toolbar-dense {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02);
  height: 56px;
}

.toolbar-dense__left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.search-dense-wrapper {
  position: relative;
  flex: 1;
  max-width: 360px;
}

.search-dense-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
}

.search-dense-input {
  width: 100%;
  height: 38px;
  border-radius: 8px;
  border: 1px solid var(--border-dense);
  padding: 0 12px 0 36px;
  background: var(--card-bg);
  color: var(--text-main);
  font-size: 13px;
  transition: all 0.15s ease;
}

.search-dense-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.filter-dense-select {
  :deep(.el-select__wrapper) {
    height: 38px !important;
    border-radius: 8px !important;
    background: #f8fafc !important;
    border: 1px solid var(--border-dense) !important;
    box-shadow: none !important;
  }
}

.primary-dense-button {
  height: 38px;
  padding: 0 16px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(91, 92, 246, 0.2);
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.primary-dense-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(91, 92, 246, 0.3);
}

/* ===== DENSE TABLE ===== */
.table-dense-card {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.03);
  margin-top: 12px;
}

:deep(.table-header-dense) th {
  background: #f8fafc !important;
  color: var(--text-secondary) !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px !important;
  border-bottom: 1px solid var(--border-dense) !important;
}

:deep(.table-row-dense) {
  background: var(--card-bg);
  transition: all 0.15s ease;
  cursor: pointer;
}

:deep(.table-row-dense:hover) td {
  background: #f8fafc !important;
}

:deep(.table-cell-dense) {
  padding: 8px 16px !important;
  vertical-align: middle;
  border-bottom: 1px solid #f1f5f9 !important;
  height: 64px;
}

.product-item-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-thumb-compact {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f1f5f9;
  border: 1px solid var(--border-dense);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  object-fit: cover;
}

.product-info-compact {
  display: flex;
  flex-direction: column;
}

.product-title-compact {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 240px;
}

.product-sku-compact {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}

.category-badge-compact {
  display: inline-block;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 22px;
  padding: 0 8px;
  border-radius: 4px;
  background: var(--category-bg);
  color: var(--category-text);
  font-size: 11px;
  font-weight: 600;
  line-height: 22px;
}

.stock-badge-compact {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
}

.stock-badge-compact.danger { background: var(--danger-bg); color: var(--danger-text); }
.stock-badge-compact.warning { background: var(--warning-bg); color: var(--warning-text); }
.stock-badge-compact.success { background: var(--success-bg); color: var(--success-text); }

.price-cell-dense {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
  font-family: 'DM Mono', monospace;
}

.price-cell-dense.empty {
  color: var(--text-muted);
}

.actions-cell-dense {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.action-btn-dense {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #f8fafc;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn-dense:hover {
  background: #eef2ff;
  color: var(--primary);
  border-color: #c7d2fe;
}

.action-btn-dense.edit:hover {
  color: #6366f1;
  background: #eff6ff;
}
.action-btn-dense.stock:hover {
  color: #2563eb;
  background: #eff6ff;
}
.action-btn-dense.movement:hover {
  color: #7c3aed;
  background: #f5f3ff;
}

.pagination-dense {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--card-bg);
  border-top: 1px solid #f1f5f9;
}

:deep(.el-pagination.is-background .el-pager li) {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  border: 1px solid var(--border-dense) !important;
  background: var(--card-bg) !important;
  color: var(--text-secondary) !important;
  font-weight: 600;
  font-size: 12px;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--primary) !important;
  color: white !important;
  border-color: var(--primary) !important;
}
</style>


