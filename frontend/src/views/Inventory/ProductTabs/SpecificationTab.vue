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
        <div class="header-actions">
          <el-button @click="editingSpec = null" class="btn-back">
            До списку
          </el-button>
          <el-button class="btn-validate" @click="openValidationDialog" :disabled="!specForm.items || specForm.items.length === 0">
            <el-icon class="mr-1"><Memo /></el-icon> Перевірити розрахунок
          </el-button>
          <el-button type="primary" :loading="saving" @click="saveSpecification" class="btn-save">
            <el-icon><Check /></el-icon> Зберегти специфікацію
          </el-button>
        </div>
      </div>

      <!-- Validation Parameters Dialog (Calculation Simulator) -->
      <el-dialog
        v-model="validationParamsDialogOpen"
        title="Параметри для перевірки розрахунку"
        width="500px"
        append-to-body
        class="premium-dialog"
      >
        <div class="dialog-description mb-4">
           Вкажіть значення параметрів, щоб перевірити, як система розрахує кількість матеріалів для цього варіанту виробу.
        </div>

        <el-form label-position="top">
           <div class="grid grid-cols-2 gap-4">
              <el-form-item label="Висота (H), мм">
                 <el-input-number v-model="simulationDims.height_mm" :controls="false" class="w-full" />
              </el-form-item>
              <el-form-item label="Ширина (W), мм">
                 <el-input-number v-model="simulationDims.width_mm" :controls="false" class="w-full" />
              </el-form-item>
              <el-form-item label="Довжина (L), мм">
                 <el-input-number v-model="simulationDims.length_mm" :controls="false" class="w-full" />
              </el-form-item>
              <el-form-item label="Вага (Kg), кг">
                 <el-input-number v-model="simulationDims.weight_kg" :controls="false" class="w-full" />
              </el-form-item>
           </div>

           <!-- Dynamic Characteristics Selection -->
           <div v-for="charName in usedCharacteristics" :key="charName" class="mt-2">
              <el-form-item :label="charName">
                 <el-select v-model="simulationDims.custom_attributes[charName]" placeholder="Оберіть значення" class="w-full" filterable allow-create>
                    <el-option 
                       v-for="opt in getCharOptions(charName)" 
                       :key="opt" 
                       :label="opt" 
                       :value="opt" 
                    />
                 </el-select>
              </el-form-item>
           </div>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="validationParamsDialogOpen = false">Скасувати</el-button>
            <el-button type="primary" @click="runValidationFromDialog" class="btn-run-calc">
               Запустити розрахунок
            </el-button>
          </div>
        </template>
      </el-dialog>
       
      <!-- Validation Result Banner -->
      <div v-if="validationResult.summary.rowsCount > 0 || validationResult.errors.length > 0" class="bom-validation-banner mt-4">
         <el-alert 
           v-if="validationResult.errors.length > 0" 
           title="Знайдено помилки" 
           type="error" 
           show-icon 
           :closable="false"
         >
            <div class="bom-alert-list" style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">
               <div v-for="(err, idx) in validationResult.errors" :key="idx" class="bom-alert-item" style="font-size: 12px;">
                  • {{ err.message }}
               </div>
            </div>
         </el-alert>
         
         <el-alert 
           v-if="validationResult.warnings.length > 0" 
           title="Попередження" 
           type="warning" 
           show-icon 
           :closable="false"
           class="mt-2"
         >
            <div class="bom-alert-list" style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">
               <div v-for="(warn, idx) in validationResult.warnings" :key="idx" class="bom-alert-item" style="font-size: 12px;">
                  • {{ warn.message }}
               </div>
            </div>
         </el-alert>

         <div v-if="validationResult.isValid && validationResult.errors.length === 0" class="bom-success-summary mt-2">
            <el-alert 
               title="Розрахунок перевірено — все добре" 
               type="success" 
               show-icon 
               :closable="false"
            >
               <div class="text-xs font-medium mt-1">
                  Матеріалів: {{ validationResult.summary.materialsCount }} | 
                  Проблем: 0 | 
                  Орієнтовна собівартість: <strong>{{ validationResult.summary.totalMaterialCost }} грн</strong>
               </div>
            </el-alert>
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
          
          <div class="bom-grid-table">
             <!-- Header Row -->
             <div class="bom-grid-row header-row">
                <div class="bom-col-material">Товар / Матеріал</div>
                <div class="bom-col-qty">Кількість</div>
                <div class="bom-col-uom">Од.</div>
                <div class="bom-col-settings"></div>
                <div class="bom-col-actions">Дії</div>
             </div>
             
             <!-- Body Rows -->
             <div class="bom-grid-body">
                <div v-for="(row, index) in specForm.items" :key="index" class="bom-grid-row" :class="{'row-error': getRowValidationStatus(index + 1) === 'error', 'row-warning': getRowValidationStatus(index + 1) === 'warning'}">
                   <div class="bom-col-material">
                      <el-select
                         v-model="row.component_id"
                         filterable
                         remote
                         reserve-keyword
                         placeholder="Пошук номенклатури..."
                         :remote-method="searchProducts"
                         :loading="searchingProducts"
                         class="w-full"
                         @change="(val) => handleComponentSelect(row, val)"
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
                   </div>
                   
                   <div class="bom-col-qty">
                      <el-input-number 
                         v-model="row.quantity" 
                         :min="0" :step="1" :precision="3" 
                         class="w-full"
                         :disabled="row.calc_type && row.calc_type !== 'fixed'"
                         controls-position="right"
                         size="small"
                      />
                      
                      <div class="bom-qty-helper">
                         <template v-if="row.calc_type && row.calc_type !== 'fixed'">
                            <el-tooltip placement="top" effect="dark">
                               <template #content>
                                  <div class="p-1">
                                     <div class="font-bold border-b border-gray-600 mb-1 pb-1">Розшифровка розрахунку:</div>
                                     <div v-for="(line, idx) in calculateQuantityDetails(row)" :key="idx" class="text-xs py-0.5">
                                        • {{ line }}
                                     </div>
                                  </div>
                               </template>
                               <span class="cursor-help border-b border-dotted border-gray-400">
                                  Розраховано: {{ getBaseQuantity(row).toFixed(3) }}
                               </span>
                            </el-tooltip>
                            <span v-if="getTotalWastePercent(row) > 0" class="text-orange-400 font-bold"> (+{{ getTotalWastePercent(row) }}%)</span>
                         </template>
                      </div>
                   </div>

                   <div class="bom-col-uom">
                      <span class="bom-uom">{{ row.unit_of_measure || 'шт' }}</span>
                   </div>

                   <div class="bom-col-settings">
                      <div 
                         class="calc-indicator-grid" 
                         :class="row.calc_type && row.calc_type !== 'fixed' ? 'active' : 'inactive'"
                         @click="openCalcDialog(row)"
                      >
                         <el-icon :size="14"><Setting /></el-icon>
                      </div>
                   </div>

                   <div class="bom-col-actions">
                      <el-button link type="danger" :icon="Delete" @click="removeItem(index)" />
                   </div>
                </div>
             </div>

             <div v-if="!specForm.items || specForm.items.length === 0" class="bom-grid-empty">
                <el-empty description="Жодного матеріалу не додано" :image-size="60" />
             </div>
          </div>
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
              <el-form-item :label="`Висота (H), мм`" :class="{ 'warning-border': testDims.height_mm < 100 }">
                <el-input-number v-model="testDims.height_mm" class="w-full" :precision="0" />
                <div v-if="testDims.height_mm > 0 && testDims.height_mm < 100" class="text-[10px] text-orange-500 font-bold">Можливо см?</div>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="`Ширина (W), мм`" :class="{ 'warning-border': testDims.width_mm < 100 }">
                <el-input-number v-model="testDims.width_mm" class="w-full" :precision="0" />
                <div v-if="testDims.width_mm > 0 && testDims.width_mm < 100" class="text-[10px] text-orange-500 font-bold">Можливо см?</div>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="`Довжина (L), мм`" :class="{ 'warning-border': testDims.length_mm < 100 }">
                <el-input-number v-model="testDims.length_mm" class="w-full" :precision="0" />
                <div v-if="testDims.length_mm > 0 && testDims.length_mm < 100" class="text-[10px] text-orange-500 font-bold">Можливо см?</div>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Вага, кг">
                <el-input-number v-model="testDims.weight_kg" class="w-full" />
              </el-form-item>
            </el-col>
          </el-row>

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
            <span class="text-lg font-bold">Налаштування розумного розрахунку [v1.4-MM]</span>
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
                <div v-for="dim in interpDims" :key="dim.key" :class="'dim-section dim-' + dim.key">
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
                                <el-radio-button label="м" />
                            </el-radio-group>
                            <el-button type="primary" size="small" @click="addPoint(activeCalcItem, dim.key)" :icon="Plus" circle />
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <el-table :data="getPoints(activeCalcItem, dim.key)" size="small" border class="compact-table">
                            <el-table-column :label="dim.label + ' (' + getDimConfig(activeCalcItem, dim.key).unit + ')'">
                                <template #default="scope">
                                    <el-input-number 
                                      v-model="scope.row.x"
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
                                    v-model="getDimConfig(activeCalcItem, dim.key).default"
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
                <el-option label="Висота (H)" value="height_mm" />
                <el-option label="Ширина (W)" value="width_mm" />
                <el-option label="Довжина (L)" value="length_mm" />
              </el-select>
            </el-form-item>

            <el-form-item label="Коефіцієнт (Множник)" v-if="activeCalcItem.calc_type === 'proportional'" class="mt-4">
              <el-input v-model="activeCalcItem.calc_formula" type="number" step="0.0001" placeholder="напр. 0.1" />
              <div class="text-xs text-gray-400 mt-1" style="line-height: 1.2;">К-сть = Вимір × Коефіцієнт</div>
            </el-form-item>

            <el-form-item label="Своя математична формула" v-if="activeCalcItem.calc_type === 'formula'" class="mt-4">
              <el-input v-model="activeCalcItem.calc_formula" type="textarea" :rows="3" placeholder="напр. {W} * {H} / 1000000" />
              <div class="mt-2 flex flex-wrap gap-2">
                <el-button v-for="v in ['{W}', '{H}', '{L}', '{Kg}']" :key="v" size="small" @click="addVarToFormula(v)">{{ v }}</el-button>
                <el-dropdown trigger="click" @command="addAttrToFormula" v-if="productAttributes.length > 0">
                  <el-button size="small" type="info" plain>+ Додати характеристику</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-for="attr in productAttributes" :key="attr.id" :command="attr.name">{{ attr.name }}</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </el-form-item>

            <div v-if="activeCalcItem.calc_type === 'characteristic_mapping'" class="mt-4">
               <div class="detail-mapping-box p-4 rounded-lg border border-indigo-100 bg-indigo-50/30">
                  <div class="mapping-header flex justify-between items-center mb-4">
                     <label class="text-xs font-bold text-indigo-900 uppercase">Зв'язок характеристик</label>
                     <el-button type="primary" size="small" @click="addMappingLine" plain :icon="Plus">Додати зв'язок</el-button>
                  </div>
                  <div class="mapping-rows space-y-3">
                     <div v-for="(m, idx) in activeCalcItem.characteristic_mappings" :key="idx" class="flex items-center gap-3">
                        <div class="flex-1">
                           <label class="text-[10px] text-gray-500 block mb-1">Характеристика компонента</label>
                           <el-select v-model="m.component_characteristic_id" size="small" class="w-full" placeholder="Виберіть...">
                              <el-option v-for="a in componentAttributes" :key="a.id" :label="a.name" :value="a.id" />
                           </el-select>
                        </div>
                        <div class="text-indigo-400 mt-5">-></div>
                        <div class="flex-1">
                           <label class="text-[10px] text-gray-500 block mb-1">Характеристика виробу</label>
                           <el-select v-model="m.parent_characteristic_id" size="small" class="w-full" placeholder="Виберіть...">
                              <el-option v-for="a in parentAttributes" :key="a.id" :label="a.name" :value="a.id" />
                           </el-select>
                        </div>
                        <el-button type="danger" link :icon="Delete" class="mt-5" @click="removeMappingLine(idx)" />
                     </div>
                     
                     <div v-if="!activeCalcItem.characteristic_mappings?.length" class="text-center py-4 border-2 border-dashed border-indigo-100 rounded text-gray-400 text-xs">
                        Немає налаштованих зв'язків. Натисніть "Додати зв'язок".
                     </div>
                  </div>
               </div>
            </div>
            
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
import { Clock, Plus, Delete, ArrowLeft, Setting, Monitor, Back, Check, Warning, Memo, InfoFilled } from '@element-plus/icons-vue'
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

