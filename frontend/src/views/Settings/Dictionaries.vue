<template>
  <div class="dictionaries-container">
    <div class="page-header">
      <div class="header-content">
        <h2>Системні довідники</h2>
        <p class="text-gray">Налаштування довідкових даних системи ERP</p>
      </div>
    </div>

    <div class="dict-layout">
      <!-- Left Sidebar: Categories -->
      <div class="dict-sidebar">
        <div class="sidebar-title">Довідники</div>
        <div class="category-list">
            <div 
                v-for="cat in categories" 
                :key="cat.code"
                class="category-item" 
                :class="{ active: activeCategory === cat.code }"
                @click="handleCategorySelect(cat.code)"
            >
                <div class="cat-icon">
                    <el-icon><component :is="cat.icon" /></el-icon>
                </div>
                <div class="cat-info">
                    <div class="cat-name">{{ cat.name }}</div>
                    <div class="cat-count">{{ counts[cat.code] || 0 }} значень</div>
                </div>
                <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
        </div>
      </div>

      <!-- Main Content: Items List -->
      <div class="dict-content">
        <div class="content-header">
            <div class="content-title">
                <h3>{{ currentCategoryName }}</h3>
                <p>Класифікація та параметри для розділу {{ currentCategoryName.toLowerCase() }}</p>
            </div>
            <div class="header-actions">
                <el-button-group class="mr-2">
                    <el-button :icon="Download" @click="handleExport">Експорт</el-button>
                    <el-button :icon="Upload" @click="handleImport">Імпорт</el-button>
                </el-button-group>
                <el-button type="primary" :icon="Plus" @click="openAddModal">
                    Додати значення
                </el-button>
            </div>
        </div>

        <div class="search-bar">
            <el-input 
                v-model="searchQuery" 
                placeholder="Пошук..." 
                prefix-icon="Search"
                clearable
            />
        </div>

        <div class="items-list" v-loading="loading">
            <!-- SPECIAL CASE: PRODUCT ATTRIBUTES -->
            <template v-if="activeCategory === 'PRODUCT_ATTRIBUTES'">
                <div v-for="(item, index) in filteredItems" :key="item.id || index" class="list-item attribute-item">
                    <div class="item-left">
                        <div class="item-icon-circle bg-gray-light">
                            <el-icon v-if="item.type === 'COLOR'"><Brush /></el-icon>
                            <el-icon v-else-if="item.type === 'SELECT'"><Collection /></el-icon>
                            <el-icon v-else-if="item.type === 'NUMBER'"><Edit /></el-icon>
                            <el-icon v-else><Edit /></el-icon>
                        </div>
                        <div class="item-details">
                            <div class="item-name">
                                {{ item.name }}
                                <el-tag size="small" :type="getTypeTag(item.type)">{{ item.type }}</el-tag>
                            </div>
                            <div class="item-desc">
                                <span v-if="item.options?.length">{{ item.options.length }} варіантів: </span>
                                <span class="options-preview">
                                    {{ item.options?.slice(0, 3).map(o => o.value).join(', ') }}
                                    <span v-if="item.options?.length > 3">...</span>
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="item-right">
                       <el-tag v-if="item.is_archived" type="info">В архіві</el-tag>
                        <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, item)">
                            <span class="action-btn">
                                <el-icon><MoreFilled /></el-icon>
                            </span>
                            <template #dropdown>
                                <el-dropdown-menu>
                                    <el-dropdown-item command="edit">Редагувати</el-dropdown-item>
                                    <el-dropdown-item command="copy">Копіювати</el-dropdown-item>
                                    <el-dropdown-item command="archive" v-if="!item.is_archived">В архів</el-dropdown-item>
                                    <el-dropdown-item command="delete" divided class="text-danger">Видалити</el-dropdown-item>
                                </el-dropdown-menu>
                            </template>
                        </el-dropdown>
                    </div>
                </div>
            </template>

            <!-- GENERIC ITEMS -->
            <template v-else>
                <div v-for="(item, index) in filteredItems" :key="item.id || index" class="list-item">
                    <div class="item-left">
                        <div class="item-badge" :class="`bg-${item.color || 'blue'}`">
                            {{ index + 1 }}
                        </div>
                        <div class="item-details">
                            <div class="item-name">
                                {{ item.name }}
                                <span class="item-code">{{ item.code }}</span>
                            </div>
                            <div class="item-desc">{{ item.description || 'Опис елемента (placeholder)' }}</div>
                        </div>
                    </div>
                    
                    <div class="item-right">
                       <el-switch 
                            v-model="item.is_active" 
                            active-color="#13ce66" 
                            inactive-color="#ff4949"
                            :disabled="item.is_fixed"
                            @change="handleToggle(item)"
                        />
                        
                <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, item)">
                    <span class="action-btn">
                        <el-icon><MoreFilled /></el-icon>
                    </span>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="edit" :disabled="item.is_fixed">Редагувати</el-dropdown-item>
                            <el-dropdown-item v-if="activeCategory === 'PRODUCT_CATEGORY'" command="attributes">Налаштувати характеристики</el-dropdown-item>
                            <el-dropdown-item command="delete" :disabled="item.is_fixed" divided class="text-danger">Видалити</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>
    </template>
    
    <el-empty v-if="filteredItems.length === 0" description="Немає записів" />
