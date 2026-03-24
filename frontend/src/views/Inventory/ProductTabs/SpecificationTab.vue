<template>
  <div class="specification-tab-container">
    
    <!-- LIST VIEW -->
    <div v-if="!editingSpec" class="specs-list">
       <div class="tab-header">
          <h3>Специфікації (Рецептури)</h3>
          <el-button type="primary" @click="createNewSpec" :icon="Plus">Додати специфікацію</el-button>
       </div>
       
       <el-table :data="specifications" v-loading="loading" stripe border style="width: 100%; margin-top: 15px">
          <el-table-column prop="name" label="Назва специфікації" min-width="200" />
          <el-table-column label="Статус" width="120">
             <template #default="scope">
                <el-tag v-if="scope.row.is_default" type="success" effect="dark" size="small">Основна</el-tag>
                <el-tag v-else type="info" size="small">Альтернативна</el-tag>
             </template>
          </el-table-column>
          <el-table-column prop="is_active" label="Активна" width="100">
             <template #default="scope">
                <el-switch v-model="scope.row.is_active" disabled />
             </template>
          </el-table-column>
          <el-table-column label="Дії" width="150" align="right">
             <template #default="scope">
                <el-button size="small" @click="editSpec(scope.row)">Відкрити</el-button>
                <el-button size="small" type="danger" link @click="deleteSpec(scope.row.id)" :icon="Delete" />
             </template>
          </el-table-column>
          <template #empty>
             <el-empty description="Жодної специфікації не знайдено" />
          </template>
       </el-table>
    </div>

    <!-- EDITOR VIEW -->
    <div v-else class="spec-editor">
       <div class="tab-header">
          <div class="header-left">
             <el-button :icon="ArrowLeft" circle @click="editingSpec = null" class="back-btn" />
             <h3>{{ specForm.id ? 'Редагування специфікації' : 'Нова специфікація' }}</h3>
          </div>
          <div class="header-actions">
             <el-button @click="editingSpec = null">Скасувати</el-button>
             <el-button type="primary" :loading="saving" @click="saveSpecification">Зберегти</el-button>
          </div>
       </div>
       
       <el-card shadow="never" class="mt-4">
          <el-form :model="specForm" label-position="top">
             <el-row :gutter="24">
                <el-col :span="12">
                   <el-form-item label="Назва специфікації (Напр. Стандартна)">
                      <el-input v-model="specForm.name" />
                   </el-form-item>
                </el-col>
                <el-col :span="12">
                   <el-form-item label="Статуси">
                      <div class="flex gap-4">
                         <el-checkbox v-model="specForm.is_default" border>Основна рецептура</el-checkbox>
                         <el-checkbox v-model="specForm.is_active" border>Активна</el-checkbox>
                      </div>
                   </el-form-item>
                </el-col>
             </el-row>
             <el-form-item label="Внутрішні нотатки">
                <el-input v-model="specForm.notes" type="textarea" :rows="2" />
             </el-form-item>
          </el-form>
       </el-card>

       <el-card shadow="never" class="mt-4 pb-4">
          <div class="flex justify-between items-center mb-4">
             <h4 class="m-0">Компоненти (Матеріали)</h4>
             <el-button type="success" size="small" @click="addItem" plain :icon="Plus">Додати рядок</el-button>
          </div>
          
          <el-table :data="specForm.items" stripe style="width: 100%" class="component-table">
             <el-table-column label="Товар / Матеріал" min-width="300">
                <template #default="scope">
                   <el-select
                      v-model="scope.row.component_id"
                      filterable
                      remote
                      reserve-keyword
                      placeholder="Пошук номенклатури..."
                      :remote-method="searchProducts"
                      :loading="searchingProducts"
                      class="w-full"
                   >
                      <el-option
                         v-for="p in productSearchResults"
                         :key="p.id"
                         :label="p.name"
                         :value="p.id"
                      >
                         <div class="flex justify-between w-full">
                            <span>{{ p.name }}</span>
                            <span class="text-gray-400 text-xs">{{ p.sku }}</span>
                         </div>
                      </el-option>
                   </el-select>
                </template>
             </el-table-column>
             
             <el-table-column label="Кількість / Розрахунок" width="200">
                <template #default="scope">
                   <div class="flex items-center gap-2">
                     <el-input-number v-model="scope.row.quantity" :min="0.0001" :step="1" :precision="3" style="flex: 1" :disabled="scope.row.calc_type && scope.row.calc_type !== 'fixed'" />
                     <el-tooltip :content="scope.row.calc_type && scope.row.calc_type !== 'fixed' ? 'Параметричний розрахунок увімкнено' : 'Налаштувати смарт-розрахунок'" placement="top">
                       <el-button :type="scope.row.calc_type && scope.row.calc_type !== 'fixed' ? 'success' : 'default'" :icon="Setting" circle @click="openCalcDialog(scope.row)" />
                     </el-tooltip>
                   </div>
                </template>
             </el-table-column>
             
             <el-table-column label="Од. вим." width="120">
                <template #default="scope">
                   <el-input v-model="scope.row.unit_of_measure" placeholder="шт/кг" />
                </template>
             </el-table-column>
             
             <el-table-column label="Дії" width="60" align="center">
                <template #default="scope">
                   <el-button link type="danger" :icon="Delete" @click="removeItem(scope.$index)" />
                </template>
             </el-table-column>
          </el-table>
       </el-card>

    </div>

    <!-- Calculator Config Dialog -->
    <el-dialog v-model="calcDialogOpen" title="Налаштування розумного розрахунку" width="600px">
      <div v-if="activeCalcItem" class="p-2">
        <el-form label-position="top">
            <el-form-item label="Тип калькулятора">
              <el-select v-model="activeCalcItem.calc_type" class="w-full" @change="handleTypeChange(activeCalcItem)">
                <el-option label="Фіксована кількість" value="fixed" />
                <el-option label="Таблиця (Інтерполяція)" value="interpolation" />
                <el-option label="Площа (W * H)" value="area" />
                <el-option label="Об'єм (W * H * L)" value="volume" />
                <el-option label="Своя формула" value="formula" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Вимір для таблиці" v-if="activeCalcItem.calc_type === 'interpolation'">
              <el-select v-model="activeCalcItem.calc_dimension" class="w-full">
                <el-option label="Висота (H)" value="height_cm" />
                <el-option label="Ширина (W)" value="width_cm" />
                <el-option label="Довжина (L)" value="length_cm" />
              </el-select>
            </el-form-item>

            <el-form-item label="Коефіцієнт відходів (%)">
              <el-input-number v-model="activeCalcItem.calc_waste_factor" :precision="2" :step="0.01" :min="0" :max="1" style="width: 100%" />
            </el-form-item>

            <div v-if="activeCalcItem.calc_type === 'interpolation'" class="mt-4">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-semibold">Точки розрахунку (Розмір -> Кількість)</span>
                    <el-button type="primary" size="small" @click="addPoint(activeCalcItem)" plain >Додати точку</el-button>
                </div>
                <el-table :data="activeCalcItem.calc_data_points" size="small" border>
                    <el-table-column label="Значення виміру (см)">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.input" size="small" style="width: 100%" />
                        </template>
                    </el-table-column>
                    <el-table-column :label="`Потрібна кількість (${activeCalcItem.unit_of_measure || 'шт'})`">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.output" :precision="4" size="small" style="width: 100%" />
                        </template>
                    </el-table-column>
                    <el-table-column width="60" align="center">
                        <template #default="scope">
                            <el-button type="danger" link @click="removePoint(activeCalcItem, scope.$index)" :icon="Delete" />
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <el-form-item label="JS Формула (змінні: W, H, L)" v-if="activeCalcItem.calc_type === 'formula'" class="mt-4">
              <el-input v-model="activeCalcItem.calc_formula" placeholder="(W * H) / 10000" />
            </el-form-item>
            
            <div v-if="['area', 'volume'].includes(activeCalcItem.calc_type)" class="mt-2 p-3 bg-blue-50 text-blue-700 text-sm rounded">
                Автоматичний розрахунок матеріалу на основі фізичних розмірів товару.
                Якщо у товару зміниться ширина чи висота — система автоматично перерахує кількість цього матеріалу при плануванні виробництва.
            </div>
            
            <div v-if="activeCalcItem.calc_type !== 'fixed'" class="mt-4">
                <el-alert title="Увага" type="info" :closable="false" show-icon>
                  Параметричний розрахунок ігнорує поле "Кількість" в таблиці. Його буде розраховано динамічно.
                </el-alert>
            </div>
            
            <!-- Preview Block -->
            <div v-if="activeCalcItem.calc_type !== 'fixed'" style="margin-top: 16px; padding: 16px; border-radius: 8px; background-color: #eff6ff; border: 1px solid #bfdbfe; display: flex; align-items: center; justify-content: space-between;">
              <div>
                <div style="font-size: 14px; font-weight: 600; color: #1e3a8a; margin-bottom: 4px;">Поточний результат розрахунку:</div>
                <div style="font-size: 12px; color: #1d4ed8;">Для розрахунку використані поточні габарити цього товару (Ш: {{ productDimensions.width_cm || 0 }}см, В: {{ productDimensions.height_cm || 0 }}см, Д: {{ productDimensions.length_cm || 0 }}см)</div>
              </div>
              <div style="font-size: 20px; font-weight: 700; color: #2563eb; text-align: right;">
                {{ calculateQuantity(activeCalcItem) }} 
                <span style="font-size: 14px; font-weight: 400; color: #64748b; margin-left: 4px;">{{ activeCalcItem.unit_of_measure || 'шт' }}</span>
              </div>
            </div>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="calcDialogOpen = false">Готово</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Delete, ArrowLeft, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getProductSpecifications,
    createProductSpecification,
    updateProductSpecification,
    deleteProductSpecification
} from '@/api/specifications'
import api from '@/api'

