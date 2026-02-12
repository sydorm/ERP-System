<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Номенклатура</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
        <el-breadcrumb-item>Склад</el-breadcrumb-item>
        <el-breadcrumb-item>Номенклатура</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-container class="view-layout">
      <!-- Left Sidebar: Categories Filter -->
      <el-aside width="240px" class="view-sidebar">
        <div class="sidebar-header">
             <span class="sidebar-title">Категорії</span>
             <el-button link type="primary" size="small" @click="fetchDictionaries">
                <el-icon><Refresh /></el-icon>
             </el-button>
        </div>
        <el-menu
          :default-active="filterCategory"
          class="category-menu"
          @select="handleCategorySelect"
        >
          <el-menu-item index="">
            <el-icon><Menu /></el-icon>
            <span>Всі товари</span>
          </el-menu-item>
          <el-menu-item 
            v-for="cat in categoryOptions" 
            :key="cat.code" 
            :index="cat.code"
          >
            <el-icon><Folder /></el-icon>
            <span>{{ cat.name }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- Main Content -->
      <el-main class="view-content">
        <el-card shadow="never" class="content-card">
          <!-- Toolbar -->
          <div class="toolbar">
             <div class="toolbar-left">
                <el-input
                  v-model="searchQuery"
                  placeholder="Пошук (Назва, Артикул)..."
                  prefix-icon="Search"
                  class="search-input"
                  clearable
                  @input="handleSearch"
                />
             </div>
             <div class="toolbar-right">
                <el-button type="primary" :icon="Plus" @click="openAddModal">
                    Додати товар
                </el-button>
             </div>
          </div>

          <!-- Data Table -->
          <el-table 
            :data="products" 
            stripe 
            style="width: 100%" 
            v-loading="loading"
            class="data-table"
           >
            <el-table-column width="60" label="">
                <template #default="scope">
                    <el-image 
                        style="width: 32px; height: 32px; border-radius: 4px"
                        :src="scope.row.image_url" 
                        :preview-src-list="scope.row.image_url ? [scope.row.image_url] : []"
                        fit="cover"
                    >
                        <template #error>
                            <div class="image-placeholder">
                                <el-icon><Picture /></el-icon>
                            </div>
                        </template>
                    </el-image>
                </template>
            </el-table-column>
            
            <el-table-column prop="sku" label="Артикул" width="120">
                <template #default="scope">
                    <span class="font-bold">{{ scope.row.sku }}</span>
                </template>
            </el-table-column>
            
            <el-table-column prop="name" label="Назва товару" min-width="200">
                 <template #default="scope">
                    <span class="product-name" @click="handleEdit(scope.row)">{{ scope.row.name }}</span>
                </template>
            </el-table-column>
            
            <el-table-column prop="unit_of_measure" label="Од." width="80" align="center" />
            
            <el-table-column prop="price" label="Ціна" width="120" align="right">
                <template #default="scope">
                    {{ formatCurrency(scope.row.price, scope.row.currency) }}
                </template>
            </el-table-column>

            <el-table-column label="Залишок" width="100" align="center">
                <template #default="scope">
                     <span class="text-gray">-</span> 
                </template>
            </el-table-column>

            <el-table-column label="Дії" width="100" align="right">
              <template #default="scope">
                <el-button link type="primary" :icon="Edit" @click="handleEdit(scope.row)"></el-button>
                <el-button link type="danger" :icon="Delete" @click="handleDelete(scope.row)"></el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="total"
              :page-size="limit"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>

    <!-- Add/Edit Modal (Updated with Tabs and Variants) -->
    <el-dialog v-model="dialogVisible" :title="isEditMode ? 'Редагувати товар' : 'Додати товар'" width="800px">
        <el-tabs v-model="activeTab">
            <el-tab-pane label="Загальна інформація" name="general">
                <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-width="120px" label-position="top">
                    <el-row :gutter="20">
                        <el-col :span="12">
                             <el-form-item label="Артикул (SKU)" prop="sku">
                                <el-input v-model="productForm.sku" placeholder="Напр. WOOD-001" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="Категорія" prop="category">
                                 <el-select v-model="productForm.category" placeholder="Оберіть категорію" style="width: 100%" @change="handleCategoryChange">
                                    <el-option 
                                        v-for="item in categoryOptions"
                                        :key="item.code"
                                        :label="item.name" 
                                        :value="item.code" 
                                    />
                                 </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-form-item label="Назва товару" prop="name">
                        <el-input v-model="productForm.name" placeholder="Введіть назву товару" />
                    </el-form-item>
                    
                    <el-row :gutter="20">
                        <el-col :span="8">
                             <el-form-item label="Од. виміру" prop="unit_of_measure">
                                <el-select v-model="productForm.unit_of_measure" placeholder="Од.">
                                    <el-option v-for="item in uomOptions" :key="item.code" :label="item.name" :value="item.code" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="Ціна продажу" prop="price">
                                <el-input-number v-model="productForm.price" :precision="2" :step="100" :min="0" style="width: 100%" />
                            </el-form-item>
                        </el-col>
                         <el-col :span="8">
                            <el-form-item label="Валюта" prop="currency">
                                 <el-select v-model="productForm.currency" placeholder="Валюта">
                                    <el-option v-for="item in currencyOptions" :key="item.code" :label="item.code" :value="item.code" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-form-item label="Опис" prop="description">
                        <el-input v-model="productForm.description" type="textarea" rows="3" />
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <el-tab-pane label="Характеристики та Варіанти" name="variants">
                <ProductVariantsManager 
                    v-if="productForm.category"
                    :category-attributes="currentCategoryAttributes"
                    :product-code="productForm.sku"
                    :initial-variants="productForm.variants"
                    @update:variants="(val) => productForm.variants = val"
                />
                <el-alert v-else title="Спершу оберіть категорію товару" type="warning" show-icon :closable="false" />
            </el-tab-pane>
        </el-tabs>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">Скасувати</el-button>
                <el-button type="primary" @click="submitProduct" :loading="submitting">
                    {{ isEditMode ? 'Зберегти зміни' : 'Створити' }}
                </el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { Plus, Search, Edit, Delete, Picture, Menu, Folder, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import ProductVariantsManager from '@/components/ProductVariantsManager.vue'

// State
const activeTab = ref('general')
const loading = ref(false)
const submitting = ref(false)
const products = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(20)

const searchQuery = ref('')
const filterCategory = ref('')

const dialogVisible = ref(false)
const isEditMode = ref(false)
const productFormRef = ref(null)

// Dictionaries
const uomOptions = ref([])
const categoryOptions = ref([])
const currencyOptions = ref([])
const currentCategoryAttributes = ref([])

// Form
const productForm = reactive({
    id: null,
    sku: '',
    name: '',
    category: '',
    unit_of_measure: 'шт',
    price: 0,
    currency: 'UAH',
    description: '',
    image_url: '',
    variants: []
})

const productRules = {
    sku: [{ required: true, message: 'Введіть артикул', trigger: 'blur' }],
    name: [{ required: true, message: 'Введіть назву', trigger: 'blur' }],
    unit_of_measure: [{ required: true, message: 'Оберіть од. виміру', trigger: 'change' }],
    price: [{ required: true, message: 'Введіть ціну', trigger: 'blur' }],
}

// API Actions
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
        products.value = response.data
        // Assume rough total for now as API response is simple list
        total.value = products.value.length < limit.value ? products.value.length + skip.value : 100 
    } catch (error) {
        ElMessage.error('Помилка завантаження товарів')
    } finally {
        loading.value = false
    }
}

