<template>
  <div class="nomenclature-drawers">
    <!-- ===== SIDE DRAWER (INFO) ===== -->
    <el-drawer
      :model-value="visible"
      title="Інформація про товар"
      size="480px"
      direction="rtl"
      :destroy-on-close="true"
      @update:model-value="$emit('update:visible', $event)"
    >
      <div v-if="product" class="drawer-content-dense">
        <div class="drawer-header-block">
          <h3>{{ product.name }}</h3>
          <p class="drawer-sku">{{ product.sku }} <span class="sku-divider">·</span> {{ getUomName(product.unit_of_measure) }}</p>
        </div>

        <el-divider />

        <div class="drawer-section">
          <h4>Запаси по складах</h4>
          <el-table :data="warehouseStock" style="width: 100%" size="small">
            <el-table-column prop="name" label="Склад" />
            <el-table-column prop="balance" label="Залишок" align="right">
              <template #default="{ row }">{{ row.balance }} {{ getUomName(product.unit_of_measure) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <el-divider />

        <div class="drawer-section">
          <h4>Останні рухи</h4>
          <el-table :data="productMovements" style="width: 100%" size="small">
            <el-table-column prop="date" label="Дата" width="100" />
            <el-table-column prop="type" label="Операція" width="100" />
            <el-table-column prop="qty" label="К-сть" align="right" width="70" />
            <el-table-column prop="note" label="Коментар" />
          </el-table>
        </div>
      </div>
    </el-drawer>

    <!-- ===== PRODUCT FORM DRAWER (CREATE & EDIT) ===== -->
    <el-drawer
      :model-value="formVisible"
      :title="isEditMode ? 'Редагувати позицію' : 'Створити нову позицію'"
      size="520px"
      direction="rtl"
      @update:model-value="$emit('update:formVisible', $event)"
    >
      <div class="form-drawer-content">
        <el-form :model="formModel" label-position="top" size="default">
          <el-form-item label="Назва номенклатури" required>
            <el-input 
              :model-value="formModel.name" 
              placeholder="Напр: Профіль 20x20x1.2" 
              @update:model-value="$emit('update:formModel', { ...formModel, name: $event })"
            />
            <el-button 
              type="primary" 
              link 
              style="margin-top: 6px;"
              @click="$emit('run-ai-fill')"
            >
              🤖 Автозаповнення через AI
            </el-button>
          </el-form-item>

          <el-form-item label="Артикул (SKU)" required>
            <el-input 
              :model-value="formModel.sku" 
              placeholder="Напр: PRF-20X20" 
              @update:model-value="$emit('update:formModel', { ...formModel, sku: $event })"
            />
          </el-form-item>

          <el-form-item label="Категорія" required>
            <el-select 
              :model-value="formModel.category" 
              style="width: 100%"
              @update:model-value="$emit('update:formModel', { ...formModel, category: $event })"
            >
              <el-option
                v-for="cat in categoryOptions"
                :key="cat.code"
                :label="cat.name"
                :value="cat.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Одиниця виміру" required>
            <el-select 
              :model-value="formModel.unit_of_measure" 
              style="width: 100%"
              @update:model-value="$emit('update:formModel', { ...formModel, unit_of_measure: $event })"
            >
              <el-option
                v-for="uom in uomOptions"
                :key="uom.code"
                :label="uom.name"
                :value="uom.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Ціна (грн)">
            <el-input-number 
              :model-value="formModel.price" 
              :min="0" 
              style="width: 100%" 
              @update:model-value="$emit('update:formModel', { ...formModel, price: $event })"
            />
          </el-form-item>

          <el-form-item label="Початковий залишок">
            <el-input-number 
              :model-value="formModel.stock_balance" 
              :min="0" 
              style="width: 100%" 
              @update:model-value="$emit('update:formModel', { ...formModel, stock_balance: $event })"
            />
          </el-form-item>

          <el-form-item label="Мінімальний залишок">
            <el-input-number 
              :model-value="formModel.min_stock" 
              :min="0" 
              style="width: 100%" 
              @update:model-value="$emit('update:formModel', { ...formModel, min_stock: $event })"
            />
          </el-form-item>
        </el-form>

        <div class="form-drawer-actions" style="margin-top: 24px; display: flex; gap: 12px;">
          <el-button @click="$emit('update:formVisible', false)">Скасувати</el-button>
          <el-button type="primary" @click="$emit('save')" :loading="saveLoading">
            {{ isEditMode ? 'Зберегти' : 'Створити' }}
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  formVisible: Boolean,
  product: Object,
  warehouseStock: Array,
  productMovements: Array,
  isEditMode: Boolean,
  formModel: Object,
  saveLoading: Boolean,
  categoryOptions: Array,
  uomOptions: Array,
  getUomName: Function
})

defineEmits(['update:visible', 'update:formVisible', 'update:formModel', 'save', 'run-ai-fill'])
</script>

<style scoped>
.drawer-content-dense {
  padding: 0 20px;
}
.drawer-header-block h3 {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
}
.drawer-sku {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}
.sku-divider {
  margin: 0 4px;
}
.drawer-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 12px;
}

.form-drawer-content {
  padding: 0 20px;
}
.form-drawer-actions {
  padding-bottom: 24px;
}
</style>
