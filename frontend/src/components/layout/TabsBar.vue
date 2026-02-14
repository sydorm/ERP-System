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
                <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
                <el-dropdown-menu>
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
import { ArrowDown } from '@element-plus/icons-vue'

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

// Watch route to add tab
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
  background-color: #fff;
  padding: 8px 16px 0 16px;
  border-bottom: 1px solid #eef0f2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}

.custom-tabs {
  flex: 1;
  width: 0;
}

:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}

:deep(.el-tabs__nav) {
  border: none !important;
}

:deep(.el-tabs__item) {
  height: 36px;
  line-height: 36px;
  border: none !important;
  background: transparent;
  margin-right: 4px;
  border-radius: 6px 6px 0 0;
  font-size: 13px;
  color: #606266;
  padding: 0 16px !important;
  transition: all 0.2s;
}

:deep(.el-tabs__item:hover) {
  background-color: #f5f7fa;
  color: #409eff;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  background: #f0f7ff;
  font-weight: 600;
  position: relative;
}

:deep(.el-tabs__item.is-active::after) {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #409eff;
}

:deep(.el-tabs__nav-prev), :deep(.el-tabs__nav-next) {
    line-height: 36px;
}

.tabs-actions {
    margin-left: 10px;
    padding-bottom: 8px;
    cursor: pointer;
    color: #909399;
}
.tabs-actions:hover {
    color: #409eff;
}
</style>
