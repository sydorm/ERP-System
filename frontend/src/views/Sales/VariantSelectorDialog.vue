<template>
  <el-dialog
    v-model="visible"
    title="Конфігурація характеристик"
    width="500px"
    @close="handleClose"
    destroy-on-close
  >
    <div v-if="product" class="variant-selector-body">
      <div class="product-info mb-4">
        <h4>{{ product.name }}</h4>
        <div class="sku-preview">SKU: {{ currentVariant?.sku || product.sku }}</div>
      </div>

      <el-form label-position="top">
        <el-form-item 
          v-for="attr in sortedAttributes" 
          :key="attr.id" 
          :label="attr.name"
        >
          <el-select
            v-model="selections[attr.id]"
            placeholder="Оберіть..."
            style="width: 100%"
            @change="handleAttributeChange(attr.id)"
            :disabled="isAttributeDisabled(attr.id)"
          >
            <el-option
              v-for="opt in getAvailableOptions(attr.id)"
              :key="opt.id"
              :label="opt.value"
              :value="opt.id"
            >
              <div class="option-item">
                <span 
                  v-if="opt.color_code" 
                  class="color-indicator" 
                  :style="{ backgroundColor: opt.color_code }"
                ></span>
                <span>{{ opt.value }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <div class="selection-footer mt-4" v-if="currentVariant">
        <div class="price-display">
          Ціна: <strong>{{ formatShort(currentVariant.price_override || product.price) }}</strong>
        </div>
      </div>
      <div v-else-if="allAttributesSelected" class="mt-4">
        <el-alert title="Така комбінація не знайдена" type="warning" show-icon :closable="false" />
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">Скасувати</el-button>
      <el-button 
        type="primary" 
        :disabled="!currentVariant"
        @click="handleConfirm"
      >
        Підтвердити
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  product: Object,
  initialVariantId: String
})

const emit = defineEmits(['update:modelValue', 'select'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const selections = ref({})
const sortedAttributes = ref([])
const allCategoryAttributes = ref([])
const attributeLoading = ref(false)

// Initialize state when product changes or dialog opens
watch(() => [props.modelValue, props.product], async ([isOpen, prod]) => {
  if (isOpen && prod) {
    await fetchAttributes()
    initializeSelector()
  }
}, { immediate: true })

const fetchAttributes = async () => {
    if (!props.product?.category) {
        allCategoryAttributes.value = []
        return
    }
    attributeLoading.value = true
    try {
        const res = await api.get(`/api/v1/attributes/category/${props.product.category}`)
        allCategoryAttributes.value = (res.data || []).map(ca => ({
            ...ca.attribute,
            is_required: ca.is_required
        }))
    } catch (e) {
        console.error('Failed to load attributes in dialog', e)
    } finally {
        attributeLoading.value = false
    }
}

const initializeSelector = () => {
  // Use category attributes if available, otherwise fallback to variant-derived
  if (allCategoryAttributes.value.length > 0) {
      sortedAttributes.value = allCategoryAttributes.value
  } else if (props.product?.variants) {
      // Extract all unique attributes across variants (legacy/fallback fallback)
      const attrsMap = new Map()
      props.product.variants.forEach(v => {
        v.values?.forEach(val => {
          if (val.attribute) {
            attrsMap.set(val.attribute.id, val.attribute)
          }
        })
      })
      sortedAttributes.value = Array.from(attrsMap.values())
  }
  
  selections.value = {}

  // If initial variant is provided, pre-fill selections
  if (props.initialVariantId) {
    const variant = props.product.variants.find(v => v.id === props.initialVariantId)
    if (variant && variant.values) {
      variant.values.forEach(v => {
        selections.value[v.attribute_id] = v.option_id
      })
    }
  }
}

const getAvailableOptions = (attrId) => {
  const attr = sortedAttributes.value.find(a => a.id === attrId)
  if (!attr || !attr.options) return []

  // If we want to strictly show ONLY what's available in variants (cascading):
  // we could filter this list. But the user said "show all values".
  // So we return all options for the attribute.
  return attr.options
}

const isAttributeDisabled = (attrId) => {
  // Optional: could disable if parent attributes aren't selected
  return false
}

const handleAttributeChange = (attrId) => {
  // Cascading reset: optional, but let's keep it simple for now
}

const allAttributesSelected = computed(() => {
  return sortedAttributes.value.every(a => !!selections.value[a.id])
})

const currentVariant = computed(() => {
  if (!allAttributesSelected.value) return null
  
  return props.product.variants.find(v => {
    return sortedAttributes.value.every(a => {
      return v.values?.some(vv => vv.attribute_id === a.id && vv.option_id === selections.value[vv.attribute_id])
    })
  })
})

const handleConfirm = () => {
  if (currentVariant.value) {
    emit('select', currentVariant.value)
    visible.value = false
  }
}

const handleClose = () => {
  selections.value = {}
}

const formatShort = (val) => new Intl.NumberFormat('uk-UA').format(val) + ' грн'
</script>

<style scoped>
.variant-selector-body {
  padding: 10px 0;
}

.product-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.sku-preview {
  font-size: 13px;
  color: #64748b;
  font-family: monospace;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-indicator {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.1);
}

.price-display {
  text-align: right;
  font-size: 16px;
}

.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
</style>
