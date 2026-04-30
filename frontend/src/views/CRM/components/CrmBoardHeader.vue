<template>
  <div class="crm-board-header">
    <div class="crm-header-left">
      <div class="crm-title-row">
        <h1 class="crm-title">Дошка замовлень</h1>
        <span class="crm-count-badge">{{ ordersCount }} замовлень</span>
      </div>
      <p class="crm-subtitle">Керування меблевим виробництвом</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  ordersCount: { type: Number, default: 0 }
})
</script>
