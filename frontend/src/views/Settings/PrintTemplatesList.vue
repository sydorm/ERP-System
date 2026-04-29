<template>
  <div class="templates-container">
    <div class="page-header">
      <div class="header-title">
        <h1>Шаблони документів</h1>
        <p>Керування друкованими формами та бланками системи</p>
      </div>
      <el-button type="primary" @click="navigateToNew" class="action-btn">
        <el-icon class="mr-1"><Plus /></el-icon> Створити шаблон
      </el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterType" placeholder="Фільтр за типом" clearable @change="fetchTemplates" style="width: 240px">
        <el-option label="Рахунок на оплату" value="invoice" />
        <el-option label="Видаткова накладна" value="sales_invoice" />
        <el-option label="Акт виконаних робіт" value="act" />
        <el-option label="Замовлення покупця" value="customer_order" />
      </el-select>
    </div>

    <el-row :gutter="20" v-loading="loading" class="template-grid">
      <el-col :span="6" v-for="t in templates" :key="t.id" class="grid-col">
        <el-card class="template-card" :body-style="{ padding: '20px' }" shadow="hover">
          <div class="template-icon" :class="t.document_type">
            <el-icon size="32"><Document /></el-icon>
          </div>
          
          <h3 class="t-title">{{ t.name }}</h3>
          <div class="t-type">
            <el-tag :type="getTypeTag(t.document_type)" size="small" effect="plain">
              {{ getTypeName(t.document_type) }}
            </el-tag>
          </div>
          
          <div class="t-badges">
            <el-tag :type="t.is_active ? 'success' : 'info'" size="small">
              {{ t.is_active ? 'Активний' : 'Неактивний' }}
            </el-tag>
            <el-tag v-if="t.is_default" type="warning" size="small" effect="dark" class="ml-1">
              Основний
            </el-tag>
          </div>

          <div class="t-actions">
            <el-tooltip content="Попередній перегляд" placement="top">
              <el-button circle size="small" @click="previewTemplate(t.id)">
                <el-icon><View /></el-icon>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="Дублювати шаблон" placement="top">
              <el-button circle size="small" @click="duplicateTemplate(t)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip v-if="!t.is_default" content="Зробити основним" placement="top">
              <el-button type="warning" circle size="small" @click="setAsDefault(t)">
                <el-icon><Star /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip content="Редагувати" placement="top">
              <el-button type="primary" circle size="small" @click="editTemplate(t.id)">
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip v-if="!t.is_default" content="Видалити" placement="top">
              <el-button type="danger" circle size="small" @click="deleteTemplate(t.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="24" v-if="templates.length === 0 && !loading">
        <el-empty description="Шаблони відсутні. Створіть свій перший шаблон!" />
      </el-col>
    </el-row>

    <!-- Preview Modal -->
    <el-dialog
      v-model="previewVisible"
      title="Перегляд макета документа"
      width="800px"
      destroy-on-close
    >
      <div class="preview-frame" v-if="previewHtml" v-html="previewHtml"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, View, CopyDocument, Star, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const templates = ref([])
const loading = ref(false)
const filterType = ref('')

const previewVisible = ref(false)
const previewHtml = ref('')

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

const previewTemplate = async (id) => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`/api/v1/print/templates/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    previewHtml.value = response.data.html_template
    previewVisible.value = true
  } catch (error) {
    ElMessage.error('Не вдалося завантажити макет для перегляду')
  }
}

const setAsDefault = async (template) => {
  try {
    const token = localStorage.getItem('token')
    await axios.put(`/api/v1/print/templates/${template.id}`, 
      { ...template, is_default: true },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success(`Шаблон "${template.name}" встановлено основним`)
    fetchTemplates()
  } catch (error) {
    ElMessage.error('Помилка оновлення статусу')
  }
}

const duplicateTemplate = async (template) => {
  try {
    const token = localStorage.getItem('token')
    const clone = {
      name: `${template.name} (Копія)`,
      document_type: template.document_type,
      description: template.description,
      html_template: template.html_template,
      css_template: template.css_template,
      is_default: false,
      is_active: true
    }
    
    await axios.post('/api/v1/print/templates', clone, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('Шаблон успішно продубльовано')
    fetchTemplates()
  } catch (error) {
    ElMessage.error('Помилка дублювання шаблону')
  }
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

.filter-bar {
  margin-bottom: 24px;
}

.template-grid {
  margin-top: 12px;
}

.grid-col {
  margin-bottom: 20px;
}

.template-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #ffffff;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  border-color: #c7d2fe;
}

.template-icon {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  margin-bottom: 16px;
}

.template-icon.invoice {
  background: #eff6ff;
  color: #2563eb;
}

.template-icon.sales_invoice {
  background: #ecfdf5;
  color: #10b981;
}

.template-icon.act {
  background: #fffbeb;
  color: #f59e0b;
}

.template-icon.customer_order {
  background: #faf5ff;
  color: #8b5cf6;
}

.t-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.t-type {
  margin-bottom: 12px;
}

.t-badges {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.t-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.ml-1 {
  margin-left: 6px;
}

.mr-1 {
  margin-right: 4px;
}

.preview-frame {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  padding: 10px;
  max-height: 60vh;
  overflow-y: auto;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
</style>