const props = defineProps({
    productId: {
        type: String,
        required: true
    },
    productDimensions: {
        type: Object,
        required: true
    }
})

const loading = ref(false)
const saving = ref(false)
const specifications = ref([])

const editingSpec = ref(null)
const specForm = ref({
    name: '',
    is_active: true,
    is_default: true,
    notes: '',
    items: []
})

const searchingProducts = ref(false)
const productSearchResults = ref([])

// Calculator UI state
const calcDialogOpen = ref(false)
const activeCalcItem = ref(null)

// Load all specifications for this product
const loadSpecifications = async () => {
    if (!props.productId) return
    loading.value = true
    try {
        specifications.value = await getProductSpecifications(props.productId)
    } catch (e) {
        ElMessage.error('Помилка завантаження специфікацій')
    } finally {
        loading.value = false
    }
}

// Open create form
const createNewSpec = () => {
    specForm.value = {
        name: 'Нова специфікація',
        is_active: true,
        is_default: specifications.value.length === 0,
        notes: '',
        items: []
    }
    editingSpec.value = 'new'
}

// Open edit form
const editSpec = (row) => {
    // Deep copy to avoid modifying original until saved
    specForm.value = JSON.parse(JSON.stringify(row))
    editingSpec.value = row.id
    
    // We need to preload the selected products so the <el-select> has labels
    if (specForm.value.items && specForm.value.items.length > 0) {
        // Collect pre-loaded components from backend response
        const preloads = specForm.value.items
           .filter(i => i.component)
           .map(i => i.component)
           
        // Merge with existing results to ensure labels show up immediately
        const newResults = [...productSearchResults.value, ...preloads]
        
        // Remove duplicates by ID
        const uniqueResults = []
        const map = new Map()
        for (const item of newResults) {
            if(!map.has(item.id)){
                map.set(item.id, true)
                uniqueResults.push(item)
            }
        }
        productSearchResults.value = uniqueResults
    }
}

