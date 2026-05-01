<template>
  <div class="crm-section crm-product-section">
    <div class="product-block-head">
      <div class="product-title-block">
        <span class="product-kicker">Крок 2 · Номенклатура</span>
        <h3>Вибір виробу</h3>
        <p>Оберіть базову модель та вкажіть індивідуальні характеристики замовлення.</p>
      </div>
      <div class="product-status-badges" v-if="productAttributes.length">
        <span class="status-badge-modern success">
          <el-icon><Check /></el-icon>
          Характеристики підтягнуто
        </span>
      </div>
    </div>

    <div class="product-main-field">
      <label class="crm-label">Виріб з каталогу</label>
      <el-select
        v-model="form.product_id"
        filterable
        placeholder="Почніть вводити назву виробу..."
        class="product-select-modern"
        @change="$emit('product-change', $event)"
      >
        <template #prefix>
          <el-icon><Box /></el-icon>
        </template>
        <el-option
          v-for="p in products"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        >
          <div class="product-option">
            <span class="p-name">{{ p.name }}</span>
            <span class="p-price" v-if="p.price">{{ p.price }} грн</span>
          </div>
        </el-option>
      </el-select>
    </div>

    <div v-if="productAttributes.length" class="attributes-container-modern">
      <div class="attr-grid-modern">
        <div v-for="attr in productAttributes" :key="attr.id" class="attr-card-modern">
          <label class="crm-label">{{ attr.name }}</label>

          <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="attr-options-modern">
            <button
              v-for="opt in attr.options"
              :key="opt.id"
              class="attr-pill-modern"
              :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
              @click="$emit('set-attr-value', attr.id, opt.value)"
            >
              <span v-if="attr.type === 'COLOR' && opt.color_code" class="color-dot-modern" :style="{ background: opt.color_code }" />
              {{ opt.value }}
            </button>
          </div>

          <div v-else-if="attr.type === 'DIMENSIONS'" class="attr-dims-modern">
            <div class="dim-input-group">
              <el-input-number
                :model-value="form.attributes_values?.[attr.id]?.w"
                @update:model-value="v => $emit('set-attr-dim', attr.id, 'w', v)"
                :min="1" placeholder="Ш"
              />
              <span class="dim-x">×</span>
              <el-input-number
                :model-value="form.attributes_values?.[attr.id]?.h"
                @update:model-value="v => $emit('set-attr-dim', attr.id, 'h', v)"
                :min="1" placeholder="В"
              />
              <span class="dim-unit">см</span>
            </div>
          </div>

          <div v-else class="attr-input-modern">
            <el-input
              :model-value="form.attributes_values?.[attr.id]"
              @update:model-value="v => $emit('set-attr-value', attr.id, v)"
              :placeholder="attr.name"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="product-footer-grid">
      <div class="crm-field">
        <label class="crm-label">Коментар до замовлення</label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="3"
          placeholder="Напишіть особливі побажання або деталі..."
          class="modern-textarea"
        />
      </div>

      <div class="crm-field">
        <label class="crm-label">Референси та фото</label>
        <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, Box } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  selectedProduct: { type: Object, default: null },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])
</script>
