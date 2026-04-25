<template>
  <div class="orders-page">
    <div class="fixed-top-area">
      <!-- ===== STAT CARDS ===== -->
      <div class="kimi-stats-row">
        <!-- Всього накладних -->
        <div class="kimi-stat-card kimi-stat-indigo">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Всього накладних</p>
            <p class="kimi-stat-value text-indigo-600">{{ receipts.length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-indigo-100 text-indigo-600">
            <el-icon><Document /></el-icon>
          </div>
        </div>
        <!-- Загальна сума -->
        <div class="kimi-stat-card kimi-stat-emerald">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Загальна сума</p>
            <p class="kimi-stat-value text-emerald-600">{{ formatCurrency(receipts.reduce((s, r) => s + (+r.total_amount || 0), 0)) }} ₴</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-emerald-100 text-emerald-600">
            <el-icon><Wallet /></el-icon>
          </div>
        </div>
        <!-- В роботі (Чернетки) -->
        <div class="kimi-stat-card kimi-stat-amber">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">В роботі</p>
            <p class="kimi-stat-value text-amber-600">{{ receipts.filter(r => r.status === 'draft').length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-amber-100 text-amber-600">
            <el-icon><Clock /></el-icon>
          </div>
        </div>
        <!-- Проведено -->
        <div class="kimi-stat-card kimi-stat-blue">
          <div class="kimi-stat-info">
            <p class="kimi-stat-label">Проведено</p>
            <p class="kimi-stat-value text-blue-600">{{ receipts.filter(r => r.status === 'posted').length }}</p>
          </div>
          <div class="kimi-stat-icon-wrapper bg-blue-100 text-blue-600">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>

      <!-- ===== SEARCH & FILTER BAR ===== -->
      <div class="kimi-filter-bar">
        <div class="kimi-filter-left">
          <el-input
            ref="searchInputRef"
            v-model="searchQuery"
            placeholder="Пошук за номером, постачальником..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            class="kimi-search-input"
          />
          <el-select
            v-model="activeStatus"
            placeholder="Всі статуси"
            clearable
            style="width:160px"
            @change="handleSearch"
            class="kimi-status-select"
          >
            <el-option label="Чернетка" value="draft" />
            <el-option label="Проведено" value="posted" />
          </el-select>
          <el-button class="kimi-refresh-btn" @click="fetchReceipts" title="Оновити">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        <div class="kimi-filter-right">
          <button class="kimi-primary-btn" @click="handleCreate">
            <el-icon><Plus /></el-icon> Нова накладна
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MAIN TABLE CARD ===== -->
    <div class="table-card scrollable-table-area">
      <el-table
        v-loading="loading"
        :data="filteredReceipts"
        height="100%"
        size="small"
        style="width: 100%"
        class="orders-table"
        @row-click="handleRowClick"
        row-class-name="kimi-row"
        header-row-class-name="kimi-header-row"
      >
        <el-table-column type="selection" width="40" align="center" />

        <el-table-column label="№" width="46" align="center">
          <template #default="{ $index }">
            <span class="kimi-text-xs kimi-text-slate-400">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Номер / Дата" width="160" sortable prop="receipt_number">
          <template #default="{ row }">
            <div>
              <p class="kimi-text-sm kimi-font-medium kimi-text-indigo-600">{{ row.receipt_number }}</p>
              <p class="kimi-text-xxs kimi-text-slate-400">{{ formatDate(row.receipt_date) }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Постачальник" min-width="200">
          <template #default="{ row }">
            <p class="kimi-text-sm kimi-font-medium">{{ getCounterpartyName(row.supplier_id) || '—' }}</p>
          </template>
        </el-table-column>

        <el-table-column label="На підставі" width="140">
          <template #default="{ row }">
            <span class="kimi-text-xs kimi-text-indigo-600 kimi-font-medium" v-if="row.base_order_id">
              {{ getOrderNumber(row.base_order_id) }}
            </span>
            <span class="kimi-text-xs kimi-text-slate-400" v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="140" align="center">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getStatusBadgeClass(row.status)">
              <el-icon class="kimi-badge-icon"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="Оплата" width="140" align="center">
          <template #default="{ row }">
            <span class="kimi-badge" :class="getPaymentBadgeClass(row)">
              {{ getPaymentLabel(row) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="total_amount" label="Сума" width="140" align="right" sortable>
          <template #default="{ row }">
            <p class="kimi-text-sm kimi-font-medium">{{ formatCurrency(row.total_amount) }} ₴</p>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="100" align="center">
          <template #default="{ row }">
            <div @click.stop class="kimi-actions-col">
              <button class="kimi-ghost-btn" @click.stop="handleEdit(row)" title="Редагувати"><el-icon class="kimi-text-indigo-400"><Edit /></el-icon></button>
              <button class="kimi-ghost-btn" @click.stop="handleDelete(row)" title="Видалити"><el-icon class="kimi-text-rose-400"><Delete /></el-icon></button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- PAGINATION -->
      <div class="pagination-footer">
        <span class="total-hint">Показано {{ filteredReceipts.length }} з {{ receipts.length }}</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          background
          layout="prev, pager, next"
          class="custom-pagination-numeric"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, Document, Wallet, Check, Clock, Refresh, Edit, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// ===== STATE =====
const loading = ref(false)
const receipts = ref([])
const counterparties = ref({})
const orders = ref({})
const searchQuery = ref('')
const activeStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// ===== COMPUTED =====
const filteredReceipts = computed(() => {
  let list = [...receipts.value]

  if (activeStatus.value) {
    list = list.filter(r => r.status === activeStatus.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r =>
      r.receipt_number?.toLowerCase().includes(q) ||
      getCounterpartyName(r.supplier_id)?.toLowerCase().includes(q)
    )
  }

  totalCount.value = list.length
  const start = (currentPage.value - 1) * pageSize.value
  return list.slice(start, start + pageSize.value)
})

// ===== API =====
const fetchReceipts = async () => {
  loading.value = true
  try {
    const [receiptsRes, cpRes, ordersRes] = await Promise.all([
      api.get('/api/v1/purchase-receipts'),
      api.get('/api/v1/counterparties', { params: { is_supplier: true } }),
      api.get('/api/v1/purchase-orders')
    ])
    receipts.value = receiptsRes.data
    
    // Build lookup maps
    const cpMap = {}
    cpRes.data.forEach(c => { cpMap[c.id] = c.name })
    counterparties.value = cpMap

    const ordMap = {}
    ordersRes.data.forEach(o => { ordMap[o.id] = o.order_number })
    orders.value = ordMap
  } catch {
    ElMessage.error('Помилка завантаження накладних')
  } finally {
    loading.value = false
  }
}

// ===== INTERACTIONS =====
const handleSearch = () => { currentPage.value = 1 }
const handleRowClick = (row) => { handleEdit(row) }
const handleCreate = () => router.push('/purchases/receipts/new')
const handleEdit = (row) => router.push(`/purchases/receipts/${row.id}`)

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити накладну ${row.receipt_number}?`, 'Увага', { type: 'warning' })
    .then(async () => {
      try {
        await api.delete(`/api/v1/purchase-receipts/${row.id}`)
        ElMessage.success('Видалено')
        fetchReceipts()
      } catch { ElMessage.error('Помилка видалення') }
    })
}

// ===== HELPERS =====
const formatDate = (d) => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const getCounterpartyName = (id) => counterparties.value[id] || '—'
const getOrderNumber = (id) => orders.value[id] || '—'
const formatCurrency = (v) => new Intl.NumberFormat('uk-UA', { minimumFractionDigits: 0 }).format(v || 0)

const getStatusBadgeClass = (status) => {
  return status === 'posted' ? 'kimi-status-emerald' : 'kimi-status-slate'
}
const getStatusIcon = (status) => {
  return status === 'posted' ? 'Check' : 'Clock'
}
const getStatusLabel = (status) => {
  return status === 'posted' ? 'Проведено' : 'Чернетка'
}

const getPaymentBadgeClass = (row) => 'kimi-payment-rose' // Placeholder
const getPaymentLabel = (row) => 'Не оплачено' // Placeholder

onMounted(fetchReceipts)
</script>

<style scoped>
/* Reusing styles from PurchaseOrderList.vue */
.orders-page {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #f4f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}
.fixed-top-area {
  flex-shrink: 0;
  z-index: 100;
  background: #f4f5f9;
  padding: 16px 20px 0px;
  display: flex;
  flex-direction: column;
}
.kimi-stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.kimi-stat-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #eef0f2;
}
.kimi-stat-info { display: flex; flex-direction: column; }
.kimi-stat-label { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; margin: 0; }
.kimi-stat-value { font-size: 24px; font-weight: 800; margin: 4px 0 0; }
.kimi-stat-icon-wrapper { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }

.kimi-filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.kimi-filter-left { display: flex; align-items: center; gap: 8px; flex: 1; }
.kimi-search-input { max-width: 400px; }
.kimi-search-input :deep(.el-input__wrapper) { border-radius: 6px; }
.kimi-status-select :deep(.el-select__wrapper) { border-radius: 6px; }
.kimi-refresh-btn { border-radius: 6px !important; }

.kimi-primary-btn {
  background: #4f46e5; color: #fff; border: none; border-radius: 6px; font-size: 14px; font-weight: 500;
  padding: 8px 16px; cursor: pointer; display: flex; align-items: center; gap: 6px;
}
.kimi-primary-btn:hover { background: #4338ca; }

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  margin: 0 20px 20px;
  flex: 1;
}

/* Kimi Table Styles */
.orders-table :deep(th.el-table__cell) {
  background: #f8fafc !important;
  color: #64748b;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 8px !important;
}
.orders-table :deep(.kimi-row) { cursor: pointer; }
.orders-table :deep(.kimi-row:hover > td) { background: #f8fafc !important; }

.kimi-text-xs { font-size: 12px; }
.kimi-text-xxs { font-size: 10px; }
.kimi-text-sm { font-size: 14px; }
.kimi-font-medium { font-weight: 500; }
.kimi-text-slate-400 { color: #94a3b8; }
.kimi-text-indigo-600 { color: #4f46e5; }
.kimi-text-indigo-400 { color: #818cf8; }
.kimi-text-emerald-600 { color: #059669; }
.kimi-text-rose-400 { color: #fb7185; }

.kimi-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 500; border: 1px solid transparent; }
.kimi-badge-icon { margin-right: 4px; }

.kimi-status-slate { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }
.kimi-status-emerald { background: #d1fae5; color: #059669; border-color: #a7f3d0; }

.kimi-payment-rose { background: #ffe4e6; color: #e11d48; border-color: #fecdd3; }

.kimi-actions-col { display: flex; gap: 4px; justify-content: center; }
.kimi-ghost-btn { background: none; border: none; cursor: pointer; padding: 4px; border-radius: 4px; }
.kimi-ghost-btn:hover { background: #f1f5f9; }

.pagination-footer {
  display: flex; justify-content: space-between; align-items: center; padding: 12px 20px;
  border-top: 1px solid #e2e8f0; background: #f8fafc;
}
</style>
