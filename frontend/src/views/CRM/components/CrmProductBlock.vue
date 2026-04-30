<template>
  <div class="crm-section">
    <div class="crm-section-head">
      <span class="crm-section-title">Виріб</span>
      <span class="crm-attr-hint" v-if="productAttributes.length">
        <el-icon><Check /></el-icon>
        характеристики підтягнуто ({{ productAttributes.length }})
      </span>
    </div>

    <div class="crm-field">
      <label class="crm-label">Оберіть виріб з номенклатури</label>
      <el-select
        v-model="form.product_id"
        filterable
        placeholder="Почніть вводити назву..."
        style="width:100%"
        @change="$emit('product-change', $event)"
      >
        <el-option
          v-for="p in products"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        />
      </el-select>
      <p class="product-hint" v-if="selectedProduct">
        {{ selectedProduct.name }}
        <span v-if="productAttributes.length"> — підтягнуто {{ productAttributes.length }} характеристики</span>
      </p>
    </div>

    <div v-if="productAttributes.length" class="attributes-block">
      <div v-for="attr in productAttributes" :key="attr.id" class="attr-group">
        <label class="crm-label">{{ attr.name }}</label>

        <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="attr-pills">
          <button
            v-for="opt in attr.options"
            :key="opt.id"
            class="attr-pill"
            :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
            :style="attr.type === 'COLOR' && opt.color_code ? { '--dot-color': opt.color_code } : {}"
            @click="$emit('set-attr-value', attr.id, opt.value)"
          >
            <span v-if="attr.type === 'COLOR' && opt.color_code" class="attr-color-dot" :style="{ background: opt.color_code }" />
            {{ opt.value }}
          </button>
        </div>

        <div v-else-if="attr.type === 'DIMENSIONS'" class="attr-dims">
          <el-input-number
            :model-value="form.attributes_values?.[attr.id]?.w"
            @update:model-value="v => $emit('set-attr-dim', attr.id, 'w', v)"
            :min="1" placeholder="Ш" size="small" style="width:90px"
          />
          <span class="dims-sep">×</span>
          <el-input-number
            :model-value="form.attributes_values?.[attr.id]?.h"
            @update:model-value="v => $emit('set-attr-dim', attr.id, 'h', v)"
            :min="1" placeholder="В" size="small" style="width:90px"
          />
          <span class="dims-unit">см</span>
        </div>

        <div v-else>
          <el-input
            :model-value="form.attributes_values?.[attr.id]"
            @update:model-value="v => $emit('set-attr-value', attr.id, v)"
            size="small"
            :placeholder="attr.name"
            style="width:100%"
          />
        </div>
      </div>
    </div>

    <div class="crm-field">
      <label class="crm-label">Коментар до виробу</label>
      <el-input
        v-model="form.comment"
        type="textarea"
        :rows="3"
        placeholder="Індивідуальні побажання клієнта..."
      />
    </div>

    <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
  </div>
</template>

<script setup>
import { Check } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  selectedProduct: { type: Object, default: null },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])
</script>
