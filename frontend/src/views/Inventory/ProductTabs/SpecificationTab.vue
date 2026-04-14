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
       <div class="editor-header">
        <div class="left-actions">
           <el-button @click="editingSpec = null" class="btn-back">
             <el-icon><Back /></el-icon> До списку
           </el-button>
        </div>
        <div class="right-actions">
           <el-button type="info" plain @click="openPreviewDialog" :disabled="!specForm.id">
             <el-icon><Monitor /></el-icon> Перевірити розрахунок
           </el-button>
           <el-button type="primary" :loading="saving" @click="saveSpecification" class="btn-save">
             <el-icon><Check /></el-icon> Зберегти специфікацію
           </el-button>
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
                   <el-input v-model="scope.row.unit_of_measure" placeholder="шт/кг" disabled />
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

    <!-- Test Calculation Preview Dialog -->
    <el-dialog v-model="previewVisible" title="Перевірка розрахунку матеріалів" width="800px">
      <div v-loading="previewLoading">
        <el-form label-position="top">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="Висота (H), см">
                <el-input-number v-model="testDims.height_cm" class="w-full" :controls="false" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Ширина (W), см">
                <el-input-number v-model="testDims.width_cm" class="w-full" :controls="false" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Глибина (L), см">
                <el-input-number v-model="testDims.length_cm" class="w-full" :controls="false" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Вага, кг">
                <el-input-number v-model="testDims.weight_kg" class="w-full" :controls="false" />
              </el-form-item>
            </el-col>
          </el-row>

          <div v-if="testAttributes.length > 0" class="mt-2 mb-4 p-3 bg-gray-50 rounded border border-gray-200">
            <h5 class="m-0 mb-3 text-gray-700">Атрибути з формул:</h5>
            <el-row :gutter="20">
              <el-col :span="8" v-for="attr in testAttributes" :key="attr">
                <el-form-item :label="attr">
                  <el-input-number v-model="testDims.custom_attributes[attr]" class="w-full" :controls="false" :precision="2" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          <div class="flex justify-end mt-2 mb-4">
            <el-button type="primary" @click="runPreviewCalculation">Розрахувати заново</el-button>
          </div>
        </el-form>

        <el-table :data="previewResults" border stripe>
          <el-table-column prop="component_name" label="Матеріал" />
          <el-table-column prop="quantity" label="Розрахована к-ть" width="150" align="right">
            <template #default="scope">
              <span class="font-bold text-indigo-600">{{ scope.row.quantity }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="unit_of_measure" label="Од. вим." width="100" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">Закрити</el-button>
      </template>
    </el-dialog>

    <!-- Calculator Config Dialog -->
    <el-dialog v-model="calcDialogOpen" :width="null" style="width: 95vw; max-width: 1700px;" class="smart-calc-dialog" top="5vh">
      <template #header>
        <div class="flex items-center gap-2">
            <span class="text-lg font-bold">Налаштування розумного розрахунку [v1.3-WIDE]</span>
            <el-tag type="success" size="small" effect="dark" class="ml-2">Оновлено</el-tag>
        </div>
      </template>
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
                <!-- Three separate dimension sub-tables in a grid -->
                <div class="dim-grid">
                <div v-for="dim in interpDims" :key="dim.key" :class="['dim-section', `dim-${dim.key}`]">
                    <div class="dim-header-box">
                        <div class="dim-title-group">
                            <span class="dim-icon">{{ dim.key.toUpperCase() }}</span>
                            <span class="dim-title">{{ dim.label }}</span>
                        </div>
                        <el-button type="primary" size="small" @click="addPoint(activeCalcItem, dim.key)" :icon="Plus" circle />
                    </div>
                    
                    <div class="table-container">
                        <el-table :data="getPoints(activeCalcItem, dim.key)" size="small" border class="compact-table">
                            <el-table-column :label="dim.label + ' (см)'">
                                <template #default="scope">
                                    <el-input-number v-model="scope.row.x" size="small" style="width:100%" :controls="false" />
                                </template>
                            </el-table-column>
                            <el-table-column :label="'К-сть (' + (activeCalcItem.unit_of_measure || 'шт') + ')'">
                                <template #default="scope">
                                    <el-input-number v-model="scope.row.qty" :precision="4" size="small" style="width:100%" :controls="false" />
                                </template>
                            </el-table-column>
                            <el-table-column width="40" align="center">
                                <template #default="scope">
                                    <el-button type="danger" link @click="removePoint(activeCalcItem, dim.key, scope.$index)" :icon="Delete" />
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>

                    <div class="dim-footer">
                        <div class="config-grid">
                            <div class="config-item">
                                <label>Стандарт (см)</label>
                                <el-input-number v-model="getDimConfig(activeCalcItem, dim.key).default" :precision="0" :min="0" size="small" :controls="false" placeholder="0" />
                            </div>
                            <div class="config-item wide">
                                <label>Читати з характеристики</label>
                                <el-select
                                    v-model="getDimConfig(activeCalcItem, dim.key).char_name"
                                    size="small"
                                    placeholder="Виберіть..."
                                    clearable
                                    filterable
                                >
                                    <el-option
                                        v-for="attr in productAttributes"
                                        :key="attr.id"
                                        :label="attr.name"
                                        :value="attr.name"
                                    />
                                </el-select>
                            </div>
                        </div>

                        <div v-if="calcStepInfo && calcStepInfo[dim.key] !== null" class="step-badge">
                            <span class="step-label">📐 Крок:</span>
                            <span class="step-value">{{ calcStepInfo[dim.key] > 0 ? '+' : '' }}{{ calcStepInfo[dim.key] }}</span>
                            <span class="step-unit">{{ activeCalcItem.unit_of_measure || 'шт' }}/см</span>
                        </div>
                    </div>
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

            <el-form-item label="Своя математична формула" v-if="activeCalcItem.calc_type === 'formula'" class="mt-4">
              <el-input v-model="activeCalcItem.calc_formula" placeholder="(W * H) / 10000 * {Товщина_ДСП}" />
              <div class="mt-2 w-full">
                <span class="text-xs text-gray-500 mb-1 block">Доступні змінні (натисніть щоб додати у формулу):</span>
                <div class="flex flex-wrap gap-2">
                  <el-tag
                    size="small"
                    type="primary"
                    class="cursor-pointer"
                    effect="light"
                    @click="activeCalcItem.calc_formula = (activeCalcItem.calc_formula || '') + 'W'"
                  >W (Ширина)</el-tag>
                  <el-tag
                    size="small"
                    type="primary"
                    class="cursor-pointer"
                    effect="light"
                    @click="activeCalcItem.calc_formula = (activeCalcItem.calc_formula || '') + 'H'"
                  >H (Висота)</el-tag>
                  <el-tag
                    size="small"
                    type="primary"
                    class="cursor-pointer"
                    effect="light"
                    @click="activeCalcItem.calc_formula = (activeCalcItem.calc_formula || '') + 'L'"
                  >L (Глибина)</el-tag>
                  <!-- Динамічні характеристики -->
                  <el-tag
                    v-for="attr in productAttributes" 
                    :key="attr.id"
                    size="small"
                    type="info"
                    class="cursor-pointer"
                    effect="plain"
                    @click="activeCalcItem.calc_formula = (activeCalcItem.calc_formula || '') + '{' + attr.name + '}'"
                    style="cursor: pointer"
                  >
                    {{ '{' + attr.name + '}' }}
                  </el-tag>
                </div>
              </div>
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
import { ref, computed, onMounted, reactive } from 'vue'
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

// All product attributes/characteristics loaded from API
const productAttributes = ref([])
const loadProductAttributes = async () => {
    try {
        const res = await api.get('/api/v1/attributes/')
        productAttributes.value = res.data || []
    } catch (e) {
        // non-critical — silent fail
    }
}

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
// interpDims: list of the three dimension descriptors used in the template
const interpDims = [
    { key: 'h', label: 'Висота (H)' },
    { key: 'w', label: 'Ширина (W)' },
    { key: 'l', label: 'Довжина (L)' },
]

// Helper: safely get the points array for a given dimension key
const getPoints = (item, key) => {
    if (!item?.calc_data_points || Array.isArray(item.calc_data_points)) return []
    return item.calc_data_points[key] || []
}

// Helper: safely get or init the dim config for a given dimension key
const getDimConfig = (item, key) => {
    if (!item.calc_dim_config) item.calc_dim_config = { h: { char_name: '', default: 0 }, w: { char_name: '', default: 0 }, l: { char_name: '', default: 0 } }
    if (!item.calc_dim_config[key]) item.calc_dim_config[key] = { char_name: '', default: 0 }
    return item.calc_dim_config[key]
}

// calcStepInfo: per-dimension step values based on first 2 points of each series
const calcStepInfo = computed(() => {
    if (!activeCalcItem.value || activeCalcItem.value.calc_type !== 'interpolation') return null
    const dp = activeCalcItem.value.calc_data_points
    if (!dp || Array.isArray(dp)) return null
    const info = {}
    let hasAny = false
    for (const key of ['h', 'w', 'l']) {
        const arr = dp[key] || []
        if (arr.length >= 2) {
            const s = [...arr].sort((a, b) => (a.x || 0) - (b.x || 0))
            const xDiff = (s[1].x || 0) - (s[0].x || 0)
            if (xDiff !== 0) {
                info[key] = parseFloat(((s[1].qty - s[0].qty) / xDiff).toFixed(4))
                hasAny = true
            } else { info[key] = null }
        } else { info[key] = null }
    }
    return hasAny ? info : null
})

// Load all specifications for this product
const loadSpecifications = async () => {
    if (!props.productId) return
    loading.value = true
    try {
        const resData = await getProductSpecifications(props.productId)
        
        // Data sanitization: backend might return floats as strings (e.g., "1.000").
        // ElInputNumber requires strict Numbers.
        resData.forEach(spec => {
            if (spec.items) {
                spec.items.forEach(item => {
                    if (typeof item.quantity === 'string') item.quantity = parseFloat(item.quantity) || 0
                    if (item.calc_data_points) {
                        for (const key of ['h', 'w', 'l']) {
                            if (Array.isArray(item.calc_data_points[key])) {
                                item.calc_data_points[key].forEach(p => {
                                    if (typeof p.x === 'string') p.x = parseFloat(p.x) || 0
                                    if (typeof p.qty === 'string') p.qty = parseFloat(p.qty) || 0
                                })
                            }
                        }
                    }
                })
            }
        })
        
        specifications.value = resData
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
        calc_data_points: { h: [], w: [], l: [] },
        calc_dim_config: { h: { char_name: '', default: 0 }, w: { char_name: '', default: 0 }, l: { char_name: '', default: 0 } },
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

    // Initialize or migrate to new per-dim format: { h: [{x,qty}], w: [{x,qty}], l: [{x,qty}] }
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) {
        const oldFlat = Array.isArray(item.calc_data_points) ? item.calc_data_points : []
        const newDp = { h: [], w: [], l: [] }
        for (const pt of oldFlat) {
            if (pt.h != null) newDp.h.push({ x: pt.size_cm || 0, qty: pt.h })
            if (pt.w != null) newDp.w.push({ x: pt.size_cm || 0, qty: pt.w })
            if (pt.l != null) newDp.l.push({ x: pt.size_cm || 0, qty: pt.l })
        }
        item.calc_data_points = newDp
    } else if (!item.calc_data_points.h) {
        const old = item.calc_data_points
        item.calc_data_points = {
            h: (old.height_cm || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
            w: (old.width_cm  || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
            l: (old.length_cm || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
        }
    }

    // Ensure calc_dim_config exists
    if (!item.calc_dim_config) {
        item.calc_dim_config = {
            h: { char_name: '', default: 0 },
            w: { char_name: '', default: 0 },
            l: { char_name: '', default: 0 }
        }
    }

    activeCalcItem.value = item
    calcDialogOpen.value = true
}

const handleTypeChange = (item) => {
    item.is_calculated = item.calc_type !== 'fixed'
}

const addPoint = (item, dimKey) => {
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) item.calc_data_points = { h: [], w: [], l: [] }
    if (!item.calc_data_points[dimKey]) item.calc_data_points[dimKey] = []
    item.calc_data_points[dimKey].push({ x: 0, qty: 0 })
}

const removePoint = (item, dimKey, index) => {
    item.calc_data_points[dimKey].splice(index, 1)
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
        const dp = item.calc_data_points
        if (!dp || Array.isArray(dp)) return item.quantity

        const dimMap = { h: 'height_cm', w: 'width_cm', l: 'length_cm' }
        let total = 0
        let hasAnyPoints = false

        for (const [key, dimKey] of Object.entries(dimMap)) {
            const pts = (dp[key] || []).filter(p => p.qty != null)
            if (pts.length === 0) continue
            hasAnyPoints = true
            const dimVal = parseFloat(props.productDimensions[dimKey]) || 0
            const sorted = [...pts].sort((a, b) => (a.x || 0) - (b.x || 0))
            let dimResult = 0
            const interp = (p1, p2, val) => {
                const slope = (p2.x !== p1.x) ? (p2.qty - p1.qty) / (p2.x - p1.x) : 0
                return p1.qty + slope * (val - p1.x)
            }
            if (sorted.length === 1) { dimResult = sorted[0].qty }
            else if (dimVal <= sorted[0].x) { dimResult = interp(sorted[0], sorted[1], dimVal) }
            else if (dimVal >= sorted[sorted.length - 1].x) { dimResult = interp(sorted[sorted.length - 2], sorted[sorted.length - 1], dimVal) }
            else {
                for (let i = 0; i < sorted.length - 1; i++) {
                    if (dimVal >= sorted[i].x && dimVal <= sorted[i + 1].x) {
                        dimResult = interp(sorted[i], sorted[i + 1], dimVal); break
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

// Preview calculation logic
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewResults = ref([])
const testDims = reactive({
    height_cm: props.productDimensions?.height_cm || 0,
    width_cm: props.productDimensions?.width_cm || 0,
    length_cm: props.productDimensions?.length_cm || 0,
    weight_kg: props.productDimensions?.weight_kg || 0,
    custom_attributes: {}
})

const testAttributes = computed(() => {
    const keys = new Set()
    if (specForm.value && specForm.value.items) {
        specForm.value.items.forEach(item => {
            if (item.calc_type === 'formula' && item.calc_formula) {
                // Find all {attribute_name}
                const regex = /{([^}]+)}/g
                let match;
                while ((match = regex.exec(item.calc_formula)) !== null) {
                    keys.add(match[1])
                    // Initialize if not present
                    if (!(match[1] in testDims.custom_attributes)) {
                        testDims.custom_attributes[match[1]] = 0
                    }
                }
            }
        })
    }
    return Array.from(keys)
})

const openPreviewDialog = () => {
    if (!specForm.value.id) return
    previewVisible.value = true
    runPreviewCalculation()
}

const runPreviewCalculation = async () => {
    previewLoading.value = true
    try {
        const res = await api.post(`/api/v1/products/specifications/${specForm.value.id}/calculate`, testDims)
        previewResults.value = res.data
    } catch (e) {
        ElMessage.error('Помилка розрахунку на сервері')
    } finally {
        previewLoading.value = false
    }
}

onMounted(() => {
    loadSpecifications()
    loadProductAttributes()
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

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.editor-header .left-actions,
.editor-header .right-actions {
    display: flex;
    align-items: center;
    gap: 12px;
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

.dim-section {
    margin-bottom: 0;
    padding: 0;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #fff;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
}

.dim-section:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.dim-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 8px;
    padding-bottom: 12px;
}

.dim-header-box {
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f1f5f9;
}

.dim-title-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.dim-icon {
    width: 24px;
    height: 24px;
    background: #e2e8f0;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 900;
    color: #475569;
}

.dim-title {
    font-size: 14px;
    font-weight: 700;
    color: #334155;
}

/* Color accents */
.dim-h .dim-icon { background: #dbeafe; color: #1d4ed8; }
.dim-h .dim-title { color: #1e40af; }
.dim-h .dim-header-box { background: #f0f7ff; }

.dim-w .dim-icon { background: #e0e7ff; color: #4338ca; }
.dim-w .dim-title { color: #3730a3; }
.dim-w .dim-header-box { background: #f5f7ff; }

.dim-l .dim-icon { background: #d1fae5; color: #047857; }
.dim-l .dim-title { color: #065f46; }
.dim-l .dim-header-box { background: #f0fdf4; }

.table-container {
    padding: 10px;
    flex: 1;
}

.compact-table :deep(.el-table__header th) {
    background-color: #f8fafc;
    color: #64748b;
    font-size: 11px;
    padding: 4px 0;
}

.dim-footer {
    padding: 12px;
    background: #f8fafc;
    border-top: 1px solid #f1f5f9;
}

.config-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 10px;
}

.config-item.wide {
    grid-column: 1 / -1;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.config-item label {
    font-size: 11px;
    font-weight: 500;
    color: #64748b;
}

.step-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    background: #fff;
    border: 1px solid #e2e8f0;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
}

.step-label { color: #94a3b8; }
.step-value { font-weight: 800; color: #0f172a; }
.step-unit { color: #64748b; font-size: 11px; }

.smart-calc-dialog :deep(.el-dialog__body) {
    padding-top: 10px;
}
</style>
