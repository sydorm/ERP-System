<template>
  <div class="document-items-table">
    <div class="tab-toolbar" v-if="!readOnly">
      <el-button size="small" class="erp-btn" @click="$emit('add-line')">Додати</el-button>
      <el-button size="small" class="erp-btn" @click="triggerExcelImport">
        <el-icon><Upload /></el-icon>&nbsp;↑ Імпорт
      </el-button>
      <input type="file" ref="excelInput" style="display:none" accept=".xlsx,.csv" @change="handleExcelFile" />
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
            <div v-if="mode === 'purchase' && getSupplierSku(scope.row)" class="supplier-line-meta">
              Артикул постачальника: {{ getSupplierSku(scope.row) }}
            </div>
            <button
              v-if="mode === 'purchase' && getSupplierOrderLink(scope.row)"
              class="supplier-order-link"
              type="button"
              @click.stop="openSupplierOrderLink(scope.row)"
            >
              <el-icon><TopRight /></el-icon>
              {{ getSupplierOrderActionLabel(scope.row) }}
            </button>
            <div v-if="mode === 'purchase' && scope.row.stock_warning" class="stock-warning">
              ⚠️ На складі вже є {{ scope.row.current_stock }} шт — мін. запас {{ scope.row.min_stock }} шт
            </div>
            <div v-if="scope.row.not_found" class="not-found-warning">
              Товар з артикулом "{{ scope.row.import_sku }}" не знайдено
            </div>
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
              <span class="selection-text" v-if="scope.row.variant_id || scope.row.values?.length || scope.row._virtual_label">
                {{ getVariantLabelByLine(scope.row) }}
              </span>
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
              :model-value="Number(scope.row.quantity) || 0" 
              @update:model-value="val => { scope.row.quantity = val; onLineChange(scope.row) }"
              :min="0.001" 
              :precision="3" 
              :controls="false" 
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
              :model-value="Number(scope.row.price) || 0" 
              @update:model-value="val => { scope.row.price = val; onLineChange(scope.row) }"
              :min="0" 
              :precision="2" 
              :controls="false" 
              class="erp-cell-input num" 
              style="width:100%" 
            />
            <div v-if="mode === 'purchase' && scope.row.last_price" class="price-comparison">
              Минулого разу: {{ scope.row.last_price }} грн
              <span :class="getPriceDiffClass(scope.row)">
                {{ getPriceDiffIcon(scope.row) }} {{ getPriceDiffPercent(scope.row) }}%
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- Сума -->
        <el-table-column label="Сума" width="110" v-if="showPrice">
          <template #default="scope">
            <el-input-number 
              size="small" 
              :model-value="Number(scope.row.total) || 0" 
              @update:model-value="val => { scope.row.total = val; onTotalChange(scope.row) }"
              :min="0" 
              :precision="2" 
              :controls="false" 
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
        <el-table-column label="" width="46" align="center" fixed="right" v-if="!readOnly">
          <template #default="scope">
            <el-dropdown trigger="click" @command="cmd => handleLineCommand(cmd, scope.row, scope.$index)">
              <el-button :icon="MoreFilled" link size="small" class="row-menu-btn" @click.stop />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="open-product" :disabled="!scope.row.product_id">
                    Відкрити картку товару
                  </el-dropdown-item>
                  <el-dropdown-item command="open-supplier" :disabled="!getSupplierOrderLink(scope.row)">
                    {{ getSupplierOrderActionLabel(scope.row) }}
                  </el-dropdown-item>
                  <el-dropdown-item command="copy-supplier-sku" :disabled="!getSupplierSku(scope.row)">
                    Скопіювати артикул постачальника
                  </el-dropdown-item>
                  <el-dropdown-item command="remove" divided>
                    Видалити рядок
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Variant Selector Dialog -->
    <VariantSelectorDialog 
      v-model="variantSelectorVisible" 
      :product="selectedProductForSelector" 
      :initial-variant-id="activeLineForSelector?.variant_id"
      :initial-values="activeLineForSelector?.values"
      @select="onVariantSelected" 
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { MoreFilled, TopRight, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import VariantSelectorDialog from '@/views/Sales/VariantSelectorDialog.vue'
import * as XLSX from 'xlsx'

const props = defineProps({
  items: { type: Array, required: true },
  products: { type: Array, default: () => [] },
  warehouses: { type: Array, default: () => [] },
  supplierId: { type: String, default: '' },
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
const router = useRouter()

const localWarehouseId = ref(props.warehouseId)
watch(() => props.warehouseId, (val) => { localWarehouseId.value = val })

// Variant Selector State
const variantSelectorVisible = ref(false)
const selectedProductForSelector = ref(null)
const activeLineForSelector = ref(null)
const excelInput = ref(null)

const handleProductChange = (productId, line) => {
  const product = props.products.find(p => p.id === productId)
  if (product) {
    line.price = product.price || 0
    line.variant_id = null
    line._virtual_label = null
    line.values = []
    
    // Stock warning check
    if (props.mode === 'purchase') {
      line.current_stock = product.current_stock || 15 // Mock if not present
      line.min_stock = product.min_stock || 5 // Mock if not present
      line.stock_warning = line.current_stock > line.min_stock
    }

    // Auto-calculate total
    updateLineTotal(line)
    
    // Emit product change for parent to handle things like fetching specs
    emit('product-change', { productId, line })
    emit('line-change', line)
    emit('change', line)
  }
}

const getProductByLine = (line) => props.products.find(p => p.id === line.product_id) || null

const getSupplierLinkByLine = (line) => {
  const product = getProductByLine(line)
  const links = Array.isArray(product?.supplier_links) ? product.supplier_links : []
  return links.find(link =>
    link?.is_active !== false
    && link?.order_url
    && link?.supplier_id === props.supplierId
  ) || null
}

const getSupplierOrderLink = (line) => getSupplierLinkByLine(line)?.order_url || ''
const getSupplierSku = (line) => getSupplierLinkByLine(line)?.supplier_sku || ''
const getSupplierOrderActionLabel = (line) => {
  const type = getSupplierLinkByLine(line)?.url_type || ''
  return ['Кабінет замовлення', 'Кабінет розкрою'].includes(type)
    ? 'Відкрити кабінет постачальника'
    : 'Оформити на сайті постачальника'
}

const openSupplierOrderLink = (line) => {
  const url = getSupplierOrderLink(line)
  if (!url) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

const copySupplierSku = async (line) => {
  const sku = getSupplierSku(line)
  if (!sku) return
  try {
    await navigator.clipboard.writeText(sku)
    ElMessage.success('Артикул постачальника скопійовано')
  } catch {
    ElMessage.info(sku)
  }
}

const handleLineCommand = (command, line, index) => {
  if (command === 'open-product' && line.product_id) {
    router.push(`/inventory/nomenclature/${line.product_id}`)
    return
  }
  if (command === 'open-supplier') {
    openSupplierOrderLink(line)
    return
  }
  if (command === 'copy-supplier-sku') {
    copySupplierSku(line)
    return
  }
  if (command === 'remove') {
    emit('remove-line', index)
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
    
    // Set label for display in the table
    if (variant.values && variant.values.length > 0) {
        activeLineForSelector.value._virtual_label = variant.values
            .map(v => v.option?.value || v.text_value)
            .filter(Boolean)
            .join(', ')
            
        // Also extract width/height for database storage
        const dimVal = variant.values.find(v => v.width || v.height)
        if (dimVal) {
          activeLineForSelector.value.characteristic_width = dimVal.width
          activeLineForSelector.value.characteristic_height = dimVal.height
        }
    } else {
        activeLineForSelector.value._virtual_label = variant.sku || null
    }
    
    emit('change', activeLineForSelector.value)
  }
}
const getVariantLabelByLine = (line) => {
  // 1. Try cached label
  if (line._virtual_label) return line._virtual_label
  
  // 2. Try stored values (JSON)
  if (line.values && line.values.length > 0) {
    const label = line.values.map(v => v.option?.value || v.text_value).filter(Boolean).join(', ')
    if (label) return label
  }
  
  // 3. Try to find variant in product data
  if (line.variant_id && line.product_id) {
    const product = props.products.find(p => p.id === line.product_id)
    const variant = product?.variants?.find(v => v.id === line.variant_id)
    if (variant) {
      if (variant.values?.length) {
        return variant.values.map(v => v.option?.value || v.text_value).filter(Boolean).join(', ')
      }
      return variant.sku || ''
    }
  }
  
  return ''
}

// Excel Import
const triggerExcelImport = () => excelInput.value.click()

const handleExcelFile = (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (ev) => {
    const data = new Uint8Array(ev.target.result)
    const workbook = XLSX.read(data, { type: 'array' })
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const json = XLSX.utils.sheet_to_json(worksheet)
    
    processImportedJson(json)
    excelInput.value.value = '' // Clear
  }
  reader.readAsArrayBuffer(file)
}

const processImportedJson = (json) => {
  json.forEach(row => {
    // Assume columns: Артикул | Кількість | Ціна
    const sku = row['Артикул'] || row['SKU']
    const qty = parseFloat(row['Кількість'] || row['Qty'] || 1)
    const price = parseFloat(row['Ціна'] || row['Price'] || 0)
    
    const product = props.products.find(p => p.sku === sku || p.name === sku)
    if (product) {
      const newLine = {
        product_id: product.id,
        quantity: qty,
        price: price || product.price || 0,
        total: qty * (price || product.price || 0),
        values: []
      }
      props.items.push(newLine)
      handleProductChange(product.id, newLine)
    } else {
      props.items.push({
        product_id: '',
        import_sku: sku,
        not_found: true,
        quantity: qty,
        price: price,
        total: qty * price,
        values: []
      })
    }
  })
  ElMessage.success(`Імпортовано ${json.length} рядків`)
}

// Helpers for price diff
const getPriceDiffPercent = (line) => {
  if (!line.last_price || !line.price) return 0
  const diff = ((line.price - line.last_price) / line.last_price) * 100
  return diff.toFixed(0)
}

const getPriceDiffClass = (line) => {
  const diff = line.price - line.last_price
  if (diff > 0) return 'text-red'
  if (diff < 0) return 'text-green'
  return ''
}

const getPriceDiffIcon = (line) => {
  const diff = line.price - line.last_price
  if (diff > 0) return '↑'
  if (diff < 0) return '↓'
  return ''
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

.supplier-line-meta {
  margin: -2px 8px 5px;
  color: #64748b;
  font-size: 11px;
  line-height: 1.2;
}

.supplier-order-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0 8px 7px;
  padding: 3px 8px;
  border: 1px solid #BFDBFE;
  border-radius: 999px;
  background: #EFF6FF;
  color: #1D4ED8;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}

.supplier-order-link:hover {
  background: #DBEAFE;
}

.row-menu-btn {
  padding: 0 !important;
  height: 24px !important;
}

.num :deep(.el-input__inner) {
  text-align: right !important;
  font-family: 'JetBrains Mono', monospace;
}

.stock-warning {
  font-size: 11px; color: #b45309; background: #fffbeb; padding: 2px 8px;
  border-radius: 4px; margin: 2px 8px 4px; border: 1px solid #fef3c7;
}

.not-found-warning {
  font-size: 11px; color: #dc2626; background: #fef2f2; padding: 2px 8px;
  border-radius: 4px; margin: 2px 8px 4px; border: 1px solid #fee2e2;
}

.price-comparison {
  font-size: 10px; color: #94a3b8; margin-top: 2px; text-align: right;
  padding-right: 8px;
}
.text-green { color: #10b981 !important; font-weight: 600; }
.text-red { color: #ef4444 !important; font-weight: 600; }
</style>
