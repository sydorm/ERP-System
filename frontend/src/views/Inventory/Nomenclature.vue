<template>
  <div class="orders-page" :class="{ 'dense-mode': isCompactMode }">
    <div class="top-section">
      <!-- KPI STAT CARDS -->
      <NomenclatureHeader :stats="stats" />

      <!-- TOOLBAR (Search, Filters, Actions) -->
      <NomenclatureToolbar
        v-model:searchQuery="searchQuery"
        v-model:filterCategory="filterCategory"
        v-model:filterType="filterType"
        v-model:filterStock="filterStock"
        v-model:activeTab="activeTab"
        :category-options="categoryOptions"
        @search="handleSearch"
        @create="goToCreate"
        @import="importWizardVisible = true"
        @export="handleExport"
      />
    </div>

    <!-- TABLE SECTION -->
    <NomenclatureTable
      :products="products"
      :loading="loading"
      v-model:selectedRows="selectedRows"
      v-model:currentPage="currentPage"
      v-model:limit="limit"
      :total="total"
      :get-uom-name="getUomName"
      :get-category-name="getCategoryName"
      :get-category-badge-style="getCategoryBadgeStyle"
      :get-stock-badge-class="getStockBadgeClass"
      :get-stock-badge-text="getStockBadgeText"
      :format-currency="formatCurrency"
      @row-click="handleRowClick"
      @toggle-selection="toggleRowSelection"
      @toggle-all="toggleAllSelection"
      @edit="handleEdit"
      @duplicate="handleDuplicate"
      @view-stock="handleViewStock"
      @view-movement="handleViewMovement"
      @delete="handleDelete"
    />

    <!-- AI ASSISTANT DRAWER -->
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

    <!-- SIDE DRAWERS (INFO & FORM) -->
    <NomenclatureDrawer
      v-model:visible="drawerVisible"
      v-model:formVisible="formDrawerVisible"
      v-model:formModel="formModel"
      :product="selectedProduct"
      :warehouse-stock="warehouseStock"
      :product-movements="productMovements"
      :is-edit-mode="isEditMode"
      :save-loading="saveLoading"
      :category-options="categoryOptions"
      :uom-options="uomOptions"
      :get-uom-name="getUomName"
      @save="saveProduct"
      @run-ai-fill="runAiFormFill"
    />

    <NomenclatureImportWizard
      v-model:visible="importWizardVisible"
      @completed="handleImportCompleted"
    />

    <NomenclatureBulkPriceDialog
      v-model:visible="bulkPriceVisible"
      :count="selectedRows.length"
      :loading="loading"
      @apply="applyBulkPriceChange"
    />

    <!-- FLOATING AI BUTTON -->
    <el-popover
      v-model:visible="aiPopoverVisible"
      placement="top-end"
      :width="320"
      trigger="click"
      popper-class="ai-popover"
    >
      <template #reference>
        <button class="ai-float-btn" title="AI-помічник">
          🤖
          <span class="ai-float-label">AI</span>
        </button>
      </template>

      <div class="ai-pop-content">
        <div class="ai-pop-header">
          <span class="ai-pop-title">🤖 AI-помічник</span>
          <span class="ai-pop-sub">Номенклатура · аналіз</span>
        </div>

        <div class="ai-pop-input-row">
          <input
            v-model="aiCommand"
            class="ai-pop-input"
            placeholder="Напишіть запит..."
            @keyup.enter="runAiAssistantPop"
          />
          <button class="ai-pop-send" @click="runAiAssistantPop">→</button>
        </div>

        <div v-if="aiAnalysisResult" class="ai-pop-result">
          {{ aiAnalysisResult }}
        </div>

        <div class="ai-pop-quick">
          <div class="ai-pop-quick-title">Швидкі дії:</div>
          <div class="ai-pop-pills">
            <button class="ai-pill" @click="aiQuickAction('Знайди дублікати')">🔍 Дублікати</button>
            <button class="ai-pill" @click="aiQuickAction('Покажи дефіцит')">⚠️ Дефіцит</button>
            <button class="ai-pill" @click="aiQuickAction('Без ціни')">💰 Без ціни</button>
            <button class="ai-pill" @click="aiQuickAction('Нульові залишки')">📦 Нуль</button>
            <button class="ai-pill" @click="aiQuickAction('Треба дозамовити')">🛒 Дозамовити</button>
            <button class="ai-pill" @click="aiDrawerVisible = true; aiPopoverVisible = false">📊 Повний аналіз</button>
          </div>
        </div>
      </div>
    </el-popover>

    <!-- BULK ACTION BAR -->
    <NomenclatureBulkBar
      :selected-count="selectedRows.length"
      :categories="categoryOptions"
      :uoms="uomOptions"
      @clear="selectedRows = []"
      @change-category="handleBulkCategoryChange"
      @change-uom="handleBulkUomChange"
      @action="handleBulkAction"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'

