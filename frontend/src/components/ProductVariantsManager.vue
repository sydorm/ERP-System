<template>
  <div class="variants-manager">
    <div class="section-header">
      <div class="title-with-badge">
        <h3>Варіанти товару (SKU)</h3>
        <el-tag v-if="variants.length" type="success" effect="plain">{{ variants.length }}</el-tag>
      </div>
      <div class="actions">
        <div class="pricing-mode-selector">
          <span class="mr-2 text-sm text-slate-500">Режим ціноутворення:</span>
          <el-radio-group v-model="localPriceRule.pricing_mode" size="small">
            <el-radio-button label="manual">Вручну</el-radio-button>
            <el-radio-button label="base_plus_markup">Базова + надбавки</el-radio-button>
          </el-radio-group>
        </div>
        <el-dropdown v-if="selectedRows.length" @command="handleBulkCommand">
          <el-button type="info">Дії з вибраними ({{ selectedRows.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="price" :disabled="localPriceRule.pricing_mode !== 'manual'">Змінити ціну</el-dropdown-item>
              <el-dropdown-item command="activate">Активувати</el-dropdown-item>
              <el-dropdown-item command="deactivate">Деактивувати</el-dropdown-item>
              <el-dropdown-item command="delete" class="text-danger">Видалити</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" :icon="MagicStick" @click="openGenerator">Згенерувати комбінації</el-button>
        <el-button :icon="Plus" @click="addManualVariant">Додати вручну</el-button>
      </div>
    </div>

    <!-- PRICING RULE CONFIG (Base + Markups) -->
    <div v-if="localPriceRule.pricing_mode === 'base_plus_markup'" class="pricing-rule-config mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
      <el-row :gutter="20" class="mb-4">
        <el-col :span="8">
          <el-form-item label="Базова ціна" class="mb-0">
            <el-input-number v-model="localPriceRule.base_price" :precision="2" :step="100" class="w-full" />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="markups-section">
        <h4 class="text-sm font-semibold mb-3 text-slate-700">Надбавки за характеристики</h4>
        <div v-for="attr in variantAttributes" :key="attr.id" class="attr-markup-group mb-4">
          <div class="text-xs font-bold text-slate-500 mb-2 uppercase">{{ attr.name }}</div>
          <div class="flex flex-wrap gap-3">
            <div v-for="opt in attr.options" :key="opt.id" class="markup-item flex items-center bg-white p-2 rounded border border-slate-200">
              <span class="text-xs mr-2">{{ opt.value }}:</span>
              <el-input-number 
                :model-value="getMarkup(attr.id, opt.id)" 
                @update:model-value="(val) => setMarkup(attr.id, opt.id, val)"
                :precision="2" 
                :step="50" 
                size="small" 
                class="w-32" 
                placeholder="+0"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- VARIANTS TABLE -->
    <el-table 
        :data="variants" 
        style="width: 100%" 
        class="custom-table" 
        v-if="variants.length"
        @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column width="80" label="Фото">
        <template #default="{ row }">
          <el-upload
            class="variant-uploader"
            :show-file-list="false"
            action="#"
            :auto-upload="false"
            @change="(file) => handleVariantImage(row, file)"
          >
            <img v-if="row.image_url" :src="row.image_url" class="variant-img" />
            <el-icon v-else class="variant-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </template>
      </el-table-column>

      <el-table-column prop="sku" label="Артикул (SKU)" width="180">
        <template #default="{ row }">
          <el-input v-model="row.sku" size="small" />
        </template>
      </el-table-column>

      <el-table-column label="Характеристики" min-width="250">
        <template #default="{ row }">
          <div class="variant-values flex flex-wrap gap-2">
            <template v-for="attr in variantAttributes" :key="attr.id">
              <el-dropdown trigger="click" @command="(val) => updateVariantValue(row, attr, val)">
                <el-tag 
                  size="default" 
                  class="cursor-pointer hover:border-indigo-400 transition-colors" 
                  :type="getVariantValue(row, attr.id) ? 'primary' : 'info'"
                  effect="light"
                >
                  <span class="flex items-center whitespace-nowrap gap-1">
                    <span class="font-bold text-[10px] uppercase opacity-60">{{ attr.name }}:</span>
                    <span class="text-xs">{{ getOptionLabelForAttr(row, attr) }}</span>
                  </span>
                </el-tag>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      v-for="opt in attr.options" 
                      :key="opt.id" 
                      :command="opt"
                      :disabled="getVariantValue(row, attr.id)?.option_id === opt.id"
                    >
                      {{ opt.value }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="price_override" label="Ціна" width="120">
        <template #default="{ row }">
          <template v-if="localPriceRule.pricing_mode === 'manual'">
            <el-input-number v-model="row.price_override" :precision="2" :step="100" size="small" controls-position="right" class="w-full" />
          </template>
          <template v-else>
            <div class="calculated-price font-bold text-indigo-600">
              {{ calculateVariantPrice(row) }} <small class="font-normal text-slate-400">грн</small>
            </div>
          </template>
        </template>
      </el-table-column>

      <el-table-column prop="is_primary" label="Основний" width="100" align="center">
        <template #default="{ row }">
          <el-radio v-model="primarySku" :label="row.sku" @change="setPrimary(row)">&nbsp;</el-radio>
        </template>
      </el-table-column>

      <el-table-column fixed="right" width="60" align="center">
        <template #default="{ $index }">
          <el-button type="danger" :icon="Delete" circle size="small" @click="removeVariant($index)" />
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-else description="Немає варіантів. Натисніть кнопку вище, щоб згенерувати комбінації характеристик." />

    <!-- GENERATOR DIALOG -->
    <el-dialog v-model="genVisible" title="Генератор комбінацій" width="700px">
        <div class="generator-steps">
            <div class="step-info mb-4">
                <el-alert title="Виберіть значення для кожної характеристики. Система створить усі можливі комбінації." type="info" show-icon :closable="false" />
            </div>

            <div v-for="attr in variantAttributes" :key="attr.id" class="attr-gen-row mb-4">
                <div class="attr-label mb-2"><strong>{{ attr.name }}</strong></div>
                <el-checkbox-group v-model="genSelection[attr.id]">
                    <el-checkbox v-for="opt in attr.options" :key="opt.id" :label="opt.id">{{ opt.value }}</el-checkbox>
                </el-checkbox-group>
            </div>
            
            <div class="preview-section mt-4" v-if="previewCount > 0">
                <div class="preview-header">Буде створено <strong>{{ previewCount }}</strong> варіантів</div>
                <div class="preview-sku">Приклад SKU: <code>{{ generateSkuPreview() }}</code></div>
            </div>
        </div>
        <template #footer>
            <el-button @click="genVisible = false">Скасувати</el-button>
            <el-button type="primary" :disabled="previewCount === 0" @click="generateVariants">Створити комбінації</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Plus, Delete, MagicStick, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
    categoryAttributes: Array,
    productCode: String,
    initialVariants: Array,
    priceRule: Object,
    productAttributes: { type: Array, default: () => [] },
    variantConfig: { type: Object, default: () => ({}) },
    baseDimensions: { type: Object, default: () => ({ length_mm: 0, width_mm: 0, height_mm: 0, weight_kg: 0 }) }
})

const emit = defineEmits(['update:variants', 'update:priceRule'])

const variants = ref(props.initialVariants || [])
const localPriceRule = ref(props.priceRule || { pricing_mode: 'manual', base_price: 0, markups: [] })
const primarySku = ref('')
const genVisible = ref(false)
const genSelection = reactive({})
const selectedRows = ref([])

// Sync with parent - only emit if actually changed to avoid infinite loops
watch(variants, (newVal) => {
    const currentProps = JSON.stringify(props.initialVariants || [])
    const currentState = JSON.stringify(newVal)
    if (currentState !== currentProps) {
        emit('update:variants', newVal)
    }
}, { deep: true })

watch(localPriceRule, (newVal) => {
    emit('update:priceRule', newVal)
}, { deep: true })

// Sync FROM parent (when switching products)
watch(() => props.initialVariants, (newVal) => {
    const currentState = JSON.stringify(variants.value)
    const newProps = JSON.stringify(newVal || [])
    
    if (newProps !== currentState) {
        let parsed = JSON.parse(newProps)
        parsed.forEach(v => {
            if (typeof v.price_override === 'string') {
                v.price_override = parseFloat(v.price_override) || null
            }
        })
        variants.value = parsed
        // Update primarySku based on new variants
        const primary = variants.value.find(v => v.is_primary)
        primarySku.value = primary ? primary.sku : ''
    }
}, { deep: true, immediate: true })

// Initialize/Update genSelection when attributes change
watch(() => props.categoryAttributes, (newAttrs) => {
    newAttrs?.forEach(attr => {
        if (attr.generates_variant && !genSelection[attr.id]) {
            genSelection[attr.id] = []
        }
    })
}, { immediate: true })

const variantAttributes = computed(() => {
    return props.categoryAttributes?.filter(attr => {
        // Find per-product setting
        const prodAttr = props.productAttributes?.find(pa => pa.attribute_id === attr.id)
        if (prodAttr) return prodAttr.generates_sku
        
        // Fallback to global attribute setting
        return attr.generates_variant !== false
    }) || []
})

const getMarkup = (attrId, optId) => {
    const markup = localPriceRule.value.markups?.find(m => m.attribute_id === attrId && m.option_id === optId)
    return markup ? markup.markup : 0
}

const setMarkup = (attrId, optId, value) => {
    if (!localPriceRule.value.markups) localPriceRule.value.markups = []
    const idx = localPriceRule.value.markups.findIndex(m => m.attribute_id === attrId && m.option_id === optId)
    if (idx !== -1) {
        if (value === 0 || value === null) {
            localPriceRule.value.markups.splice(idx, 1)
        } else {
            localPriceRule.value.markups[idx].markup = value
        }
    } else if (value !== 0 && value !== null) {
        localPriceRule.value.markups.push({
            attribute_id: attrId,
            option_id: optId,
            markup: value
        })
    }
}

const calculateVariantPrice = (row) => {
    if (localPriceRule.value.pricing_mode === 'manual') return row.price_override || 0
    
    let total = parseFloat(localPriceRule.value.base_price || 0)
    row.values?.forEach(val => {
        total += parseFloat(getMarkup(val.attribute_id, val.option_id))
    })
    return total
}

const handleSelectionChange = (val) => {
    selectedRows.value = val
}

const handleBulkCommand = (cmd) => {
    if (cmd === 'price') applyBulkPrice()
    else if (cmd === 'activate') toggleBulkStatus(true)
    else if (cmd === 'deactivate') toggleBulkStatus(false)
    else if (cmd === 'delete') deleteSelected()
}

const applyBulkPrice = () => {
    ElMessageBox.prompt('Введіть нову ціну для вибраних варіантів', 'Масове редагування', {
        confirmButtonText: 'Застосувати',
        cancelButtonText: 'Скасувати',
        inputPattern: /^\d+(\.\d{1,2})?$/,
        inputErrorMessage: 'Некоректна ціна'
    }).then(({ value }) => {
        selectedRows.value.forEach(row => {
            row.price_override = parseFloat(value)
        })
        ElMessage.success(`Оновлено ціну для ${selectedRows.value.length} варіантів`)
    })
}

const toggleBulkStatus = (status) => {
    selectedRows.value.forEach(row => {
        row.is_active = status
    })
    ElMessage.success(`Статус оновлено для ${selectedRows.value.length} варіантів`)
}

const deleteSelected = () => {
    ElMessageBox.confirm(`Видалити ${selectedRows.value.length} вибраних варіантів?`, 'Видалення', {
        type: 'warning'
    }).then(() => {
        variants.value = variants.value.filter(v => !selectedRows.value.includes(v))
        ElMessage.success('Видалено')
    })
}

const previewCount = computed(() => {
    let count = 1
    let selectedAny = false
    Object.values(genSelection).forEach(arr => {
        if (arr.length > 0) {
            count *= arr.length
            selectedAny = true
        }
    })
    return selectedAny ? count : 0
})

const openGenerator = () => {
    genVisible.value = true
}

const generateSkuPreview = () => {
    return `${props.productCode || 'PROD'}-REF`
}

const generateVariants = () => {
    // Cartesian product logic
    const selectedAttrs = variantAttributes.value.filter(a => genSelection[a.id].length > 0)
    if (!selectedAttrs.length) return
    
    let results = [[]]
    selectedAttrs.forEach(attr => {
        const nextResults = []
        genSelection[attr.id].forEach(optId => {
            const opt = attr.options.find(o => o.id === optId)
            results.forEach(res => {
                nextResults.push([...res, { 
                    attribute_id: attr.id, 
                    option_id: optId, 
                    value: opt.value, 
                    name: attr.name,  // Store for display
                    option: opt,      // Store for display
                    attribute: attr   // Store for display
                }])
            })
        })
        results = nextResults
    })

    const newVariants = results.map(combo => {
        // Generate a more readable SKU suffix based on values
        const skuSuffix = combo.map(c => {
            const val = c.value || c.text_value || ''
            return val.toString().substring(0, 3).toUpperCase()
        }).join('-')
        
        const physicalParams = calculatePhysicalParams(combo)
        
        return {
            sku: `${props.productCode || 'P'}-${skuSuffix}`,
            price_override: null,
            ...physicalParams,
            values: combo.map(c => ({
                attribute_id: c.attribute_id,
                option_id: c.option_id,
                value: c.value || c.text_value,
                attribute: c.attribute,
                option: c.option
            })),
            image_url: null,
            is_primary: false,
            is_active: true
        }
    })

    // Avoid duplicates if possible (simple check by values JSON)
    const existingSignatures = new Set(variants.value.map(v => JSON.stringify(v.values.map(val => val.option_id).sort())))
    const filteredNew = newVariants.filter(nv => !existingSignatures.has(JSON.stringify(nv.values.map(val => val.option_id).sort())))

    variants.value.push(...filteredNew)
    genVisible.value = false
    ElMessage.success(`Додано ${filteredNew.length} нових комбінацій`)
}

const handleVariantImage = (row, file) => {
    // Mock local preview
    row.image_url = URL.createObjectURL(file.raw)
}

const setPrimary = (row) => {
    variants.value.forEach(v => v.is_primary = (v.sku === row.sku))
}

const removeVariant = (idx) => {
    variants.value.splice(idx, 1)
}

const addManualVariant = () => {
    variants.value.push({
        sku: `${props.productCode || 'P'}-CUSTOM`,
        price_override: null,
        length_mm: props.baseDimensions?.length_mm || 0,
        width_mm: props.baseDimensions?.width_mm || 0,
        height_mm: props.baseDimensions?.height_mm || 0,
        weight_kg: props.baseDimensions?.weight_kg || 0,
        values: [],
        image_url: null,
        is_primary: false
    })
}

const calculatePhysicalParams = (combo) => {
    const params = {
        length_mm: props.baseDimensions?.length_mm || 0,
        width_mm: props.baseDimensions?.width_mm || 0,
        height_mm: props.baseDimensions?.height_mm || 0,
        weight_kg: props.baseDimensions?.weight_kg || 0
    }

    if (!props.variantConfig) return params

    // Helper to get value from attribute in combo
    const getAttrVal = (attrId) => {
        const val = combo.find(c => c.attribute_id === attrId)
        return val ? parseFloat(val.value) : null
    }

    // Length, Width, Height
    ['length', 'width', 'height'].forEach(key => {
        const cfg = props.variantConfig[key]
        if (!cfg) return
        if (cfg.source === 'attribute' && cfg.attr_id) {
            const val = getAttrVal(cfg.attr_id)
            if (val !== null) params[`${key}_mm`] = val
        }
    })

    // Weight calculation
    const wCfg = props.variantConfig.weight
    if (wCfg && wCfg.source === 'calc') {
        const baseWeight = parseFloat(wCfg.base_kg) || 0
        const stepKg = parseFloat(wCfg.step_kg) || 0
        const stepMm = parseFloat(wCfg.step_mm) || 100
        const dimVal = params[`${wCfg.dim_key}_mm`] || 0
        
        if (stepMm > 0) {
            params.weight_kg = baseWeight + (dimVal / stepMm) * stepKg
        }
    }

    return params
}

const updateVariantValue = (row, attr, option) => {
    if (!row.values) row.values = []
    const idx = row.values.findIndex(v => v.attribute_id === attr.id)
    const newValue = {
        attribute_id: attr.id,
        option_id: option.id,
        value: option.value,
        attribute: attr,
        option: option
    }
    
    if (idx !== -1) {
        row.values[idx] = newValue
    } else {
        row.values.push(newValue)
    }
    
    // Auto-update SKU if it looks like a generated one
    if (row.sku.includes('-CUSTOM') || row.sku.includes('-REF')) {
        const suffix = row.values.map(v => v.value.substring(0, 3).toUpperCase()).join('-')
        row.sku = `${props.productCode || 'P'}-${suffix}`
    }
}

const getVariantValue = (row, attrId) => {
    return row.values?.find(v => v.attribute_id === attrId)
}

const getOptionLabelForAttr = (row, attr) => {
    const val = getVariantValue(row, attr.id)
    if (!val) return 'Виберіть...'
    
    if (attr.type === 'DIMENSIONS' && val.text_value) {
        const [w, h] = val.text_value.split('x')
        return w && h ? `${w}×${h} мм` : val.text_value
    }
    return val.option?.value || val.value || '?'
}
</script>

<style scoped>
.variants-manager {
    background: var(--el-bg-color);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-light);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    gap: 16px;
}

.actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.pricing-mode-selector {
    display: flex;
    align-items: center;
    background: #f8fafc;
    padding: 4px 12px;
    border-radius: 10px;
    border: 1px solid #eef2f7;
    margin-right: 4px;
}

.title-with-badge h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
}

.variant-uploader {
    width: 50px;
    height: 50px;
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--el-fill-color-light);
}

.variant-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.variant-uploader-icon {
    font-size: 16px;
    color: #8c8c8c;
}

.variant-values {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.attr-gen-row {
    padding: 12px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-extra-light);
}

.preview-section {
    padding: 16px;
    background: var(--el-color-primary-light-9);
    border-radius: 8px;
    border: 1px solid var(--el-color-primary-light-5);
}

.preview-sku {
    margin-top: 8px;
    font-size: 13px;
    color: #595959;
}

.mb-4 { margin-bottom: 16px; }
.mb-2 { margin-bottom: 8px; }
.mt-4 { margin-top: 16px; }
.mr-1 { margin-right: 4px; }
</style>
