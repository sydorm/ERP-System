<template>
  <div class="page-container" v-loading="loading">
    
    <!-- ─── PROFILE HEADER CARD ─── -->
    <div class="profile-header-card">
      <div class="header-content">
        <div class="profile-main">
          <div class="avatar-container">
            <el-avatar :size="80" :src="form.photo_url" class="profile-avatar">
              {{ form.full_name?.charAt(0) || 'U' }}
            </el-avatar>
            <div :class="['status-ring', getStatusClass(currentStatusName)]"></div>
          </div>
          <div class="profile-info">
            <div class="back-link" @click="router.back()">
              <el-icon><ArrowLeft /></el-icon> Назад до списку
            </div>
            <h1 class="employee-name">{{ form.full_name || 'Новий співробітник' }}</h1>
            <div class="employee-meta">
              <span class="meta-tag position">{{ form.position || 'Посада не вказана' }}</span>
              <span class="meta-divider"></span>
              <span :class="['meta-tag status', getStatusClass(currentStatusName)]">
                <span class="pulse-dot"></span>
                {{ currentStatusName || 'Статус не обрано' }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button @click="router.back()" class="btn-secondary-modern">Скасувати</el-button>
          <el-button type="primary" :loading="saving" @click="saveEmployee" class="btn-primary-gradient">
            <el-icon class="mr-2"><Check /></el-icon>
            {{ isEdit ? 'Зберегти зміни' : 'Створити профіль' }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <!-- ─── LEFT COLUMN: QUICK SUMMARY ─── -->
      <div class="side-column">
        <div class="glass-card summary-card">
          <h3 class="card-title">ШВИДКА ІНФОРМАЦІЯ</h3>
          <div class="summary-list">
            <div class="summary-item">
              <div class="item-label">ТЕЛЕФОН</div>
              <div class="item-value">{{ form.phone || '—' }}</div>
            </div>
            <div class="summary-item">
              <div class="item-label">ПІДРОЗДІЛ</div>
              <div class="item-value">{{ currentDeptName || '—' }}</div>
            </div>
            <div class="summary-item">
              <div class="item-label">ДАТА ПРИЙОМУ</div>
              <div class="item-value">{{ formatDate(form.hire_date) }}</div>
            </div>
          </div>
          <div class="notes-section">
            <div class="item-label">ПРИМІТКИ</div>
            <el-input 
              v-model="form.notes" 
              type="textarea" 
              :rows="4" 
              placeholder="Додайте опис або примітки..." 
              class="modern-textarea"
            />
          </div>
        </div>
      </div>

      <!-- ─── RIGHT COLUMN: DETAILED TABS ─── -->
      <div class="main-column">
        <el-form 
          :model="form" 
          :rules="rules" 
          ref="formRef" 
          label-position="top"
          class="modern-form"
        >
          <el-tabs v-model="activeTab" class="modern-tabs">
            <!-- Basic Info Tab -->
            <el-tab-pane label="Особисті дані" name="basic">
              <div class="form-section">
                <el-row :gutter="24">
                  <el-col :span="24">
                    <el-form-item label="ПІБ Співробітника" prop="full_name">
                      <el-input v-model="form.full_name" placeholder="Введіть повне ім'я" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="Посада" prop="position">
                      <el-input v-model="form.position" placeholder="Наприклад: Менеджер проектів" />
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

                <el-row :gutter="24">
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

                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="Дата народження" prop="birth_date">
                      <el-date-picker v-model="form.birth_date" type="date" placeholder="Оберіть дату" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Дата прийому" prop="hire_date">
                      <el-date-picker v-model="form.hire_date" type="date" placeholder="Оберіть дату" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24">
                  <el-col :span="24">
                    <el-form-item label="URL Фото">
                      <el-input v-model="form.photo_url" placeholder="Вставте посилання на зображення" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </el-tab-pane>

            <!-- Roles & Rates Tab -->
            <el-tab-pane label="Ролі та Оплата" name="roles">
              <div class="form-section">
                <div class="section-header">
                  <h4 class="section-subtitle">ПРИЗНАЧЕНІ РОЛІ ТА СТАВКИ</h4>
                  <el-button type="primary" link :icon="Plus" @click="addRole" class="btn-add-role">Додати роль</el-button>
                </div>

                <div v-if="form.roles.length === 0" class="empty-state">
                  <el-empty :image-size="80" description="Ролей ще не додано" />
                </div>

                <div v-else class="roles-table-container">
                  <el-table :data="form.roles" class="roles-table-modern">
                    <el-table-column label="Етап / Роль" min-width="180">
                      <template #default="scope">
                        <el-select v-model="scope.row.role_id" placeholder="Оберіть етап" size="small">
                          <el-option v-for="it in dictionaries.PRODUCTION_STAGE" :key="it.id" :label="it.name" :value="it.id" />
                        </el-select>
                      </template>
                    </el-table-column>

                    <el-table-column label="Тип" width="130">
                      <template #default="scope">
                        <el-select v-model="scope.row.role_type_id" placeholder="Тип" size="small">
                          <el-option v-for="it in dictionaries.ROLE_TYPE" :key="it.id" :label="it.name" :value="it.id" />
                        </el-select>
                      </template>
                    </el-table-column>

                    <el-table-column label="Ставка" width="120">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.rate" :min="0" :precision="2" :controls="false" size="small" />
                      </template>
                    </el-table-column>

                    <el-table-column width="50" align="center">
                      <template #default="scope">
                        <el-button link type="danger" :icon="Delete" @click="removeRole(scope.$index)" />
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, UserFilled, Plus, Delete, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

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

const currentStatusName = computed(() => {
  if (!form.value.status_id) return ''
  const s = dictionaries.value.EMPLOYEE_STATUS.find(it => it.id === form.value.status_id)
  return s ? s.name : ''
})

const currentDeptName = computed(() => {
  if (!form.value.department_id) return ''
  const d = departments.value.find(it => it.id === form.value.department_id)
  return d ? d.name : ''
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

const getStatusClass = (statusName) => {
  if (!statusName) return 'status-default'
  const name = statusName.toLowerCase()
  if (name.includes('актив') || name.includes('працює')) return 'status-active'
  if (name.includes('відпуст')) return 'status-warning'
  if (name.includes('звільн')) return 'status-danger'
  return 'status-default'
}

const formatDate = (date) => {
  return date ? dayjs(date).format('DD.MM.YYYY') : '—'
}

const fetchFormData = async () => {
  loading.value = true
  try {
    const dictTypes = ['PRODUCTION_STAGE', 'ACCRUAL_TYPE', 'ROLE_TYPE', 'EMPLOYEE_STATUS']
    await Promise.all(dictTypes.map(async (type) => {
      const res = await api.get('/api/v1/dictionaries/items', { params: { type } })
      dictionaries.value[type] = res.data
    }))

    const deptRes = await api.get('/api/v1/departments')
    departments.value = deptRes.data

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
    accrual_type_id: dictionaries.value.ACCRUAL_TYPE[0]?.id,
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
        const payload = {
          ...form.value,
          birth_date: form.value.birth_date ? dayjs(form.value.birth_date).format('YYYY-MM-DD') : null,
          hire_date: form.value.hire_date ? dayjs(form.value.hire_date).format('YYYY-MM-DD') : null,
          roles: form.value.roles.map(r => ({
            ...r,
            rate: parseFloat(r.rate) || 0
          }))
        }

        if (isEdit.value) {
          await api.put(`/api/v1/employees/${route.params.id}`, payload)
          ElMessage.success('Дані оновлено')
        } else {
          await api.post('/api/v1/employees', payload)
          ElMessage.success('Співробітника створено')
        }
        router.push('/personnel/employees')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
      } finally {
        saving.value = false
      }
    }
  })
}

onMounted(fetchFormData)
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: var(--erp-bg-page);
  height: calc(100vh - 64px);
  overflow-y: auto;
  color: #444050;
  font-size: 13px;
}

