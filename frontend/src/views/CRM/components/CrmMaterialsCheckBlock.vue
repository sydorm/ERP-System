<template>
  <div class="crm-section" v-if="form.product_id">
    <div class="crm-section-head">
      <span class="crm-section-title">Матеріали на складі</span>
      <span class="mat-status-badge" :class="materialCheck.has_issues ? 'mat-warn' : 'mat-ok'">
        {{ materialCheck.has_issues ? 'є проблеми' : 'все є' }}
      </span>
    </div>

    <div v-if="materialsLoading" class="mat-loading">
      <el-icon class="is-loading"><Loading /></el-icon> Перевіряємо...
    </div>
    <div v-else-if="materialCheck.items.length" class="mat-list">
      <div
        v-for="item in materialCheck.items"
        :key="item.component_id"
        class="mat-row"
        :class="`mat-${item.status}`"
      >
        <span class="mat-name">{{ item.component_name }}</span>
        <span class="mat-req">потрібно: {{ formatQty(item.required_qty) }} {{ item.unit_of_measure }}</span>
        <span class="mat-stock-badge">
          <span class="mat-stock-icon">{{ item.status === 'ok' ? '[+]' : item.status === 'low' ? '[~]' : '[!]' }}</span>
          {{ formatQty(item.available_qty) }} {{ item.unit_of_measure }}
        </span>
      </div>
      <div v-if="materialCheck.has_issues" class="mat-order-row">
        <span>Не вистачає матеріалів — замовте до запуску</span>
        <button class="mat-order-btn" @click="$emit('go-to-purchases')">
          <el-icon><Promotion /></el-icon> Замовити
        </button>
      </div>
    </div>
    <div v-else class="mat-empty">Специфікація не знайдена для цього товару</div>
  </div>
</template>

<script setup>
import { Loading, Promotion } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
  materialCheck: { type: Object, required: true },
  materialsLoading: { type: Boolean, default: false },
  formatQty: { type: Function, required: true },
})

defineEmits(['go-to-purchases'])
</script>
