<template>
  <div class="crm-editor-page">
    <div class="crm-editor-page-inner">
      <CrmOrderHeader
        :stages="stages"
        :active-stage="form.crm_stage"
        :is-passed-stage="isPassedStage"
        :order-id="orderId"
        :saving="saving"
        @back="router.back()"
        @set-stage="setStage"
        @print="printModalVisible = true"
        @save-draft="save('draft')"
        @save-production="save('production')"
      />

      <!-- ===== BODY ===== -->
      <div class="crm-body" v-loading="loading">
        <div class="crm-left-col">

          <CrmClientBlock
            :form="form"
            :v-errors="vErrors"
            :counterparties="counterparties"
            :lead-sources="leadSources"
            :delivery-methods="deliveryMethods"
            :manager-options="managerOptions"
            :can-reassign-manager="canReassignManager"
            v-model:client-name="clientName"
            v-model:client-phone="clientPhone"
            @counterparty-change="onCounterpartyChange"
            @new-client="showNewClientDialog = true"
          />

          <CrmProductBlock
            :form="form"
            :products="products"
            :selected-product="selectedProduct"
            :product-attributes="productAttributes"
            @product-change="onProductChange"
            @set-attr-value="setAttrValue"
            @set-attr-dim="setAttrDim"
            @upload-photo="uploadPhoto"
          />

          <CrmMaterialsCheckBlock
            :form="form"
            :material-check="materialCheck"
            :materials-loading="materialsLoading"
            :format-qty="formatQty"
            @go-to-purchases="goToPurchases"
          />

          <CrmFinanceBlock
            :form="form"
            :bank-accounts="bankAccounts"
            :auto-payment-status="autoPaymentStatus"
            :format-currency="formatCurrency"
            @calc-prepayment="calcPrepayment"
            @prepayment-input="onPrepaymentInput"
            @set-prepay-pct="setPrepayPct"
          />

          <CrmDeadlinesBlock
            :form="form"
            :priorities="priorities"
            :format-date="formatDate"
          />

        </div><!-- /left col -->

        <!-- ─── RIGHT SIDEBAR ─────────────────────────────────────── -->
        <div class="crm-right-col">

          <CrmReadinessChecklist
            class="saas-glass-card saas-premium-shadow"
            :progress="readinessProgress"
            :items="readinessItems"
          />

          <CrmContactPanel
            class="saas-glass-card"
            :form="form"
            :order-id="orderId"
            :communication-types="communicationTypes"
            :contact-results="contactResults"
            :contact-result="contactResult"
            v-model:contact-comm-type="contactCommType"
            v-model:contact-plan-reason="contactPlanReason"
            v-model:contact-next-at="contactNextAt"
            v-model:contact-note="contactNote"
            :next-touch-summary="nextTouchSummary"
            :saving-contact="savingContact"
            :getResultHint="getResultHint"
            @set-next-contact-preset="setNextContactPreset"
            @open-communication="commDrawerVisible = true"
            @apply-contact-result="applyContactResult"
            @log-contact="logContact"
          />

          <CrmAiAssistant
            class="saas-glass-card"
            :form="form"
            :readiness-progress="readinessProgress"
            @check="ElMessage.success('AI Аналіз завершено')"
          />

          <CrmCommunicationHistory
            class="saas-glass-card"
            v-if="orderId"
            :contacts="contacts"
            :get-contact-result-color="getContactResultColor"
            :get-comm-icon="getCommIcon"
            :get-comm-name="getCommName"
            :format-date-time="formatDateTime"
            :contact-result-label="contactResultLabel"
          />

          <CrmOrderHistoryNotes
            class="saas-glass-card"
            v-if="orderId"
            :form="form"
            :history="history"
          />

          <CrmRelatedDocuments
            class="saas-glass-card"
            v-if="orderId"
            ref="relatedDocsRef"
            :order-id="orderId"
          />

        </div><!-- /right col -->
      </div><!-- /body -->
    </div><!-- /inner -->

    <!-- ===== DIALOGS ===== -->
    <AutomationConfirmModal
      v-model="automationModal.visible"
      :rule="automationModal.rule"
      source-type="crm_lead"
      :source-id="orderId"
      @confirmed="relatedDocsRef?.refresh()"
      @skipped="automationModal.rule = null"
    />

    <CrmNewClientDialog
      v-model="showNewClientDialog"
      :new-client="newClient"
      :saving="savingClient"
      @create="createNewClient"
    />

    <CrmCommunicationDrawer
      v-model="commDrawerVisible"
      v-model:contact-comm-type="contactCommType"
      :communication-types="communicationTypes"
      :message-templates="messageTemplates"
      @apply-template="contactNote = $event"
    />

    <PrintPreviewModal
      v-if="orderId"
      v-model="printModalVisible"
      :document-id="orderId"
      document-type="invoice"
    />
  </div>
