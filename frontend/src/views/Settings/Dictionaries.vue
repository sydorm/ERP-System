<template>
  <div class="dictionaries-container">
    <div class="page-header">
      <h2>Системні Довідники</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
        <el-breadcrumb-item>Налаштування</el-breadcrumb-item>
        <el-breadcrumb-item>Довідники</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-container class="dict-layout">
      <!-- Left Sidebar: Categories -->
      <el-aside width="250px" class="dict-sidebar">
        <el-menu
          :default-active="activeCategory"
          class="dict-menu"
          @select="handleCategorySelect"
        >
          <el-menu-item index="UOM">
            <el-icon><ScaleToOriginal /></el-icon>
            <span>Одиниці виміру</span>
          </el-menu-item>
          <el-menu-item index="PRODUCT_CATEGORY">
            <el-icon><Box /></el-icon>
            <span>Категорії товарів</span>
          </el-menu-item>
          <el-menu-item index="ORDER_STATUS">
            <el-icon><List /></el-icon>
            <span>Статуси замовлень</span>
          </el-menu-item>
          <el-menu-item index="PAYMENT_METHOD">
            <el-icon><CreditCard /></el-icon>
            <span>Методи оплати</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- Main Content: Items List -->
      <el-main class="dict-content">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>{{ currentCategoryName }}</span>
              <el-button type="primary" size="small" :icon="Plus" @click="openAddModal">
                Додати значення
              </el-button>
            </div>
          </template>

          <el-table :data="localItems" v-loading="loading" style="width: 100%">
             <el-table-column prop="sort_order" label="№" width="60" align="center" />
             
             <el-table-column prop="name" label="Назва" min-width="150">
                <template #default="scope">
                    <span class="font-medium">{{ scope.row.name }}</span>
                </template>
             </el-table-column>
             
             <el-table-column prop="code" label="Код" width="120">
                 <template #default="scope">
                    <el-tag type="info" size="small">{{ scope.row.code }}</el-tag>
                 </template>
             </el-table-column>

             <el-table-column label="Колір" width="100" align="center">
                <template #default="scope">
                    <div v-if="scope.row.color" class="color-preview">
                        <el-tag :type="scope.row.color" effect="dark" size="small">Test</el-tag>
                    </div>
                    <span v-else>-</span>
                </template>
             </el-table-column>

             <el-table-column label="Системний" width="100" align="center">
                <template #default="scope">
                    <el-icon v-if="scope.row.is_fixed" color="#909399"><Lock /></el-icon>
                </template>
             </el-table-column>

             <el-table-column label="Дії" width="100" align="right">
                <template #default="scope">
                    <el-button 
                        v-if="!scope.row.is_fixed"
                        link 
                        type="danger" 
                        :icon="Delete" 
                        @click="handleDelete(scope.row)"
                    ></el-button>
                    <span v-else class="text-xs text-gray-400">Fixed</span>
                </template>
             </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>

    <!-- Add Item Modal -->
    <el-dialog v-model="dialogVisible" title="Додати значення" width="400px">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
            <el-form-item label="Назва" prop="name">
                <el-input v-model="form.name" placeholder="Наприклад: Кілограм" />
            </el-form-item>
            <el-form-item label="Код (English)" prop="code">
                <el-input v-model="form.code" placeholder="Наприклад: kg" />
            </el-form-item>
            <el-form-item label="Порядок сортування" prop="sort_order">
                <el-input-number v-model="form.sort_order" :min="0" />
            </el-form-item>
            
            <div v-if="activeCategory === 'ORDER_STATUS'">
                <el-form-item label="Колір (для статусів)">
                    <el-select v-model="form.color" placeholder="Оберіть колір">
                        <el-option label="Сірий (Default)" value="info" />
                        <el-option label="Синій (Primary)" value="primary" />
                        <el-option label="Зелений (Success)" value="success" />
                        <el-option label="Жовтий (Warning)" value="warning" />
                        <el-option label="Червоний (Danger)" value="danger" />
                    </el-select>
                </el-form-item>
            </div>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">Скасувати</el-button>
                <el-button type="primary" @click="submitForm" :loading="submitting">Зберегти</el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ScaleToOriginal, Box, List, CreditCard, Plus, Delete, Lock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// State
const activeCategory = ref('UOM')
const localItems = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const form = reactive({
    name: '',
    code: '',
    sort_order: 0,
    color: null
})

const rules = {
    name: [{ required: true, message: 'Введіть назву', trigger: 'blur' }],
    code: [{ required: true, message: 'Введіть код', trigger: 'blur' }]
}

// Computed
const currentCategoryName = computed(() => {
    const map = {
        'UOM': 'Одиниці виміру',
        'PRODUCT_CATEGORY': 'Категорії товарів',
        'ORDER_STATUS': 'Статуси замовлень',
        'PAYMENT_METHOD': 'Методи оплати'
    }
    return map[activeCategory.value]
})

// Actions
const fetchItems = async () => {
    loading.value = true
    try {
        const response = await api.get(`/api/v1/dictionaries/${activeCategory.value}`)
        localItems.value = response.data
    } catch (error) {
        ElMessage.error('Помилка завантаження довідника')
    } finally {
        loading.value = false
    }
}

const handleCategorySelect = (index) => {
    activeCategory.value = index
    fetchItems()
}

const openAddModal = () => {
    form.name = ''
    form.code = ''
    form.sort_order = localItems.value.length + 1
    form.color = null
    dialogVisible.value = true
}

const submitForm = async () => {
    if (!formRef.value) return
    
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                await api.post('/api/v1/dictionaries', {
                    category: activeCategory.value,
                    ...form
                })
                ElMessage.success('Запис додано')
                dialogVisible.value = false
                fetchItems()
            } catch (error) {
                ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
            } finally {
                submitting.value = false
            }
        }
    })
}

const handleDelete = (row) => {
    ElMessageBox.confirm(
        `Видалити запис "${row.name}"?`,
        'Увага',
        { confirmButtonText: 'Видалити', type: 'warning' }
    ).then(async () => {
        try {
            await api.delete(`/api/v1/dictionaries/${row.id}`)
            ElMessage.success('Видалено')
            fetchItems()
        } catch (error) {
            ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
        }
    })
}

onMounted(() => {
    fetchItems()
})
</script>

<style scoped>
.dictionaries-container {
    height: calc(100vh - 84px); /* Adjust based on header height */
    display: flex;
    flex-direction: column;
}
.page-header {
    margin-bottom: 20px;
}
.page-header h2 {
    margin: 0 0 10px 0;
}
.dict-layout {
    background: white;
    border: 1px solid #e6e6e6;
    border-radius: 4px;
    flex: 1;
    overflow: hidden;
}
.dict-sidebar {
    border-right: 1px solid #e6e6e6;
    background-color: #fcfcfc;
}
.dict-menu {
    border-right: none;
    background-color: transparent;
}
.dict-content {
    background-color: #fff;
    padding: 20px;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
}
.font-medium {
    font-weight: 500;
}
.text-xs {
    font-size: 12px;
}
.text-gray-400 {
    color: #9ca3af;
}
</style>
