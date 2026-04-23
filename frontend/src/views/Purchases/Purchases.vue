<template>
  <div class="purchases-layout">
    <div class="tabs-container">
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

.tabs-container {
  background: white;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
}

.purchases-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.purchases-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.purchases-content {
  flex: 1;
  overflow-y: auto;
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
