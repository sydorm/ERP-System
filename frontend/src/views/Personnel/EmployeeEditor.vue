<template>
  <div class="page-container" v-loading="loading">
    
    <!-- ─── FLOATING ROUNDED STICKY HEADER ─── -->
    <div class="sticky-header-wrapper">
      <div class="unified-sticky-header card-shadow">
        <div class="profile-main-content">
          <div class="user-avatar-wrapper">
            <el-avatar :size="80" :src="form.photo_url" class="main-avatar">
              {{ form.full_name?.charAt(0) || 'U' }}
            </el-avatar>
          </div>
          <div class="user-details-layout">
            <div class="user-info-group">
              <h2 class="user-display-name">{{ form.full_name || 'Новий співробітник' }}</h2>
              <div class="user-meta-info">
                <span class="meta-badge"><el-icon><User /></el-icon> {{ form.position || 'Посада не вказана' }}</span>
                <span class="meta-dot"></span>
                <span :class="['status-tag', getStatusClass(currentStatusName)]">
                  <span class="status-dot"></span>
                  {{ currentStatusName || 'Неактивний' }}
                </span>
              </div>
            </div>
            <div class="header-action-group">
              <el-button @click="router.back()" class="btn-ghost-modern">
                <el-icon class="mr-1"><ArrowLeft /></el-icon> Назад
              </el-button>
              <el-button type="primary" :loading="saving" @click="saveEmployee" class="btn-vuexy-glow">
                <el-icon class="mr-1"><Check /></el-icon>
                {{ isEdit ? 'Зберегти зміни' : 'Створити профіль' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- Navigation Pills (Refined Vuexy Style) -->
        <div class="header-navigation-bar">
          <div 
            v-for="tab in tabs" 
            :key="tab.id" 
            :class="['nav-item-pill', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <el-icon><component :is="tab.icon" /></el-icon>
            <span>{{ tab.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── SCROLLABLE CONTENT AREA ─── -->
    <div class="settings-content-scroll">
      
      <!-- TAB: ACCOUNT -->
      <div v-if="activeTab === 'account'" class="fade-up-animation">
        <el-card class="settings-card-premium mb-4">
          <div class="card-section-header">
            <h3 class="section-accent-title">ОСНОВНА ІНФОРМАЦІЯ</h3>
          </div>

          <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="modern-form-dense">
            <el-row :gutter="32">
              <el-col :span="12">
                <el-form-item label="ПІБ Співробітника" prop="full_name">
                  <el-input v-model="form.full_name" placeholder="Олександр Петренко" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Телефонний номер" prop="phone">
                  <el-input v-model="form.phone" placeholder="+380..." />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="32">
              <el-col :span="12">
                <el-form-item label="Посада в компанії" prop="position">
                  <el-input v-model="form.position" placeholder="Наприклад: Менеджер з продажів" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Підрозділ" prop="department_id">
                  <el-select v-model="form.department_id" placeholder="Оберіть відділ" style="width: 100%">
                    <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="32">
              <el-col :span="12">
                <el-form-item label="Поточний статус" prop="status_id">
                  <el-select v-model="form.status_id" placeholder="Оберіть статус" style="width: 100%">
                    <el-option v-for="s in dictionaries.EMPLOYEE_STATUS" :key="s.id" :label="s.name" :value="s.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Дата прийняття на роботу">
                  <el-date-picker v-model="form.hire_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="32">
              <el-col :span="24">
                <el-form-item label="Коментарі або примітки">
                  <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="Будь-яка додаткова інформація..." />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <el-card class="settings-card-premium danger-zone-card">
          <div class="danger-header">
            <h3 class="section-accent-title text-danger">БЕЗПЕКА ТА ВИДАЛЕННЯ</h3>
          </div>
          <div class="danger-body">
            <p class="danger-instruction">Після деактивації картка співробітника перейде в архів. Його доступ до системи буде негайно заблоковано.</p>
            <div class="danger-actions">
              <el-checkbox v-model="confirmDelete" label="Я підтверджую деактивацію цього профілю" class="mb-2" />
              <div class="mt-2">
                <el-button type="danger" :disabled="!confirmDelete" plain>Деактивувати фахівця</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- TAB: SECURITY -->
      <div v-if="activeTab === 'security'" class="fade-up-animation">
        <el-card class="settings-card-premium">
          <h3 class="section-accent-title">ДОСТУП ДО СИСТЕМИ</h3>
          <el-form label-position="top" class="mt-4">
            <el-row :gutter="32">
              <el-col :span="12">
                <el-form-item label="Новий пароль">
                  <el-input type="password" show-password placeholder="••••••••" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Повторіть пароль">
                  <el-input type="password" show-password placeholder="••••••••" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-button type="primary" class="btn-vuexy-glow mt-2">Оновити пароль</el-button>
          </el-form>
        </el-card>
      </div>

      <!-- TAB: PAYROLL -->
      <div v-if="activeTab === 'payroll'" class="fade-up-animation">
        <el-card class="settings-card-premium">
          <div class="card-section-header between">
            <h3 class="section-accent-title">СТАВКИ ТА РОЛІ</h3>
            <el-button type="primary" link :icon="Plus" @click="addRole">Додати нову роль</el-button>
          </div>
          <el-table :data="form.roles" class="premium-table-compact mt-4">
            <el-table-column label="Роль / Етап виробництва" min-width="250">
              <template #default="scope">
                <el-select v-model="scope.row.role_id" style="width: 100%" size="default">
                  <el-option v-for="it in dictionaries.PRODUCTION_STAGE" :key="it.id" :label="it.name" :value="it.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Ставка (грн)" width="180">
              <template #default="scope">
                <el-input-number v-model="scope.row.rate" :controls="false" style="width: 100%" />
              </template>
            </el-table-column>
            <el-table-column width="80" align="center">
              <template #default="scope">
                <el-button link type="danger" :icon="Delete" @click="removeRole(scope.$index)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  User, Location, Calendar, Lock, Bell, Link, 
  CreditCard, Plus, Delete, Check, ArrowLeft 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('account')
const isEdit = computed(() => route.params.id && route.params.id !== 'new')
const confirmDelete = ref(false)

const tabs = [
  { id: 'account', label: 'Профіль', icon: 'User' },
  { id: 'security', label: 'Безпека', icon: 'Lock' },
  { id: 'payroll', label: 'Оплата', icon: 'CreditCard' },
  { id: 'notifications', label: 'Сповіщення', icon: 'Bell' }
]

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
    role_type_id: dictionaries.value.ROLE_TYPE[0]?.id,
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
          roles: form.value.roles
            .filter(r => r.role_id !== null)
            .map(r => ({ ...r, rate: parseFloat(r.rate) || 0 }))
        }
        console.log('Sending Employee Payload:', payload)
        
        if (isEdit.value) {
          await api.put(`/api/v1/employees/${route.params.id}`, payload)
          ElMessage.success('Дані оновлено')
        } else {
          await api.post('/api/v1/employees', payload)
          ElMessage.success('Співробітника створено')
        }
        router.push('/personnel/employees')
      } catch (error) {
        console.error('API Error Details:', error.response?.data || error)
        const errorMsg = error.response?.data?.message || error.response?.data?.error || 'Помилка збереження'
        ElMessage.error(errorMsg)
        
        if (error.response?.status === 422 && error.response?.data?.details) {
          console.table(error.response.data.details)
        }
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
  padding: 0;
  background-color: #F8F9FA;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ─── Floating Rounded Sticky Header ─── */
.sticky-header-wrapper {
  padding: 24px 32px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  background: transparent; /* Remove the greyish glow */
}

.card-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.unified-sticky-header {
  background: #ffffff !important;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.02);
}

.profile-main-content {
  padding: 24px 32px 20px;
  display: flex;
  align-items: center;
  gap: 28px;
}

.user-avatar-wrapper {
  position: relative;
}
.main-avatar {
  border: 4px solid #fff;
  box-shadow: 0 8px 20px rgba(15, 20, 34, 0.1);
  background-color: #F1F5F9;
}

.user-details-layout {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-display-name {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 6px 0;
  color: #2D3748;
  letter-spacing: -0.02em;
}

.user-meta-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.meta-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #718096;
}

.meta-dot {
  width: 5px;
  height: 5px;
  background: #CBD5E1;
  border-radius: 50%;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.header-action-group {
  display: flex;
  gap: 12px;
}

/* ─── Navigation Bar (Vuexy Style) ─── */
.header-navigation-bar {
  display: flex;
  padding: 0 32px;
  background: #fff;
  border-top: 1px solid #F1F5F9;
}

.nav-item-pill {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
  color: #64748B;
  transition: all 0.25s ease;
  position: relative;
}

.nav-item-pill:hover {
  color: #7367f0;
}

.nav-item-pill.active {
  color: #7367f0;
  background: rgba(115, 103, 240, 0.06);
}
.nav-item-pill.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #7367f0;
}

/* ─── Content Area ─── */
.settings-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  scroll-behavior: smooth;
}

.settings-card-premium {
  border: none;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(15, 20, 34, 0.03);
  margin-bottom: 24px;
  background: #fff;
}

.section-accent-title {
  font-size: 12px;
  font-weight: 800;
  color: #475569;
  letter-spacing: 1.5px;
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid #7367f0;
  text-transform: uppercase;
}

.card-section-header {
  margin-bottom: 28px;
}
.card-section-header.between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ─── Modern Form ─── */
:deep(.el-form-item__label) {
  font-weight: 700;
  font-size: 13px;
  color: #4A5568;
  margin-bottom: 8px !important;
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  border-radius: 10px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  background-color: #F8FAFC !important;
  transition: all 0.2s;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #7367f0 inset !important;
}

/* ─── Buttons ─── */
.btn-primary-compact {
  background: linear-gradient(135deg, #7367f0 0%, #a8a1f8 100%);
  border: none;
  color: #fff;
  font-weight: 700;
  border-radius: 8px;
  padding: 12px 24px;
  box-shadow: 0 8px 15px rgba(115, 103, 240, 0.3);
  transition: all 0.3s;
}
.btn-primary-compact:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(115, 103, 240, 0.35);
}

.btn-vuexy-glow {
  background: linear-gradient(135deg, #7367f0 0%, #a8a1f8 100%) !important;
  border: none;
  font-weight: 700;
  border-radius: 8px;
  padding: 12px 24px;
  box-shadow: 0 8px 15px rgba(115, 103, 240, 0.3);
  transition: all 0.3s;
  color: #fff;
}
.btn-vuexy-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(115, 103, 240, 0.35);
}

.btn-ghost-modern {
  background: transparent;
  border: 1px solid #E2E8F0;
  color: #64748B;
  font-weight: 700;
  border-radius: 8px;
  padding: 12px 24px;
}
.btn-ghost-modern:hover {
  background: #F8FAFC;
  border-color: #CBD5E1;
}

/* ─── Danger Zone ─── */
.danger-zone-card {
  border: 1px solid rgba(239, 68, 68, 0.1);
}
.danger-body {
  padding: 10px 12px;
}
.danger-instruction {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 20px;
}

/* ─── Status Colors ─── */
.status-active { background: rgba(16, 185, 129, 0.1); color: #10B981; }
.status-warning { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
.status-danger { background: rgba(239, 68, 68, 0.1); color: #EF4444; }
.status-default { background: rgba(148, 163, 184, 0.1); color: #64748B; }

.fade-up-animation {
  animation: fadeUp 0.5s ease-out forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.mr-1 { margin-right: 6px; }
.mb-2 { margin-bottom: 12px; }
.mt-4 { margin-top: 24px; }
</style>
