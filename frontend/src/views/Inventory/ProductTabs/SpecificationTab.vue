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
                      @change="(val) => handleComponentSelect(scope.row, val)"
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
                     <el-input-number v-model="scope.row.quantity" :min="0" :step="1" :precision="3" style="flex: 1" :disabled="scope.row.calc_type && scope.row.calc_type !== 'fixed'" />
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
                <el-option label="Таблиця (Точки / Авто-пропорція)" value="interpolation" />
                <el-option label="Пропорція (від розміру)" value="proportional" />
                <el-option label="Площа (W * H)" value="area" />
                <el-option label="Об'єм (W * H * L)" value="volume" />
                <el-option label="Своя формула" value="formula" />
              </el-select>
            </el-form-item>
            


            <div v-if="activeCalcItem.calc_type === 'interpolation'" class="mt-4">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-semibold">Точки розрахунку — вкажіть розмір і кількість матеріалу для кожного виміру</span>
                    <el-button type="primary" size="small" @click="addPoint(activeCalcItem)" plain>Додати точку</el-button>
                </div>
                <el-table :data="activeCalcItem.calc_data_points || []" size="small" border>
                    <el-table-column label="Розмір (см)" width="110">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.size_cm" size="small" style="width: 100%" :controls="false" />
                        </template>
                    </el-table-column>
                    <el-table-column label="Висота H">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.h" :precision="4" size="small" style="width: 100%" :controls="false" placeholder="–" />
                        </template>
                    </el-table-column>
                    <el-table-column label="Ширина W">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.w" :precision="4" size="small" style="width: 100%" :controls="false" placeholder="–" />
                        </template>
                    </el-table-column>
                    <el-table-column label="Довжина L">
                        <template #default="scope">
                            <el-input-number v-model="scope.row.l" :precision="4" size="small" style="width: 100%" :controls="false" placeholder="–" />
                        </template>
                    </el-table-column>
                    <el-table-column width="50" align="center">
                        <template #default="scope">
                            <el-button type="danger" link @click="removePoint(activeCalcItem, scope.$index)" :icon="Delete" />
                        </template>
                    </el-table-column>
                </el-table>

                <!-- Calculated step info panel -->
                <div v-if="calcStepInfo" class="mt-3 p-3 rounded" style="background:#eff6ff;border:1px solid #bfdbfe">
                    <div style="font-size:12px;font-weight:600;color:#1e40af;margin-bottom:4px">📐 Система вивчила крок на 1 см:</div>
                    <div style="font-size:13px;color:#1d4ed8;display:flex;gap:16px;flex-wrap:wrap">
                        <span v-if="calcStepInfo.h !== null">Висота: <b>{{ calcStepInfo.h > 0 ? '+' : '' }}{{ calcStepInfo.h }} {{ activeCalcItem.unit_of_measure || 'шт' }}/см</b></span>
                        <span v-if="calcStepInfo.w !== null">Ширина: <b>{{ calcStepInfo.w > 0 ? '+' : '' }}{{ calcStepInfo.w }} {{ activeCalcItem.unit_of_measure || 'шт' }}/см</b></span>
                        <span v-if="calcStepInfo.l !== null">Довжина: <b>{{ calcStepInfo.l > 0 ? '+' : '' }}{{ calcStepInfo.l }} {{ activeCalcItem.unit_of_measure || 'шт' }}/см</b></span>
                    </div>
                </div>
            </div>

            <el-form-item label="Вимір для розрахунку" v-if="activeCalcItem.calc_type === 'proportional'" class="mt-4">
              <el-select v-model="activeCalcItem.calc_dimension" class="w-full">
                <el-option label="Висота (H)" value="height_cm" />
                <el-option label="Ширина (W)" value="width_cm" />
                <el-option label="Довжина (L)" value="length_cm" />
              </el-select>
            </el-form-item>

            <el-form-item label="Коефіцієнт (Множник)" v-if="activeCalcItem.calc_type === 'proportional'" class="mt-4">
              <el-input v-model="activeCalcItem.calc_formula" type="number" step="0.0001" placeholder="напр. 0.1" />
              <div class="text-xs text-gray-400 mt-1" style="line-height: 1.2;">К-сть = Вимір × Коефіцієнт</div>
            </el-form-item>

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
import { ref, computed, onMounted } from 'vue'
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
// calcStepInfo: shows the inferred per-cm step from the first two interpolation points
const calcStepInfo = computed(() => {
    if (!activeCalcItem.value || activeCalcItem.value.calc_type !== 'interpolation') return null
    const points = activeCalcItem.value.calc_data_points
    if (!Array.isArray(points) || points.length < 2) return null
    const sorted = [...points].sort((a, b) => (a.size_cm || 0) - (b.size_cm || 0))
    const p1 = sorted[0], p2 = sorted[1]
    const sizeDiff = (p2.size_cm || 0) - (p1.size_cm || 0)
    if (sizeDiff === 0) return null
    const info = {}
    let hasAny = false
    for (const key of ['h', 'w', 'l']) {
        if (p1[key] != null && p2[key] != null) {
            info[key] = parseFloat(((p2[key] - p1[key]) / sizeDiff).toFixed(4))
            hasAny = true
        } else {
            info[key] = null
        }
    }
    return hasAny ? info : null
})

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
    
    // Validate items: require a component, and either quantity > 0 OR it is a smart-calculated item
    const validItems = specForm.value.items.filter(i => i.component_id && (i.quantity > 0 || (i.calc_type && i.calc_type !== 'fixed')))
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

