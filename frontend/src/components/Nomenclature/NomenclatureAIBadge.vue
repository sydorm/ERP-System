<template>
  <el-tooltip
    :content="'AI Попередження: ' + reason"
    placement="top"
    effect="dark"
  >
    <span class="ai-warning-badge">
      <el-icon><WarningFilled /></el-icon>
      <span class="ai-pulse"></span>
    </span>
  </el-tooltip>
</template>

<script setup>
import { WarningFilled } from '@element-plus/icons-vue'

defineProps({
  reason: {
    type: String,
    default: 'Потребує уваги'
  }
})
</script>

<style scoped>
.ai-warning-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
  font-size: 14px;
  position: relative;
  cursor: help;
}

.ai-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.4);
  animation: pulse 2s infinite;
  z-index: -1;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.8;
  }
  70% {
    transform: scale(2);
    opacity: 0;
  }
  100% {
    transform: scale(0.8);
    opacity: 0;
  }
}
</style>
