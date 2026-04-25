<template>
  <div class="page-container">
    <!-- === TOP BAR === -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" class="back-btn" title="Назад" />
        <div>
          <h2>{{ isEditMode ? 'Редагування товару' : 'Новий товар' }}</h2>
          <p class="page-subtitle">{{ isEditMode ? `Артикул: ${form.sku}` : 'Створення нової номенклатури' }}</p>
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
    track_inventory: true,
    barcode: '',
    internal_code: '',
    weight_kg: 0,
    length_cm: 0,
    width_cm: 0,
    tags: [],
    notes: '',
    variants: [],
    
    // Procurement & Stock Management
    min_stock: 0.0,
    optimal_stock: 0.0,
    default_supplier_id: null,
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
    product_attributes: []
})

const productCharacteristics = ref([])
const categoryAttributes = ref([])

// Options
const uomOptions = computed(() => dictStore.getCategory('UOM'))
const categoryOptions = computed(() => dictStore.getCategory('PRODUCT_CATEGORY'))
const currencyOptions = computed(() => dictStore.getCategory('CURRENCY'))

// Data
const stockLevels = ref([])
const suppliers = ref([])
const hasSpecification = ref(false)

const goBack = () => {
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

const fetchProduct = async () => {
    if (!isEditMode.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}`)
        Object.assign(form, res.data)
        
        // Ensure numeric fields are numbers for el-input-number
        form.price = parseFloat(form.price) || 0
        form.cost = form.cost ? parseFloat(form.cost) : 0
        form.weight_kg = parseFloat(form.weight_kg) || 0
        form.length_cm = parseFloat(form.length_cm) || 0
        form.width_cm = parseFloat(form.width_cm) || 0
        form.height_cm = parseFloat(form.height_cm) || 0
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
      router.push('/inventory/nomenclature')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  })
}

watch(() => form.category, fetchCategoryAttributes)

onMounted(() => {
    fetchDictionaries()
    fetchProduct()
    fetchSuppliers()
})
</script>

<style scoped>
.page-container {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: #f4f5f9;
  z-index: 100;
  overflow: hidden;
}

/* === TOP BAR === */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 4px 20px;
  height: 42px;
  border-bottom: 1px solid #eef0f5;
  flex-shrink: 0;
  z-index: 10;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  border: 1px solid #eef2f7;
  color: #64748b;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: #f8fafc;
  color: #6366f1;
  border-color: #6366f1;
  transform: translateX(-2px);
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.01em;
}

.page-subtitle {
  margin: 0;
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
  border-radius: 10px;
  padding: 8px 16px;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #f8fafc;
  color: #1e293b;
  border-color: #cbd5e1;
}

.btn-delete {
  font-weight: 600;
}

.btn-save {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  font-weight: 700;
  font-size: 13px;
  color: #ffffff;
  border-radius: 10px;
  padding: 8px 20px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-save:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
  transform: translateY(-1px);
  filter: brightness(1.1);
}

.btn-save:active {
  transform: translateY(0);
}

/* === EDITOR CONTENT === */
.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  background-color: #f4f5f9;
}

/* === CONTENT CARD === */
.content-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
  border: 1px solid #eef0f5;
  overflow: hidden;
  width: 100%;
}

/* === TABS STYLING === */
.product-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: #ffffff;
  padding: 0 24px;
  border-bottom: 1px solid #f1f5f9;
}

.product-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.product-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  height: 44px;
  line-height: 44px;
  padding: 0 16px !important;
  transition: all 0.2s ease;
}

.product-tabs :deep(.el-tabs__item:hover) {
  color: #6366f1;
}

.product-tabs :deep(.el-tabs__item.is-active) {
  color: #6366f1;
}

.product-tabs :deep(.el-tabs__active-bar) {
  background-color: #6366f1;
  height: 3px;
  border-radius: 3px 3px 0 0;
}

.product-tabs :deep(.el-tabs__content) {
  padding: 0;
}

/* Specialized tab areas */
.empty-tab {
  padding: 80px 40px;
  text-align: center;
}

.notes-tab {
  padding: 32px;
}
</style>