const addItem = () => {
    specForm.value.items.push({
        component_id: null,
        quantity: 1,
        unit_of_measure: 'шт',
        notes: '',
        is_calculated: false,
        calc_dimension: null,
        calc_data_points: { width_cm: [], height_cm: [], length_cm: [] },
        calc_formula: '',
        calc_waste_factor: 0
    })
}

const removeItem = (index) => {
    specForm.value.items.splice(index, 1)
}

// Calculator Logic
const openCalcDialog = (item) => {
    if (!item.calc_type) item.calc_type = 'fixed'

    // Migrate old format { width_cm: [{input, output}], ... } → new unified [{size_cm, h, w, l}]
    if (!item.calc_data_points) {
        item.calc_data_points = []
    } else if (!Array.isArray(item.calc_data_points)) {
        const old = item.calc_data_points
        const keyMap = { width_cm: 'w', height_cm: 'h', length_cm: 'l' }
        const maxLen = Math.max(
            (old.width_cm || []).length,
            (old.height_cm || []).length,
            (old.length_cm || []).length
        )
        const newPoints = []
        for (let i = 0; i < maxLen; i++) {
            const entry = { size_cm: 0, h: null, w: null, l: null }
            for (const [dimKey, arrKey] of Object.entries(keyMap)) {
                if (old[dimKey] && old[dimKey][i] != null) {
                    if (entry.size_cm === 0) entry.size_cm = old[dimKey][i].input || 0
                    entry[arrKey] = old[dimKey][i].output
                }
            }
            newPoints.push(entry)
        }
        item.calc_data_points = newPoints
    }

    activeCalcItem.value = item
    calcDialogOpen.value = true
}

const handleTypeChange = (item) => {
    item.is_calculated = item.calc_type !== 'fixed'
}

const addPoint = (item) => {
    if (!Array.isArray(item.calc_data_points)) item.calc_data_points = []
    item.calc_data_points.push({ size_cm: 0, h: null, w: null, l: null })
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
        const rawPoints = item.calc_data_points
        if (!Array.isArray(rawPoints) || rawPoints.length === 0) return item.quantity

        const dimMap = { h: 'height_cm', w: 'width_cm', l: 'length_cm' }
        let total = 0
        let hasAnyPoints = false

        for (const [key, dimKey] of Object.entries(dimMap)) {
            const relevant = rawPoints.filter(p => p[key] != null)
            if (relevant.length === 0) continue
            hasAnyPoints = true

            const dimVal = parseFloat(props.productDimensions[dimKey]) || 0
            const pts = [...relevant].sort((a, b) => (a.size_cm || 0) - (b.size_cm || 0))

            let dimResult = 0
            if (pts.length === 1) {
                dimResult = pts[0][key]
            } else {
                const interp = (p1, p2, val) => {
                    const slope = (p2.size_cm !== p1.size_cm) ? (p2[key] - p1[key]) / (p2.size_cm - p1.size_cm) : 0
                    return p1[key] + slope * (val - p1.size_cm)
                }
                if (dimVal <= pts[0].size_cm) {
                    dimResult = interp(pts[0], pts[1], dimVal)
                } else if (dimVal >= pts[pts.length - 1].size_cm) {
                    dimResult = interp(pts[pts.length - 2], pts[pts.length - 1], dimVal)
                } else {
                    for (let i = 0; i < pts.length - 1; i++) {
                        if (dimVal >= pts[i].size_cm && dimVal <= pts[i + 1].size_cm) {
                            dimResult = interp(pts[i], pts[i + 1], dimVal)
                            break
                        }
                    }
                }
            }
            total += Math.max(0, dimResult)
        }

        if (!hasAnyPoints) return item.quantity
        result = total
    }
    else if (item.calc_type === 'proportional') {
        const dimVal = parseFloat(props.productDimensions[item.calc_dimension || 'width_cm']) || 0
        const coeff = parseFloat(item.calc_formula) || 0
        result = dimVal * coeff
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

// Auto-fill unit of measure when component is selected
const handleComponentSelect = (row, componentId) => {
    const selected = productSearchResults.value.find(p => p.id === componentId)
    if (selected && selected.unit_of_measure) {
        row.unit_of_measure = selected.unit_of_measure
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
