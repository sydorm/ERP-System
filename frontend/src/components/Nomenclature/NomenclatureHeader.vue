<template>
  <div class="stats-row-dense">
    <!-- Всього позицій -->
    <div class="stats-card-dense">
      <div class="stats-card-dense__icon total">
        <el-icon><Box /></el-icon>
      </div>
      <div class="stats-card-dense__content">
        <span class="stats-card-dense__label">Всього позицій</span>
        <span class="stats-card-dense__value">{{ stats.total_products }}</span>
        <span class="stats-card-dense__subtext">+12 за 30 днів</span>
      </div>
      <div class="stats-card-dense__sparkline">
        <svg width="60" height="20"><path d="M0,10 L10,15 L20,5 L30,18 L40,8 L50,12 L60,2" fill="none" stroke="#635bff" stroke-width="2"/></svg>
      </div>
    </div>

    <!-- В наявності -->
    <div class="stats-card-dense">
      <div class="stats-card-dense__icon success">
        <el-icon><Check /></el-icon>
      </div>
      <div class="stats-card-dense__content">
        <span class="stats-card-dense__label">В наявності</span>
        <span class="stats-card-dense__value">{{ stats.in_stock }}</span>
        <span class="stats-card-dense__subtext">+18 за 30 днів</span>
      </div>
      <div class="stats-card-dense__sparkline">
        <svg width="60" height="20"><path d="M0,18 L10,12 L20,15 L30,8 L40,10 L50,5 L60,2" fill="none" stroke="#22c55e" stroke-width="2"/></svg>
      </div>
    </div>

    <!-- Закінчуються -->
    <div class="stats-card-dense">
      <div class="stats-card-dense__icon warning">
        <el-icon><Warning /></el-icon>
      </div>
      <div class="stats-card-dense__content">
        <span class="stats-card-dense__label">Закінчуються</span>
        <span class="stats-card-dense__value">{{ stats.low_stock }}</span>
        <span class="stats-card-dense__subtext">+4 за 30 днів</span>
      </div>
      <div class="stats-card-dense__sparkline">
        <svg width="60" height="20"><path d="M0,5 L10,8 L20,2 L30,12 L40,5 L50,15 L60,18" fill="none" stroke="#f59e0b" stroke-width="2"/></svg>
      </div>
    </div>

    <!-- Немає -->
    <div class="stats-card-dense">
      <div class="stats-card-dense__icon danger">
        <el-icon><CircleClose /></el-icon>
      </div>
      <div class="stats-card-dense__content">
        <span class="stats-card-dense__label">Немає</span>
        <span class="stats-card-dense__value">{{ stats.out_of_stock }}</span>
        <span class="stats-card-dense__subtext">-3 за 30 днів</span>
      </div>
      <div class="stats-card-dense__sparkline">
        <svg width="60" height="20"><path d="M0,2 L10,5 L20,12 L30,8 L40,15 L50,12 L60,18" fill="none" stroke="#ef4444" stroke-width="2"/></svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Box, Check, Warning, CircleClose } from '@element-plus/icons-vue'

defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      total_products: 0,
      in_stock: 0,
      low_stock: 0,
      out_of_stock: 0
    })
  }
})
</script>

<style scoped>
.stats-row-dense {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.stats-card-dense {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 12px 32px rgba(15,23,42,0.04);
  transition: all 0.2s ease;
  height: 72px;
  box-sizing: border-box;
}
.stats-card-dense:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(15,23,42,0.08);
}
.stats-card-dense__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.stats-card-dense__icon.total { background: #eff6ff; color: #2563eb; }
.stats-card-dense__icon.success { background: #dcfce7; color: #16a34a; }
.stats-card-dense__icon.warning { background: #fef3c7; color: #d97706; }
.stats-card-dense__icon.danger { background: #fee2e2; color: #ef4444; }

.stats-card-dense__content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stats-card-dense__label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stats-card-dense__value {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}
.stats-card-dense__subtext {
  font-size: 10px;
  color: #94a3b8;
}
.stats-card-dense__sparkline {
  margin-left: auto;
  opacity: 0.6;
}
</style>