</template>

<script setup>
import './styles/CrmOrderEditor.css'
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import PrintPreviewModal from '@/components/PrintPreviewModal.vue'
import AutomationConfirmModal from '@/components/AutomationConfirmModal.vue'
import CrmOrderHeader from './components/CrmOrderHeader.vue'
import CrmClientBlock from './components/CrmClientBlock.vue'
import CrmProductBlock from './components/CrmProductBlock.vue'
import CrmFinanceBlock from './components/CrmFinanceBlock.vue'
import CrmDeadlinesBlock from './components/CrmDeadlinesBlock.vue'
import CrmReadinessChecklist from './components/CrmReadinessChecklist.vue'
import CrmContactPanel from './components/CrmContactPanel.vue'
import CrmCommunicationHistory from './components/CrmCommunicationHistory.vue'
import CrmAiAssistant from './components/CrmAiAssistant.vue'
import CrmRelatedDocuments from './components/CrmRelatedDocuments.vue'
import CrmMaterialsCheckBlock from './components/CrmMaterialsCheckBlock.vue'
import CrmOrderHistoryNotes from './components/CrmOrderHistoryNotes.vue'
import CrmNewClientDialog from './components/CrmNewClientDialog.vue'
import CrmCommunicationDrawer from './components/CrmCommunicationDrawer.vue'
import { createInitialCrmOrderForm, createMaterialCheckState, createNewClientForm } from './composables/useCrmOrderForm'
import { collectMissingProductionFields, createCrmOrderValidationErrors, validateCrmOrderRequiredFields } from './composables/useCrmOrderValidation'
import { defaultCommTypes, defaultContactResults, getCommShort, getResultHint, messageTemplates, toLocalDateTimeValue } from './composables/useCrmContactLogic'
import { buildReadinessItems, calculateReadinessProgress } from './composables/useCrmReadiness'
import api from '@/api'

const printModalVisible = ref(false)
const commDrawerVisible = ref(false)

const router    = useRouter()
const route     = useRoute()
const userStore = useUserStore()
const orderId   = computed(() => route.params.id !== 'new' ? route.params.id : null)
const currentUser = computed(() => userStore.user || {})
const currentUserId = computed(() => currentUser.value?.id || null)
const getUserDisplayName = (u) => {
  if (!u) return 'Поточний користувач'
  return (
    u.name
    || u.full_name
    || [u.firstName || u.first_name, u.lastName || u.last_name].filter(Boolean).join(' ')
    || u.email
    || u.username
    || 'Поточний користувач'
  )
}
const currentUserName = computed(() => {
  return getUserDisplayName(currentUser.value)
})
const canReassignManager = computed(() => {
  const u = currentUser.value
  return Boolean(
    u?.is_superuser
    || ['admin', 'director'].includes(u?.role)
    || userStore.hasPermission?.('crm.order.reassign')
    || userStore.hasPermission?.('crm.manage')
  )
})

// ─── State ────────────────────────────────────────────────────────────────────
const loading        = ref(false)
const saving         = ref(false)
const savingClient   = ref(false)
const automationModal = reactive({ visible: false, rule: null })
const relatedDocsRef = ref(null)
const materialsLoading = ref(false)
const products       = ref([])
const counterparties = ref([])
const users          = ref([])
const productAttributes = ref([])
const showNewClientDialog = ref(false)

