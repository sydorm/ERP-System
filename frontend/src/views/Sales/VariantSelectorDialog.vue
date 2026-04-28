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
      <div class="selection-body" v-loading="attributeLoading" element-loading-text="Завантаження характеристик...">
        <el-form label-position="top" class="premium-form" v-if="!attributeLoading">
          <!-- VARIANT GENERATING ATTRIBUTES -->
          <div class="variant-attributes-section mb-6">
            <h4 class="text-xs font-bold text-indigo-600 uppercase mb-4 tracking-wider">Основні параметри (SKU)</h4>
            <el-form-item
              v-for="attr in variantAttributes"
              :key="attr.id"
              :label="attr.name"
              class="selection-item"
            >
              <div v-if="attr.type === 'DIMENSIONS'" class="dims-container-vertical">
                <el-select
                  v-model="selections[attr.id]"
                  placeholder="Оберіть варіант..."
                  style="width: 100%"
                  filterable
                  clearable
                  @change="handleDimOptionChange(attr.id)"
                  class="premium-select mb-2"
                >
                  <el-option
                    v-for="opt in getAvailableOptions(attr.id)"
                    :key="opt.id"
                    :label="opt.value"
                    :value="opt.id"
                  />
                </el-select>
                
                <div class="dims-manual-wrapper">
                  <div class="dims-row">
                    <span class="manual-hint">або вручну:</span>
                    <div class="dims-inputs-group">
                      <el-input-number
                        v-model="getDimValue(attr.id).w"
                        :min="0" :precision="0" :controls="false"
                        placeholder="Ширина"
                        class="dim-input"
                        @change="handleAttributeChange(attr.id, true)"
                      />
                      <span class="dims-sep">×</span>
                      <el-input-number
                        v-model="getDimValue(attr.id).h"
                        :min="0" :precision="0" :controls="false"
                        placeholder="Висота"
                        class="dim-input"
                        @change="handleAttributeChange(attr.id, true)"
                      />
                      <span class="dims-unit">мм</span>
                    </div>
                  </div>
                </div>
              </div>

              <el-select
                v-else
                v-model="selections[attr.id]"
                placeholder="Оберіть варіант..."
                style="width: 100%"
                filterable
                :allow-create="attr.allow_manual_input"
                default-first-option
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
                    <span v-if="opt.color_code" class="color-pill" :style="{ backgroundColor: opt.color_code }"></span>
                    <span class="option-text">{{ opt.value }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </div>

          <!-- EXTRA ATTRIBUTES (NON-VARIANT) -->
          <div v-if="extraAttributes.length" class="extra-attributes-section pt-4 border-t border-slate-100">
            <h4 class="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider">Додаткові умови</h4>
            <el-form-item
              v-for="attr in extraAttributes"
              :key="attr.id"
              :label="attr.name"
              class="selection-item"
            >
              <div v-if="attr.type === 'DIMENSIONS'" class="dims-container-vertical">
                <el-select
                  v-model="selections[attr.id]"
                  placeholder="Виберіть..."
                  style="width: 100%"
                  filterable
                  clearable
                  @change="handleDimOptionChange(attr.id)"
                  class="premium-select mb-2"
                >
                  <el-option
                    v-for="opt in getAvailableOptions(attr.id)"
                    :key="opt.id"
                    :label="opt.value"
                    :value="opt.id"
                  />
                </el-select>
                <div class="dims-manual-wrapper">
                  <div class="dims-row">
                    <span class="manual-hint">або вручну:</span>
                    <div class="dims-inputs-group">
                      <el-input-number
                        v-model="getDimValue(attr.id).w"
                        :min="0" :precision="0" :controls="false"
                        placeholder="Ширина"
                        class="dim-input"
                        @change="handleAttributeChange(attr.id, true)"
                      />
                      <span class="dims-sep">×</span>
                      <el-input-number
                        v-model="getDimValue(attr.id).h"
                        :min="0" :precision="0" :controls="false"
                        placeholder="Висота"
                        class="dim-input"
                        @change="handleAttributeChange(attr.id, true)"
                      />
                      <span class="dims-unit">мм</span>
                    </div>
                  </div>
                </div>
              </div>

              <el-input 
                v-else-if="attr.type === 'TEXT'" 
                v-model="selections[attr.id]" 
                placeholder="Введіть текст..."
                @change="handleAttributeChange(attr.id)"
              />
              
              <el-select
                v-else
                v-model="selections[attr.id]"
                placeholder="Виберіть..."
                style="width: 100%"
                filterable
                :allow-create="attr.allow_manual_input || attr.type === 'TEXT'"
                @change="handleAttributeChange(attr.id)"
                class="premium-select"
              >
                <el-option
                  v-for="opt in getAvailableOptions(attr.id)"
                  :key="opt.id"
                  :label="opt.value"
                  :value="opt.id"
                />
              </el-select>
            </el-form-item>
          </div>
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
import { Picture, Brush, Operation, EditPen } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean,
  product: Object,
  initialVariantId: { type: String, default: null },
  initialValues: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'select'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const selections = ref({})
const dimSelections = ref({})
const allCategoryAttributes = ref([])
const attributeLoading = ref(false)

// Watchers
watch(() => [props.modelValue, props.product], async ([isOpen, prod]) => {
  if (isOpen && prod) {
    await fetchAttributes()
    // initializeSelector is now called inside fetchAttributes for atomicity
  }
}, { immediate: true })

const fetchAttributes = async () => {
    if (!props.product?.category) {
        allCategoryAttributes.value = []
        initializeSelector() // Initialize with empty
        return
    }
    attributeLoading.value = true
    try {
        const res = await api.get(`/api/v1/attributes/category/${props.product.category}`)
        allCategoryAttributes.value = (res.data || []).map(ca => ({
            ...ca.attribute,
            is_required: ca.is_required
        }))
        // Initialize IMMEDIATELY after loading
        initializeSelector()
    } catch (e) {
        console.error('Failed to load attributes in dialog', e)
    } finally {
        attributeLoading.value = false
    }
}

const initializeSelector = () => {
  // Reset
  selections.value = {}
  dimSelections.value = {}

  // 1. Initialize all known attributes with defaults
  const allAttrs = allCategoryAttributes.value.length ? allCategoryAttributes.value : []
  allAttrs.forEach(attr => {
      if (attr.type === 'DIMENSIONS') {
          dimSelections.value[attr.id] = { w: null, h: null }
      }
  })

  // 2. If no category attributes but we have variants, extract attributes from variants
  if (allAttrs.length === 0 && props.product?.variants) {
      props.product.variants.forEach(v => {
        v.values?.forEach(val => {
          if (val.attribute) {
              if (val.attribute.type === 'DIMENSIONS' && !dimSelections.value[val.attribute_id]) {
                  dimSelections.value[val.attribute_id] = { w: null, h: null }
              }
          }
        })
      })
  }
  
  // 3. Load initial values if variant ID is provided OR initial values passed
  let valuesToLoad = []
  if (props.initialVariantId && props.product?.variants) {
    const variant = props.product.variants.find(v => v.id === props.initialVariantId)
    if (variant?.values) valuesToLoad = variant.values
  } else if (props.initialValues && props.initialValues.length > 0) {
    valuesToLoad = props.initialValues
  }

  if (valuesToLoad.length > 0) {
    valuesToLoad.forEach(v => {
      // Find attribute type from our cached category attributes if possible
      const attr = allCategoryAttributes.value.find(a => a.id === v.attribute_id)
      const type = attr?.type || v.attribute?.type

      if (type === 'DIMENSIONS') {
          // Priority: numeric width/height, fallback: parse text_value
          if (v.width && v.height) {
              dimSelections.value[v.attribute_id] = { w: v.width, h: v.height }
          } else if (v.text_value) {
              // Normalize and split
              const norm = v.text_value.replace(/[\u00d7*]/g, 'x').replace(/\s+/g, '')
              const [w, h] = norm.split('x')
              dimSelections.value[v.attribute_id] = { w: parseInt(w) || null, h: parseInt(h) || null }
          }
      } else {
          selections.value[v.attribute_id] = v.option_id || v.text_value
      }
    })
  }
}

const variantAttributes = computed(() => {
    const attrs = allCategoryAttributes.value.length ? allCategoryAttributes.value : []
    return attrs.filter(a => {
        const prodAttr = props.product?.product_attributes?.find(pa => pa.attribute_id === a.id)
        if (prodAttr) return prodAttr.generates_sku
        return a.generates_variant !== false
    })
})

const extraAttributes = computed(() => {
    const attrs = allCategoryAttributes.value.length ? allCategoryAttributes.value : []
    return attrs.filter(a => {
        const prodAttr = props.product?.product_attributes?.find(pa => pa.attribute_id === a.id)
        if (prodAttr) return !prodAttr.generates_sku
        return a.generates_variant === false
    })
})

const getAvailableOptions = (attrId) => {
  const attr = allCategoryAttributes.value.find(a => a.id === attrId)
  return attr?.options || []
}

const allAttributesSelected = computed(() => {
  if (variantAttributes.value.length === 0) return false
  return variantAttributes.value.every(a => {
    if (a.type === 'DIMENSIONS') {
      const d = dimSelections.value[a.id]
      return d && d.w > 0 && d.h > 0
    }
    return !!selections.value[a.id]
  })
})

const currentVariant = computed(() => {
  if (!allAttributesSelected.value) return null
  
  return props.product.variants.find(v => {
    return variantAttributes.value.every(a => {
      const selection = selections.value[a.id]
      const dim = dimSelections.value[a.id]
      
      return v.values?.some(vv => {
        if (vv.attribute_id !== a.id) return false
        if (a.type === 'DIMENSIONS') {
            if (!vv.text_value) return false
            const normStored = vv.text_value.replace(/[\u00d7*]/g, 'x').replace(/\s+/g, '')
            const normExpected = `${dim.w}x${dim.h}`
            return normStored === normExpected
        }
        return vv.option_id === selection || vv.text_value === selection
      })
    })
  })
})

const handleConfirm = async () => {
  if (allAttributesSelected.value) {
    const selectedValues = variantAttributes.value.concat(extraAttributes.value).map(attr => {
        const selection = selections.value[attr.id]
        const isUuid = typeof selection === 'string' && selection.length === 36
        
        if (attr.type === 'DIMENSIONS') {
          const d = dimSelections.value[attr.id]
          const fmt = attr.dimension_format || '{width}×{height}'
          const val = fmt.replace('{width}', d.w).replace('{height}', d.h)
          return { 
            attribute_id: attr.id, 
            option_id: null, 
            text_value: val, 
            attribute: attr, 
            option: null,
            width: d.w,
            height: d.h
          }
        }
        return {
            attribute_id: attr.id,
            option_id: isUuid ? selection : null,
            text_value: isUuid ? null : selection,
            attribute: attr,
            option: isUuid ? attr.options?.find(o => o.id === selection) : null
        }
    }).filter(v => v.option_id || v.text_value)

    if (currentVariant.value) {
        emit('select', {
            ...currentVariant.value,
            values: selectedValues
        })
        visible.value = false
    } else {
        // Check if we should skip variant creation for materials/components
        const catStr = (props.product?.category || '').toUpperCase();
        const skipVariantCreation = 
            props.product?.type === 'material' || 
            props.product?.type === 'component' || 
            catStr.includes('МАТЕРІАЛ') || 
            catStr.includes('ДСП') || 
            catStr.includes('МЕТАЛ') ||
            catStr.includes('MATERIAL') ||
            catStr.includes('DSP') ||
            catStr.includes('METAL');

        if (skipVariantCreation) {
            const virtualVariant = {
                id: null,
                product_id: props.product.id,
                sku: props.product.sku,
                values: selectedValues
            }
            emit('select', virtualVariant)
            visible.value = false
            return
        }

        // If variant not found but all variant-generating attributes are selected
        // Ask to create a new variant
        try {
            const dimAttr = variantAttributes.value.find(a => a.type === 'DIMENSIONS')
            let label = "цю комбінацію"
            if (dimAttr) {
                const d = dimSelections.value[dimAttr.id]
                label = `${d.w}×${d.h}`
            }

            await ElMessageBox.confirm(
                `Варіант "${label}" не існує. Створити автоматично?`,
                'Новий варіант',
                { confirmButtonText: 'Так, створити', cancelButtonText: 'Ні, просто вибрати', type: 'info' }
            )

            // Create variant
            attributeLoading.value = true
            const newSku = `${props.product.sku}-${Date.now().toString().slice(-4)}`
            
            // Map values for the API (only variant-generating ones)
            const variantValues = selectedValues.filter(v => {
                const attr = allCategoryAttributes.value.find(a => a.id === v.attribute_id)
                return attr?.generates_variant !== false
            }).map(v => ({
                attribute_id: v.attribute_id,
                option_id: v.option_id,
                text_value: v.text_value
            }))

            const res = await api.post('/api/v1/attributes/variants', {
                product_id: props.product.id,
                sku: newSku,
                values: variantValues
            })
            
            emit('select', {
                ...res.data,
                values: selectedValues
            })
            visible.value = false
        } catch (e) {
            if (e !== 'cancel') {
                console.error('Failed to create variant', e)
                ElMessage.error('Помилка при створенні варіанту')
            } else {
                // User said "No, just select" -> send as virtual
                const virtualVariant = {
                    id: null,
                    product_id: props.product.id,
                    sku: props.product.sku,
                    values: selectedValues
                }
                emit('select', virtualVariant)
                visible.value = false
            }
        } finally {
            attributeLoading.value = false
        }
    }
  }
}

const handleClose = () => { selections.value = {} }
const handleAttributeChange = () => {}

const handleDimOptionChange = (attrId) => {
  const selected = selections.value[attrId]
  if (!selected) return
  
  // Find the option label to parse dimensions if selected is an ID
  const options = getAvailableOptions(attrId)
  const opt = options.find(o => o.id === selected)
  const val = opt ? opt.value : selected.toString()
  
  // Robust split using regex for x, ×, *
  const parts = val.replace(/\s+/g, '').split(/[x\u00d7*]/)
  if (parts.length >= 2) {
    if (!dimSelections.value[attrId]) {
      dimSelections.value[attrId] = { w: 0, h: 0 }
    }
    dimSelections.value[attrId].w = parseFloat(parts[0]) || 0
    dimSelections.value[attrId].h = parseFloat(parts[1]) || 0
  }
}

const getDimValue = (attrId) => {
    if (!dimSelections.value[attrId]) {
        dimSelections.value[attrId] = { w: null, h: null }
    }
    return dimSelections.value[attrId]
}

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

.dims-container-vertical { display: flex; flex-direction: column; gap: 4px; }
.dims-manual-wrapper { padding-top: 4px; }
.dims-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}
.manual-hint { 
  font-size: 12px; 
  color: #94a3b8; 
  white-space: nowrap; 
  font-weight: 500;
  flex-shrink: 0;
}
.dims-inputs-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}
.dim-input { width: 85px !important; }
.dim-input :deep(.el-input__inner) { text-align: center; font-weight: 600; }
.dims-sep { font-size: 16px; color: #cbd5e1; font-weight: 600; }
.dims-unit { font-size: 12px; color: #94a3b8; font-weight: 600; min-width: 24px; }
</style>
