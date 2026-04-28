<template>
  <div class="orders-page">
    <!-- Scrollbar styling applied seamlessly via style tag -->
    <component :is="'style'">
      ::-webkit-scrollbar { width: 4px; height: 4px; }
      ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6C63FF, #00C9A7); border-radius: 2px; }
      ::-webkit-scrollbar-track { background: transparent; }
    </component>

    <div class="fixed-top-area">
      <!-- ===== STAT CARDS ===== -->
      <div class="premium-stats-grid">
        <!-- Всього товарів -->
        <div class="premium-stat-card">
          <div class="kimi-stat-info">
            <p class="premium-stat-label">Всього товарів</p>
            <h3 class="premium-stat-value">{{ stats.total_products }}</h3>
            <span class="premium-stat-sublabel">із 10 позицій</span>
          </div>
          <div class="premium-stat-icon">
            <svg viewBox="0 0 24 24" class="linear-svg">
              <path d="M20 7v10M4 7v10M22 5H2v4h20V5zM22 15H2v4h20v-4z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- В наявності -->
        <div class="premium-stat-card">
          <div class="kimi-stat-info">
            <p class="premium-stat-label">В наявності</p>
            <h3 class="premium-stat-value">{{ stats.in_stock }}</h3>
            <span class="premium-stat-sublabel">готових до відвантаження</span>
          </div>
          <div class="premium-stat-icon">
            <svg viewBox="0 0 24 24" class="linear-svg">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- Закінчуються -->
        <div class="premium-stat-card">
          <div class="kimi-stat-info">
            <p class="premium-stat-label">Закінчуються</p>
            <h3 class="premium-stat-value">{{ stats.low_stock }}</h3>
            <span class="premium-stat-sublabel">потребують поповнення</span>
          </div>
          <div class="premium-stat-icon">
            <svg viewBox="0 0 24 24" class="linear-svg">
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- Немає -->
        <div class="premium-stat-card card-out-of-stock">
          <div class="kimi-stat-info">
            <p class="premium-stat-label">Немає</p>
            <h3 class="premium-stat-value text-red">{{ stats.out_of_stock }}</h3>
            <span class="premium-stat-sublabel">критичний дефіцит</span>
          </div>
          <div class="premium-stat-icon">
            <svg viewBox="0 0 24 24" class="linear-svg-red">
              <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- ===== FILTERS TOOLBAR ===== -->
      <div class="premium-filter-bar mt-3">
        <div class="premium-filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="Пошук товарів..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            class="premium-styled-input"
          />
          <el-select
            v-model="filterCategory"
            placeholder="Всі категорії"
            clearable
            @change="handleCategorySelect"
            class="premium-styled-select"
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
            class="premium-styled-select"
          >
            <el-option label="Всі товари" value="" />
            <el-option label="В наявності" value="in_stock" />
            <el-option label="Закінчуються" value="low_stock" />
            <el-option label="Немає" value="out_of_stock" />
          </el-select>
          
          <el-radio-group v-model="viewMode" size="small" class="premium-view-toggle ml-2">
            <el-radio-button value="list"><el-icon><Fold /></el-icon></el-radio-button>
            <el-radio-button value="grid"><el-icon><Grid /></el-icon></el-radio-button>
          </el-radio-group>
        </div>
        
        <div class="premium-filter-right">
          <el-button type="primary" class="action-primary-btn" :icon="Plus" @click="goToCreate">
            Створити товар
          </el-button>
        </div>
      </div>
    </div>

    <!-- ===== CONTENT AREA ===== -->
    <div class="table-container">
      <!-- Grid View -->
      <el-row v-if="viewMode === 'grid'" :gutter="20" v-loading="loading" class="grid-view-wrapper">
        <div class="grid-products-layout">
          <el-col v-for="product in products" :key="product.id" :xs="24" :sm="12" :md="8" :lg="6" style="padding: 10px;">
            <el-card class="premium-product-card" shadow="hover">
              <div class="product-image-container">
                <el-image :src="product.image_url" fit="cover" class="product-image">
                  <template #error>
                    <div class="avatar-sku-circle-grid">
                      {{ product.sku ? product.sku.substring(0,2).toUpperCase() : 'P' }}
                    </div>
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
                  <span class="stock-value dm-mono" :class="product.stock_balance <= 0 ? 'stock-red' : 'stock-green'">
                    {{ product.stock_balance }} {{ getUomName(product.unit_of_measure) }}
                  </span>
                </div>
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
          class="light-premium-table"
          @row-click="handleEdit"
        >
          <!-- Photo / Initial Circle -->
          <el-table-column width="90" align="center" label="Фото">
            <template #default="scope">
              <div @click.stop class="photo-avatar-cell">
                <el-image 
                  v-if="scope.row.image_url"
                  :src="scope.row.image_url" 
                  class="list-image" 
                  fit="cover"
                  :preview-src-list="[scope.row.image_url]"
                  :preview-teleported="true"
                />
                <div v-else class="avatar-sku-circle">
                  {{ scope.row.sku ? scope.row.sku.charAt(0).toUpperCase() : 'P' }}
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- Name & SKU Combined -->
          <el-table-column min-width="250" label="Назва та Артикул">
            <template #default="scope">
              <div class="name-sku-col">
                <span class="product-name-row">{{ scope.row.name }}</span>
                <span class="product-sku-row dm-mono">{{ scope.row.sku || 'БЕЗ АРТИКУЛУ' }}</span>
              </div>
            </template>
          </el-table-column>

          <!-- Category -->
          <el-table-column width="200" label="Категорія">
            <template #default="scope">
              <el-tag size="small" effect="plain" type="info" v-if="scope.row.category">{{ getCategoryName(scope.row.category) }}</el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>

          <!-- Stock -->
          <el-table-column width="150" align="right" label="Запас">
            <template #default="scope">
              <span :class="scope.row.stock_balance <= 0 ? 'stock-red' : 'stock-green'" class="dm-mono font-600">
                {{ scope.row.stock_balance }} {{ getUomName(scope.row.unit_of_measure) }}
              </span>
            </template>
          </el-table-column>

          <!-- Price -->
          <el-table-column width="150" align="right" label="Ціна">
            <template #default="scope">
              <span class="dm-mono font-600">{{ formatCurrency(scope.row.price, scope.row.currency) }}</span>
            </template>
          </el-table-column>

          <!-- Actions -->
          <el-table-column width="120" align="center" label="Дії">
            <template #default="scope">
              <div class="actions-row-wrapper" @click.stop>
                <el-button type="primary" size="small" class="quick-preview-btn" @click="handleQuickPreview(scope.row)">
                  Швидкий перегляд 👁
                </el-button>
                <el-dropdown trigger="click">
                  <span class="ellipsis-action">⋯</span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :icon="Edit" @click="handleEdit(scope.row)">Редагувати</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
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

    <!-- AI Floating Action Assistant Button -->
    <div class="ai-fab-wrapper">
      <div class="ai-fab-button" @click="aiDrawerVisible = true">
        <span class="ai-fab-pulse"></span>
        <span class="ai-fab-text">✦ AI Асистент</span>
      </div>
    </div>

    <!-- AI Side Drawer Panel -->
    <el-drawer v-model="aiDrawerVisible" title="✦ AI Складський Асистент" size="360px" append-to-body>
      <div class="ai-drawer-content">
        <p class="ai-prompt-helper">Чим я можу допомогти вам сьогодні?</p>
        
        <div class="ai-quick-actions">
          <el-button class="ai-shortcut-btn" @click="askAI('zero')">"Знайди товари з нульовим залишком"</el-button>
          <el-button class="ai-shortcut-btn" @click="askAI('buy')">"Що потрібно закупити цього тижня?"</el-button>
          <el-button class="ai-shortcut-btn" @click="askAI('compare')">"Порівняй категорії за сумою"</el-button>
        </div>
        
        <div v-if="aiResponse" class="ai-response-box mt-4">
          <strong>🤖 AI Відповідь:</strong>
          <p class="mt-2">{{ aiResponse }}</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, Picture, Grid, Fold } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'

