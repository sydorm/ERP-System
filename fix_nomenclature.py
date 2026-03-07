import re

file_path = r"g:\Моделювання\R1\frontend\src\views\Inventory\Nomenclature.vue"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_template = """<template>
  <div class="nomenclature-page">
    <div class="fixed-top-area">
      <!-- ===== PAGE HEADER ===== -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Номенклатура</h1>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
            <el-breadcrumb-item>Склад</el-breadcrumb-item>
            <el-breadcrumb-item>Номенклатура</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="goToCreate" class="btn-create">
            Створити товар
          </el-button>
        </div>
      </div>

      <!-- ===== STAT CARDS ===== -->
      <div class="stats-row">
        <div class="stat-card total">
          <div class="stat-icon"><el-icon><Box /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.total_products }}</div>
            <div class="stat-label">Всього товарів</div>
          </div>
          <div class="stat-dot"></div>
        </div>
        <div class="stat-card in-stock">
          <div class="stat-icon"><el-icon><Coordinate /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.in_stock }}</div>
            <div class="stat-label">В наявності</div>
          </div>
          <div class="stat-dot"></div>
        </div>
        <div class="stat-card low-stock">
          <div class="stat-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.low_stock }}</div>
            <div class="stat-label">Закінчуються</div>
          </div>
          <div class="stat-dot"></div>
        </div>
        <div class="stat-card out-of-stock">
          <div class="stat-icon"><el-icon><CircleClose /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.out_of_stock }}</div>
            <div class="stat-label">Немає</div>
          </div>
          <div class="stat-dot"></div>
        </div>
      </div>

      <!-- ===== FILTER BAR ===== -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук товарів... (/ для фокусу)"
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
          ref="searchInputRef"
        />
        
        <div class="category-chips">
          <button class="filter-tab" :class="{ active: filterCategory === '' }" @click="handleCategorySelect('')">
            Всі
          </button>
          <button 
            v-for="cat in categoryOptions" :key="cat.code" 
            class="filter-tab" 
            :class="{ active: filterCategory === cat.code }" 
            @click="handleCategorySelect(cat.code)"
          >
            {{ cat.name }}
          </button>
        </div>

        <div class="view-toggle">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="grid"><el-icon><Grid /></el-icon></el-radio-button>
            <el-radio-button value="list"><el-icon><Fold /></el-icon></el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div> <!-- END fixed-top-area -->

    <!-- ===== MAIN CONTENT CARD ===== -->
    <div class="table-card scrollable-content-area" v-loading="loading">
      <!-- Empty State -->
      <div v-if="products.length === 0 && !loading" class="empty-state">
        <el-empty description="Товарів не знайдено" />
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid' && products.length > 0" class="grid-content">
        <div class="dense-grid">
          <div 
            v-for="product in products" 
            :key="product.id" 
            class="dense-product-card"
            @click="handleEdit(product)"
          >
            <div class="card-img">
              <el-image :src="product.image_url" fit="cover" style="width: 100%; height: 100%;">
                <template #error>
                  <div class="img-ph"><el-icon><Picture /></el-icon></div>
                </template>
              </el-image>
            </div>
            <div class="card-info">
              <div class="card-cat">{{ getCategoryName(product.category) }}</div>
              <div class="card-title">{{ product.name }}</div>
              <div class="card-sku">{{ product.sku || '—' }}</div>
              <div class="card-bottom">
                <span class="card-price">{{ formatCurrency(product.price, product.currency) }}</span>
                <span class="card-stock" :class="getStockClass(product.stock_balance)">
                  {{ product.stock_balance }} <span class="unit">{{ product.unit_of_measure }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else-if="products.length > 0" class="list-content">
        <el-table 
          :data="products" 
          style="width: 100%" 
          height="100%"
          size="small"
          class="dense-table"
          @row-click="handleEdit"
          row-class-name="product-row"
        >
          <el-table-column width="60">
            <template #default="{ row }">
              <div class="list-avatar">
                <el-image :src="row.image_url" fit="cover" class="list-img">
                  <template #error><el-icon><Picture /></el-icon></template>
                </el-image>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="sku" label="Артикул" width="120">
            <template #default="{ row }"><span class="table-sku">{{ row.sku || '—' }}</span></template>
          </el-table-column>
          <el-table-column prop="name" label="Назва" min-width="200">
            <template #default="{ row }"><span class="table-title">{{ row.name }}</span></template>
          </el-table-column>
          <el-table-column label="Категорія" width="160">
            <template #default="{ row }"><span class="table-cat">{{ getCategoryName(row.category) }}</span></template>
          </el-table-column>
          <el-table-column label="Запас" width="120" align="right">
            <template #default="{ row }">
              <span class="table-stock" :class="getStockClass(row.stock_balance)">
                {{ row.stock_balance }} <span class="unit">{{ row.unit_of_measure }}</span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Ціна" width="120" align="right">
            <template #default="{ row }">
              <span class="table-price">{{ formatCurrency(row.price, row.currency) }}</span>
            </template>
          </el-table-column>
          <el-table-column width="60" align="right">
            <template #default="{ row }">
              <div @click.stop>
                <el-dropdown trigger="click" @command="(cmd) => { if(cmd==='edit') handleEdit(row); if(cmd==='delete') handleDelete(row); }">
                  <span class="action-btn"><el-icon><MoreFilled /></el-icon></span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">Редагувати</el-dropdown-item>
                      <el-dropdown-item command="delete" divided class="text-danger">Видалити</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- PAGINATION -->
      <div class="pagination-footer" v-if="products.length > 0">
        <span class="total-hint">Показано {{ products.length }} з {{ total }}</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="limit"
          layout="prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
          class="custom-pagination"
        />
      </div>
    </div>
  </div>
</template>"""

