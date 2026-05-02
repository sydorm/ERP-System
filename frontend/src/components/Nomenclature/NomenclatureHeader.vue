<template>
  <div class="kpi-grid-modern">
    <!-- Всього позицій -->
    <div class="kpi-card-modern">
      <div class="kpi-header-row">
        <div class="kpi-icon-wrapper" style="background-color: rgba(115, 103, 240, 0.1); color: #7367f0;">
          <el-icon><Box /></el-icon>
        </div>
        <div class="kpi-trend trend-up">+12%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stats.total_products }}</div>
        <div class="kpi-label">Всього позицій</div>
      </div>
    </div>

    <!-- Низький запас -->
    <div class="kpi-card-modern">
      <div class="kpi-header-row">
        <div class="kpi-icon-wrapper" style="background-color: rgba(255, 159, 67, 0.1); color: #ff9f43;">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="kpi-trend trend-down">-8%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stats.low_stock }}</div>
        <div class="kpi-label">Низький запас</div>
      </div>
    </div>

    <!-- В наявності -->
    <div class="kpi-card-modern">
      <div class="kpi-header-row">
        <div class="kpi-icon-wrapper" style="background-color: rgba(40, 199, 111, 0.1); color: #28c76f;">
          <el-icon><Check /></el-icon>
        </div>
        <div class="kpi-trend trend-up">+24%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stats.in_stock }}</div>
        <div class="kpi-label">В наявності</div>
      </div>
    </div>

    <!-- Дефіцит -->
    <div class="kpi-card-modern">
      <div class="kpi-header-row">
        <div class="kpi-icon-wrapper" style="background-color: rgba(234, 84, 85, 0.1); color: #ea5455;">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="kpi-trend trend-down">-14%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stats.out_of_stock }}</div>
        <div class="kpi-label">Дефіцит</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Box, Warning, Check, CircleClose } from '@element-plus/icons-vue'

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
.kpi-grid-modern {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.kpi-card-modern {
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: 0 4px 20px 0 rgba(15, 20, 34, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
}

.kpi-card-modern:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px 0 rgba(15, 20, 34, 0.1);
}

.kpi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.kpi-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.kpi-trend {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
}

.trend-up { background: rgba(40, 199, 111, 0.12); color: #28c76f; }
.trend-down { background: rgba(234, 84, 85, 0.12); color: #ea5455; }

.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: #444050;
  line-height: 1.2;
}

.kpi-label {
  font-size: 12px;
  color: #8E8BA2;
  font-weight: 600;
  margin-top: 2px;
}
</style>
