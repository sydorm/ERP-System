<template>
  <div class="page-container">
    <!-- === TOP BAR === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" class="back-btn" />
        <h2>{{ isEditMode ? 'Редагування товару' : 'Новий товар' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveProduct" class="btn-save">
          Зберегти
        </el-button>
      </div>
    </div>

    <!-- === CONTENT CARD === -->
    <div class="editor-content" v-loading="loading">
      <div class="content-card">
        <el-tabs v-model="activeTab" class="product-tabs">
          <el-tab-pane label="Загальна інформація" name="general">
            <GeneralTab
              v-model="form"
              :category-options="categoryOptions"
              :uom-options="uomOptions"
            />
          </el-tab-pane>

          <el-tab-pane label="Характеристики" name="characteristics">
            <CharacteristicsTab
              v-model="productCharacteristics"
              :product-id="form.id"
              :category-code="form.category"
            />
          </el-tab-pane>

          <el-tab-pane label="Ціни та Комерція" name="pricing">
            <PricingTab
              v-model="form"
              :currency-options="currencyOptions"
              :has-specification="hasSpecification"
            />
          </el-tab-pane>

          <el-tab-pane label="Специфікації (BOM)" name="specification">
            <template v-if="form.id">
               <SpecificationTab :product-id="form.id" />
            </template>
            <el-empty v-else description="Спершу збережіть товар, щоб додавати специфікації" />
          </el-tab-pane>

          <el-tab-pane label="Складські запаси" name="inventory">
            <InventoryTab :stock-levels="stockLevels" />
          </el-tab-pane>

          <el-tab-pane label="Файли" name="files">
            <FilesTab />
          </el-tab-pane>

          <el-tab-pane label="Варіанти" name="variants">
            <ProductVariantsManager
              :category-attributes="categoryAttributes"
              :product-code="form.sku"
              :initial-variants="form.variants"
              @update:variants="(val) => form.variants = val"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

// Sub-components
import GeneralTab from './ProductTabs/GeneralTab.vue'
import CharacteristicsTab from './ProductTabs/CharacteristicsTab.vue'
import PricingTab from './ProductTabs/PricingTab.vue'
import SpecificationTab from './ProductTabs/SpecificationTab.vue'
import InventoryTab from './ProductTabs/InventoryTab.vue'
import FilesTab from './ProductTabs/FilesTab.vue'
import ProductVariantsManager from '@/components/ProductVariantsManager.vue'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id)

const form = reactive({
    id: null,
    sku: '',
    name: '',
    description: '',
    category: '',
    unit_of_measure: 'шт',
    price: 0,
    cost: 0,
    currency: 'UAH',
    image_url: '',
    is_active: true,
    variants: []
})

const productCharacteristics = ref([])
const categoryAttributes = ref([])

// Options
const uomOptions = ref([])
const categoryOptions = ref([])
const currencyOptions = ref([])

// Data
const stockLevels = ref([])
const hasSpecification = ref(false)

const goBack = () => {
    router.push('/inventory/nomenclature')
}

const fetchDictionaries = async () => {
    try {
        const [uomRes, catRes, currRes] = await Promise.all([
            api.get('/api/v1/dictionaries/UOM'),
            api.get('/api/v1/dictionaries/PRODUCT_CATEGORY'),
            api.get('/api/v1/dictionaries/CURRENCY')
        ])
        uomOptions.value = uomRes.data
        categoryOptions.value = catRes.data
        currencyOptions.value = currRes.data
        
        // Auto-fetch attributes if category is selected
        if (form.category) fetchCategoryAttributes()
    } catch (error) {
        console.error('Failed to load dictionaries', error)
    }
}

const fetchCategoryAttributes = async () => {
    if (!form.category) {
        categoryAttributes.value = []
        return
    }
    try {
        const res = await api.get(`/api/v1/attributes/category/${form.category}`)
        categoryAttributes.value = (res.data || []).map(ca => ({
            ...ca.attribute,
            is_required: ca.is_required
        }))
    } catch (e) {
        console.error('Failed to load category attributes', e)
    }
}

const fetchProduct = async () => {
    if (!isEditMode.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}`)
        Object.assign(form, res.data)
        
        // Ensure price/cost are numbers for el-input-number
        form.price = parseFloat(form.price) || 0
        form.cost = parseFloat(form.cost) || 0
        
        // Extract characteristics from primary variant
        const primaryVar = form.variants?.find(v => v.is_primary) || form.variants?.[0]
        if (primaryVar && primaryVar.values) {
            productCharacteristics.value = primaryVar.values.map(v => ({
                attribute_id: v.attribute_id,
                option_id: v.option_id,
                text_value: v.text_value,
                bool_value: v.bool_value || false,
                is_fixed: false // We can't know from data alone without sync, but sync will fix it
            }))
        }
        
        fetchStockLevels()
    } catch (e) {
        ElMessage.error('Помилка завантаження товару')
    } finally {
        loading.value = false
    }
}

const fetchStockLevels = async () => {
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}/stock`)
        stockLevels.value = res.data
    } catch (e) {
        console.error('Failed to load stock levels', e)
    }
}

const saveProduct = async () => {
    // Ensure numeric types
    form.price = parseFloat(form.price) || 0
    form.cost = (form.cost !== null && form.cost !== undefined) ? parseFloat(form.cost) : null

    // If we only have characteristics (legacy/single mode) but no variants defined in Variants tab,
    // ensure at least one primary variant exists.
    if (form.variants.length === 0 && productCharacteristics.value.length > 0) {
        form.variants = [{
            sku: form.sku,
            is_primary: true,
            is_active: true,
            values: productCharacteristics.value.map(c => ({
                attribute_id: c.attribute_id,
                option_id: c.option_id,
                text_value: String(c.text_value || ''),
                bool_value: !!c.bool_value
            }))
        }]
    }

    submitting.value = true
    try {
        if (isEditMode.value) {
            await api.put(`/api/v1/products/${form.id}`, form)
            ElMessage.success('Товар оновлено')
        } else {
            const res = await api.post('/api/v1/products', form)
            ElMessage.success('Товар створено')
            router.push(`/inventory/nomenclature/${res.data.id}`)
        }
    } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
    } finally {
        submitting.value = false
    }
}

watch(() => form.category, fetchCategoryAttributes)

onMounted(() => {
    fetchDictionaries()
    fetchProduct()
})
</script>

<style scoped>
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f4f6f8;
}

/* === TOP BAR === */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 12px 24px;
  border-bottom: 1px solid #f0f3f6;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-save {
  background: #2563eb;
  border: none;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
}

/* === EDITOR CONTENT === */
.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

/* === CONTENT CARD === */
.content-card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f3f6;
  overflow: hidden;
}

/* === TABS === */
.product-tabs :deep(.el-tabs__header) {
  background: #ffffff;
  padding: 0 20px;
  margin-bottom: 0;
  border-bottom: 1px solid #f1f5f9;
}

.product-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none; /* remove default bottom line */
}

.product-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 500;
  color: #94a3b8;
  padding: 0 16px;
  height: 44px;
  line-height: 44px;
  transition: color 0.2s;
}

.product-tabs :deep(.el-tabs__item:hover) {
  color: #2563eb;
}

.product-tabs :deep(.el-tabs__item.is-active) {
  color: #2563eb;
  font-weight: 600;
}

.product-tabs :deep(.el-tabs__active-bar) {
  background-color: #2563eb;
  height: 2px;
  border-radius: 2px;
}

.product-tabs :deep(.el-tabs__content) {
  padding: 0;
}
</style>
