<template>
  <div class="crm-section control-card">
    <div class="side-card-title">
      <span>ГОТОВНІСТЬ ЗАЯВКИ</span>
      <b>{{ readinessProgress }}%</b>
    </div>
    <div class="readiness-meter">
      <span :style="{ width: `${readinessProgress}%` }"></span>
    </div>
    <div class="readiness-list">
      <div
        v-for="item in readinessItems"
        :key="item.key"
        class="readiness-item"
        :class="{ done: item.done }"
      >
        <span>{{ item.done ? '✓' : '•' }}</span>
        <small>{{ item.label }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  readinessProgress: { type: Number, default: 0 },
  readinessItems: { type: Array, default: () => [] }
})
</script>