const isSimulationMode = ref(false)
const validationParamsDialogOpen = ref(false)
const simulationDims = reactive({
    height_mm: 0,
    width_mm: 0,
    length_mm: 0,
    weight_kg: 0,
    custom_attributes: {}
})

const openValidationDialog = () => {
    isSimulationMode.value = true
    simulationDims.height_mm = props.productDimensions.height_mm || 0
    simulationDims.width_mm = props.productDimensions.width_mm || 0
    simulationDims.length_mm = props.productDimensions.length_mm || 0
    simulationDims.weight_kg = props.productDimensions.weight_kg || 0
    
    // Sync characteristics
    usedCharacteristics.value.forEach(char => {
        const val = getAttrValue(char)
        if (val !== null) {
            simulationDims.custom_attributes[char] = val
        }
    })
    
    validationParamsDialogOpen.value = true
}

const runValidationFromDialog = () => {
    validationParamsDialogOpen.value = false
    validateBom()
}

const getCharOptions = (charName) => {
    const attr = productAttributes.value.find(a => a.name === charName)
    if (!attr || !attr.options) return []
    return attr.options.map(o => o.value)
}

const usedCharacteristics = computed(() => {
    const chars = new Set()
    if (specForm.value && specForm.value.items) {
        specForm.value.items.forEach(item => {
            if (item.calc_dim_config) {
                Object.values(item.calc_dim_config).forEach(cfg => {
                    if (cfg.char_name) chars.add(cfg.char_name)
                })
            }
            // Also check global variant sync
            if (props.productDimensions.variant_config) {
                const dims = ['height', 'width', 'length']
                dims.forEach(d => {
                    const g = props.productDimensions.variant_config[d]
                    if (g?.source === 'attribute' && g.attr_id) {
                        const attr = productAttributes.value.find(a => a.id === g.attr_id)
                        if (attr) chars.add(attr.name)
                    }
                })
            }
        })
    }
    return Array.from(chars)
})

