<template>
  <div class="smart-spec-container">
    <div v-if="!selectedSpec" class="specs-list">
      <div class="tab-header">
        <h3>Розумні специфікації (Параметричні)</h3>
        <p class="tab-subtitle">Розрахунок кількості матеріалів залежно від розмірів виробу</p>
      </div>
      
      <div v-if="specifications.length > 0">
        <el-table :data="specifications" v-loading="loading" stripe border class="mt-4">
          <el-table-column prop="name" label="Назва специфікації" min-width="200" />
          <el-table-column label="Статус" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.is_default" type="success" size="small">Основна</el-tag>
              <el-tag v-else type="info" size="small">Альтернативна</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="150" align="right">
            <template #default="scope">
              <el-button size="small" type="primary" plain @click="selectSpec(scope.row)">Налаштувати правила</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="mt-4">
        <el-empty 
          description="Немає збережених специфікацій. Створіть та збережіть специфікацію у вкладці 'Специфікації (BOM)', щоб налаштувати для неї розумні правила."
          :image-size="120"
        />
      </div>
    </div>

    <div v-else class="spec-rules-editor">
      <div class="tab-header">
        <div class="header-left">
          <el-button :icon="ArrowLeft" circle @click="selectedSpec = null" />
          <div>
            <h3>Правила для: {{ selectedSpec.name }}</h3>
            <p class="tab-subtitle">Налаштування математичних залежностей</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" :loading="saving" @click="saveRules">Зберегти всі правила</el-button>
        </div>
      </div>

      <el-card shadow="never" class="mt-4 dimension-preview">
        <div class="flex items-center gap-6">
          <div class="dim-item">
            <span class="dim-label">Висота (H):</span>
            <span class="dim-value">{{ productDimensions.height_cm || 0 }} см</span>
          </div>
          <div class="dim-item">
            <span class="dim-label">Ширина (W):</span>
            <span class="dim-value">{{ productDimensions.width_cm || 0 }} см</span>
          </div>
          <div class="dim-item">
            <span class="dim-label">Довжина (L):</span>
            <span class="dim-value">{{ productDimensions.length_cm || 0 }} см</span>
          </div>
          <div class="dim-item" v-if="productDimensions.weight_kg">
            <span class="dim-label">Вага (Kg):</span>
            <span class="dim-value">{{ productDimensions.weight_kg }} кг</span>
          </div>
          <div class="text-xs text-gray-400 ml-auto">
            * Фізичні параметри з вкладки "Загальна інформація"
          </div>
        </div>
      </el-card>

      <div class="rules-list mt-4">
        <el-collapse v-model="activeRuleNames">
          <el-collapse-item v-for="item in selectedSpec.items" :key="item.id" :name="item.id">
            <template #title>
              <div class="rule-header">
                <span class="comp-name">{{ item.component?.name || 'Компонент' }}</span>
                <span class="comp-sku text-gray-400">{{ item.component?.sku }}</span>
                <el-tag v-if="item.is_calculated" type="success" size="small" class="ml-2">
                  {{ getCalcTypeLabel(item.calc_type) }}
                </el-tag>
                <el-tag v-else type="info" size="small" class="ml-2">Фіксована к-сть: {{ item.quantity }} {{ item.unit_of_measure }}</el-tag>
                
                <span v-if="item.is_calculated" class="preview-result ml-auto mr-4">
                  Прогноз: <span class="calc-val">{{ calculateQuantity(item) }}</span> {{ item.unit_of_measure }}
                </span>
              </div>
            </template>

            <div class="rule-body">
              <el-form label-position="top">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="Тип калькулятора">
                      <el-select v-model="item.calc_type" class="w-full" @change="handleTypeChange(item)">
                        <el-option label="Фіксована кількість" value="fixed" />
                        <el-option label="Таблиця (Точки / Авто-пропорція)" value="interpolation" />
                        <el-option label="Пропорція (від розміру)" value="proportional" />
                        <el-option label="Площа (W * H)" value="area" />
                        <el-option label="Об'єм (W * H * L)" value="volume" />
                        <el-option label="Своя формула" value="formula" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="8" v-if="['interpolation', 'proportional'].includes(item.calc_type)">
                    <el-form-item label="Вимір для розрахунку">
                      <el-select v-model="item.calc_dimension" class="w-full">
                        <el-option label="Висота (H)" value="height_cm" />
                        <el-option label="Ширина (W)" value="width_cm" />
                        <el-option label="Довжина (L)" value="length_cm" />
                      </el-select>
                    </el-form-item>
                  </el-col>

                  <el-col :span="8">
                    <el-form-item label="Коефіцієнт відходів (%)">
                      <el-input-number v-model="item.calc_waste_factor" :precision="2" :step="0.01" :min="0" :max="1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- Interpolation Table -->
                <div v-if="item.calc_type === 'interpolation'" class="data-points-section mt-2">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-semibold">Точки розрахунку (Розмір -> Кількість)</span>
                    <el-button type="primary" size="small" @click="addPoint(item)" plain :icon="Plus">Додати точку</el-button>
                  </div>
                  <div class="text-xs text-gray-500 mb-2">
                    Введіть 2 або більше точок. Система автоматично вирахує математичну пропорцію (крок) для будь-яких інших розмірів, спираючись на ці дані.
                  </div>
                  <el-table :data="item.calc_data_points" size="small" border>
                    <el-table-column label="Значення виміру (см)" width="180">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.input" size="small" style="width: 100%" />
                      </template>
                    </el-table-column>
                    <el-table-column label="Потрібна кількість">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.output" :precision="4" size="small" style="width: 100%" />
                      </template>
                    </el-table-column>
                    <el-table-column width="60" align="center">
                      <template #default="scope">
                        <el-button type="danger" link :icon="Delete" @click="removePoint(item, scope.$index)" />
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <!-- Proportional Editor -->
                <el-row v-if="item.calc_type === 'proportional'" :gutter="20" class="mt-2">
                  <el-col :span="8">
                    <el-form-item label="Коефіцієнт (Множник)">
                      <el-input v-model="item.calc_formula" type="number" step="0.0001" placeholder="напр. 0.1" />
                      <div class="text-xs text-gray-400 mt-1">К-сть = Вимір × Коефіцієнт</div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- Formula Editor -->
                <el-row v-if="item.calc_type === 'formula'" :gutter="20" class="mt-2">
                  <el-col :span="24">
                    <el-form-item label="JS Формула (доступні змінні: H, W, L)">
                      <el-input v-model="item.calc_formula" placeholder="напр. (W * H) / 10000" />
                      <div class="text-xs text-gray-400 mt-1">Приклад: (W * H) / 10000 для м.кв.</div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- Formula Previews for Area/Volume -->
                <div v-if="['area', 'volume'].includes(item.calc_type)" class="mt-2 p-3 bg-blue-50 rounded text-sm text-blue-700">
                  <span v-if="item.calc_type === 'area'">Формула: Кількість = Ширина (W) * Висота (H) * (1 + відходи)</span>
                  <span v-if="item.calc_type === 'volume'">Формула: Кількість = W * H * L * (1 + відходи)</span>
                </div>
              </el-form>
              
              <div class="danger-zone mt-4" v-if="item.calc_type !== 'fixed'">
                 <el-button type="danger" size="small" plain @click="disableRule(item)">Вимкнути розрахунок</el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { getProductSpecifications, updateProductSpecification } from '@/api/specifications'

