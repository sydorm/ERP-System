<template>
  <div class="erp-page-container">
    <!-- Header fields -->
    <div class="erp-toolbar">
      <div class="toolbar-left">
        <el-button @click="goBack" :icon="ArrowLeft" circle />
        <h1 class="page-title">
          {{ isEditMode ? `Завдання на виробництво ${form.order_number}` : 'Нове завдання на виробництво' }}
        </h1>
        <el-tag
          v-if="form.status"
          :type="statusType"
          style="margin-left: 12px; font-weight: 600;"
          effect="dark"
        >{{ statusLabel }}</el-tag>
      </div>
      <div class="toolbar-right">
        <el-button @click="saveOrder('draft')" :disabled="submitting">Записати</el-button>
        <el-button type="success" @click="saveOrder('released')" :disabled="submitting || form.status !== 'draft'">Передати в роботу</el-button>
        <el-button type="primary" @click="saveOrder('completed')" :disabled="submitting || !['draft', 'released', 'in_progress'].includes(form.status)">Оприбуткувати / Завершити</el-button>
      </div>
    </div>

    <div class="erp-header-fields">
      <div class="fields-grid-3">
        <!-- Number & Date -->
        <div class="field-block">
          <span class="field-label">Номер / Дата</span>
          <div style="display: flex; gap: 8px;">
            <el-input v-model="form.order_number" disabled placeholder="Автоматично" style="width: 120px;" />
            <el-date-picker
              v-model="form.order_date"
              type="datetime"
              format="DD.MM.YYYY HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Дата"
              style="flex: 1;"
            />
          </div>
        </div>
        
        <!-- Warehouse (Optional for where products go / where materials are taken) -->
        <div class="field-block">
          <span class="field-label">Склад виробництва</span>
          <el-select v-model="form.warehouse_id" placeholder="Оберіть склад" class="w-full">
            <el-option
              v-for="wh in warehouses"
              :key="wh.id"
              :label="wh.name"
              :value="wh.id"
            />
          </el-select>
        </div>
        
        <!-- Due Date -->
        <div class="field-block">
          <span class="field-label">Завершити до</span>
          <el-date-picker
            v-model="form.due_date"
            type="date"
            format="DD.MM.YYYY"
            value-format="YYYY-MM-DD"
            placeholder="Термін виконання"
            class="w-full"
          />
        </div>
      </div>
      
      <div class="field-block mt-4" style="max-width: 600px;">
        <span class="field-label">Підстава</span>
        <div class="flex items-center gap-2">
           <el-input v-model="form.base_order_id" disabled placeholder="Створено вручну" />
        </div>
      </div>
    </div>

    <!-- Tabs Content -->
    <div class="erp-main-content">
      <el-tabs v-model="activeTab" class="erp-tabs" style="flex: 1; display:flex; flex-direction:column;">
        
        <!-- PRODUCTS TO PRODUCE -->
        <el-tab-pane name="products">
          <template #label><el-icon><Box /></el-icon>&nbsp;Продукція <el-badge v-if="form.lines.length" :value="form.lines.length" class="tab-badge" /></template>
          
          <div class="tab-content-card">
            <div class="actions-bar mb-3">
              <el-button type="primary" :icon="Plus" size="small" @click="addLine">Додати продукцію</el-button>
              <el-button :icon="Refresh" size="small" @click="recalculateMaterials">Оновити матеріали (BOM)</el-button>
            </div>
            
            <el-table :data="form.lines" border size="small" class="erp-dense-table">
              <el-table-column label="N" width="50" type="index" align="center" />
              
              <el-table-column label="Продукція" min-width="250">
                <template #default="scope">
                  <el-select
                    v-model="scope.row.product_id"
                    filterable
                    placeholder="Оберіть товар..."
                    class="erp-cell-input"
                    style="width: 100%"
                    @change="handleProductChange($event, scope.row)"
                  >
                    <el-option
                      v-for="p in products"
                      :key="p.id"
                      :label="p.name"
                      :value="p.id"
                    >
                      <span style="float: left">{{ p.name }}</span>
                      <span style="float: right; color: #8492a6; font-size: 12px">{{ p.sku }}</span>
                    </el-option>
                  </el-select>
                </template>
              </el-table-column>
              
              <el-table-column label="Характеристика" min-width="150">
                <template #default="scope">
                   <span v-if="hasVariants(scope.row.product_id)" class="text-xs text-gray-500 cursor-pointer" @click="openVariantSelector(scope.row)">
                     {{ getVariantLabel(scope.row) || 'Не обрано' }}
                   </span>
                   <span v-else class="text-gray-300 text-xs">-</span>
                </template>
              </el-table-column>
              
              <el-table-column label="Специфікація" min-width="150">
                <template #default="scope">
                  <el-select
                    v-model="scope.row.specification_id"
                    size="small"
                    placeholder="За замовчуванням"
                    clearable
                    class="erp-cell-input"
                    style="width: 100%"
                    @change="recalculateMaterials"
                  >
                     <el-option
                       v-for="spec in getSpecsForProduct(scope.row.product_id)"
                       :key="spec.id"
                       :label="spec.name + (spec.is_default ? ' (Авто)' : '')"
                       :value="spec.id"
                     />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column label="К-ть" width="100">
                <template #default="scope">
                  <el-input-number
                    v-model="scope.row.quantity"
                    :min="0.001"
                    :step="1"
                    size="small"
                    class="erp-cell-input w-full"
                    :controls="false"
                    @change="recalculateMaterials"
                  />
                </template>
              </el-table-column>
              
              <el-table-column label="" width="50" align="center">
                <template #default="scope">
                  <el-button type="danger" :icon="Delete" circle plain size="small" @click="removeLine(scope.$index)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- MATERIALS (BOM) -->
        <el-tab-pane name="materials">
          <template #label><el-icon><List /></el-icon>&nbsp;Матеріали <el-badge v-if="form.materials.length" :value="form.materials.length" class="tab-badge" type="warning"/></template>
          
          <div class="tab-content-card">
            <div class="actions-bar mb-3">
              <span class="text-sm text-gray-500 mr-4">Сформовано на основі специфікацій продукції. Ви можете редагувати вручну.</span>
              <el-button type="success" :icon="Plus" size="small" plain @click="addMaterial">Додати матеріал вручну</el-button>
            </div>
            
            <el-table :data="form.materials" border size="small" class="erp-dense-table" stripe>
              <el-table-column label="N" width="50" type="index" align="center" />
              
              <el-table-column label="Матеріал / Компонент" min-width="250">
                <template #default="scope">
                  <el-select
                    v-model="scope.row.component_id"
                    filterable
                    placeholder="Оберіть компонент..."
                    class="erp-cell-input"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="p in products"
                      :key="p.id"
                      :label="p.name"
                      :value="p.id"
                    />
                  </el-select>
                </template>
              </el-table-column>
              
              <el-table-column label="Од. вим." width="80">
                <template #default="scope">
                   <el-input v-model="scope.row.unit_of_measure" size="small" class="erp-cell-input" />
                </template>
              </el-table-column>
              
              <el-table-column label="Потрібно" width="120" align="right">
                <template #default="scope">
                  <el-input-number
                    v-model="scope.row.required_quantity"
                    :min="0"
                    :step="0.1"
                    size="small"
                    class="erp-cell-input w-full"
                    :controls="false"
                  />
                </template>
              </el-table-column>

              <el-table-column label="" width="50" align="center">
                <template #default="scope">
                  <el-button type="danger" :icon="Delete" circle plain size="small" @click="removeMaterial(scope.$index)" />
                </template>
              </el-table-column>
            </el-table>
            
            <div class="mt-4 p-4 bg-yellow-50 text-yellow-800 text-sm rounded-md border border-yellow-200">
              Матеріали будуть автоматично списані зі складу після натискання «Оприбуткувати / Завершити».
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Refresh, Box, List, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const isEditMode = computed(() => !!route.params.id)

