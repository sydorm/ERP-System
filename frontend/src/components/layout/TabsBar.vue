<template>
  <div class="tabs-container">
    <el-tabs
      v-model="activeTab"
      type="card"
      closable
      @tab-remove="removeTab"
      @tab-click="clickTab"
      class="custom-tabs"
    >
      <el-tab-pane
        v-for="item in tabsStore.tabs"
        :key="item.path"
        :label="item.title"
        :name="item.path"
        :closable="item.closable"
      >
         <template #label>
            <span class="tab-label">
                {{ item.title }}
            </span>
         </template>
      </el-tab-pane>
    </el-tabs>
    
    <div class="tabs-actions">
        <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
                <el-icon class="new-tab-plus"><Plus /></el-icon>
            </span>
            <template #dropdown>
                <el-dropdown-menu class="tabs-dropdown-menu">
                    <el-dropdown-item command="closeOthers">Закрити інші</el-dropdown-item>
                    <el-dropdown-item command="closeAll">Закрити всі</el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useTabsStore } from '@/stores/tabs'
import { useRouter, useRoute } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'

const tabsStore = useTabsStore()
const router = useRouter()
const route = useRoute()

const activeTab = computed({
  get: () => tabsStore.activeTabPath,
  set: (val) => {
    tabsStore.activeTabPath = val
  }
})

const clickTab = (tab) => {
  router.push(tab.props.name)
}

const removeTab = (targetName) => {
  tabsStore.closeTab(targetName)
}

const handleCommand = (command) => {
    if (command === 'closeOthers') {
        tabsStore.closeOthers(activeTab.value)
    } else if (command === 'closeAll') {
        tabsStore.closeAll()
    }
}

watch(
  () => route.path,
  () => {
    if (route.path) {
        tabsStore.addTab(route)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.tabs-container {
  background-color: #ffffff;
  height: 44px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}

.custom-tabs {
  flex: 1;
  width: 0;
  height: 100%;
}

:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
  height: 100%;
}

:deep(.el-tabs__nav-wrap) {
  height: 100%;
}

:deep(.el-tabs__nav-scroll) {
  height: 100%;
}

:deep(.el-tabs__nav) {
  border: none !important;
  height: 100%;
  display: flex;
  align-items: center;
}

:deep(.el-tabs__item) {
  height: 44px;
  line-height: 44px;
  border: none !important;
  background: transparent;
  font-size: 13.5px;
  color: #9CA3AF;
  font-weight: 500;
  padding: 0 18px !important;
  transition: color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  position: relative;
}

:deep(.el-tabs__item:hover) {
  color: #374151;
  background: transparent;
}

:deep(.el-tabs__item.is-active) {
  color: #1F2937;
  font-weight: 600;
}

:deep(.el-tabs__item.is-active::after) {
  content: "";
  position: absolute;
  bottom: 0;
  left: 18px;
  right: 18px;
  height: 2px;
  background: linear-gradient(90deg, #6C63FF, #00C9A7);
  border-radius: 2px;
}

/* Close Button hidden until hover */
:deep(.el-tabs__item .is-icon-close) {
  opacity: 0;
  width: 0;
  overflow: hidden;
  margin-left: 0;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-tabs__item:hover .is-icon-close) {
  opacity: 1;
  width: 14px;
  margin-left: 6px;
}

:deep(.el-tabs__nav-prev), :deep(.el-tabs__nav-next) {
    line-height: 44px;
}

.tabs-actions {
    margin-left: 12px;
    display: flex;
    align-items: center;
    cursor: pointer;
}

.new-tab-plus {
  font-size: 16px;
  color: #9CA3AF;
  transition: color 0.2s ease;
  stroke-width: 1.5;
}
.new-tab-plus:hover {
  color: #374151;
}

.tabs-dropdown-menu {
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
</style>
