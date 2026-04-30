<template>
  <div class="attributes-manager h-full flex flex-col bg-white">
    <!-- Toolbar -->
    <div class="p-5 border-b border-slate-100 flex justify-between items-center bg-white flex-shrink-0">
      <div>
        <h2 class="text-lg font-bold text-slate-800">Характеристики товарів</h2>
        <p class="text-xs text-slate-500 mt-1">Керування властивостями (колір, розмір, матеріал) та їх значеннями</p>
      </div>
      <div class="flex gap-3">
        <el-input 
          v-model="searchQuery" 
          placeholder="Пошук..." 
          prefix-icon="Search"
          clearable
          class="w-64"
        />
        <el-button color="#4f46e5" :icon="Plus" @click="openAddAttrModal">
          Створити характеристику
        </el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="flex-1 overflow-auto p-5" v-loading="loading">
      <el-table :data="filteredAttributes" style="width: 100%" class="custom-table" row-key="id" @expand-change="handleExpand">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="p-4 bg-slate-50/50 border-t border-b border-slate-100 pl-[60px]">
              <div v-if="row.type === 'SELECT' || row.type === 'COLOR' || row.type === 'DIMENSIONS'">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-semibold text-slate-700">Значення ({{ row.options?.length || 0 }})</h4>
                  <el-button size="small" type="primary" plain @click="openAddOptionModal(row)">
                    + Додати значення
                  </el-button>
                </div>
                
                <div v-if="row.options && row.options.length > 0" class="flex flex-wrap gap-2">
                  <div 
                    v-for="opt in row.options" 
                    :key="opt.id"
                    class="px-3 py-1.5 bg-white border border-slate-200 rounded-md text-sm text-slate-700 flex items-center gap-2 shadow-sm"
                  >
                    <div v-if="row.type === 'COLOR' && opt.color_code" 
                         class="w-3.5 h-3.5 rounded-full border border-slate-200" 
                         :style="{ backgroundColor: opt.color_code }"></div>
                    <span>{{ opt.value }}</span>
                    <el-icon class="ml-1 cursor-pointer text-slate-300 hover:text-red-500 transition-colors" @click.stop="handleDeleteOption(opt, row)">
                      <Close />
                    </el-icon>
                  </div>
                </div>
                <div v-else class="text-sm text-slate-400 italic">
                  Ще немає доданих значень. Натисніть "Додати значення", щоб створити перший варіант.
                </div>
              </div>
              <div v-else class="text-sm text-slate-500 py-2">
                Цей тип характеристики ({{ getTypeName(row.type) }}) не потребує наперед заданих значень полів. Значення вписуються вручну в картці товару.
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="Назва" min-width="200">
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <el-icon v-if="row.icon" class="text-slate-400 text-lg"><component :is="row.icon" /></el-icon>
              <span class="font-medium text-slate-800">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="Тип" width="130">
          <template #default="{ row }">
            <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium" :class="getTypeClass(row.type)">
              {{ getTypeName(row.type) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="generates_variant" label="Генерує варіант" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="row.generates_variant ? 'success' : 'info'" size="small">
              {{ row.generates_variant ? '✅ Так' : '❌ Ні' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Категорії" min-width="180">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag v-if="!row.category_codes || row.category_codes.length === 0" size="small" type="info">Всі</el-tag>
              <el-tag v-else v-for="code in row.category_codes.slice(0, 3)" :key="code" size="small" class="mb-1">
                {{ getCategoryName(code) }}
              </el-tag>
              <el-tooltip v-if="row.category_codes && row.category_codes.length > 3" :content="getCategoryNames(row.category_codes)" placement="top">
                <el-tag size="small" type="info" class="mb-1">+{{ row.category_codes.length - 3 }}</el-tag>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="Опис" min-width="150">
          <template #default="{ row }">
            <span class="text-xs text-slate-500 truncate block max-w-xs" :title="row.description || ''">{{ row.description || '—' }}</span>
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
                  <el-dropdown-item v-if="row.type === 'SELECT' || row.type === 'COLOR' || row.type === 'DIMENSIONS'" command="add_option">
                     Додати значення
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided class="text-red-500">Видалити</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Modal: Add/Edit Attribute -->
    <el-dialog v-model="attrModalVisible" :title="isEditMode ? 'Редагувати характеристику' : 'Створити характеристику'" width="500px">
      <el-form ref="attrFormRef" :model="attrForm" :rules="attrRules" label-position="top">
        <el-form-item label="Назва (напр. Колір, Розмір)" prop="name">
          <el-input v-model="attrForm.name" placeholder="Введіть назву" />
        </el-form-item>
        
        <el-form-item label="Тип значення" prop="type">
          <el-select v-model="attrForm.type" placeholder="Оберіть тип" class="w-full">
            <el-option label="Випадаючий список (з наперед заданих)" value="SELECT" />
            <el-option label="Колір (список з кольоровими іконками)" value="COLOR" />
            <el-option label="Довільний текст" value="TEXT" />
            <el-option label="Число" value="NUMBER" />
            <el-option label="Так / Ні" value="BOOLEAN" />
            <el-option label="Розміри (Ш × В, мм)" value="DIMENSIONS" />
          </el-select>
          <div class="text-xs text-slate-400 mt-1">
            Для 'Списку' і 'Кольору' ви зможете додати варіанти значень після збереження.
          </div>
        </el-form-item>

        <el-form-item label="Категорії">
          <el-select v-model="attrForm.category_codes" multiple filterable placeholder="Всюди (якщо пусто)" class="w-full">
             <el-option v-for="cat in categories" :key="cat.code" :label="cat.name" :value="cat.code" />
          </el-select>
        </el-form-item>

        <el-form-item label="Генерує варіант SKU" prop="generates_variant">
          <el-switch v-model="attrForm.generates_variant" active-text="Так" inactive-text="Ні" />
          <div class="text-xs text-slate-500 mt-1">
            Якщо ввімкнено, ця характеристика буде використовуватись для автоматичної генерації комбінацій (варіантів) товару.
          </div>
        </el-form-item>

        <div v-if="attrForm.type === 'SELECT' || attrForm.type === 'DIMENSIONS'" class="bg-indigo-50/50 p-4 rounded-lg mb-4 border border-indigo-100">
          <h4 class="text-sm font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            <el-icon><Operation /></el-icon> Налаштування конфігуратора (BOM)
          </h4>
          
          <el-form-item label="Дозволити ручне введення" prop="allow_manual_input" class="mb-3">
            <el-switch v-model="attrForm.allow_manual_input" active-text="Так" inactive-text="Ні" />
            <div class="text-xs text-slate-500 mt-1">
              Якщо ввімкнено, у замовленні можна буде вписати власний розмір (напр. "95"), замість вибору зі списку.
            </div>
          </el-form-item>

          <el-form-item label="Впливає на габарит (BOM)" prop="mapped_dimension" class="mb-0">
            <el-select v-model="attrForm.mapped_dimension" placeholder="Не впливає" clearable class="w-full">
              <el-option label="Немає (Просто текст)" value="" />
              <el-option label="Довжина (L)" value="length_mm" />
              <el-option label="Ширина (W)" value="width_mm" />
              <el-option label="Висота (H)" value="height_mm" />
            </el-select>
            <div class="text-xs text-slate-500 mt-1">
              Значення цієї характеристики автоматично підставиться у Розумний Калькулятор замість базового габариту товару.
            </div>
          </el-form-item>

          <el-form-item v-if="attrForm.type === 'DIMENSIONS'" label="Формат варіанту" prop="dimension_format" class="mt-3 mb-0">
            <el-input v-model="attrForm.dimension_format" placeholder="{width}×{height}" />
            <div class="text-xs text-slate-500 mt-1">
              Як буде виглядати назва характеристики (напр. {width}×{height} або {width}x{height})
            </div>
          </el-form-item>
        </div>

        <el-form-item label="Опис (опціонально)">
          <el-input v-model="attrForm.description" type="textarea" :rows="2" placeholder="Для чого ця характеристика?" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <el-button @click="attrModalVisible = false">Скасувати</el-button>
          <el-button color="#4f46e5" @click="submitAttrForm" :loading="submitting">{{ isEditMode ? 'Зберегти' : 'Створити' }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Modal: Add Option (Value) -->
    <el-dialog v-model="optModalVisible" :title="`Додати значення: ${activeAttrForOpt?.name}`" width="450px">
      <el-form ref="optFormRef" :model="optForm" :rules="optRules" label-position="top" @submit.prevent>
        <el-form-item v-if="activeAttrForOpt?.type !== 'DIMENSIONS'" label="Значення (напр. Червоний, XL, Метал)" prop="value">
          <el-input v-model="optForm.value" placeholder="Введіть значення" @keyup.enter="submitOptForm"/>
        </el-form-item>

        <el-form-item v-else label="Розміри (Ш × В, мм)">
          <div class="flex items-center gap-2">
            <el-input-number v-model="optForm.w" :min="0" :precision="0" :controls="false" placeholder="Ширина" class="w-full" @keyup.enter="submitOptForm" />
            <span class="text-slate-400 font-bold">×</span>
            <el-input-number v-model="optForm.h" :min="0" :precision="0" :controls="false" placeholder="Висота" class="w-full" @keyup.enter="submitOptForm" />
            <span class="text-slate-400">мм</span>
          </div>
        </el-form-item>
        
        <el-form-item v-if="activeAttrForOpt?.type === 'COLOR'" label="Колір (HEX)" prop="color_code">
          <div class="flex items-center gap-4">
             <el-color-picker v-model="optForm.color_code" show-alpha />
             <el-input v-model="optForm.color_code" class="w-28" @keyup.enter="submitOptForm" />
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <el-button @click="optModalVisible = false">Закрити</el-button>
          <el-button color="#4f46e5" @click="submitOptForm" :loading="optSubmitting">Додати</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Search, MoreFilled, Menu, Collection, Operation, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const query = ref('')

const attributes = ref([])
const categories = ref([])
const loading = ref(false)
const searchQuery = ref('')
const expandedRows = ref(new Set())

// Modals state
const attrModalVisible = ref(false)
const isEditMode = ref(false)
const submitting = ref(false)
const attrFormRef = ref(null)

const optModalVisible = ref(false)
const optSubmitting = ref(false)
const optFormRef = ref(null)
const activeAttrForOpt = ref(null)

// Forms
const attrForm = reactive({
  id: null,
  name: '',
  type: 'SELECT',
  description: '',
  category_codes: [],
  allow_manual_input: false,
  mapped_dimension: '',
  dimension_format: '{width}×{height}',
  generates_variant: true
})

const optForm = reactive({
  value: '',
  color_code: '#4f46e5',
  w: null,
  h: null
})

// Rules
const attrRules = {
  name: [{ required: true, message: 'Обов\'язкове поле', trigger: 'blur' }],
  type: [{ required: true, message: 'Оберіть тип', trigger: 'change' }]
}

const optRules = {
  value: [{ required: true, message: 'Обов\'язкове поле', trigger: 'blur' }]
}

// Computed
const filteredAttributes = computed(() => {
  if (!searchQuery.value) return attributes.value
  const q = searchQuery.value.toLowerCase()
  return attributes.value.filter(a => a.name.toLowerCase().includes(q))
})

// Lifecycle
onMounted(() => {
  fetchCategories()
  fetchAttributes()
})

// Methods
const fetchCategories = async () => {
    try {
        const res = await api.get('/api/v1/dictionaries/PRODUCT_CATEGORY')
        categories.value = res.data
    } catch (e) {
        console.error("Failed to load categories", e)
    }
}

const getCategoryName = (code) => {
    const cat = categories.value.find(c => c.code === code)
    return cat ? cat.name : code
}

const getCategoryNames = (codes) => {
    return codes.map(c => getCategoryName(c)).join(', ')
}

const fetchAttributes = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/attributes')
    const attrs = res.data || []
    attributes.value = attrs.map(a => ({
       ...a,
       options: a.options || []
    }))
  } catch (e) {
    ElMessage.error('Не вдалося завантажити характеристики')
  } finally {
    loading.value = false
  }
}

// Attribute Modal
const openAddAttrModal = () => {
  isEditMode.value = false
  attrForm.id = null
  attrForm.name = ''
  attrForm.type = 'SELECT'
  attrForm.description = ''
  attrForm.category_codes = []
  attrForm.allow_manual_input = false
  attrForm.mapped_dimension = null
  attrForm.generates_variant = true
  attrModalVisible.value = true
}

const submitAttrForm = async () => {
  if (!attrFormRef.value) return
  await attrFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        let icon = 'Menu'
        if (attrForm.type === 'COLOR') icon = 'Collection'
        
        if (isEditMode.value) {
            await api.put(`/api/v1/attributes/${attrForm.id}`, { ...attrForm, icon })
            ElMessage.success('Характеристику оновлено')
        } else {
            await api.post('/api/v1/attributes', { ...attrForm, icon })
            ElMessage.success('Характеристику створено')
        }
        
        attrModalVisible.value = false
        fetchAttributes()
      } catch (e) {
        ElMessage.error('Помилка збереження')
      } finally {
        submitting.value = false
      }
    }
  })
}

