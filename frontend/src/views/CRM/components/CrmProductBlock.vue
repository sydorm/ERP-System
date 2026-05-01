<template>
  <div class="crm-section crm-product-section-premium">
    <div class="product-block-header">
      <div class="header-main">
        <div class="step-badge">Крок 2</div>
        <div class="title-group">
          <h3>Конфігурація виробу</h3>
          <p>Оберіть модель та налаштуйте індивідуальні параметри</p>
        </div>
      </div>
      <div class="header-status" v-if="productAttributes.length">
        <div class="glass-pill success">
          <el-icon><Check /></el-icon>
          <span>{{ productAttributes.length }} параметрів знайдено</span>
        </div>
      </div>
    </div>

    <div class="product-selection-zone">
      <div class="selection-card">
        <label class="premium-label">
          <el-icon><Box /></el-icon>
          Базова номенклатура
        </label>
        <el-select
          v-model="form.product_id"
          filterable
          placeholder="Почніть вводити назву виробу..."
          class="premium-select"
          @change="$emit('product-change', $event)"
        >
          <template #prefix>
            <el-icon class="select-icon-modern"><Box /></el-icon>
          </template>
          <el-option
            v-for="p in products"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          >
            <div class="product-option-modern">
              <span class="p-name">{{ p.name }}</span>
              <span class="p-price" v-if="p.price">{{ p.price }} грн</span>
            </div>
          </el-option>
        </el-select>
      </div>
    </div>

    <transition name="slide-fade">
      <div v-if="productAttributes.length" class="attributes-explorer">
        <div class="explorer-head">
          <el-icon><Operation /></el-icon>
          Характеристики моделі
        </div>
        <div class="attributes-grid-modern">
          <div v-for="attr in productAttributes" :key="attr.id" class="attribute-item-card">
            <div class="attr-info">
              <label>{{ attr.name }}</label>
            </div>

            <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="options-pills-modern">
              <button
                v-for="opt in attr.options"
                :key="opt.id"
                class="pill-choice"
                :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
                @click="$emit('set-attr-value', attr.id, opt.value)"
              >
                <span v-if="attr.type === 'COLOR' && opt.color_code" class="color-indicator" :style="{ background: opt.color_code }" />
                {{ opt.value }}
              </button>
            </div>

            <div v-else-if="attr.type === 'DIMENSIONS'" class="dimensions-input-modern">
              <div class="dim-box">
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.w"
                  @update:model-value="v => $emit('set-attr-dim', attr.id, 'w', v)"
                  :min="1" placeholder="Ш"
                  controls-position="right"
                />
                <span class="sep">×</span>
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.h"
                  @update:model-value="v => $emit('set-attr-dim', attr.id, 'h', v)"
                  :min="1" placeholder="В"
                  controls-position="right"
                />
                <span class="unit">см</span>
              </div>
            </div>

            <div v-else class="text-input-modern">
              <el-input
                :model-value="form.attributes_values?.[attr.id]"
                @update:model-value="v => $emit('set-attr-value', attr.id, v)"
                :placeholder="attr.name"
              />
            </div>
          </div>
        </div>
      </div>
    </transition>

    <div class="nomenclature-footer">
      <div class="comment-block">
        <label class="premium-label">
          <el-icon><EditPen /></el-icon>
          Коментар до замовлення
        </label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="4"
          placeholder="Напишіть особливі побажання клієнта..."
          class="premium-textarea"
        />
      </div>

      <div class="media-block">
        <label class="premium-label">
          <el-icon><Picture /></el-icon>
          Візуальні референси
        </label>
        <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, Box, Operation, EditPen, Picture } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  selectedProduct: { type: Object, default: null },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])
</script>

<style scoped>
.crm-product-section-premium {
  padding: 32px;
  background: #fff;
  border-radius: 24px;
}

.product-block-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-main {
  display: flex;
  gap: 16px;
  align-items: center;
}

.step-badge {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #fff;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.title-group h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 850;
  color: #0F172A;
  letter-spacing: -0.02em;
}

.title-group p {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
}

.glass-pill.success {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.product-selection-zone {
  margin-bottom: 32px;
}

.selection-card {
  background: #F8FAFC;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid #F1F5F9;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.selection-card:hover {
  background: #fff;
  border-color: #10B981;
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.08);
}

.premium-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 12px;
}

.premium-label .el-icon {
  color: #10B981;
  font-size: 16px;
}

.product-option-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.p-price {
  font-weight: 800;
  color: #10B981;
}

.attributes-explorer {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.explorer-head {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 800;
  color: #0F172A;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #F1F5F9;
}

.attributes-grid-modern {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.attribute-item-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attribute-item-card label {
  font-size: 12px;
  font-weight: 700;
  color: #64748B;
}

.options-pills-modern {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-choice {
  padding: 8px 16px;
  border-radius: 12px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.pill-choice:hover {
  border-color: #10B981;
  color: #059669;
}

.pill-choice.active {
  background: #10B981;
  color: #fff;
  border-color: #10B981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
  transform: scale(1.02);
}

.color-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
  border: 1px solid rgba(0,0,0,0.1);
}

.dimensions-input-modern .dim-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dim-box .sep { color: #CBD5E1; font-weight: 800; }
.dim-box .unit { color: #94A3B8; font-size: 12px; font-weight: 700; }

.nomenclature-footer {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 32px;
}

:deep(.el-input__wrapper), :deep(.el-textarea__inner) {
  border-radius: 14px;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 12px;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover), :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #CBD5E1 inset !important;
}

:deep(.el-input__wrapper.is-focus), :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #10B981 inset !important;
  background: #F0FDF4;
}

.slide-fade-enter-active { transition: all 0.4s ease-out; }
.slide-fade-leave-active { transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(20px); opacity: 0; }

@media (max-width: 1200px) {
  .nomenclature-footer {
    grid-template-columns: 1fr;
  }
}
</style>
