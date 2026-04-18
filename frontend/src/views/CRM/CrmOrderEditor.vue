<template>
  <div class="crm-editor-page">

    <!-- ===== TOP BAR ===== -->
    <div class="crm-top-bar">
      <button class="crm-back-btn" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div class="crm-top-stages">
        <button
          v-for="(stage, idx) in stages"
          :key="stage.key"
          class="stage-pill"
          :class="{ active: form.crm_stage === stage.key, past: isPassedStage(idx) }"
          @click="setStage(stage.key)"
        >
          <span class="stage-pill-num">{{ idx + 1 }}</span>
          {{ stage.label }}
        </button>
      </div>
      <div class="crm-top-actions">
        <button class="crm-draft-btn" @click="save('draft')" :disabled="saving">
          Записати чернетку
        </button>
        <button class="crm-save-btn" @click="save('production')" :disabled="saving">
          <el-icon><Promotion /></el-icon>
          Зберегти та передати у виробництво
        </button>
      </div>
    </div>

    <!-- ===== BODY ===== -->
    <div class="crm-body" v-loading="loading">
      <div class="crm-left-col">

        <!-- ══ CLIENT BLOCK ══ -->
        <div class="crm-section">
          <div class="crm-section-head">
            <span class="crm-section-title">Клієнт</span>
            <el-select
              v-model="form.counterparty_id"
              filterable
              clearable
              placeholder="Оберіть або введіть клієнта"
              class="cp-select"
              @change="onCounterpartyChange"
            >
              <el-option
                v-for="cp in counterparties"
                :key="cp.id"
                :label="cp.name"
                :value="cp.id"
              />
            </el-select>
            <button class="crm-link-btn" @click="showNewClientDialog = true">
              <el-icon><Plus /></el-icon> Новий клієнт
            </button>
          </div>

          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Ім'я та прізвище</label>
              <el-input v-model="clientName" placeholder="Олена Ковальчук" />
            </div>
            <div class="crm-field">
              <label class="crm-label">Телефон</label>
              <el-input v-model="clientPhone" placeholder="+380 96 123 45 67" />
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Канал звернення</label>
            <div class="channel-pills">
              <button
                v-for="ch in channels"
                :key="ch.value"
                class="channel-pill"
                :class="[`ch-${ch.value}`, form.channel === ch.value ? 'active' : '']"
                @click="form.channel = form.channel === ch.value ? null : ch.value"
              >{{ ch.label }}</button>
            </div>
          </div>

          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Місто</label>
              <el-input v-model="form.city" placeholder="Київ" />
            </div>
            <div class="crm-field">
              <label class="crm-label">Доставка</label>
              <el-select v-model="form.delivery_type" placeholder="Оберіть" clearable style="width:100%">
                <el-option value="nova_poshta"  label="Нова Пошта" />
                <el-option value="ukrposhta"    label="Укрпошта" />
                <el-option value="courier"      label="Кур'єр" />
                <el-option value="pickup"       label="Самовивіз" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- ══ PRODUCT BLOCK ══ -->
        <div class="crm-section">
          <div class="crm-section-head">
            <span class="crm-section-title">Виріб</span>
            <span class="crm-attr-hint" v-if="productAttributes.length">
              <el-icon><Check /></el-icon>
              характеристики підтягнуто ({{ productAttributes.length }})
            </span>
          </div>

          <div class="crm-field">
            <label class="crm-label">Оберіть виріб з номенклатури</label>
            <el-select
              v-model="form.product_id"
              filterable
              placeholder="Почніть вводити назву..."
              style="width:100%"
              @change="onProductChange"
            >
              <el-option
                v-for="p in products"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>
            <p class="product-hint" v-if="selectedProduct">
              {{ selectedProduct.name }}
              <span v-if="productAttributes.length"> — підтягнуто {{ productAttributes.length }} характеристики</span>
            </p>
          </div>

          <!-- Dynamic attribute pills -->
          <div v-if="productAttributes.length" class="attributes-block">
            <div
              v-for="attr in productAttributes"
              :key="attr.id"
              class="attr-group"
            >
              <label class="crm-label">
                З картки товару: <strong>{{ attr.name }}</strong>
              </label>

              <!-- SELECT / COLOR — pill chooser -->
              <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="attr-pills">
                <button
                  v-for="opt in attr.options"
                  :key="opt.id"
                  class="attr-pill"
                  :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
                  :style="attr.type === 'COLOR' && opt.color_code
                    ? { '--dot-color': opt.color_code }
                    : {}"
                  @click="setAttrValue(attr.id, opt.value)"
                >
                  <span v-if="attr.type === 'COLOR' && opt.color_code" class="attr-color-dot" :style="{ background: opt.color_code }" />
                  {{ opt.value }}
                </button>
              </div>

              <!-- DIMENSIONS — two inputs W × H -->
              <div v-else-if="attr.type === 'DIMENSIONS'" class="attr-dims">
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.w"
                  @update:model-value="v => setAttrDim(attr.id, 'w', v)"
                  :min="1" placeholder="Ш" size="small" style="width:90px"
                />
                <span class="dims-sep">×</span>
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.h"
                  @update:model-value="v => setAttrDim(attr.id, 'h', v)"
                  :min="1" placeholder="В" size="small" style="width:90px"
                />
                <span class="dims-unit">см</span>
              </div>

              <!-- TEXT / NUMBER — plain input -->
              <div v-else>
                <el-input
                  :model-value="form.attributes_values?.[attr.id]"
                  @update:model-value="v => setAttrValue(attr.id, v)"
                  size="small"
                  :placeholder="attr.name"
                  style="width:100%"
                />
              </div>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Коментар до виробу</label>
            <el-input
              v-model="form.comment"
              type="textarea"
              :rows="3"
              placeholder="Індивідуальні побажання клієнта..."
            />
          </div>

          <!-- Reference photo -->
          <div class="crm-field">
            <label class="crm-label">Фото референс від клієнта</label>
            <div class="photo-upload-zone" @click="triggerPhotoUpload">
              <img v-if="form.reference_photo" :src="form.reference_photo" class="photo-preview" />
              <div v-else class="photo-placeholder">
                <el-icon><Picture /></el-icon>
                <span>+ Завантажити фото</span>
              </div>
            </div>
            <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="uploadPhoto" />
          </div>
        </div>

        <!-- ══ MATERIALS CHECK ══ -->
        <div class="crm-section" v-if="form.product_id">
          <div class="crm-section-head">
            <span class="crm-section-title">Матеріали на складі</span>
            <span class="mat-status-badge" :class="materialCheck.has_issues ? 'mat-warn' : 'mat-ok'">
              {{ materialCheck.has_issues ? 'є проблеми' : 'все є' }}
            </span>
          </div>

          <div v-if="materialsLoading" class="mat-loading">
            <el-icon class="is-loading"><Loading /></el-icon> Перевіряємо...
          </div>
          <div v-else-if="materialCheck.items.length" class="mat-list">
            <div
              v-for="item in materialCheck.items"
              :key="item.component_id"
              class="mat-row"
              :class="`mat-${item.status}`"
            >
              <span class="mat-name">{{ item.component_name }}</span>
              <span class="mat-req">потрібно: {{ formatQty(item.required_qty) }} {{ item.unit_of_measure }}</span>
              <span class="mat-stock-badge">
                <span class="mat-stock-icon">{{ item.status === 'ok' ? '[+]' : item.status === 'low' ? '[~]' : '[!]' }}</span>
                {{ formatQty(item.available_qty) }} {{ item.unit_of_measure }}
              </span>
            </div>
            <div v-if="materialCheck.has_issues" class="mat-order-row">
              <span>Не вистачає матеріалів — замовте до запуску</span>
              <button class="mat-order-btn" @click="goToPurchases">
                <el-icon><Promotion /></el-icon> Замовити
              </button>
            </div>
          </div>
          <div v-else class="mat-empty">Специфікація не знайдена для цього товару</div>
        </div>

      </div><!-- /left col -->

      <!-- ─── RIGHT SIDEBAR ─────────────────────────────────────── -->
      <div class="crm-right-col">

        <!-- ══ SUMMARY ══ -->
        <div class="crm-section crm-summary">
          <div class="crm-section-title" style="margin-bottom:10px">Підсумок замовлення</div>

          <div class="summary-stats">
            <div class="sum-stat">
              <p class="sum-stat-val">{{ formatCurrency(form.total_amount) }}</p>
              <p class="sum-stat-label">сума грн</p>
            </div>
            <div class="sum-stat">
              <p class="sum-stat-val">{{ formatCurrency(form.prepayment_amount || 0) }}</p>
              <p class="sum-stat-label">передоплата</p>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Сума замовлення (грн)</label>
            <el-input-number
              v-model="form.total_amount"
              :min="0" :precision="0"
              style="width:100%"
              @change="calcPrepayment"
            />
          </div>

          <div class="crm-field">
            <label class="crm-label">Передоплата</label>
            <div class="prepay-pills">
              <button
                v-for="pct in [30, 50, 100]"
                :key="pct"
                class="prepay-pill"
                :class="{ active: form.prepayment_percent === pct }"
                @click="setPrepayPct(pct)"
              >{{ pct }}%</button>
              <button
                class="prepay-pill pay-none"
                :class="{ active: form.prepayment_percent === 0 }"
                @click="setPrepayPct(0)"
              >Без передоплати</button>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Статус оплати</label>
            <div class="pay-status-pills">
              <button
                v-for="ps in paymentStatuses"
                :key="ps.value"
                class="pay-status-pill"
                :class="[`psp-${ps.value}`, form.payment_status === ps.value ? 'active' : '']"
                @click="form.payment_status = ps.value"
              >{{ ps.label }}</button>
            </div>
          </div>

          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Дата заявки</label>
              <el-date-picker
                v-model="form.order_date"
                type="date"
                format="DD.MM.YYYY"
                value-format="YYYY-MM-DD"
                style="width:100%"
              />
            </div>
            <div class="crm-field">
              <label class="crm-label">Дедлайн</label>
              <el-date-picker
                v-model="form.deadline_date"
                type="date"
                format="DD.MM.YYYY"
                value-format="YYYY-MM-DD"
                style="width:100%"
              />
            </div>
          </div>
          <p class="deadline-hint" v-if="!form.deadline_date">
            Дедлайн розраховується автоматично по типу виробу
          </p>
        </div>

        <!-- ══ PRODUCTION ══ -->
        <div class="crm-section">
          <div class="crm-section-title" style="margin-bottom:10px">Виробництво</div>

          <div class="crm-field">
            <label class="crm-label">Відповідальний майстер</label>
            <el-select v-model="form.manager_id" clearable placeholder="Оберіть майстра" style="width:100%">
              <el-option
                v-for="u in users"
                :key="u.id"
                :label="u.full_name || u.email"
                :value="u.id"
              />
            </el-select>
          </div>

          <div class="crm-field">
            <label class="crm-label">Пріоритет</label>
            <div class="priority-pills">
              <button
                v-for="p in priorities"
                :key="p.value"
                class="priority-pill"
                :class="[`pp-${p.value}`, form.priority === p.value ? 'active' : '']"
                @click="form.priority = p.value"
              >{{ p.label }}</button>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Наступний контакт</label>
            <el-date-picker
              v-model="form.next_contact_date"
              type="date"
              format="DD.MM.YYYY"
              value-format="YYYY-MM-DD"
              style="width:100%"
              placeholder="Коли передзвонити?"
            />
          </div>
        </div>

        <!-- ══ HISTORY ══ -->
        <div class="crm-section">
          <div class="crm-section-title" style="margin-bottom:8px">Історія</div>
          <div class="history-list">
            <div class="history-item" v-for="(h, i) in history" :key="i">
              <span class="h-dot" />
              <div class="h-body">
                <span class="h-text">{{ h.text }}</span>
                <span class="h-time">{{ h.time }}</span>
              </div>
            </div>
          </div>

          <div class="crm-field" style="margin-top:10px">
            <label class="crm-label">Додати нотатку</label>
            <el-input
              v-model="form.internal_notes"
              type="textarea"
              :rows="3"
              placeholder="Запис менеджера..."
            />
          </div>
        </div>

      </div><!-- /right col -->
    </div><!-- /body -->

    <!-- ===== NEW CLIENT DIALOG ===== -->
    <el-dialog v-model="showNewClientDialog" title="Новий клієнт" width="460px">
      <div class="crm-grid-2">
        <div class="crm-field">
          <label class="crm-label">Ім'я та прізвище *</label>
          <el-input v-model="newClient.name" />
        </div>
        <div class="crm-field">
          <label class="crm-label">Телефон</label>
          <el-input v-model="newClient.phone" />
        </div>
      </div>
      <div class="crm-field">
        <label class="crm-label">Email</label>
        <el-input v-model="newClient.email" />
      </div>
      <template #footer>
        <el-button @click="showNewClientDialog = false">Скасувати</el-button>
        <el-button type="primary" @click="createNewClient" :loading="savingClient">Створити</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Plus, Check, Promotion, Picture, Loading, Clock
} from '@element-plus/icons-vue'
import apiClient from '@/api/index.js'