// Option Modal
const openAddOptionModal = (attr) => {
  activeAttrForOpt.value = attr
  optForm.value = ''
  optForm.color_code = '#4f46e5'
  optForm.w = null
  optForm.h = null
  optModalVisible.value = true
  
  refreshOptionsFor(attr.id)
}

const submitOptForm = async () => {
  if (!optFormRef.value || !activeAttrForOpt.value) return

  if (activeAttrForOpt.value.type === 'DIMENSIONS') {
    if (!optForm.w || !optForm.h) {
        ElMessage.warning('Вкажіть ширину та висоту')
        return
    }
    const fmt = activeAttrForOpt.value.dimension_format || '{width}×{height}'
    optForm.value = fmt.replace('{width}', optForm.w).replace('{height}', optForm.h)
  }

  await optFormRef.value.validate(async (valid) => {
    if (valid) {
      optSubmitting.value = true
      try {
        const payload = { value: optForm.value }
        if (activeAttrForOpt.value.type === 'COLOR') {
          payload.color_code = optForm.color_code
        }
        if (activeAttrForOpt.value.type === 'DIMENSIONS') {
          payload.width = optForm.w
          payload.height = optForm.h
        }
        
        await api.post(`/api/v1/attributes/${activeAttrForOpt.value.id}/options`, payload)
        ElMessage.success('Значення додано')
        
        // Reset form for quick mass entry
        optForm.value = ''
        optForm.w = null
        optForm.h = null
        optForm.color_code = '#4f46e5'
        
        await refreshOptionsFor(activeAttrForOpt.value.id)
      } catch (e) {
        ElMessage.error('Помилка додавання значення')
      } finally {
        optSubmitting.value = false
      }
    }
  })
}