new_style = """<style scoped>
/* ===== PAGE ===== */
.nomenclature-page {
  padding: 0;
  background: #f4f5f9;
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* ===== FIXED TOP AREA ===== */
.fixed-top-area {
  position: sticky;
  top: -20px;
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ===== HEADER ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.page-title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.3px;
}
.breadcrumb { margin-top: 2px; }
.header-actions { display: flex; gap: 10px; }

.btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 9px;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  transition: box-shadow 0.2s, transform 0.15s;
}
.btn-create:hover {
  box-shadow: 0 6px 20px rgba(99,102,241,0.45);
  transform: translateY(-1px);
}

/* ===== STAT CARDS ===== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.08); transform: translateY(-1px); }
.stat-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.total .stat-icon { background: #ede9fe; color: #6366f1; }
.total .stat-dot { background: #6366f1; }

.in-stock .stat-icon { background: #d1fae5; color: #10b981; }
.in-stock .stat-dot { background: #10b981; }

.low-stock .stat-icon { background: #fef3c7; color: #f59e0b; }
.low-stock .stat-dot { background: #f59e0b; }

.out-of-stock .stat-icon { background: #fee2e2; color: #ef4444; }
.out-of-stock .stat-dot { background: #ef4444; }

.stat-value { font-size: 18px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.stat-label { font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-dot {
  position: absolute; top: 10px; right: 10px;
  width: 6px; height: 6px; border-radius: 50%;
}

/* ===== FILTER BAR & TABS ===== */
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 4px;
}
.search-input { width: 280px; flex-shrink: 0; }
.search-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  background: #fff;
  height: 28px;
}
.search-input :deep(.el-input__inner) { font-size: 12px; }
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}

.category-chips {
  display: flex;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
  padding-bottom: 2px;
}

.filter-tab {
  padding: 4px 10px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
}
.filter-tab:hover { border-color: #6366f1; color: #6366f1; }
.filter-tab.active {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
  box-shadow: 0 2px 8px rgba(99,102,241,0.28);
}

.view-toggle { margin-left: auto; }

/* ===== MAIN CARD & CONTENT ===== */
.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  margin: 0 20px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 400px;
}

/* ===== DENSE TABLE ===== */
.list-content { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.dense-table { flex: 1; }
.dense-table :deep(th.el-table__cell) {
  background: #f8fafc !important;
  color: #64748b;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  border-bottom: 1px solid #e2e8f0 !important;
  padding: 6px 8px !important;
  position: sticky;
  top: 0;
  z-index: 2;
}
.dense-table :deep(td.el-table__cell) {
  border-bottom: 1px solid #f1f5f9 !important;
  border-right: none !important;
  padding: 4px 8px !important;
}
.dense-table :deep(.product-row) { cursor: pointer; transition: background 0.15s; }
.dense-table :deep(.product-row:hover > td) { background: #f8fafc !important; }

.list-avatar {
  width: 32px; height: 32px;
  border-radius: 6px; overflow: hidden;
  background: #f1f5f9; display: flex; align-items: center; justify-content: center;
}
.list-img { width: 100%; height: 100%; }
.list-avatar .el-icon { color: #94a3b8; font-size: 14px; }

.table-sku { font-size: 11px; color: #64748b; font-family: monospace; }
.table-title { font-size: 12px; font-weight: 600; color: #1e293b; }
.table-cat { font-size: 11px; color: #64748b; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }
.table-stock { font-size: 12px; font-weight: 700; }
.table-stock .unit { font-size: 10px; font-weight: 500; color: #94a3b8; }
.table-price { font-size: 12px; font-weight: 600; color: #1e293b; }

.action-btn {
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover { background: #ede9fe; color: #6366f1; }

.text-success { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-danger { color: #ef4444; }

/* ===== DENSE GRID ===== */
.grid-content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}
.dense-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}
.dense-product-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}
.dense-product-card:hover { border-color: #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transform: translateY(-2px); }
.card-img {
  height: 120px;
  background: #f8fafc;
  display: flex; align-items: center; justify-content: center;
}
.img-ph { color: #cbd5e1; font-size: 24px; }
.card-info { padding: 10px; display: flex; flex-direction: column; flex: 1; }
.card-cat { font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 2px; }
.card-title { font-size: 12px; font-weight: 600; color: #1e293b; line-height: 1.3; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-sku { font-size: 10px; color: #94a3b8; font-family: monospace; margin-bottom: auto; }
.card-bottom { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 8px; }
.card-price { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-stock { font-size: 11px; font-weight: 700; }

/* ===== PAGINATION & EMPTY ===== */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}
.total-hint { font-size: 12px; color: #64748b; font-weight: 500; }
.custom-pagination :deep(.el-pager li) {
  background: transparent !important;
  font-size: 12px;
  min-width: 24px; height: 24px; line-height: 24px;
}
.custom-pagination :deep(.el-pager li.is-active) { color: #6366f1; font-weight: 700; }
.custom-pagination :deep(button) { background: transparent !important; }

.empty-state { padding: 40px 0; display: flex; justify-content: center; align-items: center; flex: 1; }
</style>"""

