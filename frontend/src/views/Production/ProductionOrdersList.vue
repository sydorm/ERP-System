<template>
  <div class="erp-page-container">
    <!-- Header -->
    <div class="erp-toolbar">
      <div class="toolbar-left">
        <h1 class="page-title">Завдання на виробництво</h1>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="createNew">Створити завдання</el-button>
        <el-button :icon="Refresh" circle @click="fetchData" />
      </div>
    </div>

    <!-- Filters -->
    <div class="erp-filters-bar">
      <el-input
        v-model="searchQuery"
        placeholder="Пошук за номером, коментарем..."
        class="search-input"
        :prefix-icon="Search"
        clearable
        @clear="fetchData"
        @keyup.enter="fetchData"
      />
      
      <el-select v-model="statusFilter" placeholder="Всі статуси" clearable class="status-select" @change="fetchData">
        <el-option label="Чернетка" value="draft" />
        <el-option label="В роботі" value="in_progress" />
        <el-option label="Завершено" value="completed" />
        <el-option label="Скасовано" value="cancelled" />
      </el-select>
    </div>

    <!-- Data Table -->
    <div class="erp-table-container" v-loading="loading">
      <el-table
        :data="filteredOrders"
        style="width: 100%"
        class="erp-table"
        stripe
        hover
        @row-dblclick="handleRowDblClick"
      >
        <el-table-column prop="order_date" label="Дата" width="160">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.order_date) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="order_number" label="Номер" width="150">
          <template #default="{ row }">
            <span class="code-text" @click.stop="editOrder(row)">{{ row.order_number }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="Статус" width="130">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="light" round class="status-tag">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Пов'язаний документ" min-width="180">
          <template #default="{ row }">
            <div v-if="row.base_order_id" class="doc-badge">
              <el-icon><Document /></el-icon> Замовлення покупця
            </div>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="comment" label="Коментар" min-width="200" show-overflow-tooltip />

        <el-table-column fixed="right" label="Дії" width="100" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-2">
              <el-button
                type="primary"
                :icon="Edit"
                circle
                size="small"
                plain
                class="action-btn"
                @click="editOrder(row)"
              />
              <el-popconfirm
                title="Видалити завдання?"
                confirm-button-text="Так"
                cancel-button-text="Ні"
                @confirm="deleteOrder(row)"
              >
                <template #reference>
                  <el-button
                    type="danger"
                    :icon="Delete"
                    circle
                    size="small"
                    plain
                    class="action-btn"
                  />
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="Немає завдань на виробництво" />
        </template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh, Search, Edit, Delete, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const orders = ref([])
const loading = ref(false)

const searchQuery = ref('')
const statusFilter = ref('')

// Computed
const filteredOrders = computed(() => {
  let result = orders.value

  if (statusFilter.value) {
    result = result.filter(o => o.status === statusFilter.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(o => 
      (o.order_number && o.order_number.toLowerCase().includes(q)) ||
      (o.comment && o.comment.toLowerCase().includes(q))
    )
  }

  return result
})

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    // We only have the standard root path per our backend setup
    const response = await api.get('/api/v1/production')
    orders.value = response.data
  } catch (error) {
    console.error('Failed to load production orders', error)
    ElMessage.error('Помилка завантаження завдань')
  } finally {
    loading.value = false
  }
}

const createNew = () => {
  router.push('/production/orders/new')
}

const editOrder = (row) => {
  router.push(`/production/orders/${row.id}`)
}

const handleRowDblClick = (row) => {
  editOrder(row)
}

const deleteOrder = async (row) => {
  if (row.status !== 'draft') {
    ElMessage.warning('Можна видаляти лише чернетки')
    return
  }
  
  try {
    await api.delete(`/api/v1/production/${row.id}`)
    ElMessage.success('Завдання видалено')
    fetchData()
  } catch (err) {
    ElMessage.error('Помилка видалення')
  }
}

// Formatters
const formatDate = (dateString) => {
  if (!dateString) return ''
  return dayjs(dateString).format('DD.MM.YYYY HH:mm')
}

const getStatusLabel = (status) => {
  const map = {
    draft: 'Чернетка',
    released: 'В роботу',
    in_progress: 'В процесі',
    completed: 'Завершено',
    cancelled: 'Скасовано'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    released: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* Inherits global .erp-page-container, .erp-toolbar, .erp-filters-bar */
.date-text {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.code-text {
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-weight: 600;
  color: #409eff;
  cursor: pointer;
  font-size: 13px;
}

.code-text:hover {
  text-decoration: underline;
}

.status-tag {
  min-width: 80px;
  text-align: center;
  font-weight: 500;
}

.doc-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

.action-btn {
  border: none;
  background: transparent;
}

.action-btn:hover {
  background: #f3f4f6;
  transform: translateY(-1px);
}
</style>
