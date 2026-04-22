<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button link :icon="ArrowLeft" @click="router.back()">Назад до списку</el-button>
        <h2>{{ isEdit ? 'Редагування співробітника' : 'Новий співробітник' }}</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" :loading="saving" @click="saveEmployee" class="btn-save">
          {{ isEdit ? 'Зберегти зміни' : 'Створити' }}
        </el-button>
      </div>
    </div>

    <el-form 
      v-loading="loading"
      :model="form" 
      :rules="rules" 
      ref="formRef" 
      label-position="top"
    >
      <el-tabs v-model="activeTab" class="custom-tabs">
        <!-- Basic Info Tab -->
        <el-tab-pane label="Основні дані" name="basic">
          <el-card shadow="never" class="form-card">
            <el-row :gutter="20">
              <el-col :span="16">
                <el-form-item label="ПІБ співробітника" prop="full_name">
                  <el-input v-model="form.full_name" placeholder="Петренко Петро Петрович" />
                </el-form-item>

                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="Посада" prop="position">
                      <el-input v-model="form.position" placeholder="Наприклад: Зварювальник 5р." />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Підрозділ" prop="department_id">
                      <el-select v-model="form.department_id" placeholder="Оберіть підрозділ" style="width: 100%">
                        <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="Статус" prop="status_id">
                      <el-select v-model="form.status_id" placeholder="Оберіть статус" style="width: 100%">
                        <el-option v-for="s in dictionaries.EMPLOYEE_STATUS" :key="s.id" :label="s.name" :value="s.id" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Телефон" prop="phone">
                      <el-input v-model="form.phone" placeholder="+380..." />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="Дата народження" prop="birth_date">
                      <el-date-picker v-model="form.birth_date" type="date" placeholder="Оберіть дату" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Дата прийому на роботу" prop="hire_date">
                      <el-date-picker v-model="form.hire_date" type="date" placeholder="Оберіть дату" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-col>

              <el-col :span="8">
                <el-form-item label="Фото">
                  <div class="photo-placeholder">
                    <el-icon v-if="!form.photo_url" :size="48"><UserFilled /></el-icon>
                    <img v-else :src="form.photo_url" class="photo-img" />
                    <el-input v-model="form.photo_url" placeholder="URL фото (буде аплоад у v2)" size="small" class="mt-2" />
                  </div>
                </el-form-item>
                
                <el-form-item label="Додаткова інформація">
                  <el-input v-model="form.notes" type="textarea" :rows="4" placeholder="Будь-які примітки..." />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>
        </el-tab-pane>

        <!-- Roles & Rates Tab -->
        <el-tab-pane label="Ролі та Оплата" name="roles">
          <el-card shadow="never" class="form-card">
            <template #header>
               <div class="card-header">
                 <span>Призначені ролі на виробництві / в компанії</span>
                 <el-button type="primary" link :icon="Plus" @click="addRole">Додати роль</el-button>
               </div>
            </template>

            <div v-if="form.roles.length === 0" class="empty-roles">
              <el-empty description="Ролей не призначено. Додайте хоча б одну основну роль." />
            </div>

            <el-table :data="form.roles" style="width: 100%" v-else>
              <el-table-column label="Роль (Етап виробництва)" min-width="200">
                <template #default="scope">
                  <el-select v-model="scope.row.role_id" placeholder="Оберіть етап" style="width: 100%">
                    <el-option v-for="it in dictionaries.PRODUCTION_STAGE" :key="it.id" :label="it.name" :value="it.id" />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column label="Тип ролі" width="180">
                <template #default="scope">
                  <el-select v-model="scope.row.role_type_id" placeholder="Тип" style="width: 100%">
                    <el-option v-for="it in dictionaries.ROLE_TYPE" :key="it.id" :label="it.name" :value="it.id" />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column label="Нарахування" width="200">
                <template #default="scope">
                  <el-select v-model="scope.row.accrual_type_id" placeholder="Тип нарахування" style="width: 100%">
                    <el-option v-for="it in dictionaries.ACCRUAL_TYPE" :key="it.id" :label="it.name" :value="it.id" />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column label="Ставка" width="150">
                <template #default="scope">
                  <el-input-number v-model="scope.row.rate" :min="0" :precision="2" :controls="false" style="width: 100%" />
                </template>
              </el-table-column>

              <el-table-column width="60" align="center">
                <template #default="scope">
                  <el-button link type="danger" :icon="Delete" @click="removeRole(scope.$index)" />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, UserFilled, Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('basic')
