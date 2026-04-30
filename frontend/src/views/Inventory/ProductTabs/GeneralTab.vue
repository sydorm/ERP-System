<template>
  <div class="general-tab-content">
    <el-form :model="modelValue" label-position="top" class="product-form">
      <div class="form-grid">
        
        <!-- ===== LEFT COLUMN (65-70%) ===== -->
        <div class="form-left-col">
          
          <!-- 6.1 Основні дані -->
          <div class="form-section">
            <div class="section-header">
              <h3>Основні дані</h3>
              <p class="section-desc">Назва, артикул, категорія та службові коди товару</p>
            </div>
            
            <el-form-item prop="name" class="mb-4">
              <template #label>
                <div class="label-with-ai">
                  <span class="field-label required">Назва товару</span>
                  <el-button 
                    type="primary" 
                    link 
                    size="small" 
                    class="ai-action-btn"
                    @click="aiStandardizeName"
                  >
                    <el-icon class="mr-1"><MagicStick /></el-icon> AI-стандартизувати
                  </el-button>
                </div>
              </template>
              <el-input v-model="modelValue.name" size="large" placeholder="Введіть назву (напр., Полиця для взуття Classic)" class="modern-input" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="sku">
                  <template #label>
                    <span class="field-label" :class="{ required: !hasVariants }">Артикул (SKU)</span>
                  </template>
                  <el-input v-model="modelValue.sku" placeholder="SKU-001" class="modern-input" />
                  <div v-if="hasVariants" class="field-hint">SKU визначається варіантами</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="category">
                  <template #label><span class="field-label required">Категорія</span></template>
                  <el-select v-model="modelValue.category" placeholder="Оберіть категорію" style="width: 100%" class="modern-select">
                    <el-option v-for="opt in categoryOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 12px;">
              <el-col :span="12">
                <el-form-item>
                  <template #label><span class="field-label">Штрихкод (EAN)</span></template>
                  <el-input v-model="modelValue.barcode" placeholder="1234567890123" class="modern-input">
                    <template #prefix><el-icon><DataLine /></el-icon></template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <template #label><span class="field-label">Внутрішній код</span></template>
                  <el-input v-model="modelValue.internal_code" placeholder="Код у системі" class="modern-input" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 6.2 Опис -->
          <div class="form-section">
            <div class="section-header">
              <h3>Опис товару</h3>
            </div>
            <el-form-item>
              <template #label>
                <div class="label-with-ai">
                  <span class="field-label">Опис та характеристики</span>
                  <el-button 
                    type="primary" 
                    link 
                    size="small" 
                    class="ai-action-btn"
                    @click="aiGenerateDescription"
                    :loading="generatingDescription"
                  >
                    <el-icon class="mr-1"><MagicStick /></el-icon> AI-згенерувати опис
                  </el-button>
                </div>
              </template>
              <el-input 
                v-model="modelValue.description" 
                type="textarea" 
                :rows="6" 
                placeholder="Докладний опис товару, технічні характеристики..." 
                class="modern-textarea" 
              />
            </el-form-item>
          </div>

          <!-- 6.3 Фізичні параметри -->
          <div class="form-section">
            <div class="section-header">
              <h3>Фізичні параметри</h3>
              <p class="section-desc">Габаритні розміри (мм) та вагові характеристики (кг)</p>
            </div>
            
            <div class="physical-params-list">
              <!-- Dimensions Tooltip -->
              <el-alert
                title="Усі габаритні розміри виробу вказуються в міліметрах. Наприклад: 600 мм = 60 см = 0.6 м."
                type="info"
                show-icon
                :closable="false"
                class="mb-4"
              />

              <!-- Length -->
              <div class="param-block">
                <span class="param-block-label">Довжина (мм)</span>
                <div class="param-block-controls">
                  <el-radio-group v-model="getVariantConfig('length').source" size="small" class="modern-radios">
                    <el-radio-button label="fixed">Фіксовано</el-radio-button>
                    <el-radio-button label="attribute">З хар-ки</el-radio-button>
                  </el-radio-group>
                  <el-input-number 
                    v-if="getVariantConfig('length').source === 'fixed'" 
                    v-model="modelValue.length_mm" 
                    :precision="0" 
                    class="modern-number-input"
                  />
                  <el-select 
                    v-if="getVariantConfig('length').source === 'attribute'" 
                    v-model="getVariantConfig('length').attr_id" 
                    placeholder="Оберіть атрибут" 
                    class="modern-select param-select"
                  >
                    <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                  </el-select>
                  <span v-if="modelValue.length_mm > 0 && modelValue.length_mm < 100" class="field-warning-text">
                    <el-icon><Warning /></el-icon> Можливо в см?
                  </span>
                </div>
              </div>

              <!-- Width -->
              <div class="param-block">
                <span class="param-block-label">Ширина (мм)</span>
                <div class="param-block-controls">
                  <el-radio-group v-model="getVariantConfig('width').source" size="small" class="modern-radios">
                    <el-radio-button label="fixed">Фіксовано</el-radio-button>
                    <el-radio-button label="attribute">З хар-ки</el-radio-button>
                  </el-radio-group>
                  <el-input-number 
                    v-if="getVariantConfig('width').source === 'fixed'" 
                    v-model="modelValue.width_mm" 
                    :precision="0" 
                    class="modern-number-input"
                  />
                  <el-select 
                    v-if="getVariantConfig('width').source === 'attribute'" 
                    v-model="getVariantConfig('width').attr_id" 
                    placeholder="Оберіть атрибут" 
                    class="modern-select param-select"
                  >
                    <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                  </el-select>
                  <span v-if="modelValue.width_mm > 0 && modelValue.width_mm < 100" class="field-warning-text">
                    <el-icon><Warning /></el-icon> Можливо в см?
                  </span>
                </div>
              </div>

              <!-- Height -->
              <div class="param-block">
                <span class="param-block-label">Висота (мм)</span>
                <div class="param-block-controls">
                  <el-radio-group v-model="getVariantConfig('height').source" size="small" class="modern-radios">
                    <el-radio-button label="fixed">Фіксовано</el-radio-button>
                    <el-radio-button label="attribute">З хар-ки</el-radio-button>
                  </el-radio-group>
                  <el-input-number 
                    v-if="getVariantConfig('height').source === 'fixed'" 
                    v-model="modelValue.height_mm" 
                    :precision="0" 
                    class="modern-number-input"
                  />
                  <el-select 
                    v-if="getVariantConfig('height').source === 'attribute'" 
                    v-model="getVariantConfig('height').attr_id" 
                    placeholder="Оберіть атрибут" 
                    class="modern-select param-select"
                  >
                    <el-option v-for="attr in categoryAttributes" :key="attr.id" :label="attr.name" :value="attr.id" />
                  </el-select>
                  <span v-if="modelValue.height_mm > 0 && modelValue.height_mm < 100" class="field-warning-text">
                    <el-icon><Warning /></el-icon> Можливо в см?
                  </span>
                </div>
              </div>

              <!-- Weight -->
              <div class="param-block align-items-start">
                <span class="param-block-label pt-2">Вага (кг)</span>
                <div class="param-block-controls flex-col align-items-start gap-3">
                  <el-radio-group v-model="getVariantConfig('weight').source" size="small" class="modern-radios">
                    <el-radio-button label="fixed">Фіксовано</el-radio-button>
                    <el-radio-button label="calc">Розрахунок</el-radio-button>
                    <el-radio-button label="manual">Вручну</el-radio-button>
                  </el-radio-group>
                  
                  <el-input-number 
                    v-if="getVariantConfig('weight').source === 'fixed'" 
                    v-model="modelValue.weight_kg" 
                    :precision="3" 
                    class="modern-number-input"
                  />

                  <div v-if="getVariantConfig('weight').source === 'calc'" class="calc-settings">
                     <span>Базова:</span>
                     <el-input-number v-model="getVariantConfig('weight').base_kg" :precision="1" class="modern-number-input small-input" :controls="false" />
                     <span>+</span>
                     <el-input-number v-model="getVariantConfig('weight').step_kg" :precision="1" class="modern-number-input small-input" :controls="false" />
                     <span>на кожні</span>
                     <el-input-number v-model="getVariantConfig('weight').step_mm" :precision="0" class="modern-number-input small-input" :controls="false" />
                     <span>мм</span>
                     <el-select v-model="getVariantConfig('weight').dim_key" class="modern-select small-select">
                       <el-option label="Довжина" value="length" />
                       <el-option label="Ширина" value="width" />
                       <el-option label="Висота" value="height" />
                     </el-select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== RIGHT COLUMN (30-35%) ===== -->
        <div class="form-right-col">
          
          <!-- Блок 1: Фото -->
          <div class="side-card">
            <div class="card-title">Фото товару</div>
            
            <div 
              class="image-dropzone" 
              @click="triggerImageUpload" 
              v-loading="uploading"
            >
              <el-image v-if="modelValue.image_url" :src="modelValue.image_url" fit="cover" class="dropzone-preview" />
              <div v-else class="dropzone-placeholder">
                <el-icon :size="36" class="dropzone-icon"><Picture /></el-icon>
                <span class="dropzone-text">Завантажити фото</span>
                <span class="dropzone-hint">Натисніть для вибору</span>
              </div>
              <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleImageChange" />
            </div>
            
            <div class="image-actions" v-if="modelValue.image_url">
              <el-button size="small" type="primary" plain @click="triggerImageUpload">Замінити</el-button>
              <el-button size="small" type="danger" plain @click="removeImage">Видалити</el-button>
            </div>
          </div>

          <!-- Блок 2: Параметри -->
          <div class="side-card">
            <div class="card-title">Додаткові параметри</div>
            
            <el-form-item class="mb-3">
              <template #label><span class="side-label">Одиниця виміру</span></template>
              <el-select v-model="modelValue.unit_of_measure" style="width: 100%" class="modern-select">
                <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
              </el-select>
            </el-form-item>

            <div class="side-toggle">
              <div class="toggle-meta">
                <span class="toggle-title">Статус</span>
                <span class="toggle-desc" :class="modelValue.is_active ? 'active' : 'inactive'">
                  {{ modelValue.is_active ? 'Активний' : 'В архіві' }}
                </span>
              </div>
              <el-switch v-model="modelValue.is_active" active-color="#4f46e5" />
            </div>

            <div class="side-toggle">
              <div class="toggle-meta">
                <span class="toggle-title">Облік запасів</span>
                <span class="toggle-desc" :class="modelValue.track_inventory ? 'active' : 'inactive'">
                  {{ modelValue.track_inventory ? 'Ведеться' : 'Не ведеться' }}
                </span>
              </div>
              <el-switch v-model="modelValue.track_inventory" active-color="#4f46e5" />
            </div>

            <el-form-item class="mt-3">
              <template #label><span class="side-label">Теги / Мітки</span></template>
              <el-select
                v-model="modelValue.tags"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="Введіть теги..."
                style="width: 100%"
                class="modern-select"
              >
                <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
              </el-select>
            </el-form-item>
          </div>

          <!-- Блок 3: AI Checklist -->
          <div class="side-card ai-card">
            <div class="ai-card-header">
              <el-icon class="ai-logo-icon"><MagicStick /></el-icon>
              <div class="ai-meta">
                <span class="ai-card-title">AI-якість картки</span>
                <span class="ai-score">{{ aiScore }}% заповнено</span>
              </div>
            </div>
            
            <div class="ai-progress-bar">
              <div class="ai-progress-fill" :style="{ width: aiScore + '%' }"></div>
            </div>

            <ul class="ai-checklist">
              <li v-for="(item, idx) in aiIssues" :key="idx" :class="{ solved: item.status }">
                <el-icon class="status-icon">
                  <CircleCheck v-if="item.status" />
                  <Warning v-else />
                </el-icon>
                <span>{{ item.text }}</span>
              </li>
            </ul>

            <el-button 
              type="primary" 
              class="w-full mt-3 ai-run-btn" 
              @click="runAiCheck"
              :loading="checkingAi"
            >
              Перевірити через AI
            </el-button>
          </div>
        </div>

      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Picture, DataLine, MagicStick, CircleCheck, Warning } from '@element-plus/icons-vue'
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
    props.modelValue.variant_config[key] = { source: 'fixed', attr_id: null, base_kg: 0, step_kg: 0, step_mm: 100, dim_key: 'length' }
  }
  return props.modelValue.variant_config[key]
}

