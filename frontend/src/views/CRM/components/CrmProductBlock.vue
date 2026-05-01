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
          <span>{{ productStatusLabel }}</span>
          <b>{{ productCompletionPct }}%</b>
        </div>
      </div>
    </div>

    <div class="product-selection-zone">
      <div class="input-card-premium full-width">
        <div class="field-headline">
          <label><el-icon class="text-emerald-500"><Box /></el-icon> Базова номенклатура</label>
          <span v-if="selectedProduct" class="selected-product-pill">{{ selectedProduct.sku || 'SKU не задано' }}</span>
        </div>
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
        <div v-if="selectedProduct" class="product-glance">
          <div class="product-mark">
            <el-icon><Box /></el-icon>
          </div>
          <div class="product-glance-copy">
            <strong>{{ selectedProduct.name }}</strong>
            <span>{{ productAttributes.length ? `${productAttributes.length} параметрів для налаштування` : 'Модель обрана, параметри не задані' }}</span>
          </div>
        </div>
      </div>
    </div>

    <transition name="el-zoom-in-top">
      <div v-if="productAttributes.length" class="attributes-compact-zone">
        <div class="attributes-zone-head">
          <div>
            <span class="zone-kicker">Параметри виробу</span>
            <strong>Налаштування під клієнта</strong>
          </div>
          <em>{{ filledAttributes }} / {{ productAttributes.length }} заповнено</em>
        </div>
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
        <div class="functional-card-title">
          <label><el-icon class="text-slate-400"><EditPen /></el-icon> Коментар до замовлення</label>
          <span>Для виробництва</span>
        </div>
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
          <div class="card-head-main">
            <el-icon><Picture /></el-icon>
            <span>Візуальні референси</span>
          </div>
          <em>{{ form.reference_photo ? '1 файл' : 'очікує файл' }}</em>
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

const selectedProduct = computed(() => props.products.find(p => String(p.id) === String(props.form.product_id)))
const filledAttributes = computed(() => (
  Object.values(props.form.attributes_values || {}).filter(value => {
    if (value == null || value === '') return false
    if (typeof value === 'object') return Object.values(value).some(Boolean)
    return true
  }).length
))
const productCompletionPct = computed(() => {
  const checks = [props.form.product_id, filledAttributes.value > 0, props.form.comment]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
})
const productStatusLabel = computed(() => {
  if (isBlockComplete.value) return 'Конфігуровано'
  if (props.form.product_id) return 'Потрібні параметри'
  return 'Оберіть виріб'
})
</script>

<style scoped>
.crm-product-block-premium {
  background: #fff;
  border-radius: 24px;
  border: 1px solid rgba(226, 232, 240, .9);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07), 0 1px 0 rgba(255, 255, 255, .9) inset;
  overflow: hidden;
  position: relative;
  isolation: isolate;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.crm-product-block-premium:hover {
  transform: translateY(-2px);
  border-color: rgba(187, 247, 208, .95);
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.09), 0 1px 0 rgba(255, 255, 255, .9) inset;
}

.crm-product-block-premium::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: linear-gradient(180deg, #15B97A, #0E905F);
  opacity: .95;
  z-index: 1;
}

/* --- HEADER PREMIUM --- */
.block-header-premium {
  padding: 18px 24px 16px 28px;
  background:
    radial-gradient(circle at 11% 0%, rgba(21, 185, 122, .15), transparent 29%),
    linear-gradient(90deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}

.step-pill-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #15B97A 0%, #0E905F 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(21, 185, 122, 0.28);
  position: relative;
  overflow: hidden;
}
.step-pill-modern::after {
  content: '';
  position: absolute;
  inset: -40% -20% auto auto;
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, .25);
  border-radius: 999px;
}
.step-pill-modern .label { font-size: 8px; font-weight: 800; text-transform: uppercase; opacity: 0.8; line-height: 1; }
.step-pill-modern .number { font-size: 16px; font-weight: 900; line-height: 1.1; }

.header-icon-box {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, .9);
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #10B981;
  box-shadow: 0 8px 18px rgba(21,185,122,.11);
  border: 1px solid #DCFCE7;
}