const leadSources = ref([])
const paymentStatusesRes = ref([])
const prioritiesRes = ref([])
const bankAccounts = ref([])
const deliveryMethods = ref([])


const communicationTypes = ref([...defaultCommTypes])

const contactResults = ref([...defaultContactResults])


const materialCheck = reactive(createMaterialCheckState())

const newClient = reactive(createNewClientForm())

const managerOptions = computed(() => {
  const list = users.value.map(u => ({ ...u, name: getUserDisplayName(u) }))
  if (currentUserId.value && !list.some(u => String(u.id) === String(currentUserId.value))) {
    list.unshift({ id: currentUserId.value, name: currentUserName.value })
  }
  return list
})


// Communication
const contacts      = ref([])
const contactResult = ref(null)
const contactCommType = ref('CALL')
const contactNote   = ref('')
const contactNextAt = ref(null)
const contactPlanReason = ref('first_touch')
const savingContact = ref(false)

const vErrors = reactive(createCrmOrderValidationErrors())

// Watch contact result to auto-set reminder
watch(() => contactResult.value, (newVal) => {
  if (newVal === 'NO_ANSWER') setNextContactPreset({ hours: 2, reason: 'retry_no_answer', syncContactLog: true })
  if (newVal === 'THINKING') setNextContactPreset({ tomorrow: true, h: 10, reason: 'clarify', syncContactLog: true })
  if (newVal === 'CONFIRMED') contactPlanReason.value = 'payment'
})

// Sync comm type with lead source for new orders
watch(() => contactCommType.value, (newVal) => {
  if (!orderId.value && newVal) {
    // Try to find matching lead source by name or code
    const found = leadSources.value.find(ls => ls.id === newVal || ls.name === newVal)
    if (found) form.lead_source_id = found.id
  }
})

const form = reactive(createInitialCrmOrderForm(route.query.stage || 'new'))

// Client quick-edit fields (synced to counterparty)
const clientName  = ref('')
const clientPhone = ref('')

// Config fetched during loadData
const stages = [
  { key: 'new',        label: 'Нова заявка' },
  { key: 'payment',    label: 'Оплата' },
  { key: 'processing', label: 'В роботі' },
  { key: 'production', label: 'Виробництво' },
  { key: 'done',       label: 'Виконано' },
]
const stageIndex = computed(() => stages.findIndex(s => s.key === form.crm_stage))
const isPassedStage = (idx) => idx < stageIndex.value

// Dictionaries fetched in onMounted
const priorities = computed(() => prioritiesRes.value.map(i => ({ value: i.id, label: i.name, color: i.color })))
const paymentStatuses = computed(() => paymentStatusesRes.value.map(i => ({ value: i.id, label: i.name, color: i.color })))


// ─── Computed ─────────────────────────────────────────────────────────────────
const selectedProduct = computed(() => products.value.find(p => p.id === form.product_id) || null)

const requiredAttributesFilled = computed(() => {
  if (!productAttributes.value.length) return true
  return productAttributes.value.every(attr => {
    const value = form.attributes_values?.[attr.id]
    if (attr.type === 'DIMENSIONS') return Boolean(value?.w && value?.h)
    return value !== undefined && value !== null && value !== ''
  })
})

const readinessItems = computed(() => buildReadinessItems({
  form,
  clientPhone: clientPhone.value,
  requiredAttributesFilled: requiredAttributesFilled.value,
}))

const readinessProgress = computed(() => calculateReadinessProgress(readinessItems.value))

const nextTouchSummary = computed(() => {
  if (!form.next_contact_at) return 'Додайте дату наступного контакту, щоб менеджер не загубив клієнта.'
  const channel = getCommName(contactCommType.value)
  const reasonMap = {
    first_touch: 'перший контакт',
    retry_no_answer: 'повтор після не відповів',
    clarify: 'уточнити деталі',
    payment: 'нагадати про оплату',
    production: 'погодити виробництво'
  }
  return `${channel}: ${reasonMap[contactPlanReason.value] || 'контакт'} · ${formatDateTime(form.next_contact_at)}`
})