const router = useRouter()
const route  = useRoute()
const orderId = computed(() => route.params.id !== 'new' ? route.params.id : null)

// ─── State ────────────────────────────────────────────────────────────────────
const loading        = ref(false)
const saving         = ref(false)
const savingClient   = ref(false)
const materialsLoading = ref(false)
const products       = ref([])
const counterparties = ref([])
const users          = ref([])
const productAttributes = ref([])
const showNewClientDialog = ref(false)
const photoInput     = ref(null)

const materialCheck = reactive({ has_issues: false, items: [] })

const newClient = reactive({ name: '', phone: '', email: '' })

const form = reactive({
  order_number:   'Авто',
  order_date:     new Date().toISOString().slice(0, 10),
  counterparty_id: null,
  warehouse_id:   null,
  product_id:     null,
  crm_stage:      route.query.stage || 'new',
  channel:        null,
  city:           null,
  delivery_type:  null,
  attributes_values: {},
  total_amount:   0,
  paid_amount:    0,
  payment_status: 'unpaid',
  prepayment_percent: null,
  prepayment_amount:  null,
  deadline_date:  null,
  next_contact_date: null,
  priority:       'normal',
  manager_id:     null,
  comment:        null,
  internal_notes: null,
  reference_photo: null,
  discount_percent: 0,
})

