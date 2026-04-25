<template>
  <div class="characteristics-tab-content" v-loading="loading">
    <div class="section-header">
      <div class="section-divider">Технічні характеристики</div>
      <el-button 
        type="primary" 
        :icon="Plus" 
        size="small" 
        class="kimi-btn-primary"
        @click="addCharacteristic" 
        :disabled="availableAttributesForAdd.length === 0"
      >
        Додати характеристику
      </el-button>
    </div>

    <div v-if="localCharacteristics.length === 0" class="empty-state">
      <el-empty description="Характеристики ще не задані" :image-size="100">
        <template #extra>
          <el-button 
            type="primary" 
            plain 
            class="kimi-btn-outline"
            @click="addCharacteristic" 
            :disabled="availableAttributesForAdd.length === 0"
          >
            Обрати із випадаючого списку
          </el-button>
        </template>
      </el-empty>
    </div>

    <div v-else class="char-list">
      <div v-for="(char, index) in localCharacteristics" :key="index" class="char-row-premium">
        <div class="char-main">
          <div class="attr-icon-box">
            <el-icon><Operation /></el-icon>
          </div>
          <div class="attr-content">
            <div class="attr-header">
              <span class="attr-name">{{ getAttributeName(char.attribute_id) }}</span>
              <el-tag v-if="char.is_fixed" size="small" type="warning" effect="light" round class="fixed-tag">
                Обов'язкова
              </el-tag>
            </div>
            <div class="attr-meta">
              <span class="type-badge">{{ typeLabel(getAttrType(char)) }}</span>
              
              <!-- Compact Values Display (Tags) -->
              <div class="values-row">
                <!-- Pre-defined option tag -->
                <el-tag 
                  v-if="char.option_id" 
                  closable 
                  size="small" 
                  type="success" 
                  effect="plain"
                  @close="clearValue(char)"
                >
                  {{ getOptionValue(char.option_id) }}
                </el-tag>

                <!-- Text/Dimensions manual tag -->
                <el-tag 
                  v-if="char.text_value && !char.option_id" 
                  closable 
                  size="small" 
                  type="info" 
                  effect="plain"
                  @close="char.text_value = ''; emitUpdate()"
                >
                  {{ formatDisplayValue(char) }}
                </el-tag>

                <!-- Empty state hint -->
                <span v-if="!char.option_id && !char.text_value && !char.bool_value" class="empty-val-hint">
                  значення не задано
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="char-sku-toggle">
          <span class="toggle-label">Генерує SKU</span>
          <el-switch
            :model-value="getGeneratesSku(char.attribute_id)"
            @update:model-value="val => setGeneratesSku(char.attribute_id, val)"
            active-color="#6366f1"
            size="small"
          />
        </div>
        
        <div class="char-controls">
          <el-button 
            v-if="['SELECT', 'COLOR', 'DIMENSIONS'].includes(getAttrType(char))"
            :icon="Plus" 
            circle
            size="small"
            class="kimi-btn-icon"
            @click="openAddOptionDialog(char.attribute_id)"
            title="Додати значення"
          />

          <el-button 
            v-if="!char.is_fixed" 
            :icon="Delete" 
            circle
            size="small"
            class="kimi-btn-delete"
            @click="removeCharacteristic(index)" 
            title="Видалити"
          />
          <div v-else style="width: 32px"></div>
        </div>
      </div>
    </div>

    <!-- Add Option Dialog -->
    <el-dialog
      v-model="addOptionVisible"
      title="Додати нове значення"
      width="400px"
      class="kimi-dialog"
      append-to-body
      destroy-on-close
    >
      <el-form label-position="top" class="dialog-form">
        <el-form-item v-if="selectedAttrType !== 'DIMENSIONS'" label="Значення">
          <el-input v-model="newOption.value" placeholder="Наприклад: Червоний, 1000мм..." class="styled-input" />
        </el-form-item>
        <el-form-item v-else label="Розміри (Ш × В, мм)">
          <div class="color-picker-row">
            <el-input-number v-model="newOption.w" :min="0" :precision="0" :controls="false" placeholder="Ширина" />
            <span class="dims-sep">×</span>
            <el-input-number v-model="newOption.h" :min="0" :precision="0" :controls="false" placeholder="Висота" />
          </div>
        </el-form-item>
        <el-form-item v-if="selectedAttrType === 'COLOR'" label="Код кольору">
          <div class="color-picker-row">
            <el-color-picker v-model="newOption.color_code" />
            <el-input v-model="newOption.color_code" placeholder="#HEX" class="styled-input" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addOptionVisible = false" class="btn-cancel">Скасувати</el-button>
          <el-button type="primary" :loading="savingOption" @click="saveNewOption" :disabled="!newOption.value" class="btn-save">
            Зберегти
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>