const submitProduct = async () => {
    if (!productFormRef.value) return
    
    await productFormRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                // Ensure variants data is properly formatted (it should be ref'd correctly)
                const payload = { ...productForm }
                
                if (isEditMode.value) {
                    await api.put(`/api/v1/products/${productForm.id}`, payload)
                    ElMessage.success('Товар оновлено')
                } else {
                    await api.post('/api/v1/products', payload)
                    ElMessage.success('Товар створено')
                }
                dialogVisible.value = false
                fetchProducts()
            } catch (error) {
                console.error(error)
                ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
            } finally {
                submitting.value = false
            }
        }
    })
}

const handleDelete = (row) => {
    ElMessageBox.confirm(
        `Ви впевнені, що хочете видалити ${row.name}?`,
        'Увага',
        {
            confirmButtonText: 'Видалити',
            cancelButtonText: 'Скасувати',
            type: 'warning',
        }
    ).then(async () => {
        try {
            await api.delete(`/api/v1/products/${row.id}`)
            ElMessage.success('Товар видалено')
            fetchProducts()
        } catch (error) {
            ElMessage.error('Помилка видалення')
        }
    })
}

// UI Handlers
const handleCategorySelect = (index) => {
    filterCategory.value = index
    skip.value = 0
    fetchProducts()
}

