<template>
  <div class="kpi-force-row" style="display: flex; gap: 20px; width: 100%; margin-bottom: 8px;">
    <!-- Всього позицій -->
    <div class="kpi-card-force" style="flex: 1; background: white; padding: 12px 16px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center; min-height: 70px; border: 1px solid rgba(0,0,0,0.02);">
      <div class="kpi-header-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <div class="kpi-icon-box" style="width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; background-color: rgba(115, 103, 240, 0.12) !important; color: #7367f0 !important; border: 1px solid rgba(0,0,0,0.03);">
          <el-icon><User /></el-icon>
        </div>
        <div class="kpi-trend trend-up" style="font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: rgba(40, 199, 111, 0.12); color: #28c76f;">+12%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value" style="font-size: 20px; font-weight: 800; color: #444050; line-height: 1;">{{ stats.total_products }}</div>
        <div class="kpi-label" style="font-size: 11px; color: #8E8BA2; font-weight: 600; margin-top: 2px;">Всього позицій</div>
      </div>
    </div>

    <!-- Низький запас -->
    <div class="kpi-card-force" style="flex: 1; background: white; padding: 12px 16px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center; min-height: 70px; border: 1px solid rgba(0,0,0,0.02);">
      <div class="kpi-header-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <div class="kpi-icon-box" style="width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; background-color: rgba(255, 159, 67, 0.12) !important; color: #ff9f43 !important; border: 1px solid rgba(0,0,0,0.03);">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="kpi-trend trend-down" style="font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: rgba(234, 84, 85, 0.12); color: #ea5455;">-8%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value" style="font-size: 20px; font-weight: 800; color: #444050; line-height: 1;">{{ stats.low_stock }}</div>
        <div class="kpi-label" style="font-size: 11px; color: #8E8BA2; font-weight: 600; margin-top: 2px;">Низький запас</div>
      </div>
    </div>

    <!-- В наявності -->
    <div class="kpi-card-force" style="flex: 1; background: white; padding: 12px 16px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center; min-height: 70px; border: 1px solid rgba(0,0,0,0.02);">
      <div class="kpi-header-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <div class="kpi-icon-box" style="width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; background-color: rgba(40, 199, 111, 0.12) !important; color: #28c76f !important; border: 1px solid rgba(0,0,0,0.03);">
          <el-icon><Check /></el-icon>
        </div>
        <div class="kpi-trend trend-up" style="font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: rgba(40, 199, 111, 0.12); color: #28c76f;">+24%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value" style="font-size: 20px; font-weight: 800; color: #444050; line-height: 1;">{{ stats.in_stock }}</div>
        <div class="kpi-label" style="font-size: 11px; color: #8E8BA2; font-weight: 600; margin-top: 2px;">В наявності</div>
      </div>
    </div>

    <!-- Дефіцит -->
    <div class="kpi-card-force" style="flex: 1; background: white; padding: 12px 16px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center; min-height: 70px; border: 1px solid rgba(0,0,0,0.02);">
      <div class="kpi-header-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <div class="kpi-icon-box" style="width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; background-color: rgba(234, 84, 85, 0.12) !important; color: #ea5455 !important; border: 1px solid rgba(0,0,0,0.03);">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="kpi-trend trend-down" style="font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: rgba(234, 84, 85, 0.12); color: #ea5455;">-14%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value" style="font-size: 20px; font-weight: 800; color: #444050; line-height: 1;">{{ stats.out_of_stock }}</div>
        <div class="kpi-label" style="font-size: 11px; color: #8E8BA2; font-weight: 600; margin-top: 2px;">Дефіцит</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, Warning, Check, CircleClose } from '@element-plus/icons-vue'

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
/* Scoped styles kept for transitions or non-inline needs */
.kpi-card-force { transition: all 0.3s ease; }
.kpi-card-force:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important; }
</style>