<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue'
import { Plus, Delete, Operation } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  productId: { type: String, default: null },
  categoryCode: { type: String, default: '' },
  modelValue: { type: Array, default: () => [] },
  productAttributes: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:characteristics', 'update:modelValue', 'update:productAttributes'])

// All attributes from backend (loaded once, shared)
const allAttributes = ref([])
const categoryAttributes = ref([]) // Attributes linked to currently selected category
const loading = ref(false)

// Local characteristics (attribute_id -> value mapping)
const localCharacteristics = ref([])

// Sync props.modelValue to local state
watch(() => props.modelValue, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(localCharacteristics.value)) {
    localCharacteristics.value = [...newVal]
  }
}, { immediate: true, deep: true })

// Computed: attributes already used in the current list
const usedAttributeIds = computed(() => localCharacteristics.value.map(c => c.attribute_id).filter(Boolean))

// Attributes available for a new row (not already used) AND matching current category or global
const availableAttributesForAdd = computed(() => {
  return allAttributes.value.filter(a => {
    // Already added? Skip
    if (usedAttributeIds.value.includes(a.id)) return false
    
    // If it has no specific categories, it's global -> keep
    if (!a.category_codes || a.category_codes.length === 0) return true
    
    // If it has specific categories, check if our current category matches
    return a.category_codes.includes(props.categoryCode)
  })
})

// For a specific row – show its own attribute + available ones
const getAvailableForRow = (char) => {
  return allAttributes.value.filter(a => {
    if (a.id === char.attribute_id) return true
    if (usedAttributeIds.value.includes(a.id)) return false
    if (!a.category_codes || a.category_codes.length === 0) return true
    return a.category_codes.includes(props.categoryCode)
  })
}

const getAttributeName = (attrId) => {
  const attr = allAttributes.value.find(a => a.id === attrId)
  return attr?.name || 'Характеристика'
}

const getAttrType = (char) => {
  const attr = allAttributes.value.find(a => a.id === char.attribute_id)
  return attr?.type || 'TEXT'
}

// Add Option Dialog Logic
const addOptionVisible = ref(false)
const savingOption = ref(false)
const selectedAttrForOption = ref(null)
const selectedAttrType = ref('SELECT')
const newOption = reactive({
  value: '',
  color_code: '',
  w: null,
  h: null
})

const openAddOptionDialog = (attrId) => {
  const attr = allAttributes.value.find(a => a.id === attrId)
  if (!attr) return
  
  selectedAttrForOption.value = attrId
  selectedAttrType.value = attr.type
  newOption.value = ''
  newOption.w = null
  newOption.h = null
  newOption.color_code = attr.type === 'COLOR' ? '#000000' : ''
  addOptionVisible.value = true
}

const saveNewOption = async () => {
  if (!selectedAttrForOption.value) return
  
  if (selectedAttrType.value === 'DIMENSIONS') {
    if (!newOption.w || !newOption.h) {
      ElMessage.warning('Вкажіть ширину та висоту')
      return
    }
    const attr = allAttributes.value.find(a => a.id === selectedAttrForOption.value)
    const fmt = attr?.dimension_format || '{width}×{height}'
    newOption.value = fmt.replace('{width}', newOption.w).replace('{height}', newOption.h)
  }

  if (!newOption.value) return
  
  savingOption.value = true
  try {
    const payload = {
      value: newOption.value,
      color_code: newOption.color_code || null
    }
    if (selectedAttrType.value === 'DIMENSIONS') {
      payload.width = newOption.w
      payload.height = newOption.h
    }
    
    const res = await api.post(`/api/v1/attributes/${selectedAttrForOption.value}/options`, payload)
    
    // Refresh the specific attribute in our list
    const attr = allAttributes.value.find(a => a.id === selectedAttrForOption.value)
    if (attr) {
      if (!attr.options) attr.options = []
      attr.options.push(res.data)
    }
    
    ElMessage.success('Значення додано')
    addOptionVisible.value = false
  } catch (e) {
    console.error('Failed to add option', e)
    ElMessage.error(e.response?.data?.detail || 'Помилка додавання')
  } finally {
    savingOption.value = false
  }
}

const getAttrOptions = (char) => {
  const attr = allAttributes.value.find(a => a.id === char.attribute_id)
  return attr?.options || []
}