// Save logic
const saveSpecification = async () => {
    if (!specForm.value.name) {
        ElMessage.warning('Вкажіть назву специфікації')
        return
    }
    
    // Validate items
    const validItems = specForm.value.items.filter(i => i.component_id && i.quantity > 0)
    specForm.value.items = validItems

    saving.value = true
    try {
        if (specForm.value.id) {
            await updateProductSpecification(specForm.value.id, specForm.value)
            ElMessage.success('Специфікацію оновлено')
        } else {
            await createProductSpecification(props.productId, specForm.value)
            ElMessage.success('Специфікацію створено')
        }
        editingSpec.value = null
        await loadSpecifications()
    } catch (e) {
        ElMessage.error(e.response?.data?.detail || 'Помилка збереження')
    } finally {
        saving.value = false
    }
}

// Delete logic
const deleteSpec = async (id) => {
    try {
        await ElMessageBox.confirm('Видалити цю специфікацію?', 'Увага', { type: 'warning' })
        await deleteProductSpecification(id)
        ElMessage.success('Видалено')
        await loadSpecifications()
    } catch (e) {
        if (e !== 'cancel') {
             ElMessage.error('Помилка видалення')
        }
    }
}

// Add Item Row
const addItem = () => {
    specForm.value.items.push({
        component_id: null,
        quantity: 1,
        unit_of_measure: 'шт',
        notes: '',
        is_calculated: false,
        calc_dimension: null,
        calc_data_points: [],
        calc_formula: '',
        calc_waste_factor: 0
    })
}

