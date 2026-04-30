<template>
  <div class="toolbar-section">
    <!-- ===== ACTION BUTTONS ROW (under KPI) ===== -->
    <div class="action-row">
      <div class="action-row__left">
        <!-- Quick Filter Tabs -->
        <div class="quick-tabs-premium">
          <div
            class="quick-tab-item"
            :class="{ active: activeTab === 'all' }"
            @click="$emit('update:activeTab', 'all')"
          >Усі</div>
          <div
            class="quick-tab-item"
            :class="{ active: activeTab === 'materials' }"
            @click="$emit('update:activeTab', 'materials')"
          >Матеріали</div>
          <div
            class="quick-tab-item"
            :class="{ active: activeTab === 'products' }"
            @click="$emit('update:activeTab', 'products')"
          >Готові вироби</div>
        </div>
      </div>
      <div class="action-row__right">
        <button class="act-btn act-btn--secondary" @click="$emit('import')">
          📥 Імпорт
        </button>
        <button class="act-btn act-btn--secondary" @click="$emit('export')">
          📤 Експорт
        </button>
        <button class="act-btn act-btn--primary" @click="$emit('create')">
          <el-icon><Plus /></el-icon> Створити товар
        </button>
      </div>
    </div>

    <!-- ===== FILTERS TOOLBAR ===== -->
    <div class="toolbar-dense">
      <div class="toolbar-dense__left">
        <div class="search-dense-wrapper">
          <el-icon class="search-dense-icon"><Search /></el-icon>
          <input
            :value="searchQuery"
            placeholder="Пошук за назвою, артикулом або SKU..."
            class="search-dense-input"
            @input="$emit('update:searchQuery', $event.target.value)"
          />
        </div>

        <el-select
          :model-value="filterCategory"
          placeholder="Всі категорії"
          clearable
          @change="$emit('update:filterCategory', $event)"
          class="filter-dense-select pill-select"
          style="width: 160px;"
        >
          <el-option
            v-for="cat in categoryOptions"
            :key="cat.code"
            :label="cat.name"
            :value="cat.code"
          />
        </el-select>

        <el-select
          :model-value="filterType"
          placeholder="Всі типи"
          clearable
          @change="$emit('update:filterType', $event)"
          class="filter-dense-select pill-select"
          style="width: 140px;"
        >
          <el-option label="Усі типи" value="" />
          <el-option label="Готовий виріб" value="product" />
          <el-option label="Матеріал" value="material" />
          <el-option label="Комплектуюча" value="component" />
        </el-select>

        <el-select
          :model-value="filterStock"
          placeholder="Наявність"
          clearable
          @change="$emit('update:filterStock', $event)"
          class="filter-dense-select pill-select"
          style="width: 130px;"
        >
          <el-option label="Всі" value="" />
          <el-option label="В наявності" value="in_stock" />
          <el-option label="Закінчуються" value="low_stock" />
          <el-option label="Немає" value="out_of_stock" />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, Search } from '@element-plus/icons-vue'

defineProps({
  searchQuery: String,
  filterCategory: String,
  filterType: String,
  filterStock: String,
  activeTab: String,
  categoryOptions: {
    type: Array,
    default: () => []
  }
})

defineEmits([
  'update:searchQuery',
  'update:filterCategory',
  'update:filterType',
  'update:filterStock',
  'update:activeTab',
  'import',
  'export',
  'create'
])
</script>

<style scoped>
.toolbar-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.action-row__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-tabs-premium {
  display: flex;
  background: rgba(241, 245, 249, 0.6);
  padding: 4px;
  border-radius: 12px;
  gap: 4px;
}
.quick-tab-item {
  padding: 6px 14px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}
.quick-tab-item:hover { color: #0f172a; }
.quick-tab-item.active {
  background: #ffffff;
  color: #635bff;
  box-shadow: 0 2px 8px rgba(99, 91, 255, 0.12);
}

.act-btn {
  height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.18s ease;
  white-space: nowrap;
  border: none;
}
.act-btn--secondary {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #475569;
}
.act-btn--secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}
.act-btn--primary {
  background: linear-gradient(135deg, #635bff, #7c3aed);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(99,91,255,0.32);
}
.act-btn--primary:hover {
  box-shadow: 0 6px 20px rgba(99,91,255,0.42);
  transform: translateY(-1px);
}

.toolbar-dense {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 28px rgba(15,23,42,0.03);
  gap: 16px;
}
.toolbar-dense__left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.search-dense-wrapper {
  position: relative;
  width: 300px;
}
.search-dense-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 16px;
  width: 16px;
  height: 16px;
}
.search-dense-input {
  width: 100%;
  height: 38px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 0 12px 0 35px;
  font-size: 13px;
  background: #ffffff;
  transition: all 0.2s ease;
  color: #0f172a;
}
.search-dense-input:focus {
  outline: none;
  border-color: #635bff;
  box-shadow: 0 0 0 3px rgba(99, 91, 255, 0.1);
}
.pill-select :deep(.el-select__wrapper) {
  height: 38px !important;
  border-radius: 12px !important;
  border: 1px solid #e2e8f0 !important;
  background: #ffffff !important;
  box-shadow: none !important;
  font-size: 13px !important;
}
</style>