.block-header-premium .title { font-size: 17px; font-weight: 850; color: #0F172A; margin: 0; letter-spacing: -0.02em; }
.block-header-premium .subtitle { font-size: 11px; color: #94A3B8; margin: 0; font-weight: 500; }

.status-badge-premium {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(241, 245, 249, .82);
  border: 1px solid rgba(226, 232, 240, .9);
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  transition: all 0.3s ease;
  white-space: nowrap;
}
.status-badge-premium b {
  color: #065F46;
  font-size: 10px;
  font-weight: 900;
}
.status-badge-premium.is-complete { background: #ECFDF5; border-color: #BBF7D0; color: #059669; }

.product-selection-zone {
  padding: 16px 16px 0;
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FFFB 100%);
}

.field-headline,
.functional-card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.selected-product-pill {
  padding: 4px 8px;
  border-radius: 999px;
  color: #047857;
  background: #ECFDF5;
  border: 1px solid #BBF7D0;
  font-size: 10px;
  font-weight: 850;
}

.product-glance {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding: 9px 10px;
  border-radius: 12px;
  border: 1px solid #DDF7EA;
  background: linear-gradient(90deg, rgba(236, 253, 245, .9), rgba(255,255,255,.95));
}

.product-mark {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, #15B97A, #0E905F);
  box-shadow: 0 8px 14px rgba(21,185,122,.20);
}

.product-glance-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  line-height: 1.18;
}

.product-glance-copy strong {
  overflow: hidden;
  color: #0F172A;
  font-size: 12px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-glance-copy span {
  color: #64748B;
  font-size: 10px;
  font-weight: 700;
}

.input-card-premium {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease, background .18s ease;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 68px;
}
.input-card-premium:hover {
  border-color: #CBD5E1;
  box-shadow: 0 10px 24px rgba(15,23,42,.045);
  transform: translateY(-1px);
}
.input-card-premium label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  color: #94A3B8;
  font-size: 10px;
  font-weight: 850;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.input-card-premium label .el-icon { color: rgba(21,185,122,.82); font-size: 12px; }
.input-card-premium:focus-within { border-color: #10B981; background: #fff; box-shadow: 0 0 0 4px rgba(21,185,122,.06); }

.attributes-compact-zone {
  background:
    linear-gradient(180deg, rgba(248,250,252,.9), #FFFFFF);
  border-radius: 18px;
  padding: 16px;
  margin: 16px;
  border: 1px solid #F1F5F9;
}

.attributes-zone-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.attributes-zone-head div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.zone-kicker {
  color: #10B981;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.attributes-zone-head strong {
  color: #0F172A;
  font-size: 13px;
  font-weight: 850;
}

.attributes-zone-head em {
  padding: 5px 9px;
  border-radius: 999px;
  color: #047857;
  background: #ECFDF5;
  border: 1px solid #BBF7D0;
  font-size: 10px;
  font-style: normal;
  font-weight: 850;
  white-space: nowrap;
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
  transform: translateY(-1px);
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
  padding: 0 16px 16px;
}

.comment-card {
  min-height: 172px;
  background:
    linear-gradient(180deg, #FFFFFF, #F8FAFC);
}

.functional-card-title span {
  padding: 4px 8px;
  border-radius: 999px;
  color: #64748B;
  background: #F1F5F9;
  font-size: 10px;
  font-weight: 800;
}

.media-card-premium {
  background: #fff;
  border: 1px solid #E5EAF2;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.media-card-premium:hover {
  border-color: #BBF7D0;
  box-shadow: 0 12px 28px rgba(15,23,42,.055);
  transform: translateY(-1px);
}
.media-card-premium .card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;
}
.card-head-main {
  display: flex;
  align-items: center;
  gap: 8px;
}
.media-card-premium .card-head .el-icon { color: #10B981; }
.media-card-premium .card-head em {
  color: #94A3B8;
  font-size: 10px;
  font-style: normal;
  letter-spacing: 0;
  text-transform: none;
}

:deep(.el-input__wrapper), :deep(.el-textarea__inner) {
  box-shadow: none !important;
  background: transparent !important;
  border: 0 !important;
  padding: 0 !important;
  min-height: 34px !important;
}
:deep(.el-input__inner), :deep(.el-textarea__inner) { color: #334155 !important; font-size: 14px !important; font-weight: 750 !important; }

@media (max-width: 992px) {
  .product-footer-premium { grid-template-columns: 1fr; }
  .block-header-premium {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
