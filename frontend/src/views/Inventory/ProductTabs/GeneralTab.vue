<template>
  <div class="general-tab-content">
    <el-form :model="modelValue" label-position="top" class="product-form">
      <el-row :gutter="40">
        <!-- ===== LEFT COLUMN ===== -->
        <el-col :span="16">
          <div class="compact-section">
            <div class="section-divider" style="margin-top: 0">Основні дані</div>
            <!-- Product name -->
            <el-form-item prop="name" class="compact-form-item">
              <template #label><span class="field-label">Назва товару</span></template>
              <el-input v-model="modelValue.name" size="large" placeholder="Введіть назву (напр., Нога стола чорна 710мм)" class="styled-input" />
            </el-form-item>
          </div>

          <!-- SKU + Category -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item prop="sku">
                <template #label>
                  <span class="field-label">
                    Артикул (SKU) 
                    <span v-if="!hasVariants" class="req">*</span>
                  </span>
                </template>
                <el-input 
                  v-model="modelValue.sku" 
                  placeholder="WOO-001" 
                  class="styled-input" 
                />
                <div v-if="hasVariants" class="field-hint">
                  SKU визначається варіантами
                </div>
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

          <div class="section-divider">Додатково</div>
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
          
          <div class="physical-params-grid">
            <!-- Length (Довжина) -->
            <div class="param-row">
              <div class="param-label">Довжина (см):</div>
              <div class="param-controls">
                <el-radio-group v-model="getVariantConfig('length').source" size="small">
                  <el-radio-button label="fixed">Фіксовано</el-radio-button>
                  <el-radio-button label="attribute">З хар-ки</el-radio-button>
                </el-radio-group>
                
                <el-input-number v-if="getVariantConfig('length').source === 'fixed'" v-model="modelValue.length_cm" :precision="1" size="small" class="w-32 ml-2" />
                <el-select v-if="getVariantConfig('length').source === 'attribute'" v-model="getVariantConfig('length').attr_id" placeholder="Виберіть..." size="small" class="w-48 ml-2">
                  <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                </el-select>
              </div>
            </div>

            <!-- Width (Ширина) -->
            <div class="param-row">
              <div class="param-label">Ширина (см):</div>
              <div class="param-controls">
                <el-radio-group v-model="getVariantConfig('width').source" size="small">
                  <el-radio-button label="fixed">Фіксовано</el-radio-button>
                  <el-radio-button label="attribute">З хар-ки</el-radio-button>
                </el-radio-group>
                
                <el-input-number v-if="getVariantConfig('width').source === 'fixed'" v-model="modelValue.width_cm" :precision="1" size="small" class="w-32 ml-2" />
                <el-select v-if="getVariantConfig('width').source === 'attribute'" v-model="getVariantConfig('width').attr_id" placeholder="Виберіть..." size="small" class="w-48 ml-2">
                  <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                </el-select>
              </div>
            </div>

            <!-- Height (Висота) -->
            <div class="param-row">
              <div class="param-label">Висота (см):</div>
              <div class="param-controls">
                <el-radio-group v-model="getVariantConfig('height').source" size="small">
                  <el-radio-button label="fixed">Фіксовано</el-radio-button>
                  <el-radio-button label="attribute">З хар-ки</el-radio-button>
                </el-radio-group>
                
                <el-input-number v-if="getVariantConfig('height').source === 'fixed'" v-model="modelValue.height_cm" :precision="1" size="small" class="w-32 ml-2" />
                <el-select v-if="getVariantConfig('height').source === 'attribute'" v-model="getVariantConfig('height').attr_id" placeholder="Виберіть..." size="small" class="w-48 ml-2">
                  <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                </el-select>
              </div>
            </div>

            <!-- Weight (Вага) -->
            <div class="param-row">
              <div class="param-label">Вага (кг):</div>
              <div class="param-controls items-start !gap-2">
                <div class="flex flex-col gap-2">
                  <el-radio-group v-model="getVariantConfig('weight').source" size="small">
                    <el-radio-button label="fixed">Фіксовано</el-radio-button>
                    <el-radio-button label="calc">Розрахунок</el-radio-button>
                    <el-radio-button label="manual">Вручну в табл.</el-radio-button>
                  </el-radio-group>
                  
                  <div v-if="getVariantConfig('weight').source === 'fixed'" class="flex items-center gap-2">
                     <el-input-number v-model="modelValue.weight_kg" :precision="3" size="small" class="w-32" />
                  </div>

                  <div v-if="getVariantConfig('weight').source === 'calc'" class="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 p-2 rounded border border-slate-100">
                     Базова: <el-input-number v-model="getVariantConfig('weight').base_kg" :precision="1" size="small" style="width:70px" :controls="false" /> кг
                     + <el-input-number v-model="getVariantConfig('weight').step_kg" :precision="1" size="small" style="width:60px" :controls="false" /> кг 
                     на кожні <el-input-number v-model="getVariantConfig('weight').step_cm" :precision="0" size="small" style="width:60px" :controls="false" /> см
                     параметра: 
                     <el-select v-model="getVariantConfig('weight').dim_key" size="small" style="width:100px">
                       <el-option label="Довжина" value="length" />
                       <el-option label="Ширина" value="width" />
                       <el-option label="Висота" value="height" />
                     </el-select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- ===== RIGHT COLUMN ===== -->
        <el-col :span="8">
          <div class="section-divider">Медіа</div>
          <!-- Image upload -->
          <el-form-item>
            <template #label><span class="field-label">Зображення товару</span></template>
            <div class="image-upload-zone" @click="triggerImageUpload" v-loading="uploading">
              <el-image v-if="modelValue.image_url" :src="modelValue.image_url" fit="cover" class="preview-image" />
              <div v-else class="upload-placeholder">
                <el-icon :size="32" class="upload-icon"><Picture /></el-icon>
                <span class="upload-text">Завантажити фото</span>
                <span class="upload-hint">Перетягніть або натисніть</span>
              </div>
              <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleImageChange" />
            </div>
            <div v-if="modelValue.image_url" class="image-url-field">
              <el-input v-model="modelValue.image_url" placeholder="URL зображення" size="small" clearable class="styled-input" />
            </div>
          </el-form-item>

          <div class="section-divider">Параметри</div>
          <!-- Unit of measure -->
          <el-form-item>
            <template #label><span class="field-label">Одиниця виміру</span></template>
            <el-select v-model="modelValue.unit_of_measure" style="width: 100%" class="styled-select">
              <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
            </el-select>
          </el-form-item>

          <!-- Status toggle -->
          <div class="toggle-card">
            <div class="toggle-row">
              <div class="toggle-info">
                <span class="toggle-title">Статус товару</span>
                <span class="toggle-status-text" :class="modelValue.is_active ? 'active' : 'inactive'">
                  {{ modelValue.is_active ? 'Активний' : 'В архіві' }}
                </span>
              </div>
              <el-switch
                v-model="modelValue.is_active"
                active-color="#6366f1"
                inactive-color="#e2e8f0"
              />
            </div>
          </div>

          <!-- Track inventory toggle -->
          <div class="toggle-card">
            <div class="toggle-row">
              <div class="toggle-info">
                <span class="toggle-title">Облік запасів</span>
                <span class="toggle-status-text" :class="modelValue.track_inventory ? 'active' : 'inactive'">
                  {{ modelValue.track_inventory ? 'Ведеться' : 'Не ведеться' }}
                </span>
              </div>
              <el-switch
                v-model="modelValue.track_inventory"
                active-color="#6366f1"
                inactive-color="#e2e8f0"
              />
            </div>
          </div>

          <!-- Tags -->
          <el-form-item style="margin-top: 16px;">
            <template #label><span class="field-label">Теги / Мітки</span></template>
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
import { ref, computed } from 'vue'
import { Picture, DataLine } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: { type: Object, required: true },
  categoryOptions: { type: Array, default: () => [] },
  uomOptions: { type: Array, default: () => [] },
  categoryAttributes: { type: Array, default: () => [] },
})

