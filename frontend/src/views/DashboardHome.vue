<template>
  <div class="dashboard-home">
    <div class="kimi-stats-row mb-6">
      <!-- Statistics Cards -->
      <div class="kimi-stat-card kimi-stat-blue">
        <div class="kimi-stat-info">
          <p class="kimi-stat-label">Замовлення</p>
          <p class="kimi-stat-value text-blue-600">24</p>
        </div>
        <div class="kimi-stat-icon-wrapper bg-blue-100 text-blue-600">
          <el-icon><ShoppingCart /></el-icon>
        </div>
      </div>

      <div class="kimi-stat-card kimi-stat-emerald">
        <div class="kimi-stat-info">
          <p class="kimi-stat-label">Дохід</p>
          <p class="kimi-stat-value text-emerald-600">₴45,230</p>
        </div>
        <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
          <el-icon><Wallet /></el-icon>
        </div>
      </div>

      <div class="kimi-stat-card kimi-stat-amber">
        <div class="kimi-stat-info">
          <p class="kimi-stat-label">Товарів на складі</p>
          <p class="kimi-stat-value text-amber-600">156</p>
        </div>
        <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
          <el-icon><Box /></el-icon>
        </div>
      </div>

      <div class="kimi-stat-card kimi-stat-rose">
        <div class="kimi-stat-info">
          <p class="kimi-stat-label">Контрагенти</p>
          <p class="kimi-stat-value text-rose-600">48</p>
        </div>
        <div class="kimi-stat-icon-wrapper bg-rose-100 text-rose-600">
          <el-icon><User /></el-icon>
        </div>
      </div>
    </div>

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
  width: 100%; padding: 20px;
}

.text-blue-600 { color: #2563eb; }
.text-emerald-600 { color: #059669; }
.text-amber-600 { color: #d97706; }
.text-rose-600 { color: #e11d48; }

.bg-blue-100 { background: #dbeafe; }
.bg-emerald-100 { background: #d1fae5; }
.bg-amber-100 { background: #fef3c7; }
.bg-rose-100 { background: #ffe4e6; }

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