const history = computed(() => {
  const items = []
  if (orderId.value) {
    items.push({ text: 'Заявка створена', time: formatDate(form.order_date) })
    if (form.crm_stage !== 'new') {
      items.push({ text: `Переведено у «${stages.find(s => s.key === form.crm_stage)?.label}»`, time: 'раніше' })
    }
  } else {
    items.push({ text: 'Заявка створена', time: 'щойно' })
  }
  return items
})

const autoPaymentStatus = computed(() => {
  const total = Number(form.total_amount) || 0
  const paid = Number(form.prepayment_amount) || 0
  
  if (paid === 0) return { label: 'Не оплачено', color: '#94a3b8', key: 'unpaid' }
  if (paid >= total && total > 0) return { label: 'Оплачено повністю', color: '#22c55e', key: 'paid' }
  return { label: 'Часткова оплата', color: '#eab308', key: 'partial' }
})

watch(() => autoPaymentStatus.value, (newVal) => {
  form.payment_status = newVal.key
}, { immediate: true })

watch(() => contactCommType.value, (newVal) => {
  form.next_contact_channel = newVal
}, { immediate: true })

// ─── Helpers ──────────────────────────────────────────────────────────────────
const formatCurrency = (v) => Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 0 })
const formatQty = (v) => Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 0, maximumFractionDigits: 3 })
const formatDate = (d) => {
  if (!d) return ''
  const [y, m, day] = (d || '').split('-')
  return `${day}.${m}.${y}`
}

// ─── Attribute helpers ────────────────────────────────────────────────────────
const setAttrValue = (attrId, value) => {
  form.attributes_values = { ...form.attributes_values, [attrId]: value }
}
const setAttrDim = (attrId, axis, value) => {
  const cur = form.attributes_values?.[attrId] || {}
  form.attributes_values = { ...form.attributes_values, [attrId]: { ...cur, [axis]: value } }
}

// ─── Prepayment calc ──────────────────────────────────────────────────────────
const setPrepayPct = (pct) => {
  form.prepayment_percent = pct
  calcPrepayment()
}
const calcPrepayment = () => {
  if (form.prepayment_percent > 0) {
    form.prepayment_amount = Math.round(form.total_amount * form.prepayment_percent / 100)
  } else if (form.prepayment_percent === 0) {
    form.prepayment_amount = 0
  }
}
const onPrepaymentInput = () => {
  if (form.total_amount > 0) {
    form.prepayment_percent = Math.round((form.prepayment_amount || 0) / form.total_amount * 100)
  } else {
    form.prepayment_percent = 0
  }
}

