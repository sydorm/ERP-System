<template>
  <div class="dictionaries-container p-6 bg-slate-50 min-h-screen">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 mb-2">Довідники</h1>
        <p class="text-slate-500">Системні налаштування та класифікатори</p>
      </div>
    </div>

    <!-- Horizontal Tabs (Main Sections) -->
    <div class="mb-6 border-b border-slate-200">
      <div class="flex space-x-8">
        <button 
          v-for="section in sections" 
          :key="section.id"
          @click="activeSection = section.id"
          class="pb-4 px-2 text-sm font-semibold transition-colors duration-200 relative"
          :class="activeSection === section.id ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-700'"
        >
          {{ section.name }}
          <div 
            v-if="activeSection === section.id" 
            class="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-600 rounded-t-full"
          ></div>
        </button>
      </div>
    </div>

    <div class="flex gap-6 h-[calc(100vh-200px)]">
      <!-- Left Sidebar (Sub-categories) -->
      <div class="w-64 flex-shrink-0">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div class="p-4 border-b border-slate-100 bg-slate-50/50">
            <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {{ currentSectionName }}
            </h3>
          </div>
          <div class="p-2 space-y-1">
            <template v-if="activeSection === 'numbering'">
              <button
                v-for="seq in sequences"
                :key="seq.id"
                @click="handleSequenceSelect(seq)"
                class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-between"
                :class="activeSequence === seq.id 
                  ? 'bg-indigo-50 text-indigo-700' 
                  : 'text-slate-600 hover:bg-slate-50'"
              >
                <div class="flex flex-col">
                  <span>{{ docTypeLabels[seq.document_type] || seq.document_type }}</span>
                  <span class="text-[10px] text-slate-400 font-mono">
                    {{ seq.prefix }}{{ String(seq.next_number).padStart(seq.padding, '0') }}
                  </span>
                </div>
              </button>
            </template>
            <template v-else>
              <button
                v-for="dict in currentSectionDictionaries"
                :key="dict.code"
                @click="handleDictionarySelect(dict.code)"
                class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-between"
                :class="activeDictionary === dict.code 
                  ? 'bg-indigo-50 text-indigo-700' 
                  : 'text-slate-600 hover:bg-slate-50'"
              >
                <span>{{ dict.name }}</span>
                <span v-if="counts[dict.code] !== undefined" class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
                  {{ counts[dict.code] }}
                </span>
              </button>
            </template>
          </div>

        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
        
        <!-- CUSTOM COMPONENT FOR ATTRIBUTES -->
        <ProductAttributesManager v-if="activeDictionary === 'PRODUCT_ATTRIBUTES'" />

        <!-- NUMBERING UI -->
        <template v-else-if="activeSection === 'numbering'">
          <div class="p-12 max-w-2xl mx-auto w-full" v-if="seqForm.id">
            <div class="mb-10 overflow-hidden rounded-3xl border border-slate-100 bg-slate-50/50 p-8 text-center shadow-inner">
                <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Наступний номер буде:</p>
                <h3 class="text-5xl font-black text-indigo-600 tracking-tight">
                  {{ seqForm.prefix }}{{ String(seqForm.next_number || 1).padStart(seqForm.padding || 5, '0') }}
                </h3>
            </div>

            <el-form label-position="top" class="premium-form">
              <el-row :gutter="32">
                <el-col :span="14">
                  <el-form-item label="Префікс">
                    <el-input v-model="seqForm.prefix" placeholder="напр. ORD-" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :span="10">
                  <el-form-item label="К-сть нулів (Padding)">
                    <el-input-number v-model="seqForm.padding" :min="1" :max="10" class="w-full" size="large" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="Наступний номер лічильника">
                <el-input-number v-model="seqForm.next_number" :min="1" class="w-full" size="large" />
                <div class="mt-4 p-4 rounded-xl bg-orange-50 border border-orange-100 text-xs text-orange-700 flex items-start gap-3">
                  <el-icon class="mt-0.5 text-base"><WarningFilled /></el-icon>
                  <span>
                    <strong>Будьте обережні:</strong> зменшення наступного номера може призвести до дублювання номерів документів, якщо замовлення з такими номерами вже існують у базі.
                  </span>
                </div>
              </el-form-item>

              <div class="mt-12 pt-8 border-t border-slate-100 flex justify-end">
                <el-button type="primary" color="#4f46e5" size="large" class="px-10" @click="saveSequence" :loading="seqSubmitting">
                   Зберегти налаштування
                </el-button>
              </div>
            </el-form>
          </div>
          <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-400 p-12">
            <el-icon :size="64" class="mb-4 opacity-20"><Document /></el-icon>
            <p>Оберіть тип документа зліва для налаштування нумерації</p>
          </div>
        </template>


        <!-- STANDARD DICTIONARY UI -->
        <template v-else>
          <!-- Toolbar -->
          <div class="p-5 border-b border-slate-100 flex justify-between items-center bg-white">
            <div>
              <h2 class="text-lg font-bold text-slate-800">{{ currentDictionary?.name }}</h2>
              <p class="text-xs text-slate-500 mt-1">{{ currentDictionary?.description }}</p>
            </div>
          <div class="flex gap-3">
            <el-input 
              v-model="searchQuery" 
              placeholder="Пошук..." 
              prefix-icon="Search"
              clearable
              class="w-64"
            />
            <el-button type="primary" color="#4f46e5" :icon="Plus" @click="openAddModal">
              Додати
            </el-button>
          </div>
        </div>

        <!-- Data Table -->
        <div class="flex-1 overflow-auto p-5" v-loading="loading">
          <el-table :data="filteredItems" style="width: 100%" class="custom-table">
            <el-table-column type="index" label="#" width="60" />
            <el-table-column prop="name" label="Назва" min-width="200">
              <template #default="{ row }">
                <span class="font-medium text-slate-800">{{ row.name }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="code" label="Код" width="150">
              <template #default="{ row }">
                <code class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">{{ row.code }}</code>
              </template>
            </el-table-column>




            <el-table-column label="Властивості" min-width="150">
              <template #default="{ row }">
                <div class="flex items-center gap-3">
                  <div v-if="row.color" class="flex items-center gap-1">
                    <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: row.color.startsWith('#') ? row.color : `var(--el-color-${row.color})` }"></div>
                    <span class="text-xs text-slate-500">{{ row.color }}</span>
                  </div>
                  <div v-if="row.icon" class="flex items-center gap-1">
                    <span class="text-lg">{{ row.icon }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="is_active" label="Статус" width="120">
              <template #default="{ row }">
                <el-switch 
                  v-model="row.is_active" 
                  active-color="#10b981" 
                  inactive-color="#ef4444"
                  @change="handleToggle(row)"
                  size="small"
                />
              </template>
            </el-table-column>

            <el-table-column fixed="right" width="80" align="center">
              <template #default="{ row }">
                <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
                  <el-button text circle>
                    <el-icon class="text-slate-400 rotate-90"><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">Редагувати</el-dropdown-item>
                      <el-dropdown-item command="delete" :disabled="row.is_fixed" divided class="text-red-500">Видалити</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </div>
        </template>
      </div>
    </div>

    <!-- Generic Modal for Add/Edit -->
    <el-dialog v-model="dialogVisible" :title="isEditMode ? 'Редагувати' : 'Додати'" width="500px" class="premium-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="Назва" prop="name">
          <el-input v-model="form.name" placeholder="Введіть назву" />
        </el-form-item>
        
        <el-form-item label="Стандартна одиниця (Системний код)" prop="code" v-if="activeDictionary === 'UOM'">
          <el-select 
            v-model="form.code" 
            filterable 
            allow-create 
            default-first-option
            placeholder="Оберіть з бібліотеки або впишіть свій" 
            :disabled="isEditMode && form.is_fixed"
            @change="handleUomSelect"
            class="w-full"
          >
            <el-option v-for="uom in standardUOMs" :key="uom.code" :label="uom.label" :value="uom.code" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Системний код" prop="code" v-else>
          <el-input v-model="form.code" placeholder="Унікальний ідентифікатор" :disabled="isEditMode && form.is_fixed" />
        </el-form-item>

        <el-form-item label="Опис (опціонально)">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="Додаткова інформація" />
        </el-form-item>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="Колір">
            <el-color-picker v-model="form.color" />
          </el-form-item>
          <el-form-item label="Іконка (Емодзі або назва)">
            <el-input v-model="form.icon" placeholder="напр. 📞 або Box" />
          </el-form-item>
        </div>





        <!-- Dynamic Fields based on active dictionary -->
        <el-form-item v-if="['LEAD_SOURCE', 'ORDER_STATUS', 'CANCEL_REASON'].includes(activeDictionary)" label="Колір тегу">
          <div class="flex gap-2 mb-2 flex-wrap">
            <div 
              v-for="color in colors" 
              :key="color.value"
              class="w-6 h-6 rounded-full cursor-pointer border-2 transition-transform hover:scale-110"
              :class="[
                `bg-${color.value}`, 
                form.color === color.value ? 'border-indigo-600 scale-110' : 'border-transparent'
              ]"
              @click="form.color = color.value"
            ></div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.is_active" label="Активно" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <el-button @click="dialogVisible = false">Скасувати</el-button>
          <el-button color="#4f46e5" @click="submitForm" :loading="submitting">
            {{ isEditMode ? 'Зберегти' : 'Далі' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Search, MoreFilled, WarningFilled, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import api from '@/api'
import { useDictionaryStore } from '@/stores/dictionary'
import ProductAttributesManager from './ProductAttributesManager.vue'

const dictStore = useDictionaryStore()

// Standard Library
const standardUOMs = [
  { code: 'pcs', label: 'Штуки (pcs)', defaultName: 'шт.' },
  { code: 'm', label: 'Метри (m)', defaultName: 'м' },
  { code: 'm2', label: 'Метри квадратні (m2)', defaultName: 'м.кв.' },
  { code: 'm3', label: 'Метри кубічні (m3)', defaultName: 'м.куб.' },
  { code: 'kg', label: 'Кілограми (kg)', defaultName: 'кг' },
  { code: 'g', label: 'Грами (g)', defaultName: 'г' },
  { code: 'l', label: 'Літри (l)', defaultName: 'л' },
  { code: 'pack', label: 'Упаковки (pack)', defaultName: 'упак.' },
  { code: 'set', label: 'Комплекти (set)', defaultName: 'компл.' }
]

const handleUomSelect = (code) => {
  if (!form.name) {
    const std = standardUOMs.find(u => u.code === code)
    if (std) form.name = std.defaultName
  }
}

// Foundation Structure
const sections = [
  { id: 'finance', name: 'Фінанси' },
  { id: 'commerce', name: 'Комерція' },
  { id: 'inventory', name: 'Номенклатура' },
  { id: 'tags', name: 'Теги та Статуси' },
  { id: 'production', name: 'Виробництво' },
  { id: 'numbering', name: 'Нумерація' }
]


const dictionariesMap = {
  'finance': [
    { code: 'CASH_FLOW_CATEGORY', name: 'Статті доходів і витрат', description: 'Категоризація фінансових транзакцій' },
    { code: 'PAYMENT_METHOD', name: 'Способи оплати', description: 'Методи отримання коштів від клієнтів' },
    { code: 'CURRENCY', name: 'Валюти', description: 'Системні валюти для розрахунків' }
  ],
  'commerce': [
    { code: 'LEAD_SOURCE', name: 'Джерела лідів', description: 'Звідки приходять клієнти' },
    { code: 'CANCEL_REASON', name: 'Причини скасування', description: 'Чому зірвалася угода' },
    { code: 'CLIENT_TYPE', name: 'Типи клієнтів', description: 'Класифікація покупців' },
    { code: 'PRICE_TYPE', name: 'Типи цін', description: 'Оптова, роздрібна, дилерська тощо' },
    { code: 'COMMUNICATION_TYPE', name: 'Види комунікацій', description: 'Телефон, Viber, Telegram тощо' },
    { code: 'CONTACT_RESULT', name: 'Результати контакту', description: 'Не відповів, Думає, Відмовився тощо' }
  ],
  'inventory': [
    { code: 'PRODUCT_CATEGORY', name: 'Категорії товарів', description: 'Деревоподібна структура номенклатури' },
    { code: 'PRODUCT_ATTRIBUTES', name: 'Характеристики товарів', description: 'Кольори, розміри, матеріали' },
    { code: 'UOM', name: 'Одиниці виміру', description: 'Шт., кг., упаковки' },
    { code: 'DELIVERY_METHOD', name: 'Способи доставки', description: 'NP, Укрпошта, Самовивіз тощо' }
  ],
  'tags': [
    { code: 'ORDER_STATUS', name: 'Статуси замовлень', description: 'Життєвий цикл замовлення покупця' },
    { code: 'PAYMENT_STATUS', name: 'Статуси оплати', description: 'Не оплачено, Частково, Оплачено' },
    { code: 'PRIORITY', name: 'Пріоритети', description: 'Терміновість виконання' }
  ],
  'production': [
    { code: 'PRODUCTION_STAGE', name: 'Виробничі етапи', description: 'Зварювання, Фарбування, Збірка тощо' },
    { code: 'ACCRUAL_TYPE', name: 'Типи нарахування ЗП', description: 'Відрядна, Погодинна, Фіксована тощо' },
    { code: 'ROLE_TYPE', name: 'Типи ролей', description: 'Основна, Суміщення' },
    { code: 'EMPLOYEE_STATUS', name: 'Статуси співробітників', description: 'Активний, У відпустці, Звільнений' }
  ]

}

const activeSection = ref('commerce')
const activeDictionary = ref('LEAD_SOURCE')

// Numbering State
const sequences = ref([])
const activeSequence = ref(null)
const seqSubmitting = ref(false)
const seqForm = reactive({
  id: null,
  document_type: '',
  prefix: '',
  next_number: 1,
  padding: 5
})

const docTypeLabels = {
  'order': 'Замовлення покупця',
  'purchase_receipt': 'Прибуткова накладна',
  'sales_invoice': 'Видаткова накладна',
  'transfer': 'Переміщення',
  'inventory': 'Інвентаризація'
}


// Data State
const localItems = ref([])
const counts = ref({})
const loading = ref(false)
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEditMode = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  color: 'blue',
  order: 0,
  is_active: true,
  is_fixed: false
})


