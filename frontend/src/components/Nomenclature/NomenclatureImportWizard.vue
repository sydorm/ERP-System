<template>
  <el-dialog
    :model-value="visible"
    width="1120px"
    class="nomenclature-import-dialog"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <template #header>
      <div class="import-header">
        <div>
          <span class="import-kicker">Імпорт номенклатури</span>
          <h2>Excel / CSV майстер</h2>
          <p>Завантаження, зіставлення колонок, перевірка і контрольований імпорт товарів.</p>
        </div>
        <button class="template-btn" type="button" @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          Завантажити шаблон Excel
        </button>
      </div>
    </template>

    <div class="import-wizard">
      <el-steps :active="activeStep" finish-status="success" class="import-steps">
        <el-step title="Файл" />
        <el-step title="Лист" />
        <el-step title="Зіставлення" />
        <el-step title="Перевірка" />
        <el-step title="Імпорт" />
        <el-step title="Результат" />
      </el-steps>

      <div class="wizard-content-scroll">
        <!-- Step 0: Upload -->
        <section v-if="activeStep === 0" class="wizard-panel upload-panel">
          <div class="upload-card" @click="fileInput?.click()" @dragover.prevent @drop.prevent="handleDrop">
            <input ref="fileInput" type="file" accept=".xlsx,.csv" hidden @change="handleFileSelect" />
            <div class="upload-icon"><el-icon><UploadFilled /></el-icon></div>
            <h3>Завантажте Excel або CSV файл</h3>
            <p>Підтримуються `.xlsx` та `.csv`, до 10 MB і до 5000 рядків.</p>
            <button class="primary-soft-btn" type="button">Обрати файл</button>
            <span v-if="selectedFile" class="selected-file">{{ selectedFile.name }}</span>
          </div>
        </section>

        <!-- Step 1: Sheet Selection -->
        <section v-else-if="activeStep === 1" class="wizard-panel">
          <div class="panel-title-row">
            <div>
              <h3>Вибір листа Excel</h3>
              <p>Якщо в файлі кілька листів, оберіть той, де знаходиться номенклатура.</p>
            </div>
          </div>
          <el-select v-model="selectedSheet" class="sheet-select" placeholder="Оберіть лист" @change="reloadPreview">
            <el-option v-for="sheet in sheets" :key="sheet" :label="sheet" :value="sheet" />
          </el-select>
        </section>

        <!-- Step 2: Mapping & Preview -->
        <section v-else-if="activeStep === 2" class="wizard-panel mapping-preview-panel">
          <div class="panel-title-row">
            <div>
              <h3>Зіставлення та перегляд</h3>
              <p>Оберіть відповідну колонку над кожним стовпцем таблиці. Рядки будуть імпортовані згідно з вашим вибором.</p>
            </div>
            <div class="import-mode-compact">
              <el-select v-model="importMode" size="small" class="mode-select">
                <el-option label="Створити та оновити" value="create_update" />
                <el-option label="Тільки створити нові" value="create_only" />
                <el-option label="Тільки оновити існуючі" value="update_only" />
              </el-select>
            </div>
          </div>

          <div class="table-container-modern">
            <el-table :data="previewRows" height="520" border class="preview-table mapping-table">
              <el-table-column label="#" prop="_row_number" width="60" fixed />
              
              <el-table-column
                v-for="header in headers"
                :key="header"
                :prop="header"
                min-width="220"
              >
                <template #header>
                  <div class="column-mapping-header">
                    <span class="excel-col-name">{{ header }}</span>
                    <el-select
                      v-model="reverseMapping[header]"
                      placeholder="Не імпортувати"
                      clearable
                      filterable
                      size="small"
                      class="mapping-select"
                      @change="onColumnMapChange(header, $event)"
                    >
                      <el-option
                        v-for="field in fields"
                        :key="field.key"
                        :label="field.label"
                        :value="field.key"
                        :disabled="isFieldMapped(field.key, header)"
                      >
                        <div class="field-option">
                          <span>{{ field.label }}</span>
                          <el-tag v-if="field.required" size="small" type="danger" effect="plain">REQ</el-tag>
                        </div>
                      </el-option>
                    </el-select>
                  </div>
                </template>
                <template #default="{ row }">
                  <div class="cell-preview">{{ row[header] }}</div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="mapping-footer-options">
            <div class="options-group">
              <span class="group-label">Пошук дублікатів:</span>
              <el-checkbox-group v-model="duplicateKeys" size="small">
                <el-checkbox label="sku">Артикул</el-checkbox>
                <el-checkbox label="name">Назва</el-checkbox>
              </el-checkbox-group>
            </div>
            <div class="options-group">
              <el-checkbox v-model="options.create_missing_categories" size="small">Створювати категорії</el-checkbox>
              <el-checkbox v-model="options.normalize_units" size="small">Нормалізувати одиниці</el-checkbox>
            </div>
          </div>
        </section>

        <!-- Step 3: Validation -->
        <section v-else-if="activeStep === 3" class="wizard-panel">
          <div class="panel-title-row">
            <div>
              <h3>Перевірка даних</h3>
              <p>Ми перевірили ваші дані на відповідність типам та наявність обов'язкових полів.</p>
            </div>
            <button class="primary-soft-btn" type="button" @click="validateImport" :disabled="loading">Перевірити ще раз</button>
          </div>
          <div class="summary-grid">
            <div><b>{{ validationSummary.create || 0 }}</b><span>буде створено</span></div>
            <div><b>{{ validationSummary.update || 0 }}</b><span>буде оновлено</span></div>
            <div><b>{{ validationSummary.skip || 0 }}</b><span>пропущено</span></div>
            <div><b>{{ validationSummary.warnings || 0 }}</b><span>warnings</span></div>
            <div class="danger"><b>{{ validationSummary.errors || 0 }}</b><span>errors</span></div>
          </div>
          <el-table :data="validationRows" height="380" border class="preview-table">
            <el-table-column prop="row_number" label="Рядок" width="80" />
            <el-table-column prop="action" label="Дія" width="120">
              <template #default="{ row }">
                <span class="action-chip" :class="row.action">{{ actionLabel(row.action) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="Назва" min-width="180" />
            <el-table-column prop="sku" label="Артикул" min-width="120" />
            <el-table-column label="Повідомлення" min-width="320">
              <template #default="{ row }">
                <div class="message-stack">
                  <span v-for="err in row.errors" :key="err" class="msg error">{{ err }}</span>
                  <span v-for="warn in row.warnings" :key="warn" class="msg warn">{{ warn }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <!-- Step 4: Confirmation -->
        <section v-else-if="activeStep === 4" class="wizard-panel confirm-panel">
          <h3>Підтвердження імпорту</h3>
          <p>Імпорт буде виконано тільки для рядків без критичних помилок. Існуючі товари будуть оновлені згідно з обраним режимом.</p>
          <div class="confirm-card">
            <span>Файл</span><b>{{ selectedFile?.name }}</b>
            <span>Лист</span><b>{{ selectedSheet }}</b>
            <span>Рядків до обробки</span><b>{{ rowCount }}</b>
          </div>
        </section>

        <!-- Step 5: Result -->
        <section v-else class="wizard-panel result-panel">
          <div class="result-icon">✓</div>
          <h3>Імпорт завершено</h3>
          <div class="summary-grid result">
            <div><b>{{ importResult.created || 0 }}</b><span>створено</span></div>
            <div><b>{{ importResult.updated || 0 }}</b><span>оновлено</span></div>
            <div><b>{{ importResult.skipped || 0 }}</b><span>пропущено</span></div>
            <div class="danger"><b>{{ importResult.errors || 0 }}</b><span>помилки</span></div>
          </div>
          <button v-if="importResult.report_id" class="template-btn" type="button" @click="downloadReport">
            <el-icon><Download /></el-icon>
            Завантажити звіт помилок
          </button>
        </section>
      </div>

      <div class="wizard-footer">
        <button class="ghost-btn" type="button" @click="handleClose">Закрити</button>
        <div>
          <button v-if="activeStep > 0 && activeStep < 5" class="ghost-btn" type="button" @click="activeStep--">Назад</button>
          <button class="primary-btn" type="button" :disabled="loading || !canGoNext" @click="nextStep">
            {{ nextButtonText }}
          </button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible', 'completed'])

const activeStep = ref(0)
const loading = ref(false)
const fileInput = ref(null)
const selectedFile = ref(null)
const importId = ref(null)
const sheets = ref([])
const selectedSheet = ref('')
const headers = ref([])
const previewRows = ref([])
const rowCount = ref(0)
const fields = ref([])
const mapping = reactive({})
const importMode = ref('create_update')
const duplicateKeys = ref(['sku', 'name', 'internal_code', 'barcode'])
const options = reactive({
  create_missing_categories: false,
  normalize_units: true,
  create_missing_suppliers: false,
})
const validationSummary = ref({})
const validationRows = ref([])
const importResult = ref({})

watch(() => props.visible, (value) => {
  if (value) resetWizard()
})

const reverseMapping = reactive({})

const onColumnMapChange = (header, fieldKey) => {
  if (fieldKey) {
    Object.keys(reverseMapping).forEach(h => {
      if (h !== header && reverseMapping[h] === fieldKey) {
        reverseMapping[h] = undefined
      }
    })
  }
  
  Object.keys(mapping).forEach(key => delete mapping[key])
  Object.entries(reverseMapping).forEach(([h, key]) => {
    if (key) mapping[key] = h
  })
}

const isFieldMapped = (fieldKey, currentHeader) => {
  return Object.entries(reverseMapping).some(([h, key]) => key === fieldKey && h !== currentHeader)
}

const canGoNext = computed(() => {
  if (activeStep.value === 0) return Boolean(importId.value)
  if (activeStep.value === 2) return Boolean(mapping.name && mapping.unit_of_measure)
  if (activeStep.value === 3) return Boolean(validationRows.value.length)
  if (activeStep.value === 5) return false
  return true
})

const nextButtonText = computed(() => {
  if (activeStep.value === 0) return 'Далі'
  if (activeStep.value === 1) return 'До таблиці'
  if (activeStep.value === 2) return 'Перевірити дані'
  if (activeStep.value === 3) return 'До підтвердження'
  if (activeStep.value === 4) return 'Запустити імпорт'
  if (activeStep.value === 5) return 'Готово'
  return 'Далі'
})

const resetWizard = () => {
  activeStep.value = 0
  selectedFile.value = null
  importId.value = null
  sheets.value = []
  selectedSheet.value = ''
  headers.value = []
  previewRows.value = []
  rowCount.value = 0
  fields.value = []
  Object.keys(mapping).forEach(key => delete mapping[key])
  Object.keys(reverseMapping).forEach(key => delete reverseMapping[key])
  validationSummary.value = {}
  validationRows.value = []
  importResult.value = {}
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files?.[0]
  if (file) uploadFile(file)
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) uploadFile(file)
}

const uploadFile = async (file, sheet = null) => {
  selectedFile.value = file
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (sheet) formData.append('sheet', sheet)
    const res = await api.post('/api/v1/nomenclature/import/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    applyPreview(res.data)
    ElMessage.success('Файл прочитано')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Не вдалося прочитати файл')
  } finally {
    loading.value = false
  }
}

const applyPreview = (data) => {
  importId.value = data.import_id
  sheets.value = data.sheets || []
  selectedSheet.value = data.selected_sheet
  headers.value = data.headers || []
  previewRows.value = data.rows || []
  rowCount.value = data.row_count || 0
  fields.value = data.fields || []
  
  Object.keys(mapping).forEach(key => delete mapping[key])
  Object.keys(reverseMapping).forEach(key => delete reverseMapping[key])
  
  Object.entries(data.suggested_mapping || {}).forEach(([key, value]) => { 
    mapping[key] = value 
    reverseMapping[value] = key
  })
}

const reloadPreview = () => {
  if (selectedFile.value) uploadFile(selectedFile.value, selectedSheet.value)
}

const validateImport = async () => {
  loading.value = true
  try {
    const res = await api.post('/api/v1/nomenclature/import/validate', {
      import_id: importId.value,
      mapping,
      options,
      mode: importMode.value,
      duplicate_keys: duplicateKeys.value,
    })
    validationSummary.value = res.data.summary || {}
    validationRows.value = res.data.rows || []
    ElMessage.success('Перевірку завершено')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка перевірки даних')
  } finally {
    loading.value = false
  }
}

const executeImport = async () => {
  loading.value = true
  try {
    const res = await api.post('/api/v1/nomenclature/import/execute', {
      import_id: importId.value,
      mode: importMode.value,
    })
    importResult.value = res.data
    activeStep.value = 5
    emit('completed')
    ElMessage.success('Імпорт завершено')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка імпорту')
  } finally {
    loading.value = false
  }
}

const nextStep = async () => {
  if (activeStep.value === 2) {
    await validateImport()
    if (validationRows.value.length) activeStep.value = 3
    return
  }
  if (activeStep.value === 4) {
    await executeImport()
    return
  }
  activeStep.value += 1
}

const downloadBlob = async (url, filename) => {
  const res = await api.get(url, { responseType: 'blob' })
  const blobUrl = URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(blobUrl)
}

const downloadTemplate = async () => {
  try {
    await downloadBlob('/api/v1/nomenclature/import/template', 'nomenclature_import_template.xlsx')
  } catch {
    ElMessage.error('Не вдалося завантажити шаблон')
  }
}

const downloadReport = async () => {
  if (importResult.value.report_id) {
    try {
      await downloadBlob(`/api/v1/nomenclature/import/report/${importResult.value.report_id}`, `nomenclature_import_report_${importResult.value.report_id}.csv`)
    } catch {
      ElMessage.error('Не вдалося завантажити звіт')
    }
  }
}

const actionLabel = (action) => ({
  create: 'Створити',
  update: 'Оновити',
  error: 'Помилка',
}[action] || action)
</script>

<style scoped>
:deep(.nomenclature-import-dialog) {
  display: flex !important;
  flex-direction: column;
  max-height: 90vh;
  height: 800px;
  margin: 5vh auto !important;
  border-radius: 24px;
  overflow: hidden;
}

:deep(.nomenclature-import-dialog .el-dialog__header) {
  padding: 0;
  margin: 0;
}

:deep(.nomenclature-import-dialog .el-dialog__body) {
  flex: 1;
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.import-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 24px 32px;
  background: #fff;
  border-bottom: 1px solid #F1F5F9;
}

.import-kicker {
  color: #1463FF;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.import-header h2 {
  margin: 4px 0;
  color: #0F172A;
  font-size: 22px;
  font-weight: 850;
}

.import-header p,
.panel-title-row p,
.confirm-panel p {
  margin: 0;
  color: #64748B;
  font-size: 13px;
}

.template-btn,
.primary-soft-btn,
.primary-btn,
.ghost-btn {
  height: 40px;
  padding: 0 18px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  background: #FFFFFF;
  color: #1463FF;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn {
  color: #FFFFFF;
  border: none;
  background: linear-gradient(135deg, #1463FF 0%, #0047D1 100%);
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.2);
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(20, 99, 255, 0.3);
}

.primary-btn:disabled {
  opacity: .55;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.ghost-btn {
  color: #64748B;
}

.import-wizard {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
}

.import-steps {
  padding: 20px 32px;
  background: #F8FAFC;
  border-bottom: 1px solid #F1F5F9;
}

.wizard-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  min-height: 0;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.mapping-preview-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.table-container-modern {
  flex: 1;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #E2E8F0;
  background: #fff;
  min-height: 300px;
}

.column-mapping-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: #F8FAFC;
}

.excel-col-name {
  font-size: 11px;
  font-weight: 800;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.mapping-select {
  width: 100%;
}

:deep(.mapping-select .el-input__wrapper) {
  background: #fff !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
  border-radius: 10px !important;
}

.cell-preview {
  font-size: 13px;
  color: #1E293B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 10px;
}

.mapping-footer-options {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: #F8FAFC;
  border-radius: 16px;
  border: 1px solid #F1F5F9;
  margin-top: 12px;
}

.options-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748B;
}

.import-mode-compact {
  display: flex;
  align-items: center;
}

.mode-select {
  width: 180px;
}

.wizard-panel {
  min-height: 380px;
}

.upload-panel {
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-card {
  width: min(620px, 100%);
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  border: 2px dashed #CBD5E1;
  border-radius: 24px;
  background: #F8FAFC;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-card:hover {
  border-color: #1463FF;
  background: #EFF6FF;
  transform: translateY(-2px);
}

.upload-icon {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: #fff;
  color: #1463FF;
  font-size: 32px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.upload-card h3,
.wizard-panel h3 {
  margin: 0;
  color: #0F172A;
  font-weight: 850;
}

.selected-file {
  padding: 6px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #E2E8F0;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
}

.panel-title-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.sheet-select {
  width: 360px;
}

.preview-table {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #F1F5F9;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.summary-grid div,
.confirm-card {
  padding: 16px;
  border: 1px solid #F1F5F9;
  border-radius: 18px;
  background: #fff;
  text-align: center;
}

.summary-grid b {
  display: block;
  color: #0F172A;
  font-size: 24px;
  font-weight: 900;
}

.summary-grid span {
  color: #64748B;
  font-size: 12px;
  font-weight: 600;
}

.summary-grid .danger b {
  color: #EF4444;
}

.action-chip,
.msg {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 800;
}

.action-chip.create { background: #ECFDF5; color: #059669; }
.action-chip.update { background: #EFF6FF; color: #1463FF; }
.action-chip.error { background: #FEF2F2; color: #EF4444; }

.confirm-panel,
.result-panel {
  text-align: center;
  padding: 40px 0;
}

.confirm-card {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px 18px;
  min-width: 480px;
  text-align: left;
  margin: 0 auto;
}

.confirm-card span {
  color: #64748B;
  font-weight: 600;
}

.result-icon {
  width: 72px;
  height: 72px;
  display: grid;
  place-items: center;
  border-radius: 24px;
  background: #ECFDF5;
  color: #059669;
  font-size: 36px;
  font-weight: 950;
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.1);
  margin: 0 auto 20px;
}

.summary-grid.result {
  width: 100%;
  max-width: 800px;
  grid-template-columns: repeat(4, 1fr);
  margin: 20px auto;
}

.message-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.msg.error { background: #FEF2F2; color: #EF4444; }
.msg.warn { background: #FFF7ED; color: #B45309; }

.wizard-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 32px;
  background: #fff;
  border-top: 1px solid #F1F5F9;
}
</style>