</div>

<!-- Attributes Linking Dialog -->
<el-dialog v-model="linkDialogVisible" title="Характеристики категорії" width="500px">
    <div v-loading="linkingLoading">
        <p class="mb-4 text-gray">Виберіть характеристики, які будуть доступні для товарів цієї категорії:</p>
        <el-checkbox-group v-model="selectedCategoryAttributes">
            <div v-for="attr in allAttributes" :key="attr.id" class="mb-2">
                <el-checkbox :label="attr.id">{{ attr.name }}</el-checkbox>
            </div>
        </el-checkbox-group>
    </div>
    <template #footer>
        <el-button @click="linkDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" @click="saveCategoryLinks">Зберегти</el-button>
    </template>
</el-dialog>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <!-- Add/Edit Modal (Updated for Attributes) -->
    <el-dialog v-model="dialogVisible" :title="isEditMode ? 'Редагувати' : 'Додати'" width="600px" class="custom-dialog">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
            
            <template v-if="activeCategory === 'PRODUCT_ATTRIBUTES'">
                <el-row :gutter="20">
                    <el-col :span="14">
                        <el-form-item label="Назва характеристики" prop="name">
                            <el-input v-model="form.name" placeholder="напр. Матеріал каркасу" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="10">
                        <el-form-item label="Тип даних">
                            <el-select v-model="form.type" placeholder="Оберіть тип">
                                <el-option label="Список (Select)" value="SELECT" />
                                <el-option label="Колір (Color)" value="COLOR" />
                                <el-option label="Текст" value="TEXT" />
                                <el-option label="Число" value="NUMBER" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>

                <!-- OPTIONS LIST FOR SELECT/COLOR -->
                <div v-if="['SELECT', 'COLOR'].includes(form.type)" class="options-container mb-4">
                    <div class="flex justify-between items-center mb-2">
                        <label class="el-form-item__label">Варіанти значень</label>
                        <el-button type="primary" size="small" link @click="addAttributeOption">
                            <el-icon><Plus /></el-icon> Додати значення
                        </el-button>
                    </div>
                    
                    <div class="options-list">
                        <div v-for="(opt, idx) in form.options" :key="idx" class="option-row">
                            <el-icon class="drag-handle"><Rank /></el-icon>
                            
                            <el-color-picker v-if="form.type === 'COLOR'" v-model="opt.color_code" size="small" class="mr-2" />
                            
                            <el-input v-model="opt.value" placeholder="Значення" size="small" class="flex-1" />
                            
                            <el-button type="danger" :icon="Close" circle size="small" @click="removeAttributeOption(idx)" />
                        </div>
                    </div>
                </div>

                <el-form-item label="Опис">
                    <el-input v-model="form.description" type="textarea" :rows="2" />
                </el-form-item>
            </template>

            <template v-else>
                <el-form-item label="Назва" prop="name">
                    <el-input v-model="form.name" :placeholder="currentPlaceholders.name" />
                </el-form-item>
                
                <el-form-item label="Код (унікальний)" prop="code">
                    <el-input v-model="form.code" :placeholder="currentPlaceholders.code" :disabled="isEditMode && form.is_fixed" />
                </el-form-item>

                <el-form-item label="Опис (опціонально)">
                    <el-input v-model="form.description" :placeholder="currentPlaceholders.desc" />
                </el-form-item>

                <el-form-item v-if="activeCategory === 'PRODUCT_CATEGORY'" label="Шаблон SKU (напр. {CAT}-{COLOR})">
                    <template #label>
                        <span>Шаблон SKU </span>
                        <el-tooltip content="Доступні змінні: {CAT}, {COLOR}, {SIZE}, {MATERIAL}, {WIDTH}" placement="top">
                            <el-icon><QuestionFilled /></el-icon>
                        </el-tooltip>
                    </template>
                    <el-input v-model="form.sku_template" placeholder="{CAT}-{COLOR}-{WIDTH}" />
                </el-form-item>
                
                <el-form-item label="Колір">
                    <div class="color-picker">
                        <div 
                            v-for="color in colors" 
                            :key="color.value"
                            class="color-circle"
                            :class="[{ active: form.color === color.value }, `bg-${color.value}`]"
                            @click="form.color = color.value"
                        ></div>
                    </div>
                </el-form-item>
            </template>
            
            <el-form-item>
                <div class="flex-center">
                    <el-switch v-model="form.is_active" />
                    <span style="margin-left: 10px">Активне</span>
                </div>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">Скасувати</el-button>
                <el-button type="primary" @click="submitForm" :loading="submitting">
                    {{ isEditMode ? 'Зберегти' : 'Додати' }}
                </el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { 
    ScaleToOriginal, Box, List, CreditCard, 
    Plus, Search, ArrowRight, MoreFilled, 
    Check, Close, Rank, QuestionFilled,
    Download, Upload
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// State
const activeCategory = ref('PRODUCT_CATEGORY')
const localItems = ref([])
const counts = ref({})
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEditMode = ref(false)
const searchQuery = ref('')

const form = reactive({
    id: null,
    name: '',
    code: '',
    type: 'SELECT',
    options: [],
    sort_order: 0,
    color: 'blue',
    description: '',
    sku_template: '',
    is_active: true,
    is_fixed: false,
    is_archived: false
})

const getTypeTag = (type) => {
    const tags = { 'COLOR': 'success', 'SELECT': 'primary', 'NUMBER': 'warning', 'TEXT': 'info' }
    return tags[type] || 'info'
}

const addAttributeOption = () => {
    if (!form.options) form.options = []
    form.options.push({ value: '', color_code: '#409EFF' })
}

const removeAttributeOption = (idx) => {
    form.options.splice(idx, 1)
}

const rules = {
    name: [{ required: true, message: 'Введіть назву', trigger: 'blur' }],
    code: [{ required: true, message: 'Введіть код', trigger: 'blur' }]
}

const colors = [
    { value: 'blue', hex: '#409eff' },
    { value: 'green', hex: '#67c23a' },
    { value: 'orange', hex: '#e6a23c' },
    { value: 'red', hex: '#f56c6c' },
    { value: 'purple', hex: '#9c27b0' },
    { value: 'teal', hex: '#009688' },
    { value: 'gray', hex: '#909399' },
]

const categories = [
    { code: 'ORDER_STATUS', name: 'Статуси замовлень', icon: List },
    { code: 'PAYMENT_METHOD', name: 'Статуси оплати', icon: CreditCard }, 
    { code: 'PAYMENT_METHOD_TYPE', name: 'Способи оплати', icon: CreditCard },
    { code: 'DELIVERY_METHOD', name: 'Способи доставки', icon: Box }, 
    { code: 'PRODUCT_CATEGORY', name: 'Категорії товарів', icon: Box },
    { code: 'PRODUCT_ATTRIBUTES', name: 'Характеристики товарів', icon: Setting },
    { code: 'UOM', name: 'Одиниці виміру', icon: ScaleToOriginal },
    { code: 'CURRENCY', name: 'Валюти', icon: Money }, 
    { code: 'CLIENT_SOURCE', name: 'Джерела клієнтів', icon: UserIcon }, 
]

// Import icons
import { User as UserIcon, Money, Setting, Collection, Brush, Edit, PriceTag } from '@element-plus/icons-vue'


// Placeholders Configuration
const categoryPlaceholders = {
    'UOM': { name: 'Наприклад: Кілограм', code: 'kg', desc: 'Одиниця виміру маси' },
    'PRODUCT_CATEGORY': { name: 'Наприклад: Меблі', code: 'furniture', desc: 'Столи, стільці, дивани' },
    'PRODUCT_ATTRIBUTES': { name: 'Наприклад: Тканина', code: 'fabric', desc: 'Тип оббивки меблів' },
    'ORDER_STATUS': { name: 'Наприклад: Новий', code: 'new', desc: 'Замовлення щойно створено' },
}

// Computed
const currentCategoryName = computed(() => {
    const cat = categories.find(c => c.code === activeCategory.value)
    return cat ? cat.name : ''
})

const currentPlaceholders = computed(() => {
    return categoryPlaceholders[activeCategory.value] || { 
        name: 'Наприклад: Значення', 
        code: 'code', 
        desc: 'Опис значення' 
    }
})

const filteredItems = computed(() => {
    if (!searchQuery.value) return localItems.value
    const lower = searchQuery.value.toLowerCase()
    return localItems.value.filter(item => 
        item.name.toLowerCase().includes(lower) || 
        (item.code && item.code.toLowerCase().includes(lower))
    )
})

// Actions
const fetchCounts = async () => {
    try {
        const response = await api.get('/api/v1/dictionaries/meta/counts')
        counts.value = response.data
    } catch (error) {
        console.error('Failed to load counts')
    }
}

const fetchItems = async () => {
    loading.value = true
    try {
        const url = activeCategory.value === 'PRODUCT_ATTRIBUTES' 
            ? '/api/v1/attributes' 
            : `/api/v1/dictionaries/${activeCategory.value}`
            
        const response = await api.get(url)
        localItems.value = response.data
    } catch (error) {
        localItems.value = []
    } finally {
        loading.value = false
    }
}

const handleCategorySelect = (code) => {
    activeCategory.value = code
    fetchItems()
}

const openAddModal = () => {
    isEditMode.value = false
    clearForm()
    dialogVisible.value = true
}

const clearForm = () => {
    form.id = null
    form.name = ''
    form.code = ''
    form.type = 'SELECT'
    form.options = []
    form.sort_order = localItems.value.length + 1
    form.color = 'blue'
    form.description = ''
    form.sku_template = ''
    form.is_active = true
    form.is_fixed = false
    form.is_archived = false
}

const linkDialogVisible = ref(false)
const linkingLoading = ref(false)
const allAttributes = ref([])
const selectedCategoryAttributes = ref([])
const currentCategoryId = ref(null)
const currentCategoryCode = ref(null)

const handleCommand = (cmd, item) => {
    if (cmd === 'edit') {
        isEditMode.value = true
        Object.assign(form, item)
        dialogVisible.value = true
    } else if (cmd === 'copy') {
        isEditMode.value = false
        clearForm()
        form.name = `${item.name} (копія)`
        form.type = item.type
        form.options = JSON.parse(JSON.stringify(item.options || []))
        dialogVisible.value = true
    } else if (cmd === 'archive') {
        handleArchive(item)
    } else if (cmd === 'attributes') {
        openLinkDialog(item)
    } else if (cmd === 'delete') {
        handleDelete(item)
    }
}

const openLinkDialog = async (category) => {
    currentCategoryId.value = category.id
    currentCategoryCode.value = category.code
    linkDialogVisible.value = true
    linkingLoading.value = true
    try {
        const [allRes, linkedRes] = await Promise.all([
            api.get('/api/v1/attributes'),
            api.get(`/api/v1/attributes/category/${category.code}`)
        ])
        allAttributes.value = allRes.data
        selectedCategoryAttributes.value = linkedRes.data.map(l => l.attribute_id)
    } catch (e) {
        ElMessage.error('Помилка завантаження характеристик')
    } finally {
        linkingLoading.value = false
    }
}

const saveCategoryLinks = async () => {
    linkingLoading.value = true
    try {
        // Simple logic: for each selected, send link request (backend should handle duplicates)
        // Ideally we should sync (delete unselected, add new)
        for (const attrId of selectedCategoryAttributes.value) {
            await api.post('/api/v1/attributes/category', {
                category_code: currentCategoryCode.value,
                attribute_id: attrId
            })
        }
        ElMessage.success('Характеристики прив\'язано')
        linkDialogVisible.value = false
    } catch (e) {
        ElMessage.error('Помилка збереження зв\'язків')
    } finally {
        linkingLoading.value = false
    }
}

const handleArchive = (row) => {
    ElMessageBox.confirm(
        `Перенести в архів характеристику "${row.name}"? Вона перестане пропонуватися в нових товарах.`,
        'Архівування',
        { confirmButtonText: 'В архів', type: 'info' }
    ).then(async () => {
        try {
            await api.patch(`/api/v1/attributes/${row.id}/archive`)
            ElMessage.success('Перенесено в архів')
            fetchItems()
        } catch (error) {
            ElMessage.error('Помилка архівування')
        }
    })
}

const handleToggle = async (item) => {
    // Implement API call to toggle status
    ElMessage.success(`Статус змінено: ${item.is_active ? 'Активний' : 'Неактивний'}`)
}

const submitForm = async () => {
    if (!formRef.value) return
    
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                if (activeCategory.value === 'PRODUCT_ATTRIBUTES') {
                    const url = '/api/v1/attributes'
                    await api.post(url, form)
                } else {
                    const payload = { ...form, category: activeCategory.value }
                    await api.post('/api/v1/dictionaries', payload)
                }
                
                ElMessage.success('Збережено успішно')
                dialogVisible.value = false
                fetchItems()
                fetchCounts()
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
            fetchCounts()
        } catch (error) {
            ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
        }
    })
}

