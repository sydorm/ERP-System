<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
         <el-button :icon="ArrowLeft" circle @click="goBack" />
         <h2>{{ isEditMode ? 'Редагування товару' : 'Новий товар' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveProduct">
            Зберегти
        </el-button>
      </div>
    </div>

    <div class="editor-content" v-loading="loading">
      <el-tabs v-model="activeTab" class="product-tabs">
        <el-tab-pane label="Загальна інформація" name="general">
          <GeneralTab 
            v-model="form" 
            :category-options="categoryOptions" 
            :uom-options="uomOptions"
          />
        </el-tab-pane>

        <!-- 2. Characteristics -->
        <el-tab-pane label="Характеристики" name="characteristics">
          <CharacteristicsTab 
            v-model="productCharacteristics"
            :product-id="form.id"
            :category-code="form.category"
          />
        </el-tab-pane>

        <!-- 2. Commercial -->
        <el-tab-pane label="Ціни та Комерція" name="pricing">
          <PricingTab 
            v-model="form" 
            :currency-options="currencyOptions"
            :has-specification="hasSpecification"
          />
        </el-tab-pane>

        <!-- 3. Specification (BOM) -->
        <el-tab-pane label="Специфікація (BOM)" name="specification">
          <SpecificationTab 
            :items="specificationItems"
            :total-cost="totalBomCost"
          />
        </el-tab-pane>

        <!-- 4. Warehouse -->
        <el-tab-pane label="Складські запаси" name="inventory">
          <InventoryTab :stock-levels="stockLevels" />
        </el-tab-pane>

        <!-- 5. Files -->
        <el-tab-pane label="Файли та техдокументація" name="files">
          <FilesTab />
        </el-tab-pane>

        <!-- 6. Variants -->
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
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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
const specificationItems = ref([])
const stockLevels = ref([])
const hasSpecification = ref(false)

const totalBomCost = computed(() => {
    return specificationItems.value.reduce((acc, item) => acc + (item.quantity * item.unitPrice), 0)
})

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
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 16px 24px;
    border-bottom: 1px solid #eef0f2;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-left h2 {
    margin: 0;
    font-size: 20px;
}

.editor-content {
    flex: 1;
    overflow-y: auto;
    background: #f8f9fa;
}

.product-tabs {
    height: 100%;
}

:deep(.el-tabs__header) {
    background: white;
    padding: 0 24px;
    margin-bottom: 0;
}
</style>
