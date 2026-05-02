<template>
  <div class="page-container" v-loading="loading">
    
    <!-- ─── VUEXY PROFILE HEADER ─── -->
    <div class="account-header-modern shadow-sm">
      <div class="user-profile-banner">
        <img src="https://demos.pixinvent.com/vuexy-html-admin-template/assets/img/pages/profile-banner.png" class="banner-img" />
      </div>
      <div class="user-profile-info">
        <div class="user-avatar-section">
          <el-avatar :size="100" :src="form.photo_url" class="main-avatar">
            {{ form.full_name?.charAt(0) || 'U' }}
          </el-avatar>
        </div>
        <div class="user-details-section">
          <div class="user-main-info">
            <h2 class="user-name">{{ form.full_name || 'Новий співробітник' }}</h2>
            <div class="user-meta-row">
              <span class="meta-item"><el-icon><User /></el-icon> {{ form.position || 'Посада' }}</span>
              <span class="meta-item"><el-icon><Location /></el-icon> {{ currentDeptName || 'Відділ' }}</span>
              <span class="meta-item"><el-icon><Calendar /></el-icon> Прийнятий {{ formatDate(form.hire_date) }}</span>
            </div>
          </div>
          <div class="user-actions">
            <span :class="['status-badge-pill', getStatusClass(currentStatusName)]">
              {{ currentStatusName || 'Неактивний' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── NAVIGATION PILLS (VUEXY STYLE) ─── -->
    <div class="nav-pills-container mb-4">
      <div 
        v-for="tab in tabs" 
        :key="tab.id" 
        :class="['nav-pill', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <el-icon><component :is="tab.icon" /></el-icon>
        <span>{{ tab.label }}</span>
      </div>
    </div>

    <!-- ─── SETTINGS CONTENT ─── -->
    <div class="settings-view-wrapper">
      
      <!-- TAB: ACCOUNT -->
      <div v-if="activeTab === 'account'" class="animate-fade-in">
        <el-card class="settings-card mb-4">
          <template #header>
            <div class="card-header-modern">
              <h3 class="card-title-modern">Деталі профілю</h3>
              <p class="card-subtitle">Основна інформація та контакти співробітника</p>
            </div>
          </template>

          <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="modern-form">
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

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="URL ФОТО">
                  <el-input v-model="form.photo_url" placeholder="https://..." />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="form-footer mt-4">
              <el-button type="primary" :loading="saving" @click="saveEmployee" class="btn-vuexy-primary">Зберегти зміни</el-button>
              <el-button @click="router.back()" class="btn-vuexy-secondary">Відмінити</el-button>
            </div>
          </el-form>
        </el-card>

        <!-- Danger Zone -->
        <el-card class="settings-card danger-zone-card shadow-sm">
          <template #header>
            <h3 class="card-title-modern text-danger">Видалення профілю</h3>
          </template>
          <div class="danger-zone-content">
            <p class="danger-text">Після деактивації співробітник втратить доступ до системи. Це рішення можна скасувати в архіві.</p>
            <el-checkbox v-model="confirmDelete" label="Я підтверджую деактивацію цього профілю" />
            <div class="mt-3">
              <el-button type="danger" :disabled="!confirmDelete" plain>Деактивувати співробітника</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- TAB: SECURITY -->
      <div v-if="activeTab === 'security'" class="animate-fade-in">
        <el-card class="settings-card shadow-sm">
          <template #header>
            <h3 class="card-title-modern">Зміна пароля</h3>
          </template>
          <el-form label-position="top">
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
            <div class="password-checklist">
              <h4 class="checklist-title">Вимоги до пароля:</h4>
              <ul class="checklist-items">
                <li><el-icon class="mr-1"><Check /></el-icon> Мінімум 8 символів</li>
                <li><el-icon class="mr-1"><Check /></el-icon> Хоча б одна велика літера</li>
                <li><el-icon class="mr-1"><Check /></el-icon> Хоча б одна цифра або спецсимвол</li>
              </ul>
            </div>
            <el-button type="primary" class="btn-vuexy-primary mt-3">Оновити доступ</el-button>
          </el-form>
        </el-card>
      </div>

      <!-- TAB: PAYROLL -->
      <div v-if="activeTab === 'payroll'" class="animate-fade-in">
        <el-card class="settings-card shadow-sm">
          <template #header>
            <div class="card-header-between">
              <h3 class="card-title-modern">Ролі та Оплата</h3>
              <el-button type="primary" link :icon="Plus" @click="addRole">Додати роль</el-button>
            </div>
          </template>

          <el-table :data="form.roles" class="modern-table">
            <el-table-column label="Етап виробництва" min-width="220">
              <template #default="scope">
                <el-select v-model="scope.row.role_id" style="width: 100%" size="default">
                  <el-option v-for="it in dictionaries.PRODUCTION_STAGE" :key="it.id" :label="it.name" :value="it.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Ставка" width="160">
              <template #default="scope">
                <el-input-number v-model="scope.row.rate" :controls="false" style="width: 100%" />
              </template>
            </el-table-column>
            <el-table-column label="Дії" width="80" align="center">
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
  padding: 24px;
  background-color: var(--erp-bg-page);
  height: calc(100vh - 64px);
  overflow-y: auto;
  color: #444050;
  font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* ─── Vuexy Header ─── */
.account-header-modern {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
}

.user-profile-banner {
  height: 140px;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-profile-info {
  padding: 0 24px 24px;
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-top: -50px;
}

.main-avatar {
  border: 5px solid #fff;
  box-shadow: 0 4px 14px rgba(15, 20, 34, 0.1);
}

.user-details-section {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 8px;
}

.user-name {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 6px 0;
  color: #444050;
}

.user-meta-row {
  display: flex;
  gap: 20px;
  color: #8E8BA2;
  font-size: 13px;
  font-weight: 600;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge-pill {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ─── Nav Pills ─── */
.nav-pills-container {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.nav-pill {
  padding: 10px 18px;
  background: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 700;
  color: #64748B;
  box-shadow: 0 2px 6px rgba(15, 20, 34, 0.03);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.nav-pill:hover {
  background: #f1f1f2;
  color: #7367f0;
}
.nav-pill.active {
  background: #7367f0;
  color: #fff;
  box-shadow: 0 4px 12px rgba(115, 103, 240, 0.35);
}

/* ─── Content Cards ─── */
.settings-card {
  border: none;
  border-radius: 14px;
  box-shadow: 0 4px 18px rgba(15, 20, 34, 0.05);
}

.card-header-modern {
  margin-bottom: 8px;
}
.card-title-modern {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #444050;
}
.card-subtitle {
  font-size: 13px;
  color: #A3A7C5;
  margin: 4px 0 0;
}

.card-header-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ─── Form Styles ─── */
:deep(.el-form-item__label) {
  font-weight: 700;
  font-size: 12px;
  color: #444050;
  margin-bottom: 6px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 4px 12px !important;
}

.btn-vuexy-primary {
  background: #7367f0;
  border: none;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 6px;
  transition: all 0.2s;
}
.btn-vuexy-primary:hover {
  background: #5e50ee;
  box-shadow: 0 4px 12px rgba(115, 103, 240, 0.4);
}

.btn-vuexy-secondary {
  background: rgba(142, 139, 162, 0.1);
  border: none;
  color: #8e8ba2;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 6px;
}

/* ─── Security & Checklist ─── */
.password-checklist {
  background: rgba(115, 103, 240, 0.04);
  padding: 20px;
  border-radius: 10px;
  margin-top: 24px;
}
.checklist-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #7367f0;
}
.checklist-items {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 13px;
  color: #64748B;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.checklist-items li {
  display: flex;
  align-items: center;
}

/* ─── Danger Zone ─── */
.danger-zone-card {
  border: 1px solid rgba(239, 68, 68, 0.15);
  background: rgba(239, 68, 68, 0.02);
}
.danger-text {
  font-size: 13px;
  color: #64748B;
  margin-bottom: 16px;
}

/* ─── Status Colors ─── */
.status-active { background: rgba(16, 185, 129, 0.12); color: #10B981; }
.status-warning { background: rgba(245, 158, 11, 0.12); color: #F59E0B; }
.status-danger { background: rgba(239, 68, 68, 0.12); color: #EF4444; }
.status-default { background: rgba(148, 163, 184, 0.12); color: #64748B; }

.mb-4 { margin-bottom: 24px; }
.mt-3 { margin-top: 16px; }
.mt-4 { margin-top: 24px; }
.mr-1 { margin-right: 4px; }

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