onMounted(() => {
    fetchItems()
    fetchCounts()
})
</script>

<style scoped>
.dictionaries-container {
    padding: 24px;
    height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    background: #f5f6f8; /* Kimi background */
}

.page-header {
    margin-bottom: 24px;
}

.page-header h2 {
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.text-gray {
    color: #8c8c8c;
    font-size: 14px;
    margin: 0;
}

.dict-layout {
    display: flex;
    gap: 24px;
    flex: 1;
    overflow: hidden;
}

/* Sidebar */
.dict-sidebar {
    width: 280px;
    background: white;
    border-radius: 12px;
    padding: 20px 0;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.sidebar-title {
    padding: 0 20px 16px;
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
}

.category-list {
    flex: 1;
    overflow-y: auto;
}

.category-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    cursor: pointer;
    transition: all 0.2s;
    border-left: 3px solid transparent;
}

.category-item:hover {
    background: #f9fafb;
}

.category-item.active {
    background: #e6f7ff; /* Kimi blue tint */
    border-left-color: #1890ff;
}

.cat-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f0f2f5;
    border-radius: 8px;
    color: #595959;
    margin-right: 12px;
}

.category-item.active .cat-icon {
    background: #1890ff;
    color: white;
}

.cat-info {
    flex: 1;
}