const handleDeleteOption = async (option, attribute) => {
  try {
    await ElMessageBox.confirm(
      `Видалити значення "${option.value}"?`,
      'Видалення значення',
      {
        confirmButtonText: 'Видалити',
        confirmButtonClass: 'el-button--danger',
        cancelButtonText: 'Скасувати',
        type: 'warning'
      }
    )
    
    await api.delete(`/api/v1/attributes/options/${option.id}`)
    ElMessage.success('Значення видалено')
    await refreshOptionsFor(attribute.id)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('Помилка видалення значення')
    }
  }
}

const refreshOptionsFor = async (attrId) => {
    const res = await api.get('/api/v1/attributes')
    const fresh = res.data.find(a => a.id === attrId)
    if (fresh) {
        const idx = attributes.value.findIndex(a => a.id === attrId)
        if (idx !== -1) {
            attributes.value[idx].options = fresh.options || []
        }
    }
}

const handleExpand = async (row, expandedRowsArr) => {
  const isExpanded = expandedRowsArr.includes(row)
  if (isExpanded && (row.type === 'SELECT' || row.type === 'COLOR' || row.type === 'DIMENSIONS')) {
    await refreshOptionsFor(row.id)
  }
}

// Actions
const handleCommand = (cmd, row) => {
  if (cmd === 'add_option') {
    openAddOptionModal(row)
  } else if (cmd === 'edit') {
    isEditMode.value = true
    Object.assign(attrForm, row)
    if (!attrForm.category_codes) attrForm.category_codes = []
    if (attrForm.allow_manual_input === undefined) attrForm.allow_manual_input = false
    if (attrForm.generates_variant === undefined) attrForm.generates_variant = true
    attrModalVisible.value = true
  } else if (cmd === 'delete') {
    ElMessageBox.confirm('Ви впевнені, що хочете видалити характеристику і всі її значення?', 'Видалити', { type: 'warning' })
      .then(async () => {
        try {
          await api.delete(`/api/v1/attributes/${row.id}`)
          ElMessage.success('Видалено')
          fetchAttributes()
        } catch {
          ElMessage.error('Помилка видалення')
        }
      }).catch(() => {})
  }
}

// Formatting
const getTypeName = (type) => {
  const map = {
    'TEXT': 'Текст',
    'SELECT': 'Список',
    'COLOR': 'Колір',
    'NUMBER': 'Число',
    'BOOLEAN': 'Так/Ні',
    'DIMENSIONS': 'Розміри'
  }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = {
    'SELECT': 'bg-blue-100 text-blue-700',
    'COLOR': 'bg-purple-100 text-purple-700',
    'TEXT': 'bg-slate-100 text-slate-700',
    'NUMBER': 'bg-amber-100 text-amber-700',
    'BOOLEAN': 'bg-green-100 text-green-700',
    'DIMENSIONS': 'bg-indigo-100 text-indigo-700'
  }
  return map[type] || 'bg-slate-100 text-slate-700'
}
</script>

<style scoped>
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

.custom-table :deep(.el-table__expanded-cell) {
  padding: 0 !important;
  background: #f8fafc !important;
}
</style>