const toMeters = (value, unit) => {
    if (unit === 'мм') return value / 1000
    if (unit === 'см') return value / 100
    if (unit === 'м') return value
    return value / 1000 // default mm
}

const getAttrValue = (attrName) => {
    if (!attrName) return null
    
    // Priority: Simulation Mode
    if (isSimulationMode.value && simulationDims.custom_attributes[attrName] !== undefined) {
        return parseFloat(simulationDims.custom_attributes[attrName]) || 0
    }

    const attrDef = productAttributes.value.find(a => a.name === attrName)
    if (!attrDef) return null
    
    // Check in product_attributes
    const attrVal = (props.productDimensions.product_attributes || []).find(a => a.attribute_id === attrDef.id)
    if (attrVal) {
        return parseFloat(attrVal.text_value) || 0
    }
    return null
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
    if (!item.calc_dim_config) {
        item.calc_dim_config = { 
            h: { char_name: '', default: 0, unit: 'мм', waste: 0 }, 
            w: { char_name: '', default: 0, unit: 'мм', waste: 0 }, 
            l: { char_name: '', default: 0, unit: 'мм', waste: 0 } 
        }
    }
    if (!item.calc_dim_config[key]) item.calc_dim_config[key] = { char_name: '', default: 0, unit: 'мм', waste: 0 }
    if (!item.calc_dim_config[key].unit) item.calc_dim_config[key].unit = 'мм'
    if (item.calc_dim_config[key].waste === undefined) item.calc_dim_config[key].waste = 0
    return item.calc_dim_config[key]
}

