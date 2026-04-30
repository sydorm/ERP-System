<template>
  <div class="table-section" v-loading="loading">
    <!-- Grid Table -->
    <div class="nom-table">
      <!-- HEADER ROW -->
      <div class="nom-row nom-header">
        <div class="nom-cell nom-cell--check">
          <input 
            type="checkbox" 
            :checked="isAllSelected" 
            @change="$emit('toggle-all', $event.target.checked)" 
          />
        </div>
        <div class="nom-cell nom-cell--photo"></div>
        <div class="nom-cell nom-cell--name">Назва / Артикул</div>
        <div class="nom-cell nom-cell--category">Категорія</div>
        <div class="nom-cell nom-cell--stock">Залишок</div>
        <div class="nom-cell nom-cell--status">Статус</div>
        <div class="nom-cell nom-cell--price">Ціна</div>
        <div class="nom-cell nom-cell--actions"></div>
      </div>

      <!-- BODY ROWS -->
      <NomenclatureRow
        v-for="row in products"
        :key="row.id"
        :row="row"
        :is-selected="selectedRows.some(r => r.id === row.id)"
        :uom-name="getUomName(row.unit_of_measure)"
        :category-name="getCategoryName(row.category)"
        :category-style="getCategoryBadgeStyle(row.category)"
        :stock-badge-class="getStockBadgeClass(row.stock_balance, row.min_stock)"
        :stock-badge-text="getStockBadgeText(row.stock_balance, row.min_stock)"
        :formatted-price="formatCurrency(row.price, row.currency)"
        @click="$emit('row-click', $event)"
        @toggle-selection="$emit('toggle-selection', $event)"
        @edit="$emit('edit', $event)"
        @duplicate="$emit('duplicate', $event)"
        @view-stock="$emit('view-stock', $event)"
        @view-movement="$emit('view-movement', $event)"
        @delete="$emit('delete', $event)"
      />

      <!-- Empty State -->
      <div v-if="!loading && products.length === 0" class="nom-empty">
        <div class="nom-empty-icon">📦</div>
        <div class="nom-empty-text">Номенклатуру не знайдено</div>
        <div class="nom-empty-sub">Спробуйте змінити фільтри або створіть нову позицію</div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-dense">
      <el-select 
        :model-value="limit" 
        size="small" 
        style="width: 70px;" 
        @change="$emit('update:limit', $event)"
      >
        <el-option v-for="size in [10, 20, 50, 100]" :key="size" :label="size" :value="size" />
      </el-select>
      <el-pagination
        :current-page="currentPage"
        :page-size="limit"
        :total="total"
        background
        layout="prev, pager, next"
        @update:current-page="$emit('update:currentPage', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NomenclatureRow from './NomenclatureRow.vue'

const props = defineProps({
  products: { type: Array, default: () => [] },
  loading: Boolean,
  selectedRows: { type: Array, default: () => [] },
  currentPage: Number,
  limit: Number,
  total: Number,
  getUomName: Function,
  getCategoryName: Function,
  getCategoryBadgeStyle: Function,
  getStockBadgeClass: Function,
  getStockBadgeText: Function,
  formatCurrency: Function
})

const emit = defineEmits([
  'update:currentPage', 
  'update:limit', 
  'update:selectedRows',
  'row-click',
  'toggle-selection',
  'toggle-all',
  'edit',
  'duplicate',
  'view-stock',
  'view-movement',
  'delete'
])

const isAllSelected = computed(() => {
  return props.products.length > 0 && props.selectedRows.length === props.products.length
})
</script>

<style scoped>
.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.6);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  margin: 16px 24px 24px;
  overflow: hidden;
}

.nom-table {
  flex: 1;
  width: 100%;
  overflow-x: auto;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.nom-row {
  display: grid;
  grid-template-columns:
    44px    /* checkbox */
    64px    /* photo */
    minmax(240px, 2.2fr) /* name */
    180px   /* category */
    170px   /* stock */
    150px   /* status */
    120px   /* price */
    96px;   /* actions */
  align-items: center;
  min-width: 900px;
}

.nom-header {
  background: #F8F9FC;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  height: 42px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nom-header .nom-cell {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94A3B8;
  padding: 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nom-cell {
  padding: 0 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.nom-cell--check {
  justify-content: center;
  padding: 0;
}
.nom-cell--check input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #1463FF;
}

.nom-empty {
  padding: 60px 24px;
  text-align: center;
}
.nom-empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}
.nom-empty-text {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}
.nom-empty-sub {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 4px;
}

.pagination-dense {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid #eef2f7;
}
</style>
