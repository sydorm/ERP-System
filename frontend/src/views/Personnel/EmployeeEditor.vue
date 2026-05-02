<template>
  <div class="page-container" v-loading="loading">
    
    <!-- ─── UNIFIED STICKY HEADER BLOCK ─── -->
    <div class="unified-sticky-header shadow-sm">
      <div class="user-profile-banner">
        <img src="https://demos.pixinvent.com/vuexy-html-admin-template/assets/img/pages/profile-banner.png" class="banner-img" />
      </div>
      
      <div class="profile-main-content">
        <div class="user-avatar-section">
          <el-avatar :size="90" :src="form.photo_url" class="main-avatar">
            {{ form.full_name?.charAt(0) || 'U' }}
          </el-avatar>
        </div>
        <div class="user-details-section">
          <div class="user-title-box">
            <h2 class="user-name">{{ form.full_name || 'Новий співробітник' }}</h2>
            <div class="user-meta-tags">
              <span class="meta-tag"><el-icon><User /></el-icon> {{ form.position || 'Посада' }}</span>
              <span class="meta-divider"></span>
              <span :class="['status-pill-mini', getStatusClass(currentStatusName)]">{{ currentStatusName || 'Неактивний' }}</span>
            </div>
          </div>
          <div class="header-actions-box">
            <el-button @click="router.back()" class="btn-vuexy-secondary">Назад</el-button>
            <el-button type="primary" :loading="saving" @click="saveEmployee" class="btn-vuexy-primary">
              {{ isEdit ? 'Зберегти' : 'Створити' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- Combined Navigation Inside Header -->
      <div class="header-nav-pills">
        <div 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="['nav-pill-item', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
        </div>
      </div>
    </div>

    <!-- ─── SCROLLABLE CONTENT ─── -->
    <div class="settings-scroll-area">
      
      <!-- TAB: ACCOUNT -->
      <div v-if="activeTab === 'account'" class="animate-fade-in">
        <el-card class="settings-card-modern mb-4">
          <template #header>
            <h3 class="card-section-title">ОСНОВНА ІНФОРМАЦІЯ</h3>
          </template>

          <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="ПІБ" prop="full_name">
                  <el-input v-model="form.full_name" placeholder="Олександр Петренко" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ТЕЛЕФОН" prop="phone">
                  <el-input v-model="form.phone" placeholder="+380..." />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="ПОСАДА" prop="position">
                  <el-input v-model="form.position" placeholder="Senior Developer" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ПІДРОЗДІЛ" prop="department_id">
                  <el-select v-model="form.department_id" placeholder="Оберіть відділ" style="width: 100%">
                    <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="СТАТУС" prop="status_id">
                  <el-select v-model="form.status_id" placeholder="Оберіть статус" style="width: 100%">
                    <el-option v-for="s in dictionaries.EMPLOYEE_STATUS" :key="s.id" :label="s.name" :value="s.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ДАТА ПРИЙОМУ">
                  <el-date-picker v-model="form.hire_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <el-card class="settings-card-modern danger-zone-card shadow-sm">
          <div class="danger-zone-content">
            <h3 class="card-section-title text-danger">ВИДАЛЕННЯ ПРОФІЛЮ</h3>
            <p class="danger-text">Після деактивації співробітник втратить доступ до системи.</p>
            <el-checkbox v-model="confirmDelete" label="Я підтверджую деактивацію" />
            <div class="mt-3">
              <el-button type="danger" :disabled="!confirmDelete" plain size="small">Деактивувати</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- TAB: SECURITY -->
      <div v-if="activeTab === 'security'" class="animate-fade-in">
        <el-card class="settings-card-modern">
          <h3 class="card-section-title">ЗМІНА ПАРОЛЯ</h3>
          <el-form label-position="top" class="mt-3">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Новий пароль">
                  <el-input type="password" show-password placeholder="••••••••" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Підтвердіть пароль">
                  <el-input type="password" show-password placeholder="••••••••" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-button type="primary" class="btn-vuexy-primary mt-2">Оновити доступ</el-button>
          </el-form>
        </el-card>
      </div>

      <!-- TAB: PAYROLL -->
      <div v-if="activeTab === 'payroll'" class="animate-fade-in">
        <el-card class="settings-card-modern">
          <div class="section-header-flex">
            <h3 class="card-section-title">РОЛІ ТА СТАВКИ</h3>
            <el-button type="primary" link :icon="Plus" @click="addRole">Додати роль</el-button>
          </div>
          <el-table :data="form.roles" class="modern-table-compact mt-3">
            <el-table-column label="Етап виробництва" min-width="220">
              <template #default="scope">
                <el-select v-model="scope.row.role_id" style="width: 100%" size="small">
                  <el-option v-for="it in dictionaries.PRODUCTION_STAGE" :key="it.id" :label="it.name" :value="it.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Ставка" width="140">
              <template #default="scope">
                <el-input-number v-model="scope.row.rate" :controls="false" style="width: 100%" size="small" />
              </template>
            </el-table-column>
            <el-table-column width="60" align="center">
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
  CreditCard, Plus, Delete, Check 
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
  { id: 'notifications', label: 'Сповіщення', icon: 'Bell' },
  { id: 'connections', label: 'Зв\'язки', icon: 'Link' }
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
  department_id: [{ required: true, message: 'Оберіть підрозділ', trigger: 'change' }]
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
          roles: form.value.roles.map(r => ({ ...r, rate: parseFloat(r.rate) || 0 }))
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
        ElMessage.error('Помилка збереження')
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
  background-color: var(--erp-bg-page);
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ─── Unified Sticky Header ─── */
.unified-sticky-header {
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #F1F1F2;
  box-shadow: 0 4px 12px rgba(15, 20, 34, 0.05);
}

.user-profile-banner {
  height: 100px;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-main-content {
  padding: 0 24px 16px;
  display: flex;
  align-items: flex-end;
  gap: 20px;
  margin-top: -40px;
}

.main-avatar {
  border: 4px solid #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.user-details-section {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 4px;
}

.user-name {
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 4px 0;
  color: #444050;
}

.user-meta-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #8E8BA2;
  font-size: 12px;
  font-weight: 600;
}

.meta-divider {
  width: 4px;
  height: 4px;
  background: #CBD5E1;
  border-radius: 50%;
}

.status-pill-mini {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-actions-box {
  display: flex;
  gap: 8px;
}

/* ─── Header Navigation (Tabs) ─── */
.header-nav-pills {
  display: flex;
  padding: 0 24px;
  background: #FBFBFC;
  border-top: 1px solid #F1F1F2;
}

.nav-pill-item {
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 13px;
  color: #64748B;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-pill-item:hover {
  color: #7367f0;
  background: rgba(115, 103, 240, 0.05);
}

.nav-pill-item.active {
  color: #7367f0;
  border-bottom-color: #7367f0;
  background: #fff;
}

/* ─── Scrollable Content ─── */
.settings-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.settings-card-modern {
  border: none;
  border-radius: 14px;
  box-shadow: 0 4px 18px rgba(15, 20, 34, 0.04);
  margin-bottom: 20px;
}

.card-section-title {
  font-size: 11px;
  font-weight: 800;
  color: #A3A7C5;
  letter-spacing: 1px;
  margin: 0;
  text-transform: uppercase;
}

.section-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ─── Buttons ─── */
.btn-vuexy-primary {
  background: #7367f0;
  border: none;
  font-weight: 700;
  border-radius: 6px;
  padding: 10px 20px;
}
.btn-vuexy-secondary {
  background: #F1F1F2;
  border: none;
  color: #64748B;
  font-weight: 700;
  border-radius: 6px;
  padding: 10px 20px;
}

/* ─── Form Elements ─── */
:deep(.el-form-item__label) {
  font-weight: 700;
  font-size: 12px;
  color: #444050;
  margin-bottom: 4px !important;
}

:deep(.el-input__wrapper) {
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
}

/* ─── Status Colors ─── */
.status-active { background: rgba(16, 185, 129, 0.12); color: #10B981; }
.status-warning { background: rgba(245, 158, 11, 0.12); color: #F59E0B; }
.status-danger { background: rgba(239, 68, 68, 0.12); color: #EF4444; }
.status-default { background: rgba(148, 163, 184, 0.12); color: #64748B; }

.mb-4 { margin-bottom: 24px; }
.mt-2 { margin-top: 12px; }
.mt-3 { margin-top: 16px; }

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