const isEdit = computed(() => route.params.id && route.params.id !== 'new')

const departments = ref([])
const dictionaries = ref({
  PRODUCTION_STAGE: [],
  ACCRUAL_TYPE: [],
  ROLE_TYPE: [],
  EMPLOYEE_STATUS: []
})

const formRef = ref(null)
const form = ref({
  full_name: '',
  position: '',
  department_id: null,
  status_id: null,
  phone: '',
  birth_date: null,
  hire_date: new Date(),
  photo_url: '',
  notes: '',
  roles: []
})

const rules = {
  full_name: [{ required: true, message: 'Введіть ПІБ', trigger: 'blur' }],
  position: [{ required: true, message: 'Введіть посаду', trigger: 'blur' }],
  department_id: [{ required: true, message: 'Оберіть підрозділ', trigger: 'change' }],
  status_id: [{ required: true, message: 'Оберіть статус', trigger: 'change' }]
}

const fetchFormData = async () => {
  loading.value = true
  try {
    // 1. Fetch Dictionaries
    const dictTypes = ['PRODUCTION_STAGE', 'ACCRUAL_TYPE', 'ROLE_TYPE', 'EMPLOYEE_STATUS']
    await Promise.all(dictTypes.map(async (type) => {
      const res = await api.get('/api/v1/dictionaries/items', { params: { type } })
      dictionaries.value[type] = res.data
    }))

    // 2. Fetch Departments
    const deptRes = await api.get('/api/v1/departments')
    departments.value = deptRes.data

    // 3. Fetch Employee if editing
    if (isEdit.value) {
      const empRes = await api.get(`/api/v1/employees/${route.params.id}`)
      form.value = { 
        ...empRes.data,
        roles: empRes.data.roles.map(r => ({
          role_id: r.role_id,
          role_type_id: r.role_type_id,
          accrual_type_id: r.accrual_type_id,
          rate: parseFloat(r.rate) || 0,
          is_active: r.is_active
        }))
      }
    }
  } catch (error) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const addRole = () => {
  form.value.roles.push({
    role_id: null,
    role_type_id: dictionaries.value.ROLE_TYPE.find(t => t.code?.includes('MAIN'))?.id || dictionaries.value.ROLE_TYPE[0]?.id,
    accrual_type_id: null,
    rate: 0,
    is_active: true
  })
}

const removeRole = (index) => {
  form.value.roles.splice(index, 1)
}

const saveEmployee = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        if (isEdit.value) {
          await api.put(`/api/v1/employees/${route.params.id}`, form.value)
          ElMessage.success('Дані оновлено')
        } else {
          await api.post('/api/v1/employees', form.value)
          ElMessage.success('Співробітника створено')
        }
        router.push('/personnel/employees')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
      } finally {
        saving.value = false
      }
    } else {
      ElMessage.warning('Будь ласка, заповніть обов\'язкові поля')
    }
  })
}

onMounted(fetchFormData)
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 8px 0 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1d1f;
}

.btn-save {
  background: #2a85ff;
  border: none;
  font-weight: 600;
  padding: 12px 24px;
}

.form-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.photo-placeholder {
  width: 100%;
  aspect-ratio: 1;
  background: #f1f3f5;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #adb5bd;
  margin-bottom: 16px;
  overflow: hidden;
  border: 2px dashed #dee2e6;
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.custom-tabs :deep(.el-tabs__item) {
  font-weight: 600;
  font-size: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.empty-roles {
  padding: 40px 0;
}

.mt-2 {
  margin-top: 8px;
}
</style>
