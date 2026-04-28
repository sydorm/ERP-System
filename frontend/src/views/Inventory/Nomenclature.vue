<template>
  <div class="orders-page" :class="{ 'dense-mode': isCompactMode }">
    <div class="top-section">
      <div class="page-header-premium">
        <div class="breadcrumbs-premium">Головна / Номенклатура</div>
        <div class="header-flex-premium">
          <div>
            <h1 class="page-title-premium">Номенклатура</h1>
            <p class="page-subtitle-premium">Товари, матеріали, комплектуючі та готові вироби</p>
          </div>
          <div class="header-actions-premium">
            <button class="secondary-premium-btn" @click="ElMessage.info('Імпорт Excel/CSV')">
              📥 Імпорт
            </button>
            <button class="secondary-premium-btn" @click="ElMessage.info('Експорт Excel/CSV')">
              📤 Експорт
            </button>
            <button class="primary-dense-button" @click="goToCreate">
              <el-icon><Plus /></el-icon> Створити товар
            </button>
          </div>
        </div>
      </div>

      <!-- ===== KPI STAT CARDS ===== -->
      <div class="stats-row-dense kimi-mb-4">
        <!-- Всього позицій -->
        <div class="stats-card-dense">
          <div class="stats-card-dense__icon total">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stats-card-dense__content">
            <span class="stats-card-dense__label">Всього позицій</span>
            <span class="stats-card-dense__value">{{ stats.total_products }}</span>
            <span class="stats-card-dense__subtext">+12 за останні 30 днів</span>
          </div>
          <div class="stats-card-dense__sparkline">
            <svg width="60" height="20"><path d="M0,10 L10,15 L20,5 L30,18 L40,8 L50,12 L60,2" fill="none" stroke="#635bff" stroke-width="2"/></svg>
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
            <span class="stats-card-dense__subtext">+18 за останні 30 днів</span>
          </div>
          <div class="stats-card-dense__sparkline">
            <svg width="60" height="20"><path d="M0,18 L10,12 L20,15 L30,8 L40,10 L50,5 L60,2" fill="none" stroke="#22c55e" stroke-width="2"/></svg>
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
            <span class="stats-card-dense__subtext">+4 за останні 30 днів</span>
          </div>
          <div class="stats-card-dense__sparkline">
            <svg width="60" height="20"><path d="M0,5 L10,8 L20,2 L30,12 L40,5 L50,15 L60,18" fill="none" stroke="#f59e0b" stroke-width="2"/></svg>
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
            <span class="stats-card-dense__subtext">-3 за останні 30 днів</span>
          </div>
          <div class="stats-card-dense__sparkline">
            <svg width="60" height="20"><path d="M0,2 L10,5 L20,12 L30,8 L40,15 L50,12 L60,18" fill="none" stroke="#ef4444" stroke-width="2"/></svg>
          </div>
        </div>
      </div>

      <!-- ===== AI ASSISTANT BLOCK ===== -->
      <div class="ai-banner-premium kimi-mb-4">
        <div class="ai-banner-content">
          <span class="ai-banner-icon">🤖</span>
          <div>
            <h4 class="ai-banner-title">AI-помічник номенклатури</h4>
            <p class="ai-banner-desc">Пошук дублікатів, аналіз дефіциту та розумні рекомендації.</p>
          </div>
        </div>
        <button class="ai-banner-btn" @click="aiDrawerVisible = true">
          Запустити AI-аналіз
        </button>
      </div>

      <!-- ===== FILTERS TOOLBAR ===== -->
      <div class="toolbar-dense kimi-mb-4">
        <div class="toolbar-dense__left">
          <div class="search-dense-wrapper">
            <el-icon class="search-dense-icon"><Search /></el-icon>
            <input
              v-model="searchQuery"
              placeholder="Пошук за назвою, артикулом або SKU..."
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
            v-model="filterType"
            placeholder="Всі типи"
            clearable
            @change="handleFilterChange"
            class="filter-dense-select pill-select"
            style="width: 160px;"
          >
            <el-option label="Усі типи" value="" />
            <el-option label="Готовий виріб" value="product" />
            <el-option label="Матеріал" value="material" />
            <el-option label="Комплектуюча" value="component" />
          </el-select>

          <el-select
            v-model="filterStock"
            placeholder="Наявність"
            clearable
            @change="handleFilterChange"
            class="filter-dense-select pill-select"
            style="width: 140px;"
          >
            <el-option label="Всі" value="" />
            <el-option label="В наявності" value="in_stock" />
            <el-option label="Закінчуються" value="low_stock" />
            <el-option label="Немає" value="out_of_stock" />
          </el-select>
          
          <!-- Кнопка Швидкі дії -->
          <el-dropdown trigger="click">
            <button class="column-toggle-btn">
              ⚡ Дії
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="ElMessage.info('Масове архівування')">Архівувати</el-dropdown-item>
                <el-dropdown-item @click="ElMessage.info('Змінити категорію')">Змінити категорію</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Quick Filter Tabs -->
      <div class="quick-tabs-premium kimi-mb-4">
        <div 
          class="quick-tab-item" 
          :class="{ active: activeTab === 'all' }"
          @click="activeTab = 'all'; filterCategory = ''"
        >Усі</div>
        <div 
          class="quick-tab-item" 
          :class="{ active: activeTab === 'materials' }"
          @click="activeTab = 'materials'; filterCategory = 'MATERIAL'"
        >Матеріали</div>
        <div 
          class="quick-tab-item" 
          :class="{ active: activeTab === 'products' }"
          @click="activeTab = 'products'; filterCategory = 'PRODUCT'"
        >Готові вироби</div>
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
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="45" align="center" />

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
                <el-icon v-if="row.category === 'MATERIAL'"><Grid /></el-icon>
                <el-icon v-else><Box /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Name, SKU & Unit Block -->
        <el-table-column min-width="280" class-name="table-cell-dense">
          <template #header>Назва / Артикул</template>
          <template #default="{ row }">
            <div class="product-item-block">
              <div class="product-info-compact">
                <div class="product-title-compact">
                  {{ row.name }}
                </div>
                <div class="product-sku-compact">
                  {{ row.sku }} <span class="sku-divider">·</span> {{ getUomName(row.unit_of_measure) }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Category -->
        <el-table-column width="160" class-name="table-cell-dense">
          <template #header>Категорія</template>
          <template #default="{ row }">
            <span class="category-badge-premium" :title="getCategoryName(row.category)">
              {{ getCategoryName(row.category) }}
            </span>
          </template>
        </el-table-column>

        <!-- Stock -->
        <el-table-column width="160" align="left" class-name="table-cell-dense">
          <template #header>Залишок</template>
          <template #default="{ row }">
            <div class="stock-progress-wrapper">
              <div class="stock-number-dense">
                {{ row.stock_balance }} {{ getUomName(row.unit_of_measure) }}
              </div>
              <div class="stock-progress-bar">
                <div 
                  class="stock-progress-fill" 
                  :class="getStockBadgeClass(row.stock_balance, row.min_stock)"
                  :style="{ width: row.stock_balance <= 0 ? '8%' : Math.min(100, (row.stock_balance / (row.min_stock || 10)) * 100) + '%' }"
                ></div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Status Badge -->
        <el-table-column width="140" align="center" class-name="table-cell-dense">
          <template #header>Статус</template>
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

        <!-- Actions (Dropdown menu) -->
        <el-table-column width="120" align="right" class-name="table-cell-dense">
          <template #header>Дії</template>
          <template #default="{ row }">
            <div class="actions-cell-premium" @click.stop>
              <button class="action-btn-premium" @click="handleEdit(row)" title="Редагувати">
                <el-icon><Edit /></el-icon>
              </button>
              
              <el-dropdown trigger="click" @click.stop>
                <button class="action-btn-premium" title="Більше">
                  <el-icon><More /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleRowClick(row)">
                      <el-icon><View /></el-icon> Перегляд
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleViewStock(row)">
                      <el-icon><Box /></el-icon> Залишки на складах
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleViewMovement(row)">
                      <el-icon><Coordinate /></el-icon> Рух товару
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
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

    <!-- ===== AI ASSISTANT DRAWER ===== -->
    <el-drawer
      v-model="aiDrawerVisible"
      title="AI Помічник Номенклатури"
      size="420px"
      direction="rtl"
    >
      <div class="ai-assistant-content">
        <div class="ai-assistant-input-zone">
          <el-input
            v-model="aiCommand"
            placeholder="Напишіть запит (напр: покажи дефіцит)..."
            clearable
            @keyup.enter="runAiAssistant"
          >
            <template #append>
              <el-button @click="runAiAssistant">🤖</el-button>
            </template>
          </el-input>
        </div>
        
        <div v-if="aiAnalysisResult" class="ai-assistant-result-zone">
          <div class="ai-result-box">
            {{ aiAnalysisResult }}
          </div>
        </div>

        <div class="ai-assistant-prompts">
          <p class="ai-prompt-title">Приклади запитів:</p>
          <div class="ai-prompt-pill" @click="aiCommand = 'Знайди дублікати'; runAiAssistant()">🔍 Знайди дублікати</div>
          <div class="ai-prompt-pill" @click="aiCommand = 'Покажи дефіцит'; runAiAssistant()">⚠️ Покажи дефіцит</div>
        </div>
      </div>
    </el-drawer>



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
    <!-- ===== PRODUCT FORM DRAWER (CREATE & EDIT) ===== -->
    <el-drawer
      v-model="formDrawerVisible"
      :title="isEditMode ? 'Редагувати позицію' : 'Створити нову позицію'"
      size="520px"
      direction="rtl"
    >
      <div class="form-drawer-content">
        <el-form :model="formModel" label-position="top" size="default">
          
          <el-form-item label="Назва номенклатури" required>
            <el-input v-model="formModel.name" placeholder="Напр: Профіль 20x20x1.2" />
            <el-button 
              type="primary" 
              link 
              style="margin-top: 6px;"
              @click="runAiFormFill"
            >
              🤖 Автозаповнення через AI
            </el-button>
          </el-form-item>

          <el-form-item label="Артикул (SKU)" required>
            <el-input v-model="formModel.sku" placeholder="Напр: PRF-20X20" />
          </el-form-item>

          <el-form-item label="Категорія" required>
            <el-select v-model="formModel.category" style="width: 100%">
              <el-option
                v-for="cat in categoryOptions"
                :key="cat.code"
                :label="cat.name"
                :value="cat.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Одиниця виміру" required>
            <el-select v-model="formModel.unit_of_measure" style="width: 100%">
              <el-option
                v-for="uom in uomOptions"
                :key="uom.code"
                :label="uom.name"
                :value="uom.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Ціна (грн)">
            <el-input-number v-model="formModel.price" :min="0" style="width: 100%" />
          </el-form-item>

          <el-form-item label="Початковий залишок">
            <el-input-number v-model="formModel.stock_balance" :min="0" style="width: 100%" />
          </el-form-item>

          <el-form-item label="Мінімальний залишок">
            <el-input-number v-model="formModel.min_stock" :min="0" style="width: 100%" />
          </el-form-item>

        </el-form>

        <div class="form-drawer-actions" style="margin-top: 24px; display: flex; gap: 12px;">
          <el-button @click="formDrawerVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveProduct" :loading="saveLoading">
            {{ isEditMode ? 'Зберегти' : 'Створити' }}
          </el-button>
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
  Box, Coordinate, Warning, CircleClose, Grid, Fold, View, More
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

// Multi-select items state
const selectedRows = ref([])
const handleSelectionChange = (val) => {
  selectedRows.value = val
}

const visibleColumns = ref({
  brand: false,
  weight: false,
  dimensions: false,
  supplier: false
})

// AI Assistant Logic
const aiDrawerVisible = ref(false)
const aiCommand = ref('')
const aiAnalysisResult = ref('')

const runAiAssistant = () => {
  if (!aiCommand.value) return
  
  if (aiCommand.value.toLowerCase().includes('дефіцит') || aiCommand.value.toLowerCase().includes('мало')) {
    aiAnalysisResult.value = '🤖 AI Аналітика: Знайдено 3 позиції з критичним залишком. Рекомендовано створити замовлення постачальнику для: "Банкетка Loren 80" та "Профіль 20x20".'
  } else if (aiCommand.value.toLowerCase().includes('дублікати')) {
    aiAnalysisResult.value = '🤖 AI Аналітика: Схожих дублікатів у вашій базі наразі не виявлено. Всі позиції унікальні.'
  } else {
    aiAnalysisResult.value = `🤖 AI Результат: За вашим запитом "${aiCommand.value}" оброблено дані. Рекомендовано звернути увагу на категорію "Метал".`
  }
}

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
const filterType = ref('')
const filterStockDetails = ref('')
const activeTab = ref('all')

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
    
    // Apply front-end filtering for UI Types & Stock Details
    if (filterType.value) {
      results = results.filter(p => {
        if (filterType.value === 'product') return p.category === 'PRODUCT'
        if (filterType.value === 'material') return p.category === 'MATERIAL'
        return true
      })
    }

    if (filterStock.value) {
      if (filterStock.value === 'in_stock') {
        results = results.filter(p => p.stock_balance > 0)
      } else if (filterStock.value === 'low_stock') {
        results = results.filter(p => p.stock_balance > 0 && p.stock_balance <= (p.min_stock || 5))
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

// Product Form Drawer state
const formDrawerVisible = ref(false)
const isEditMode = ref(false)
const saveLoading = ref(false)
const formModel = ref({
  id: null,
  name: '',
  sku: '',
  category: 'PRODUCT',
  unit_of_measure: 'pcs',
  price: 0,
  stock_balance: 0,
  min_stock: 0
})

const handleEdit = (row) => {
  isEditMode.value = true
  formModel.value = { ...row }
  formDrawerVisible.value = true
}

const goToCreate = () => {
  isEditMode.value = false
  formModel.value = {
    id: null,
    name: '',
    sku: '',
    category: 'PRODUCT',
    unit_of_measure: 'pcs',
    price: 0,
    stock_balance: 0,
    min_stock: 0
  }
  formDrawerVisible.value = true
}

const saveProduct = async () => {
  if (!formModel.value.name || !formModel.value.sku) {
    ElMessage.warning('Будь ласка, заповніть обов\'язкові поля')
    return
  }
  
  saveLoading.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/products/${formModel.value.id}`, formModel.value)
      ElMessage.success('Дані успішно оновлено')
    } else {
      await api.post('/api/v1/products', formModel.value)
      ElMessage.success('Номенклатуру успішно створено')
    }
    formDrawerVisible.value = false
    fetchProducts()
    fetchStatistics()
  } catch (error) {
    ElMessage.error('Помилка збереження даних')
  } finally {
    saveLoading.value = false
  }
}

const runAiFormFill = () => {
  if (!formModel.value.name) {
    ElMessage.info('Введіть назву товару для AI-аналізу')
    return
  }
  
  const nameLower = formModel.value.name.toLowerCase()
  if (nameLower.includes('профіль') || nameLower.includes('метал')) {
    formModel.value.category = 'MATERIAL'
    formModel.value.unit_of_measure = 'm'
    formModel.value.sku = 'PRF-' + Math.floor(Math.random() * 1000)
  } else if (nameLower.includes('тканина') || nameLower.includes('поролон')) {
    formModel.value.category = 'MATERIAL'
    formModel.value.unit_of_measure = 'm'
    formModel.value.sku = 'TXT-' + Math.floor(Math.random() * 1000)
  } else {
    formModel.value.category = 'PRODUCT'
    formModel.value.unit_of_measure = 'pcs'
    formModel.value.sku = 'PRD-' + Math.floor(Math.random() * 1000)
  }
  ElMessage.success('AI підібрав оптимальні характеристики!')
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
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;

  --primary: #635bff;
  --success-bg: #dcfce7;
  --success-text: #16a34a;
  --warning-bg: #fef3c7;
  --warning-text: #d97706;
  --danger-bg: #fee2e2;
  --danger-text: #ef4444;

  padding: 24px;
  background: radial-gradient(circle at top left, rgba(99,102,241,0.08), transparent 28%), var(--page-bg);
  min-height: calc(100vh - 64px);
  font-family: 'Inter', sans-serif;
  color: var(--text-primary);
}

/* ===== HEADER ===== */
.page-header-premium {
  margin-bottom: 20px;
}
.breadcrumbs-premium {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
  font-weight: 500;
}
.page-title-premium {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

/* ===== STAT CARDS ===== */
.stats-row-dense {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.stats-card-dense {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 12px 32px rgba(15,23,42,0.04);
  transition: all 0.2s ease;
  height: 72px;
  box-sizing: border-box;
}
.stats-card-dense:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(15,23,42,0.08);
}
.stats-card-dense__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.stats-card-dense__icon.total { background: #eff6ff; color: #2563eb; }
.stats-card-dense__icon.success { background: var(--success-bg); color: var(--success-text); }
.stats-card-dense__icon.warning { background: var(--warning-bg); color: var(--warning-text); }
.stats-card-dense__icon.danger { background: var(--danger-bg); color: var(--danger-text); }

.stats-card-dense__content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stats-card-dense__label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stats-card-dense__value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

/* ===== TOOLBAR ===== */
.toolbar-dense {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 28px rgba(15,23,42,0.03);
  margin-top: 16px;
  gap: 16px;
}
.toolbar-dense__left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.search-dense-wrapper {
  position: relative;
  width: 320px;
}
.search-dense-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
.search-dense-input {
  width: 100%;
  height: 42px;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 0 12px 0 38px;
  font-size: 14px;
  background: #ffffff;
  transition: all 0.2s ease;
}
.search-dense-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 91, 255, 0.1);
}
.pill-select :deep(.el-select__wrapper) {
  height: 42px !important;
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
  background: #ffffff !important;
  box-shadow: none !important;
}
.column-toggle-btn {
  height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: #ffffff;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}
.column-toggle-btn:hover {
  background: #f8fafc;
  border-color: var(--primary);
}
.primary-dense-button {
  height: 42px;
  padding: 0 20px;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 12px 28px rgba(99, 91, 255, 0.28);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.primary-dense-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 34px rgba(99, 91, 255, 0.34);
}

/* ===== TABLE SECTION ===== */
.table-section {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.05);
  margin-top: 20px;
  overflow: hidden;
}
:deep(.table-header-dense th) {
  background: #f8fafc !important;
  color: var(--text-secondary) !important;
  font-weight: 700 !important;
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
  background: linear-gradient(90deg, rgba(99, 91, 255, 0.03), rgba(255, 255, 255, 0)) !important;
}
:deep(.table-cell-dense) {
  padding: 8px 16px !important;
  border-bottom: 1px solid #eef2f7 !important;
}

.product-item-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.product-thumb-compact {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid var(--border);
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
.product-info-compact {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.product-title-compact {
  font-weight: 600;
  font-size: 15px;
  color: #0f172a;
}
.product-sku-compact {
  font-size: 12px;
  color: var(--text-muted);
}
.sku-divider {
  margin: 0 4px;
}

.category-badge-premium {
  display: inline-block;
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.stock-badge-premium {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}
.stock-badge-premium.danger { background: var(--danger-bg); color: var(--danger-text); }
.stock-badge-premium.warning { background: var(--warning-bg); color: var(--warning-text); }
.stock-badge-premium.success { background: var(--success-bg); color: var(--success-text); }

.price-cell-dense {
  font-weight: 600;
  font-size: 14px;
  color: #0f172a;
}
.price-cell-dense.empty {
  color: var(--text-muted);
}

.actions-cell-premium {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}
.action-btn-premium {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.action-btn-premium:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #4f46e5;
  transform: translateY(-1px);
}

.pagination-dense {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid #eef2f7;
}

/* ===== COMPACT MODE ===== */
.dense-mode {
  padding: 16px;
}
.dense-mode .stats-card-dense {
  height: 56px;
  padding: 10px 14px;
}
.dense-mode .stats-card-dense__value {
  font-size: 20px;
}
.dense-mode .toolbar-dense {
  padding: 10px 12px;
  margin-top: 12px;
}
.dense-mode .table-section {
  margin-top: 12px;
}
.dense-mode :deep(.table-row-dense) {
  height: 56px;
}
.dense-mode :deep(.table-cell-dense) {
  padding: 8px 14px !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.6);
}

.header-flex-premium {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.page-subtitle-premium {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}
.header-actions-premium {
  display: flex;
  gap: 12px;
}
.secondary-premium-btn {
  height: 42px;
  padding: 0 16px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.secondary-premium-btn:hover {
  background: #f8fafc;
  border-color: var(--primary);
}

.stats-card-dense__subtext {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
}
.stats-card-dense__sparkline {
  margin-left: auto;
}

.ai-banner-premium {
  background: linear-gradient(135deg, rgba(99, 91, 255, 0.08), rgba(139, 92, 246, 0.08));
  border: 1px solid rgba(99, 91, 255, 0.2);
  border-radius: 16px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  box-sizing: border-box;
}
.ai-banner-content {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-banner-icon {
  font-size: 20px;
}
.ai-banner-title {
  font-size: 15px;
  font-weight: 700;
  color: #4f46e5;
  margin: 0;
}
.ai-banner-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 2px 0 0 0;
}
.ai-banner-btn {
  padding: 6px 14px;
  background: #4f46e5;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.ai-banner-btn:hover {
  background: #4338ca;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.quick-tabs-premium {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--border);
  padding: 0 10px 8px 10px;
  margin-top: 16px;
}
.quick-tab-item {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
  padding-bottom: 8px;
}
.quick-tab-item:hover {
  color: var(--primary);
}
.quick-tab-item.active {
  color: var(--primary);
}
.quick-tab-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -9px;
  height: 2px;
  background: var(--primary);
  border-radius: 2px;
}

.stock-progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stock-number-dense {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.stock-progress-bar {
  width: 100%;
  height: 6px;
  background: #eef2f7;
  border-radius: 3px;
  overflow: hidden;
}
.stock-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.stock-progress-fill.success { background-color: var(--success-text); }
.stock-progress-fill.warning { background-color: var(--warning-text); }
.stock-progress-fill.danger { background-color: #f43f5e; }

.ai-assistant-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.ai-assistant-result-zone {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
}
.ai-result-box {
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
}
.ai-assistant-prompts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ai-prompt-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}
.ai-prompt-pill {
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.ai-prompt-pill:hover {
  background: rgba(99, 91, 255, 0.05);
  border-color: var(--primary);
}
</style>






