<template>
  <div class="general-tab-content">
    <el-form :model="modelValue" :rules="rules" label-position="top" class="product-form">
      <el-row :gutter="40">
        <!-- Left column: text fields -->
        <el-col :span="16">
          <el-form-item prop="name">
            <template #label><span class="field-label">Назва товару</span></template>
            <el-input v-model="modelValue.name" size="large" placeholder="Введіть назву (напр., Нога стола чорна 710мм)" class="styled-input" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item prop="sku">
                <template #label><span class="field-label">Артикул (SKU)</span></template>
                <el-input v-model="modelValue.sku" placeholder="WOOD-001" class="styled-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="category">
                <template #label><span class="field-label">Категорія</span></template>
                <el-select v-model="modelValue.category" placeholder="Оберіть категорію" style="width: 100%" class="styled-select">
                  <el-option v-for="opt in categoryOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <template #label><span class="field-label">Опис товару</span></template>
            <el-input v-model="modelValue.description" type="textarea" :rows="5" placeholder="Докладний опис товару, технічні характеристики..." class="styled-input" />
          </el-form-item>
        </el-col>

        <!-- Right column: image + meta -->
        <el-col :span="8">
          <el-form-item>
            <template #label><span class="field-label">Зображення</span></template>
            <div class="image-upload-zone">
              <el-image v-if="modelValue.image_url" :src="modelValue.image_url" fit="cover" class="preview-image" />
              <div v-else class="upload-placeholder">
                <el-icon :size="36" class="upload-icon"><Picture /></el-icon>
                <span class="upload-text">Натисніть для завантаження</span>
                <span class="upload-hint">PNG, JPG до 5MB</span>
              </div>
            </div>
          </el-form-item>

          <el-form-item>
            <template #label><span class="field-label">Одиниця виміру</span></template>
            <el-select v-model="modelValue.unit_of_measure" style="width: 100%" class="styled-select">
              <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <template #label><span class="field-label">Статус товару</span></template>
            <div class="status-toggle-row">
              <el-switch
                v-model="modelValue.is_active"
                class="ios-switch"
                :active-color="'#2563eb'"
                :inactive-color="'#e2e8f0'"
              />
              <span class="status-label" :class="modelValue.is_active ? 'active' : 'inactive'">
                {{ modelValue.is_active ? 'Активний' : 'Архівний' }}
              </span>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  categoryOptions: {
    type: Array,
    default: () => []
  },
  uomOptions: {
    type: Array,
    default: () => []
  },
  rules: {
    type: Object,
    default: () => ({})
  }
})
</script>

<style scoped>
.general-tab-content {
  padding: 24px;
}

/* Field labels */
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: none;
  letter-spacing: 0;
}

/* Inputs */
.product-form :deep(.el-input__wrapper),
.product-form :deep(.el-select__wrapper),
.product-form :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px !important;
  background: #f8fafc !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.product-form :deep(.el-input__wrapper:hover),
.product-form :deep(.el-select__wrapper:hover),
.product-form :deep(.el-textarea__inner:hover) {
  border-color: #94a3b8 !important;
  background: #fff !important;
}

.product-form :deep(.el-input__wrapper.is-focus),
.product-form :deep(.el-select__wrapper.is-focused),
.product-form :deep(.el-textarea__inner:focus) {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
  background: #fff !important;
  outline: none;
}

.product-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.product-form :deep(.el-form-item__label) {
  padding-bottom: 4px !important;
  line-height: normal !important;
}

/* Image upload zone */
.image-upload-zone {
  width: 100%;
  height: 190px;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: #f8fafc;
  transition: border-color 0.2s, background 0.2s;
}

.image-upload-zone:hover {
  border-color: #2563eb;
  background: #eff6ff;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.upload-icon {
  color: #94a3b8;
  transition: color 0.2s;
}

.image-upload-zone:hover .upload-icon {
  color: #2563eb;
}

.upload-text {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.upload-hint {
  font-size: 11px;
  color: #94a3b8;
}

.preview-image {
  width: 100%;
  height: 100%;
  border-radius: 10px;
}

/* Status toggle */
.status-toggle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.ios-switch :deep(.el-switch__core) {
  width: 44px !important;
  height: 24px !important;
  border-radius: 12px !important;
}

.ios-switch :deep(.el-switch__core .el-switch__action) {
  width: 18px;
  height: 18px;
  top: 3px;
}

.status-label {
  font-size: 13px;
  font-weight: 500;
}

.status-label.active {
  color: #16a34a;
}

.status-label.inactive {
  color: #94a3b8;
}
</style>