const colors = [
  { value: 'blue', hex: '#3b82f6' },
  { value: 'green', hex: '#10b981' },
  { value: 'orange', hex: '#f59e0b' },
  { value: 'red', hex: '#ef4444' },
  { value: 'purple', hex: '#8b5cf6' },
  { value: 'teal', hex: '#14b8a6' },
  { value: 'gray', hex: '#64748b' },
  { value: 'indigo', hex: '#4f46e5' },
  { value: 'pink', hex: '#ec4899' },
  { value: 'rose', hex: '#f43f5e' },
  { value: 'cyan', hex: '#06b6d4' },
  { value: 'amber', hex: '#f59e0b' }
]

const rules = {
  name: [{ required: true, message: 'Введіть назву', trigger: 'blur' }],
  code: [{ required: true, message: 'Введіть код', trigger: 'blur' }]
}

// Computed
const currentSectionName = computed(() => {
  return sections.find(s => s.id === activeSection.value)?.name
})

const currentSectionDictionaries = computed(() => {
  return dictionariesMap[activeSection.value] || []
})

const currentDictionary = computed(() => {
  return currentSectionDictionaries.value.find(d => d.code === activeDictionary.value)
})

const filteredItems = computed(() => {
  if (!searchQuery.value) return localItems.value
  const lower = searchQuery.value.toLowerCase()
  return localItems.value.filter(item => 
    item.name.toLowerCase().includes(lower) || 
    (item.code && item.code.toLowerCase().includes(lower))
  )
})

