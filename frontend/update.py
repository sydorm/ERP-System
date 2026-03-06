import re

filepath = r"G:\Моделювання\R1\frontend\src\views\Sales\OrderEditor.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

script_match = re.search(r'(<script setup>.*?</script>)', content, re.DOTALL)
if not script_match:
    exit(1)
script_block = script_match.group(1)

new_template = """<template>
  <div class="erp-page-container">
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button type="warning" size="small" :loading="submitting" @click="saveOrder" class="erp-btn-primary">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveOrder" class="erp-btn">Записати</el-button>
        <el-button size="small" @click="saveOrder" class="erp-btn">Провести</el-button>
        <el-dropdown v-if="isEditMode" trigger="click" @command="handleCreateBasedOn" size="small">
          <el-button size="small" class="erp-btn">
            Створити на підставі <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="invoice">Видаткова накладна</el-dropdown-item>
              <el-dropdown-item command="payment">Вхідний платіж</el-dropdown-item>
              <el-dropdown-item command="purchase_order">Замовлення постачальнику</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <div class="erp-doc-info">
            <span class="erp-doc-title">{{ isEditMode ? 'Замовлення покупця ' + form.order_number : 'Замовлення покупця (створення)' }}</span>
        </div>
      </div>
    </div>

    <div class="erp-header-fields">
      <div class="erp-field-row">
        <div class="erp-field">
          <span class="erp-label">Стан:</span>
          <el-select v-model="form.status" size="small" class="erp-input-wrapper status-select" :class="'status-' + form.status">
            <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code" />
          </el-select>
        </div>
        <div class="erp-field">
          <span class="erp-label">Номер:</span>
          <el-input v-model="form.order_number" size="small" class="erp-input-wrapper" disabled />
        </div>
        <div class="erp-field">
          <span class="erp-label">від:</span>
          <el-date-picker v-model="form.order_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" />
        </div>
        <div class="erp-field-links">
           <a href="javascript:void(0)" class="erp-link">Підписи та інші реквізити</a>
        </div>
      </div>
      <div class="erp-field-row">
        <div class="erp-field client-field">
          <span class="erp-label req">Покупець:</span>
          <el-select v-model="form.counterparty_id" filterable size="small" class="erp-input-wrapper" @change="onClientChange">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
      </div>
      <div class="erp-field-row">
        <div class="erp-field">
          <span class="erp-label">Відвантаження:</span>
          <el-date-picker v-model="form.shipping_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" placeholder="Планова" />
        </div>
        <div class="erp-field">
           <a href="javascript:void(0)" class="erp-link">+ Калькуляція замовлення</a>
        </div>
      </div>
    </div>

    <div class="erp-tabs-section">
      <div class="erp-tabs">
        <div class="erp-tab active">Товари, послуги</div>
        <div class="erp-tab">Доставка</div>
        <div class="erp-tab">Додатково</div>
      </div>
      
      <div class="erp-table-toolbar">
        <el-button size="small" class="erp-btn" @click="addLine">Додати</el-button>
        <el-button size="small" class="erp-btn-icon" title="Вгору">↑</el-button>
        <el-button size="small" class="erp-btn-icon" title="Вниз">↓</el-button>
        <el-button size="small" class="erp-btn" :icon="Search" @click="openNomenclatureDialog(form.lines.length - 1 || 0)">Підібрати</el-button>
        <el-button size="small" class="erp-btn-icon" :icon="Setting" title="Налаштування колонок"></el-button>
      </div>

      <div class="erp-field-row erp-warehouse-row">
        <div class="erp-field">
          <span class="erp-label">Склад (резерв): <span class="req">*</span></span>
          <el-select v-model="form.warehouse_id" size="small" class="erp-input-wrapper warehouse-select">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </div>
      </div>
    </div>

    <div class="erp-table-wrapper" v-loading="loading">
      <el-table :data="form.lines" border size="small" class="erp-dense-table" height="100%">
        <el-table-column type="index" label="N" width="40" align="center" />
        <el-table-column label="Номенклатура" min-width="200">
          <template #default="scope">
            <el-select
              v-model="scope.row.product_id"
              filterable
              size="small"
              placeholder=""
              class="erp-cell-input"
              @change="(val) => handleProductChange(val, scope.row)"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Характеристика" min-width="150" v-if="visibleCols.characteristic">
          <template #default="scope">
            <div class="erp-cell-trigger" @click="openVariantSelector(scope.row)">
              <span class="selection-text" v-if="scope.row.variant_id">{{ getVariantLabelByLine(scope.row) }}</span>
              <span class="selection-text virtual" v-else-if="scope.row._virtual_label">{{ scope.row._virtual_label }}</span>
              <span class="placeholder" v-else>...</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Кількість" width="90">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.quantity" :min="0.001" :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" />
          </template>
        </el-table-column>
        <el-table-column label="В резерв" width="80" align="center">
          <template #default="scope">
            <el-checkbox />
          </template>
        </el-table-column>
        <el-table-column label="Ціна" width="100">
          <template #default="scope">
            <el-input-number size="small" v-model="scope.row.price" :min="0" :precision="2" :controls="false" @change="updateLineTotal(scope.row)" class="erp-cell-input num" />
          </template>
        </el-table-column>
        <el-table-column label="Сума" width="100" align="right">
          <template #default="scope">
            <span class="erp-cell-text">{{ formatCurrency(scope.row.total) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Специфікація" min-width="100">
           <template #default>
              <span class="placeholder">...</span>
           </template>
        </el-table-column>
        <el-table-column label="" width="40" align="center" fixed="right">
          <template #default="scope">
            <el-button type="danger" :icon="Delete" link size="small" @click="removeLine(scope.$index)" style="padding:0;height:auto;" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="erp-footer">
      <div class="erp-footer-left">
        <el-input
          v-model="form.comment"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 3 }"
          placeholder="Коментар..."
          class="erp-comment-input"
        />
      </div>
      <div class="erp-footer-right">
        <div class="erp-total-row">
            <span class="erp-total-label">Знижка руч., %:</span>
            <el-input-number v-model="form.discount_percent" :min="0" :max="100" :precision="1" :controls="false" size="small" class="erp-total-input" />
            <span class="erp-total-label ml-4">ПДВ:</span>
            <span class="erp-total-value">0,00</span>
        </div>
        <div class="erp-total-row">
            <span class="erp-total-label">Знижка руч., Σ:</span>
            <el-input-number :model-value="discountAmount" disabled :controls="false" size="small" class="erp-total-input" />
            <span class="erp-total-label ml-4">Всього:</span>
            <span class="erp-total-value sum">{{ formatCurrency(totalAmount) }}</span>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="nomenclatureDialogVisible"
      title="Вибір номенклатури"
      width="800px"
      destroy-on-close
    >
      <el-input
        v-model="nomenclatureSearch"
        placeholder="Пошук за назвою або SKU..."
        :prefix-icon="Search"
        clearable
        style="margin-bottom: 16px"
      />
      <el-table
        :data="filteredProducts" border height="400px" highlight-current-row @current-change="onDialogProductSelect"
      >
        <el-table-column property="sku" label="SKU" width="120" />
        <el-table-column property="name" label="Назва" min-width="250" />
        <el-table-column property="category" label="Категорія" width="150" />
        <el-table-column label="Ціна" width="120" align="right">
          <template #default="scope">
            {{ formatShort(scope.row.price) }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="nomenclatureDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" :disabled="!selectedDialogProduct" @click="confirmDialogSelection">
          Вибрати
        </el-button>
      </template>
    </el-dialog>

    <VariantSelectorDialog
      v-model="variantSelectorVisible"
      :product="selectedProductForSelector"
      @select="onVariantSelected"
      @clear="clearVirtualVariant(activeLineForSelector)"
    />
  </div>
</template>"""

