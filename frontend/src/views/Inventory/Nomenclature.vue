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
            placeholder="Пошук за назвою, артикулом або категорією..."
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

        <!-- Колонки Dropdown -->
        <el-dropdown trigger="click" :hide-on-click="false" class="column-settings-dropdown">
          <button class="column-toggle-btn">
            ⚙️ Колонки
          </button>
          <template #dropdown>
            <el-dropdown-menu class="column-toggle-menu">
              <el-dropdown-item><el-checkbox v-model="visibleColumns.brand">Бренд</el-checkbox></el-dropdown-item>
              <el-dropdown-item><el-checkbox v-model="visibleColumns.weight">Вага</el-checkbox></el-dropdown-item>
              <el-dropdown-item><el-checkbox v-model="visibleColumns.dimensions">Розміри</el-checkbox></el-dropdown-item>
              <el-dropdown-item><el-checkbox v-model="visibleColumns.supplier">Постачальник</el-checkbox></el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
        @row-click="handleRowClick"
      >
        <!-- Photo -->
        <el-table-column width="64" class-name="table-cell-dense">
          <template #default="{ row }">
            <div @click.stop>
              <el-image 
                v-if="row.image_url"
                :src="row.image_url" 
                class="product-thumb-compact" 
                fit="cover"
              />
              <div v-else class="product-thumb-compact">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Name, SKU & Unit Block -->
        <el-table-column min-width="280" class-name="table-cell-dense">
          <template #header>Товар</template>
          <template #default="{ row }">
            <el-tooltip 
              :content="`Артикул: ${row.sku} | Одиниця: ${getUomName(row.unit_of_measure)} | Мін. запас: ${row.min_stock || 5}`"
              placement="top"
              :open-delay="400"
            >
              <div class="product-item-block">
                <div class="product-info-compact">
                  <div class="product-title-compact">
                    {{ row.name }}
                    <span 
                      v-if="row.stock_balance === 0" 
                      class="ai-warning-indicator" 
                      @click.stop="ElMessage.warning('AI: Запас нульовий! Рекомендується поповнити склад!')"
                    >
                      ⚠️
                    </span>
                  </div>
                  <div class="product-sku-compact">{{ row.sku }} • {{ getUomName(row.unit_of_measure) }}</div>
                </div>
              </div>
            </el-tooltip>
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

        <!-- Dynamic Columns -->
        <el-table-column v-if="visibleColumns.brand" label="Бренд" width="120" class-name="table-cell-dense">
          <template #default="{ row }">{{ row.brand || '-' }}</template>
        </el-table-column>

        <el-table-column v-if="visibleColumns.weight" label="Вага" width="100" class-name="table-cell-dense">
          <template #default="{ row }">{{ row.weight || '-' }}</template>
        </el-table-column>

        <el-table-column v-if="visibleColumns.dimensions" label="Розміри" width="120" class-name="table-cell-dense">
          <template #default="{ row }">{{ row.dimensions || '-' }}</template>
        </el-table-column>

        <el-table-column v-if="visibleColumns.supplier" label="Постачальник" width="140" class-name="table-cell-dense">
          <template #default="{ row }">{{ row.supplier || '-' }}</template>
        </el-table-column>

        <!-- Stock -->
        <el-table-column width="140" align="center" class-name="table-cell-dense">
          <template #header>Запас</template>
          <template #default="{ row }">
            <span class="stock-badge-compact" :class="getStockBadgeClass(row.stock_balance, row.min_stock)">
              {{ getStockBadgeText(row.stock_balance, row.min_stock) }} ({{ row.stock_balance }})
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
                  ✏️
                </button>
              </el-tooltip>
              <el-tooltip content="Залишки" placement="top">
                <button class="action-btn-dense stock" @click="handleViewStock(row)">
                  📦
                </button>
              </el-tooltip>
              <el-tooltip content="Рух" placement="top">
                <button class="action-btn-dense movement" @click="handleViewMovement(row)">
                  📊
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

    <!-- ===== SIDE DRAWER ===== -->
    <el-drawer
      v-model="drawerVisible"
      title="Деталі товару"
      size="480px"
      direction="rtl"
      :destroy-on-close="true"
    >
      <div v-if="selectedProduct" class="drawer-content-dense">
        <div class="drawer-header-block">
          <h3>{{ selectedProduct.name }}</h3>
          <p class="drawer-sku">{{ selectedProduct.sku }} • {{ getUomName(selectedProduct.unit_of_measure) }}</p>
        </div>

        <el-divider />

        <div class="drawer-section">
          <h4>Запаси по складах</h4>
          <el-table :data="warehouseStock" style="width: 100%" size="small">
            <el-table-column prop="name" label="Склад" />
            <el-table-column prop="balance" label="Залишок" align="right">
              <template #default="{ row }">{{ row.balance }} {{ getUomName(selectedProduct.unit_of_measure) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <el-divider />

        <div class="drawer-section">
          <h4>Останні рухи</h4>
          <el-table :data="productMovements" style="width: 100%" size="small">
            <el-table-column prop="date" label="Дата" width="100" />
            <el-table-column prop="type" label="Операція" width="100" />
            <el-table-column prop="qty" label="К-сть" align="right" width="70" />
            <el-table-column prop="note" label="Коментар" />
          </el-table>
        </div>
      </div>
    </el-drawer>
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