// Watchers
watch(activeSection, (newSection) => {
  if (newSection === 'numbering') {
    fetchSequences()
  } else if (dictionariesMap[newSection] && dictionariesMap[newSection].length > 0) {
    activeDictionary.value = dictionariesMap[newSection][0].code
  }
})


watch(activeDictionary, () => {
  fetchItems()
  searchQuery.value = ''
})


// API Methods
const fetchCounts = async () => {
  try {
    const response = await api.get('/api/v1/dictionaries/meta/counts')
    counts.value = response.data
  } catch (error) {
    console.error('Failed to load counts')
  }
}

const fetchItems = async () => {
  if (!activeDictionary.value) return
  
  loading.value = true
  try {
    const data = await dictStore.fetchCategory(activeDictionary.value, true) // Force refresh when in settings
    localItems.value = data
  } catch (error) {
    localItems.value = []
  } finally {
    loading.value = false
  }
}

const handleDictionarySelect = (code) => {
  activeDictionary.value = code
}

const openAddModal = () => {
  isEditMode.value = false
  clearForm()
  dialogVisible.value = true
}

const clearForm = () => {
  form.id = null
  form.name = ''
  form.code = ''
  form.description = ''
  form.color = 'blue'
  form.order = 0
  form.is_active = true
  form.is_fixed = false
}


