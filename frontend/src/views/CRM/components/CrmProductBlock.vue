<template>
  <div class="crm-section crm-product-block-premium">
    <div class="product-header-compact">
      <div class="header-main">
        <div class="step-badge-mini">Крок 2</div>
        <h3 class="text-base font-extrabold text-slate-800">Конфігурація виробу</h3>
      </div>
      <div class="header-status" v-if="productAttributes.length">
        <div class="status-pill-mini success">
          <el-icon><Check /></el-icon>
          <span>{{ productAttributes.length }} параметрів</span>
        </div>
      </div>
    </div>

    <div class="product-selection-zone">
      <div class="input-card-premium full-width">
        <label><el-icon class="text-emerald-500"><Box /></el-icon> Базова номенклатура</label>
        <el-select
          v-model="form.product_id"
          filterable
          placeholder="Оберіть виріб..."
          class="compact-select w-full"
          @change="$emit('product-change', $event)"
        >
          <el-option
            v-for="p in products"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          >
            <div class="flex items-center justify-between w-full">
              <span class="text-xs font-semibold">{{ p.name }}</span>
              <span class="text-[10px] text-emerald-600 font-bold" v-if="p.price">{{ p.price }} грн</span>
            </div>
          </el-option>
        </el-select>
      </div>
    </div>

    <transition name="el-zoom-in-top">
      <div v-if="productAttributes.length" class="attributes-compact-zone">
        <div class="attributes-grid">
          <div v-for="attr in productAttributes" :key="attr.id" class="input-card-premium">
            <label>{{ attr.name }}</label>
            
            <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="compact-options">
              <button
                v-for="opt in attr.options"
                :key="opt.id"
                class="compact-pill"
                :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
                @click="$emit('set-attr-value', attr.id, opt.value)"
              >
                <span v-if="attr.type === 'COLOR' && opt.color_code" class="color-dot" :style="{ background: opt.color_code }" />
                {{ opt.value }}
              </button>
            </div>

            <div v-else-if="attr.type === 'DIMENSIONS'" class="compact-dims">
              <el-input-number
                :model-value="form.attributes_values?.[attr.id]?.w"
                @update:model-value="v => $emit('set-attr-dim', attr.id, 'w', v)"
                :min="1" placeholder="Ш"
                controls-position="right"
                class="dim-input"
              />
              <span class="sep">×</span>
              <el-input-number
                :model-value="form.attributes_values?.[attr.id]?.h"
                @update:model-value="v => $emit('set-attr-dim', attr.id, 'h', v)"
                :min="1" placeholder="В"
                controls-position="right"
                class="dim-input"
              />
              <span class="unit">см</span>
            </div>

            <div v-else class="compact-text-input">
              <el-input
                :model-value="form.attributes_values?.[attr.id]"
                @update:model-value="v => $emit('set-attr-value', attr.id, v)"
                :placeholder="attr.name"
                class="compact-field"
              />
            </div>
          </div>
        </div>
      </div>
    </transition>

    <div class="product-footer-compact">
      <div class="input-card-premium comment-card">
        <label><el-icon class="text-slate-400"><EditPen /></el-icon> Коментар</label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="2"
          placeholder="Особливі побажання..."
          class="compact-textarea"
        />
      </div>

      <div class="media-card">
        <label class="text-[11px] font-semibold text-slate-500 mb-1.5 block px-1">
          <el-icon class="text-slate-400 mr-1"><Picture /></el-icon> Референси
        </label>
        <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, Box, EditPen, Picture } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])
</script>

<style scoped>
.crm-product-block-premium {
  padding: 20px;
  background: #fff;
  border-radius: 24px;
}

.product-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-badge-mini {
  background: #15B97A;
  color: #fff;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
}

.status-pill-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
}

.status-pill-mini.success {
  background: #ECFDF5;
  color: #059669;
}

.product-selection-zone {
  margin-bottom: 16px;
}

.input-card-premium {
  @apply flex flex-col gap-1 p-2.5 rounded-xl transition-all duration-200;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 64px;
}

.input-card-premium label {
  @apply flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 px-0.5;
}

.attributes-compact-zone {
  background: #F8FAFC;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #F1F5F9;
}

.attributes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.compact-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 2px;
}

.compact-pill {
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.compact-pill:hover {
  border-color: #10B981;
  color: #10B981;
}

.compact-pill.active {
  background: #10B981;
  color: #fff;
  border-color: #10B981;
}

.color-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  border: 1px solid rgba(0,0,0,0.1);
}

.compact-dims {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.dim-input {
  width: 70px !important;
}

:deep(.el-input-number.is-controls-right .el-input-number__increase),
:deep(.el-input-number.is-controls-right .el-input-number__decrease) {
  width: 20px !important;
}

.compact-dims .sep { color: #CBD5E1; font-weight: 800; font-size: 12px; }
.compact-dims .unit { color: #94A3B8; font-size: 10px; font-weight: 700; }

.product-footer-compact {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
}

.comment-card {
  min-height: 100px;
}

:deep(.el-input__wrapper), :deep(.el-textarea__inner) {
  @apply shadow-none bg-transparent border-none p-0 h-7 !important;
  box-shadow: none !important;
}

:deep(.el-input__inner), :deep(.el-textarea__inner) {
  @apply font-bold text-slate-700 text-[13px] !important;
}

:deep(.compact-select .el-select__wrapper) {
  @apply h-8 !important;
  min-height: 32px !important;
}

@media (max-width: 992px) {
  .product-footer-compact { grid-template-columns: 1fr; }
}
</style>
