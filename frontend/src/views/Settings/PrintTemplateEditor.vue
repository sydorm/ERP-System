<template>
  <div class="editor-container">
    <div class="page-header">
      <div class="header-title">
        <el-button @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> Назад
        </el-button>
        <h1>{{ isNew ? 'Створення шаблону' : 'Редагування шаблону' }}</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="saveTemplate" :loading="saving" class="action-btn">
          Зберегти
        </el-button>
      </div>
    </div>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="form-layout">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="form-card" shadow="never">
            <el-form-item label="Назва шаблону" prop="name">
              <el-input v-model="form.name" placeholder="Наприклад: Рахунок стандартний" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Тип документа" prop="document_type">
                  <el-select v-model="form.document_type" placeholder="Оберіть тип" style="width: 100%">
                    <el-option label="Рахунок на оплату" value="invoice" />
                    <el-option label="Видаткова накладна" value="sales_invoice" />
                    <el-option label="Акт виконаних робіт" value="act" />
                    <el-option label="Замовлення покупця" value="customer_order" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Опис" prop="description">
                  <el-input v-model="form.description" placeholder="Опис шаблону" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="switches-block">
              <el-form-item label="Статус" prop="is_active" class="switch-item">
                <el-switch v-model="form.is_active" active-text="Активний" />
              </el-form-item>
              <el-form-item label="За замовчуванням" prop="is_default" class="switch-item">
                <el-switch v-model="form.is_default" active-text="Основний" />
              </el-form-item>
            </div>

            <el-form-item label="HTML-код шаблону" prop="html_template" class="code-item">
              <el-input 
                v-model="form.html_template" 
                type="textarea" 
                :rows="20" 
                placeholder="Введіть HTML структуру документа..." 
                class="code-editor"
              />
            </el-form-item>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="glossary-card" shadow="never">
            <template #header>
              <div class="glossary-header">
                <span>Доступні змінні</span>
              </div>
            </template>
            <div class="glossary-content">
              <p class="glossary-desc">Клікніть, щоб скопіювати змінну в буфер обміну:</p>
              
              <div class="glossary-section">
                <h4>Документ</h4>
                <el-tag class="variable-tag" @click="copyToClipboard('{{document.number}}')" v-text="'{{document.number}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{document.date}}')" v-text="'{{document.date}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{document.contract}}')" v-text="'{{document.contract}}'"></el-tag>
              </div>

              <div class="glossary-section">
                <h4>Постачальник</h4>
                <el-tag class="variable-tag" @click="copyToClipboard('{{seller.name}}')" v-text="'{{seller.name}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{seller.edrpou}}')" v-text="'{{seller.edrpou}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{seller.iban}}')" v-text="'{{seller.iban}}'"></el-tag>
              </div>

              <div class="glossary-section">
                <h4>Покупець</h4>
                <el-tag class="variable-tag" @click="copyToClipboard('{{buyer.name}}')" v-text="'{{buyer.name}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{buyer.edrpou}}')" v-text="'{{buyer.edrpou}}'"></el-tag>
              </div>

              <div class="glossary-section">
                <h4>Таблиця товарів</h4>
                <el-tag class="variable-tag type-table" @click="copyToClipboard('{{items_table}}')" v-text="'{{items_table}}'"></el-tag>
              </div>

              <div class="glossary-section">
                <h4>Підсумки</h4>
                <el-tag class="variable-tag" @click="copyToClipboard('{{totals.total_with_vat}}')" v-text="'{{totals.total_with_vat}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{totals.vat}}')" v-text="'{{totals.vat}}'"></el-tag>
                <el-tag class="variable-tag" @click="copyToClipboard('{{totals.total_in_words}}')" v-text="'{{totals.total_in_words}}'"></el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)

const id = computed(() => route.params.id)
const isNew = computed(() => !id.value || id.value === 'new')

const form = reactive({
  name: '',
  document_type: 'invoice',
  description: '',
  html_template: '',
  css_template: '',
  is_default: false,
  is_active: true
})

const rules = {
  name: [{ required: true, message: 'Вкажіть назву шаблону', trigger: 'blur' }],
  document_type: [{ required: true, message: 'Оберіть тип документа', trigger: 'change' }],
  html_template: [{ required: true, message: 'Введіть HTML вміст', trigger: 'blur' }]
}

const goBack = () => {
  router.push('/settings/print-templates')
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage({
    message: `Змінну ${text} скопійовано!`,
    type: 'success',
    duration: 1500
  })
}

const fetchTemplate = async () => {
  if (isNew.value) return
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`/api/v1/print/templates/${id.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const data = response.data
    form.name = data.name
    form.document_type = data.document_type
    form.description = data.description
    form.html_template = data.html_template
    form.css_template = data.css_template
    form.is_default = data.is_default
    form.is_active = data.is_active
  } catch (error) {
    ElMessage.error('Не вдалося завантажити шаблон')
    goBack()
  }
}

const saveTemplate = async () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      const token = localStorage.getItem('token')
      
      if (isNew.value) {
        await axios.post('/api/v1/print/templates', form, {
          headers: { Authorization: `Bearer ${token}` }
        })
        ElMessage.success('Шаблон створено')
      } else {
        await axios.put(`/api/v1/print/templates/${id.value}`, form, {
          headers: { Authorization: `Bearer ${token}` }
        })
        ElMessage.success('Шаблон оновлено')
      }
      goBack()
    } catch (error) {
      ElMessage.error('Помилка при збереженні')
    } finally {
      saving.value = false
    }
  })
}

onMounted(fetchTemplate)
</script>

<style scoped>
.editor-container {
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

.header-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.back-btn {
  border-radius: 8px;
}

.form-card, .glossary-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.switches-block {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
  background: #f1f5f9;
  padding: 16px;
  border-radius: 8px;
}

.switch-item {
  margin-bottom: 0;
}

.code-editor {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
}

.glossary-desc {
  font-size: 13px;
  color: #64748b;
  margin-top: 0;
  margin-bottom: 16px;
}

.glossary-section {
  margin-bottom: 20px;
}

.glossary-section h4 {
  font-size: 14px;
  color: #334155;
  margin: 0 0 8px 0;
}

.variable-tag {
  margin-right: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.variable-tag:hover {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #c7d2fe;
  transform: translateY(-1px);
}

.type-table {
  width: 100%;
  text-align: center;
}
</style>
