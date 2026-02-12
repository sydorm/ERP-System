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
  background-color: #f5f7fa;
  padding: 6px 10px 0 10px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.custom-tabs {
  flex: 1;
  width: 0; /* Important for flex overflow */
}

/* Override Element Plus Tabs Styles for Compact Look */
:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}

:deep(.el-tabs__nav) {
  border: none !important;
}

:deep(.el-tabs__item) {
  height: 32px;
  line-height: 32px;
  border: 1px solid #e4e7ed !important;
  background: white;
  margin-right: 4px;
  border-radius: 4px 4px 0 0;
  font-size: 13px;
  color: #606266;
  padding: 0 16px !important;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  background: #fff;
  border-bottom: 1px solid #fff !important; /* Merge with content */
  font-weight: 500;
}

:deep(.el-tabs__nav-prev), :deep(.el-tabs__nav-next) {
    line-height: 32px;
}

.tabs-actions {
    margin-left: 10px;
    cursor: pointer;
    color: #909399;
}
.tabs-actions:hover {
    color: #409eff;
}
</style>
