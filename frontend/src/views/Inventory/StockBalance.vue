<template>
  <div class="erp-light-container">
    <!-- Top Actions Bar -->
    <div class="erp-actions-toolbar">
      <div class="actions-left">
        <el-input 
          v-model="searchQuery" 
          placeholder="Пошук товару або артикула..." 
          :prefix-icon="Search" 
          clearable 
          class="search-input"
        />
        
        <el-select v-model="filterWarehouse" placeholder="Склад" clearable class="ml-2">
          <el-option v-for="wh in warehouses" :key="wh.id" :label="wh.name" :value="wh.id" />
        </el-select>

        <el-select v-model="filterCategory" placeholder="Категорія" clearable class="ml-2">
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </div>

      <div class="actions-right">
        <el-button :icon="Refresh" @click="fetchStock" circle />
        <el-button type="primary" :icon="Download" @click="exportStock">
          Експорт
        </el-button>
      </div>
    </div>

    <!-- Stats Row -->
    <el-row :gutter="20" class="stats-row mt-4">
      <el-col :span="6">
        <div class="metric-card" style="--card-accent: #3B82F6;">
          <div class="metric-card__label">ПОЗИЦІЙ В НАЯВНОСТІ</div>
          <div class="metric-card__value">{{ filteredStock.length }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card" style="--card-accent: #22C55E;">
          <div class="metric-card__label">ЗАГАЛЬНА КІЛЬКІСТЬ</div>
          <div class="metric-card__value">{{ totalQty }} шт</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card" style="--card-accent: #F59E0B;">
          <div class="metric-card__label">ОЦІНКА ЗАЛИШКІВ</div>
          <div class="metric-card__value">{{ formatCurrency(totalValue) }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- Stock Table -->
    <div class="mt-5 list-container">
      <el-table 
        v-loading="loading" 
        :data="filteredStock" 
        style="width: 100%" 
        class="light-premium-table"
        border
        stripe
      >
        <el-table-column label="Товар" min-width="250">
          <template #default="scope">
            <div class="product-cell">
              <router-link :to="'/inventory/nomenclature/' + scope.row.product_id" class="product-name">
                {{ scope.row.product_name }}
              </router-link>
              <div class="product-sku">{{ scope.row.variant_sku }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Характеристика" min-width="150">
          <template #default="scope">
            <el-tag size="small" type="info" effect="plain" v-if="scope.row.variant_label">
              {{ scope.row.variant_label }}
            </el-tag>
            <span v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column label="Склад" min-width="150">
          <template #default="scope">
            <div class="warehouse-tag">
              <el-icon><Location /></el-icon>
              <span>{{ scope.row.warehouse }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Категорія" prop="category" min-width="120">
          <template #default="scope">
            <el-tag size="small" v-if="scope.row.category">{{ scope.row.category }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Собівартість" width="130" align="right">
          <template #default="scope">
            <span class="dm-mono">{{ formatCurrency(scope.row.cost) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Наявність" width="120" align="right">
          <template #default="scope">
            <span :class="{'text-danger': scope.row.quantity <= 0, 'text-success': scope.row.quantity > 0}" class="fw-bold">
              {{ scope.row.quantity }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="Разом" width="150" align="right">
          <template #default="scope">
            <span class="dm-mono fw-bold">{{ formatCurrency(scope.row.cost * scope.row.quantity) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Download, Refresh, Location } from '@element-plus/icons-vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const stock = ref([])
const warehouses = ref([])
const searchQuery = ref('')
const filterWarehouse = ref('')
const filterCategory = ref('')

const fetchStock = async () => {
  loading.value = true
  try {
    const [stockRes, warehousesRes] = await Promise.all([
      api.get('/api/v1/warehouses/stock'),
      api.get('/api/v1/warehouses')
    ])
    stock.value = stockRes.data
    warehouses.value = warehousesRes.data
  } catch (error) {
    console.error('Error fetching stock:', error)
    ElMessage.error('Помилка завантаження залишків')
  } finally {
    loading.value = false
  }
}

const categories = computed(() => {
  const cats = new Set(stock.value.map(i => i.category).filter(Boolean))
  return Array.from(cats).sort()
})

const filteredStock = computed(() => {
  return stock.value.filter(item => {
    const matchesSearch = !searchQuery.value || 
      item.product_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (item.variant_sku && item.variant_sku.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    const matchesWarehouse = !filterWarehouse.value || item.warehouse_id === filterWarehouse.value
    const matchesCategory = !filterCategory.value || item.category === filterCategory.value
    
    return matchesSearch && matchesWarehouse && matchesCategory
  })
})

const totalQty = computed(() => filteredStock.value.reduce((sum, i) => sum + i.quantity, 0))
const totalValue = computed(() => filteredStock.value.reduce((sum, i) => sum + (i.quantity * (i.cost || 0)), 0))

const formatCurrency = (val) => {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)
}

const exportStock = () => {
  ElMessage.info('Функція експорту в розробці')
}

onMounted(() => {
  fetchStock()
})
</script>

<style scoped>
.erp-light-container {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 64px);
}

.erp-actions-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.search-input { width: 300px; }

.metric-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  border-left: 4px solid var(--card-accent);
  box-shadow: 0 4px 15px rgba(0,0,0,0.02);
}

.metric-card__label {
  font-size: 12px;
  font-weight: 700;
  color: #64748B;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.metric-card__value {
  font-size: 24px;
  font-weight: 800;
  color: #1E293B;
}

.product-cell {
  display: flex;
  flex-direction: column;
}

.product-name {
  color: #1463FF;
  font-weight: 600;
  text-decoration: none;
}

.product-sku {
  font-size: 11px;
  color: #64748B;
  margin-top: 2px;
}

.warehouse-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  font-size: 13px;
}

.dm-mono { font-family: 'DM Mono', monospace; }
.fw-bold { font-weight: 700; }
.text-danger { color: #EF4444; }
.text-success { color: #10B981; }
</style>
