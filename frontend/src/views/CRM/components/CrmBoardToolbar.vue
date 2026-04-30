<template>
  <div class="crm-toolbar">

    <!-- Zone 1: Search -->
    <el-input
      :model-value="searchQuery"
      placeholder="Пошук клієнта, тел, виробу..."
      class="crm-search"
      clearable
      :prefix-icon="Search"
      @update:model-value="$emit('update:searchQuery', $event)"
    />

    <!-- Zone 2: Secondary controls grouped in one popover -->
    <el-popover
      v-model:visible="controlsOpen"
      placement="bottom-end"
      :width="320"
      trigger="click"
      popper-class="crm-controls-popper"
    >
      <template #reference>
        <button class="crm-ctrl-btn" :class="{ active: activeControlsCount > 0 }">
          <el-icon><Setting /></el-icon>
          <span>Параметри</span>
          <span v-if="activeControlsCount" class="ctrl-badge">{{ activeControlsCount }}</span>
          <el-icon class="ctrl-chevron" :class="{ rotated: controlsOpen }"><ArrowDown /></el-icon>
        </button>
      </template>

      <div class="ctrl-panel">
        <!-- View switch -->
        <div class="ctrl-section">
          <span class="ctrl-label">Вигляд</span>
          <div class="ctrl-view-tabs">
            <button class="view-tab active">
              <el-icon><Grid /></el-icon> Kanban
            </button>
            <button class="view-tab" @click="$emit('analytics'); controlsOpen = false">
              <el-icon><TrendCharts /></el-icon> Аналітика
            </button>
          </div>
        </div>

        <!-- Manager scope -->
        <div class="ctrl-section">
          <span class="ctrl-label">Менеджер</span>
          <el-select v-model="filters.managerScope" placeholder="Всі заявки" size="small">
            <el-option label="Мої заявки" value="mine" />
            <el-option label="Усі заявки" value="all" />
            <el-option
              v-for="u in users"
              :key="u.id"
              :label="u.name"
              :value="`manager:${u.id}`"
            />
          </el-select>
        </div>

        <!-- Sort -->
        <div class="ctrl-section">
          <span class="ctrl-label">Сортування</span>
          <el-select
            :model-value="sortOption"
            size="small"
            @update:model-value="$emit('update:sortOption', $event)"
          >
            <el-option label="За датою (нові)" value="created_desc" />
            <el-option label="За дедлайном" value="deadline_asc" />
            <el-option label="За сумою (спадання)" value="amount_desc" />
            <el-option label="За пріоритетом" value="priority_desc" />
          </el-select>
        </div>

        <div class="ctrl-divider" />

        <!-- Filters -->
        <div class="ctrl-section">
          <span class="ctrl-label">Пріоритет</span>
          <el-select v-model="filters.priority" placeholder="Всі" clearable size="small">
            <el-option label="Терміново" value="critical" />
            <el-option label="Високий" value="urgent" />
            <el-option label="Середній" value="normal" />
            <el-option label="Низький" value="low" />
          </el-select>
        </div>
        <div class="ctrl-section">
          <span class="ctrl-label">Статус оплати</span>
          <el-select v-model="filters.payment" placeholder="Всі" clearable size="small">
            <el-option label="Не оплачено" value="unpaid" />
            <el-option label="Часткова" value="partial" />
            <el-option label="Оплачено" value="paid" />
          </el-select>
        </div>
        <div class="ctrl-section">
          <span class="ctrl-label">Дедлайн</span>
          <el-select v-model="filters.deadline" placeholder="Всі" clearable size="small">
            <el-option label="Прострочені" value="overdue" />
            <el-option label="Сьогодні" value="today" />
            <el-option label="Цього тижня" value="this_week" />
          </el-select>
        </div>
        <div class="ctrl-section ctrl-section--row">
          <el-checkbox v-model="filters.attentionOnly">Тільки потребують уваги</el-checkbox>
        </div>

        <div class="ctrl-divider" />

        <!-- Footer actions -->
        <div class="ctrl-footer">
          <el-dropdown trigger="click" @command="$emit('export', $event)">
            <button class="ctrl-footer-btn">
              <el-icon><Download /></el-icon> Експорт
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="excel">Excel (.csv)</el-dropdown-item>
                <el-dropdown-item command="pdf" disabled>PDF (скоро)</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <div class="ctrl-footer-actions">
            <button
              v-if="isAnyFilterActive"
              class="ctrl-footer-btn ctrl-footer-btn--ghost"
              @click="$emit('resetAll'); controlsOpen = false"
            >
              × Скинути все
            </button>
            <button
              class="ctrl-footer-btn ctrl-footer-btn--primary"
              @click="$emit('applyFilters'); controlsOpen = false"
            >
              Застосувати
            </button>
          </div>
        </div>
      </div>
    </el-popover>

    <!-- Zone 3: Primary CTA -->
    <button class="crm-new-btn" @click="$emit('newOrder')">
      <el-icon><Plus /></el-icon>
      <span>Нове замовлення</span>
    </button>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, Plus, Setting, Download, ArrowDown, Grid, TrendCharts } from '@element-plus/icons-vue'

