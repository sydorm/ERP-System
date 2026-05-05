<template>
  <div class="attributes-manager h-full flex flex-col bg-white">
    <!-- Toolbar -->
    <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-gradient-to-r from-white to-slate-50/50 flex-shrink-0">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <h2 class="text-xl font-black text-slate-800 tracking-tight">Характеристики товарів</h2>
          <div class="w-1.5 h-1.5 rounded-full bg-indigo-400"></div>
        </div>
        <p class="text-sm text-slate-500 font-medium">Керування властивостями (колір, розмір, матеріал) та їх значеннями</p>
      </div>
      <div class="flex gap-4">
        <el-input 
          v-model="searchQuery" 
          placeholder="Пошук за назвою..." 
          prefix-icon="Search"
          clearable
          class="w-72 premium-input"
        />
        <el-button type="primary" class="premium-button-indigo" :icon="Plus" @click="openAddAttrModal">
          Створити характеристику
        </el-button>
      </div>
    </div>


    <!-- Data Table -->
    <div class="flex-1 overflow-auto p-5" v-loading="loading">
      <el-table :data="filteredAttributes" style="width: 100%" class="custom-table high-density" row-key="id" @expand-change="handleExpand">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="p-6 bg-slate-50/80 border-t border-b border-slate-100 pl-[60px] shadow-inner">
              <div v-if="row.type === 'SELECT' || row.type === 'COLOR' || row.type === 'DIMENSIONS'">
                <div class="flex items-center justify-between mb-4">
                  <h4 class="text-sm font-bold text-slate-800 flex items-center gap-2">
                    <el-icon class="text-indigo-500"><Operation /></el-icon>
                    Доступні значення <span class="opacity-40">({{ row.options?.length || 0 }})</span>
                  </h4>
                  <el-button size="small" type="primary" class="premium-button-indigo-soft" @click="openAddOptionModal(row)">
                    + Додати нове значення
                  </el-button>
                </div>
                
                <div v-if="row.options && row.options.length > 0" class="flex flex-wrap gap-2.5">
                  <div 
                    v-for="opt in row.options" 
                    :key="opt.id"
                    class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 flex items-center gap-3 shadow-sm hover:border-indigo-300 transition-all group"
                  >
                    <div v-if="row.type === 'COLOR' && opt.color_code" 
                         class="w-4 h-4 rounded-lg border border-slate-200 shadow-sm" 
                         :style="{ backgroundColor: opt.color_code }"></div>
                    <span>{{ opt.value }}</span>
                    <el-icon class="ml-1 cursor-pointer text-slate-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100" @click.stop="handleDeleteOption(opt, row)">
                      <Close />
                    </el-icon>
                  </div>
                </div>
                <div v-else class="text-sm text-slate-400 font-medium py-4 text-center bg-white/50 rounded-2xl border border-dashed border-slate-200">
                  Ще немає доданих значень.
                </div>
              </div>
              <div v-else class="text-sm text-slate-500 py-3 font-medium flex items-center gap-2">
                <el-icon class="text-slate-300"><InfoFilled /></el-icon>
                Тип "{{ getTypeName(row.type) }}" не потребує попередніх значень.
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="Характеристика" min-width="220">
          <template #default="{ row }">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500 transition-colors">
                <el-icon class="text-lg"><component :is="row.icon || 'Operation'" /></el-icon>
              </div>
              <div>
                <span class="font-black text-slate-900 block">{{ row.name }}</span>
                <span v-if="row.description" class="text-[10px] text-slate-400 font-medium truncate max-w-[180px]">{{ row.description }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="Тип даних" width="140">
          <template #default="{ row }">
            <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider" :class="getTypeClass(row.type)">
              {{ getTypeName(row.type) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="generates_variant" label="Генерація SKU" width="140" align="center">
          <template #default="{ row }">
            <div class="flex justify-center">
              <div v-if="row.generates_variant" class="px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-black flex items-center gap-1.5 border border-emerald-100">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                АКТИВНО
              </div>
              <div v-else class="px-3 py-1 rounded-full bg-slate-50 text-slate-400 text-[10px] font-black border border-slate-100">
                ВИМКНЕНО
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Використання" min-width="200">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1.5">
              <span v-if="!row.category_codes || row.category_codes.length === 0" class="text-[10px] font-bold text-slate-400 px-2 py-0.5 rounded-md bg-slate-50 border border-slate-100">ВСІ КАТЕГОРІЇ</span>
              <template v-else>
                <span v-for="code in row.category_codes.slice(0, 2)" :key="code" class="text-[10px] font-bold text-indigo-600 px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-100">
                  {{ getCategoryName(code).toUpperCase() }}
                </span>
                <el-tooltip v-if="row.category_codes.length > 2" :content="getCategoryNames(row.category_codes)" placement="top">
                  <span class="text-[10px] font-bold text-slate-400 px-2 py-0.5 rounded-md bg-slate-50 border border-slate-100">+{{ row.category_codes.length - 2 }}</span>
                </el-tooltip>
              </template>
            </div>
          </template>
        </el-table-column>

        <el-table-column fixed="right" width="60" align="center">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
              <el-button text circle class="hover:bg-slate-50">
                <el-icon class="text-slate-400 rotate-90"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="premium-dropdown">
                  <el-dropdown-item command="edit"><el-icon><EditPen /></el-icon> Редагувати</el-dropdown-item>
                  <el-dropdown-item v-if="row.type === 'SELECT' || row.type === 'COLOR' || row.type === 'DIMENSIONS'" command="add_option">
                     <el-icon><Plus /></el-icon> Значення
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided class="text-red-500"><el-icon><Delete /></el-icon> Видалити</el-dropdown-item>
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

        <div class="grid grid-cols-2 gap-6 mt-4">
          <!-- Documents Section -->
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <h4 class="text-[11px] font-black text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <el-icon><Document /></el-icon> Поведінка в документах
            </h4>
            <div class="space-y-2">
              <el-checkbox v-model="attrForm.show_in_purchase_receipt" label="Показувати в прибутковій накладній" class="w-full !mr-0" />
              <el-checkbox v-model="attrForm.show_in_purchase_order" label="Показувати в замовленні пост." class="w-full !mr-0" />
              <el-checkbox v-model="attrForm.show_in_sales_order" label="Показувати в замовленні покупця" class="w-full !mr-0" />
              <el-checkbox v-model="attrForm.required" label="Обов'язкове для заповнення" class="w-full !mr-0" />
            </div>
          </div>

          <!-- Stock/Inventory Section -->
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <h4 class="text-[11px] font-black text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <el-icon><Box /></el-icon> Складський облік
            </h4>
            <div class="space-y-2">
              <el-checkbox v-model="attrForm.track_stock_separately" label="Вести залишки в розрізі цієї хар." class="w-full !mr-0" />
              <el-checkbox v-model="attrForm.block_if_empty" label="Блокувати проведення якщо пусто" class="w-full !mr-0" />
            </div>

            <h4 class="text-[11px] font-black text-slate-400 uppercase tracking-wider mt-4 mb-3 flex items-center gap-2">
              <el-icon><PriceTag /></el-icon> Номенклатура
            </h4>
            <div class="space-y-2">
              <el-checkbox v-model="attrForm.generates_variant" label="Впливає на генерацію SKU" class="w-full !mr-0" />
            </div>
          </div>
        </div>

        <div v-if="attrForm.type === 'SELECT' || attrForm.type === 'DIMENSIONS'" class="bg-indigo-50/50 p-4 rounded-lg mt-4 mb-4 border border-indigo-100">
          <h4 class="text-sm font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            <el-icon><Operation /></el-icon> Налаштування конфігуратора (BOM)
          </h4>
          
          <el-form-item label="Дозволити ручне введення" prop="allow_manual_input" class="mb-3">
            <el-switch v-model="attrForm.allow_manual_input" active-text="Так" inactive-text="Ні" />
          </el-form-item>

          <el-form-item label="Впливає на габарит (BOM)" prop="mapped_dimension" class="mb-0">
            <el-select v-model="attrForm.mapped_dimension" placeholder="Не впливає" clearable class="w-full">
              <el-option label="Немає (Просто текст)" value="" />
              <el-option label="Довжина (L)" value="length_mm" />
              <el-option label="Ширина (W)" value="width_mm" />
              <el-option label="Висота (H)" value="height_mm" />
            </el-select>
          </el-form-item>

          <el-form-item v-if="attrForm.type === 'DIMENSIONS'" label="Формат варіанту" prop="dimension_format" class="mt-3 mb-0">
            <el-input v-model="attrForm.dimension_format" placeholder="{width}×{height}" />
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
import { Plus, Search, MoreFilled, Menu, Collection, Operation, Close, InfoFilled, EditPen, Delete } from '@element-plus/icons-vue'

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
  generates_variant: true,
  show_in_purchase_receipt: true,
  show_in_purchase_order: true,
  show_in_sales_order: true,
  required: false,
  track_stock_separately: true,
  block_if_empty: false
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
  attrForm.show_in_purchase_receipt = true
  attrForm.show_in_purchase_order = true
  attrForm.show_in_sales_order = true
  attrForm.required = false
  attrForm.track_stock_separately = true
  attrForm.block_if_empty = false
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
    if (attrForm.show_in_purchase_receipt === undefined) attrForm.show_in_purchase_receipt = true
    if (attrForm.show_in_purchase_order === undefined) attrForm.show_in_purchase_order = true
    if (attrForm.show_in_sales_order === undefined) attrForm.show_in_sales_order = true
    if (attrForm.required === undefined) attrForm.required = false
    if (attrForm.track_stock_separately === undefined) attrForm.track_stock_separately = true
    if (attrForm.block_if_empty === undefined) attrForm.block_if_empty = false
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
