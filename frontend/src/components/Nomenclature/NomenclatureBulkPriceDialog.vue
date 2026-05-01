<template>
  <el-dialog
    :model-value="visible"
    title="Масове коригування цін"
    width="480px"
    class="bulk-price-dialog"
    @close="$emit('update:visible', false)"
  >
    <div class="bulk-price-content">
      <div class="selection-info">
        Ви обрали <b>{{ count }}</b> товарів для зміни ціни.
      </div>

      <div class="adjustment-form">
        <el-form label-position="top">
          <el-form-item label="Тип коригування">
            <el-radio-group v-model="form.type" class="premium-radio-group">
              <el-radio-button label="percentage">Відсоток (%)</el-radio-button>
              <el-radio-button label="fixed">Фіксована сума</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Операція">
            <el-radio-group v-model="form.operation" class="premium-radio-group">
              <el-radio-button label="increase">Збільшити (+)</el-radio-button>
              <el-radio-button label="decrease">Зменшити (-)</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Значення">
            <el-input-number 
              v-model="form.value" 
              :precision="form.type === 'percentage' ? 1 : 2" 
              :step="1" 
              class="full-width"
              :min="0"
            />
          </el-form-item>
        </el-form>
      </div>

      <div class="price-preview" v-if="form.value > 0">
        <div class="preview-icon">💡</div>
        <div class="preview-text">
          Ціна буде 
          <span :class="form.operation">{{ form.operation === 'increase' ? 'збільшена' : 'зменшена' }}</span> 
          на <b>{{ form.value }}{{ form.type === 'percentage' ? '%' : ' грн' }}</b>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">Скасувати</el-button>
        <el-button 
          type="primary" 
          :loading="loading" 
          class="apply-btn"
          @click="handleApply"
        >
          Застосувати зміни
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  visible: Boolean,
  count: Number,
  loading: Boolean
})

const emit = defineEmits(['update:visible', 'apply'])

const form = reactive({
  type: 'percentage',
  operation: 'increase',
  value: 0
})

const handleApply = () => {
  emit('apply', { ...form })
}
</script>

<style scoped>
.bulk-price-content {
  padding: 10px 0;
}

.selection-info {
  background: #F1F5F9;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  color: #475569;
  margin-bottom: 24px;
  border: 1px solid #E2E8F0;
}

.selection-info b {
  color: #1463FF;
}

.premium-radio-group {
  width: 100%;
  display: flex;
}

:deep(.premium-radio-group .el-radio-button) {
  flex: 1;
}

:deep(.premium-radio-group .el-radio-button__inner) {
  width: 100%;
  border-radius: 8px !important;
  margin: 0 4px;
  border: 1px solid #E2E8F0 !important;
}

.full-width {
  width: 100%;
}

.price-preview {
  margin-top: 24px;
  padding: 16px;
  background: #F0FDF4;
  border-radius: 14px;
  border: 1px solid #DCFCE7;
  display: flex;
  gap: 12px;
  align-items: center;
}

.preview-icon {
  font-size: 20px;
}

.preview-text {
  font-size: 13px;
  color: #166534;
  font-weight: 600;
}

.preview-text b {
  color: #15803d;
}

.increase { color: #059669; font-weight: 800; }
.decrease { color: #DC2626; font-weight: 800; }

.apply-btn {
  background: linear-gradient(135deg, #1463FF 0%, #0047D1 100%);
  border: none;
  font-weight: 700;
  padding: 0 24px;
  height: 40px;
  border-radius: 10px;
}
</style>