// ─── Stage ────────────────────────────────────────────────────────────────────
const setStage = async (key) => {
  // Rule 1: Payment Stage
  if (key === 'payment') {
    const hasClient = form.counterparty_id || clientName.value || clientPhone.value
    const hasProduct = form.product_id
    const hasAmount = Number(form.total_amount || 0) > 0
    if (!hasClient || !hasProduct || !hasAmount) {
      ElMessage.warning('Для переходу в "Оплата" вкажіть клієнта або телефон, виріб та суму замовлення.')
      return
    }
  }

  // Rule 2: Processing (В роботі) Stage
  if (key === 'processing') {
    const hasClient = form.counterparty_id || clientName.value
    const hasPhone = clientPhone.value
    const hasProduct = form.product_id
    const hasAttrs = requiredAttributesFilled.value
    const hasAmount = Number(form.total_amount || 0) > 0
    const hasDeadline = form.deadline_date
    const hasTerms = form.prepayment_percent !== null || form.prepayment_amount !== null || form.payment_status

    if (!hasDeadline) {
      ElMessage.warning('Вкажіть дату готовності перед передачею заявки в роботу.')
      return
    }
    if (!hasClient || !hasPhone || !hasProduct || !hasAttrs || !hasAmount || !hasTerms) {
      ElMessage.warning('Для переходу "В роботу" заповніть клієнта, телефон, виріб, характеристики, суму та умови оплати.')
      return
    }
  }

  // Rule 3: Production (Виробництво) Stage
  if (key === 'production') {
    if (form.crm_stage !== 'processing') {
      ElMessage.warning('Перехід у "Виробництво" дозволений тільки зі статусу "В роботі".')
      return
    }
    const hasDeadline = form.deadline_date
    const hasAttrs = requiredAttributesFilled.value
    const hasComment = form.comment || form.internal_notes
    if (!hasDeadline || !hasAttrs || !hasComment) {
      ElMessage.warning('Для переходу у "Виробництво" вкажіть дату готовності, характеристики та коментар для виробництва.')
      return
    }
  }

  if (key === 'processing' && orderId.value) {
    try {
      const res = await api.post('/api/v1/business-process/event', {
        source_type: 'crm_lead',
        source_id: orderId.value,
        event_type: 'status_changed',
        to_status: 'processing',
      })
      const { can_proceed, validation_error, rules } = res.data
      if (!can_proceed) {
        ElMessage.warning(validation_error || 'Не можна змінити статус')
        return
      }
      form.crm_stage = key
      const askRule = rules?.find(r => r.mode === 'ask_confirmation')
      if (askRule) {
        automationModal.rule = askRule
        automationModal.visible = true
      } else {
        const autoRule = rules?.find(r => r.mode === 'automatic')
        if (autoRule) {
          try {
            await api.post('/api/v1/business-process/execute', {
              rule_id: autoRule.rule_id,
              source_type: 'crm_lead',
              source_id: orderId.value,
            })
          } catch { /* non-critical */ }
        }
      }
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || 'Помилка перевірки статусу')
      return
    }
  } else {
    form.crm_stage = key
  }
}

// ─── Counterparty change ──────────────────────────────────────────────────────
const onCounterpartyChange = (id) => {
  const cp = counterparties.value.find(c => c.id === id)
  if (cp) {
    clientName.value  = cp.name
    clientPhone.value = cp.phone || ''
  }
}

// ─── Product change ───────────────────────────────────────────────────────────
const onProductChange = async (productId) => {
  productAttributes.value = []
  form.attributes_values = {}
  materialCheck.items = []
  materialCheck.has_issues = false

  if (!productId) return

  try {
    // Fetch category attributes for this product
    const product = products.value.find(p => p.id === productId)
    if (product?.category) {
      const res = await api.get(`/api/v1/attributes/category/${product.category}`)
      productAttributes.value = res.data
        ?.map(ca => ca.attribute)
        .filter(a => a && !a.is_archived) || []
    }
    // Auto-fill total amount from product price if available and not already set
    if (product?.price && Number(product.price) > 0) {
      form.total_amount = Number(product.price)
      calcPrepayment()
    }
  } catch { /* no attributes */ }

  // Check materials if we already have an order ID
  await checkMaterials(productId)
}

