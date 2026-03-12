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
              <div v-if="getAttrOptions(char).length > 0" class="options-preview">
                <span v-for="opt in getAttrOptions(char).slice(0, 5)" :key="opt.id" class="mini-option-dot">
                  <span v-if="opt.color_code" class="dot-swatch" :style="{ background: opt.color_code }"></span>
                  {{ opt.value }}
                </span>
                <span v-if="getAttrOptions(char).length > 5" class="more-hint">...що ще</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="char-controls">
          <el-button 
            v-if="['SELECT', 'COLOR'].includes(getAttrType(char))"
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
        <el-form-item label="Значення">
          <el-input v-model="newOption.value" placeholder="Наприклад: Червоний, 1000мм..." class="styled-input" />
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
  modelValue: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:characteristics', 'update:modelValue'])

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
  color_code: ''
})

const openAddOptionDialog = (attrId) => {
  const attr = allAttributes.value.find(a => a.id === attrId)
  if (!attr) return
  
  selectedAttrForOption.value = attrId
  selectedAttrType.value = attr.type
  newOption.value = ''
  newOption.color_code = attr.type === 'COLOR' ? '#000000' : ''
  addOptionVisible.value = true
}

const saveNewOption = async () => {
  if (!selectedAttrForOption.value || !newOption.value) return
  
  savingOption.value = true
  try {
    const res = await api.post(`/api/v1/attributes/${selectedAttrForOption.value}/options`, {
      value: newOption.value,
      color_code: newOption.color_code || null
    })
    
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
  const map = { TEXT: 'Текст', SELECT: 'Список', NUMBER: 'Число', COLOR: 'Колір', BOOLEAN: 'Так/Ні' }
  return map[type] || type
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
      } else if (ca.is_required || ca.attribute.name.toLowerCase() === 'каркас') {
         // Mark existing as fixed if needed
         const char = localCharacteristics.value.find(c => c.attribute_id === ca.attribute_id)
         if (char) char.is_fixed = true
      }
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