const removeItem = (index) => {
    specForm.value.items.splice(index, 1)
}

// Calculator Logic
const openCalcDialog = (item) => {
    // Ensure all calculator fields exist on the item
    if (!item.calc_type) item.calc_type = 'fixed'
    if (!item.calc_data_points) item.calc_data_points = []
    
    activeCalcItem.value = item
    calcDialogOpen.value = true
}

const handleTypeChange = (item) => {
    item.is_calculated = item.calc_type !== 'fixed'
    if (item.calc_type === 'interpolation' && item.calc_data_points.length === 0) {
        item.calc_dimension = 'width_cm'
    }
}

const addPoint = (item) => {
    if (!item.calc_data_points) item.calc_data_points = []
    item.calc_data_points.push({ input: 0, output: 0 })
}

const removePoint = (item, index) => {
    item.calc_data_points.splice(index, 1)
}

const calculateQuantity = (item) => {
    if (!item || item.calc_type === 'fixed') return item?.quantity || 0

    const dimensions = {
        W: parseFloat(props.productDimensions.width_cm) || 0,
        H: parseFloat(props.productDimensions.height_cm) || 0,
        L: parseFloat(props.productDimensions.length_cm) || 0,
        Kg: parseFloat(props.productDimensions.weight_kg) || 0
    }

    let result = 0

    if (item.calc_type === 'interpolation') {
        if (!item.calc_data_points || item.calc_data_points.length === 0) return item.quantity
        
        const dimVal = parseFloat(props.productDimensions[item.calc_dimension]) || 0
        const points = [...item.calc_data_points].sort((a, b) => a.input - b.input)
        
        if (dimVal <= points[0].input) result = points[0].output
        else if (dimVal >= points[points.length - 1].input) result = points[points.length - 1].output
        else {
            for (let i = 0; i < points.length - 1; i++) {
                const p1 = points[i]; const p2 = points[i+1]
                if (dimVal >= p1.input && dimVal <= p2.input) {
                    const ratio = (dimVal - p1.input) / (p2.input - p1.input)
                    result = p1.output + ratio * (p2.output - p1.output)
                    break
                }
            }
        }
    } 
    else if (item.calc_type === 'area') {
        result = dimensions.W * dimensions.H / 10000 
    }
    else if (item.calc_type === 'volume') {
        result = dimensions.W * dimensions.H * dimensions.L / 1000000 
    }
    else if (item.calc_type === 'formula') {
        try {
            const { W, H, L, Kg } = dimensions
            result = eval(item.calc_formula || '0')
        } catch (e) {
            return 'Помилка'
        }
    }

    if (item.calc_waste_factor) {
        result *= (1 + parseFloat(item.calc_waste_factor))
    }
    
    return typeof result === 'number' ? result.toFixed(4) : result
}

// Product Search for components
const searchProducts = async (query) => {
    searchingProducts.value = true
    try {
        // Fetch all products or search by term
        // Ideally we exclude the parent product to prevent circular dependencies
        const params = query ? { search: query } : {}
        const res = await api.get('/api/v1/products', { params })
        
        // Exclude self
        productSearchResults.value = res.data.filter(p => p.id !== props.productId)
    } catch (e) {
        console.error('Failed to search products', e)
    } finally {
        searchingProducts.value = false
    }
}

onMounted(() => {
    loadSpecifications()
    searchProducts('') // Preload some products for the dropdown
})
</script>

<style scoped>
.specification-tab-container {
    padding: 10px 24px 24px 24px;
}

.tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.tab-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.flex {
    display: flex;
}
.gap-4 {
    gap: 1rem;
}
.justify-between {
    justify-content: space-between;
}
.items-center {
    align-items: center;
}
.mb-4 {
    margin-bottom: 1rem;
}
.m-0 { margin: 0; }
.mt-4 { margin-top: 1rem; }
.pb-4 { padding-bottom: 1rem; }
.w-full { width: 100%; }
.text-gray-400 { color: #9ca3af; }
.text-xs { font-size: 0.75rem; }

.component-table {
    border-top: 1px solid #ebeef5;
}
</style>