# Replace template
content = re.sub(r'<template>.*?</template>', new_template, content, flags=re.DOTALL)

# Replace style
content = re.sub(r'<style scoped>.*?</style>', new_style, content, flags=re.DOTALL)

# Insert MoreFilled icon import if it's not there
import_line_pattern = r"import \{\s*(.*?)\s*\}\s*from '@element-plus/icons-vue'"
def add_morefilled(match):
    icons = match.group(1)
    if 'MoreFilled' not in icons:
        icons += ', MoreFilled'
    return f"import {{ {icons} }} from '@element-plus/icons-vue'"

content = re.sub(import_line_pattern, add_morefilled, content)

# Add searchInputRef declaration
if 'const searchInputRef =' not in content:
    content = content.replace('const limit = ref(12)', 'const limit = ref(20)\nconst searchInputRef = ref(null)')

# Add keyboard shortcuts listener
script_to_add = """
// ===== KEYBOARD SHORTCUTS =====
const handleKeydown = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  if (e.key === 'n' || e.key === 'N') { e.preventDefault(); goToCreate() }
  if (e.key === '/') { e.preventDefault(); searchInputRef.value?.focus() }
}
onMounted(() => { window.addEventListener('keydown', handleKeydown) })
onUnmounted(() => { window.removeEventListener('keydown', handleKeydown) })
"""
if 'handleKeydown' not in content:
    # Just insert it before </script>
    import_unmounted = ""
    if 'onUnmounted' not in content:
       content = re.sub(r"import \{([^}]+)\} from 'vue'", lambda m: f"import {{{m.group(1)}, onUnmounted}} from 'vue'" if 'onUnmounted' not in m.group(1) else m.group(0), content)

    content = content.replace('</script>', script_to_add + '\n</script>')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Nomenclature updated successfully.")