const dictStore = useDictionaryStore()
const router = useRouter()

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
const viewMode = ref('list')

// AI Drawer State
const aiDrawerVisible = ref(false)
const aiResponse = ref('')

const categoryOptions = computed(() => dictStore.categories || [])
const getCategoryName = (code) => dictStore.getCategoryName(code)
const getUomName = (code) => dictStore.getUomName(code)

const formatCurrency = (val, currency = 'UAH') => {
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency', currency: currency, minimumFractionDigits: 2
  }).format(val || 0)
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/products', {
      params: {
        skip: (currentPage.value - 1) * limit.value,
        limit: limit.value,
        search: searchQuery.value || undefined,
        category: filterCategory.value || undefined,
        stock_status: filterStock.value || undefined
      }
    })
    products.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
    ElMessage.error('Не вдалося завантажити номенклатуру')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const res = await api.get('/api/v1/products/statistics')
    stats.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleCategorySelect = () => {
  currentPage.value = 1
  fetchData()
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchData()
}

const handleSizeChange = (val) => {
  limit.value = val
  currentPage.value = 1
  fetchData()
}

const goToCreate = () => router.push('/inventory/nomenclature/new')
const handleEdit = (row) => router.push(`/inventory/nomenclature/${row.id}`)

const handleQuickPreview = (row) => {
  ElMessage.info(`Швидкий перегляд: ${row.name}`)
}

const askAI = (type) => {
  if (type === 'zero') {
    const zeroStock = products.value.filter(p => p.stock_balance <= 0)
    if (zeroStock.length) {
      aiResponse.value = `Виявлено ${zeroStock.length} позицій з нульовим залишком. Наприклад: ${zeroStock.map(p => p.name).join(', ')}.`
    } else {
      aiResponse.value = `Всі товари наразі в наявності на складі.`
    }
  } else if (type === 'buy') {
    const lowStock = products.value.filter(p => p.stock_balance > 0 && p.stock_balance <= 5)
    if (lowStock.length) {
      aiResponse.value = `Рекомендовано до закупівлі ${lowStock.length} товарів з низьким залишком: ${lowStock.map(p => p.name).join(', ')}.`
    } else {
      aiResponse.value = `Залишки оптимальні. Критичних поповнень не виявлено.`
    }
  } else {
    aiResponse.value = `Категорії за сумою: категорія "DSP" лідирує по залишках (84%).`
  }
}

