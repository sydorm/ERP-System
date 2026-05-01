<template>
  <div class="toolbar-section">
    <!-- ===== CONSOLIDATED ACTION & FILTER ROW ===== -->
    <div class="action-row">
      <div class="action-row__left">
        <div class="search-dense-wrapper">
          <el-icon class="search-dense-icon"><Search /></el-icon>
          <input
            :value="searchQuery"
            placeholder="Пошук за назвою, артикулом..."
            class="search-dense-input"
            @input="$emit('update:searchQuery', $event.target.value)"
          />
        </div>

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
}

.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.action-row__left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.action-row__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.act-btn {
  height: 44px;
  padding: 0 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
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
  border: 1px solid #E6ECF3;
  color: #5A6A80;
}

.act-btn--secondary:hover {
  background: #f8fafc;
  border-color: #1463FF;
  color: #1463FF;
}

.act-btn--primary {
  background: linear-gradient(135deg, #15B97A 0%, #0E905F 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(21, 185, 122, 0.22);
}

.act-btn--primary:hover {
  background: linear-gradient(135deg, #12A46C 0%, #15B97A 100%);
  box-shadow: 0 6px 18px rgba(21, 185, 122, 0.3);
  transform: translateY(-1px);
}

.search-dense-wrapper {
  position: relative;
  width: 260px;
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
  height: 44px;
  border-radius: 12px;
  border: 1px solid #E6ECF3;
  padding: 0 12px 0 40px;
  font-size: 14px;
  background: #ffffff;
  transition: all 0.2s ease;
  color: #0f172a;
}

.search-dense-input:focus {
  outline: none;
  border-color: #1463FF;
  box-shadow: 0 0 0 3px rgba(20, 99, 255, 0.1);
}

.pill-select :deep(.el-select__wrapper) {
  height: 44px !important;
  border-radius: 12px !important;
  border: 1px solid #E6ECF3 !important;
  background: #ffffff !important;
  box-shadow: none !important;
  font-size: 14px !important;
}
</style>