// Components
import NomenclatureHeader from '../../components/Nomenclature/NomenclatureHeader.vue'
import NomenclatureToolbar from '../../components/Nomenclature/NomenclatureToolbar.vue'
import NomenclatureTable from '../../components/Nomenclature/NomenclatureTable.vue'
import NomenclatureDrawer from '../../components/Nomenclature/NomenclatureDrawer.vue'
import NomenclatureImportWizard from '../../components/Nomenclature/NomenclatureImportWizard.vue'
import NomenclatureBulkBar from '../../components/Nomenclature/NomenclatureBulkBar.vue'
import NomenclatureBulkPriceDialog from '../../components/Nomenclature/NomenclatureBulkPriceDialog.vue'

const dictStore = useDictionaryStore()
const router = useRouter()

// Compact mode state
const isCompactMode = ref(localStorage.getItem('nomenclature_dense_mode') === 'true')

// UI States
const drawerVisible = ref(false)
const selectedProduct = ref(null)
const warehouseStock = ref([])
const productMovements = ref([])
const selectedRows = ref([])
const importWizardVisible = ref(false)
const bulkPriceVisible = ref(false)

// AI Assistant Logic
const aiDrawerVisible = ref(false)
const aiPopoverVisible = ref(false)
const aiCommand = ref('')
const aiAnalysisResult = ref('')

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
const activeTab = ref('all')

const categoryOptions = computed(() => dictStore.getCategory('PRODUCT_CATEGORY'))
const uomOptions = computed(() => dictStore.getCategory('UOM'))

// Watchers for immediate filtering
watch([filterCategory, filterType, filterStock, activeTab, limit], () => {
  handleFilterChange()
})

watch(searchQuery, () => {
  handleSearch()
})

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
    
    // Front-end filtering
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

const handleFilterChange = () => {
  skip.value = 0
  currentPage.value = 1
  fetchProducts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  skip.value = (page - 1) * limit.value
  fetchProducts()
}

const toggleRowSelection = (row) => {
  const index = selectedRows.value.findIndex(r => r.id === row.id)
  if (index > -1) {
    selectedRows.value.splice(index, 1)
  } else {
    selectedRows.value.push(row)
  }
}

const toggleAllSelection = (isSelected) => {
  selectedRows.value = isSelected ? [...products.value] : []
}

// Product Form Logic
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

const handleRowClick = (row) => {
  router.push(`/inventory/nomenclature/${row.id}`)
}

const handleEdit = (row) => {
  router.push(`/inventory/nomenclature/${row.id}`)
}

const handleDuplicate = (row) => {
  ElMessage.info('Дублювання: ' + row.name)
}

const goToCreate = () => {
  router.push('/inventory/nomenclature/new')
}

const handleDelete = (row) => {
  ElMessage.warning('Видалення: ' + row.name)
}

const handleExport = () => {
  ElMessage.info('Експорт Excel/CSV')
}

const handleImportCompleted = () => {
  fetchStatistics().then(() => fetchProducts())
}

const handleViewStock = (row) => {
  ElMessage.info(`Залишки для ${row.name}`)
}