const handleCommand = (cmd, item) => {
  if (cmd === 'edit') {
    isEditMode.value = true
    Object.assign(form, item)
    dialogVisible.value = true
  } else if (cmd === 'delete') {
    handleDelete(item)
  }
}

const handleToggle = async (item) => {
  try {
    const payload = { ...item }
    if (item.id) {
      await api.put(`/api/v1/dictionaries/${item.id}`, payload)
    } else {
      await api.post(`/api/v1/dictionaries`, payload)
    }
    ElMessage.success('Збережено')
  } catch(e) {
    if (item.id) item.is_active = !item.is_active // revert UI if it was a toggle
    ElMessage.error(e.response?.data?.detail || 'Помилка збереження')
  }
}


const fetchSequences = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/document-sequences')
    sequences.value = res.data
    if (sequences.value.length > 0 && !activeSequence.value) {
      handleSequenceSelect(sequences.value[0])
    }
  } catch (error) {
    ElMessage.error('Помилка завантаження лічильників')
  } finally {
    loading.value = false
  }
}

const handleSequenceSelect = (seq) => {
  activeSequence.value = seq.id
  Object.assign(seqForm, seq)
}

const saveSequence = async () => {
  seqSubmitting.value = true
  try {
    const payload = {
      prefix: seqForm.prefix,
      next_number: seqForm.next_number,
      padding: seqForm.padding
    }
    await api.put(`/api/v1/document-sequences/${seqForm.id}`, payload)
    ElMessage.success('Налаштування збережено')
    fetchSequences()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    seqSubmitting.value = false
  }
}