const getVariantConfig = (key) => {
  if (!props.modelValue.variant_config) props.modelValue.variant_config = {}
  if (!props.modelValue.variant_config[key]) {
    props.modelValue.variant_config[key] = { source: 'fixed', attr_id: null, base_kg: 0, step_kg: 0, step_cm: 10, dim_key: 'length' }
  }
  return props.modelValue.variant_config[key]
}

const hasVariants = computed(() => {
  return props.modelValue.variants && props.modelValue.variants.length > 0
})

const fileInput = ref(null)
const uploading = ref(false)

const commonTags = ref(['Меблі', 'Дерево', 'Метал', 'Пластик', 'Вироби'])

const triggerImageUpload = () => {
  if (!props.modelValue.image_url && !uploading.value) {
    fileInput.value?.click()
  }
}

const handleImageChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    ElMessage.error('Будь ласка, оберіть файл зображення')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('Розмір файлу не повинен перевищувати 5MB')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await api.post('/api/v1/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // The backend returns a relative URL like `/api/v1/uploads/...`
    // which Vite proxies, or can be used directly as image source.
    props.modelValue.image_url = res.data.url
    ElMessage.success('Зображення завантажено')
  } catch (error) {
    console.error('Upload failed', error)
    ElMessage.error('Помилка завантаження зображення')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>

<style scoped>
.general-tab-content {
  padding: 12px 24px;
  background: #ffffff;
}

.product-form {
  width: 100%;
  margin: 0 auto;
}
.compact-form-item { margin-bottom: 8px !important; }
.compact-section { margin-bottom: 8px; }

/* === SECTION DIVIDERS === */
.section-divider {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 16px 0 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #f1f5f9;
}

/* === FIELD LABELS === */
.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 4px;
}