defineProps({
  users: { type: Array, default: () => [] },
  filters: { type: Object, required: true },
  searchQuery: { type: String, default: '' },
  sortOption: { type: String, default: 'created_desc' },
  activeControlsCount: { type: Number, default: 0 },
  isAnyFilterActive: { type: Boolean, default: false }
})

defineEmits([
  'update:searchQuery',
  'update:sortOption',
  'analytics',
  'resetAll',
  'resetFilters',
  'applyFilters',
  'export',
  'newOrder'
])

const controlsOpen = ref(false)
</script>

<style scoped>
/* ── Toolbar shell ─────────────────────────────────────────── */
.crm-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ── Search ────────────────────────────────────────────────── */
.crm-search {
  flex: 1;
  min-width: 180px;
  max-width: 340px;
}
.crm-search :deep(.el-input__wrapper) {
  height: 38px;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(20,99,255,0.06);
  border: 1px solid var(--erp-border, #E6ECF3);
  transition: box-shadow 0.2s;
}
.crm-search :deep(.el-input__wrapper):hover,
.crm-search :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(21, 185, 122, 0.12);
  border-color: var(--erp-status-success, #15B97A);
}

/* ── Parameters button ─────────────────────────────────────── */
.crm-ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 14px;
  border: 1px solid rgba(21, 185, 122, 0.25);
  border-radius: 10px;
  background: #fff;
  color: var(--erp-text-main, #1a2233);
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
  box-shadow: 0 1px 4px rgba(21, 185, 122, 0.08);
}
.crm-ctrl-btn:hover {
  border-color: var(--erp-status-success, #15B97A);
  box-shadow: 0 0 0 3px rgba(21, 185, 122, 0.1);
  color: var(--erp-status-success, #15B97A);
}
.crm-ctrl-btn.active {
  border-color: var(--erp-status-success, #15B97A);
  background: rgba(21, 185, 122, 0.05);
  color: var(--erp-status-success, #15B97A);
}

.ctrl-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--erp-status-success, #15B97A);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

.ctrl-chevron {
  font-size: 11px;
  transition: transform 0.2s;
  opacity: 0.6;
}
.ctrl-chevron.rotated {
  transform: rotate(180deg);
}

/* ── Primary CTA ────────────────────────────────────────────── */
.crm-new-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 38px;
  padding: 0 18px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #15B97A 0%, #34D399 100%);
  color: #fff;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 4px 14px rgba(21, 185, 122, 0.30);
  transition: all 0.18s;
}
.crm-new-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(21, 185, 122, 0.40);
  background: linear-gradient(135deg, #12A46C 0%, #15B97A 100%);
}
.crm-new-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(21, 185, 122, 0.25);
}
</style>

<!-- Popper styles must be global (teleported outside scoped component) -->
<style>
.crm-controls-popper {
  padding: 0 !important;
  border-radius: 14px !important;
  border: 1px solid var(--erp-border, #E6ECF3) !important;
  box-shadow: 0 8px 32px rgba(20,40,80,0.13) !important;
  overflow: hidden;
}
.crm-controls-popper .el-popper__arrow { display: none; }

.ctrl-panel {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ctrl-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.ctrl-section--row {
  flex-direction: row;
  align-items: center;
}

.ctrl-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #8a96a8;
}

.ctrl-section .el-select { width: 100%; }

.ctrl-view-tabs {
  display: flex;
  gap: 6px;
}
.view-tab {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--erp-border, #E6ECF3);
  background: #fff;
  font-size: 12.5px;
  font-weight: 500;
  color: #5a6478;
  cursor: pointer;
  transition: all 0.15s;
}
.view-tab:hover {
  border-color: var(--erp-primary, #1463FF);
  color: var(--erp-primary, #1463FF);
}
.view-tab.active {
  background: var(--erp-primary, #1463FF);
  border-color: var(--erp-primary, #1463FF);
  color: #fff;
}

.ctrl-divider {
  height: 1px;
  background: var(--erp-border, #E6ECF3);
  margin: 2px 0;
}

.ctrl-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 2px;
}
.ctrl-footer-actions {
  display: flex;
  gap: 6px;
}

.ctrl-footer-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 12px;
  border-radius: 7px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--erp-border, #E6ECF3);
  background: #fff;
  color: #5a6478;
  transition: all 0.15s;
}
.ctrl-footer-btn:hover {
  border-color: #b0bec5;
  color: #2d3a4a;
}
.ctrl-footer-btn--ghost {
  color: #e53935;
  border-color: #fce8e6;
  background: #fff5f5;
}
.ctrl-footer-btn--ghost:hover {
  background: #ffebee;
}
.ctrl-footer-btn--primary {
  background: linear-gradient(135deg, #1463FF 0%, #3b82f6 100%);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 2px 8px rgba(20,99,255,0.22);
}
.ctrl-footer-btn--primary:hover {
  box-shadow: 0 4px 14px rgba(20,99,255,0.32);
  transform: translateY(-1px);
}
</style>