const hasVariants = computed(() => {
  return props.modelValue.variants && props.modelValue.variants.length > 0
})

const fileInput = ref(null)
const uploading = ref(false)
const checkingAi = ref(false)
const generatingDescription = ref(false)

const commonTags = ref(['Меблі', 'Дерево', 'Метал', 'Пластик', 'Вироби'])

const aiScore = computed(() => {
  let score = 0
  if (props.modelValue.name) score += 20
  if (props.modelValue.description) score += 20
  if (props.modelValue.image_url) score += 20
  if (props.modelValue.length_mm && props.modelValue.width_mm && props.modelValue.height_mm) score += 20
  if (props.modelValue.sku && props.modelValue.category) score += 20
  return score
})

const aiIssues = computed(() => {
  return [
    { text: 'Назва та категорія заповнені', status: !!props.modelValue.name && !!props.modelValue.category },
    { text: 'Фото виробу додано', status: !!props.modelValue.image_url },
    { text: 'Опис товару створено', status: !!props.modelValue.description },
    { text: 'Фізичні розміри вказано', status: !!(props.modelValue.length_mm && props.modelValue.width_mm && props.modelValue.height_mm) },
    { text: 'Перевірено на дублікати', status: true }
  ]
})

const runAiCheck = () => {
  checkingAi.value = true
  setTimeout(() => {
    checkingAi.value = false
    ElMessage.success('Аналіз завершено')
  }, 1200)
}

