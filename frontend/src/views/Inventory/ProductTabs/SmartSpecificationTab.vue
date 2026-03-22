<template>
  <div class="smart-spec-container">
    <div v-if="!selectedSpec" class="specs-list">
      <div class="tab-header">
        <h3>Розумні специфікації (Параметричні)</h3>
        <p class="tab-subtitle">Розрахунок кількості матеріалів залежно від розмірів виробу</p>
      </div>
      
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
            <span class="dim-value">{{ productDimensions.length_cm }} см</span>
          </div>
          <div class="dim-item">
            <span class="dim-label">Ширина (W):</span>
            <span class="dim-value">{{ productDimensions.width_cm }} см</span>
          </div>
          <div class="dim-item">
            <span class="dim-label">Довжина (L):</span>
            <span class="dim-value">{{ productDimensions.weight_kg }} см</span>
          </div>
          <div class="text-xs text-gray-400">
            * Використовуються фізичні параметри з вкладки "Загальна інформація"
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
                <el-tag v-if="item.is_calculated" type="success" size="small" class="ml-2">Розумний розрахунок</el-tag>
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
                    <el-form-item label="Вимір для розрахунку">
                      <el-select v-model="item.calc_dimension" class="w-full" @change="item.is_calculated = !!item.calc_dimension">
                        <el-option label="Висота (H)" value="height_cm" />
                        <el-option label="Ширина (W)" value="width_cm" />
                        <el-option label="Довжина (L)" value="length_cm" />
                        <el-option label="Своя формула" value="custom" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="Коефіцієнт відходів (%)">
                      <el-input-number v-model="item.calc_waste_factor" :precision="2" :step="0.01" :min="0" :max="1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8" v-if="item.calc_dimension === 'custom'">
                    <el-form-item label="Формула (JS синтаксис)">
                      <el-input v-model="item.calc_formula" placeholder="напр. (h * w) / 100" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="data-points-section mt-2">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-semibold">Точки розрахунку (Таблиця залежностей)</span>
                    <el-button type="primary" size="small" @click="addPoint(item)" plain :icon="Plus">Додати точку</el-button>
                  </div>
                  
                  <el-table :data="item.calc_data_points" size="small" border>
                    <el-table-column label="Значення виміру (см)" width="180">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.input" size="small" style="width: 100%" />
                      </template>
                    </el-table-column>
                    <el-table-column label="Потрібна кількість матеріалу">
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
                  
                  <div class="text-xs text-gray-400 mt-2">
                    * Система використовує лінійну інтерполяцію між найближчими точками.
                  </div>
                </div>
              </el-form>
              
              <div class="danger-zone mt-4" v-if="item.is_calculated">
                 <el-button type="danger" size="small" plain @click="disableRule(item)">Вимкнути розумний розрахунок</el-button>
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
}

const getRule = (item) => {
  if (!item.calc_data_points) {
    item.calc_data_points = []
    item.calc_waste_factor = 0
    item.is_calculated = false
  }
  return item
}

const addPoint = (item) => {
  if (!item.calc_data_points) item.calc_data_points = []
  item.calc_data_points.push({ input: 0, output: 0 })
  item.calc_data_points.sort((a, b) => a.input - b.input)
  item.is_calculated = true
}

const removePoint = (item, index) => {
  item.calc_data_points.splice(index, 1)
  if (item.calc_data_points.length === 0) item.is_calculated = false
}

const disableRule = (item) => {
  item.is_calculated = false
  item.calc_dimension = null
}

const calculateQuantity = (item) => {
  if (!item.is_calculated || !item.calc_data_points || item.calc_data_points.length === 0) return item.quantity

  // Get current dimension value
  let inputValue = 0
  if (item.calc_dimension === 'height_cm') inputValue = props.productDimensions.length_cm // Using actual field mapping from backend
  else if (item.calc_dimension === 'width_cm') inputValue = props.productDimensions.width_cm
  else if (item.calc_dimension === 'length_cm') inputValue = props.productDimensions.weight_kg // Dimensions fields in model are a bit mixed?
  
  // Sorting for safety
  const points = [...item.calc_data_points].sort((a, b) => a.input - b.input)
  
  if (inputValue <= points[0].input) return points[0].output
  if (inputValue >= points[points.length - 1].input) return points[points.length - 1].output
  
  // Interpolation
  for (let i = 0; i < points.length - 1; i++) {
    const p1 = points[i]
    const p2 = points[i+1]
    if (inputValue >= p1.input && inputValue <= p2.input) {
      const ratio = (inputValue - p1.input) / (p2.input - p1.input)
      let quantity = p1.output + ratio * (p2.output - p1.output)
      
      // Add waste factor
      if (item.calc_waste_factor) {
        quantity *= (1 + item.calc_waste_factor)
      }
      
      return quantity.toFixed(4)
    }
  }
  
  return item.quantity
}

const saveRules = async () => {
  saving.value = true
  try {
    // We send the whole spec update to backend
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
</style>