.cat-name {
    font-size: 14px;
    font-weight: 500;
    color: #262626;
    margin-bottom: 2px;
}

.cat-count {
    font-size: 12px;
    color: #8c8c8c;
}

.arrow-icon {
    font-size: 14px;
    color: #bfbfbf;
}

/* Main Content */
.dict-content {
    flex: 1;
    background: white;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.content-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
}

.content-title h3 {
    margin: 0 0 4px 0;
    font-size: 18px;
    font-weight: 600;
}

.content-title p {
    margin: 0;
    color: #8c8c8c;
    font-size: 13px;
}

.search-bar {
    margin-bottom: 20px;
}

.items-list {
    flex: 1;
    overflow-y: auto;
}

.list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    margin-bottom: 12px;
    background: white;
    transition: all 0.2s;
}

.list-item:hover {
    border-color: #d9d9d9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.item-left {
    display: flex;
    align-items: center;
}

.item-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    margin-right: 16px;
    font-size: 14px;
}

.item-details {
    display: flex;
    flex-direction: column;
}

.item-name {
    font-weight: 600;
    color: #262626;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.item-code {
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    color: #8c8c8c;
    font-weight: normal;
}

.item-desc {
    font-size: 13px;
    color: #8c8c8c;
    margin-top: 2px;
}