const checkMaterials = async (productId) => {
  if (!productId) return
  materialsLoading.value = true
  try {
    const pid = orderId.value || 'new'
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}/material-check?product_id=${productId}`)
      Object.assign(materialCheck, res.data)
    } else {
      // For new orders, fetch spec directly
      const specRes = await api.get(`/api/v1/products/${productId}/specifications`)
      const specs = specRes.data || []
      const defaultSpec = specs.find(s => s.is_default && s.is_active) || specs[0]
      if (!defaultSpec?.items?.length) { materialsLoading.value = false; return }

      // Get stock for each component
      const items = []
      let hasIssues = false
      for (const item of defaultSpec.items) {
        const stockRes = await api.get(`/api/v1/products/${item.component_id}/stock`)
        const avail = stockRes.data?.total_quantity || 0
        const req = Number(item.quantity)
        const st = avail >= req ? 'ok' : avail > 0 ? 'low' : 'missing'
        if (st !== 'ok') hasIssues = true
        items.push({
          component_id: item.component_id,
          component_name: item.component?.name || item.component_id,
          component_sku: item.component?.sku || '',
          unit_of_measure: item.unit_of_measure || item.component?.unit_of_measure || 'шт',
          required_qty: req,
          available_qty: avail,
          status: st,
        })
      }
      materialCheck.items = items
      materialCheck.has_issues = hasIssues
    }
  } catch { /* silent */ } finally {
    materialsLoading.value = false
  }
}

// ─── Photo upload ─────────────────────────────────────────────────────────────
const uploadPhoto = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await api.post('/api/v1/upload/image', fd)
    form.reference_photo = res.data.url
  } catch {
    ElMessage.error('Помилка завантаження фото')
  }
}

// ─── New client ───────────────────────────────────────────────────────────────
const createNewClient = async () => {
  if (!newClient.name) { ElMessage.warning('Вкажіть ім\'я'); return }
  savingClient.value = true
  try {
    const res = await api.post('/api/v1/counterparties', {
      name: newClient.name,
      phone: newClient.phone,
      email: newClient.email,
      is_customer: true,
      is_supplier: false,
    })
    counterparties.value.push(res.data)
    form.counterparty_id = res.data.id
    clientName.value  = res.data.name
    clientPhone.value = res.data.phone || ''
    showNewClientDialog.value = false
    Object.assign(newClient, { name: '', phone: '', email: '' })
    ElMessage.success('Клієнта створено')
  } catch {
    ElMessage.error('Помилка створення клієнта')
  } finally {
    savingClient.value = false
  }
}

// ─── Go to purchases ──────────────────────────────────────────────────────────
const goToPurchases = () => router.push('/purchases/orders/new')

// ─── Communication helpers ────────────────────────────────────────────────────
const formatDateTime = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const setNextContactPreset = (opts = {}) => {
  const d = new Date()
  if (opts.minutes) d.setMinutes(d.getMinutes() + opts.minutes)
  if (opts.hours) d.setHours(d.getHours() + opts.hours)
  if (opts.tomorrow) {
    d.setDate(d.getDate() + 1)
    d.setHours(opts.h || 10, 0, 0, 0)
  }
  if (opts.days) {
    d.setDate(d.getDate() + opts.days)
    d.setHours(opts.h || 10, 0, 0, 0)
  }

  const value = toLocalDateTimeValue(d)
  form.next_contact_at = value
  if (opts.syncContactLog) contactNextAt.value = value
  if (opts.reason) contactPlanReason.value = opts.reason
}

const applyContactResult = (code) => {
  const nextValue = contactResult.value === code ? null : code
  contactResult.value = nextValue
  if (!nextValue) return
  if (code === 'NO_ANSWER') setNextContactPreset({ hours: 2, reason: 'retry_no_answer', syncContactLog: true })
  if (code === 'THINKING') setNextContactPreset({ tomorrow: true, h: 10, reason: 'clarify', syncContactLog: true })
  if (code === 'CONFIRMED') {
    contactPlanReason.value = 'payment'
    if (!form.next_contact_at) setNextContactPreset({ days: 1, h: 10, reason: 'payment' })
  }
}

const loadContacts = async () => {
  if (!orderId.value) return
  try {
    const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
    contacts.value = res.data
  } catch { /* silent */ }
}

const getCommName = (code) => {
  const ct = communicationTypes.value.find(i => i.code === code)
  return ct ? ct.name : 'Контакт'
}
const getCommIcon = (code) => {
  const ct = communicationTypes.value.find(i => i.code === code)
  return ct ? ct.icon : '📞'
}
const contactResultIcon = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.icon : '📞'
}
const contactResultLabel = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.name : code
}
const getContactResultColor = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.color : '#e2e8f0'
}

const logContact = async () => {
  if (!contactResult.value) return
  savingContact.value = true
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      result: contactResult.value,
      communication_type: contactCommType.value,
      note: contactNote.value || null,
      next_contact_at: contactNextAt.value || null,
    })
    ElMessage.success('Контакт записано')
    contactResult.value = null
    contactNote.value = ''
    contactNextAt.value = null
    await loadData()  // reload to reflect updated stage / attempts / next_contact_at
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка запису контакту')
  } finally {
    savingContact.value = false
  }
}

// ─── Save ─────────────────────────────────────────────────────────────────────
const save = async (action) => {
  Object.assign(vErrors, validateCrmOrderRequiredFields({ form, clientName: clientName.value }))

  if (action === 'production') {
    const missing = collectMissingProductionFields({
      form,
      clientName: clientName.value,
      clientPhone: clientPhone.value,
      requiredAttributesFilled: requiredAttributesFilled.value,
      contactResult: contactResult.value,
    })

    if (missing.length > 0) {
      ElMessage.warning({
        message: `Для передачі у виробництво не вистачає даних:\n- ${missing.join('\n- ')}`,
        duration: 5000
      })
      return
    }
  }

  if (vErrors.client || vErrors.amount) {
    ElMessage.warning('Заповніть обов\'язкові поля: Клієнт, Сума')
    return
  }

  // Auto-pick warehouse if not set
  if (!form.warehouse_id) {
    try {
      const wRes = await api.get('/api/v1/warehouses?limit=1')
      if (wRes.data?.[0]) form.warehouse_id = wRes.data[0].id
      else { ElMessage.warning('Не знайдено жодного складу'); return }
    } catch { ElMessage.warning('Не вдалося отримати склад'); return }
  }

  saving.value = true
  try {
    // Merge NP branch into attributes_values (JSONB)
    const mergedAttrs = { ...form.attributes_values }
    if (form.np_branch) mergedAttrs._np_branch = form.np_branch
    else                delete mergedAttrs._np_branch
    if (form.next_contact_channel) mergedAttrs._next_contact_channel = form.next_contact_channel
    else                           delete mergedAttrs._next_contact_channel
    if (form.next_contact_comment) mergedAttrs._next_contact_comment = form.next_contact_comment
    else                           delete mergedAttrs._next_contact_comment

    if (!form.manager_id && currentUserId.value) form.manager_id = currentUserId.value

    const payload = {
      order_number:       form.order_number,
      order_date:         form.order_date,
      counterparty_id:    form.counterparty_id,
      warehouse_id:       form.warehouse_id,
      total_amount:       form.total_amount,
      discount_percent:   form.discount_percent,
      crm_stage:          form.crm_stage,
      channel:            form.channel,
      lead_source_id:     form.lead_source_id,
      city:               form.city,
      delivery_type:      form.delivery_type,
      delivery_method_id: form.delivery_method_id,
      attributes_values:  mergedAttrs,
      paid_amount:        form.paid_amount,
      payment_status:     form.payment_status,
      payment_status_id:  form.payment_status_id,
      prepayment_percent: form.prepayment_percent,
      prepayment_amount:  form.prepayment_amount,
      deadline_date:      form.deadline_date,
      next_contact_at:    form.next_contact_at,
      priority:           form.priority,
      priority_id:        form.priority_id,
      manager_id:         form.manager_id,
      cancel_reason_id:   form.cancel_reason_id,
      client_type_id:     form.client_type_id,
      comment:            form.comment,
      internal_notes:     form.internal_notes,
      reference_photo:    form.reference_photo,

      lines: form.product_id ? [{
        product_id: form.product_id,
        quantity:   1,
        price:      form.total_amount,
        total:      form.total_amount,
      }] : [],
    }

    // 1. Save / update the order
    let savedOrder
    if (orderId.value) {
      const res = await api.put(`/api/v1/orders/${orderId.value}`, payload)
      savedOrder = res.data
    } else {
      const res = await api.post('/api/v1/orders', payload)
      savedOrder = res.data
    }

    // 2. If "send to production" — call dedicated endpoint that sets stage + creates ProductionOrder
    if (action === 'production') {
      try {
        const prodRes = await api.post(`/api/v1/orders/${savedOrder.id}/send-to-production`)
        ElMessage.success(`Передано у виробництво! Завдання ${prodRes.data.production_order_number} створено`)
        router.push(`/production/orders/${prodRes.data.production_order_id}`)
        return
      } catch (err) {
        ElMessage.error('Замовлення збережено, але помилка при створенні завдання: ' + (err.response?.data?.detail || ''))
        router.push(`/crm/orders/${savedOrder.id}`)
        return
      }
    }

    ElMessage.success('Збережено як чернетку')
    router.push(`/crm/orders/${savedOrder.id}`)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка збереження')
  } finally {
    saving.value = false
  }
}

// ─── Load ─────────────────────────────────────────────────────────────────────
const loadData = async () => {
  loading.value = true
  try {
    if (!userStore.user) await userStore.fetchUser().catch(() => {})

    const [pRes, cpRes, usersRes] = await Promise.allSettled([
      api.get('/api/v1/products?limit=500'),
      api.get('/api/v1/counterparties?limit=500&is_customer=true'),
      api.get('/users/colleagues'),
    ])
    products.value       = pRes.status       === 'fulfilled' ? pRes.value.data       : []
    counterparties.value = cpRes.status      === 'fulfilled' ? cpRes.value.data      : []
    users.value          = usersRes.status   === 'fulfilled' ? usersRes.value.data   : []
    if (!orderId.value && !form.manager_id && currentUserId.value) {
      form.manager_id = currentUserId.value
    }

    // 1. Load Dictionaries (always needed, even for new orders)
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
      console.warn('Non-critical dictionaries failed to load', e)
    }

    // Ensure dictionaries have fallback data if API returns empty
    if (!communicationTypes.value || communicationTypes.value.length === 0) {
      communicationTypes.value = [...defaultCommTypes]
    }
    if (!contactResults.value || contactResults.value.length === 0) {
      contactResults.value = [...defaultContactResults]
    }
    if (!leadSources.value || leadSources.value.length === 0) {
      // Use comm types as fallback for lead sources if empty
      leadSources.value = communicationTypes.value.map(ct => ({ id: ct.code, name: ct.name, color: '#6366f1' }))
    }

    // 2. Load existing Order data
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}`)
      const o = res.data
      Object.assign(form, o)
      // Map new fields
      form.lead_source_id = o.lead_source_id
      form.delivery_method_id = o.delivery_method_id
      form.payment_status_id = o.payment_status_id
      form.priority_id = o.priority_id
      form.cancel_reason_id = o.cancel_reason_id
      form.client_type_id = o.client_type_id
      Object.assign(form, {
        order_number:    o.order_number,
        order_date:      o.order_date,
        counterparty_id: o.counterparty_id,
        warehouse_id:    o.warehouse_id,
        product_id:      o.lines?.[0]?.product_id || null,
        crm_stage:       o.crm_stage || 'new',
        channel:         o.channel,
        city:            o.city,
        delivery_type:   o.delivery_type,
        attributes_values: (() => {
          const av = { ...(o.attributes_values || {}) }
          delete av._np_branch; delete av._client_status
          return av
        })(),
        np_branch:        o.attributes_values?._np_branch || null,
        next_contact_channel: o.attributes_values?._next_contact_channel || 'CALL',
        next_contact_comment: o.attributes_values?._next_contact_comment || null,
        next_contact_at:  o.next_contact_at || null,
        contact_attempts: o.contact_attempts || 0,
        total_amount:     Number(o.total_amount),
        paid_amount:     Number(o.paid_amount || 0),
        payment_status:  o.payment_status || 'unpaid',
        prepayment_percent: o.prepayment_percent ? Number(o.prepayment_percent) : null,
        prepayment_amount:  o.prepayment_amount ? Number(o.prepayment_amount) : null,
        deadline_date:   o.deadline_date,
        next_contact_date: o.next_contact_date,
        priority:        o.priority || 'normal',
        manager_id:      o.manager_id,
        comment:         o.comment,
        internal_notes:  o.internal_notes,
        reference_photo: o.reference_photo,
        discount_percent: Number(o.discount_percent || 0),
      })
      contactCommType.value = form.next_contact_channel || contactCommType.value
      if (form.product_id) await onProductChange(form.product_id)

      const cp = counterparties.value.find(c => c.id === form.counterparty_id)
      if (cp) {
        clientName.value = cp.name
        clientPhone.value = cp.phone || ''
      }

      await loadContacts()
    }
  } catch (err) {
    ElMessage.error('Помилка завантаження: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
