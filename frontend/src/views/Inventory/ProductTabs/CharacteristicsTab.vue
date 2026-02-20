<template>
  <el-card shadow="never" class="tab-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">Характеристики товару</span>
        <el-button type="primary" :icon="Plus" size="small" @click="addCharacteristic" :disabled="availableAttributes.length === 0">
          Додати
        </el-button>
      </div>
    </template>

    <div v-if="characteristics.length === 0" class="empty-state">
      <el-empty description="Характеристики не задані" :image-size="80">
        <el-button type="primary" @click="addCharacteristic" :disabled="availableAttributes.length === 0">
          Додати характеристику
        </el-button>
      </el-empty>
    </div>

    <div v-else class="char-list">
      <div v-for="(char, index) in characteristics" :key="index" class="char-row">
        <div class="char-attribute">
          <el-select
            v-model="char.attribute_id"
            placeholder="Оберіть характеристику"
            style="width: 100%"
            @change="onAttributeChange(char)"
          >
            <el-option
              v-for="attr in getAvailableForRow(char)"
              :key="attr.id"
              :label="attr.name"
              :value="attr.id"
            >
              <span>{{ attr.name }}</span>
              <el-tag v-if="attr.type" size="small" type="info" style="margin-left: 8px">{{ typeLabel(attr.type) }}</el-tag>
            </el-option>
          </el-select>
        </div>
        <div class="char-value">
          <!-- SELECT type -->
          <el-select
            v-if="getAttrType(char) === 'SELECT'"
            v-model="char.option_id"
            placeholder="Оберіть значення"
            style="width: 100%"
          >
            <el-option v-for="opt in getAttrOptions(char)" :key="opt.id" :label="opt.value" :value="opt.id" />
          </el-select>

          <!-- COLOR type -->
          <div v-else-if="getAttrType(char) === 'COLOR'" class="color-picker-row">
            <el-select v-model="char.option_id" placeholder="Оберіть колір" style="flex: 1">
              <el-option v-for="opt in getAttrOptions(char)" :key="opt.id" :label="opt.value" :value="opt.id">
                <span class="color-swatch" :style="{ background: opt.color_code || '#ccc' }"></span>
                <span>{{ opt.value }}</span>
              </el-option>
            </el-select>
          </div>

          <!-- NUMBER type -->
          <el-input-number
            v-else-if="getAttrType(char) === 'NUMBER'"
            v-model="char.text_value"
            controls-position="right"
            style="width: 100%"
          />

          <!-- BOOLEAN type -->
          <el-switch
            v-else-if="getAttrType(char) === 'BOOLEAN'"
            v-model="char.bool_value"
          />

          <!-- TEXT type (default) -->
          <el-input
            v-else
            v-model="char.text_value"
            placeholder="Введіть значення"
          />
        </div>
        <el-button :icon="Delete" link type="danger" @click="removeCharacteristic(index)" />
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
  categoryCode: { type: String, default: '' }
})

const emit = defineEmits(['update:characteristics'])

// All attributes from backend (loaded once, shared)
const allAttributes = ref([])
const loading = ref(false)

// Local characteristics (attribute_id -> value mapping)
const characteristics = ref([])

// Computed: attributes already used in the current list
const usedAttributeIds = computed(() => characteristics.value.map(c => c.attribute_id).filter(Boolean))

// Attributes available for a new row (not already used)
const availableAttributes = computed(() => {
  return allAttributes.value.filter(a => !usedAttributeIds.value.includes(a.id))
})

// For a specific row – show its own attribute + available ones
const getAvailableForRow = (char) => {
  return allAttributes.value.filter(a => a.id === char.attribute_id || !usedAttributeIds.value.includes(a.id))
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
  // Reset value when attribute changes
  char.option_id = null
  char.text_value = ''
  char.bool_value = false
  emitUpdate()
}

const addCharacteristic = () => {
  characteristics.value.push({
    attribute_id: null,
    option_id: null,
    text_value: '',
    bool_value: false
  })
}

const removeCharacteristic = (index) => {
  characteristics.value.splice(index, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:characteristics', characteristics.value)
}

// Watch for changes and emit
watch(characteristics, emitUpdate, { deep: true })

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

onMounted(() => {
  fetchAttributes()
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

.char-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.char-attribute {
  flex: 1;
  min-width: 0;
}

.char-value {
  flex: 1;
  min-width: 0;
}

.color-picker-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-swatch {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
  vertical-align: middle;
  border: 1px solid rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .char-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
