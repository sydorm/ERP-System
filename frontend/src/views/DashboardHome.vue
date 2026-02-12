<template>
  <div class="dashboard-home">
    <el-row :gutter="20">
      <!-- Statistics Cards -->
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="30"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-title">Замовлення</div>
              <div class="stat-value">24</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="30"><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-title">Дохід</div>
              <div class="stat-value">₴45,230</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="30"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-title">Товарів на складі</div>
              <div class="stat-value">156</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-title">Контрагенти</div>
              <div class="stat-value">48</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Продажі за тиждень</span>
            </div>
          </template>
          <div class="chart-placeholder">
            📊 Графік продажів (інтеграція з ECharts буде додана пізніше)
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Останні замовлення</span>
            </div>
          </template>
          <el-table :data="recentOrders" style="width: 100%" size="small">
            <el-table-column prop="number" label="№" width="100" />
            <el-table-column prop="customer" label="Клієнт" />
            <el-table-column prop="amount" label="Сума" width="120" />
            <el-table-column prop="status" label="Статус" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quick Actions -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Швидкі дії</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" :icon="Plus">Нове замовлення</el-button>
            <el-button type="success" :icon="DocumentAdd">Прибуткова накладна</el-button>
            <el-button type="warning" :icon="User">Новий контрагент</el-button>
            <el-button type="info" :icon="Box">Новий товар</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ShoppingCart, Wallet, Box, User, Plus, DocumentAdd } from '@element-plus/icons-vue'

const recentOrders = reactive([
  { number: 'ORD-001', customer: 'ТОВ "Компанія 1"', amount: '₴2,500', status: 'Нове' },
  { number: 'ORD-002', customer: 'ФОП Іваненко', amount: '₴1,200', status: 'В роботі' },
  { number: 'ORD-003', customer: 'ТОВ "Партнер"', amount: '₴3,800', status: 'Виконано' },
  { number: 'ORD-004', customer: 'ПП "Сервіс"', amount: '₴950', status: 'Нове' }
])

const getStatusType = (status) => {
  const types = {
    'Нове': 'info',
    'В роботі': 'warning',
    'Виконано': 'success',
    'Скасовано': 'danger'
  }
  return types[status] || 'info'
}
</script>

<style scoped>
.dashboard-home {
  width: 100%;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
