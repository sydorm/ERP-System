<template>
  <div class="crm-section crm-product-block-premium">
    <div class="block-header-premium">
      <div class="flex items-center gap-4">
        <!-- Modern Step Pill -->
        <div class="step-pill-modern variant-2">
          <span class="label">Крок</span>
          <span class="number">02</span>
        </div>
        
        <!-- Icon & Titles -->
        <div class="flex items-center gap-3">
          <div class="header-icon-box variant-2">
            <el-icon><Operation /></el-icon>
          </div>
          <div>
            <h3 class="title">Конфігурація виробу</h3>
            <p class="subtitle">Оберіть модель та налаштуйте індивідуальні параметри</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Completion Status -->
        <div class="status-badge-premium" :class="{ 'is-complete': isBlockComplete }">
          <el-icon><CircleCheck v-if="isBlockComplete" /><InfoFilled v-else /></el-icon>
          <span>{{ isBlockComplete ? 'Конфігуровано' : 'Оберіть виріб' }}</span>
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

    <div class="product-footer-premium">
      <div class="input-card-premium comment-card">
        <label><el-icon class="text-slate-400"><EditPen /></el-icon> Коментар до замовлення</label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="4"
          placeholder="Особливі побажання клієнта..."
          class="compact-textarea"
        />
      </div>

      <div class="media-card-premium">
        <div class="card-head">
          <el-icon><Picture /></el-icon>
          <span>Візуальні референси</span>
        </div>
        <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Box, EditPen, Picture, Operation, CircleCheck, InfoFilled } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

const props = defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])

const isBlockComplete = computed(() => {
  return props.form.product_id && (Object.keys(props.form.attributes_values || {}).length > 0)
})
</script>

<style scoped>
.crm-product-block-premium {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.03), 0 0 0 1px rgba(15, 23, 42, 0.05);
  overflow: hidden;
}

/* --- HEADER PREMIUM --- */
.block-header-premium {
  padding: 16px 24px;
  background: linear-gradient(90deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-pill-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #10B981;
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.step-pill-modern .label { font-size: 8px; font-weight: 800; text-transform: uppercase; opacity: 0.8; line-height: 1; }
.step-pill-modern .number { font-size: 16px; font-weight: 900; line-height: 1.1; }

.header-icon-box {
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #10B981;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  border: 1px solid #DCFCE7;
}

.block-header-premium .title { font-size: 16px; font-weight: 800; color: #1E293B; margin: 0; }
.block-header-premium .subtitle { font-size: 11px; color: #94A3B8; margin: 0; font-weight: 500; }

.status-badge-premium {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #F1F5F9;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  transition: all 0.3s ease;
}
.status-badge-premium.is-complete { background: #ECFDF5; color: #059669; }

.product-selection-zone {
  margin-bottom: 16px;
}

.input-card-premium {
  @apply flex flex-col gap-1 p-3 rounded-xl transition-all duration-200;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 68px;
}
.input-card-premium label { @apply flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1; }
.input-card-premium label .el-icon { @apply text-emerald-400/80 text-[12px]; }
.input-card-premium:focus-within { border-color: #10B981; background: #fff; }

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

.compact-pill.active { background: #10B981; color: #fff; border-color: #10B981; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2); }

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

/* Footer Composition */
.product-footer-premium {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}

.comment-card { min-height: 140px; }

.media-card-premium {
  background: #fff;
  border: 1px solid #E5EAF2;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.media-card-premium .card-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;
}
.media-card-premium .card-head .el-icon { color: #10B981; }

:deep(.el-input__wrapper), :deep(.el-textarea__inner) { @apply shadow-none bg-transparent border-none p-0 h-8 !important; }
:deep(.el-input__inner), :deep(.el-textarea__inner) { @apply font-bold text-slate-700 text-[14px] !important; }

@media (max-width: 992px) {
  .product-footer-premium { grid-template-columns: 1fr; }
}
</style>
