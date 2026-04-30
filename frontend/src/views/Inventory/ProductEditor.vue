<template>
  <div class="page-container">
    <!-- === STICKY HEADER === -->
    <div class="sticky-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" class="back-btn" title="Назад" />
        <div class="header-titles">
          <div class="header-top-row">
            <h2>{{ isEditMode ? 'Редагування товару' : 'Новий товар' }}</h2>
            <div class="header-badges" v-if="isEditMode">
              <span class="status-badge" :class="form.is_active ? 'active' : 'inactive'">
                {{ form.is_active ? 'Активний' : 'В архіві' }}
              </span>
              <span class="category-badge" v-if="form.category">
                {{ getCategoryName(form.category) }}
              </span>
            </div>
          </div>
          <div class="header-bottom-row">
            <span class="product-title">{{ form.name || 'Новий товар' }}</span>
            <span class="product-sku" v-if="form.sku && isEditMode">Артикул: {{ form.sku }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="goBack" class="btn-cancel">
          Закрити
        </el-button>
        <el-button v-if="isEditMode" type="danger" plain @click="confirmDelete" class="btn-delete">
          Видалити
        </el-button>
        <el-button type="primary" :loading="submitting" @click="saveProduct" class="btn-save">
          <el-icon><Check /></el-icon> Зберегти
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
              :category-attributes="categoryAttributes"
            />
          </el-tab-pane>

          <el-tab-pane label="Характеристики" name="characteristics">
            <CharacteristicsTab
              v-model="productCharacteristics"
              :product-id="form.id"
              :category-code="form.category"
              :product-attributes="form.product_attributes"
              @update:productAttributes="(val) => form.product_attributes = val"
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
              <SpecificationTab :product-id="form.id" :product-dimensions="form" />
            </template>
            <el-empty v-else description="Спершу збережіть товар, щоб додавати специфікації" />
          </el-tab-pane>



          <el-tab-pane label="Складський запас" name="inventory">
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
              :price-rule="form.price_rule"
              :product-attributes="form.product_attributes"
              :variant-config="form.variant_config"
              :base-dimensions="{ length_mm: form.length_mm, width_mm: form.width_mm, height_mm: form.height_mm, weight_kg: form.weight_kg }"
              @update:variants="(val) => form.variants = val"
              @update:priceRule="(val) => form.price_rule = val"
            />
          </el-tab-pane>

          <el-tab-pane label="Закупівлі та Постачальники" name="procurement">
            <ProcurementTab
              v-model="form"
              :suppliers="suppliers"
            />
          </el-tab-pane>

          <el-tab-pane label="Альтернативи" name="alternatives">
            <div class="empty-tab">
              <el-empty description="Розділ Альтернативи буде доступний в наступній версії" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="Виробництво" name="manufacturing">
            <ManufacturingTab
              v-model="form"
            />
          </el-tab-pane>

          <el-tab-pane label="Пакування" name="packaging">
            <div class="empty-tab">
              <el-empty description="Параметри пакування будуть доступні в наступній версії" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="Нотатки" name="notes">
            <div class="notes-tab">
              <el-form-item label="Внутрішні нотатки">
                <el-input
                  v-model="form.notes"
                  type="textarea"
                  :rows="8"
                  placeholder="Додайте внутрішні нотатки для цього товару..."
                />
              </el-form-item>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Close, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'

const dictStore = useDictionaryStore()

// Sub-components
import { useTabsStore } from '@/stores/tabs'
const tabsStore = useTabsStore()

import GeneralTab from './ProductTabs/GeneralTab.vue'
import CharacteristicsTab from './ProductTabs/CharacteristicsTab.vue'
import PricingTab from './ProductTabs/PricingTab.vue'
import SpecificationTab from './ProductTabs/SpecificationTab.vue'

import InventoryTab from './ProductTabs/InventoryTab.vue'
import FilesTab from './ProductTabs/FilesTab.vue'
import ProductVariantsManager from '@/components/ProductVariantsManager.vue'
import ProcurementTab from './ProductTabs/ProcurementTab.vue'
import ManufacturingTab from './ProductTabs/ManufacturingTab.vue'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id && route.params.id !== 'new')

