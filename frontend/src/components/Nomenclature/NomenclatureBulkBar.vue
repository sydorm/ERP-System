<template>
  <transition name="bulk-fade">
    <div v-if="selectedCount > 0" class="bulk-action-bar">
      <div class="bulk-info">
        <div class="selection-badge">{{ selectedCount }}</div>
        <span class="selection-text">позицій обрано</span>
        <button class="clear-btn" @click="$emit('clear')">Скасувати</button>
      </div>

      <div class="bulk-divider"></div>

      <div class="bulk-actions">
        <!-- Change Category -->
        <el-dropdown @command="handleCategoryCommand">
          <button class="bulk-btn">
            <el-icon><Collection /></el-icon>
            Змінити категорію
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="cat in categories" 
                :key="cat.code" 
                :command="cat.code"
              >
                {{ cat.name }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- Change Unit of Measure -->
        <el-dropdown @command="(uom) => $emit('change-uom', uom)">
          <button class="bulk-btn">
            <el-icon><ScaleToOriginal /></el-icon>
            Од. виміру
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="uom in uoms" 
                :key="uom.code" 
                :command="uom.code"
              >
                {{ uom.name }} ({{ uom.short_name }})
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- Price Adjustment (Planned) -->
        <button class="bulk-btn" @click="$emit('action', 'price')">
          <el-icon><Money /></el-icon>
          Коригувати ціну
        </button>

        <!-- Status Change (Planned) -->
        <el-dropdown @command="(cmd) => $emit('action', 'status', cmd)">
          <button class="bulk-btn">
            <el-icon><CircleCheck /></el-icon>
            Статус
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="active">Активний</el-dropdown-item>
              <el-dropdown-item command="archived">Архів</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- AI Advice (Creative) -->
        <button class="bulk-btn ai-magic-btn" @click="$emit('action', 'ai-optimize')">
          <span class="ai-sparkle">✨</span>
          AI Оптимізація
        </button>

        <div class="bulk-divider"></div>

        <!-- Delete -->
        <button class="bulk-btn delete-btn" @click="$emit('action', 'delete')">
          <el-icon><Delete /></el-icon>
          Видалити
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { 
  Collection, Money, CircleCheck, Delete, ScaleToOriginal 
} from '@element-plus/icons-vue'

const props = defineProps({
  selectedCount: { type: Number, default: 0 },
  categories: { type: Array, default: () => [] },
  uoms: { type: Array, default: () => [] }
})

const emit = defineEmits(['clear', 'action', 'change-category', 'change-uom'])

const handleCategoryCommand = (categoryCode) => {
  emit('change-category', categoryCode)
}
</script>

<style scoped>
.bulk-action-bar {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1050;
  height: 64px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  display: flex;
  align-items: center;
  padding: 0 12px 0 24px;
  color: #fff;
  min-width: 600px;
}

.bulk-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-badge {
  background: #1463FF;
  color: #fff;
  min-width: 24px;
  height: 24px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 13px;
  box-shadow: 0 0 15px rgba(20, 99, 255, 0.4);
}

.selection-text {
  font-size: 14px;
  font-weight: 600;
  color: #94A3B8;
}

.clear-btn {
  background: transparent;
  border: none;
  color: #F8FAFC;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.clear-btn:hover { opacity: 1; }

.bulk-divider {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 20px;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bulk-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.bulk-btn .el-icon {
  font-size: 16px;
  color: #1463FF;
}

.ai-magic-btn {
  background: linear-gradient(135deg, rgba(99, 91, 255, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
  border-color: rgba(99, 91, 255, 0.3);
}

.ai-magic-btn:hover {
  background: linear-gradient(135deg, rgba(99, 91, 255, 0.3) 0%, rgba(124, 58, 237, 0.3) 100%);
}

.ai-sparkle { font-size: 16px; }

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
}

.delete-btn .el-icon { color: #EF4444; }

/* Transitions */
.bulk-fade-enter-active, .bulk-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.bulk-fade-enter-from, .bulk-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(40px);
}
</style>
