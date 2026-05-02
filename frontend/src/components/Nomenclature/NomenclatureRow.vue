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
    <div class="nom-cell nom-cell--photo" @click.stop v-if="false">
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
      <div class="status-badge-premium" :class="stockBadgeClass">
        <el-icon v-if="stockBadgeClass === 'danger'" :size="14"><CircleClose /></el-icon>
        <el-icon v-else-if="stockBadgeClass === 'success'" :size="14"><CircleCheck /></el-icon>
        <el-icon v-else :size="14"><Warning /></el-icon>
        <span>{{ stockBadgeText }}</span>
      </div>
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
import { Edit, Box, More, View, Fold, Coordinate, CircleClose, Grid, CircleCheck, Warning } from '@element-plus/icons-vue'
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
    32px    /* checkbox */
    minmax(280px, 2.5fr) /* name */
    180px   /* category */
    170px   /* stock */
    150px   /* status */
    120px   /* price */
    96px;   /* actions */
  align-items: center;
  min-width: 900px;
}

.nom-body-row {
  height: auto; /* Allow padding to define height */
  border-bottom: 1px solid #F1F5F9;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #ffffff;
}
.nom-body-row:last-child {
  border-bottom: none;
}
.nom-body-row:hover {
  background: #F8F9FC;
}
.nom-body-row:hover .nom-action-btn {
  opacity: 1;
}
.nom-body-row.is-selected {
  background: #F0F5FF;
}

.nom-cell {
  padding: 6px 12px; /* Standardized as per request */
  overflow: hidden;
  display: flex;
  align-items: center;
}

.nom-cell--check {
  justify-content: center;
  padding: 0;
}
.nom-cell--check input[type="checkbox"] {
  width: 12px;
  height: 12px;
  cursor: pointer;
  accent-color: #1463FF;
}

.nom-cell--photo {
  justify-content: center;
  padding: 0;
}
.nom-thumb {
  width: 32px; /* Reduced from 40px */
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  flex-shrink: 0;
}
.nom-thumb--icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  font-size: 16px;
}

.nom-cell--name {
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0; /* Reduced gap */
  padding-right: 8px;
}
.nom-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}
.nom-name {
  font-size: 14px;
  font-weight: 700;
  color: #444050;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nom-sku {
  font-size: 11px;
  font-weight: 600;
  color: #94A3B8;
  margin-top: 2px;
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
  padding: 3px 8px; /* Reduced padding */
  font-size: 10px; /* Reduced from 11px */
  font-weight: 700;
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
  gap: 3px;
}
.nom-stock-qty {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 400;
  color: #0F172A;
  white-space: nowrap;
}
.nom-prog-bar {
  width: 80px;
  height: 4px;
  background: #F1F5F9;
  border-radius: 2px;
  overflow: hidden;
}
.nom-prog-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.nom-prog-fill.success { background: #15B97A; }
.nom-prog-fill.warning { background: #F59E0B; }
.nom-prog-fill.danger  { background: #F04452; }

.nom-cell--status {
  justify-content: flex-start;
}
.status-badge-premium {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}
.status-badge-premium.danger {
  color: #EF4444;
  background: #FEF2F2;
}
.status-badge-premium.success {
  color: #16A34A;
  background: #F0FDF4;
}
.status-badge-premium.warning {
  color: #D97706;
  background: #FFF7ED;
}

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
  width: 28px;
  height: 28px;
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
  font-size: 13px;
  opacity: 0;
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