const handleSearch = () => {
    skip.value = 0
    setTimeout(() => {
        fetchProducts()
    }, 500)
}

const handlePageChange = (page) => {
    skip.value = (page - 1) * limit.value
    fetchProducts()
}

const handleCategoryChange = async (val) => {
    if (!val) {
        currentCategoryAttributes.value = []
        return
    }
    await fetchCategoryAttributes(val)
}

const fetchCategoryAttributes = async (categoryCode) => {
    try {
        const response = await api.get(`/api/v1/attributes/category/${categoryCode}`)
        // The API returns links, we need to extract attributes
        currentCategoryAttributes.value = response.data.map(link => link.attribute)
    } catch (e) {
        currentCategoryAttributes.value = []
    }
}

const openAddModal = () => {
    isEditMode.value = false
    activeTab.value = 'general'
    Object.assign(productForm, {
        id: null,
        sku: '',
        name: '',
        category: filterCategory.value || '', 
        unit_of_measure: uomOptions.value.length > 0 ? uomOptions.value[0].code : 'шт',
        price: 0,
        currency: 'UAH',
        description: '',
        image_url: '',
        variants: []
    })
    if (productForm.category) handleCategoryChange(productForm.category)
    dialogVisible.value = true
}

const handleEdit = async (row) => {
    isEditMode.value = true
    activeTab.value = 'general'
    Object.assign(productForm, row)
    // Fetch variants if needed (assuming they are in row or fetch separately)
    if (productForm.category) await handleCategoryChange(productForm.category)
    dialogVisible.value = true
}

const formatCurrency = (value, currency) => {
    return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: currency || 'UAH' }).format(value)
}

onMounted(() => {
    fetchDictionaries()
    fetchProducts()
})
</script>

<style scoped>
.page-container {
    height: calc(100vh - 84px);
    display: flex;
    flex-direction: column;
}

.page-header {
    margin-bottom: 20px;
    flex-shrink: 0;
}
.page-header h2 {
    margin: 0 0 10px 0;
    color: #303133;
}

.view-layout {
    flex: 1;
    background: white;
    border: 1px solid #e6e6e6;
    border-radius: 4px;
    overflow: hidden;
}

.view-sidebar {
    background-color: #fcfcfc;
    border-right: 1px solid #e6e6e6;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 16px 20px;
    font-weight: 600;
    color: #606266;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.category-menu {
    border-right: none;
    background: transparent;
    flex: 1;
    overflow-y: auto;
}

.view-content {
    padding: 0;
    background-color: #fff;
    display: flex;
    flex-direction: column;
}

.content-card {
    border: none;
    box-shadow: none !important;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.content-card :deep(.el-card__body) {
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.search-input {
    width: 300px;
}

.data-table {
    flex: 1;
}

.product-name {
    font-weight: 500;
    color: #409eff;
    cursor: pointer;
}
.product-name:hover {
    text-decoration: underline;
}

.font-bold {
    font-weight: 600;
}

.text-gray {
    color: #909399;
}

.image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f5f7fa;
    color: #909399;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style>
