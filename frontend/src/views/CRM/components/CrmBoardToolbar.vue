<template>
  <div class="crm-header-right">
    <el-select
      v-model="filters.managerScope"
      class="manager-scope-select"
      placeholder="Менеджер"
    >
      <el-option label="Мої заявки" value="mine" />
      <el-option label="Усі заявки" value="all" />
      <el-option
        v-for="u in users"
        :key="u.id"
        :label="u.name"
        :value="`manager:${u.id}`"
      />
    </el-select>

    <div class="crm-view-switch">
      <button class="view-btn active">Kanban</button>
      <button class="view-btn" @click="$emit('analytics')">Аналітика</button>
    </div>

    <el-input
      :model-value="searchQuery"
      placeholder="Пошук клієнта, тел, виробу..."
      class="crm-search-input"
      clearable
      :prefix-icon="Search"
      @update:model-value="$emit('update:searchQuery', $event)"
    />

    <button
      v-if="isAnyFilterActive"
      class="crm-reset-all-btn"
      @click="$emit('resetAll')"
    >
      × Скинути все
    </button>

    <el-popover placement="bottom-end" :width="300" trigger="click">
      <template #reference>
        <button class="crm-filter-btn">
          <el-icon><Operation /></el-icon> Фільтри
          <el-badge v-if="activeControlsCount" :value="activeControlsCount" class="filter-badge" />
        </button>
      </template>
      <div class="filter-popover-content">
        <div class="filter-section">
          <label>Сортування</label>
          <el-select :model-value="sortOption" placeholder="Сортувати" @update:model-value="$emit('update:sortOption', $event)">
            <el-option label="За датою (нові)" value="created_desc" />
            <el-option label="За дедлайном" value="deadline_asc" />
            <el-option label="За сумою (спадання)" value="amount_desc" />
            <el-option label="За пріоритетом" value="priority_desc" />
          </el-select>
        </div>
        <div class="filter-section">
          <label>Пріоритет</label>
          <el-select v-model="filters.priority" placeholder="Всі" clearable>
            <el-option label="Терміново" value="critical" />
            <el-option label="Високий" value="urgent" />
            <el-option label="Середній" value="normal" />
            <el-option label="Низький" value="low" />
          </el-select>
        </div>
        <div class="filter-section">
          <label>Статус оплати</label>
          <el-select v-model="filters.payment" placeholder="Всі" clearable>
            <el-option label="Не оплачено" value="unpaid" />
            <el-option label="Часткова" value="partial" />
            <el-option label="Оплачено" value="paid" />
          </el-select>
        </div>
        <div class="filter-section">
          <label>Менеджер</label>
          <el-select v-model="filters.managerScope" placeholder="Всі">
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
        <div class="filter-section">
          <el-checkbox v-model="filters.attentionOnly">Тільки потребують уваги</el-checkbox>
        </div>
        <div class="filter-section">
          <label>Дедлайн</label>
          <el-select v-model="filters.deadline" placeholder="Всі" clearable>
            <el-option label="Прострочені" value="overdue" />
            <el-option label="Сьогодні" value="today" />
            <el-option label="Цього тижня" value="this_week" />
          </el-select>
        </div>
        <div class="filter-footer">
          <el-button @click="$emit('resetFilters')" size="small">Скинути</el-button>
          <el-button type="primary" size="small" @click="$emit('applyFilters')">Застосувати</el-button>
        </div>
      </div>
    </el-popover>

    <el-dropdown trigger="click" @command="$emit('export', $event)">
      <button class="crm-export-btn">
        <el-icon><Download /></el-icon> Експорт
      </button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="excel">Excel (.csv)</el-dropdown-item>
          <el-dropdown-item command="pdf" disabled>PDF (скоро)</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <button class="crm-new-btn-indigo" @click="$emit('newOrder')">
      <el-icon><Plus /></el-icon> Нове замовлення
    </button>
  </div>
</template>

<script setup>
import { Search, Plus, Operation, Download } from '@element-plus/icons-vue'

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
</script>