const submitForm = async () => {

  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          name: form.name,
          code: form.code,
          description: form.description, // Include description
          color: form.color,
          order: form.order,
          is_active: form.is_active,
          is_fixed: form.is_fixed, // Include is_fixed
          category: activeDictionary.value
        }

        
        if (isEditMode.value) {
          await api.put(`/api/v1/dictionaries/${form.id}`, payload)
        } else {
          await api.post('/api/v1/dictionaries', payload)
        }
        
        ElMessage.success('Збережено успішно')
        dialogVisible.value = false
        fetchItems()
        fetchCounts()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Видалити запис "${row.name}"?`,
    'Увага',
    { confirmButtonText: 'Видалити', confirmButtonClass: 'el-button--danger', type: 'warning' }
  ).then(async () => {
    try {
      await api.delete(`/api/v1/dictionaries/${row.id}`)
      ElMessage.success('Видалено')
      fetchItems()
      fetchCounts()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || 'Помилка видалення')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchItems()
  fetchCounts()
})
</script>

<style scoped>
/* Tailwind colors mapping for dictionary bg/text classes */
.bg-blue { background-color: #3b82f6; }
.bg-green { background-color: #10b981; }
.bg-orange { background-color: #f59e0b; }
.bg-red { background-color: #ef4444; }
.bg-purple { background-color: #8b5cf6; }
.bg-teal { background-color: #14b8a6; }
.bg-gray { background-color: #64748b; }
.bg-indigo { background-color: #4f46e5; }
.bg-pink { background-color: #ec4899; }
.bg-rose { background-color: #f43f5e; }
.bg-cyan { background-color: #06b6d4; }
.bg-amber { background-color: #fcd34d; }

/* Custom premium styling for generic el-table */
.custom-table {
  --el-table-border-color: transparent !important;
  --el-table-header-bg-color: #f8fafc;
  --el-table-header-text-color: #64748b;
  --el-table-row-hover-bg-color: #f1f5f9;
}

.custom-table :deep(th.el-table__cell) {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.05em;
  padding: 12px 16px;
}

.custom-table :deep(td.el-table__cell) {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.premium-dialog :deep(.el-dialog__header) {
  margin-right: 0;
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.premium-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.premium-dialog :deep(.el-dialog__title) {
  font-weight: 700;
  font-size: 18px;
  color: #1e293b;
}
</style>
