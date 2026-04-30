<template>
  <div class="purchases-layout">
    <div class="purchases-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
// Layout wrapper for Purchases module
</script>

<style scoped>
.purchases-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.purchases-content {
  flex: 1;
  overflow-y: auto;
  background-color: var(--erp-bg-page);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
