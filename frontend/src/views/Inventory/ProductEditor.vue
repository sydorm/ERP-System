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
        <!-- 1. General Info -->
        <el-tab-pane label="Загальна інформація" name="general">
          <GeneralTab 
            v-model="form" 
            :category-options="categoryOptions" 
            :uom-options="uomOptions"
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
import PricingTab from './ProductTabs/PricingTab.vue'
import SpecificationTab from './ProductTabs/SpecificationTab.vue'
import InventoryTab from './ProductTabs/InventoryTab.vue'
import FilesTab from './ProductTabs/FilesTab.vue'

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
    is_active: true
})

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
    } catch (error) {
        console.error('Failed to load dictionaries', error)
    }
}

const fetchProduct = async () => {
    if (!isEditMode.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}`)
        Object.assign(form, res.data)
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