const typeLabel = (type) => {
  const map = { TEXT: 'Текст', SELECT: 'Список', NUMBER: 'Число', COLOR: 'Колір', BOOLEAN: 'Так/Ні', DIMENSIONS: 'Розміри' }
  return map[type] || type
}

const getDimW = (char) => {
  const parts = (char.text_value || '').split('x')
  return parts[0] ? Number(parts[0]) : null
}
const getDimH = (char) => {
  const parts = (char.text_value || '').split('x')
  return parts[1] ? Number(parts[1]) : null
}
const setDimW = (char, val) => {
  const h = getDimH(char) ?? ''
  char.text_value = `${val ?? ''}x${h}`
  emitUpdate()
}
const setDimH = (char, val) => {
  const w = getDimW(char) ?? ''
  char.text_value = `${w}x${val ?? ''}`
  emitUpdate()
}

const onOptionChange = (char) => {
  if (char.option_id && getAttrType(char) === 'DIMENSIONS') {
    const opt = getAttrOptions(char).find(o => o.id === char.option_id)
    if (opt && opt.width && opt.height) {
      char.text_value = `${opt.width}x${opt.height}`
    }
  }
  emitUpdate()
}

const getOptionValue = (optionId) => {
  for (const attr of allAttributes.value) {
    if (attr.options) {
      const opt = attr.options.find(o => o.id === optionId)
      if (opt) return opt.value
    }
  }
  return '...'
}

const formatDisplayValue = (char) => {
  if (getAttrType(char) === 'DIMENSIONS') {
    const [w, h] = (char.text_value || '').split('x')
    return w && h ? `${w}×${h} мм` : char.text_value
  }
  return char.text_value
}

const clearValue = (char) => {
  char.option_id = null
  char.text_value = ''
  emitUpdate()
}

const onAttributeChange = (char) => {
  emitUpdate()
}

const addCharacteristic = (attributeId = null, isFixed = false) => {
  const newChar = {
    attribute_id: attributeId,
    option_id: null,
    text_value: '',
    bool_value: false,
    is_fixed: isFixed
  }
  
  if (attributeId) {
    const attr = allAttributes.value.find(a => a.id === attributeId)
    if (attr && attr.options && attr.options.length === 1) {
      newChar.option_id = attr.options[0].id
    }
  }
  
  localCharacteristics.value.push(newChar)
  emitUpdate()
}

const removeCharacteristic = (index) => {
  localCharacteristics.value.splice(index, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:characteristics', localCharacteristics.value)
  emit('update:modelValue', localCharacteristics.value)
}

const getGeneratesSku = (attrId) => {
  const attr = props.productAttributes.find(a => a.attribute_id === attrId)
  return attr ? attr.generates_sku : true
}

const setGeneratesSku = (attrId, val) => {
  const attrs = [...props.productAttributes]
  const idx = attrs.findIndex(a => a.attribute_id === attrId)
  if (idx > -1) {
    attrs[idx] = { ...attrs[idx], generates_sku: val }
  } else {
    attrs.push({ attribute_id: attrId, generates_sku: val })
  }
  emit('update:productAttributes', attrs)
}

// Watch for changes and emit
watch(localCharacteristics, emitUpdate, { deep: true })

// Category Sync logic
const syncCategoryAttributes = async () => {
  if (!props.categoryCode) {
    categoryAttributes.value = []
    return
  }
  
  try {
    const res = await api.get(`/api/v1/attributes/category/${props.categoryCode}`)
    categoryAttributes.value = res.data || []
    
    // Auto-add missing attributes from category
    categoryAttributes.value.forEach(ca => {
      const alreadyPresent = localCharacteristics.value.some(c => c.attribute_id === ca.attribute_id)
      if (!alreadyPresent) {
        addCharacteristic(ca.attribute_id, ca.is_required || ca.attribute.name.toLowerCase() === 'каркас')
      }
      
      // Also ensure it's in product_attributes
      const inAttrs = props.productAttributes.some(a => a.attribute_id === ca.attribute_id)
      if (!inAttrs) {
          const newAttrs = [...props.productAttributes, { attribute_id: ca.attribute_id, generates_sku: true }]
          emit('update:productAttributes', newAttrs)
      }
    })

    // Remove empty characteristics that don't belong to this category anymore
    localCharacteristics.value = localCharacteristics.value.filter(c => {
      // Keep if it has a value (don't delete user data)
      if (c.option_id || c.text_value || c.bool_value) return true
      
      // Keep if it belongs to current category or is global
      const attr = allAttributes.value.find(a => a.id === c.attribute_id)
      if (!attr) return true
      
      // Safety check: if backend thinks it belongs to this category, keep it
      const belongsToCategory = categoryAttributes.value.some(ca => ca.attribute_id === c.attribute_id)
      if (belongsToCategory) return true

      // Otherwise, check if it's explicitly global (no category codes)
      const isGlobal = !attr.category_codes || attr.category_codes.length === 0
      return isGlobal
    })
  } catch (e) {
    console.error('Failed to sync category attributes', e)
  }
}

watch(() => props.categoryCode, syncCategoryAttributes)

const fetchAttributes = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/attributes/')
    allAttributes.value = res.data || []
  } catch (e) {
    console.error('Failed to load attributes', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchAttributes()
  if (props.categoryCode) {
    await syncCategoryAttributes()
  }
})
</script>

