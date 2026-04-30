<template>
  <div class="crm-section control-card">
    <div class="side-card-title">
      <span>ГОТОВНІСТЬ ЗАЯВКИ</span>
      <b>{{ progress }}%</b>
    </div>
    <div class="readiness-meter">
      <span :style="{ width: `${progress}%` }"></span>
    </div>
    <div class="readiness-list">
      <div v-for="item in items" :key="item.key" class="readiness-item" :class="{ done: item.done }">
        <span>{{ item.done ? '✓' : '•' }}</span>
        <small>{{ item.label }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  progress: { type: Number, required: true },
  items: { type: Array, required: true },
})
</script>
