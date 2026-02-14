<template>
  <el-card shadow="never" class="tab-card">
    <div class="tab-header-tiny">
      <h3>Склад виробу</h3>
      <el-button type="primary" size="small" :icon="Plus">Додати матеріал</el-button>
    </div>
    
    <el-table :data="items" stripe style="width: 100%; margin-top: 15px">
      <el-table-column prop="sku" label="Артикул" width="120" />
      <el-table-column prop="name" label="Назва компонента" />
      <el-table-column prop="quantity" label="Кількість" width="120">
        <template #default="scope">
          <el-input-number v-model="scope.row.quantity" size="small" :min="0.0001" style="width: 100px" />
        </template>
      </el-table-column>
      <el-table-column prop="uom" label="Од." width="80" />
      <el-table-column prop="cost" label="Вартість" width="120" align="right">
        <template #default="scope">
          {{ formatCurrency(scope.row.quantity * scope.row.unitPrice, 'UAH') }}
        </template>
      </el-table-column>
      <el-table-column label="Дії" width="80" align="right">
        <template #default="scope">
          <el-button link type="danger" :icon="Delete" />
        </template>
      </el-table-column>
    </el-table>

    <div class="bom-footer">
      <div class="bom-total">
        Загальна собівартість матеріалів: <strong>{{ formatCurrency(totalCost, 'UAH') }}</strong>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { Plus, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  totalCost: {
    type: Number,
    default: 0
  }
})

const formatCurrency = (val, curr) => {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: curr || 'UAH' }).format(val)
}
</script>

<style scoped>
.tab-card {
  margin: 24px;
  border: 1px solid #eef0f2;
}

.tab-header-tiny {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bom-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eef0f2;
  text-align: right;
}

.bom-total {
  font-size: 16px;
}

.bom-total strong {
  color: #409eff;
}
</style>
