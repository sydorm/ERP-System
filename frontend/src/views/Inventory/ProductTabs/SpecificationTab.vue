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
          
          <el-table :key="editingSpec" :data="specForm.items" stripe style="width: 100%" class="component-table">
             <el-table-column label="Товар / Матеріал" min-width="320">
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
             
             <el-table-column label="Кількість / Розрахунок" width="300">
                <template #default="scope">
                    <div class="flex flex-col gap-1">
                      <div class="flex items-center gap-2">
                        <el-input-number 
                          v-model="scope.row.quantity" 
                          :min="0" 
                          :step="1" 
                          :precision="3" 
                          class="qty-input"
                          :disabled="scope.row.calc_type && scope.row.calc_type !== 'fixed'"
                          controls-position="right"
                        />
                        <el-tooltip :content="scope.row.calc_type && scope.row.calc_type !== 'fixed' ? 'Параметричний розрахунок увімкнено' : 'Налаштувати смарт-розрахунок'" placement="top">
                           <div class="flex items-center">
                              <el-button 
                                  :type="hasMapping(scope.row) ? 'success' : (scope.row.calc_type && scope.row.calc_type !== 'fixed' ? 'primary' : 'default')" 
                                  :icon="Setting" 
                                  circle 
                                  size="small"
                                  @click="openCalcDialog(scope.row)" 
                              />
                              <div v-if="hasMapping(scope.row)" class="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-1"></div>
                           </div>
                        </el-tooltip>
                      </div>
                      <div v-if="scope.row.calc_type && scope.row.calc_type !== 'fixed'" class="calc-breakdown text-[10px] text-gray-500 leading-tight">
                         <span class="font-medium text-indigo-600">{{ getBaseQuantity(scope.row).toFixed(3) }}</span> 
                         <span v-if="getTotalWastePercent(scope.row) > 0" class="text-orange-600"> + {{ getTotalWastePercent(scope.row) }}% відходів</span>
                         <span v-if="getTotalWastePercent(scope.row) > 0"> = {{ scope.row.quantity.toFixed(3) }}</span>
                         <span class="ml-1 uppercase">{{ getUomName(scope.row.unit_of_measure) }}</span>
                      </div>
                    </div>
                </template>
             </el-table-column>
             
             <el-table-column label="Од. вим." width="100" align="center">
                <template #default="scope">
                   <div class="uom-badge">
                      {{ getUomName(scope.row.unit_of_measure) }}
                   </div>
                </template>
             </el-table-column>
             
             <el-table-column label="Дії" width="60" align="center">
                <template #default="scope">
                   <el-button link type="danger" :icon="Delete" @click="removeItem(scope.$index)" />
                </template>
             </el-table-column>
          </el-table>
       </el-card>

       <!-- PRODUCTION STAGES BLOCK -->
       <el-card shadow="never" class="mt-4 pb-4">
          <div class="flex justify-between items-center mb-4">
             <h4 class="m-0">Виробничі етапи</h4>
             <el-button type="primary" size="small" @click="addStage" plain :icon="Plus">Додати етап</el-button>
          </div>
          
          <el-table :data="specForm.stages" stripe style="width: 100%" class="stages-table">
             <el-table-column label="Етап" min-width="200">
                <template #default="scope">
                   <el-select v-model="scope.row.stage_id" placeholder="Виберіть етап..." class="w-full" clearable>
                      <el-option v-for="s in productionStages" :key="s.id" :label="s.name" :value="s.id" />
                   </el-select>
                </template>
             </el-table-column>
             
             <el-table-column label="Час (год)" width="150">
                <template #default="scope">
                   <el-input-number v-model="scope.row.duration_hours" :min="0" :step="0.5" :precision="2" class="w-full" />
                </template>
             </el-table-column>
             
             <el-table-column label="Виконавець" min-width="200">
                <template #default="scope">
                    <el-select v-model="scope.row.brigade_id" placeholder="Виберіть виконавця..." class="w-full" clearable>
                       <el-option v-for="p in getFilteredPerformers(scope.row.stage_id)" :key="p.id" :label="p.name" :value="p.id" />
                    </el-select>
                </template>
             </el-table-column>
             
             <el-table-column label="Дії" width="60" align="center">
                <template #default="scope">
                   <el-button link type="danger" :icon="Delete" @click="removeStage(scope.$index)" />
                </template>
             </el-table-column>
          </el-table>
          
          <div v-if="specForm.stages && specForm.stages.length > 0" class="mt-3 text-right text-gray-500 text-sm">
            Загальний час техпроцесу: <span class="font-bold text-indigo-600">{{ totalStagesDuration }} год</span>
          </div>
       </el-card>

    </div>

    <!-- Test Calculation Preview Dialog -->
    <el-dialog v-model="previewVisible" title="Перевірка розрахунку матеріалів" width="800px">
      <div v-loading="previewLoading">
        <el-form label-position="top">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item :label="`Висота (H), ${previewUnit}`">
                <el-input-number v-model="testDimsDisplay.height" class="w-full" @change="(v) => updateTestDim('height_cm', v)" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="`Ширина (W), ${previewUnit}`">
                <el-input-number v-model="testDimsDisplay.width" class="w-full" @change="(v) => updateTestDim('width_cm', v)" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="`Глибина (L), ${previewUnit}`">
                <el-input-number v-model="testDimsDisplay.length" class="w-full" @change="(v) => updateTestDim('length_cm', v)" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Вага, кг">
                <el-input-number v-model="testDims.weight_kg" class="w-full" />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="flex justify-center mb-4">
             <el-radio-group v-model="previewUnit" size="small">
                <el-radio-button label="мм" />
                <el-radio-button label="см" />
             </el-radio-group>
          </div>

          <div v-if="testAttributes.length > 0" class="mt-2 mb-4 p-3 bg-gray-50 rounded border border-gray-200">
            <h5 class="m-0 mb-3 text-gray-700">Атрибути з формул:</h5>
            <el-row :gutter="20">
              <el-col :span="8" v-for="attr in testAttributes" :key="attr">
                <el-form-item :label="attr">
                  <el-input-number v-model="testDims.custom_attributes[attr]" class="w-full" :precision="2" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          <div class="flex justify-end mt-2 mb-4">
            <el-button type="primary" @click="runPreviewCalculation">Розрахувати заново</el-button>
          </div>
        </el-form>

        <el-table :data="previewResults" border stripe>
          <el-table-column prop="component_name" label="Матеріал" min-width="180">
            <template #default="scope">
               <div class="flex flex-col">
                  <span class="font-bold">{{ scope.row.component_name }}</span>
                  <span v-if="scope.row.variant_name" class="text-[10px] text-indigo-600 font-bold uppercase">Варіант: {{ scope.row.variant_name }}</span>
               </div>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="Розрахована к-ть" width="150" align="right">
            <template #default="scope">
              <span class="font-bold text-indigo-600">{{ scope.row.quantity }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Од. вим." width="80">
            <template #default="scope">
              {{ getUomName(scope.row.unit_of_measure) }}
            </template>
          </el-table-column>
          <el-table-column label="Наявність" width="180" align="right">
            <template #default="scope">
               <div class="flex flex-col items-end">
                  <span :class="['text-xs font-bold', scope.row.stock_quantity < scope.row.quantity ? 'text-red-500' : 'text-green-600']">
                     Залишок: {{ scope.row.stock_quantity }}
                  </span>
                  <el-tag v-if="scope.row.stock_quantity < scope.row.quantity" type="danger" size="small" effect="dark" class="mt-1">
                     Недостатньо!
                  </el-tag>
               </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="specForm.stages && specForm.stages.length > 0" class="mt-4 p-4 bg-indigo-50 rounded border border-indigo-100">
           <h5 class="m-0 mb-2 text-indigo-800">Виробничий цикл:</h5>
           <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm">
              <div v-for="stage in specForm.stages" :key="stage.id || stage.sort_order" class="flex items-center gap-1">
                 <el-icon class="text-indigo-400"><Clock /></el-icon>
                 <span class="font-medium">{{ getStageName(stage.stage_id) }}:</span>
                 <span class="text-indigo-600 font-bold">{{ stage.duration_hours }} год</span>
              </div>
              <div class="w-full mt-2 pt-2 border-top border-indigo-200">
                 <strong>Разом робочого часу: <span class="text-lg underline">{{ totalStagesDuration }} год</span></strong>
              </div>
           </div>
        </div>
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
                <el-option label="Характеристики виробу" value="characteristic_mapping" />
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
                        <div class="flex items-center gap-4">
                            <div class="flex items-center gap-1 mr-2 bg-orange-50 px-2 py-1 rounded border border-orange-100">
                                <span class="text-[10px] font-bold text-orange-700 uppercase">Відходи:</span>
                                <el-input-number v-model="getDimConfig(activeCalcItem, dim.key).waste" :min="0" :max="100" size="small" style="width:70px" :controls="false" placeholder="0" />
                                <span class="text-xs text-orange-700">%</span>
                            </div>
                            <el-radio-group v-model="getDimConfig(activeCalcItem, dim.key).unit" size="small" class="unit-toggle">
                                <el-radio-button label="мм" />
                                <el-radio-button label="см" />
                            </el-radio-group>
                            <el-button type="primary" size="small" @click="addPoint(activeCalcItem, dim.key)" :icon="Plus" circle />
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <el-table :data="getPoints(activeCalcItem, dim.key)" size="small" border class="compact-table">
                            <el-table-column :label="dim.label + ' (' + getDimConfig(activeCalcItem, dim.key).unit + ')'">
                                <template #default="scope">
                                    <el-input-number 
                                      :model-value="getDimValue(scope.row.x, getDimConfig(activeCalcItem, dim.key).unit)" 
                                      @update:model-value="(val) => scope.row.x = setDimValue(val, getDimConfig(activeCalcItem, dim.key).unit)"
                                      size="small" 
                                      style="width:100%" 
                                    />
                                </template>
                            </el-table-column>
                            <el-table-column :label="'К-сть (' + (activeCalcItem.unit_of_measure || 'шт') + ')'">
                                <template #default="scope">
                                    <el-input-number v-model="scope.row.qty" :precision="4" size="small" style="width:100%" />
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
                                <label>Стандарт ({{ getDimConfig(activeCalcItem, dim.key).unit }})</label>
                                <el-input-number 
                                    :model-value="getDimValue(getDimConfig(activeCalcItem, dim.key).default, getDimConfig(activeCalcItem, dim.key).unit)"
                                    @update:model-value="(val) => { getDimConfig(activeCalcItem, dim.key).default = setDimValue(val, getDimConfig(activeCalcItem, dim.key).unit) }"
                                    :precision="0" :min="0" size="small" placeholder="0" 
                                />
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
                            <span class="step-unit">{{ activeCalcItem.unit_of_measure || 'шт' }}/{{ getDimConfig(activeCalcItem, dim.key).unit }}</span>
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
                    @click="addVarToFormula('W')"
                  >W (Ширина)</el-tag>
                  <el-tag
                    size="small"
                    type="primary"
                    class="cursor-pointer"
                    effect="light"
                    @click="addVarToFormula('H')"
                  >H (Висота)</el-tag>
                  <el-tag
                    size="small"
                    type="primary"
                    class="cursor-pointer"
                    effect="light"
                    @click="addVarToFormula('L')"
                  >L (Глибина)</el-tag>
                  <el-tag
                    v-for="(attr, idx) in productAttributes" 
                    :key="idx"
                    size="small"
                    class="cursor-pointer"
                    @click="addAttrToFormula(attr.name)"
                  >
                    {{ attr.name }}
                  </el-tag>
                </div>
              </div>
            </el-form-item>
            <!-- Temporarily disabled mapping block -->
            
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
import { Clock, Plus, Delete, ArrowLeft, Setting, Monitor, Back, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getProductSpecifications,
    createProductSpecification,
    updateProductSpecification,
    deleteProductSpecification
} from '@/api/specifications'
import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'

const dictStore = useDictionaryStore()

const uomOptions = ref([])
const productionStages = ref([])
const brigadesList = ref([])
const employeesList = ref([])

onMounted(async () => {
    loading.value = true
    try {
        const results = await Promise.allSettled([
            dictStore.fetchCategory('UOM'),
            dictStore.fetchCategory('PRODUCTION_STAGE'),
            api.get('/api/v1/brigades'),
            api.get('/api/v1/employees')
        ])

        if (results[0].status === 'fulfilled') uomOptions.value = results[0].value;
        if (results[1].status === 'fulfilled') productionStages.value = results[1].value;
        if (results[2].status === 'fulfilled') brigadesList.value = results[2].value.data;
        if (results[3].status === 'fulfilled') employeesList.value = results[3].value.data;
        
        await loadSpecifications()
        await loadProductAttributes()
    } catch (e) {
        console.error('Specification tab init error', e)
    } finally {
        loading.value = false
    }
})

// Helper to filter performers (brigades + employees) by stage
const getFilteredPerformers = (stageId) => {
    const brigades = (brigadesList.value || []).filter(b => !stageId || b.stage_id === stageId || !b.stage_id)
       .map(b => ({ id: b.id, name: `👥 ${b.name}`, type: 'brigade' }))
    const employees = (employeesList.value || []).map(e => ({ id: e.id, name: `👤 ${e.full_name}`, type: 'employee' }))
    return [...brigades, ...employees]
}

const getUomName = (code) => {
    if (!code) return 'шт'
    const opt = uomOptions.value.find(o => o.code === code)
    return opt ? opt.name : code
}

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

// Preview units and display helpers
const previewUnit = ref('см')
const testDimsDisplay = computed(() => {
    const factor = previewUnit.value === 'мм' ? 10 : 1
    return {
        height: (testDims.value.height_cm || 0) * factor,
        width: (testDims.value.width_cm || 0) * factor,
        length: (testDims.value.length_cm || 0) * factor
    }
})

const updateTestDim = (field, val) => {
    const factor = previewUnit.value === 'мм' ? 10 : 1
    testDims.value[field] = val / factor
}

const getDimValue = (valInCm, unit) => {
    const factor = unit === 'мм' ? 10 : 1
    return (valInCm || 0) * factor
}

const setDimValue = (valInUnit, unit) => {
    const factor = unit === 'мм' ? 10 : 1
    return valInUnit / factor
}

const editingSpec = ref(null)
const specForm = ref({
    name: '',
    is_active: true,
    is_default: true,
    notes: '',
    items: [],
    stages: []
})

const getStageName = (id) => {
    const s = productionStages.value.find(x => x.id === id)
    return s ? s.name : 'Unknown'
}

const totalStagesDuration = computed(() => {
    if (!specForm.value.stages) return 0
    return specForm.value.stages.reduce((sum, s) => sum + (parseFloat(s.duration_hours) || 0), 0)
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

const hasMapping = (item) => {
    return item.calc_type === 'characteristic_mapping' && item.characteristic_mappings && item.characteristic_mappings.length > 0
}

const parentAttributes = ref([])
const componentAttributes = ref([])
const loadingMappingAttrs = ref(false)

const loadAttributesForMapping = async (parentId, componentId) => {
    loadingMappingAttrs.value = true
    try {
        const [parentRes, componentRes] = await Promise.all([
            api.get(`/api/v1/products/${parentId}/attributes`),
            api.get(`/api/v1/products/${componentId}/attributes`)
        ])
        parentAttributes.value = parentRes.data || []
        componentAttributes.value = componentRes.data || []
    } catch (e) {
        ElMessage.error('Помилка завантаження атрибутів для мапінгу')
    } finally {
        loadingMappingAttrs.value = false
    }
}

const addMappingLine = () => {
    if (!activeCalcItem.value.characteristic_mappings) {
        activeCalcItem.value.characteristic_mappings = []
    }
    activeCalcItem.value.characteristic_mappings.push({
        component_characteristic_id: null,
        parent_characteristic_id: null
    })
}

const removeMappingLine = (index) => {
    activeCalcItem.value.characteristic_mappings.splice(index, 1)
}

// Helper: safely get the points array for a given dimension key
const getPoints = (item, key) => {
    if (!item?.calc_data_points || Array.isArray(item.calc_data_points)) return []
    return item.calc_data_points[key] || []
}

// Helper: safely get or init the dim config for a given dimension key
const getDimConfig = (item, key) => {
    if (!item.calc_dim_config) item.calc_dim_config = { h: { char_name: '', default: 0, unit: 'см', waste: 0 }, w: { char_name: '', default: 0, unit: 'см', waste: 0 }, l: { char_name: '', default: 0, unit: 'см', waste: 0 } }
    if (!item.calc_dim_config[key]) item.calc_dim_config[key] = { char_name: '', default: 0, unit: 'см', waste: 0 }
    if (!item.calc_dim_config[key].unit) item.calc_dim_config[key].unit = 'см'
    if (item.calc_dim_config[key].waste === undefined) item.calc_dim_config[key].waste = 0
    return item.calc_dim_config[key]
}

const calculateQuantityInternal = (item, includeWaste = true) => {
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
            
            // Apply waste for this dimension
            if (includeWaste && item.calc_dim_config?.[key]?.waste) {
                dimResult *= (1 + parseFloat(item.calc_dim_config[key].waste) / 100)
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
        if (includeWaste && item.calc_waste_factor) {
            result *= (1 + parseFloat(item.calc_waste_factor))
        }
    }
    else if (item.calc_type === 'area') {
        result = dimensions.W * dimensions.H / 10000 
        if (includeWaste && item.calc_waste_factor) {
            result *= (1 + parseFloat(item.calc_waste_factor))
        }
    }
    else if (item.calc_type === 'volume') {
        result = dimensions.W * dimensions.H * dimensions.L / 1000000 
        if (includeWaste && item.calc_waste_factor) {
            result *= (1 + parseFloat(item.calc_waste_factor))
        }
    }
    else if (item.calc_type === 'formula') {
        try {
            const { W, H, L, Kg } = dimensions
            result = eval(item.calc_formula || '0')
            if (includeWaste && item.calc_waste_factor) {
                result *= (1 + parseFloat(item.calc_waste_factor))
            }
        } catch (e) {
            return 'Помилка'
        }
    }

    return result
}

const calculateQuantity = (item) => {
    const result = calculateQuantityInternal(item, true)
    return typeof result === 'number' ? result.toFixed(4) : result
}

const getBaseQuantity = (item) => {
    if (!item || item.calc_type === 'fixed') return item?.quantity || 0
    return calculateQuantityInternal(item, false)
}

const getTotalWastePercent = (item) => {
    if (!item.calc_dim_config) return 0
    const base = calculateQuantityInternal(item, false)
    if (!base || base === 0) return 0
    const withWaste = calculateQuantityInternal(item, true)
    const percent = ((withWaste / base) - 1) * 100
    return percent > 0 ? parseFloat(percent.toFixed(1)) : 0
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
                    // Sync up-to-date unit of measure from component
                    if (item.component?.unit_of_measure) {
                        item.unit_of_measure = item.component.unit_of_measure
                    }

                    // FORCE standard material type to prevent UI hiding fields
                    item.line_type = 'material'

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
        items: [],
        stages: []
    }
    editingSpec.value = 'new'
}

// Open edit form
const editSpec = (row) => {
    // Deep copy to avoid modifying original until saved
    const cleanedRow = JSON.parse(JSON.stringify(row))
    
    // RADICAL SANITIZATION: Force everyone to 'material' and remove the problematic DSP row
    if (cleanedRow.items) {
        cleanedRow.items = cleanedRow.items
            .filter(item => {
                // Unconditionally remove this specific item to allow clean re-entry
                const name = item.component?.name || ''
                return !name.includes('ДСП Сонома 18 мм')
            })
            .map(item => ({
                ...item,
                line_type: 'material',
                quantity: item.quantity || 1,
                unit_of_measure: item.unit_of_measure || item.component?.unit_of_measure || 'шт'
            }))
    }
    
    specForm.value = cleanedRow
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
    if (!specForm.value.items) specForm.value.items = []
    specForm.value.items.push({
        component_id: null,
        quantity: 1,
        unit_of_measure: 'шт',
        line_type: 'material',
        calc_type: 'fixed',
        calc_data_points: { h: [], w: [], l: [] },
        calc_dim_config: { h: { char_name: '', default: 0, unit: 'см', waste: 0 }, w: { char_name: '', default: 0, unit: 'см', waste: 0 }, l: { char_name: '', default: 0, unit: 'см', waste: 0 } },
        calc_formula: '',
        calc_waste_factor: 0
    })
}

const removeItem = (index) => {
    specForm.value.items.splice(index, 1)
}

const addStage = () => {
    if (!specForm.value.stages) specForm.value.stages = []
    specForm.value.stages.push({
        stage_id: null,
        duration_hours: 1,
        role_id: null,
        sort_order: specForm.value.stages.length
    })
}

const removeStage = (index) => {
    specForm.value.stages.splice(index, 1)
    // Refresh sort order
    specForm.value.stages.forEach((s, idx) => s.sort_order = idx)
}

// Calculator Logic
const openCalcDialog = (item) => {
    activeCalcItem.value = item
    if (!item.calc_type) item.calc_type = 'fixed'

    // DEEP MIGRATION: Handle all legacy formats of calc_data_points
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) {
        const oldData = Array.isArray(item.calc_data_points) ? item.calc_data_points : []
        const newDp = { h: [], w: [], l: [] }
        
        // Try to recover data from flat array if it exists
        oldData.forEach(pt => {
            if (pt.h != null) newDp.h.push({ x: pt.size_cm || pt.x || 0, qty: pt.h || pt.qty || 0 })
            if (pt.w != null) newDp.w.push({ x: pt.size_cm || pt.x || 0, qty: pt.w || pt.qty || 0 })
            if (pt.l != null) newDp.l.push({ x: pt.size_cm || pt.x || 0, qty: pt.l || pt.qty || 0 })
        })
        item.calc_data_points = newDp
    } else {
        // Ensure h, w, l keys exist in the object
        if (!item.calc_data_points.h) item.calc_data_points.h = []
        if (!item.calc_data_points.w) item.calc_data_points.w = []
        if (!item.calc_data_points.l) item.calc_data_points.l = []
        
        // Check for cm-based keys from older beta versions
        if (item.calc_data_points.height_cm && item.calc_data_points.h.length === 0) {
            item.calc_data_points.h = item.calc_data_points.height_cm.map(p => ({ x: p.input || 0, qty: p.output || 0 }))
        }
        if (item.calc_data_points.width_cm && item.calc_data_points.w.length === 0) {
            item.calc_data_points.w = item.calc_data_points.width_cm.map(p => ({ x: p.input || 0, qty: p.output || 0 }))
        }
        if (item.calc_data_points.length_cm && item.calc_data_points.l.length === 0) {
            item.calc_data_points.l = item.calc_data_points.length_cm.map(p => ({ x: p.input || 0, qty: p.output || 0 }))
        }
    if (item.calc_type === 'characteristic_mapping') {
        loadAttributesForMapping(props.productId, item.component_id)
    }
    
    // Ensure calc_dim_config exists
    if (!item.calc_dim_config) {
        item.calc_dim_config = {
            h: { char_name: '', default: 0, unit: 'см', waste: 0 },
            w: { char_name: '', default: 0, unit: 'см', waste: 0 },
            l: { char_name: '', default: 0, unit: 'см', waste: 0 }
        }
    } else {
        // Ensure units and waste exist in existing config
        for (const k of ['h', 'w', 'l']) {
            if (!item.calc_dim_config[k]) item.calc_dim_config[k] = { char_name: '', default: 0, unit: 'см', waste: 0 }
            if (!item.calc_dim_config[k].unit) item.calc_dim_config[k].unit = 'см'
            if (item.calc_dim_config[k].waste === undefined) item.calc_dim_config[k].waste = 0
        }
    }

    calcDialogOpen.value = true
}

const handleTypeChange = (item) => {
    if (item.calc_type === 'interpolation' && (!item.calc_data_points || Array.isArray(item.calc_data_points))) {
        item.calc_data_points = { h: [], w: [], l: [] }
    }
    if (item.calc_type === 'characteristic_mapping') {
        if (!item.characteristic_mappings) item.characteristic_mappings = []
        loadAttributesForMapping(props.productId, item.component_id)
    }
}

const addPoint = (item, dimKey) => {
    if (!item) return
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) {
        item.calc_data_points = { h: [], w: [], l: [] }
    }
    if (!item.calc_data_points[dimKey]) item.calc_data_points[dimKey] = []
    item.calc_data_points[dimKey].push({ x: 0, qty: 0 })
}

const removePoint = (item, dimKey, index) => {
    item.calc_data_points[dimKey].splice(index, 1)
}

// Material mapping helpers
const addMappingRow = (item) => {
    if (!item.material_mapping) item.material_mapping = {}
    // Find a unique key name
    let i = 1
    while (item.material_mapping[`Значення ${i}`]) i++
    item.material_mapping[`Значення ${i}`] = null
}




const addVarToFormula = (v) => {
    if (!activeCalcItem.value) return
    activeCalcItem.value.calc_formula = (activeCalcItem.value.calc_formula || '') + v
}

const addAttrToFormula = (name) => {
    if (!activeCalcItem.value) return
    activeCalcItem.value.calc_formula = (activeCalcItem.value.calc_formula || '') + '{' + name + '}'
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
    // Force standard material type to ensure all fields are visible
    row.line_type = 'material'
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

.detail-mapping-box {
    background: #f5f7ff;
}

.mapping-header label {
    letter-spacing: 0.05em;
}

.mapping-rows label {
    letter-spacing: 0.05em;
}
</style>
