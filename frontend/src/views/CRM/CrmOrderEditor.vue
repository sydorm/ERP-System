<template>
  <div class="crm-editor-page" v-loading="loading">
    <CrmOrderHeader
      :stages="stages"
      :active-stage="form.crm_stage"
      :is-passed-stage="isPassedStage"
      :order-id="orderId"
      :saving="saving"
      @back="router.push('/crm')"
      @set-stage="setStage"
      @print="printOrder"
      @save-draft="save('draft')"
      @save-production="save('production')"
    />

    <div class="crm-body">
      <div class="crm-left-col">
        <!-- Main Form Section -->
        <div class="crm-section">
          <div class="crm-section-head">
            <h3 class="crm-section-title">Основна інформація</h3>
            <span class="crm-attr-hint" v-if="orderId">Замовлення #{{ form.order_number }}</span>
          </div>
          
          <div class="crm-field">
            <label class="crm-label">Клієнт</label>
            <div style="display: flex; gap: 8px;">
              <el-select
                v-model="form.counterparty_id"
                filterable
                remote
                :remote-method="searchCounterparties"
                placeholder="Виберіть або знайдіть клієнта"
                class="cp-select modern-select"
                :class="{ 'field-error': vErrors.counterparty_id }"
              >
                <el-option
                  v-for="cp in counterparties"
                  :key="cp.id"
                  :label="cp.name + (cp.phone ? ' (' + cp.phone + ')' : '')"
                  :value="cp.id"
                />
              </el-select>
              <el-button @click="openCreateCounterparty" :icon="Plus" circle title="Додати клієнта" />
            </div>
          </div>

          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Джерело</label>
              <el-select v-model="form.lead_source_id" placeholder="Звідки прийшов" class="modern-select">
                <el-option v-for="s in leadSources" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </div>
            <div class="crm-field">
              <label class="crm-label">Місто / Доставка</label>
              <el-input v-model="form.city" placeholder="Населений пункт" />
            </div>
          </div>
          
          <div class="crm-field" style="margin-top: 12px;">
            <label class="crm-label">Канал зв'язку</label>
            <div class="channel-pills">
              <div 
                v-for="ch in channels" 
                :key="ch.code"
                class="channel-pill"
                :class="[`ch-${ch.code}`, { active: form.channel === ch.code }]"
                @click="form.channel = ch.code"
              >
                {{ ch.icon }} {{ ch.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- Product Attributes Section -->
        <div class="crm-section">
          <div class="crm-section-head">
            <h3 class="crm-section-title">Параметри виробу</h3>
            <span class="crm-attr-hint"><el-icon><MagicStick /></el-icon> Адаптивно</span>
          </div>

          <div class="crm-field">
            <label class="crm-label">Виріб</label>
            <el-select 
              v-model="form.product_id" 
              filterable 
              placeholder="Виберіть модель" 
              class="modern-select"
              @change="onProductChange"
            >
              <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>

          <div class="attributes-block" v-if="productAttributes.length">
            <div v-for="attr in productAttributes" :key="attr.id" class="attr-group">
              <label class="crm-label">{{ attr.name }}</label>
              
              <!-- Color/Options Selection -->
              <div class="attr-pills" v-if="attr.type !== 'dimensions'">
                <div 
                  v-for="opt in attr.options" 
                  :key="opt.id"
                  class="attr-pill"
                  :class="{ active: form.attributes_values[attr.id] === opt.id }"
                  @click="form.attributes_values[attr.id] = opt.id"
                >
                  <span v-if="opt.color" class="attr-color-dot" :style="{ background: opt.color }"></span>
                  {{ opt.name }}
                </div>
              </div>

              <!-- Dimensions Input -->
              <div class="attr-dims" v-else>
                <el-input-number v-model="form.attributes_values[attr.id + '_w']" :precision="0" :step="100" placeholder="Ширина" />
                <span class="dims-sep">×</span>
                <el-input-number v-model="form.attributes_values[attr.id + '_h']" :precision="0" :step="100" placeholder="Висота" />
                <span class="dims-unit">мм</span>
              </div>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Коментар до виробу</label>
            <el-input type="textarea" v-model="form.comment" :rows="3" placeholder="Особливості конструкції, фурнітура тощо..." />
          </div>
          
          <!-- Image Upload Placeholder -->
          <div class="crm-field" style="margin-top: 12px;">
            <label class="crm-label">Фото/Ескіз</label>
            <div class="photo-upload-zone" @click="triggerPhotoUpload">
              <img v-if="form.reference_photo" :src="form.reference_photo" class="photo-preview" />
              <div v-else class="photo-placeholder">
                <el-icon><Picture /></el-icon>
                <span>Натисніть або перетягніть фото</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Fulfillment & Internal -->
        <div class="crm-section">
          <div class="crm-section-head">
            <h3 class="crm-section-title">Виконання</h3>
          </div>
          
          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Склад відвантаження</label>
              <el-select v-model="form.warehouse_id" class="modern-select">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </div>
            <div class="crm-field">
              <label class="crm-label">Тип оплати</label>
              <el-select v-model="form.payment_status_id" class="modern-select">
                <el-option v-for="s in paymentStatuses" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </div>
          </div>

          <div class="crm-field" style="margin-top: 12px;">
            <label class="crm-label">Внутрішні нотатки (не бачить клієнт)</label>
            <el-input type="textarea" v-model="form.internal_notes" :rows="2" />
          </div>
        </div>
      </div>

      <div class="crm-right-col">
        <!-- Order Summary Card -->
        <CrmOrderSummary
          :form="form"
          :saving="saving"
          :payment-statuses="paymentStatuses"
          :priorities="priorities"
          :managers="users"
          @update-amount="updateTotalAmount"
        />

        <!-- Contact Management Card -->
        <CrmContactPanel
          v-if="orderId && (stages.findIndex(s => s.code === form.crm_stage) <= 1)"
          :order-id="orderId"
          :attempts="form.contact_attempts"
          :next-contact-at="form.next_contact_at"
          :comm-types="communicationTypes"
          :contact-results="contactResults"
          :history="contactHistory"
          :loading-history="loadingContacts"
          @log="logContact"
        />

        <!-- Material Availability (Placeholder) -->
        <div class="crm-section" v-if="form.product_id">
          <div class="crm-section-head">
            <h3 class="crm-section-title">Матеріали</h3>
            <span v-if="checkingMaterials" class="mat-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
            </span>
            <span v-else class="mat-status-badge" :class="matStatusClass">
              {{ matStatusLabel }}
            </span>
          </div>
          
          <div class="mat-list" v-if="materials.length">
            <div v-for="m in materials" :key="m.id" class="mat-row" :class="`mat-${m.status}`">
              <span class="mat-name">{{ m.component_name }}</span>
              <span class="mat-req">{{ m.required_qty }} {{ m.unit_of_measure }}</span>
              <span class="mat-stock-badge">{{ m.available_qty }}</span>
            </div>
          </div>
          <div class="mat-empty" v-else>
            {{ checkingMaterials ? 'Перевірка...' : 'Специфікація не завантажена' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Create Counterparty Dialog -->
    <el-dialog v-model="cpDialogVisible" title="Новий клієнт" width="500px" class="saas-dialog">
      <el-form label-position="top">
        <el-form-item label="Ім'я / Назва" required>
          <el-input v-model="newCp.name" placeholder="Петро Петренко" />
        </el-form-item>
        <el-form-item label="Телефон">
          <el-input v-model="newCp.phone" v-maska data-maska="+38 (0##) ###-##-##" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cpDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" @click="createCounterparty" :loading="creatingCp">Створити</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Picture, MagicStick, Loading, Printer, Promotion 
} from '@element-plus/icons-vue'
import { vMaska } from 'maska'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { useCrmOrderValidation } from './composables/useCrmOrderValidation'

// Components
import CrmOrderHeader from './components/CrmOrderHeader.vue'
import CrmOrderSummary from './components/CrmOrderSummary.vue'
import CrmContactPanel from './components/CrmContactPanel.vue'

const router    = useRouter()
const route     = useRoute()
const userStore = useUserStore()

// UUID validation regex
const isUuid = (val) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(val)

const orderId   = computed(() => {
  const id = route.params.id
  if (id === 'new') return null
  if (!isUuid(id)) {
    console.warn(`[CRM] Invalid Order ID in route: "${id}"`)
    return null
  }
  return id
})

const currentUser = computed(() => userStore.user || {})
const currentUserId = computed(() => currentUser.value?.id || null)

// ─── State ──────────────────────────────────────────────────────────────────
const loading = ref(true)
const saving  = ref(false)
const stages = [
  { code: 'new',        name: 'Нова заявка', color: '#6366f1' },
  { code: 'processing', name: 'Уточнення',   color: '#f59e0b' },
  { code: 'confirmed',  name: 'Підтверджено', color: '#10b981' },
  { code: 'payment',    name: 'Очікує оплату', color: '#8b5cf6' },
  { code: 'production', name: 'У виробництві', color: '#ec4899' },
  { code: 'done',       name: 'Виконано',     color: '#22c55e' },
]

const channels = [
  { code: 'instagram', name: 'Instagram', icon: '📸' },
  { code: 'website',   name: 'Сайт',      icon: '🌐' },
  { code: 'referral',  name: 'Рекомендація', icon: '🤝' },
  { code: 'telegram',  name: 'Telegram',  icon: '✈️' },
  { code: 'olx',       name: 'OLX',       icon: '📦' },
  { code: 'phone',     name: 'Телефон',   icon: '📞' },
]

const form = reactive({
  counterparty_id: null,
  lead_source_id:  null,
  order_number:    '',
  order_date:      new Date().toISOString().split('T')[0],
  warehouse_id:    null,
  product_id:      null,
  crm_stage:       'new',
  channel:         'instagram',
  city:            '',
  delivery_type:   'NP',
  attributes_values: {},
  np_branch:        null,
  next_contact_channel: 'CALL',
  next_contact_comment: '',
  next_contact_at:  null,
  contact_attempts: 0,
  total_amount:     0,
  paid_amount:     0,
  payment_status:  'unpaid',
  payment_status_id: null,
  prepayment_percent: null,
  prepayment_amount:  null,
  deadline_date:   null,
  next_contact_date: null,
  priority:        'normal',
  priority_id:     null,
  manager_id:      null,
  comment:         '',
  internal_notes:  '',
  reference_photo: null,
  discount_percent: 0,
})

// Dictionaries
const products       = ref([])
const counterparties = ref([])
const warehouses     = ref([])
const leadSources    = ref([])
const paymentStatusesRes = ref([])
const prioritiesRes      = ref([])
const deliveryMethods    = ref([])
const communicationTypes = ref([])
const contactResults     = ref([])
const bankAccounts       = ref([])
const users              = ref([])

const paymentStatuses = computed(() => paymentStatusesRes.value)
const priorities      = computed(() => prioritiesRes.value)

// Attributes Logic
const productAttributes = ref([])
const materials         = ref([])
const checkingMaterials = ref(false)

// Contacts logic
const contactHistory = ref([])
const loadingContacts = ref(false)

const { vErrors, validateCrmOrderRequiredFields, collectMissingProductionFields } = useCrmOrderValidation()

// ─── Methods ─────────────────────────────────────────────────────────────────
const isPassedStage = (stageCode) => {
  const currentIdx = stages.findIndex(s => s.code === form.crm_stage)
  const targetIdx  = stages.findIndex(s => s.code === stageCode)
  return targetIdx < currentIdx
}

const setStage = (stageCode) => {
  form.crm_stage = stageCode
}

const searchCounterparties = async (query) => {
  if (!query || query.length < 2) return
  try {
    const res = await api.get(`/api/v1/counterparties?search=${query}&is_customer=true&limit=20`)
    counterparties.value = res.data
  } catch (err) {
    console.error('Search failed', err)
  }
}

const onProductChange = async (val) => {
  if (!val) {
    productAttributes.value = []
    materials.value = []
    return
  }
  try {
    // Load attributes for this product
    const attrRes = await api.get(`/api/v1/products/${val}/attributes`)
    productAttributes.value = attrRes.data
    
    // Check materials
    checkMaterials()
  } catch (err) {
    console.error('Product change failed', err)
  }
}

const checkMaterials = async () => {
  if (!form.product_id) return
  checkingMaterials.value = true
  try {
    const res = await api.get(`/api/v1/crm/orders/check-materials?product_id=${form.product_id}`)
    materials.value = res.data.items || []
  } catch (e) {
    console.warn('Material check failed', e)
  } finally {
    checkingMaterials.value = false
  }
}

const matStatusClass = computed(() => {
  if (!materials.value.length) return ''
  const hasMissing = materials.value.some(m => m.status === 'missing')
  const hasLow     = materials.value.some(m => m.status === 'low')
  return hasMissing ? 'mat-missing' : (hasLow ? 'mat-warn' : 'mat-ok')
})

const matStatusLabel = computed(() => {
  if (!materials.value.length) return 'Немає даних'
  const hasMissing = materials.value.some(m => m.status === 'missing')
  return hasMissing ? 'Дефіцит' : 'В наявності'
})

const loadContacts = async () => {
  if (!orderId.value) return
  loadingContacts.value = true
  try {
    const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
    contactHistory.value = res.data
  } catch (err) {
    console.warn('History failed', err)
  } finally {
    loadingContacts.value = false
  }
}

const logContact = async (data) => {
  if (!orderId.value) return
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, data)
    ElMessage.success('Контакт записано')
    loadContacts()
    form.contact_attempts = (form.contact_attempts || 0) + 1
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка запису контакту')
  }
}

const updateTotalAmount = (val) => {
  form.total_amount = val
}

const triggerPhotoUpload = () => {
  // Placeholder for file input
  ElMessage.info('Завантаження фото буде доступне після підключення FileStorage')
}

// ─── Save ─────────────────────────────────────────────────────────────────────
const save = async (action) => {
  const isProduction = action === 'production'
  
  // 1. Validation
  const errors = validateCrmOrderRequiredFields({ form, clientName: clientName.value })
  Object.assign(vErrors, errors)
  
  if (Object.keys(errors).length > 0) {
    ElMessage.warning('Будь ласка, заповніть обов\'язкові поля')
    return
  }

  if (isProduction) {
    const missing = collectMissingProductionFields({
      form,
      clientName: clientName.value,
      clientPhone: clientPhone.value
    })
    if (missing.length) {
      ElMessage.warning(`Для передачі у виробництво не вистачає: ${missing.join(', ')}`)
      return
    }
  }

  saving.value = true
  try {
    // Stage update
    if (isProduction) form.crm_stage = 'production'
    else if (action === 'draft' && form.crm_stage === 'new') form.crm_stage = 'processing'

    let savedOrder
    if (orderId.value) {
      const res = await api.patch(`/api/v1/orders/${orderId.value}`, {
        ...form,
        attributes_values: {
          ...form.attributes_values,
          _np_branch: form.np_branch,
          _next_contact_channel: form.next_contact_channel,
          _next_contact_comment: form.next_contact_comment,
        }
      })
      savedOrder = res.data
    } else {
      const res = await api.post('/api/v1/orders', {
        ...form,
        lines: form.product_id ? [{
          product_id: form.product_id,
          quantity: 1,
          price: form.total_amount,
          total: form.total_amount
        }] : []
      })
      savedOrder = res.data
    }

    // 2. Production task creation if needed
    if (isProduction) {
      try {
        const prodRes = await api.post(`/api/v1/orders/${savedOrder.id}/transfer-to-production`)
        ElMessage.success(`Передано у виробництво! Завдання ${prodRes.data.production_order_number} створено`)
        router.push(`/production/orders/${prodRes.data.production_order_id}`)
        return
      } catch (err) {
        ElMessage.error('Замовлення збережено, але помилка при створенні завдання: ' + (err.response?.data?.detail || ''))
        router.push(`/crm/orders/${savedOrder.id}`)
        return
      }
    }

    ElMessage.success(orderId.value ? 'Оновлено' : 'Створено')
    if (!orderId.value) router.push(`/crm/orders/${savedOrder.id}`)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка збереження')
  } finally {
    saving.value = false
  }
}

// ─── Create Counterparty ───
const cpDialogVisible = ref(false)
const creatingCp = ref(false)
const newCp = reactive({ name: '', phone: '' })
const clientName = computed(() => counterparties.value.find(c => c.id === form.counterparty_id)?.name || '')
const clientPhone = computed(() => counterparties.value.find(c => c.id === form.counterparty_id)?.phone || '')

const openCreateCounterparty = () => {
  newCp.name = ''
  newCp.phone = ''
  cpDialogVisible.value = true
}

const createCounterparty = async () => {
  if (!newCp.name) return
  creatingCp.value = true
  try {
    const res = await api.post('/api/v1/counterparties', {
      ...newCp,
      is_customer: true,
      company_id: 'default'
    })
    counterparties.value.push(res.data)
    form.counterparty_id = res.data.id
    cpDialogVisible.value = false
    ElMessage.success('Клієнта створено')
  } catch (e) {
    ElMessage.error('Не вдалося створити клієнта')
  } finally {
    creatingCp.value = false
  }
}

const printOrder = () => {
  window.open(`${api.defaults.baseURL}/api/v1/orders/${orderId.value}/print`, '_blank')
}

// ─── Load ─────────────────────────────────────────────────────────────────────
const loadData = async () => {
  loading.value = true
  try {
    if (!userStore.user) await userStore.fetchUser().catch(() => {})

    // Load initial data in parallel
    const [pRes, cpRes, usersRes, whRes] = await Promise.allSettled([
      api.get('/api/v1/products?limit=500'),
      api.get('/api/v1/counterparties?limit=500&is_customer=true'),
      api.get('/api/v1/users/colleagues'),
      api.get('/api/v1/warehouses'),
    ])
    
    products.value       = pRes.status === 'fulfilled' ? pRes.value.data : []
    counterparties.value = cpRes.status === 'fulfilled' ? cpRes.value.data : []
    users.value          = usersRes.status === 'fulfilled' ? usersRes.value.data : []
    warehouses.value     = whRes.status === 'fulfilled' ? whRes.value.data : []

    if (!orderId.value && !form.manager_id && currentUserId.value) {
      form.manager_id = currentUserId.value
    }
    if (!form.warehouse_id && warehouses.value.length) {
      form.warehouse_id = warehouses.value.find(w => w.is_default)?.id || warehouses.value[0].id
    }

    // Load Dictionaries
    try {
      const [ls, ps, pr, dm, ct, cr, accs] = await Promise.all([
        api.get('/api/v1/dictionaries/LEAD_SOURCE'),
        api.get('/api/v1/dictionaries/PAYMENT_STATUS'),
        api.get('/api/v1/dictionaries/PRIORITY'),
        api.get('/api/v1/dictionaries/DELIVERY_METHOD'),
        api.get('/api/v1/dictionaries/COMMUNICATION_TYPE'),
        api.get('/api/v1/dictionaries/CONTACT_RESULT'),
        api.get('/api/v1/companies/default/accounts').catch(() => ({ data: [] }))
      ])
      leadSources.value = ls.data
      paymentStatusesRes.value = ps.data
      prioritiesRes.value = pr.data
      deliveryMethods.value = dm.data
      communicationTypes.value = ct.data
      contactResults.value = cr.data
      bankAccounts.value = accs.data
    } catch (e) {
      console.warn('Dictionaries failed to load', e)
    }

    // Load actual order if ID exists
    if (orderId.value) {
      try {
        const res = await api.get(`/api/v1/orders/${orderId.value}`)
        const o = res.data
        
        // Sync form with data
        Object.assign(form, o)
        
        // Ensure numeric fields are cast
        form.total_amount = Number(o.total_amount)
        form.paid_amount = Number(o.paid_amount || 0)
        
        // Load additional order info
        loadContacts()
        if (form.product_id) onProductChange(form.product_id)
      } catch (err) {
        ElMessage.error('Помилка завантаження замовлення')
        console.error('[CRM] Load Order Error:', err)
      }
    } else if (route.params.id !== 'new') {
      ElMessage.warning('Некоректний ідентифікатор замовлення. Повернення до списку.')
      router.push('/crm')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Watchers
watch(() => form.product_id, (newVal) => {
  if (newVal) checkMaterials()
})
</script>

<style src="./styles/CrmOrderEditor.css"></style>
