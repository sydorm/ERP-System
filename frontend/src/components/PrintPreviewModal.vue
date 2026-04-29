<template>
  <el-dialog
    v-model="visible"
    title="Попередній перегляд документа"
    width="850px"
    class="print-dialog"
    :before-close="handleClose"
    append-to-body
    destroy-on-close
  >
    <template #header>
      <div class="dialog-header-actions">
        <h3>Друк документа</h3>
        <div class="actions-toolbar">
          <el-button type="primary" @click="triggerPrint">
            <el-icon class="mr-1"><Printer /></el-icon> Друкувати
          </el-button>
          <el-button @click="handleClose">Закрити</el-button>
        </div>
      </div>
    </template>

    <div class="print-container" v-loading="loading">
      <div v-if="!loading && renderedHtml" class="document-frame" ref="printFrame">
        <div v-html="renderedHtml"></div>
      </div>
      <el-empty v-else-if="!loading" description="Не вдалося сформувати друковану форму" />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Printer } from '@element-plus/icons-vue'
import axios from 'axios'
import { renderTemplate } from '@/utils/templateEngine'
import { numberToUkrainianWords } from '@/utils/numberToWordsUk'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  documentId: { type: String, required: true },
  documentType: { type: String, required: true },
  templateId: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const renderedHtml = ref('')
const printFrame = ref(null)

const triggerPrint = () => {
  const printContents = printFrame.value.innerHTML
  const originalContents = document.body.innerHTML

  // Temporary inject contents to prevent printing the ERP dashboard itself
  const printWindow = window.open('', '_blank', 'width=900,height=800')
  printWindow.document.write('<html><head><title>Друк документа</title>')
  printWindow.document.write('<style>@page { size: A4; margin: 12mm; } body { font-family: Arial, sans-serif; }</style>')
  printWindow.document.write('</head><body>')
  printWindow.document.write(printContents)
  printWindow.document.write('</body></html>')
  printWindow.document.close()
  
  setTimeout(() => {
    printWindow.focus()
    printWindow.print()
    printWindow.close()
  }, 500)
}

const handleClose = () => {
  visible.value = false
}

const loadAndRender = async () => {
  if (!props.documentId || !props.modelValue) return
  
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    
    // 1. Fetch the template HTML
    let templateHtml = ''
    if (props.templateId) {
      const templateRes = await axios.get(`/api/v1/print/templates/${props.templateId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      templateHtml = templateRes.data.html_template
    } else {
      // Fallback to default active template
      const templatesRes = await axios.get(`/api/v1/print/templates?document_type=${props.documentType}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (templatesRes.data && templatesRes.data.length > 0) {
        // Find standard default or pick the first one
        const def = templatesRes.data.find(t => t.is_default) || templatesRes.data[0]
        templateHtml = def.html_template
      }
    }
    
    // 2. Fetch the raw print data context
    const dataRes = await axios.get(`/api/v1/print/data/${props.documentType}/${props.documentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const printData = dataRes.data
    
    // 3. Apply monetary Ukrainian conversion mapping
    if (printData.totals) {
      printData.totals.total_in_words = numberToUkrainianWords(printData.totals.total_with_vat)
    }

    // 4. Run substitution
    renderedHtml.value = renderTemplate(templateHtml, printData)
  } catch (error) {
    ElMessage.error('Помилка генерації друкованої форми')
    console.error(error)
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadAndRender()
  }
})
</script>

<style scoped>
.dialog-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 40px;
}

.dialog-header-actions h3 {
  margin: 0;
  font-size: 18px;
}

.print-container {
  background-color: #cbd5e1;
  padding: 20px;
  display: flex;
  justify-content: center;
  min-height: 400px;
}

.document-frame {
  background-color: #ffffff;
  width: 210mm;
  min-height: 297mm;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 20px;
}

.mr-1 {
  margin-right: 4px;
}
</style>