const activeTab = ref('products')
const submitting = ref(false)

const products = ref([])
const warehouses = ref([])
const specsCache = ref({}) // product_id -> specs[]

const form = ref({
  order_number: '',
  order_date: new Date().toISOString().substring(0, 19),
  due_date: null,
  status: 'draft',
  base_order_id: null,
  company_id: '',
  warehouse_id: '',
  comment: '',
  lines: [],
  materials: []
})

// --- Data loading ---
const fetchStaticData = async () => {
  try {
    const [prodRes, whRes, compRes] = await Promise.all([
      api.get('/api/v1/products?limit=1000'),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/companies')
    ])
    products.value = prodRes.data
    warehouses.value = whRes.data
    
    if (!isEditMode.value) {
      if (whRes.data.length > 0) form.value.warehouse_id = whRes.data[0].id
      if (compRes.data.length > 0) form.value.company_id = compRes.data[0].id
      
      // If we are passing components from query (created from Order base)
      const qBase = route.query.base_order
      if (qBase) {
        form.value.base_order_id = qBase
        // We'd ideally fetch the base order and populate lines, but for now just linked.
        try {
            const bRes = await api.get(`/api/v1/orders/${qBase}`)
            form.value.lines = bRes.data.lines.map(l => ({
                product_id: l.product_id,
                variant_id: l.variant_id,
                specification_id: l.specification_id,
                quantity: l.quantity,
                produced_quantity: 0
            }))
            // trigger recalculation!
            recalculateMaterials()
        } catch(e) {}
      }
    }
  } catch (e) {
    ElMessage.error('Помилка завантаження довідників')
  }
}