<style scoped>
.characteristics-tab-content {
  padding: 16px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-divider {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.section-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #f1f5f9;
  margin-right: 20px;
}

.kimi-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
  transition: all 0.2s ease;
}

.kimi-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(99, 102, 241, 0.3);
}

.kimi-btn-outline {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 600;
}

.empty-state {
  padding: 60px 0;
  background: #f8fafc;
  border-radius: 20px;
  border: 2px dashed #eef2f6;
}

.char-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.char-row-premium {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #ffffff;
  border: 1px solid #eef2f6;
  border-radius: 14px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.char-row-premium:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05);
  transform: translateY(-1px);
}

.char-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.attr-icon-box {
  width: 44px;
  height: 44px;
  background: #f5f3ff;
  color: #6366f1;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: inset 0 2px 4px rgba(99, 102, 241, 0.05);
}

.attr-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.attr-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.attr-name {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.01em;
}

.fixed-tag {
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0 8px;
  height: 20px;
  line-height: 20px;
}

.attr-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.type-badge {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
  letter-spacing: 0.02em;
}

.options-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #64748b;
}

.mini-option-dot {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  padding: 2px 8px;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
}

.dot-swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.12);
}

.more-hint {
  font-weight: 600;
  color: #94a3b8;
  font-size: 11px;
}

.char-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kimi-btn-icon {
  border: 1px solid #e2e8f0;
  color: #64748b;
  transition: all 0.2s;
}

.kimi-btn-icon:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f5f3ff;
}

.kimi-btn-delete {
  border: 1px solid #fee2e2;
  color: #f87171;
  transition: all 0.2s;
}

.kimi-btn-delete:hover {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #ef4444;
}

.char-sku-toggle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 0 16px;
  border-left: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
}

.toggle-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  white-space: nowrap;
}

/* Dialog Styles */
.kimi-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

.kimi-dialog :deep(.el-dialog__header) {
  padding: 24px 32px;
  margin-right: 0;
  border-bottom: 1px solid #f1f5f9;
}

.kimi-dialog :deep(.el-dialog__title) {
  font-weight: 700;
  color: #1e293b;
}

.kimi-dialog :deep(.el-dialog__body) {
  padding: 32px;
}

.kimi-dialog :deep(.el-dialog__footer) {
  padding: 16px 32px 32px;
  border-top: none;
}

.dialog-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #475569;
}

.styled-input :deep(.el-input__wrapper) {
  background: #f8fafc !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  padding: 8px 16px !important;
}

.color-picker-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.dimensions-input {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dim-field {
  width: 72px;
}

.dim-field :deep(.el-input__wrapper) {
  background: #f8fafc !important;
  border-radius: 8px !important;
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  padding: 2px 8px !important;
}

.dims-sep {
  font-size: 14px;
  font-weight: 700;
  color: #94a3b8;
}

.dims-unit {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.values-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.empty-val-hint {
  font-size: 11px;
  color: #cbd5e1;
  font-style: italic;
}

.value-selector-box {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.kimi-value-select {
  width: 200px;
}

.option-item-flex {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot-swatch-mini {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.1);
}

.dimensions-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 2px 10px;
  border-radius: 8px;
}

.manual-label {
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  font-weight: 700;
  margin-right: 4px;
}

.dim-field-compact {
  width: 50px;
}

.dim-field-compact :deep(.el-input__wrapper) {
  padding: 0 4px !important;
  background: white !important;
}

.btn-cancel {
  border-radius: 10px;
  font-weight: 600;
}

.btn-save {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  font-weight: 700;
  border-radius: 10px;
}
</style>
