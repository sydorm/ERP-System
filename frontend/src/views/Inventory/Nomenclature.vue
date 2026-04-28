<template>
  <div class="orders-page" :class="{ 'dense-mode': isCompactMode }">
    <div class="top-section">
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
              placeholder="Пошук за назвою, артикулом..."
              class="search-dense-input"
              @input="handleSearch"
            />
          </div>
          
          <el-select
            v-model="filterCategory"
            placeholder="Всі категорії"
            clearable
            @change="handleCategorySelect"
            class="filter-dense-select pill-select"
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
            class="filter-dense-select pill-select"
            style="width: 160px;"
          >
            <el-option label="Всі товари" value="" />
            <el-option label="В наявності" value="in_stock" />
            <el-option label="Закінчуються" value="low_stock" />
            <el-option label="Немає" value="out_of_stock" />
          </el-select>

          <!-- Колонки Dropdown -->
          <el-dropdown trigger="click" :hide-on-click="false">
            <button class="column-toggle-btn">
              ⚙️ Колонки
            </button>
            <template #dropdown>
              <el-dropdown-menu class="column-toggle-menu">
                <el-dropdown-item><el-checkbox v-model="visibleColumns.brand">Бренд</el-checkbox></el-dropdown-item>
                <el-dropdown-item><el-checkbox v-model="visibleColumns.weight">Вага</el-checkbox></el-dropdown-item>
                <el-dropdown-item><el-checkbox v-model="visibleColumns.dimensions">Розміри</el-checkbox></el-dropdown-item>
                <el-dropdown-item><el-checkbox v-model="visibleColumns.supplier">Постачальник</el-checkbox></el-dropdown-item>
                <el-dropdown-item divided>
                  <el-checkbox v-model="isCompactMode" @change="toggleCompactMode">Компактний режим</el-checkbox>
                </el-dropdown-item>
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
    </div>

    <!-- ===== TABLE SECTION ===== -->
    <div class="table-section table-dense-card" v-loading="loading">
      <el-table
        :data="products"
        style="width: 100%"
        height="100%"
        :row-class-name="() => 'table-row-dense'"
        :header-row-class-name="() => 'table-header-dense'"
        @row-click="handleRowClick"
      >
        <!-- Left Indicator Line (via CSS) -->
        <el-table-column width="16" class-name="indicator-col">
          <template #default="{ row }">
            <div class="row-status-indicator" :class="getStockBadgeClass(row.stock_balance, row.min_stock)"></div>
          </template>
        </el-table-column>

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
            <div class="product-item-block">
              <div class="product-info-compact">
                <div class="product-title-compact">
                  {{ row.name }}
                  
                  <!-- AI Popover instead of Tooltip -->
                  <el-popover
                    v-if="row.stock_balance === 0"
                    placement="top"
                    :width="220"
                    trigger="click"
                    popper-class="premium-ai-popover"
                  >
                    <template #reference>
                      <span class="ai-warning-dot" @click.stop></span>
                    </template>
                    <div class="ai-popover-content">
                      <h5 class="ai-popover-title">🤖 AI Аналітика</h5>
                      <p class="ai-popover-desc">Критичний залишок! Необхідно поповнити запаси цього товару.</p>
                    </div>
                  </el-popover>
                </div>
                <div class="product-sku-compact">
                  {{ row.sku }} <span class="sku-divider">·</span> {{ getUomName(row.unit_of_measure) }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Category -->
        <el-table-column width="180" class-name="table-cell-dense">
          <template #header>Категорія</template>
          <template #default="{ row }">
            <span class="category-badge-premium" :title="getCategoryName(row.category)">
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
            <span class="stock-badge-premium" :class="getStockBadgeClass(row.stock_balance, row.min_stock)">
              {{ getStockBadgeText(row.stock_balance, row.min_stock) }}
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

        <!-- Actions (4 icons) -->
        <el-table-column width="180" align="right" class-name="table-cell-dense">
          <template #header>Дії</template>
          <template #default="{ row }">
            <div class="actions-cell-premium" @click.stop>
              <button class="action-btn-premium" @click="handleEdit(row)" title="Редагувати">
                ✏️
              </button>
              <button class="action-btn-premium" @click="handleViewStock(row)" title="Склад">
                📦
              </button>
              <button class="action-btn-premium" @click="handleViewMovement(row)" title="Рух">
                📊
              </button>
              <button class="action-btn-premium" @click="handleRowClick(row)" title="Перегляд">
                👁️
              </button>
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
      title="Інформація про товар"
      size="480px"
      direction="rtl"
      :destroy-on-close="true"
    >
      <div v-if="selectedProduct" class="drawer-content-dense">
        <div class="drawer-header-block">
          <h3>{{ selectedProduct.name }}</h3>
          <p class="drawer-sku">{{ selectedProduct.sku }} <span class="sku-divider">·</span> {{ getUomName(selectedProduct.unit_of_measure) }}</p>
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
="productMovements" style="width: 100%" size="small">
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

// Compact mode state
const isCompactMode = ref(localStorage.getItem('nomenclature_dense_mode') === 'true')
const toggleCompactMode = (val) => {
  isCompactMode.value = val
  localStorage.setItem('nomenclature_dense_mode', val)
}

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
  --page-bg: #f4f7fb;
  --card-bg: rgba(255, 255, 255, 0.82);
  --text-main: #0f172a;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border-premium: rgba(226, 232, 240, 0.9);
  
  --primary: #6366f1;
  --primary-dark: #4f46e5;

  --success-bg: #dcfce7;
  --success-text: #16a34a;

  --warning-bg: #fef3c7;
  --warning-text: #d97706;

  --danger-bg: #fee2e2;
  --danger-text: #dc2626;

  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: radial-gradient(circle at top left, rgba(99,102,241,0.08), transparent 28%), var(--page-bg);
  padding: 20px;
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--text-main);
  box-sizing: border-box;
}