const resetForm = () => {
    Object.assign(form, {
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
        track_inventory: true,
        barcode: '',
        internal_code: '',
        weight_kg: 0,
        length_mm: 0,
        width_mm: 0,
        height_mm: 0,
        tags: [],
        notes: '',
        variants: [],
        min_stock: 0.0,
        optimal_stock: 0.0,
        default_supplier_id: null,
        supplier_links: [],
        delivery_days: 0,
        production_time_hours: null,
        complexity_code: null,
        min_production_batch: 1,
        max_production_per_day: null,
        special_production_conditions: '',
        performer_restriction_type: 'any_role',
        restricted_brigade_id: null,
        restricted_employee_id: null,
        price_rule: {
            pricing_mode: 'manual',
            base_price: 0,
            markups: []
        },
        product_attributes: [],
        variant_config: {
            length: { source: 'fixed', attr_id: null },
            width: { source: 'fixed', attr_id: null },
            height: { source: 'fixed', attr_id: null },
            weight: { source: 'fixed', base_kg: 0, step_kg: 0, step_mm: 100, dim_key: 'length' }
        }
    })
    productCharacteristics.value = []
    stockLevels.value = []
    hasSpecification.value = false
    activeTab.value = 'general'
}

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
    track_inventory: true,
    barcode: '',
    internal_code: '',
    weight_kg: 0,
    length_mm: 0,
    width_mm: 0,
    height_mm: 0,
    tags: [],
    notes: '',
    variants: [],
    
    // Procurement & Stock Management
    min_stock: 0.0,
    optimal_stock: 0.0,
    default_supplier_id: null,
    supplier_links: [],
    delivery_days: 0,

    // Manufacturing Parameters
    production_time_hours: null,
    complexity_code: null,
    min_production_batch: 1,
    max_production_per_day: null,
    special_production_conditions: '',
    performer_restriction_type: 'any_role',
    restricted_brigade_id: null,
    restricted_employee_id: null,

    // Pricing Rule
    price_rule: {
        pricing_mode: 'manual',
        base_price: 0,
        markups: []
    },
    product_attributes: [],
    variant_config: {
        length: { source: 'fixed', attr_id: null },
        width: { source: 'fixed', attr_id: null },
        height: { source: 'fixed', attr_id: null },
        weight: { source: 'fixed', base_kg: 0, step_kg: 0, step_mm: 100, dim_key: 'length' }
    }
})

const productCharacteristics = ref([])
const categoryAttributes = ref([])

// Options
const uomOptions = computed(() => dictStore.getCategory('UOM'))
const categoryOptions = computed(() => dictStore.getCategory('PRODUCT_CATEGORY'))
const currencyOptions = computed(() => dictStore.getCategory('CURRENCY'))

const getCategoryName = (code) => {
  const cat = categoryOptions.value.find(c => c.code === code)
  return cat ? cat.name : code
}

// Data
const stockLevels = ref([])
const suppliers = ref([])
const hasSpecification = ref(false)

const goBack = () => {
    tabsStore.closeTab(route.path)
    router.push('/inventory/nomenclature')
}

const fetchDictionaries = async () => {
    try {
        await dictStore.fetchMultiple(['UOM', 'PRODUCT_CATEGORY', 'CURRENCY'])
        
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

const fetchSuppliers = async () => {
    try {
        const res = await api.get('/api/v1/counterparties', { params: { is_supplier: true } })
        suppliers.value = res.data
    } catch (e) {
        console.error('Failed to load suppliers', e)
    }
}

const loadProduct = async (id) => {
    loading.value = true
    try {
        const res = await api.get(`/api/v1/products/${id}`)
        Object.assign(form, res.data)
        if (!Array.isArray(form.supplier_links)) form.supplier_links = []
        
        // Ensure numeric fields are numbers for el-input-number
        form.price = parseFloat(form.price) || 0
        form.cost = form.cost ? parseFloat(form.cost) : 0
        form.weight_kg = parseFloat(form.weight_kg) || 0
        form.length_mm = parseFloat(form.length_mm) || 0
        form.width_mm = parseFloat(form.width_mm) || 0
        form.height_mm = parseFloat(form.height_mm) || 0
        form.min_stock = parseFloat(form.min_stock) || 0
        form.optimal_stock = parseFloat(form.optimal_stock) || 0
        if (form.price_rule) {
            form.price_rule.base_price = parseFloat(form.price_rule.base_price) || 0
            if (form.price_rule.markups) {
                form.price_rule.markups.forEach(m => {
                    m.markup = parseFloat(m.markup) || 0
                })
            }
        }
        
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
        
        await fetchStockLevels(id)
    } catch (e) {
        ElMessage.error('Помилка завантаження товару')
    } finally {
        loading.value = false
    }
}

const fetchStockLevels = async (id) => {
    try {
        const res = await api.get(`/api/v1/products/${id}/stock`)
        stockLevels.value = res.data
    } catch (e) {
        console.error('Failed to load stock levels', e)
    }
}

const saveProduct = async () => {
    // Validation: SKU is required if no variants are present
    const hasVariants = form.variants && form.variants.length > 0
    if (!hasVariants && !form.sku) {
        ElMessage.error('Вкажіть артикул або створіть варіанти')
        activeTab.value = 'general'
        return
    }

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
            ElMessage.success('Збережено ✓')
        } else {
            const res = await api.post('/api/v1/products', form)
            ElMessage.success('Збережено ✓')
            router.replace({ params: { id: res.data.id } })
        }
    } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
    } finally {
        submitting.value = false
    }
}

