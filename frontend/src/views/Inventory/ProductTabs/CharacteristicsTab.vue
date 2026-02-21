<template>
  <el-card shadow="never" class="tab-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">Характеристики товару</span>
        <el-button type="primary" :icon="Plus" size="small" @click="addCharacteristic" :disabled="availableAttributesForAdd.length === 0">
          Додати
        </el-button>
      </div>
    </template>

    <div v-if="localCharacteristics.length === 0" class="empty-state">
      <el-empty description="Характеристики не задані" :image-size="80">
        <el-button type="primary" @click="addCharacteristic" :disabled="availableAttributesForAdd.length === 0">
          Додати характеристику
        </el-button>
      </el-empty>
    </div>

    <div v-else class="char-list">
      <div v-for="(char, index) in localCharacteristics" :key="index" class="char-row-premium">
        <div class="char-info">
          <el-icon class="attr-icon"><Operation /></el-icon>
          <div class="attr-details">
            <span class="attr-name">{{ getAttributeName(char.attribute_id) }}</span>
            <span class="attr-type">{{ typeLabel(getAttrType(char)) }}</span>
          </div>
        </div>
        
        <div class="char-status">
          <el-tag v-if="char.is_fixed" size="small" type="warning" effect="light">Обов'язкова</el-tag>
          <el-tag v-else size="small" type="info" effect="plain">Опціональна</el-tag>
        </div>

        <el-button 
          v-if="!char.is_fixed" 
          :icon="Delete" 
          circle
          size="small"
          type="danger" 
          @click="removeCharacteristic(index)" 
          title="Видалити"
        />
        <div v-else style="width: 32px"></div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
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

// Attributes available for a new row (not already used)
const availableAttributesForAdd = computed(() => {
  return allAttributes.value.filter(a => !usedAttributeIds.value.includes(a.id))
})

// For a specific row – show its own attribute + available ones
const getAvailableForRow = (char) => {
  return allAttributes.value.filter(a => a.id === char.attribute_id || !usedAttributeIds.value.includes(a.id))
}

const getAttributeName = (attrId) => {
  const attr = allAttributes.value.find(a => a.id === attrId)
  return attr?.name || 'Характеристика'
}

const getAttrType = (char) => {
  const attr = allAttributes.value.find(a => a.id === char.attribute_id)
  return attr?.type || 'TEXT'
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
.tab-card {
  margin: 24px;
  border: 1px solid #eef0f2;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1d1f;
}

.empty-state {
  padding: 20px 0;
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
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #eef2f6;
  transition: all 0.2s ease;
}

.char-row-premium:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.char-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.attr-icon {
  font-size: 18px;
  color: #6366f1;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.attr-details {
  display: flex;
  flex-direction: column;
}

.attr-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.attr-type {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.char-status {
  padding: 0 16px;
}

@media (max-width: 640px) {
  .char-row-premium {
    flex-wrap: wrap;
    gap: 16px;
  }
  .char-status {
    width: 100%;
    padding: 0;
  }
}
</style>
