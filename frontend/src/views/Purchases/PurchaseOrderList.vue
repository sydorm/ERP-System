<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Замовлення постачальникам</h2>
    </div>

    <div class="page-content">
      <AutoGrid
        ref="grid"
        :config="gridConfig"
        @create="goToCreate"
        @row-click="goToEdit"
      >
        <template #col-status="{ value }">
          <el-tag :type="getStatusType(value)">
            {{ getStatusLabel(value) }}
          </el-tag>
        </template>
      </AutoGrid>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AutoGrid from '@/components/common/AutoGrid.vue'

const router = useRouter()
const grid = ref(null)

const gridConfig = {
  endpoint: '/api/v1/purchase-orders',
  searchable: true,
  creatable: true,
  createLabel: 'Нове замовлення',
  showActions: true,
  columns: [
    { prop: 'order_number', label: 'Номер', width: '150', sortable: true },
    { prop: 'order_date', label: 'Дата', width: '150', type: 'date', sortable: true },
    { prop: 'expected_date', label: 'Очікується', width: '150', type: 'date', sortable: true },
    { prop: 'status', label: 'Статус', width: '150' },
    { prop: 'supplier_id', label: 'Постачальник', width: '250' },
    { prop: 'total_amount', label: 'Сума', width: '150', type: 'currency' }
  ]
}

const getStatusType = (status) => {
    switch (status) {
        case 'draft': return 'info'
        case 'confirmed': return 'primary'
        case 'done': return 'success'
        case 'cancelled': return 'danger'
        default: return 'info'
    }
}

const getStatusLabel = (status) => {
    switch (status) {
        case 'draft': return 'Чернетка'
        case 'confirmed': return 'Підтверджено'
        case 'done': return 'Виконано'
        case 'cancelled': return 'Скасовано'
        default: return status
    }
}

const goToCreate = () => {
  router.push('/purchases/orders/new')
}

const goToEdit = (row) => {
  router.push(`/purchases/orders/${row.id}`)
}
</script>

<style scoped>
.page-container {
  padding: 24px;
}
.page-header {
  margin-bottom: 24px;
}
</style>