const loadOrder = async () => {
  try {
    const { data } = await api.get(`/api/v1/production/${route.params.id}`)
    
    // Ensure specs are loaded for products inside
    const uniqueIds = [...new Set(data.lines.map(l => l.product_id).filter(Boolean))]
    await Promise.all(uniqueIds.map(async pid => {
        if (!specsCache.value[pid]) {
            try {
                const s = await api.get(`/api/v1/specifications/product/${pid}`)
                specsCache.value[pid] = s.data
            } catch(e) {}
        }
    }))
    
    Object.assign(form.value, data)
  } catch (err) {
    ElMessage.error('Помилка завантаження документа')
  }
}

// --- Specification logic (similar to OrderEditor) ---
const getProductSpecifications = async (productId) => {
  const { data } = await api.get(`/api/v1/specifications/product/${productId}`)
  return data
}

const getSpecsForProduct = (pid) => specsCache.value[pid] || []

const handleProductChange = async (productId, line) => {
  if (productId && !specsCache.value[productId]) {
      try {
        const specs = await getProductSpecifications(productId)
        specsCache.value[productId] = specs
      } catch (e) {
        console.error('Failed to load spec for', productId)
      }
      
      const cached = specsCache.value[productId]
      if (cached && cached.length) {
          const defaultSpec = cached.find(s => s.is_default) || cached[0]
          line.specification_id = defaultSpec.id
      }
      recalculateMaterials()
  }
}

// Helper calculation engine exactly from OrderEditor
const calculateQuantity = (item, product, variantValues = []) => {
  let result = 0
  const dims = { W: 0, H: 0, L: 0, Kg: 0 }
  
  if (variantValues && variantValues.length) {
    variantValues.forEach(val => {
       if (val.dimension_code === 'width_cm') dims.W = parseFloat(val.custom_value || val.value?.value || 0)
       if (val.dimension_code === 'height_cm') dims.H = parseFloat(val.custom_value || val.value?.value || 0)
       if (val.dimension_code === 'length_cm') dims.L = parseFloat(val.custom_value || val.value?.value || 0)
       if (val.dimension_code === 'weight_kg') dims.Kg = parseFloat(val.custom_value || val.value?.value || 0)
    })
  }

  if (item.calc_type === 'fixed') {
    result = item.quantity
  }
  else if (item.calc_type === 'stepped' && item.step_rules && item.step_rules.length > 0) {
    const dimVal = dims[item.calc_dimension === 'width_cm' ? 'W' : (item.calc_dimension === 'height_cm' ? 'H' : 'L')] || 0
    let applicableRule = null
    for (const rule of item.step_rules) {
      if (dimVal >= rule.min_val && dimVal <= rule.max_val) {
        applicableRule = rule
        break
      }
    }
    result = applicableRule ? applicableRule.qty : item.quantity
  }
  else if (item.calc_type === 'table_xy' && item.xy_rules && item.xy_rules.length > 0) {
    let dimX, dimY
    if (item.calc_dimension === 'width_cm:height_cm') { dimX = dims.W; dimY = dims.H }
    else { dimX = dims.W; dimY = dims.H }
    let applicableRule = null
    for (const rule of item.xy_rules) {
       if (dimX >= rule.x_min && dimX <= rule.x_max && dimY >= rule.y_min && dimY <= rule.y_max) {
           applicableRule = rule; break
       }
    }
    result = applicableRule ? applicableRule.qty : item.quantity
  }
  else if (item.calc_type === 'formula') {
    try {
      const { W, H, L, Kg } = dims
      result = eval(item.calc_formula)
    } catch (e) { result = 0 }
  } else {
      result = item.quantity
  }

  if (item.calc_waste_factor) {
    result *= (1 + parseFloat(item.calc_waste_factor))
  }
  return result
}