const confirmDelete = () => {
  ElMessageBox.confirm(
    `Ви впевнені, що хочете видалити цей товар?`,
    'Увага',
    {
      confirmButtonText: 'Видалити',
      cancelButtonText: 'Скасувати',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/products/${form.id}`)
      ElMessage.success('Товар видалено')
      tabsStore.closeTab(route.path)
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  })
}

watch(() => form.category, fetchCategoryAttributes)

watch(() => route.params.id, (newId) => {
    if (newId === 'new' || !newId) {
        resetForm()
    } else {
        loadProduct(newId)
    }
}, { immediate: true })

onMounted(() => {
    fetchDictionaries()
    fetchSuppliers()
})
</script>

<style scoped>
.page-container {
  --product-editor-header-height: 74px;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  min-height: 100%;
}

/* === STICKY HEADER === */
.sticky-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 12px 24px;
  min-height: var(--product-editor-header-height);
  border-bottom: 1px solid #E6ECF3;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 90;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-top-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-bottom-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  border: 1px solid #e2e8f0;
  color: #64748b;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: #f1f5f9;
  color: #4f46e5;
  border-color: #cbd5e1;
}

.header-titles h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  line-height: 1;
}
.status-badge.active {
  background-color: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.status-badge.inactive {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.category-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background-color: #f5f3ff;
  color: #4f46e5;
  border: 1px solid #ddd6fe;
  line-height: 1;
}

.product-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.product-sku {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-cancel {
  border: 1px solid #e2e8f0;
  color: #64748b;
  font-weight: 600;
  font-size: 13px;
  border-radius: 12px;
  height: 40px;
  padding: 0 16px;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #f8fafc;
  color: #1e293b;
  border-color: #cbd5e1;
}

.btn-delete {
  font-weight: 600;
  border-radius: 12px;
  height: 40px;
}

.btn-save {
  background: #4f46e5;
  border: none;
  font-weight: 600;
  font-size: 13px;
  color: #ffffff;
  border-radius: 12px;
  height: 40px;
  padding: 0 20px;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
  transition: all 0.2s ease;
}

.btn-save:hover {
  background: #4338ca;
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}

/* === EDITOR CONTENT === */
.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8fafc;
}

/* === CONTENT CARD === */
.content-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.1), 0 2px 8px -1px rgba(148, 163, 184, 0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  width: 100%;
}

/* === TABS STYLING === */
.product-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: #ffffff;
  padding: 12px 24px 0 24px;
  border-bottom: 1px solid #E6ECF3;
  position: sticky;
  top: var(--product-editor-header-height);
  z-index: 80;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.04);
}

.product-tabs :deep(.el-tabs__nav-scroll) {
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
}

.product-tabs :deep(.el-tabs__nav) {
  white-space: nowrap;
}

.product-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.product-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  height: 48px;
  line-height: 48px;
  padding: 0 20px !important;
  transition: all 0.2s ease;
}

.product-tabs :deep(.el-tabs__item:hover) {
  color: #4f46e5;
}

.product-tabs :deep(.el-tabs__item.is-active) {
  color: #4f46e5;
}

.product-tabs :deep(.el-tabs__active-bar) {
  background-color: #4f46e5;
  height: 3px;
  border-radius: 3px 3px 0 0;
}

.product-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.empty-tab {
  padding: 80px 40px;
  text-align: center;
}

.notes-tab {
  padding: 32px;
}
</style>
