<template>
  <div class="kpi-grid-force">
    <!-- Всього позицій -->
    <div class="kpi-card-force">
      <div class="kpi-header-row">
        <div class="kpi-icon-box" style="background-color: rgba(115, 103, 240, 0.12) !important; color: #7367f0 !important;">
          <el-icon><User /></el-icon>
        </div>
        <div class="kpi-trend trend-up">+12%</div>
      </div>
      <div class="kpi-body">
        <div class="kpi-value">{{ stats.total_products }}</div>
        <div class="kpi-label">Всього позицій</div>
      </div>
    </div>

    <!-- Низький запас -->
    <div class="kpi-card-force">
      <div class="kpi-header-row">
        <div class="kpi-icon-box" style="background-color: rgba(255, 159, 67, 0.12) !important; color: #ff9f43 !important;">
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
    <div class="kpi-card-force">
      <div class="kpi-header-row">
        <div class="kpi-icon-box" style="background-color: rgba(40, 199, 111, 0.12) !important; color: #28c76f !important;">
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
    <div class="kpi-card-force">
      <div class="kpi-header-row">
        <div class="kpi-icon-box" style="background-color: rgba(234, 84, 85, 0.12) !important; color: #ea5455 !important;">
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
.kpi-grid-force {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.kpi-card-force {
  background: #ffffff !important;
  padding: 12px 18px !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 15px 0 rgba(15, 20, 34, 0.04) !important;
  border: 1px solid rgba(0, 0, 0, 0.02) !important;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 80px;
}

.kpi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.kpi-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.kpi-trend {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
}

.trend-up { background: rgba(40, 199, 111, 0.12); color: #28c76f; }
.trend-down { background: rgba(234, 84, 85, 0.12); color: #ea5455; }

.kpi-value {
  font-size: 22px;
  font-weight: 800;
  color: #444050;
  line-height: 1;
}

.kpi-label {
  font-size: 11px;
  color: #8E8BA2;
  font-weight: 600;
  margin-top: 2px;
}
</style>