.req {
  color: #f43f5e;
  margin-left: 2px;
}

.field-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  line-height: 1.2;
}

/* === INPUT STYLING === */
.product-form :deep(.el-input__wrapper),
.product-form :deep(.el-select__wrapper),
.product-form :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 10px !important;
  background-color: #f8fafc !important;
  padding: 4px 10px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-form :deep(.el-input__wrapper:hover),
.product-form :deep(.el-select__wrapper:hover),
.product-form :deep(.el-textarea__inner:hover) {
  border-color: #cbd5e1 !important;
  background-color: #f1f5f9 !important;
}

.product-form :deep(.el-input__wrapper.is-focus),
.product-form :deep(.el-select__wrapper.is-focused),
.product-form :deep(.el-textarea__inner:focus) {
  border-color: #6366f1 !important;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
}

/* Specific for large input */
.product-form :deep(.el-input--large .el-input__wrapper) {
  padding: 8px 12px !important;
  font-size: 15px;
  font-weight: 500;
}

/* Sections spacing */
.product-form :deep(.el-form-item) {
  margin-bottom: 12px;
}

.product-form :deep(.el-form-item__label) {
  padding-bottom: 2px !important;
  line-height: 1 !important;
}

/* === IMAGE UPLOAD ZONE === */
.image-upload-zone {
  width: 100%;
  aspect-ratio: 1 / 1;
  max-height: 280px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.image-upload-zone:hover {
  border-color: #6366f1;
  background: #f5f3ff;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.1);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  padding: 20px;
}

.upload-icon {
  color: #94a3b8;
  transition: color 0.3s ease;
}

.image-upload-zone:hover .upload-icon {
  color: #6366f1;
}

.upload-text {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.upload-hint {
  font-size: 11px;
  color: #94a3b8;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.image-upload-zone:hover .preview-image {
  transform: scale(1.05);
}

/* === TOGGLE SWITCHES === */
.toggle-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.toggle-card:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.toggle-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.toggle-title {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.toggle-status-text {
  font-size: 11px;
  font-weight: 500;
}

.toggle-status-text.active { color: #10b981; }
.toggle-status-text.inactive { color: #94a3b8; }

/* === PHYSICAL PARAMS GRID === */
.physical-params-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

.param-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.param-label {
  width: 110px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  padding-top: 6px;
}

.param-controls {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.w-32 { width: 8rem; }
.w-48 { width: 12rem; }
.ml-2 { margin-left: 0.5rem; }

</style>