// Client quick-edit fields (synced to counterparty)
const clientName  = ref('')
const clientPhone = ref('')

// ─── Config ───────────────────────────────────────────────────────────────────
const stages = [
  { key: 'new',        label: 'Нова заявка' },
  { key: 'processing', label: 'В обробці' },
  { key: 'confirmed',  label: 'Підтверджено' },
  { key: 'payment',    label: 'Оплата' },
  { key: 'production', label: 'У виробництві' },
  { key: 'done',       label: 'Виконано' },
]
const stageIndex = computed(() => stages.findIndex(s => s.key === form.crm_stage))
const isPassedStage = (idx) => idx < stageIndex.value

const channels = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'website',   label: 'Сайт' },
  { value: 'referral',  label: 'Сарафанка' },
  { value: 'telegram',  label: 'Telegram' },
  { value: 'olx',       label: 'OLX' },
  { value: 'phone',     label: 'Телефон' },
]
const priorities = [
  { value: 'normal',   label: 'Звичайний' },
  { value: 'urgent',   label: 'Терміновий' },
  { value: 'critical', label: 'Критичний' },
]
const paymentStatuses = [
  { value: 'unpaid',  label: 'Не оплачено' },
  { value: 'partial', label: 'Частково' },
  { value: 'paid',    label: 'Оплачено' },
]

