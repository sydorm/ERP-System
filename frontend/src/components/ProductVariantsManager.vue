<template>
  <div class="variants-manager">
    <div class="section-header">
      <div class="title-with-badge">
        <h3>Варіанти товару (SKU)</h3>
        <el-tag v-if="variants.length" type="success" effect="plain">{{ variants.length }}</el-tag>
      </div>
      <div class="actions">
        <el-dropdown v-if="selectedRows.length" class="mr-2" @command="handleBulkCommand">
          <el-button type="info">Дії з вибраними ({{ selectedRows.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="price">Змінити ціну</el-dropdown-item>
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

      <el-table-column label="Характеристики" min-width="200">
        <template #default="{ row }">
          <div class="variant-values">
            <el-tag v-for="val in row.values" :key="val.attribute_id" size="small" class="mr-1" effect="light">
              {{ getAttributeLabel(val) }}: {{ getOptionLabel(val) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="price_override" label="Ціна" width="120">
        <template #default="{ row }">
          <el-input-number v-model="row.price_override" :precision="2" :step="100" size="small" controls-position="right" />
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

            <div v-for="attr in categoryAttributes" :key="attr.id" class="attr-gen-row mb-4">
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
    initialVariants: Array
})

const emit = defineEmits(['update:variants'])

const variants = ref(props.initialVariants || [])
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

// Sync FROM parent (when switching products)
watch(() => props.initialVariants, (newVal) => {
    const currentState = JSON.stringify(variants.value)
    const newProps = JSON.stringify(newVal || [])
    
    if (newProps !== currentState) {
        variants.value = JSON.parse(newProps)
        // Update primarySku based on new variants
        const primary = variants.value.find(v => v.is_primary)
        primarySku.value = primary ? primary.sku : ''
    }
}, { deep: true, immediate: true })

// Initialize/Update genSelection when attributes change
watch(() => props.categoryAttributes, (newAttrs) => {
    newAttrs?.forEach(attr => {
        if (!genSelection[attr.id]) {
            genSelection[attr.id] = []
        }
    })
}, { immediate: true })

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
    const selectedAttrs = props.categoryAttributes.filter(a => genSelection[a.id].length > 0)
    if (!selectedAttrs.length) return
    
    let results = [[]]
    selectedAttrs.forEach(attr => {
        const nextResults = []
        genSelection[attr.id].forEach(optId => {
            const opt = attr.options.find(o => o.id === optId)
            results.forEach(res => {
                nextResults.push([...res, { attribute_id: attr.id, option_id: optId, value: opt.value, attr_name: attr.name }])
            })
        })
        results = nextResults
    })

    const newVariants = results.map(combo => {
        const skuSuffix = combo.map(c => c.value.substring(0, 3).toUpperCase()).join('-')
        return {
            sku: `${props.productCode || 'P'}-${skuSuffix}`,
            price_override: null,
            values: combo,
            image_url: null,
            is_primary: false
        }
    })

    variants.value.push(...newVariants)
    genVisible.value = false
    ElMessage.success(`Згенеровано ${newVariants.length} варіантів`)
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
        values: [],
        image_url: null,
        is_primary: false
    })
}

const getAttributeLabel = (val) => val.attr_name || 'Хар-ка'
const getOptionLabel = (val) => val.value || 'Значення'
</script>

<style scoped>
.variants-manager {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #f0f0f0;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.title-with-badge {
    display: flex;
    align-items: center;
    gap: 12px;
}

.title-with-badge h3 {
    margin: 0;
    font-size: 18px;
}

.variant-uploader {
    width: 50px;
    height: 50px;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
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
    background: #f8f9fa;
    border-radius: 8px;
}

.preview-section {
    padding: 16px;
    background: #e6f7ff;
    border-radius: 8px;
    border: 1px solid #91d5ff;
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