/* ─── Profile Header Card ─── */
.profile-header-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(15, 20, 34, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-container {
  position: relative;
}

.profile-avatar {
  border: 4px solid #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.status-ring {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 14px;
  height: 14px;
  border: 3px solid #fff;
  border-radius: 50%;
}

.status-ring.status-active { background-color: #10B981; }
.status-ring.status-warning { background-color: #F59E0B; }
.status-ring.status-danger { background-color: #EF4444; }
.status-ring.status-default { background-color: #94A3B8; }

.back-link {
  font-size: 12px;
  color: #A3A7C5;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  transition: color 0.2s;
}
.back-link:hover { color: #6366F1; }

.employee-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.employee-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-tag {
  font-size: 13px;
  font-weight: 600;
}

.meta-tag.position { color: #8E8BA2; }

.meta-tag.status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  text-transform: uppercase;
  font-size: 11px;
}

.meta-divider {
  width: 1px;
  height: 14px;
  background-color: #E2E8F0;
}

/* ─── Buttons ─── */
.btn-primary-gradient {
  background: linear-gradient(135deg, #7367f0 0%, #ce9ffc 100%);
  border: none;
  color: #fff;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(115, 103, 240, 0.4);
}

.btn-secondary-modern {
  border: 1px solid #E2E8F0;
  color: #64748B;
  font-weight: 600;
  border-radius: 8px;
}

/* ─── Content Grid ─── */
.content-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(15, 20, 34, 0.03);
}

.card-title {
  font-size: 11px;
  font-weight: 800;
  color: #A3A7C5;
  letter-spacing: 1.5px;
  margin-bottom: 20px;
  text-transform: uppercase;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.item-label {
  font-size: 11px;
  font-weight: 700;
  color: #A3A7C5;
  margin-bottom: 4px;
}

.item-value {
  font-size: 14px;
  font-weight: 600;
  color: #444050;
}

.main-column {
  background: #fff;
  border-radius: 14px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(15, 20, 34, 0.03);
  overflow: hidden;
}

.modern-form {
  padding: 0;
}

.modern-tabs :deep(.el-tabs__header) {
  background: #F8F9FA;
  margin: 0;
  padding: 0 24px;
  border-bottom: 1px solid #F1F1F2;
}

.modern-tabs :deep(.el-tabs__item) {
  height: 54px;
  line-height: 54px;
  font-weight: 700;
  font-size: 14px;
  color: #8E8BA2;
}

.modern-tabs :deep(.el-tabs__item.is-active) {
  color: #6366F1;
}

.form-section {
  padding: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-subtitle {
  font-size: 12px;
  font-weight: 800;
  color: #A3A7C5;
  letter-spacing: 1px;
  margin: 0;
}

/* ─── Custom Form Styles ─── */
:deep(.el-form-item__label) {
  font-weight: 700;
  font-size: 12px;
  color: #444050;
  margin-bottom: 8px !important;
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  background-color: #FBFBFC !important;
}

.roles-table-container {
  border: 1px solid #F1F1F2;
  border-radius: 10px;
  overflow: hidden;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background-color: currentColor;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.5); }
  100% { opacity: 1; transform: scale(1); }
}

.status-active { color: #10B981; background: rgba(16, 185, 129, 0.1); }
.status-warning { color: #F59E0B; background: rgba(245, 158, 11, 0.1); }
.status-danger { color: #EF4444; background: rgba(239, 68, 68, 0.1); }
.status-default { color: #94A3B8; background: rgba(148, 163, 184, 0.1); }

.empty-state {
  padding: 40px;
}
</style>
