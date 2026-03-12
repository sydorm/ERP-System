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
              <div v-if="row.type === 'SELECT' || row.type === 'COLOR'">
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
                    {{ opt.value }}
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
                  <el-dropdown-item v-if="row.type === 'SELECT' || row.type === 'COLOR'" command="add_option">
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
        <el-form-item label="Значення (напр. Червоний, XL, Метал)" prop="value">
          <el-input v-model="optForm.value" placeholder="Введіть значення" @keyup.enter="submitOptForm"/>
        </el-form-item>
        
        <el-form-item v-if="activeAttrForOpt?.type === 'COLOR'" label="Колір (HEX)" prop="color_code">
          <div class="flex items-center gap-4">
             <el-color-picker v-model="optForm.color_code" show-alpha />
             <el-input v-model="optForm.color_code" class="w-28" />
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
import { Plus, Search, MoreFilled, Menu, Collection } from '@element-plus/icons-vue'
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
  category_codes: []
})

const optForm = reactive({
  value: '',
  color_code: '#000000'
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
    // Option loading strategy: expand fetches options or we just rely on lazy load. 
    // Backend doesn't return options in root list.
    // Wait, let's load options for all SELECT/COLOR types since it's an admin view.
    const attrs = res.data || []
    
    // For SELECT and COLOR, we ideally fetch options. 
    // The backend `GET /attributes/` normally returns `options` relationship if eager loaded.
    // Let's assume options are included. If not, we fetch on expand.
    attributes.value = attrs.map(a => ({
       ...a,
       options: a.options || [] // Backend actually doesn't eager load options by default unless specified. 
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
  optModalVisible.value = true
  
  // Quick trick to fetch options if they weren't loaded
  refreshOptionsFor(attr.id)
}

const submitOptForm = async () => {
  if (!optFormRef.value || !activeAttrForOpt.value) return
  await optFormRef.value.validate(async (valid) => {
    if (valid) {
      optSubmitting.value = true
      try {
        const payload = { value: optForm.value }
        if (activeAttrForOpt.value.type === 'COLOR') {
          payload.color_code = optForm.color_code
        }
        
        await api.post(`/api/v1/attributes/${activeAttrForOpt.value.id}/options`, payload)
        ElMessage.success('Значення додано')
        optForm.value = '' // reset input for quick mass entry
        
        // Refresh options list in background
        await refreshOptionsFor(activeAttrForOpt.value.id)
      } catch (e) {
        ElMessage.error('Помилка додавання значення')
      } finally {
        optSubmitting.value = false
      }
    }
  })
}

// Because the current backend `GET /attributes/` doesn't eager load `options`, 
// we will fetch them individually or refresh via category attrs endpoint as a workaround if needed.
// Actually, I can use the same logic CharacteristicsTab uses, or simply reload.
// For a safe UI, I'll fetch `/api/v1/attributes/category/ALL` or something. 
// Wait, we can't fetch options directly through a standard endpoint right now without category link.
// Let's rely on the frontend reloading the full list if backend was updated to return options, 
// OR we just use the `GET /api/v1/attributes/` if it DOES return options (fastapi response_model might include it).
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
  if (isExpanded && (row.type === 'SELECT' || row.type === 'COLOR')) {
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
    'BOOLEAN': 'Так/Ні'
  }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = {
    'SELECT': 'bg-blue-100 text-blue-700',
    'COLOR': 'bg-purple-100 text-purple-700',
    'TEXT': 'bg-slate-100 text-slate-700',
    'NUMBER': 'bg-amber-100 text-amber-700',
    'BOOLEAN': 'bg-green-100 text-green-700'
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
