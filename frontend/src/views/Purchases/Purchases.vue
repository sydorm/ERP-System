<template>
  <div class="purchases-layout">
    <div class="module-nav-wrapper">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="purchases-tabs">
        <el-tab-pane label="Замовлення" name="orders" />
        <el-tab-pane label="Планування" name="planning" />
        <el-tab-pane label="Прибуткові накладні" name="receipts" />
      </el-tabs>
    </div>
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
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const activeTab = ref('orders')

const updateActiveTab = () => {
  if (route.path.includes('/purchases/planning')) activeTab.value = 'planning'
  else if (route.path.includes('/purchases/receipts')) activeTab.value = 'receipts'
  else activeTab.value = 'orders'
}

const handleTabClick = (tab) => {
  if (tab.paneName === 'planning') router.push('/purchases/planning')
  else if (tab.paneName === 'receipts') router.push('/purchases/receipts')
  else router.push('/purchases/orders')
}

watch(() => route.path, updateActiveTab)
onMounted(updateActiveTab)
</script>

<style scoped>
.purchases-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.module-nav-wrapper {
  background: transparent;
  padding: 0 24px;
  margin-bottom: -1px;
  position: relative;
  z-index: 2;
}

.purchases-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  border-bottom: none;
}

.purchases-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.purchases-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
  color: var(--erp-text-secondary);
  height: 48px;
  line-height: 48px;
  transition: all 0.2s;
}

.purchases-tabs :deep(.el-tabs__item.is-active) {
  color: var(--erp-primary);
  font-weight: 700;
}

.purchases-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--erp-primary);
  height: 3px;
  border-radius: 3px 3px 0 0;
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
