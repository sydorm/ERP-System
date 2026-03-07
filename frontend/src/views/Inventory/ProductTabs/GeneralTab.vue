<template>
  <div class="general-tab-content">
    <el-form :model="modelValue" label-position="top" class="product-form">
      <el-row :gutter="40">
        <!-- ===== LEFT COLUMN ===== -->
        <el-col :span="16">
          <!-- Product name -->
          <el-form-item prop="name">
            <template #label><span class="field-label">Назва товару</span></template>
            <el-input v-model="modelValue.name" size="large" placeholder="Введіть назву (напр., Нога стола чорна 710мм)" class="styled-input" />
          </el-form-item>

          <!-- SKU + Category -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item prop="sku">
                <template #label><span class="field-label required-mark">Артикул (SKU) <span class="req">*</span></span></template>
                <el-input v-model="modelValue.sku" placeholder="WOO-001" class="styled-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="category">
                <template #label><span class="field-label required-mark">Категорія <span class="req">*</span></span></template>
                <el-select v-model="modelValue.category" placeholder="Оберіть категорію" style="width: 100%" class="styled-select">
                  <el-option v-for="opt in categoryOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Description -->
          <el-form-item>
            <template #label><span class="field-label">Опис товару</span></template>
            <el-input v-model="modelValue.description" type="textarea" :rows="4" placeholder="Докладний опис товару, технічні характеристики..." class="styled-input" />
          </el-form-item>

          <!-- Barcode + Internal code -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item>
                <template #label><span class="field-label">Штрихкод (EAN)</span></template>
                <el-input v-model="modelValue.barcode" placeholder="1234567890123" class="styled-input">
                  <template #prefix><el-icon><DataLine /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <template #label><span class="field-label">Внутрішній код</span></template>
                <el-input v-model="modelValue.internal_code" placeholder="Внутрішній артикул" class="styled-input" />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Weight + Dimensions -->
          <div class="section-divider">Фізичні параметри</div>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item>
                <template #label><span class="field-label">Вага (кг)</span></template>
                <el-input-number
                  v-model="modelValue.weight_kg"
                  :precision="3"
                  :step="0.1"
                  :min="0"
                  controls-position="right"
                  style="width: 100%"
                  class="styled-number"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label><span class="field-label">Довжина (см)</span></template>
                <el-input-number
                  v-model="modelValue.length_cm"
                  :precision="1"
                  :step="1"
                  :min="0"
                  controls-position="right"
                  style="width: 100%"
                  class="styled-number"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label><span class="field-label">Ширина (см)</span></template>
                <el-input-number
                  v-model="modelValue.width_cm"
                  :precision="1"
                  :step="1"
                  :min="0"
                  controls-position="right"
                  style="width: 100%"
                  class="styled-number"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-col>

        <!-- ===== RIGHT COLUMN ===== -->
        <el-col :span="8">
          <!-- Image upload -->
          <el-form-item>
            <template #label><span class="field-label">Зображення</span></template>
            <div class="image-upload-zone" @click="triggerImageUpload">
              <el-image v-if="modelValue.image_url" :src="modelValue.image_url" fit="cover" class="preview-image" />
              <div v-else class="upload-placeholder">
                <el-icon :size="32" class="upload-icon"><Picture /></el-icon>
                <span class="upload-text">Натисніть для завантаження</span>
                <span class="upload-hint">PNG, JPG до 5MB</span>
              </div>
              <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleImageChange" />
            </div>
            <div v-if="modelValue.image_url" class="image-url-field">
              <el-input v-model="modelValue.image_url" placeholder="URL зображення" size="small" clearable class="styled-input" />
            </div>
          </el-form-item>

          <!-- Unit of measure -->
          <el-form-item>
            <template #label><span class="field-label">Одиниця виміру</span></template>
            <el-select v-model="modelValue.unit_of_measure" style="width: 100%" class="styled-select">
              <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
            </el-select>
          </el-form-item>

          <!-- Status toggle -->
          <el-form-item>
            <template #label><span class="field-label">Статус товару</span></template>
            <div class="toggle-row">
              <el-switch
                v-model="modelValue.is_active"
                :active-color="'#6366f1'"
                :inactive-color="'#e2e8f0'"
              />
              <span class="toggle-label" :class="modelValue.is_active ? 'active' : 'inactive'">
                {{ modelValue.is_active ? 'Активний' : 'Архівний' }}
              </span>
            </div>
          </el-form-item>

          <!-- Track inventory toggle -->
          <el-form-item>
            <template #label><span class="field-label">Облік запасу</span></template>
            <div class="toggle-row">
              <el-switch
                v-model="modelValue.track_inventory"
                :active-color="'#6366f1'"
                :inactive-color="'#e2e8f0'"
              />
              <span class="toggle-label" :class="modelValue.track_inventory ? 'active' : 'inactive'">
                {{ modelValue.track_inventory ? 'Вести облік' : 'Без обліку' }}
              </span>
            </div>
          </el-form-item>

          <!-- Tags -->
          <el-form-item>
            <template #label><span class="field-label">Теги</span></template>
            <el-select
              v-model="modelValue.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="Додайте теги..."
              style="width: 100%"
              class="styled-select"
            >
              <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture, DataLine } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  categoryOptions: { type: Array, default: () => [] },
  uomOptions: { type: Array, default: () => [] },
})

const fileInput = ref(null)

const commonTags = ref(['Меблі', 'Дерево', 'Метал', 'Пластик', 'Вироби'])

const triggerImageUpload = () => {
  if (!props.modelValue.image_url) {
    fileInput.value?.click()
  }
}

const handleImageChange = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    // In a real app, you'd upload to a server. For now, create a local URL.
    const url = URL.createObjectURL(file)
    props.modelValue.image_url = url
  }
}
</script>

<style scoped>
.general-tab-content {
  padding: 24px;
}

.section-divider {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 4px 0 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
}

/* Field labels */
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}
.req { color: #ef4444; }

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
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
  background: #fff !important;
  outline: none;
}

.product-form :deep(.el-form-item) { margin-bottom: 18px; }
.product-form :deep(.el-form-item__label) { padding-bottom: 4px !important; line-height: normal !important; }

/* Number input */
.styled-number :deep(.el-input__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px !important;
  background: #f8fafc !important;
}
.styled-number :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* Image upload zone */
.image-upload-zone {
  width: 100%;
  height: 180px;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: #f8fafc;
  transition: border-color 0.2s, background 0.2s;
  overflow: hidden;
}
.image-upload-zone:hover { border-color: #6366f1; background: #f5f3ff; }

.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.upload-icon { color: #94a3b8; transition: color 0.2s; }
.image-upload-zone:hover .upload-icon { color: #6366f1; }
.upload-text { font-size: 12px; font-weight: 500; color: #64748b; }
.upload-hint { font-size: 10px; color: #94a3b8; }
.preview-image { width: 100%; height: 100%; border-radius: 10px; }

.image-url-field { margin-top: 8px; }

/* Toggles */
.toggle-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; }
.toggle-label { font-size: 13px; font-weight: 500; }
.toggle-label.active { color: #16a34a; }
.toggle-label.inactive { color: #94a3b8; }
</style>