const props = defineProps({
  productId: { type: String, required: true },
  productDimensions: { type: Object, required: true }
})

const loading = ref(false)
const saving = ref(false)
const specifications = ref([])
const selectedSpec = ref(null)
const activeRuleNames = ref([])

const loadSpecifications = async () => {
  loading.value = true
  try {
    specifications.value = await getProductSpecifications(props.productId)
  } catch (e) {
    ElMessage.error('Помилка завантаження специфікацій')
  } finally {
    loading.value = false
  }
}

const selectSpec = (spec) => {
  selectedSpec.value = JSON.parse(JSON.stringify(spec))
  // Initialize calc_type if missing
  selectedSpec.value.items.forEach(item => {
    if (!item.calc_type) {
      item.calc_type = item.is_calculated ? 'interpolation' : 'fixed'
    }
  })
}

const handleTypeChange = (item) => {
  item.is_calculated = item.calc_type !== 'fixed'
  if (item.calc_type === 'interpolation' && !item.calc_data_points) {
    item.calc_data_points = []
    item.calc_dimension = 'width_cm'
  }
}

const getCalcTypeLabel = (type) => {
  const labels = {
    fixed: 'Фіксована',
    interpolation: 'Таблиця',
    proportional: 'Пропорція',
    area: 'Площа',
    volume: 'Об\'єм',
    formula: 'Формула'
  }
  return labels[type] || 'Розумний розрахунок'
}

const addPoint = (item) => {
  if (!item.calc_data_points) item.calc_data_points = []
  item.calc_data_points.push({ input: 0, output: 0 })
  item.calc_data_points.sort((a, b) => a.input - b.input)
}

const removePoint = (item, index) => {
  item.calc_data_points.splice(index, 1)
}

const disableRule = (item) => {
  item.calc_type = 'fixed'
  item.is_calculated = false
}

