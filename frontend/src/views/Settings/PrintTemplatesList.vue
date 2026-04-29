<template>
  <div class="templates-container">
    <div class="page-header">
      <div class="header-title">
        <h1>Шаблони документів</h1>
        <p>Керування друкованими формами системи</p>
      </div>
      <el-button type="primary" @click="navigateToNew" class="action-btn">
        <el-icon class="mr-1"><Plus /></el-icon> Створити шаблон
      </el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="filter-bar">
        <el-select v-model="filterType" placeholder="Фільтр за типом" clearable @change="fetchTemplates">
          <el-option label="Рахунок на оплату" value="invoice" />
          <el-option label="Видаткова накладна" value="sales_invoice" />
          <el-option label="Акт виконаних робіт" value="act" />
          <el-option label="Замовлення покупця" value="customer_order" />
        </el-select>
      </div>

      <el-table :data="templates" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="Назва шаблону" min-width="200">
          <template #default="scope">
            <span class="template-name" @click="editTemplate(scope.row.id)">
              {{ scope.row.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="document_type" label="Тип документа" width="180">
          <template #default="scope">
            <el-tag :type="getTypeTag(scope.row.document_type)" effect="light">
              {{ getTypeName(scope.row.document_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Статус" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'" size="small">
              {{ scope.row.is_active ? 'Активний' : 'Неактивний' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Основний" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.is_default" type="warning" size="small" effect="dark">Основний</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Дії" width="150" align="right">
          <template #default="scope">
            <el-button type="primary" size="small" text @click="editTemplate(scope.row.id)">
              Редагувати
            </el-button>
            <el-button 
              v-if="!scope.row.is_default" 
              type="danger" 
              size="small" 
              text 
              @click="deleteTemplate(scope.row.id)"
            >
              Видалити
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const templates = ref([])
const loading = ref(false)
const filterType = ref('')

const getTypeName = (type) => {
  const map = {
    'invoice': 'Рахунок на оплату',
    'sales_invoice': 'Видаткова накладна',
    'act': 'Акт виконаних робіт',
    'customer_order': 'Замовлення покупця'
  }
  return map[type] || type
}

const getTypeTag = (type) => {
  const map = {
    'invoice': 'primary',
    'sales_invoice': 'success',
    'act': 'warning',
    'customer_order': 'info'
  }
  return map[type] || ''
}

const fetchTemplates = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const url = filterType.value 
      ? `/api/v1/print/templates?document_type=${filterType.value}` 
      : '/api/v1/print/templates'
      
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` }
    })
    templates.value = response.data
  } catch (error) {
    ElMessage.error('Помилка завантаження шаблонів')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const navigateToNew = () => {
  router.push('/settings/print-templates/new')
}

const editTemplate = (id) => {
  router.push(`/settings/print-templates/${id}`)
}

const deleteTemplate = (id) => {
  ElMessageBox.confirm('Ви впевнені, що хочете видалити цей шаблон?', 'Увага', {
    confirmButtonText: 'Так, видалити',
    cancelButtonText: 'Скасувати',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`/api/v1/print/templates/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      ElMessage.success('Шаблон видалено')
      fetchTemplates()
    } catch (error) {
      ElMessage.error('Помилка при видаленні')
    }
  }).catch(() => {})
}

onMounted(fetchTemplates)
</script>

<style scoped>
.templates-container {
  padding: 24px;
  background-color: #f8fafc;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.header-title p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.action-btn {
  border-radius: 8px;
  padding: 10px 16px;
  font-weight: 500;
}

.table-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.filter-bar {
  margin-bottom: 20px;
}

.template-name {
  font-weight: 500;
  color: #4f46e5;
  cursor: pointer;
}

.template-name:hover {
  text-decoration: underline;
}

.mr-1 {
  margin-right: 4px;
}
</style>
