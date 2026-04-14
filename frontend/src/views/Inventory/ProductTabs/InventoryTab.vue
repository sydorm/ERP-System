<template>
  <div class="inventory-tab">
    <div class="inventory-header">
       <div class="header-info">
          <h3>Складські залишки</h3>
          <p>Поточна наявність товару на всіх складах підприємства</p>
       </div>
       <div class="header-stats" v-if="stockLevels.length > 0">
          <div class="stat-item">
             <span class="stat-label">Всього на складах</span>
             <span class="stat-value">{{ totalStock }}</span>
          </div>
       </div>
    </div>

    <div v-if="stockLevels.length === 0" class="empty-inventory">
       <el-empty description="Товар відсутній на складах">
          <template #extra>
             <p class="text-xs text-gray-400">Спробуйте створити Закупівлю або Виробництво для поповнення залишків.</p>
          </template>
       </el-empty>
    </div>

    <el-table v-else :data="stockLevels" class="stock-table" border stripe>
      <el-table-column prop="warehouse" label="Склад">
        <template #default="scope">
           <div class="warehouse-cell">
              <el-icon class="mr-2"><OfficeBuilding /></el-icon>
              <span>{{ scope.row.warehouse }}</span>
           </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="quantity" label="Наявність" width="160" align="right">
        <template #default="scope">
          <span class="qty-value" :class="scope.row.quantity <= 0 ? 'text-rose-500' : 'text-slate-700'">
            {{ formatQty(scope.row.quantity) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="reserved" label="Резерв" width="160" align="right">
        <template #default="scope">
          <span class="qty-reserved text-amber-500">
            {{ formatQty(scope.row.reserved) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="available" label="Доступно" width="160" align="right">
        <template #default="scope">
          <el-tag :type="scope.row.available <= 0 ? 'danger' : 'success'" effect="dark" class="qty-available">
            {{ formatQty(scope.row.available) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Мін. поріг" width="180" align="center">
        <template #default="scope">
          <div class="flex items-center justify-center gap-2">
             <el-input-number v-model="scope.row.minLevel" :min="0" size="small" controls-position="right" class="min-level-input" />
             <el-tooltip content="Система повідомить, коли залишок опуститься нижче цього рівня">
                <el-icon class="text-gray-300"><InfoFilled /></el-icon>
             </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="inventory-footer mt-6" v-if="stockLevels.length > 0">
       <el-alert
         title="Управління запасами"
         type="info"
         description="Резерв формується на основі активних Замовлень Покупців. Доступна кількість = Наявність - Резерв."
         show-icon
         :closable="false"
       />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { OfficeBuilding, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  stockLevels: {
    type: Array,
    default: () => []
  }
})

const totalStock = computed(() => {
  return props.stockLevels.reduce((sum, item) => sum + (parseFloat(item.quantity) || 0), 0).toFixed(2)
})

const formatQty = (val) => {
  if (val == null) return "0.00"
  return parseFloat(val).toFixed(2)
}
</script>

<style scoped>
.inventory-tab {
  padding: 32px;
  background: #fff;
}

.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.header-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.header-info p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.stat-item {
  text-align: right;
  background: #f8fafc;
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.stat-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 800;
  color: #4f46e5;
}

.stock-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0 !important;
}

.warehouse-cell {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #334155;
}

.qty-value {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.qty-reserved {
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.qty-available {
  font-weight: 700;
  min-width: 80px;
  justify-content: center;
}

.min-level-input {
  width: 90px;
}

.empty-inventory {
  padding: 60px 0;
  background: #fcfdfe;
  border-radius: 16px;
  border: 2px dashed #e2e8f0;
}

.mr-2 { margin-right: 0.5rem; }
.mt-6 { margin-top: 1.5rem; }
.text-xs { font-size: 12px; }
.text-gray-400 { color: #94a3b8; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.gap-2 { gap: 0.5rem; }
</style>