const recalculateMaterials = () => {
    const bom = []
    
    form.value.lines.forEach(line => {
        if (!line.product_id || !line.quantity) return
        const specs = specsCache.value[line.product_id] || []
        if (!specs.length) return
        
        const spec = line.specification_id ? specs.find(s => s.id === line.specification_id) : (specs.find(s => s.is_default) || specs[0])
        if (!spec || !spec.items) return
        
        const product = products.value.find(p => p.id === line.product_id)
        
        spec.items.forEach(item => {
            const qtyPerUnit = parseFloat(calculateQuantity(item, product, [])) || 0
            if (qtyPerUnit <= 0) return
            
            const totalQty = qtyPerUnit * line.quantity
            const existing = bom.find(b => b.component_id === item.component_id)
            
            if (existing) {
                existing.required_quantity += totalQty
            } else {
                bom.push({
                    component_id: item.component_id,
                    required_quantity: totalQty,
                    unit_of_measure: item.unit_of_measure || 'шт',
                    cost_estimate: 0
                })
            }
        })
    })
    
    // Replace current materials entirely. In a real system you might merge with manual edits.
    form.value.materials = bom
    ElMessage.success('Матеріали перераховано згідно специфікацій.')
}

const goBack = () => router.push('/production/orders')

// --- Lines Logic ---
const addLine = () => form.value.lines.push({ product_id: '', quantity: 1, specification_id: null })
const removeLine = (idx) => { form.value.lines.splice(idx, 1); recalculateMaterials() }
const addMaterial = () => form.value.materials.push({ component_id: '', required_quantity: 1, unit_of_measure: 'шт' })
const removeMaterial = (idx) => form.value.materials.splice(idx, 1)

// --- Saving ---
const saveOrder = async (actionStatus) => {
    if (!form.value.warehouse_id || !form.value.company_id || form.value.lines.length === 0) {
        ElMessage.warning('Заповніть Склад та додайте Продукцію')
        return
    }
    
    if (actionStatus) form.value.status = actionStatus
    
    const payload = { ...form.value }
    
    submitting.value = true
    try {
        if (isEditMode.value) {
            await api.put(`/api/v1/production/${route.params.id}`, payload)
            ElMessage.success('Збережено')
        } else {
            const res = await api.post('/api/v1/production/', payload)
            ElMessage.success('Створено')
            router.push(`/production/orders/${res.data.id}`)
            return // skip reload to avoid state flashing
        }
        await loadOrder()
    } catch(err) {
        ElMessage.error(err.response?.data?.detail || 'Помилка збереження')
    } finally {
        submitting.value = false
    }
}

const hasVariants = (pid) => {
    const p = products.value.find(x => x.id === pid)
    return p && p.variants && p.variants.length > 0
}
const getVariantLabel = (line) => {
    if (!line.variant_id) return ''
    const p = products.value.find(x => x.id === line.product_id)
    if (!p || !p.variants) return ''
    const v = p.variants.find(x => x.id === line.variant_id)
    return v ? (v.name || v.sku) : ''
}
const openVariantSelector = () => ElMessage.info('Вибір характеристик реалізовано тільки в Замовленні покупця наразі.')

// Status configs
const statusLabel = computed(() => {
    const s = form.value.status
    if (s === 'draft') return 'Чернетка'
    if (s === 'released') return 'В роботу'
    if (s === 'in_progress') return 'В процесі'
    if (s === 'completed') return 'Завершено (Оприбутковано)'
    if (s === 'cancelled') return 'Скасовано'
    return s
})

const statusType = computed(() => {
    const s = form.value.status
    if (s === 'draft') return 'info'
    if (s === 'released') return 'primary'
    if (s === 'in_progress') return 'warning'
    if (s === 'completed') return 'success'
    if (s === 'cancelled') return 'danger'
    return ''
})

onMounted(async () => {
  await fetchStaticData()
  if (isEditMode.value) {
    await loadOrder()
  }
})
</script>

<style scoped>
.fields-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.field-block { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 12px; color: #606266; font-weight: 500; }
</style>