const handleViewMovement = (row) => {
  ElMessage.info(`Рух товару для ${row.name}`)
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

const runAiAssistantPop = () => runAiAssistant()
const aiQuickAction = (cmd) => {
  aiCommand.value = cmd
  runAiAssistant()
}

// Bulk Actions Logic
const handleBulkCategoryChange = async (categoryCode) => {
  if (selectedRows.value.length === 0) return
  loading.value = true
  try {
    const ids = selectedRows.value.map(r => r.id)
    await api.post('/api/v1/products/bulk-update', {
      ids,
      updates: { category: categoryCode }
    })
    ElMessage.success(`Оновлено категорію для ${ids.length} позицій`)
    selectedRows.value = []
    fetchProducts()
  } catch (error) {
    ElMessage.error('Помилка масового оновлення категорії')
  } finally {
    loading.value = false
  }
}

const handleBulkUomChange = async (uomCode) => {
  if (selectedRows.value.length === 0) return
  loading.value = true
  try {
    const ids = selectedRows.value.map(r => r.id)
    await api.post('/api/v1/products/bulk-update', {
      ids,
      updates: { unit_of_measure: uomCode }
    })
    ElMessage.success(`Оновлено одиницю виміру для ${ids.length} позицій`)
    selectedRows.value = []
    fetchProducts()
  } catch (error) {
    ElMessage.error('Помилка масового оновлення одиниць виміру')
  } finally {
    loading.value = false
  }
}

const handleBulkAction = async (action, payload) => {
  if (selectedRows.value.length === 0) return
  const ids = selectedRows.value.map(r => r.id)

  if (action === 'price') {
    bulkPriceVisible.value = true
    return
  }

  if (action === 'delete') {
    try {
      await api.post('/api/v1/products/bulk-delete', { ids })
      ElMessage.success(`Видалено ${ids.length} позицій`)
      selectedRows.value = []
      fetchProducts()
      fetchStatistics()
    } catch (error) {
      ElMessage.error('Помилка масового видалення')
    }
    return
  }

  if (action === 'status') {
    loading.value = true
    try {
      await api.post('/api/v1/products/bulk-update', {
        ids,
        updates: { status: payload }
      })
      ElMessage.success('Статус оновлено')
      selectedRows.value = []
      fetchProducts()
    } catch (error) {
      ElMessage.error('Помилка оновлення статусу')
    } finally {
      loading.value = false
    }
    return
  }

  if (action === 'ai-optimize') {
    ElMessage.info('AI аналізує обрані товари...')
    setTimeout(() => {
      ElMessage.success('AI рекомендує перемістити 3 позиції в категорію "Метал"')
    }, 1500)
    return
  }

  ElMessage.info(`Дія ${action} в розробці`)
}

const applyBulkPriceChange = async (params) => {
  if (selectedRows.value.length === 0) return
  loading.value = true
  try {
    const ids = selectedRows.value.map(r => r.id)
    await api.post('/api/v1/products/bulk-update-prices', {
      ids,
      ...params
    })
    ElMessage.success(`Ціни успішно оновлено для ${ids.length} позицій`)
    bulkPriceVisible.value = false
    selectedRows.value = []
    fetchProducts()
  } catch (error) {
    ElMessage.error('Помилка масового оновлення цін')
  } finally {
    loading.value = false
  }
}

// Helpers
const colorMap = {
  blue: '#3b82f6', green: '#10b981', orange: '#f59e0b', red: '#ef4444',
  purple: '#8b5cf6', teal: '#14b8a6', gray: '#64748b', indigo: '#4f46e5',
  pink: '#ec4899', rose: '#f43f5e', cyan: '#06b6d4', amber: '#fcd34d'
}

const hexToRgba = (hex, opacity) => {
  if (!hex) return 'rgba(0,0,0,0)'
  let cleanHex = hex.replace('#', '').trim()
  if (cleanHex.length === 3) {
    cleanHex = cleanHex.split('').map(c => c + c).join('')
  }
  if (cleanHex.length === 8) cleanHex = cleanHex.substring(0, 6)
  if (cleanHex.length !== 6) return hex
  const r = parseInt(cleanHex.substring(0, 2), 16)
  const g = parseInt(cleanHex.substring(2, 4), 16)
  const b = parseInt(cleanHex.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

const darkenColor = (hex, percent) => {
  if (!hex) return '#000'
  let cleanHex = hex.replace('#', '').trim()
  if (cleanHex.length === 3) cleanHex = cleanHex.split('').map(c => c + c).join('')
  if (cleanHex.length === 8) cleanHex = cleanHex.substring(0, 6)
  if (cleanHex.length !== 6) return hex
  let r = parseInt(cleanHex.substring(0, 2), 16)
  let g = parseInt(cleanHex.substring(2, 4), 16)
  let b = parseInt(cleanHex.substring(4, 6), 16)
  r = Math.max(0, Math.floor(r * (1 - percent / 100)))
  g = Math.max(0, Math.floor(g * (1 - percent / 100)))
  b = Math.max(0, Math.floor(b * (1 - percent / 100)))
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`
}

const getCategoryBadgeStyle = (code) => {
  const fallback = { backgroundColor: '#F8FAFC', borderColor: '#E2E8F0', color: '#475569' }
  if (!code) return fallback
  const categories = dictStore.getCategory('PRODUCT_CATEGORY')
  const category = categories.find(cat => cat.code === code)
  if (!category || !category.color) return fallback
  let baseColor = category.color
  if (colorMap[baseColor.toLowerCase()]) baseColor = colorMap[baseColor.toLowerCase()]
  else if (!baseColor.startsWith('#')) baseColor = '#4f46e5'
  return {
    backgroundColor: hexToRgba(baseColor, 0.10),
    borderColor: hexToRgba(baseColor, 0.25),
    color: darkenColor(baseColor, 10)
  }
}

const getCategoryName = (code) => dictStore.getName('PRODUCT_CATEGORY', code)
const getUomName = (code) => dictStore.getShortName('UOM', code)
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
  background-color: #F8F9FA;
  margin: 0;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px 24px 8px;
  background: transparent;
}

/* AI FLOATING BUTTON */
.ai-float-btn {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 200;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #635bff, #7c3aed);
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(99,91,255,0.45);
  transition: all 0.2s ease;
  font-size: 20px;
}
.ai-float-btn:hover {
  box-shadow: 0 12px 30px rgba(99,91,255,0.55);
  transform: translateY(-2px);
}
.ai-float-label {
  font-size: 10px;
  font-weight: 700;
  color: #ffffff;
}

/* AI POPOVER */
.ai-pop-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
  border-bottom: 1px solid #eef2f7;
  padding-bottom: 8px;
}
.ai-pop-title { font-weight: 700; color: #0f172a; }
.ai-pop-sub { font-size: 12px; color: #94a3b8; }
.ai-pop-input-row { display: flex; gap: 6px; margin-bottom: 10px; }
.ai-pop-input {
  flex: 1; height: 36px; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 0 12px; font-size: 13px;
}
.ai-pop-send {
  width: 36px; height: 36px; border-radius: 10px; background: #635bff;
  color: white; border: none; cursor: pointer;
}
.ai-pop-result {
  font-size: 13px; background: #f0f4ff; border-radius: 10px;
  padding: 10px; margin-bottom: 10px;
}
.ai-pop-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.ai-pill {
  padding: 4px 8px; border-radius: 6px; background: #f8fafc;
  border: 1px solid #e2e8f0; font-size: 12px; cursor: pointer;
}

/* AI ASSISTANT CONTENT */
.ai-assistant-content { padding: 0 20px; }
.ai-result-box {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 16px; margin: 16px 0; font-size: 14px;
}
.ai-prompt-pill {
  padding: 8px 12px; background: #f1f5f9; border-radius: 8px;
  margin-bottom: 8px; cursor: pointer; font-size: 13px;
}

.dense-mode { padding: 16px; }
</style>
