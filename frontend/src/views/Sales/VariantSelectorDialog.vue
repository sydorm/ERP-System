<template>
  <el-dialog
    v-model="visible"
    title="Конфігурація характеристик"
    width="540px"
    class="premium-dialog"
    @close="handleClose"
    destroy-on-close
  >
    <div v-if="product" class="variant-selector-container">
      <!-- Product Hero Section -->
      <div class="product-hero">
        <div class="product-image">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
          <div v-else class="image-placeholder">
            <el-icon :size="32"><Picture /></el-icon>
          </div>
        </div>
        <div class="product-meta">
          <h3 class="product-title">{{ product.name }}</h3>
          <div class="sku-badge">
            <span class="label">SKU:</span>
            <span class="value">{{ currentVariant?.sku || product.sku }}</span>
          </div>
        </div>
      </div>

      <!-- Attributes Form -->
      <div class="selection-body">
        <el-form label-position="top" class="premium-form">
          <transition-group name="fade-list">
            <el-form-item 
              v-for="attr in sortedAttributes" 
              :key="attr.id" 
              :label="attr.name"
              class="selection-item"
            >
              <el-select
                v-model="selections[attr.id]"
                placeholder="Оберіть варіант..."
                style="width: 100%"
                filterable
                @change="handleAttributeChange(attr.id)"
                class="premium-select"
              >
                <template #prefix>
                  <el-icon v-if="attr.type === 'COLOR'"><Brush /></el-icon>
                  <el-icon v-else><Operation /></el-icon>
                </template>
                <el-option
                  v-for="opt in getAvailableOptions(attr.id)"
                  :key="opt.id"
                  :label="opt.value"
                  :value="opt.id"
                >
                  <div class="option-item">
                    <span 
                      v-if="opt.color_code" 
                      class="color-pill" 
                      :style="{ backgroundColor: opt.color_code }"
                    ></span>
                    <span class="option-text">{{ opt.value }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </transition-group>
        </el-form>
      </div>

      <!-- State Feedback -->
      <div class="selection-feedback">
        <transition name="el-fade-in-linear">
          <!-- Removed price card as requested by user -->
          <div v-if="allAttributesSelected && !currentVariant" class="not-found-card">
            <el-alert 
              title="Нова комбінація" 
              description="Ця комбінація характеристик ще не створена як окремий артикул, але ви можете її обрати."
              type="success" 
              show-icon 
              :closable="false" 
            />
          </div>
        </transition>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false" class="btn-cancel">Скасувати</el-button>
        <el-button 
          type="primary" 
          :disabled="!allAttributesSelected"
          @click="handleConfirm"
          class="btn-confirm"
        >
          Підтвердити вибір
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Picture, Brush, Operation } from '@element-plus/icons-vue'
import api from '@/api'

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

// Watchers
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
  if (allCategoryAttributes.value.length > 0) {
      sortedAttributes.value = allCategoryAttributes.value
  } else if (props.product?.variants) {
      const attrsMap = new Map()
      props.product.variants.forEach(v => {
        v.values?.forEach(val => {
          if (val.attribute) attrsMap.set(val.attribute.id, val.attribute)
        })
      })
      sortedAttributes.value = Array.from(attrsMap.values())
  }
  
  selections.value = {}

  if (props.initialVariantId) {
    const variant = props.product.variants.find(v => v.id === props.initialVariantId)
    if (variant?.values) {
      variant.values.forEach(v => {
        selections.value[v.attribute_id] = v.option_id
      })
    }
  }
}

const getAvailableOptions = (attrId) => {
  const attr = sortedAttributes.value.find(a => a.id === attrId)
  return attr?.options || []
}

const allAttributesSelected = computed(() => {
  if (sortedAttributes.value.length === 0) return false
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
  if (allAttributesSelected.value) {
    // If we have a matching variant, emit it. 
    // Otherwise emit the selections so OrderEditor can handle it.
    if (currentVariant.value) {
        emit('select', currentVariant.value)
    } else {
        // Construct a "virtual" variant object
        const virtualVariant = {
            id: null,
            product_id: props.product.id,
            sku: props.product.sku, // Base SKU
            values: sortedAttributes.value.map(attr => ({
                attribute_id: attr.id,
                option_id: selections.value[attr.id],
                attribute: attr,
                option: attr.options?.find(o => o.id === selections.value[attr.id])
            }))
        }
        emit('select', virtualVariant)
    }
    visible.value = false
  }
}

const handleClose = () => { selections.value = {} }
const handleAttributeChange = () => {}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)
</script>

<style scoped>
.variant-selector-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 8px 0;
}

/* Hero Section */
.product-hero {
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.product-image {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  color: #94a3b8;
}

.product-meta {
  flex: 1;
}

.product-title {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.sku-badge {
  display: inline-flex;
  gap: 6px;
  font-size: 13px;
  background: white;
  padding: 2px 10px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
}

.sku-badge .label { color: #64748b; }
.sku-badge .value { color: #0f172a; font-weight: 600; }

/* Form Styling */
.selection-body {
  padding: 0 4px;
}

.premium-form :deep(.el-form-item__label) {
  font-weight: 600 !important;
  color: #475569 !important;
  font-size: 14px !important;
  margin-bottom: 8px !important;
  padding: 0 !important;
}

.selection-item {
  margin-bottom: 20px !important;
}

.premium-select :deep(.el-input__wrapper) {
  padding: 4px 12px !important;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  border-radius: 10px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.premium-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #6366f1 inset, 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
}

/* Option Items */
.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 100%;
}

.color-pill {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.option-text {
  font-weight: 500;
  color: #1e293b;
}

/* Feedback Section */
.selection-feedback {
  min-height: 80px;
}

.price-card {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  padding: 16px 20px;
  border-radius: 12px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
}

.price-header {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 500;
}

.price-value {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.not-found-card {
  background: #fef2f2;
  border-radius: 12px;
  overflow: hidden;
}

/* Animations */
.fade-list-enter-active, .fade-list-leave-active {
  transition: all 0.3s ease;
}
.fade-list-enter-from, .fade-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Footer Button Styling */
.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel {
  border-radius: 8px !important;
}

.btn-confirm {
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 0 24px !important;
}
</style>
