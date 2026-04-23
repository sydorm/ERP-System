<template>
  <div class="brigades-manager flex flex-col h-full">
    <!-- Toolbar -->
    <div class="p-5 border-b border-slate-100 flex justify-between items-center bg-white">
      <div>
        <h2 class="text-lg font-bold text-slate-800">Виробничі бригади</h2>
        <p class="text-xs text-slate-500 mt-1">Керування складом команд для етапів виробництва</p>
      </div>
      <div class="flex gap-3">
        <el-input 
          v-model="searchQuery" 
          placeholder="Пошук бригади..." 
          prefix-icon="Search"
          clearable
          class="w-64"
        />
        <el-button type="primary" color="#4f46e5" :icon="Plus" @click="openAddModal">
          Додати бригаду
        </el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="flex-1 overflow-auto p-5" v-loading="loading">
      <el-table :data="filteredBrigades" style="width: 100%" class="custom-table">
        <el-table-column prop="name" label="Назва" min-width="180">
          <template #default="{ row }">
            <span class="font-bold text-slate-800">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="Виробничий етап" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="row.stage" size="small" effect="plain">{{ row.stage.name }}</el-tag>
            <span v-else class="text-slate-400 text-xs">-</span>
          </template>
        </el-table-column>

        <el-table-column label="Склад (Членів)" width="120" align="center">
          <template #default="{ row }">
            <el-badge :value="row.members?.length || 0" class="item" type="info">
              <el-icon :size="20" class="text-slate-400"><UserFilled /></el-icon>
            </el-badge>
          </template>
        </el-table-column>

        <el-table-column prop="is_active" label="Статус" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? 'Активна' : 'Пауза' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column fixed="right" width="120" align="center">
          <template #default="{ row }">
            <el-button-group>
              <el-button :icon="Edit" circle @click="openEditModal(row)" />
              <el-button :icon="Delete" circle type="danger" plain @click="handleDelete(row)" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Brigade Editor Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditMode ? 'Редагування бригади' : 'Створення бригади'" 
      width="700px"
      append-to-body
    >
      <el-form :model="form" label-position="top">
        <el-row :gutter="20">
          <el-col :span="14">
            <el-form-item label="Назва бригади" required>
              <el-input v-model="form.name" placeholder="напр. Зварювальники" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="Етап виробництва">
              <el-select v-model="form.stage_id" placeholder="Оберіть етап" class="w-full" clearable>
                <el-option v-for="s in productionStages" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="mt-6">
          <div class="flex justify-between items-center mb-4">
            <h4 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Склад бригади</h4>
            <el-button type="primary" size="small" link :icon="Plus" @click="addMemberNode">Додати учасника</el-button>
          </div>

          <el-table :data="form.members" size="small" border stripe>
            <el-table-column label="Співробітник" min-width="250">
              <template #default="{ row }">
                <el-select v-model="row.employee_id" filterable placeholder="Пошук..." class="w-full" size="default">
                  <el-option v-for="emp in employeesList" :key="emp.id" :label="emp.full_name" :value="emp.id" />
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="Роль" width="150">
              <template #default="{ row }">
                <el-select v-model="row.role_type" size="default">
                  <el-option label="Основний" value="main" />
                  <el-option label="Резервний" value="reserve" />
                </el-select>
              </template>
            </el-table-column>

            <el-table-column label="Статус" width="80" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.is_active" size="small" />
              </template>
            </el-table-column>

            <el-table-column width="50" align="center">
              <template #default="{ $index }">
                <el-button type="danger" link :icon="Delete" @click="form.members.splice($index, 1)" />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="mt-4">
          <el-checkbox v-model="form.is_active">Бригада активна</el-checkbox>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Скасувати</el-button>
        <el-button type="primary" color="#4f46e5" @click="submitForm" :loading="submitting">Зберегти бригаду</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Plus, Edit, Delete, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const searchQuery = ref('')

const brigades = ref([])
const productionStages = ref([])
const employeesList = ref([])

const form = reactive({
  id: null,
  name: '',
  stage_id: null,
  is_active: true,
  members: []
})

const filteredBrigades = computed(() => {
  if (!searchQuery.value) return brigades.value
  const q = searchQuery.value.toLowerCase()
  return brigades.value.filter(b => b.name.toLowerCase().includes(q))
})

const fetchData = async () => {
  loading.value = true
  try {
    const [brigRes, stageRes, empRes] = await Promise.all([
      api.get('/api/v1/brigades'),
      api.get('/api/v1/dictionaries/items?type=PRODUCTION_STAGE'),
      api.get('/api/v1/employees', { params: { limit: 500 } })
    ])
    brigades.value = brigRes.data
    productionStages.value = stageRes.data
    employeesList.value = empRes.data
  } catch (error) {
    ElMessage.error('Помилка завантаження даних для бригад')
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  isEditMode.value = false
  form.id = null
  form.name = ''
  form.stage_id = null
  form.is_active = true
  form.members = []
  dialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  Object.assign(form, row)
  // Deep copy members to avoid direct modification
  form.members = row.members ? JSON.parse(JSON.stringify(row.members)) : []
  dialogVisible.value = true
}

const addMemberNode = () => {
  form.members.push({
    employee_id: null,
    role_type: 'main',
    is_active: true
  })
}

const submitForm = async () => {
  if (!form.name) return ElMessage.warning('Введіть назву бригади')
  
  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/brigades/${form.id}`, form)
      ElMessage.success('Бригаду оновлено')
    } else {
      await api.post('/api/v1/brigades', form)
      ElMessage.success('Бригаду створено')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`Видалити бригаду "${row.name}"?`, 'Увага', {
    confirmButtonText: 'Видалити',
    cancelButtonText: 'Скасувати',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/api/v1/brigades/${row.id}`)
      ElMessage.success('Видалено')
      fetchData()
    } catch (error) {
      ElMessage.error('Помилка видалення')
    }
  })
}

onMounted(fetchData)
</script>