new_style = """<style scoped>
.erp-page-container {
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
  background-color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif;
}
.erp-toolbar {
  display: flex; align-items: center; padding: 6px 12px;
  background-color: #fcfcfc; border-bottom: 1px solid #dcdfe6; flex-shrink: 0;
}
.erp-toolbar-left { display: flex; align-items: center; gap: 8px; }
.erp-btn, .erp-btn-icon, .erp-btn-primary {
  border-radius: 2px !important; font-size: 13px !important; height: 28px !important;
  padding: 0 12px !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; color: #303133 !important;
}
.erp-btn:hover, .erp-btn-icon:hover { background-color: #f5f7fa !important; border-color: #c0c4cc !important; }
.erp-btn-primary {
  background-color: #fdf6ec !important; border-color: #e6a23c !important;
  color: #8a6d3b !important; font-weight: 600 !important;
}
.erp-btn-primary:hover { background-color: #faecd8 !important; }
.erp-btn-icon { padding: 0 8px !important; }
.erp-doc-info { margin-left: 16px; display: flex; align-items: center; }
.erp-doc-title { font-size: 14px; font-weight: 600; color: #303133; }
.erp-header-fields {
  background-color: #f6f7f9; padding: 12px 16px 8px 16px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px;
}
.erp-field-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.erp-field { display: flex; align-items: center; }
.erp-label {
  font-size: 13px; color: #606266; width: 105px; text-align: left; padding-right: 8px;
}
.erp-label.req { color: #f56c6c; text-decoration: underline dotted #fbc4c4; text-underline-offset: 3px; }
.erp-input-wrapper { width: 160px; }
.client-field .erp-input-wrapper { width: 320px; }
.erp-header-fields :deep(.el-input__wrapper), .erp-header-fields :deep(.el-select__wrapper) {
  border-radius: 2px !important; box-shadow: none !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; min-height: 26px !important; height: 26px !important; padding: 0 8px !important;
}
.erp-header-fields :deep(.el-input__inner) {
  height: 24px !important; line-height: 24px !important; font-size: 13px !important; color: #303133 !important;
}
.erp-header-fields :deep(.el-select__wrapper) { min-height: 26px !important; }
.erp-header-fields :deep(.el-input__wrapper:focus-within), .erp-header-fields :deep(.el-select__wrapper.is-focus) {
  border-color: #c0c4cc !important; box-shadow: inset 0 0 2px rgba(0,0,0,0.1) !important;
}
.erp-link { font-size: 13px; color: #409eff; text-decoration: none; margin-left: 8px; }
.erp-link:hover { text-decoration: underline; }
.erp-tabs-section {
  display: flex; flex-direction: column; background-color: #f6f7f9; padding: 0 16px; flex-shrink: 0;
}
.erp-tabs { display: flex; border-bottom: 2px solid #e6a23c; margin-bottom: 8px; margin-top: 4px; }
.erp-tab {
  padding: 6px 16px; font-size: 13px; cursor: pointer; color: #606266;
  background-color: #e4e7ed; border: 1px solid #dcdfe6; border-bottom: none;
  border-radius: 4px 4px 0 0; margin-right: 4px;
}
.erp-tab.active { background-color: #fdf6ec; border-color: #e6a23c; color: #8a6d3b; font-weight: 600; }
.erp-table-toolbar { display: flex; gap: 6px; margin-bottom: 6px; }
.erp-warehouse-row { margin-bottom: 6px; }
.warehouse-select { width: 250px; }
.erp-table-wrapper { flex: 1; padding: 0 16px; overflow: hidden; margin-bottom: 12px; }
.erp-dense-table { width: 100%; border: 1px solid #dcdfe6 !important; }
.erp-dense-table :deep(th.el-table__cell) {
  background-color: #f5f7fa !important; color: #606266; font-size: 12px;
  font-weight: 600; padding: 4px 0 !important; border-bottom: 1px solid #dcdfe6 !important; border-right: 1px solid #dcdfe6 !important;
}
.erp-dense-table :deep(td.el-table__cell) {
  padding: 0 !important; border-bottom: 1px solid #ebeef5 !important; border-right: 1px solid #ebeef5 !important;
}
.erp-dense-table :deep(.cell) { padding: 0 6px !important; line-height: 24px !important; }
.erp-cell-input :deep(.el-input__wrapper), .erp-cell-input :deep(.el-select__wrapper) {
  box-shadow: none !important; border: none !important; background-color: transparent !important;
  padding: 0 !important; border-radius: 0 !important; min-height: 24px !important; height: 24px !important;
}
.erp-cell-input :deep(.el-input__inner) { font-size: 13px !important; height: 24px !important; line-height: 24px !important; }
.erp-cell-input.num :deep(.el-input__inner) { text-align: right !important; }
.erp-cell-trigger { width: 100%; height: 24px; display: flex; align-items: center; font-size: 13px; cursor: pointer; }
.erp-cell-text { font-size: 13px; line-height: 24px; }
.virtual { color: #67c23a; }
.placeholder { color: #c0c4cc; }
.erp-footer {
  display: flex; justify-content: space-between; padding: 12px 16px;
  background-color: #f6f7f9; border-top: 1px solid #dcdfe6; flex-shrink: 0; gap: 20px;
}
.erp-footer-left { flex: 1; max-width: 500px; }
.erp-comment-input :deep(.el-textarea__inner) {
  border-radius: 2px; border: 1px solid #dcdfe6; font-size: 13px; padding: 6px;
}
.erp-footer-right { display: flex; flex-direction: column; gap: 6px; width: 320px; }
.erp-total-row { display: flex; align-items: center; justify-content: flex-end; }
.erp-total-label { font-size: 13px; color: #606266; width: 110px; text-align: right; margin-right: 8px; }
.ml-4 { margin-left: 16px; width: 40px; }
.erp-total-input { width: 80px; }
.erp-total-input :deep(.el-input__wrapper) {
  border-radius: 2px !important; box-shadow: none !important; border: 1px solid #dcdfe6 !important;
  height: 24px !important; min-height: 24px !important; padding: 0 6px !important;
}
.erp-total-input :deep(.el-input__inner) { font-size: 13px !important; height: 24px !important; text-align: right; }
.erp-total-value { width: 90px; text-align: right; font-size: 13px; font-weight: 600; color: #303133; }
.erp-total-value.sum { font-weight: 700; font-size: 15px; }
.req { color: #f56c6c; }
</style>"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_template + "\n\n" + script_block + "\n\n" + new_style)

print("Updated OrderEditor.vue successfully.")