const calculateQuantityInternal = (item, includeWaste = true, returnDetails = false) => {
    if (!item || item.calc_type === 'fixed') return item?.quantity || 0

    // Use simulation dimensions if enabled
    const activeDims = isSimulationMode.value ? simulationDims : props.productDimensions
    const isMeters = item.unit_of_measure === 'м'
    
    const dimensions = {
        W: parseFloat(activeDims.width_mm) || 0,
        H: parseFloat(activeDims.height_mm) || 0,
        L: parseFloat(activeDims.length_mm) || 0,
        Kg: parseFloat(activeDims.weight_kg) || 0
    }

    const dimLabels = { height_mm: 'H', width_mm: 'W', length_mm: 'L' }
    const dimFullKeys = { h: 'height_mm', w: 'width_mm', l: 'length_mm' }

    let result = 0
    let details = []

    if (item.calc_type === 'interpolation') {
        const dp = item.calc_data_points || {}
        let total = 0
        let hasAnyPoints = false

        for (const [key, dimKey] of Object.entries(dimFullKeys)) {
            const pts = (dp[key] || []).filter(p => p.qty != null)
            if (pts.length === 0) continue
            hasAnyPoints = true
            
            const config = getDimConfig(item, key)
            let dimValRaw = parseFloat(activeDims[dimKey]) || 0
            let sourceLabel = dimLabels[key] || key
            let warning = ''

            // AUTOMATION: If not explicitly set in config, check global variant_config
            let activeCharName = config.char_name
            if (!activeCharName && props.productDimensions.variant_config) {
                const globalCfg = props.productDimensions.variant_config[dimKey === 'height_mm' ? 'height' : (dimKey === 'width_mm' ? 'width' : 'length')]
                if (globalCfg?.source === 'attribute' && globalCfg.attr_id) {
                    const attr = productAttributes.value.find(a => a.id === globalCfg.attr_id)
                    if (attr) activeCharName = attr.name
                }
            }

            if (activeCharName) {
                const customVal = getAttrValue(activeCharName)
                if (customVal !== null) {
                    dimValRaw = customVal
                    sourceLabel = activeCharName
                } else {
                    warning = `[!] Характеристика "${activeCharName}" не знайдена`
                }
            }

            // Points 'x' are stored in the unit specified in config.unit
            // We compare dimValRaw (which is in mm or characteristic unit) with pts 'x'
            // We need to normalize both to the same unit (config.unit)
            let normalizedDimVal = dimValRaw
            if (!config.char_name) {
                // Product dimensions are in mm, so convert to config.unit
                if (config.unit === 'см') normalizedDimVal = dimValRaw / 10
                if (config.unit === 'м') normalizedDimVal = dimValRaw / 1000
            } else {
                // Characteristics are assumed to be in the unit specified in config.unit
                normalizedDimVal = dimValRaw
            }

            const sorted = [...pts].sort((a, b) => (a.x || 0) - (b.x || 0))
            let countResult = 0
            const interp = (p1, p2, val) => {
                const slope = (p2.x !== p1.x) ? (p2.qty - p1.qty) / (p2.x - p1.x) : 0
                return p1.qty + slope * (val - p1.x)
            }
            if (sorted.length === 1) { countResult = sorted[0].qty }
            else if (normalizedDimVal <= sorted[0].x) { countResult = interp(sorted[0], sorted[1], normalizedDimVal) }
            else if (normalizedDimVal >= sorted[sorted.length - 1].x) { countResult = interp(sorted[sorted.length - 2], sorted[sorted.length - 1], normalizedDimVal) }
            else {
                for (let i = 0; i < sorted.length - 1; i++) {
                    if (normalizedDimVal >= sorted[i].x && normalizedDimVal <= sorted[i + 1].x) {
                        countResult = interp(sorted[i], sorted[i + 1], normalizedDimVal)
                        break
                    }
                }
            }
            
            let dimFinal = countResult
            let stepLabel = `${sourceLabel}: ${dimValRaw} ${config.char_name ? config.unit : 'мм'}`
            if (warning) stepLabel += ` ${warning}`

            if (isMeters) {
                // In interpolation mode, we assume countResult is ALREADY in meters (or the material's unit)
                // if the user entered absolute values in the table. 
                // We show the dimension for reference.
                const meters = toMeters(dimValRaw, config.char_name ? config.unit : 'мм')
                stepLabel += ` (при ${meters.toFixed(3)}м) → ${dimFinal.toFixed(3)}м`
            } else {
                stepLabel += ` → ${countResult.toFixed(3)} ${item.unit_of_measure || 'шт'}`
            }

            // Apply waste for this dimension
            if (includeWaste && config.waste) {
                const wasteFactor = (1 + parseFloat(config.waste) / 100)
                dimFinal *= wasteFactor
                stepLabel += ` (+${config.waste}% відх. = ${dimFinal.toFixed(3)})`
            }
            
            details.push(stepLabel)
            total += Math.max(0, dimFinal)
        }
        if (!hasAnyPoints) return item.quantity
        result = total
    }
    else if (item.calc_type === 'proportional') {
        const dimKey = item.calc_dimension || 'width_mm'
        const dimMapLocal = { height_mm: 'h', width_mm: 'w', length_mm: 'l' }
        const key = dimMapLocal[dimKey]
        const config = getDimConfig(item, key)
        const dimLabelsLocal = { height_mm: 'H', width_mm: 'W', length_mm: 'L' }
        
        let dimValRaw = parseFloat(activeDims[dimKey]) || 0
        let sourceLabel = dimLabelsLocal[dimKey]
        let warning = ''

        if (config.char_name) {
            const customVal = getAttrValue(config.char_name)
            if (customVal !== null) {
                dimValRaw = customVal
                sourceLabel = config.char_name
            } else {
                warning = `[!] Характеристика "${config.char_name}" не знайдена`
            }
        }

        const coeff = parseFloat(item.calc_formula) || 0
        let stepLabel = `${sourceLabel}: ${dimValRaw} ${config.char_name ? config.unit : 'мм'}`
        if (warning) stepLabel += ` ${warning}`

        if (isMeters) {
            const meters = toMeters(dimValRaw, config.char_name ? config.unit : 'мм')
            result = coeff * meters
            stepLabel += ` → ${meters.toFixed(3)}м × ${coeff} = ${result.toFixed(3)}м`
        } else {
            result = dimValRaw * coeff
            stepLabel += ` → ${dimValRaw} × ${coeff} = ${result.toFixed(3)}`
        }

        if (includeWaste && item.calc_waste_factor) {
            const waste = parseFloat(item.calc_waste_factor) * 100
            result *= (1 + parseFloat(item.calc_waste_factor))
            stepLabel += ` (+${waste.toFixed(1)}% відх. = ${result.toFixed(3)})`
        }
        details.push(stepLabel)
    }
    else if (item.calc_type === 'area') {
        result = (dimensions.W * dimensions.H) / 1000000 
        details.push(`Площа: (${dimensions.W}мм × ${dimensions.H}мм) / 1000000 = ${result.toFixed(4)} м²`)
        if (includeWaste && item.calc_waste_factor) {
            const waste = parseFloat(item.calc_waste_factor) * 100
            result *= (1 + parseFloat(item.calc_waste_factor))
            details.push(`+ Відходи ${waste.toFixed(1)}% = ${result.toFixed(4)}`)
        }
    }
    else if (item.calc_type === 'volume') {
        result = (dimensions.W * dimensions.H * dimensions.L) / 1000000000 
        details.push(`Об'єм: (${dimensions.W}мм × ${dimensions.H}мм × ${dimensions.L}мм) / 1000000000 = ${result.toFixed(4)} м³`)
        if (includeWaste && item.calc_waste_factor) {
            const waste = parseFloat(item.calc_waste_factor) * 100
            result *= (1 + parseFloat(item.calc_waste_factor))
            details.push(`+ Відходи ${waste.toFixed(1)}% = ${result.toFixed(4)}`)
        }
    }
    else if (item.calc_type === 'formula') {
        try {
            const { W, H, L, Kg } = dimensions
            const regex = /{([^}]+)}/g
            let formula = item.calc_formula || '0'
            let match;
            while ((match = regex.exec(item.calc_formula)) !== null) {
                const attrName = match[1]
                if (!['W', 'H', 'L', 'Kg'].includes(attrName)) {
                    const val = getAttrValue(attrName)
                    formula = formula.replace(`{${attrName}}`, val !== null ? val : 0)
                }
            }
            formula = formula.replace(/{W}/g, W).replace(/{H}/g, H).replace(/{L}/g, L).replace(/{Kg}/g, Kg)
            
            result = eval(formula)
            details.push(`Формула: ${item.calc_formula} → ${formula} = ${result.toFixed(4)}`)

            if (includeWaste && item.calc_waste_factor) {
                const waste = parseFloat(item.calc_waste_factor) * 100
                result *= (1 + parseFloat(item.calc_waste_factor))
                details.push(`+ Відходи ${waste.toFixed(1)}% = ${result.toFixed(4)}`)
            }
        } catch (e) {
            return returnDetails ? { result: 'Помилка', details: ['Помилка у формулі'] } : 'Помилка'
        }
    }

    if (returnDetails) return { result, details }
    return result
}