.item-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.action-btn {
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    color: #8c8c8c;
}
.action-btn:hover {
    background: #f5f5f5;
    color: #262626;
}

/* Attribute specific */
.attribute-item {
    border-left: 4px solid #1890ff;
}

.item-icon-circle {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    font-size: 18px;
    color: #595959;
}

.bg-gray-light { background: #f0f2f5; }

.options-preview {
    font-weight: 500;
    color: #595959;
}

.options-container {
    background: #f9fafb;
    padding: 12px;
    border-radius: 8px;
    border: 1px dashed #d9d9d9;
}

.option-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    background: white;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #f0f0f0;
}

.drag-handle {
    cursor: grab;
    color: #bfbfbf;
}

.mb-4 { margin-bottom: 16px; }
.mb-2 { margin-bottom: 8px; }
.mr-2 { margin-right: 8px; }
.flex-1 { flex: 1; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }

/* Existing Colors */
.bg-blue { background-color: #409eff; }
.bg-green { background-color: #67c23a; }
.bg-orange { background-color: #e6a23c; }
.bg-red { background-color: #f56c6c; }
.bg-purple { background-color: #9c27b0; }
.bg-teal { background-color: #009688; }
.bg-gray { background-color: #909399; }

/* Modal */
.color-picker {
    display: flex;
    gap: 12px;
}
.color-circle {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid transparent;
    transition: transform 0.2s;
}
.color-circle.active {
    transform: scale(1.2);
    border-color: #333;
}
.text-danger {
    color: #f56c6c;
}
.flex-center {
    display: flex;
    align-items: center;
}
</style>