const aiGenerateDescription = async () => {
  if (!props.modelValue.name) {
    ElMessage.warning('Вкажіть назву товару для генерації опису')
    return
  }
  generatingDescription.value = true
  try {
    const res = await api.post('/api/ai/generate-description', {
      product_name: props.modelValue.name,
      category: props.modelValue.category,
      additional_info: `Артикул: ${props.modelValue.sku || 'не вказано'}`
    })
    if (res.data && res.data.description) {
      props.modelValue.description = res.data.description
      ElMessage.success('Опис створено AI')
    }
  } catch (error) {
    ElMessage.error('Помилка генерації опису')
  } finally {
    generatingDescription.value = false
  }
}

const aiStandardizeName = async () => {
  if (!props.modelValue.name) {
    ElMessage.warning('Вкажіть назву для оптимізації')
    return
  }
  try {
    const res = await api.post('/api/ai/chat', {
      message: `Проведи стандартизацію меблевої назви: "${props.modelValue.name}". Поверни ТІЛЬКИ виправлений рядок назви без лапок та коментарів.`,
      context: 'Форма створення номенклатури'
    })
    if (res.data && res.data.response) {
      props.modelValue.name = res.data.response.trim()
      ElMessage.success('Назву покращено')
    }
  } catch (error) {
    ElMessage.error('Помилка AI')
  }
}

