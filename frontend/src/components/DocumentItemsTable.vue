<template>
  <div class="document-items-table">
    <div class="tab-toolbar" v-if="!readOnly">
      <el-button size="small" class="erp-btn" @click="$emit('add-line')">Додати</el-button>
      <div class="tab-toolbar-right" v-if="showWarehouse">
        <span class="erp-label">Склад:</span>
        <el-select v-model="localWarehouseId" size="small" class="warehouse-select" @change="$emit('update:warehouseId', $event)">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
      </div>
    </div>

    <div class="erp-table-wrapper">
      <el-table :data="items" border size="small" class="erp-dense-table" height="100%">
        <el-table-column type="index" label="N" width="40" align="center" />
        
        <!-- Номенклатура -->
        <el-table-column label="Номенклатура" min-width="220">
          <template #default="scope">
            <el-select 
              v-model="scope.row.product_id" 
              filterable 
              size="small" 
              placeholder="Виберіть товар..." 
              class="erp-cell-input" 
              @change="(val) => handleProductChange(val, scope.row)"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>

        <!-- Характеристика -->
        <el-table-column label="Характеристика" min-width="160" v-if="showCharacteristics">
          <template #default="scope">
            <div 
              class="erp-cell-trigger" 
              :class="{ 'disabled': !scope.row.product_id }"
              @click="openVariantSelector(scope.row)"
            >
              <span class="selection-text" v-if="scope.row.variant_id">{{ getVariantLabelByLine(scope.row) }}</span>
              <span class="selection-text virtual" v-else-if="scope.row._virtual_label">{{ scope.row._virtual_label }}</span>
              <span class="placeholder" v-else-if="scope.row.product_id">Налаштувати...</span>
              <span class="placeholder disabled" v-else>Спочатку виберіть товар</span>
            </div>
          </template>
        </el-table-column>

        <!-- К-ть -->
        <el-table-column label="К-ть" width="100">
          <template #default="scope">
            <el-input-number 
              size="small" 
              v-model="scope.row.quantity" 
              :min="0.001" 
              :precision="3" 
              :controls="false" 
              @change="onLineChange(scope.row)" 
              class="erp-cell-input num" 
              style="width:100%" 
            />
          </template>
        </el-table-column>

        <!-- Ціна -->
        <el-table-column label="Ціна" width="110" v-if="showPrice">
          <template #default="scope">
            <el-input-number 
              size="small" 
              v-model="scope.row.price" 
              :min="0" 
              :precision="2" 
              :controls="false" 
              @change="onLineChange(scope.row)" 
              class="erp-cell-input num" 
              style="width:100%" 
            />
          </template>
        </el-table-column>

        <!-- Сума -->
        <el-table-column label="Сума" width="110" v-if="showPrice">
          <template #default="scope">
            <el-input-number 
              size="small" 
              v-model="scope.row.total" 
              :min="0" 
              :precision="2" 
              :controls="false" 
              @change="onTotalChange(scope.row)" 
              class="erp-cell-input num sum-input" 
              style="width:100%" 
            />
          </template>
        </el-table-column>

        <!-- Специфікація (лише для продажу) -->
        <el-table-column label="Специфікація" min-width="150" v-if="showSpecification">
          <template #default="scope">
            <el-select 
              v-model="scope.row.specification_id" 
              size="small" 
              placeholder="За замовчуванням" 
              clearable 
              class="erp-cell-input" 
              style="width:100%"
              @change="onLineChange(scope.row)"
            >
              <el-option 
                v-for="s in (specsCache[scope.row.product_id] || [])" 
                :key="s.id" 
                :label="s.is_default ? s.name + ' (Авто)' : s.name" 
                :value="s.id" 
              />
            </el-select>
          </template>
        </el-table-column>

        <!-- Склад (якщо окремо в рядку) -->
        <el-table-column label="Склад" min-width="150" v-if="mode === 'production' && showWarehouse">
           <template #default="scope">
            <el-select v-model="scope.row.warehouse_id" size="small" class="erp-cell-input" @change="onLineChange(scope.row)">
              <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
            </el-select>
          </template>
        </el-table-column>

        <!-- Дії -->
        <el-table-column label="" width="40" align="center" fixed="right" v-if="!readOnly">
          <template #default="scope">
            <el-button 
              type="danger" 
              :icon="Delete" 
              link 
              size="small" 
              @click="$emit('remove-line', scope.$index)" 
              style="padding:0;height:auto;" 
            />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Variant Selector Dialog -->
    <VariantSelectorDialog 
      v-model="variantSelectorVisible" 
      :product="selectedProductForSelector" 
      :initial-variant-id="activeLineForSelector?.variant_id"
      @select="onVariantSelected" 
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import VariantSelectorDialog from '@/views/Sales/VariantSelectorDialog.vue'

