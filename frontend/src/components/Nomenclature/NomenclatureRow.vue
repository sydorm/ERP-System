<template>
  <div
    class="nom-row nom-body-row"
    :class="{ 'is-selected': isSelected }"
    @click="$emit('click', row)"
  >
    <!-- Checkbox -->
    <div class="nom-cell nom-cell--check" @click.stop>
      <input
        type="checkbox"
        :checked="isSelected"
        @change="$emit('toggle-selection', row)"
      />
    </div>

    <!-- Photo -->
    <div class="nom-cell nom-cell--photo" @click.stop>
      <el-image
        v-if="row.image_url"
        :src="row.image_url"
        class="nom-thumb"
        fit="cover"
      />
      <div v-else class="nom-thumb nom-thumb--icon">
        <el-icon v-if="row.category === 'MATERIAL'"><Grid /></el-icon>
        <el-icon v-else><Box /></el-icon>
      </div>
    </div>

    <!-- Name / SKU -->
    <div class="nom-cell nom-cell--name">
      <div class="nom-name-row">
        <div class="nom-name">{{ row.name }}</div>
        <NomenclatureAIBadge v-if="hasAiWarning(row)" :reason="getAiWarningReason(row)" />
      </div>
      <div class="nom-sku">{{ row.sku }}<span class="nom-dot"> · </span>{{ uomName }}</div>
    </div>

    <!-- Category -->
    <div class="nom-cell nom-cell--category">
      <span 
        class="nom-cat-badge" 
        :title="categoryName"
        :style="categoryStyle"
      >
        {{ categoryName || '—' }}
      </span>
    </div>

    <!-- Stock -->
    <div class="nom-cell nom-cell--stock">
      <div class="nom-stock-qty">{{ row.stock_balance }} {{ uomName }}</div>
      <div class="nom-prog-bar">
        <div
          class="nom-prog-fill"
          :class="stockBadgeClass"
          :style="{ width: stockProgressWidth }"
        ></div>
      </div>
    </div>

    <!-- Status -->
    <div class="nom-cell nom-cell--status">
      <span class="nom-status-badge" :class="stockBadgeClass">
        {{ stockBadgeText }}
      </span>
    </div>

    <!-- Price -->
    <div class="nom-cell nom-cell--price">
      <span class="nom-price" :class="{ 'nom-price--empty': !row.price }">
        {{ formattedPrice }}
      </span>
    </div>

    <!-- Actions -->
    <div class="nom-cell nom-cell--actions" @click.stop>
      <button class="nom-action-btn" @click.stop="$emit('edit', row)" title="Редагувати">
        <el-icon><Edit /></el-icon>
      </button>
      <el-dropdown trigger="click" @click.stop>
        <button class="nom-action-btn" title="Більше">
          <el-icon><More /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$emit('click', row)">
              <el-icon><View /></el-icon>&nbsp;Перегляд
            </el-dropdown-item>
            <el-dropdown-item @click="$emit('edit', row)">
              <el-icon><Edit /></el-icon>&nbsp;Редагувати
            </el-dropdown-item>
            <el-dropdown-item @click="$emit('duplicate', row)">
              <el-icon><Fold /></el-icon>&nbsp;Дублювати
            </el-dropdown-item>
            <el-dropdown-item @click="$emit('view-stock', row)">
              <el-icon><Box /></el-icon>&nbsp;Змінити залишок
            </el-dropdown-item>
            <el-dropdown-item @click="$emit('view-movement', row)">
              <el-icon><Coordinate /></el-icon>&nbsp;Рух товару
            </el-dropdown-item>
            <el-dropdown-item divided class="nom-delete-item" @click="$emit('delete', row)">
              <el-icon><CircleClose /></el-icon>&nbsp;Видалити
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Edit, Box, More, View, Fold, Coordinate, CircleClose, Grid } from '@element-plus/icons-vue'
import NomenclatureAIBadge from './NomenclatureAIBadge.vue'

const props = defineProps({
  row: { type: Object, required: true },
  isSelected: Boolean,
  uomName: String,
  categoryName: String,
  categoryStyle: Object,
  stockBadgeClass: String,
  stockBadgeText: String,
  formattedPrice: String
})

defineEmits(['click', 'toggle-selection', 'edit', 'duplicate', 'view-stock', 'view-movement', 'delete'])

const stockProgressWidth = computed(() => {
  const qty = props.row.stock_balance || 0
  const min = props.row.min_stock || 10
  return qty <= 0 ? '6%' : Math.min(100, (qty / min) * 100) + '%'
})

const hasAiWarning = (row) => {
  return row.stock_balance <= (row.min_stock || 0) || !row.price
}

const getAiWarningReason = (row) => {
  if (row.stock_balance <= 0) return 'Критичний дефіцит'
  if (row.stock_balance <= (row.min_stock || 5)) return 'Залишок закінчується'
  if (!row.price) return 'Відсутня ціна'
  return 'Потребує уваги'
}
</script>

<style scoped>
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

.nom-body-row {
  height: 72px;
  border-bottom: 1px solid #eef2f7;
  cursor: pointer;
  transition: background 0.14s ease;
  background: #ffffff;
}
.nom-body-row:last-child {
  border-bottom: none;
}
.nom-body-row:hover {
  background: #fafbff;
}
.nom-body-row.is-selected {
  background: #f0f4ff;
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
  accent-color: #635bff;
}

.nom-cell--photo {
  justify-content: center;
  padding: 0;
}
.nom-thumb {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-shrink: 0;
}
.nom-thumb--icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 16px;
}

.nom-cell--name {
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 3px;
  padding-right: 12px;
}
.nom-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}
.nom-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nom-sku {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}
.nom-dot {
  margin: 0 2px;
}

.nom-cell--category {
  padding-right: 12px;
}
.nom-cat-badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
  border: 1px solid transparent;
}

.nom-cell--stock {
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 5px;
}
.nom-stock-qty {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
}
.nom-prog-bar {
  width: 100px;
  height: 5px;
  background: #eef2f7;
  border-radius: 3px;
  overflow: hidden;
}
.nom-prog-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.nom-prog-fill.success { background: #22c55e; }
.nom-prog-fill.warning { background: #f59e0b; }
.nom-prog-fill.danger  { background: #f43f5e; }

.nom-cell--status {
  justify-content: flex-start;
}
.nom-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  line-height: 1;
}
.nom-status-badge.success { background: #dcfce7; color: #16a34a; }
.nom-status-badge.warning { background: #fef3c7; color: #d97706; }
.nom-status-badge.danger  { background: #fee2e2; color: #ef4444; }

.nom-cell--price {
  justify-content: flex-end;
  padding-right: 16px;
}
.nom-price {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
}
.nom-price--empty {
  color: #94a3b8;
}

.nom-cell--actions {
  justify-content: flex-end;
  gap: 4px;
  padding-right: 12px;
  padding-left: 0;
}
.nom-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: 1px solid transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.nom-action-btn:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #4f46e5;
}

.nom-delete-item {
  color: #ef4444 !important;
}
</style>