/* ===== STAT CARDS ===== */
.stats-row-dense {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.stats-card-dense {
  background: var(--card-bg);
  border: 1px solid var(--border-premium);
  border-radius: 18px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease;
}
.stats-card-dense:hover {
  transform: translateY(-1px);
}
.stats-card-dense__icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
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
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.stats-card-dense__value {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.2;
}

/* ===== TOOLBAR ===== */
.toolbar-dense {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
  margin-top: 16px;
}
.toolbar-dense__left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-dense-wrapper {
  position: relative;
  width: 300px;
}
.search-dense-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
.search-dense-input {
  width: 100%;
  height: 42px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 0 14px 0 40px;
  font-size: 14px;
  background: #ffffff;
  transition: all 0.2s ease;
}
.search-dense-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.filter-dense-select.pill-select {
  :deep(.el-select__wrapper) {
    height: 42px !important;
    border-radius: 999px !important;
    border: 1px solid #e2e8f0 !important;
    background: #f8fafc !important;
    box-shadow: none !important;
  }
}

.column-toggle-btn {
  height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}
.column-toggle-btn:hover {
  background: #f8fafc;
  border-color: var(--primary);
}

.primary-dense-button {
  height: 44px;
  padding: 0 20px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 28px rgba(99, 102, 241, 0.28);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.primary-dense-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 34px rgba(99, 102, 241, 0.34);
}

/* ===== TABLE ===== */
.table-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06);
  margin-top: 16px;
}

:deep(.table-header-dense th) {
  background: #f8fafc !important;
  color: #64748b !important;
  font-weight: 800 !important;
  font-size: 11px !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 16px !important;
  height: 52px;
  border-bottom: 1px solid #eef2f7;
}
:deep(.table-row-dense) {
  height: 68px;
  cursor: pointer;
  transition: all 0.16s ease;
}
:deep(.table-row-dense:hover td) {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.05), rgba(255, 255, 255, 0)) !important;
}
:deep(.table-cell-dense) {
  padding: 12px 16px !important;
  border-bottom: 1px solid #eef2f7 !important;
}

.indicator-col {
  padding: 0 !important;
}
.row-status-indicator {
  width: 3px;
  height: 40px;
  border-radius: 0 4px 4px 0;
}
.row-status-indicator.danger { background: var(--danger-text); }
.row-status-indicator.warning { background: var(--warning-text); }
.row-status-indicator.success { background: var(--success-text); }

.product-item-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.product-thumb-compact {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(226,232,240,0.8);
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}
.product-info-compact {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.product-title-compact {
  font-weight: 700;
  font-size: 14px;
  color: #0f172a;
  display: flex;
  align-items: center;
}
.product-sku-compact {
  font-size: 12px;
  color: var(--text-muted);
}
.sku-divider {
  margin: 0 4px;
}
.ai-warning-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #f59e0b;
  border-radius: 50%;
  margin-left: 8px;
  cursor: pointer;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}

.category-badge-premium {
  display: inline-block;
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: #eef2ff;
  color: #4f46e5;
  border: 1px solid #dbe4ff;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.stock-badge-premium {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.stock-badge-premium.danger { background: var(--danger-bg); color: var(--danger-text); }
.stock-badge-premium.warning { background: var(--warning-bg); color: var(--warning-text); }
.stock-badge-premium.success { background: var(--success-bg); color: var(--success-text); }

.price-cell-dense {
  font-weight: 800;
  font-size: 14px;
  color: #0f172a;
}

.actions-cell-premium {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.action-btn-premium {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.16s ease;
  font-size: 14px;
}
.action-btn-premium:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #4f46e5;
  transform: translateY(-1px);
}

/* ===== COMPACT MODE MODIFIERS ===== */
.dense-mode {
  padding: 12px;
  height: calc(100vh - 64px);
}
.dense-mode .stats-row-dense {
  gap: 8px;
}
.dense-mode .stats-card-dense {
  height: 44px;
  border-radius: 12px;
  padding: 8px 12px;
}
.dense-mode .stats-card-dense__value {
  font-size: 18px;
}
.dense-mode .toolbar-dense {
  height: 48px;
  padding: 8px;
  border-radius: 12px;
  margin-top: 8px;
}
.dense-mode .search-dense-input {
  height: 34px;
}
.dense-mode .table-section {
  border-radius: 16px;
  margin-top: 8px;
}
.dense-mode :deep(.table-row-dense) {
  height: 56px;
}
.dense-mode :deep(.table-cell-dense) {
  padding: 6px 12px !important;
}

/* AI Popover override */
:deep(.premium-ai-popover) {
  background: #ffffff !important;
  border-radius: 14px !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.15) !important;
  padding: 12px !important;
}
.ai-popover-title {
  margin: 0 0 6px 0;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}
.ai-popover-desc {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}
</style>




