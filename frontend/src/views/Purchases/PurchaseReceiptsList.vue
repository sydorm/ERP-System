<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Прибуткові накладні</h2>
    </div>

    <div class="page-content">
      <AutoGrid
        ref="grid"
        :config="gridConfig"
        @create="goToCreate"
        @row-click="goToEdit"
      >
        <!-- Custom slot for status if needed -->
        <template #col-status="{ value }">
          <el-tag :type="value === 'posted' ? 'success' : 'info'">
            {{ value === 'posted' ? 'Проведено' : 'Чернетка' }}
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
  endpoint: '/api/v1/purchase-receipts',
  searchable: true,
  creatable: true,
  createLabel: 'Нова накладна',
  showActions: true,
  columns: [
    { prop: 'receipt_number', label: 'Номер', width: '150', sortable: true },
    { prop: 'receipt_date', label: 'Дата', width: '150', type: 'date', sortable: true },
    { prop: 'status', label: 'Статус', width: '120', type: 'status' },
    { prop: 'supplier_id', label: 'Постачальник', width: '250' }, // We'll need a way to show names later
    { prop: 'total_amount', label: 'Сума', width: '150', type: 'currency' }
  ]
}

const goToCreate = () => {
  router.push('/purchases/receipts/new')
}

const goToEdit = (row) => {
  router.push(`/purchases/receipts/${row.id}`)
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