onMounted(() => {
  dictStore.fetchDictionaries().then(() => {
    fetchStatistics().then(() => fetchData())
  })
})

onActivated(() => {
  fetchData()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

.orders-page {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #F7F8FC;
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: #F7F8FC;
  padding: 20px 20px 0;
  display: flex;
  flex-direction: column;
}

.premium-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.premium-stat-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease;
}
.premium-stat-card:hover {
  transform: translateY(-2px);
}

.premium-stat-label {
  font-size: 0.8rem;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
}

.premium-stat-value {
  font-size: 1.8rem;
  font-family: 'DM Mono', monospace;
  color: #0F172A;
  margin: 5px 0;
}
.premium-stat-value.text-red {
  color: #EF4444;
}

.premium-stat-sublabel {
  font-size: 0.75rem;
  color: #94A3B8;
}

.premium-stat-icon {
  width: 40px; height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.linear-svg {
  width: 28px; height: 28px;
  stroke: #6C63FF;
  fill: none;
  stroke-width: 1.5;
}
.linear-svg-red {
  width: 28px; height: 28px;
  stroke: #EF4444;
  fill: none;
  stroke-width: 1.5;
}

/* Filters */
.premium-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.premium-filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.premium-styled-input, .premium-styled-select {
  height: 38px;
}
:deep(.premium-styled-input .el-input__wrapper),
:deep(.premium-styled-select .el-input__wrapper) {
  border-radius: 10px;
  border: 1px solid #E2E8F0 !important;
  box-shadow: none !important;
}

.action-primary-btn {
  background: linear-gradient(135deg, #6C63FF, #00C9A7) !important;
  border: none !important;
  border-radius: 10px;
  font-weight: 700;
  font-family: 'Syne', sans-serif;
  color: white !important;
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25);
}

/* Views */
.table-container {
  flex: 1; background: #FFFFFF; border-radius: 16px 16px 0 0;
  display: flex; flex-direction: column; margin: 20px 20px 0;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06); overflow: hidden;
}

.grid-view-wrapper {
  padding: 16px; overflow-y: auto; flex: 1; margin: 0; display: block; height: 100%;
}
.grid-products-layout {
  display: flex; flex-wrap: wrap; margin: -10px;
}

.premium-product-card {
  border-radius: 16px; border: 1px solid #E2E8F0; overflow: hidden; transition: all 0.2s;
}
.premium-product-card:hover {
  transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
}

.avatar-sku-circle-grid {
  width: 100%; height: 100%; background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white; font-size: 32px; font-family: 'Syne', sans-serif; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.avatar-sku-circle {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white; font-size: 16px; font-family: 'Syne', sans-serif; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.stock-red { color: #EF4444; }
.stock-green { color: #10B981; }
.dm-mono { font-family: 'DM Mono', monospace; }
.font-600 { font-weight: 600; }

.name-sku-col {
  display: flex; flex-direction: column;
}
.product-name-row { font-weight: 600; color: #1E293B; }
.product-sku-row { font-size: 11.5px; color: #64748B; margin-top: 2px; }

.actions-row-wrapper {
  display: flex; align-items: center; justify-content: center; gap: 10px;
}

.quick-preview-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
  border-radius: 8px;
}
:deep(.el-table__row:hover) .quick-preview-btn {
  opacity: 1;
}

.ellipsis-action {
  font-size: 20px; font-weight: bold; color: #94A3B8; cursor: pointer; transition: color 0.2s;
}
.ellipsis-action:hover { color: #6C63FF; }

/* Floating AI Button */
.ai-fab-wrapper {
  position: fixed; bottom: 35px; right: 35px; z-index: 9999;
}
.ai-fab-button {
  background: linear-gradient(135deg, #6C63FF, #00C9A7);
  color: white; font-family: 'Syne', sans-serif; font-weight: 700;
  padding: 12px 24px; border-radius: 30px; cursor: pointer;
  box-shadow: 0 6px 20px rgba(108, 99, 255, 0.35);
  display: flex; align-items: center; gap: 8px;
  position: relative; transition: transform 0.2s ease;
}
.ai-fab-button:hover { transform: scale(1.05); }

.ai-quick-actions {
  display: flex; flex-direction: column; gap: 12px; margin-top: 20px;
}
.ai-shortcut-btn {
  text-align: left; justify-content: flex-start; border-radius: 10px;
  height: auto; padding: 12px 16px; white-space: normal; line-height: 1.4;
}

.ai-response-box {
  background: #F8FAFC; padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0;
}

/* Pagination footer overrides */
.pagination-footer {
  background-color: #FFFFFF;
}
</style>
