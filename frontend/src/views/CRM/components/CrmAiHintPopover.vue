<template>
  <el-popover placement="top-end" :width="290" trigger="click" popper-class="crm-hint-popover">
    <template #reference>
      <button class="card-hint-btn" @click.stop>
        <el-icon><MagicStick /></el-icon>
      </button>
    </template>
    <div class="hint-popover-content" @click.stop>
      <div class="hint-popover-title">
        <el-icon><MagicStick /></el-icon>
        Підказка по заявці
      </div>
      <ul v-if="hints.length" class="hint-list">
        <li v-for="hint in hints" :key="hint.text" :class="hint.level">
          {{ hint.text }}
        </li>
      </ul>
      <div v-else class="hint-good">Все добре. Критичних проблем немає.</div>
    </div>
  </el-popover>
</template>

<script setup>
import { MagicStick } from '@element-plus/icons-vue'

defineProps({
  hints: { type: Array, default: () => [] }
})
</script>
