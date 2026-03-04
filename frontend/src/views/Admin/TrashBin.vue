<template>
  <div class="trash-bin-container">
    <div class="page-header">
      <div class="header-left">
        <h2>Корзина</h2>
        <p class="subtitle">Відновлення або остаточне видалення об'єктів</p>
      </div>
    </div>

    <el-card class="main-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="Товари" name="product" />
        <el-tab-pane label="Контрагенти" name="counterparty" />
        <el-tab-pane label="Склади" name="warehouse" />
      </el-tabs>

      <div class="table-actions">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук..."
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
        <el-button @click="fetchTrashItems" :icon="Refresh">Оновити</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="filteredItems"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column type="index" label="№" width="60" align="center" />
        
        <!-- Динамічні колонки залежно від типу -->
        <el-table-column v-if="activeTab === 'product'" prop="sku" label="Артикул" width="150" />
        <el-table-column v-if="activeTab === 'counterparty'" prop="tax_id" label="ЄДРПОУ/ІПН" width="150" />
        
        <el-table-column prop="name" label="Назва об'єкта" min-width="200" />
        
        <el-table-column label="Дії" width="220" align="center" fixed="right">
          <template #default="scope">
            <el-tooltip content="Відновити" placement="top">
              <el-button
                type="success"
                :icon="RefreshLeft"
                circle
                @click="handleRestore(scope.row)"
              />
            </el-tooltip>
            
            <el-tooltip content="Видалити назавжди" placement="top">
              <el-button
                type="danger"
                :icon="Delete"
                circle
                @click="confirmHardDelete(scope.row)"
              />
            </el-tooltip>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="Корзина порожня" />
        </template>
      </el-table>
    </el-card>

    <!-- Діалог підтвердження остаточного видалення -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="Увага! Остаточне видалення"
      width="400px"
    >
      <div class="delete-warning">
        <el-icon class="warning-icon" color="#F56C6C" :size="48"><Warning /></el-icon>
        <p>Ви впевнені, що хочете <b>назавжди</b> видалити <strong>{{ itemToDelete?.name }}</strong>?</p>
        <p class="text-danger">Цю дію неможливо скасувати. Об'єкт буде стерто з бази даних.</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">Скасувати</el-button>
          <el-button type="danger" @click="executeHardDelete" :loading="deleteLoading">
            Видалити назавжди
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Refresh, RefreshLeft, Delete, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

// Стейт
const loading = ref(false)
const activeTab = ref('product')
const searchQuery = ref('')
const trashData = ref({
  products: [],
  counterparties: [],
  warehouses: []
})

// Видалення
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const itemToDelete = ref(null)

// Computed для фільтрації
const currentItems = computed(() => {
  if (activeTab.value === 'product') return trashData.value.products || []
  if (activeTab.value === 'counterparty') return trashData.value.counterparties || []
  if (activeTab.value === 'warehouse') return trashData.value.warehouses || []
  return []
})

const filteredItems = computed(() => {
  if (!searchQuery.value) return currentItems.value
  
  const query = searchQuery.value.toLowerCase()
  return currentItems.value.filter(item => {
    return item.name?.toLowerCase().includes(query) || 
           item.sku?.toLowerCase().includes(query) ||
           item.tax_id?.toLowerCase().includes(query)
  })
})

// Завантаження даних
const fetchTrashItems = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/trash')
    trashData.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка при завантаженні корзини')
  } finally {
    loading.value = false
  }
}

const handleTabClick = () => {
  searchQuery.value = ''
}

// Відновлення
const handleRestore = async (item) => {
  try {
    await api.post(`/api/v1/trash/restore/${activeTab.value}/${item.id}`)
    ElMessage.success(`${item.name} успішно відновлено`)
    // Оновлюємо список
    fetchTrashItems()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка при відновленні')
  }
}

// Повне видалення
const confirmHardDelete = (item) => {
  itemToDelete.value = item
  deleteDialogVisible.value = true
}

const executeHardDelete = async () => {
  if (!itemToDelete.value) return
  
  deleteLoading.value = true
  try {
    await api.delete(`/api/v1/trash/hard_delete/${activeTab.value}/${itemToDelete.value.id}`)
    ElMessage.success('Об\'єкт назавжди видалено')
    deleteDialogVisible.value = false
    fetchTrashItems()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка при видаленні')
  } finally {
    deleteLoading.value = false
    itemToDelete.value = null
  }
}

onMounted(() => {
  fetchTrashItems()
})
</script>

<style scoped>
.trash-bin-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 4px 0 0 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.main-card {
  border-radius: 8px;
}

.table-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.delete-warning {
  text-align: center;
  padding: 10px 0;
}

.warning-icon {
  margin-bottom: 15px;
}

.text-danger {
  color: var(--el-color-danger);
  font-size: 13px;
  margin-top: 10px;
}
</style>