// ─── Computed ─────────────────────────────────────────────────────────────────
const selectedProduct = computed(() => products.value.find(p => p.id === form.product_id) || null)

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
  } else {
    form.prepayment_amount = 0
  }
}

// ─── Stage ────────────────────────────────────────────────────────────────────
const setStage = (key) => { form.crm_stage = key }

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
      const res = await apiClient.get(`/attributes/category/${product.category}`)
      productAttributes.value = res.data?.filter(a => !a.is_archived) || []
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
      const res = await apiClient.get(`/orders/${orderId.value}/material-check?product_id=${productId}`)
      Object.assign(materialCheck, res.data)
    } else {
      // For new orders, fetch spec directly
      const specRes = await apiClient.get(`/products/${productId}/specifications`)
      const specs = specRes.data || []
      const defaultSpec = specs.find(s => s.is_default && s.is_active) || specs[0]
      if (!defaultSpec?.items?.length) { materialsLoading.value = false; return }

      // Get stock for each component
      const items = []
      let hasIssues = false
      for (const item of defaultSpec.items) {
        const stockRes = await apiClient.get(`/products/${item.component_id}/stock`)
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
const triggerPhotoUpload = () => photoInput.value?.click()
const uploadPhoto = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await apiClient.post('/upload/image', fd)
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
    const res = await apiClient.post('/counterparties', {
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

// ─── Save ─────────────────────────────────────────────────────────────────────
const save = async (action) => {
  if (!form.counterparty_id) { ElMessage.warning('Оберіть клієнта'); return }
  if (!form.warehouse_id) {
    // Auto-pick first warehouse
    const wRes = await apiClient.get('/warehouses?limit=1')
    if (wRes.data?.[0]) form.warehouse_id = wRes.data[0].id
    else { ElMessage.warning('Не знайдено жодного складу'); return }
  }

  saving.value = true
  try {
    const payload = {
      order_number:       form.order_number,
      order_date:         form.order_date,
      counterparty_id:    form.counterparty_id,
      warehouse_id:       form.warehouse_id,
      total_amount:       form.total_amount,
      discount_percent:   form.discount_percent,
      crm_stage:          action === 'production' ? 'production' : form.crm_stage,
      channel:            form.channel,
      city:               form.city,
      delivery_type:      form.delivery_type,
      attributes_values:  form.attributes_values,
      paid_amount:        form.paid_amount,
      payment_status:     form.payment_status,
      prepayment_percent: form.prepayment_percent,
      prepayment_amount:  form.prepayment_amount,
      deadline_date:      form.deadline_date,
      next_contact_date:  form.next_contact_date,
      priority:           form.priority,
      manager_id:         form.manager_id,
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

    let savedOrder
    if (orderId.value) {
      const res = await apiClient.put(`/orders/${orderId.value}`, payload)
      savedOrder = res.data
    } else {
      const res = await apiClient.post('/orders', payload)
      savedOrder = res.data
    }

    ElMessage.success(action === 'production' ? 'Передано у виробництво!' : 'Збережено як чернетку')
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
    const [pRes, cpRes, usersRes] = await Promise.all([
      apiClient.get('/products?limit=500&is_active=true'),
      apiClient.get('/counterparties?limit=500&is_customer=true'),
      apiClient.get('/users?limit=200'),
    ])
    products.value       = pRes.data
    counterparties.value = cpRes.data
    users.value          = usersRes.data

    if (orderId.value) {
      const res = await apiClient.get(`/orders/${orderId.value}`)
      const o = res.data
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
        attributes_values: o.attributes_values || {},
        total_amount:    Number(o.total_amount),
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
      if (form.product_id) await onProductChange(form.product_id)
      const cp = counterparties.value.find(c => c.id === form.counterparty_id)
      if (cp) { clientName.value = cp.name; clientPhone.value = cp.phone || '' }
    }
  } catch {
    ElMessage.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* ─── Page ────────────────────────────────────────────────────────────────── */
.crm-editor-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f1f5f9;
  font-family: 'Inter', sans-serif;
}

/* ─── Top Bar ─────────────────────────────────────────────────────────────── */
.crm-top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.crm-back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 8px;
  border: 1px solid #e2e8f0; background: transparent;
  color: #64748b; cursor: pointer;
}
.crm-back-btn:hover { background: #f8fafc; }

.crm-top-stages {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 0;
  overflow-x: auto;
}
.stage-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border-right: none;
  white-space: nowrap;
  transition: background 0.12s, color 0.12s;
}
.stage-pill:first-child { border-radius: 8px 0 0 8px; }
.stage-pill:last-child  { border-radius: 0 8px 8px 0; border-right: 1px solid #e2e8f0; }
.stage-pill.past   { background: #e0e7ff; color: #4338ca; border-color: #c7d2fe; }
.stage-pill.active { background: #6366f1; color: #fff; border-color: #6366f1; z-index: 1; }
.stage-pill-num {
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(255,255,255,.3);
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.stage-pill.active .stage-pill-num { background: rgba(255,255,255,.35); }

.crm-top-actions { display: flex; gap: 8px; align-items: center; }
.crm-draft-btn {
  padding: 7px 14px; border-radius: 8px;
  border: 1px solid #e2e8f0; background: #fff;
  font-size: 12px; font-weight: 500; color: #475569; cursor: pointer;
}
.crm-draft-btn:hover { background: #f8fafc; }
.crm-save-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
}
.crm-save-btn:hover { background: #4f46e5; }

/* ─── Body ────────────────────────────────────────────────────────────────── */
.crm-body {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}
.crm-left-col  { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 14px; }
.crm-right-col { width: 320px; flex-shrink: 0; display: flex; flex-direction: column; gap: 14px; }

/* ─── Section ─────────────────────────────────────────────────────────────── */
.crm-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  border: 1px solid #e2e8f0;
}
.crm-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.crm-section-title { font-size: 14px; font-weight: 700; color: #1e293b; }
.crm-attr-hint {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; color: #10b981; font-weight: 500;
}
.cp-select { flex: 1; min-width: 200px; }
.crm-link-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 6px;
  border: 1px dashed #c7d2fe; background: transparent;
  color: #6366f1; font-size: 12px; cursor: pointer;
}
.crm-link-btn:hover { background: #eef2ff; }

/* ─── Fields ──────────────────────────────────────────────────────────────── */
.crm-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.crm-field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.crm-label { font-size: 12px; font-weight: 500; color: #64748b; }

/* ─── Channel pills ───────────────────────────────────────────────────────── */
.channel-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.channel-pill {
  padding: 4px 12px; border-radius: 99px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; color: #475569;
  cursor: pointer; transition: all 0.12s;
}
.channel-pill.active { border-color: currentColor; }
.ch-instagram.active { background: #fce7f3; color: #9d174d; border-color: #f9a8d4; }
.ch-website.active   { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
.ch-referral.active  { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }
.ch-telegram.active  { background: #e0f2fe; color: #0369a1; border-color: #7dd3fc; }
.ch-olx.active       { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
.ch-phone.active     { background: #f3e8ff; color: #6b21a8; border-color: #d8b4fe; }

/* ─── Product hint ────────────────────────────────────────────────────────── */
.product-hint { font-size: 11px; color: #94a3b8; margin: 4px 0 0; }

/* ─── Attributes block ────────────────────────────────────────────────────── */
.attributes-block { display: flex; flex-direction: column; gap: 12px; margin-bottom: 12px; }
.attr-group { border-left: 3px solid #e0e7ff; padding-left: 10px; }
.attr-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.attr-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; color: #475569; cursor: pointer;
  transition: all 0.12s;
}
.attr-pill.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 600; }
.attr-color-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }

.attr-dims { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.dims-sep  { font-size: 16px; color: #94a3b8; }
.dims-unit { font-size: 12px; color: #94a3b8; }

/* ─── Photo upload ────────────────────────────────────────────────────────── */
.photo-upload-zone {
  border: 2px dashed #e2e8f0; border-radius: 10px;
  min-height: 100px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; overflow: hidden; transition: border-color 0.15s;
}
.photo-upload-zone:hover { border-color: #6366f1; }
.photo-placeholder {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: #94a3b8; font-size: 13px;
}
.photo-placeholder .el-icon { font-size: 24px; }
.photo-preview { max-width: 100%; max-height: 200px; border-radius: 8px; }

/* ─── Material check ──────────────────────────────────────────────────────── */
.mat-status-badge {
  font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 99px;
}
.mat-ok   { background: #d1fae5; color: #065f46; }
.mat-warn { background: #fef3c7; color: #92400e; }
.mat-loading { color: #94a3b8; font-size: 13px; display: flex; align-items: center; gap: 6px; }

.mat-list { display: flex; flex-direction: column; gap: 4px; }
.mat-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 10px; border-radius: 8px; font-size: 12px;
}
.mat-ok      { background: #f0fdf4; }
.mat-low     { background: #fffbeb; }
.mat-missing { background: #fff1f2; }
.mat-name  { flex: 1; font-weight: 500; color: #1e293b; }
.mat-req   { color: #94a3b8; white-space: nowrap; }
.mat-stock-badge { font-weight: 700; white-space: nowrap; }
.mat-ok      .mat-stock-badge { color: #16a34a; }
.mat-low     .mat-stock-badge { color: #d97706; }
.mat-missing .mat-stock-badge { color: #dc2626; }

.mat-order-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 10px; background: #fff1f2; border-radius: 8px;
  font-size: 12px; color: #9f1239; font-weight: 500;
}
.mat-order-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; border-radius: 7px; border: none;
  background: #ef4444; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
}
.mat-empty { font-size: 12px; color: #94a3b8; text-align: center; padding: 10px; }

/* ─── Summary ─────────────────────────────────────────────────────────────── */
.summary-stats {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; margin-bottom: 14px;
}
.sum-stat {
  background: #f8fafc; border-radius: 8px; padding: 10px 12px; text-align: center;
}
.sum-stat-val   { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 2px; }
.sum-stat-label { font-size: 11px; color: #94a3b8; margin: 0; }

.prepay-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.prepay-pill {
  padding: 4px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; color: #475569; cursor: pointer;
}
.prepay-pill.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 700; }
.prepay-pill.pay-none.active { background: #f1f5f9; border-color: #94a3b8; color: #475569; }

.pay-status-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.pay-status-pill {
  padding: 5px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; cursor: pointer;
}
.psp-unpaid.active  { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }
.psp-partial.active { background: #fef3c7; border-color: #fcd34d; color: #92400e; }
.psp-paid.active    { background: #d1fae5; border-color: #6ee7b7; color: #065f46; }

.deadline-hint { font-size: 11px; color: #94a3b8; margin: 4px 0 0; }

/* ─── Priority pills ──────────────────────────────────────────────────────── */
.priority-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.priority-pill {
  padding: 5px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; cursor: pointer;
}
.pp-normal.active   { background: #eef2ff; border-color: #6366f1; color: #4338ca; }
.pp-urgent.active   { background: #fffbeb; border-color: #fcd34d; color: #92400e; }
.pp-critical.active { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }

/* ─── History ─────────────────────────────────────────────────────────────── */
.history-list { display: flex; flex-direction: column; gap: 6px; }
.history-item { display: flex; align-items: flex-start; gap: 8px; }
.h-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #6366f1; margin-top: 4px; flex-shrink: 0;
}
.h-body { display: flex; flex-direction: column; gap: 1px; }
.h-text { font-size: 13px; color: #1e293b; }
.h-time { font-size: 11px; color: #94a3b8; }
</style>