const calculateQuantity = (item) => {
    const res = calculateQuantityInternal(item, true)
    return typeof res === 'number' ? res.toFixed(4) : res
}

const getBaseQuantity = (item) => {
    if (!item || item.calc_type === 'fixed') return item?.quantity || 0
    return calculateQuantityInternal(item, false)
}

const calculateQuantityDetails = (item) => {
    if (!item || item.calc_type === 'fixed') return ['Фіксована кількість']
    const { details } = calculateQuantityInternal(item, true, true)
    return details || []
}

const getTotalWastePercent = (item) => {
    if (!item.calc_dim_config) return 0
    const base = calculateQuantityInternal(item, false)
    if (!base || base === 0) return 0
    const withWaste = calculateQuantityInternal(item, true)
    const percent = ((withWaste / base) - 1) * 100
    return percent > 0 ? parseFloat(percent.toFixed(1)) : 0
}

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

const loadSpecifications = async () => {
    if (!props.productId) return
    loading.value = true
    try {
        const resData = await getProductSpecifications(props.productId)
        resData.forEach(spec => {
            if (spec.items) {
                spec.items.forEach(item => {
                    if (item.component?.unit_of_measure) {
                        item.unit_of_measure = item.component.unit_of_measure
                    }
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

const editSpec = (row) => {
    const cleanedRow = JSON.parse(JSON.stringify(row))
    if (cleanedRow.items) {
        cleanedRow.items = cleanedRow.items
            .map(item => ({
                ...item,
                line_type: 'material',
                quantity: item.quantity || 1,
                unit_of_measure: item.unit_of_measure || item.component?.unit_of_measure || 'шт'
            }))
    }
    specForm.value = cleanedRow
    editingSpec.value = row.id
    if (specForm.value.items && specForm.value.items.length > 0) {
        const preloads = specForm.value.items
           .filter(i => i.component)
           .map(i => i.component)
        const newResults = [...productSearchResults.value, ...preloads]
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

const validationResult = ref({
    isValid: true,
    errors: [],
    warnings: [],
    summary: {
        rowsCount: 0,
        materialsCount: 0,
        totalMaterialCost: 0,
        missingStockCount: 0,
        duplicateCount: 0
    }
})

const lastValidationDate = ref(null)

const getRowValidationStatus = (rowIdx) => {
    if (validationResult.value.errors.some(e => e.rowIndex === rowIdx)) return 'error'
    if (validationResult.value.warnings.some(w => w.rowIndex === rowIdx)) return 'warning'
    return 'success'
}

const validateBom = async () => {
    const errors = []
    const warnings = []
    let totalMaterialCost = 0
    let missingStockCount = 0
    let duplicateCount = 0

    const items = specForm.value.items || []

    if (items.length === 0) {
        errors.push({ rowIndex: -1, field: '', message: 'Специфікація не має жодного компонента.' })
    }

    const materialCounts = new Map()

    for (let i = 0; i < items.length; i++) {
        const row = items[i]
        const rowIdx = i + 1

        if (!row.component_id) {
            errors.push({ rowIndex: rowIdx, field: 'component_id', message: `Рядок ${rowIdx}: не вибрано матеріал.` })
            continue
        }

        if (materialCounts.has(row.component_id)) {
            materialCounts.set(row.component_id, materialCounts.get(row.component_id) + 1)
        } else {
            materialCounts.set(row.component_id, 1)
        }

        const material = productSearchResults.value.find(p => p.id === row.component_id) || row.component
        const materialName = material?.name || 'Матеріал'

        if (row.calc_type === 'fixed' && (row.quantity == null || row.quantity <= 0)) {
            errors.push({ rowIndex: rowIdx, field: 'quantity', message: `Рядок ${rowIdx} (${materialName}): кількість має бути більше 0.` })
        }

        if (row.calc_type && row.calc_type !== 'fixed') {
            const calcQty = calculateQuantityInternal(row, true)
            if (calcQty === 'Помилка' || calcQty == null || calcQty <= 0) {
                errors.push({ rowIndex: rowIdx, field: 'quantity', message: `Рядок ${rowIdx} (${materialName}): помилка розрахунку калькулятора або значення <= 0.` })
            }

            // CHECK FOR MISSING POINTS
            if (row.calc_type === 'interpolation') {
                const dp = row.calc_data_points || {}
                const dimMap = { h: 'Висота', w: 'Ширина', l: 'Довжина' }
                for (const k of ['h', 'w', 'l']) {
                    const pts = (dp[k] || []).filter(p => p.qty != null)
                    // If this dimension is globally or locally linked but has no points
                    const isLinked = row.calc_dim_config?.[k]?.char_name || (props.productDimensions?.variant_config?.[k === 'h' ? 'height' : (k === 'w' ? 'width' : 'length')]?.source === 'attribute')
                    if (isLinked && pts.length === 0) {
                        warnings.push({ rowIndex: rowIdx, field: 'points', message: `Рядок ${rowIdx}: додайте точки розрахунку для виміру "${dimMap[k]}", бо він пов'язаний з характеристикою.` })
                    }
                }
            }
        }

        if (!row.unit_of_measure) {
            warnings.push({ rowIndex: rowIdx, field: 'unit_of_measure', message: `Рядок ${rowIdx} (${materialName}): не вказано одиницю виміру.` })
        }

        const unitCost = parseFloat(material?.cost || 0)
        if (unitCost <= 0) {
            warnings.push({ rowIndex: rowIdx, field: 'cost', message: `Рядок ${rowIdx} (${materialName}): для матеріалу не вказана собівартість.` })
        } else {
            const actualQty = row.calc_type !== 'fixed' ? calculateQuantityInternal(row, true) : row.quantity
            if (typeof actualQty === 'number') {
                totalMaterialCost += actualQty * unitCost
            }
        }

        const stockAvailable = parseFloat(material?.stock_quantity != null ? material.stock_quantity : (material?.stock_available != null ? material.stock_available : 0))
        const actualQtyForStock = row.calc_type !== 'fixed' ? calculateQuantityInternal(row, true) : row.quantity
        
        if (typeof actualQtyForStock === 'number' && stockAvailable < actualQtyForStock) {
            missingStockCount++
            warnings.push({ rowIndex: rowIdx, field: 'stock', message: `Рядок ${rowIdx} (${materialName}): недостатньо залишку на складі. Потрібно: ${actualQtyForStock.toFixed(3)}, Доступно: ${stockAvailable.toFixed(3)}` })
        }
    }

    for (const [compId, count] of materialCounts.entries()) {
        if (count > 1) {
            duplicateCount++
            const mat = productSearchResults.value.find(p => p.id === compId) || items.find(i => i.component_id === compId)?.component
            warnings.push({ rowIndex: -1, field: '', message: `Матеріал "${mat?.name || 'Матеріал'}" доданий кілька разів.` })
        }
    }

    validationResult.value = {
        isValid: errors.length === 0,
        errors,
        warnings,
        summary: {
            rowsCount: items.length,
            materialsCount: materialCounts.size,
            totalMaterialCost: parseFloat(totalMaterialCost.toFixed(2)),
            missingStockCount,
            duplicateCount
        }
    }

    lastValidationDate.value = new Date().toLocaleString('uk-UA')

    if (errors.length === 0) {
        ElMessage.success(`Розрахунок перевірено. Помилок не знайдено.`)
    } else {
        ElMessage.error(`Знайдено помилок: ${errors.length}`)
    }
}

const saveSpecification = async () => {
    if (!specForm.value.name) {
        ElMessage.warning('Вкажіть назву специфікації')
        return
    }

    await validateBom()

    if (!validationResult.value.isValid) {
        ElMessageBox.alert('Не вдалося зберегти: специфікація містить помилки. Будь ласка, виправте їх.', 'Помилка валідації', { type: 'error' })
        return
    }

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
        calc_dim_config: { h: { char_name: '', default: 0, unit: 'мм', waste: 0 }, w: { char_name: '', default: 0, unit: 'мм', waste: 0 }, l: { char_name: '', default: 0, unit: 'мм', waste: 0 } },
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
    specForm.value.stages.forEach((s, idx) => s.sort_order = idx)
}

const openCalcDialog = (item) => {
    activeCalcItem.value = item
    if (!item.calc_type) item.calc_type = 'fixed'
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) {
        item.calc_data_points = { h: [], w: [], l: [] }
    }
    if (!item.calc_dim_config) {
        item.calc_dim_config = { 
            h: { char_name: '', default: parseFloat(props.productDimensions.height_mm) || 0, unit: 'мм', waste: 0 }, 
            w: { char_name: '', default: parseFloat(props.productDimensions.width_mm) || 0, unit: 'мм', waste: 0 }, 
            l: { char_name: '', default: parseFloat(props.productDimensions.length_mm) || 0, unit: 'мм', waste: 0 } 
        }
    } else {
        // Sync defaults if they are 0 but product has dimensions
        if (!item.calc_dim_config.h.default && props.productDimensions.height_mm) item.calc_dim_config.h.default = props.productDimensions.height_mm
        if (!item.calc_dim_config.w.default && props.productDimensions.width_mm) item.calc_dim_config.w.default = props.productDimensions.width_mm
        if (!item.calc_dim_config.l.default && props.productDimensions.length_mm) item.calc_dim_config.l.default = props.productDimensions.length_mm
    }

    // NEW: Auto-sync characteristic names from global variant_config
    if (props.productDimensions.variant_config) {
        const vCfg = props.productDimensions.variant_config
        const dims = { h: 'height', w: 'width', l: 'length' }
        for (const [key, globalKey] of Object.entries(dims)) {
            const g = vCfg[globalKey]
            if (g?.source === 'attribute' && g.attr_id && !item.calc_dim_config[key].char_name) {
                const attr = productAttributes.value.find(a => a.id === g.attr_id)
                if (attr) item.calc_dim_config[key].char_name = attr.name
            }
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
    if (!item.calc_data_points || Array.isArray(item.calc_data_points)) item.calc_data_points = { h: [], w: [], l: [] }
    if (!item.calc_data_points[dimKey]) item.calc_data_points[dimKey] = []
    item.calc_data_points[dimKey].push({ x: 0, qty: 0 })
}

const removePoint = (item, dimKey, index) => {
    item.calc_data_points[dimKey].splice(index, 1)
}

const addVarToFormula = (v) => {
    if (!activeCalcItem.value) return
    activeCalcItem.value.calc_formula = (activeCalcItem.value.calc_formula || '') + v
}

const addAttrToFormula = (name) => {
    if (!activeCalcItem.value) return
    activeCalcItem.value.calc_formula = (activeCalcItem.value.calc_formula || '') + '{' + name + '}'
}

const searchProducts = async (query) => {
    searchingProducts.value = true
    try {
        const params = query ? { search: query } : {}
        const res = await api.get('/api/v1/products', { params })
        productSearchResults.value = res.data.filter(p => p.id !== props.productId)
    } catch (e) {
        console.error('Failed to search products', e)
    } finally {
        searchingProducts.value = false
    }
}

const handleComponentSelect = (row, componentId) => {
    const selected = productSearchResults.value.find(p => p.id === componentId)
    if (selected && selected.unit_of_measure) row.unit_of_measure = selected.unit_of_measure
    row.line_type = 'material'
}

const previewVisible = ref(false)
const previewLoading = ref(false)
const previewResults = ref([])
const testDims = reactive({
    height_mm: props.productDimensions?.height_mm || 0,
    width_mm: props.productDimensions?.width_mm || 0,
    length_mm: props.productDimensions?.length_mm || 0,
    weight_kg: props.productDimensions?.weight_kg || 0,
    custom_attributes: {}
})

const testAttributes = computed(() => {
    const keys = new Set()
    if (specForm.value && specForm.value.items) {
        specForm.value.items.forEach(item => {
            if (item.calc_type === 'formula' && item.calc_formula) {
                const regex = /{([^}]+)}/g
                let match;
                while ((match = regex.exec(item.calc_formula)) !== null) {
                    keys.add(match[1])
                    if (!(match[1] in testDims.custom_attributes)) testDims.custom_attributes[match[1]] = 0
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
    searchProducts('')
})
</script>

<style scoped>
.specification-tab-container {
    padding: 0;
}

.tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.tab-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 15px;
    border-bottom: 1px solid #f1f5f9;
}

.btn-back {
    border-radius: 8px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.simulation-toggle-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f1f5f9;
    padding: 4px 12px;
    border-radius: 20px;
    margin-right: 12px;
}

.sim-label {
    font-size: 12px;
    font-weight: 600;
    color: #475569;
}

.simulation-bar {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 20px;
    margin-top: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.sim-fields {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}

.sim-field {
    display: flex;
    align-items: center;
    gap: 8px;
}

.sim-field label {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    white-space: nowrap;
}

.sim-field .el-input-number {
    width: 80px;
}

.sim-field.char-field .el-input {
    width: 100px;
}

.sim-info {
    font-size: 12px;
    color: #64748b;
    display: flex;
    align-items: center;
    font-style: italic;
}

.step-badge {
    display: flex;
    flex-direction: column;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
    background: #FFFFFF;
    margin-top: 15px;
}

.bom-grid-row {
    display: grid;
    grid-template-columns: 1fr 140px 56px 40px 40px;
    align-items: start;
    gap: 12px;
    padding: 14px 16px;
    border-bottom: 1px solid #F1F5F9;
}

.bom-grid-row.header-row {
    background: #F8FAFC;
    border-bottom: 2px solid #E2E8F0;
    font-weight: 600;
    color: #475569;
    font-size: 13px;
    min-height: auto;
    padding: 12px 16px;
}

.bom-col-qty {
    display: flex;
    flex-direction: column;
}

.bom-uom {
    display: block;
    width: 100%;
    text-align: center;
    background: #F1F5F9;
    color: #64748B;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 0;
    border-radius: 6px;
    border: 1px solid #E2E8F0;
}

.bom-qty-helper {
    font-size: 10px;
    color: #94A3B8;
    font-weight: 500;
    margin-top: 4px;
    line-height: 1.2;
}

.calc-indicator-grid {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid #E2E8F0;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #94A3B8;
}

.calc-indicator-grid.active {
    background: #EEF2FF;
    color: #4F46E5;
    border-color: #C7D2FE;
}

.dim-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.dim-section {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
}

.dim-header-box {
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
    border-radius: 12px 12px 0 0;
}

.dim-title-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.dim-icon {
    background: #4f46e5;
    color: #ffffff;
    width: 20px;
    height: 20px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
}

.dim-title {
    font-weight: 700;
    font-size: 13px;
    color: #1e293b;
}

.dim-footer {
    padding: 12px 16px;
    background: #f8fafc;
    border-top: 1px solid #f1f5f9;
    border-radius: 0 0 12px 12px;
}

.config-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 8px;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.config-item.wide {
    grid-column: span 2;
}

.config-item label {
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
}

.step-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    background: #f0fdf4;
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid #bbf7d0;
}

.step-label {
    font-size: 10px;
    color: #166534;
}

.step-value {
    font-size: 11px;
    font-weight: 700;
    color: #15803d;
}

.step-unit {
    font-size: 9px;
    color: #15803d;
}

.warning-border :deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px #f59e0b inset !important;
}
</style>
