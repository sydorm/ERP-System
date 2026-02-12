<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Номенклатура</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
          <el-breadcrumb-item>Склад</el-breadcrumb-item>
          <el-breadcrumb-item>Номенклатура</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="openAddModal">Додати товар</el-button>
      </div>
    </div>

    <el-card class="table-card">
      <!-- Search & Filters -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук за назвою або артикулом..."
          prefix-icon="Search"
          class="search-input"
          clearable
          @input="handleSearch"
        />
        <el-select v-model="filterCategory" placeholder="Категорія" clearable class="filter-select" @change="fetchProducts">
          <el-option label="Листові матеріали" value="sheets" />
          <el-option label="Клей" value="glue" />
          <el-option label="Фурнітура" value="hardware" />
        </el-select>
        <el-button :icon="Refresh" circle @click="refreshData" />
      </div>

      <!-- Data Table -->
      <el-table :data="products" stripe style="width: 100%" v-loading="loading">
        <el-table-column width="80" label="Фото">
            <template #default="scope">
                <el-image 
                    style="width: 40px; height: 40px; border-radius: 4px"
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
        
        <el-table-column prop="category" label="Категорія" width="150">
            <template #default="scope">
                <el-tag size="small" type="info">{{ scope.row.category || 'Без категорії' }}</el-tag>
            </template>
        </el-table-column>
        
        <el-table-column prop="unit_of_measure" label="Од." width="80" align="center" />
        
        <el-table-column prop="price" label="Ціна" width="120" align="right">
            <template #default="scope">
                {{ formatCurrency(scope.row.price, scope.row.currency) }}
            </template>
        </el-table-column>

        <!-- Stock is not yet implemented in backend, using placeholder or mock if needed. 
             For now, we don't have stock field in Product model, it will be in StockBalance.
             We will hide this column or show 0 until Phase 3. -->
        <el-table-column label="Залишок" width="120" align="center">
            <template #default="scope">
                 <span class="text-gray">0</span>
            </template>
        </el-table-column>

        <el-table-column label="Статус" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="dark" size="small" round>
                {{ scope.row.is_active ? 'Активний' : 'Неактивний' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="120" align="right">
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

    <!-- Add/Edit Modal -->
    <el-dialog v-model="dialogVisible" :title="isEditMode ? 'Редагувати товар' : 'Додати товар'" width="600px">
        <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-width="120px" label-position="top">
            <el-row :gutter="20">
                <el-col :span="12">
                     <el-form-item label="Артикул (SKU)" prop="sku">
                        <el-input v-model="productForm.sku" placeholder="Напр. WOOD-001" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="Категорія" prop="category">
                         <el-select v-model="productForm.category" placeholder="Оберіть категорію" style="width: 100%">
                            <el-option label="Листові матеріали" value="sheets" />
                            <el-option label="Клей" value="glue" />
                            <el-option label="Фурнітура" value="hardware" />
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
                            <el-option label="шт" value="шт" />
                            <el-option label="м2" value="м2" />
                            <el-option label="м3" value="м3" />
                            <el-option label="кг" value="кг" />
                            <el-option label="л" value="л" />
                            <el-option label="уп" value="уп" />
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="Ціна продажу" prop="price">
                        <el-input-number v-model="productForm.price" :precision="2" :step="0.01" :min="0" style="width: 100%" />
                    </el-form-item>
                </el-col>
                 <el-col :span="8">
                    <el-form-item label="Валюта" prop="currency">
                         <el-select v-model="productForm.currency" placeholder="Валюта">
                            <el-option label="UAH" value="UAH" />
                            <el-option label="USD" value="USD" />
                            <el-option label="EUR" value="EUR" />
                        </el-select>
                    </el-form-item>
                </el-col>
            </el-row>

            <el-form-item label="Опис" prop="description">
                <el-input v-model="productForm.description" type="textarea" rows="3" />
            </el-form-item>
             <el-form-item label="Посилання на фото" prop="image_url">
                <el-input v-model="productForm.image_url" placeholder="https://example.com/image.jpg" />
            </el-form-item>
        </el-form>
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
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { debounce } from 'lodash' // Make sure lodash is available or implement debounce

// State
const loading = ref(false)
const submitting = ref(false)
const products = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)

const searchQuery = ref('')
const filterCategory = ref('')

const dialogVisible = ref(false)
const isEditMode = ref(false)
const productFormRef = ref(null)

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
    image_url: ''
})

const productRules = {
    sku: [{ required: true, message: 'Введіть артикул', trigger: 'blur' }],
    name: [{ required: true, message: 'Введіть назву', trigger: 'blur' }],
    unit_of_measure: [{ required: true, message: 'Оберіть од. виміру', trigger: 'change' }],
    price: [{ required: true, message: 'Введіть ціну', trigger: 'blur' }],
}

// API Actions
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
        // Note: API currently returns list, not {items, total}. 
        // We might need to update API to return total for pagination.
        // For now assume list length is total or handled simply.
        total.value = 100 // Mock total for now as API doesn't return count yet
    } catch (error) {
        ElMessage.error('Помилка завантаження товарів')
        console.error(error)
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
                if (isEditMode.value) {
                    await api.put(`/api/v1/products/${productForm.id}`, productForm)
                    ElMessage.success('Товар оновлено')
                } else {
                    await api.post('/api/v1/products', productForm)
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

// UI Helpers
const openAddModal = () => {
    isEditMode.value = false
    Object.assign(productForm, {
        id: null,
        sku: '',
        name: '',
        category: '',
        unit_of_measure: 'шт',
        price: 0,
        currency: 'UAH',
        description: '',
        image_url: ''
    })
    dialogVisible.value = true
}

const handleEdit = (row) => {
    isEditMode.value = true
    Object.assign(productForm, row)
    dialogVisible.value = true
}

const formatCurrency = (value, currency) => {
    return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: currency || 'UAH' }).format(value)
}

const getStockClass = (stock) => {
    return stock < 10 ? 'text-danger' : 'text-success'
}

const handleSearch = () => {
    // Debounce manual implementation since lodash might be missing
    // Actually standard input debounce is better but simple wait is ok
    setTimeout(() => {
        fetchProducts()
    }, 500)
}

const handlePageChange = (page) => {
    skip.value = (page - 1) * limit.value
    fetchProducts()
}

const refreshData = () => {
    fetchProducts()
}

onMounted(() => {
    fetchProducts()
})
</script>

<style scoped>
.page-container {
    max-width: 100%;
}
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.header-left h2 {
    margin: 0 0 8px 0;
    color: #303133;
}
.filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}
.search-input {
    width: 300px;
}
.filter-select {
    width: 200px;
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
.text-danger {
    color: #f56c6c;
    font-weight: 600;
}
.text-success {
    color: #67c23a;
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
