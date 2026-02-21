<template>
  <div class="numbering-container">
    <div class="page-header">
      <div class="header-content">
        <h2>Нумерація документів</h2>
        <p class="text-gray">Налаштування префіксів та лічильників номерів для різних типів документів</p>
      </div>
    </div>

    <!-- Main Content: Items List -->
    <div class="view-content">
      <div class="content-header">
        <div class="content-title">
          <h3>Системні лічильники</h3>
          <p>Ці лічильники використовуються для автоматичної генерації номерів нових документів.</p>
        </div>
      </div>

      <div class="items-list" v-loading="loading">
        <div v-for="(item, index) in sequences" :key="item.id" class="list-item">
          <div class="item-left">
            <div class="item-icon-circle bg-blue-light">
              <el-icon><Document /></el-icon>
            </div>
            <div class="item-details">
              <div class="item-name">
                {{ formatDocType(item.document_type) }}
                <el-tag size="small" type="info">{{ item.document_type }}</el-tag>
              </div>
              <div class="item-desc">
                Формат: <strong>{{ item.prefix }}{{ String('1').padStart(item.padding, '0') }}</strong>
                (Наступний: {{ item.next_number }})
              </div>
            </div>
          </div>
          
          <div class="item-right">
            <el-button type="primary" plain @click="openEditModal(item)">
              <el-icon class="mr-1"><Edit /></el-icon> Налаштувати
            </el-button>
          </div>
        </div>
        
        <el-empty v-if="sequences.length === 0" description="Немає записів. Створіть перший документ, щоб лічильник з'явився автоматично." />
      </div>
    </div>

    <!-- Edit Modal -->
    <el-dialog v-model="dialogVisible" title="Налаштування лічильника" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-alert
          title="Обережно зі зміною 'Наступний номер'"
          type="warning"
          description="Зменшення цього числа може призвести до дублювання номерів, якщо такі документи вже існують у базі."
          show-icon
          class="mb-4"
          :closable="false"
        />

        <el-form-item label="Тип документа">
          <el-input :model-value="formatDocType(form.document_type)" disabled />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Префікс" prop="prefix">
              <el-input v-model="form.prefix" placeholder="напр. ORD-" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="К-сть нулів (Padding)" prop="padding">
              <el-input-number v-model="form.padding" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Наступний номер (Лічильник)" prop="next_number">
          <el-input-number v-model="form.next_number" :min="1" style="width: 100%" />
        </el-form-item>
        
        <div class="preview-box mt-2 p-3 bg-gray-light rounded">
          <span class="text-sm text-gray">Приклад наступного номера:</span><br/>
          <strong class="text-lg text-primary">
            {{ form.prefix }}{{ String(form.next_number || 1).padStart(form.padding || 5, '0') }}
          </strong>
        </div>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            Зберегти
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Document, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const sequences = ref([])
const loading = ref(false)
const submitting = ref(false)

const dialogVisible = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  document_type: '',
  prefix: '',
  next_number: 1,
  padding: 5
})

const rules = {
  prefix: [{ required: false, message: 'Введіть префікс', trigger: 'blur' }],
  next_number: [{ required: true, message: 'Введіть наступний номер', trigger: 'blur' }],
  padding: [{ required: true, message: 'Вкажіть кількість нулів', trigger: 'blur' }]
}

const docTypeLabels = {
  'order': 'Замовлення клієнта',
  'purchase_receipt': 'Прибуткова накладна',
  'sales_invoice': 'Видаткова накладна',
  'transfer': 'Переміщення',
  'inventory': 'Інвентаризація'
}

const formatDocType = (type) => {
  return docTypeLabels[type] || type
}

const fetchSequences = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/document-sequences')
    sequences.value = response.data
  } catch (error) {
    ElMessage.error('Помилка завантаження лічильників')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openEditModal = (item) => {
  form.id = item.id
  form.document_type = item.document_type
  form.prefix = item.prefix
  form.next_number = item.next_number
  form.padding = item.padding
  
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          prefix: form.prefix,
          next_number: form.next_number,
          padding: form.padding
        }
        await api.put(`/api/v1/document-sequences/${form.id}`, payload)
        
        ElMessage.success('Налаштування збережено')
        dialogVisible.value = false
        fetchSequences()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchSequences()
})
</script>

<style scoped>
.numbering-container {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1d1f;
}

.text-gray {
  color: #6f767e;
  margin: 0;
}

.text-primary {
  color: #2a85ff;
}

.bg-blue-light {
  background-color: #e3efeb;
  color: #2a85ff;
}

.bg-gray-light {
  background-color: #f4f4f4;
}

.view-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
}

.content-header {
  margin-bottom: 24px;
}

.content-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1d1f;
}

.content-title p {
  margin: 0;
  color: #6f767e;
  font-size: 13px;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid #eef0f2;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.list-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.item-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.item-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1d1f;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-desc {
  font-size: 13px;
  color: #6f767e;
}

.preview-box {
  border: 1px solid #eef0f2;
  text-align: center;
}
</style>