const props = defineProps({
  items: { type: Array, required: true },
  products: { type: Array, default: () => [] },
  warehouses: { type: Array, default: () => [] },
  warehouseId: { type: String, default: '' },
  specsCache: { type: Object, default: () => ({}) },
  showCharacteristics: { type: Boolean, default: true },
  showPrice: { type: Boolean, default: true },
  showSpecification: { type: Boolean, default: false },
  showWarehouse: { type: Boolean, default: false },
  readOnly: { type: Boolean, default: false },
  mode: { type: String, default: 'sale' } // purchase | sale | production | invoice
})

const emit = defineEmits(['change', 'add-line', 'remove-line', 'update:warehouseId', 'product-change'])

const localWarehouseId = ref(props.warehouseId)
watch(() => props.warehouseId, (val) => { localWarehouseId.value = val })

// Variant Selector State
const variantSelectorVisible = ref(false)
const selectedProductForSelector = ref(null)
const activeLineForSelector = ref(null)

const handleProductChange = (productId, line) => {
  const product = props.products.find(p => p.id === productId)
  if (product) {
    line.price = product.price || 0
    line.variant_id = null
    line._virtual_label = null
    line.values = []
    
    // Auto-calculate total
    updateLineTotal(line)
    
    // Emit product change for parent to handle things like fetching specs
    emit('product-change', { productId, line })
    emit('change', line)
  }
}

const onLineChange = (line) => {
  updateLineTotal(line)
  emit('change', line)
}

const onTotalChange = (line) => {
  if (line.quantity > 0) {
    line.price = parseFloat((line.total / line.quantity).toFixed(2))
  }
  emit('change', line)
}

const updateLineTotal = (line) => {
  line.total = parseFloat(((line.quantity || 0) * (line.price || 0)).toFixed(2))
}

const openVariantSelector = (line) => {
  if (props.readOnly || !line.product_id) return
  
  const product = props.products.find(p => p.id === line.product_id)
  if (!product) return
  
  // Only open if product has attributes or variants
  const hasVariants = (product.variants && product.variants.length > 0) || 
                      (product.product_attributes && product.product_attributes.length > 0)
  
  if (hasVariants) {
    selectedProductForSelector.value = product
    activeLineForSelector.value = line
    variantSelectorVisible.value = true
  }
}

const onVariantSelected = (variant) => {
  if (activeLineForSelector.value) {
    activeLineForSelector.value.variant_id = variant.id
    activeLineForSelector.value.values = variant.values || []
    
    // Handle price override from variant
    if (variant.price_override) {
        activeLineForSelector.value.price = Number(variant.price_override)
        updateLineTotal(activeLineForSelector.value)
    }
    
    // Set virtual label if it's a virtual variant
    if (!variant.id && variant.values) {
        activeLineForSelector.value._virtual_label = variant.values
            .map(v => v.option?.value || v.text_value)
            .filter(Boolean)
            .join(', ')
    } else {
        activeLineForSelector.value._virtual_label = null
    }
    
    emit('change', activeLineForSelector.value)
  }
}

const getVariantLabelByLine = (line) => {
  if (line._virtual_label) return line._virtual_label
  if (!line.variant_id || !line.product_id) return ''
  
  const product = props.products.find(p => p.id === line.product_id)
  if (!product || !product.variants) return ''
  
  const variant = product.variants.find(v => v.id === line.variant_id)
  if (!variant) return ''
  
  if (variant.values && variant.values.length > 0) {
    return variant.values.map(v => v.option?.value || v.text_value).filter(Boolean).join(', ')
  }
  return variant.sku || ''
}
</script>

<style scoped>
.document-items-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f6f7f9;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.tab-toolbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}

.erp-label {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.warehouse-select {
  width: 200px;
}

.erp-table-wrapper {
  flex: 1;
  overflow: hidden;
}

.erp-dense-table {
  width: 100%;
}

.erp-dense-table :deep(th.el-table__cell) {
  background-color: #f5f7fa !important;
  color: #606266;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 0 !important;
}

.erp-dense-table :deep(td.el-table__cell) {
  padding: 0 !important;
}

.erp-cell-input :deep(.el-input__wrapper), 
.erp-cell-input :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid transparent !important;
  background-color: transparent !important;
  padding: 0 8px !important;
  height: 32px !important;
}

.erp-cell-input :deep(.el-input__wrapper:focus-within), 
.erp-cell-input :deep(.el-input__wrapper:hover) {
  border-color: #dcdfe6 !important;
  background-color: #fff !important;
}

.erp-cell-trigger {
  padding: 0 8px;
  height: 32px;
  line-height: 32px;
  cursor: pointer;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.2s;
}

.erp-cell-trigger:hover:not(.disabled) {
  background-color: #fff;
  border-color: #dcdfe6;
}

.erp-cell-trigger.disabled {
  cursor: not-allowed;
  color: #c0c4cc;
}

.selection-text {
  color: #303133;
}

.selection-text.virtual {
  color: #6366f1;
  font-style: italic;
}

.placeholder {
  color: #909399;
}

.placeholder.disabled {
  font-size: 11px;
}

.num :deep(.el-input__inner) {
  text-align: right !important;
}
</style>