const calculateQuantity = (item) => {
  if (!item.is_calculated) return item.quantity

  const dimensions = {
    W: parseFloat(props.productDimensions.width_cm) || 0,
    H: parseFloat(props.productDimensions.height_cm) || 0,
    L: parseFloat(props.productDimensions.length_cm) || 0,
    Kg: parseFloat(props.productDimensions.weight_kg) || 0
  }

  let result = 0

  if (item.calc_type === 'interpolation') {
    if (!item.calc_data_points || item.calc_data_points.length === 0) return item.quantity
    
    // Get actual dimension key (width_cm, height_cm, length_cm)
    const dimVal = parseFloat(props.productDimensions[item.calc_dimension]) || 0
    const points = [...item.calc_data_points].sort((a, b) => a.input - b.input)
    
    if (points.length === 1) {
      result = points[0].output
    } else {
      if (dimVal <= points[0].input) {
        const p1 = points[0]; const p2 = points[1]
        const slope = (p2.input !== p1.input) ? (p2.output - p1.output) / (p2.input - p1.input) : 0
        result = p1.output + slope * (dimVal - p1.input)
      } 
      else if (dimVal >= points[points.length - 1].input) {
        const p1 = points[points.length - 2]; const p2 = points[points.length - 1]
        const slope = (p2.input !== p1.input) ? (p2.output - p1.output) / (p2.input - p1.input) : 0
        result = p2.output + slope * (dimVal - p2.input)
      } 
      else {
        for (let i = 0; i < points.length - 1; i++) {
          const p1 = points[i]; const p2 = points[i+1]
          if (dimVal >= p1.input && dimVal <= p2.input) {
            const slope = (p2.input !== p1.input) ? (p2.output - p1.output) / (p2.input - p1.input) : 0
            result = p1.output + slope * (dimVal - p1.input)
            break
          }
        }
      }
    }
    // Dont allow negative quantities resulting from negative extrapolation
    result = Math.max(0, result)
  } 
  else if (item.calc_type === 'proportional') {
    const dimVal = parseFloat(props.productDimensions[item.calc_dimension]) || 0
    const coeff = parseFloat(item.calc_formula) || 0
    result = dimVal * coeff
  }
  else if (item.calc_type === 'area') {
    result = dimensions.W * dimensions.H / 10000 // default as assuming cm and wanting m2 
  }
  else if (item.calc_type === 'volume') {
    result = dimensions.W * dimensions.H * dimensions.L / 1000000 // m3
  }
  else if (item.calc_type === 'formula') {
    try {
      // Safe local variables for formula
      const { W, H, L, Kg } = dimensions
      result = eval(item.calc_formula)
    } catch (e) {
      return 'Помилка формули'
    }
  }

  // Apply waste factor
  if (item.calc_waste_factor) {
    result *= (1 + parseFloat(item.calc_waste_factor))
  }
  
  return typeof result === 'number' ? result.toFixed(4) : result
}

const saveRules = async () => {
  saving.value = true
  try {
    await updateProductSpecification(selectedSpec.value.id, selectedSpec.value)
    ElMessage.success('Правила успішно збережено')
    await loadSpecifications()
    selectedSpec.value = null
  } catch (e) {
    ElMessage.error('Помилка збереження правил')
  } finally {
    saving.value = false
  }
}

onMounted(loadSpecifications)
</script>

<style scoped>
.smart-spec-container {
  padding: 10px 24px 24px 24px;
}

.tab-header {
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tab-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.tab-subtitle {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #64748b;
}

.dimension-preview {
  background: #f8fafc;
  border-radius: 12px;
}

.dim-item {
  display: flex;
  flex-direction: column;
}

.dim-label {
  font-size: 11px;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.dim-value {
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}

.rule-header {
  display: flex;
  align-items: center;
  width: 100%;
}

.comp-name {
  font-weight: 600;
  color: #1e293b;
  margin-right: 8px;
}

.comp-sku {
  font-size: 12px;
}

.preview-result {
  font-size: 13px;
  color: #64748b;
}

.calc-val {
  font-weight: 700;
  color: #6366f1;
}

.rule-body {
  padding: 10px 0;
}

.w-full { width: 100%; }
.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-auto { margin-left: auto; }
.mr-4 { margin-right: 1rem; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-6 { gap: 1.5rem; }

.danger-zone {
  border-top: 1px solid #fee2e2;
  padding-top: 12px;
}

.bg-blue-50 { background-color: #eff6ff; }
.p-3 { padding: 0.75rem; }
.rounded { border-radius: 0.375rem; }
.text-sm { font-size: 0.875rem; }
.text-blue-700 { color: #1d4ed8; }
.text-xs { font-size: 0.75rem; }
.text-gray-400 { color: #9ca3af; }
.mt-1 { margin-top: 0.25rem; }
</style>