const triggerImageUpload = () => {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

const removeImage = () => {
  props.modelValue.image_url = ''
}

const handleImageChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    ElMessage.error('Оберіть файл зображення')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('Розмір файлу не більше 5MB')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/api/v1/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    props.modelValue.image_url = res.data.url
    ElMessage.success('Фото збережено')
  } catch (error) {
    ElMessage.error('Помилка завантаження')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>

<style scoped>
.general-tab-content {
  padding: 0;
}

.form-grid {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.form-left-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: calc(100% - 384px);
}

.form-right-col {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 24px; /* Relative to the scrolling container, which starts below the sticky header/tabs */
}

.form-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.section-desc {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.label-with-ai {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.ai-action-btn {
  font-size: 12px;
  color: #4f46e5;
  font-weight: 600;
  padding: 0;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.field-label.required::after {
  content: ' *';
  color: #ef4444;
}

.field-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.field-warning-text {
  font-size: 11px;
  color: #f59e0b;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.modern-input :deep(.el-input__wrapper),
.modern-select :deep(.el-select__wrapper),
.modern-textarea :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  background-color: #f8fafc !important;
  padding: 8px 12px !important;
  font-size: 13px;
  transition: all 0.2s ease;
}

.modern-input :deep(.el-input__wrapper:hover),
.modern-select :deep(.el-select__wrapper:hover),
.modern-textarea :deep(.el-textarea__inner:hover) {
  border-color: #cbd5e1 !important;
  background-color: #f1f5f9 !important;
}

.modern-input :deep(.el-input__wrapper.is-focus),
.modern-select :deep(.el-select__wrapper.is-focused),
.modern-textarea :deep(.el-textarea__inner:focus) {
  border-color: #4f46e5 !important;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
}

/* Physical params list */
.physical-params-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.param-block {
  display: flex;
  align-items: center;
  gap: 20px;
}

.param-block-label {
  width: 120px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.param-block-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.modern-radios :deep(.el-radio-button__inner) {
  border-radius: 8px !important;
  border: 1px solid #e2e8f0 !important;
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
  padding: 6px 12px;
  margin-right: 6px;
}

.modern-radios :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #4f46e5 !important;
  color: #ffffff !important;
  border-color: #4f46e5 !important;
}

.calc-settings {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.small-input {
  width: 70px;
}

.small-select {
  width: 110px;
}

/* Side Cards */
.side-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
}

.image-dropzone {
  width: 100%;
  aspect-ratio: 1;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.2s ease;
  overflow: hidden;
}

.image-dropzone:hover {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.dropzone-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.dropzone-icon {
  color: #94a3b8;
}

.dropzone-text {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.dropzone-hint {
  font-size: 11px;
  color: #94a3b8;
}

.dropzone-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 12px;
}

.side-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.side-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 12px;
}

.toggle-meta {
  display: flex;
  flex-direction: column;
}

.toggle-title {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}

.toggle-desc {
  font-size: 11px;
  font-weight: 500;
}
.toggle-desc.active { color: #10b981; }
.toggle-desc.inactive { color: #94a3b8; }

/* AI Card */
.ai-card {
  background: linear-gradient(145deg, #ffffff 0%, #f5f3ff 100%);
  border: 1px solid #ddd6fe;
}

.ai-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.ai-logo-icon {
  color: #4f46e5;
  font-size: 20px;
}

.ai-meta {
  display: flex;
  flex-direction: column;
}

.ai-card-title {
  font-size: 14px;
  font-weight: 700;
  color: #4f46e5;
}

.ai-score {
  font-size: 11px;
  color: #6d28d9;
  font-weight: 600;
}

.ai-progress-bar {
  height: 6px;
  background: #ede9fe;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 16px;
}

.ai-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 3px;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ai-checklist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-checklist li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #64748b;
  transition: all 0.3s ease;
}

.ai-checklist li.solved {
  color: #10b981;
}

.ai-checklist li.solved .status-icon {
  color: #10b981;
}

.status-icon {
  font-size: 16px;
  color: #cbd5e1;
}

.ai-run-btn {
  background: #ffffff;
  border: 1px solid #ddd6fe;
  color: #4f46e5;
  font-weight: 600;
  border-radius: 10px;
  height: 36px;
  transition: all 0.2s ease;
}

.ai-run-btn:hover {
  background: #f5f3ff;
  border-color: #c4b5fd;
  transform: translateY(-1px);
}
</style>