// UI States
const drawerVisible = ref(false)
const selectedProduct = ref(null)
const warehouseStock = ref([])
const productMovements = ref([])

const visibleColumns = ref({
  brand: false,
  weight: false,
  dimensions: false,
  supplier: false
})

const handleRowClick = (row) => {
  selectedProduct.value = row
  drawerVisible.value = true
  warehouseStock.value = [
    { name: 'Головний склад', balance: Math.floor(row.stock_balance * 0.7) },
    { name: 'Склад №2', balance: Math.floor(row.stock_balance * 0.3) }
  ]
  productMovements.value = [
    { date: '2026-04-28', type: 'Прихід', qty: 10, note: 'Закупівля №104' },
    { date: '2026-04-25', type: 'Списання', qty: 2, note: 'Виробництво' }
  ]
}

// Data State
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

const getStockBadgeClass = (qty, min = 5) => {
  if (qty <= 0) return 'danger'
  if (qty < min) return 'warning'
  return 'success'
}

const getStockBadgeText = (qty, min = 5) => {
  if (qty <= 0) return 'Немає'
  if (qty < min) return 'Закінчується'
  return 'В нормі'
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

  --success-bg: #dcfce7;
  --success-text: #15803d;

  --warning-bg: #fef3c7;
  --warning-text: #b45309;

  --danger-bg: #fee2e2;
  --danger-text: #b91c1c;

  --category-bg: #f1f5f9;
  --category-text: #475569;

  background-color: var(--page-bg);
  padding: 16px;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--text-main);
}

/* ===== STAT CARDS ===== */
.stats-row-dense {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.stats-card-dense {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  height: 54px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}
.stats-card-dense__icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
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
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}
.stats-card-dense__value {
  font-size: 18px;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  line-height: 1.1;
}

/* ===== TOOLBAR ===== */
.toolbar-dense {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}
.toolbar-dense__left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.search-dense-wrapper {
  position: relative;
  width: 280px;
}
.search-dense-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
.search-dense-input {
  width: 100%;
  height: 36px;
  border-radius: 6px;
  border: 1px solid var(--border-dense);
  padding: 0 10px 0 32px;
  font-size: 13px;
}
.search-dense-input:focus {
  outline: none;
  border-color: var(--primary);
}
.filter-dense-select {
  :deep(.el-select__wrapper) {
    height: 36px !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-dense) !important;
  }
}
.column-toggle-btn {
  height: 36px;
  padding: 0 12px;
  border-radius: 6px;
  border: 1px solid var(--border-dense);
  background: var(--card-bg);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.column-toggle-menu {
  padding: 8px 12px;
}
.primary-dense-button {
  height: 38px;
  padding: 0 16px;
  background: linear-gradient(135deg, var(--primary), #7c3aed);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ===== TABLE ===== */
.table-dense-card {
  background: var(--card-bg);
  border: 1px solid var(--border-dense);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  overflow: hidden;
}
:deep(.table-header-dense th) {
  background: #f8fafc !important;
  color: var(--text-secondary) !important;
  font-weight: 700 !important;
  font-size: 11px !important;
  text-transform: uppercase;
  padding: 12px 16px !important;
}
:deep(.table-row-dense) {
  height: 64px;
  cursor: pointer;
  transition: background 0.15s ease;
}
:deep(.table-row-dense:hover td) {
  background: #f1f5f9 !important;
}
:deep(.table-cell-dense) {
  padding: 8px 16px !important;
}

.product-item-block {
  display: flex;
  align-items: center;
  gap: 10px;
}
.product-thumb-compact {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid var(--border-dense);
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}
.product-info-compact {
  display: flex;
  flex-direction: column;
}
.product-title-compact {
  font-weight: 700;
  font-size: 13px;
}
.product-sku-compact {
  font-size: 11px;
  color: var(--text-muted);
}
.ai-warning-indicator {
  margin-left: 6px;
  cursor: help;
}

.category-badge-compact {
  display: inline-block;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: var(--category-bg);
  color: var(--category-text);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.stock-badge-compact {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}
.stock-badge-compact.danger { background: var(--danger-bg); color: var(--danger-text); }
.stock-badge-compact.warning { background: var(--warning-bg); color: var(--warning-text); }
.stock-badge-compact.success { background: var(--success-bg); color: var(--success-text); }

.actions-cell-dense {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}
.action-btn-dense {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border-dense);
  background: #f8fafc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  font-size: 14px;
}
.action-btn-dense:hover {
  background: #eef2ff;
  border-color: #6366f1;
  color: #6366f1;
}

/* ===== DRAWER ===== */
.drawer-content-dense {
  padding: 0 16px;
}
.drawer-header-block h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
}
.drawer-sku {
  color: var(--text-muted);
  font-size: 12px;
}
.drawer-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>



