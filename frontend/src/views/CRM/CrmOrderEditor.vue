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

    <!-- BREADCRUMB PROGRESS -->
    <div class="crm-breadcrumb-progress">
      <div class="bc-item" :class="{ active: currentStep >= 1 }">
        <div class="bc-dot"></div> Клієнт
      </div>
      <div class="bc-sep"></div>
      <div class="bc-item" :class="{ active: currentStep >= 2 }">
        <div class="bc-dot"></div> Виріб
      </div>
      <div class="bc-sep"></div>
      <div class="bc-item" :class="{ active: currentStep >= 3 }">
        <div class="bc-dot"></div> Логістика
      </div>
      <div class="bc-sep"></div>
      <div class="bc-item" :class="{ active: currentStep >= 4 }">
        <div class="bc-dot"></div> Фінанси
      </div>
    </div>

    <div class="crm-body">
      <div class="crm-layout-2col">
        
        <!-- LEFT COLUMN (65%) -->
        <div class="crm-content-left">
          
          <!-- Block 1: Клієнт (Premium Redesign) -->
          <div class="crm-block-card card-client-premium">
            <div class="block-header-modern">
              <div class="bh-title">
                <el-icon class="icon-pulse"><User /></el-icon> 
                <span>Дані клієнта</span>
              </div>
              <div class="bh-actions">
                <el-button v-if="form.counterparty_id" link @click="showClientDrawer = true">
                  Повний профіль <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="client-form-body">
              <!-- Row 1: Search -->
              <div class="client-search-row">
                <el-select
                  v-model="form.counterparty_id"
                  filterable
                  remote
                  :remote-method="searchCounterparties"
                  placeholder="Введіть ім'я або номер телефону..."
                  class="modern-search-bar"
                  @change="onClientChange"
                >
                  <template #prefix><el-icon><Search /></el-icon></template>
                  <el-option
                    v-for="cp in counterparties"
                    :key="cp.id"
                    :label="cp.name + (cp.phone ? ' (' + cp.phone + ')' : '')"
                    :value="cp.id"
                  />
                </el-select>
                <el-button @click="openCreateCounterparty" type="primary" class="btn-add-modern">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>

              <!-- Row 2: Lead Source Tiles (Replacing Dropdown) -->
              <div class="source-selection-container">
                <span class="mini-label-modern">Звідки прийшов клієнт? (Джерело)</span>
                <div class="source-tiles-grid">
                  <div 
                    v-for="src in leadSourceIcons" 
                    :key="src.id"
                    class="source-tile"
                    :class="[src.id, { active: form.lead_source_id === src.id }]"
                    @click="form.lead_source_id = src.id"
                  >
                    <div class="st-icon">
                      <component :is="src.icon" />
                    </div>
                    <span class="st-label">{{ src.name }}</span>
                    <el-icon v-if="form.lead_source_id === src.id" class="st-check"><Check /></el-icon>
                  </div>
                </div>
              </div>

              <!-- Row 3: Meta (City + Communication Channel) -->
              <div class="client-meta-row">
                <div class="meta-field city">
                  <span class="mini-label-modern">Місто</span>
                  <el-input v-model="form.city" placeholder="Напр. Київ" />
                </div>
                
                <div class="meta-field channels">
                  <span class="mini-label-modern">Канал зв'язку</span>
                  <div class="channel-pills-modern">
                    <div 
                      v-for="ch in channelPills" 
                      :key="ch.code"
                      class="ch-pill-modern"
                      :class="[ch.code, { active: form.channel === ch.code }]"
                      @click="form.channel = ch.code"
                    >
                      <el-icon><component :is="ch.icon" /></el-icon>
                      <span>{{ ch.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Block 2: Виріб / Номенклатура -->
          <div class="crm-block-card card-product">
            <div class="block-title">
              <el-icon><Box /></el-icon> Виріб / Номенклатура
            </div>

            <div class="product-config-split">
              <div class="pc-main">
                <div class="crm-field">
                  <span class="mini-label">Модель</span>
                  <el-select v-model="form.product_id" filterable placeholder="Оберіть модель" class="modern-select" @change="onProductChange" style="width: 100%">
                    <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </div>

                <div class="attributes-block" v-if="productAttributes.length">
                  <div v-for="attr in productAttributes" :key="attr.id" class="attr-group">
                    <span class="mini-label">{{ attr.name }}</span>
                    <div class="attr-pills" v-if="attr.type !== 'dimensions'">
                      <div v-for="opt in attr.options" :key="opt.id" class="attr-pill"
                           :class="{ active: form.attributes_values[attr.id] === opt.id }"
                           @click="form.attributes_values[attr.id] = opt.id">
                        <span v-if="opt.color" class="attr-color-dot" :style="{ background: opt.color }"></span>
                        {{ opt.name }}
                      </div>
                    </div>
                    <div class="attr-dims" v-else>
                      <el-input-number v-model="form.attributes_values[attr.id + '_w']" :precision="0" placeholder="Ширина" />
                      <span class="dims-sep">×</span>
                      <el-input-number v-model="form.attributes_values[attr.id + '_h']" :precision="0" placeholder="Висота" />
                    </div>
                  </div>
                </div>

                <div class="crm-field" style="margin-top: 16px;">
                  <span class="mini-label">Коментар до виробу</span>
                  <el-input type="textarea" v-model="form.comment" :rows="3" placeholder="Деталі..." />
                </div>
              </div>

              <div class="pc-side">
                <span class="mini-label">Фото референс</span>
                <div class="photo-upload-zone-compact" @click="triggerPhotoUpload">
                  <img v-if="form.reference_photo" :src="form.reference_photo" class="photo-preview" />
                  <div v-else class="photo-placeholder">
                    <el-icon><Picture /></el-icon>
                    <span>Завантажити</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Block 3: Аналіз та логістика -->
          <div class="crm-block-card card-logistics">
            <div class="block-title">
              <el-icon><Promotion /></el-icon> Аналіз та логістика
            </div>

            <div class="crm-grid-2">
              <div class="crm-field">
                <span class="mini-label">Склад</span>
                <el-select v-model="form.warehouse_id" style="width: 100%">
                  <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
                </el-select>
              </div>
              <div class="crm-field">
                <span class="mini-label">Тип оплати</span>
                <el-select v-model="form.payment_status_id" style="width: 100%">
                  <el-option v-for="s in paymentStatuses" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
              </div>
            </div>

            <div class="crm-field" style="margin-top: 16px;">
              <span class="mini-label">Доставка</span>
              <el-input v-model="form.delivery_address" placeholder="Адреса або номер відділення" />
            </div>

            <div class="analysis-section" v-if="form.product_id" style="margin-top: 20px;">
              <div class="analysis-header">
                <span class="mini-label">Аналіз матеріалів та комплектації</span>
                <el-tag size="small" type="info" plain>Авто-перевірка</el-tag>
              </div>
              <div class="mat-list-compact">
                <div v-for="m in materials" :key="m.id" class="mat-row-compact" :class="m.status">
                  <span class="mat-name">{{ m.component_name }}</span>
                  <div class="mat-status-val">
                    <span v-if="m.status === 'ok'" class="status-ok">В НАЯВНОСТІ</span>
                    <span v-else class="status-need">ПОТРІБНО: {{ Math.max(0, m.required_qty - m.available_qty) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── RIGHT COLUMN (35%) - STICKY ─── -->
        <div class="crm-sidebar-right">
          <div class="crm-sidebar-tabs">
            <div 
              class="sidebar-tab" 
              :class="{ active: activeSidebarTab === 'summary' }"
              @click="activeSidebarTab = 'summary'"
            >
              <el-icon><Wallet /></el-icon> ПІДСУМОК
            </div>
            <div 
              class="sidebar-tab" 
              :class="{ active: activeSidebarTab === 'activity' }"
              @click="activeSidebarTab = 'activity'"
            >
              <el-icon><List /></el-icon> АКТИВНІСТЬ
              <span class="activity-badge" v-if="contactHistory.length">{{ contactHistory.length }}</span>
            </div>
          </div>

          <div class="sidebar-content-scroll">
            <!-- TAB 1: SUMMARY -->
            <transition name="fade-slide">
              <div v-if="activeSidebarTab === 'summary'" class="tab-pane">
                <div class="crm-block-card card-summary saas-premium-shadow">
                  <div class="summary-total-large">
                    <el-input-number v-model="form.total_amount" :controls="false" class="large-total-input" />
                    <span class="sum-currency">₴</span>
                  </div>

                  <div class="crm-field">
                    <span class="mini-label-modern">Предоплата</span>
                    <div class="prepay-grid">
                      <button v-for="pct in [0, 30, 50, 100]" :key="pct"
                              class="prepay-btn" :class="{ active: isPrepayActive(pct) }"
                              @click="setPrepayPercent(pct)">
                        {{ pct === 0 ? 'Без' : pct + '%' }}
                      </button>
                    </div>
                    <el-input-number v-model="form.prepayment_amount" :controls="false" style="width: 100%; margin-top: 8px;" />
                  </div>

                  <div class="crm-field" style="margin-top: 20px;">
                    <span class="mini-label-modern">Менеджер</span>
                    <el-select v-model="form.manager_id" style="width: 100%">
                      <el-option v-for="u in users" :key="u.id" :label="`${u.first_name} ${u.last_name}`" :value="u.id" />
                    </el-select>
                  </div>

                  <div class="crm-field" style="margin-top: 20px;">
                    <span class="mini-label-modern">Пріоритет</span>
                    <div class="priority-pills">
                      <div v-for="p in priorities" :key="p.id" class="priority-pill"
                           :class="[`pp-${p.code}`, { active: form.priority === p.code }]"
                           @click="form.priority_id = p.id; form.priority = p.code">
                        {{ p.name }}
                      </div>
                    </div>
                  </div>

                  <div class="crm-field" style="margin-top: 20px;">
                    <span class="mini-label-modern">Дедлайн виготовлення</span>
                    <el-date-picker v-model="form.deadline_date" type="date" placeholder="Оберіть дату" style="width: 100%" />
                  </div>

                  <div class="action-buttons-stack">
                    <el-button class="btn-save-main" @click="saveAndClose" :loading="saving" type="primary">ЗБЕРЕГТИ ТА ПЕРЕДАТИ</el-button>
                    <el-button class="btn-draft" @click="saveDraft">ЗБЕРЕГТИ ЯК ЧЕРНЕТКУ</el-button>
                    
                    <div class="quick-comms-group">
                       <el-button size="small" :icon="ChatDotRound">Чат</el-button>
                       <el-button size="small" :icon="Phone">Дзвінок</el-button>
                       <el-button size="small" :icon="ChatDotSquare">SMS</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </transition>

            <!-- TAB 2: ACTIVITY TIMELINE (Alternative for history) -->
            <transition name="fade-slide">
              <div v-if="activeSidebarTab === 'activity'" class="tab-pane">
                <div class="crm-block-card card-activity-timeline">
                  <div class="timeline-header">
                    <span class="mini-label-modern">Останні події</span>
                    <el-button link @click="loadContacts"><el-icon><Refresh /></el-icon></el-button>
                  </div>

                  <div class="activity-feed">
                    <div v-if="!contactHistory.length" class="activity-empty-state">
                      <el-icon><ChatLineRound /></el-icon>
                      <p>Історія взаємодії порожня</p>
                    </div>
                    
                    <div v-for="log in contactHistory" :key="log.id" class="activity-item">
                      <div class="activity-line"></div>
                      <div class="activity-icon-container" :class="log.communication_type.toLowerCase()">
                        <el-icon><component :is="getChannelIcon(log.communication_type)" /></el-icon>
                      </div>
                      <div class="activity-body">
                        <div class="activity-top">
                          <span class="activity-type">{{ getResultHint(log.result) }}</span>
                          <span class="activity-time">{{ formatDate(log.contacted_at) }}</span>
                        </div>
                        <p class="activity-text" v-if="log.note">{{ log.note }}</p>
                        <div class="activity-meta" v-if="log.manager_name">
                          <el-avatar :size="16" class="mini-avatar">M</el-avatar>
                          <span>Менеджер: {{ log.manager_name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="activity-footer">
                    <el-button type="primary" plain round size="small" @click="showClientDrawer = true">
                      ДОДАТИ КОНТАКТ
                    </el-button>
                  </div>
                </div>
              </div>
            </transition>
          </div>
          
          <!-- REMINDERS WIDGET (Secondary) -->
          <div class="crm-block-card card-reminder-mini" v-if="missedTasks.length">
             <div class="rem-header">
                <el-icon class="rem-icon-anim"><Bell /></el-icon>
                <span>Нагадування</span>
             </div>
             <div v-for="task in missedTasks" :key="task.id" class="reminder-item-mini">
                <div class="rem-info">
                  <span class="rem-time">{{ formatDate(task.scheduled_at) }}</span>
                  <p class="rem-text">Передзвонити клієнту</p>
                </div>
                <el-button type="warning" size="small" circle :icon="Check" @click="completeTask(task.id)" />
             </div>
          </div>
        </div>

      </div>
    </div>

    <!-- CLIENT DRAWER (HISTORY & PROFILE) -->
    <el-drawer
      v-model="showClientDrawer"
      title="Профіль клієнта та історія"
      direction="rtl"
      size="450px"
    >
      <div v-if="clientProfile" class="client-drawer-content">
        <div class="drawer-section">
          <span class="mini-label">Основна інформація</span>
          <div class="profile-main">
            <h3>{{ clientProfile.name }}</h3>
            <p>{{ clientProfile.phone }}</p>
            <div class="profile-stats">
              <div class="stat-box">
                <b>{{ formatCurrency(clientProfile.ltv) }} ₴</b>
                <span>LTV</span>
              </div>
              <div class="stat-box">
                <b>{{ clientProfile.orders_count }}</b>
                <span>Замовлень</span>
              </div>
            </div>
          </div>
        </div>

        <div class="drawer-section" style="margin-top: 24px;">
          <span class="mini-label">Історія взаємодії</span>
          <div class="drawer-history-list">
            <div v-for="log in contactHistory" :key="log.id" class="mini-log-item">
               <div class="ml-icon">{{ channels.find(c => c.code === log.communication_type.toLowerCase())?.icon || '📞' }}</div>
               <div class="ml-body">
                  <span class="ml-res">{{ getResultHint(log.result) }}</span>
                  <p class="ml-note" v-if="log.note">{{ log.note }}</p>
                  <span class="ml-time">{{ formatDate(log.contacted_at) }}</span>
               </div>
            </div>
          </div>
        </div>

        <div class="drawer-section" style="margin-top: 24px;">
          <span class="mini-label">Новий контакт</span>
          <CrmContactPanel
            v-model:contact-comm-type="contactCommType"
            v-model:contact-plan-reason="contactPlanReason"
            v-model:contact-next-at="contactNextAt"
            v-model:contact-note="contactNote"
            :form="form"
            :order-id="orderId"
            :communication-types="communicationTypes"
            :contact-results="contactResults"
            :contact-result="contactResult"
            :next-touch-summary="nextTouchSummary"
            :saving-contact="savingContact"
            :get-result-hint="getResultHint"
            @set-next-contact-preset="setNextContactPreset"
            @apply-contact-result="contactResult = $event"
            @log-contact="onLogContact"
          />
        </div>
      </div>
    </el-drawer>

    <!-- Create Counterparty Dialog -->
    <el-dialog v-model="cpDialogVisible" title="Новий клієнт" width="500px" class="saas-dialog">
      <el-form label-position="top">
        <el-form-item label="Ім'я / Назва" required>
          <el-input v-model="newCp.name" placeholder="Петро Петренко" />
        </el-form-item>
        <el-form-item label="Телефон">
          <el-input v-model="newCp.phone" placeholder="+38 (0XX) XXX-XX-XX" />
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
  Plus, Picture, MagicStick, Loading, Printer, Promotion,
  User, Box, DataAnalysis, Wallet, Search, Bell, Check, Collection,
  Camera, Share, VideoPlay, Star, More, ChatDotRound, ChatLineRound, Phone,
  ArrowRight, ArrowDown, UserFilled, Clock, Document, ChatDotSquare,
  View, Edit, CopyDocument, Delete, TrendCharts, Grid, QuestionFilled
} from '@element-plus/icons-vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { validateCrmOrderRequiredFields, collectMissingProductionFields } from './composables/useCrmOrderValidation'

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
const activeSidebarTab = ref('summary')
const stages = [
  { code: 'new',        name: 'Нова заявка', color: '#6366f1' },
  { code: 'processing', name: 'Уточнення',   color: '#f59e0b' },
  { code: 'confirmed',  name: 'Підтверджено', color: '#10b981' },
  { code: 'payment',    name: 'Очікує оплату', color: '#8b5cf6' },
  { code: 'production', name: 'У виробництві', color: '#ec4899' },
  { code: 'done',       name: 'Виконано',     color: '#22c55e' },
]

const leadSourceIcons = [
  { id: 'instagram', name: 'Instagram', icon: 'Camera' },
  { id: 'facebook', name: 'Facebook', icon: 'Share' },
  { id: 'google', name: 'Google', icon: 'Search' },
  { id: 'tiktok', name: 'TikTok', icon: 'VideoPlay' },
  { id: 'referral', name: 'Рекомендація', icon: 'Star' },
  { id: 'other', name: 'Інше', icon: 'More' }
]

const channelPills = [
  { code: 'viber', name: 'Viber', icon: 'ChatDotRound' },
  { code: 'telegram', name: 'Telegram', icon: 'Promotion' },
  { code: 'whatsapp', name: 'WhatsApp', icon: 'ChatLineRound' },
  { code: 'phone', name: 'Дзвінок', icon: 'Phone' }
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
  next_contact_plan_reason: 'first_touch',
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

const contactHistory = ref([])
const loadingContacts = ref(false)

// Contact Log State
const contactResult = ref(null)
const contactCommType = ref('CALL')
const contactPlanReason = ref('first_touch')
const contactNextAt = ref(null)
const contactNote = ref('')
const savingContact = ref(false)

const vErrors = reactive({ counterparty_id: false, total_amount: false })

const missedTasks = ref([])
const loadMissedTasks = async () => {
  if (!orderId.value) return
  try {
    const res = await api.get('/api/v1/crm/tasks/today')
    // Only show pending tasks for THIS specific order
    missedTasks.value = res.data.filter(t => t.order_id === orderId.value && t.status === 'pending')
  } catch (e) {
    console.warn('[CRM] Tasks failed', e)
  }
}

const completeTask = async (taskId) => {
  try {
    await api.put(`/api/v1/crm/tasks/${taskId}/complete`)
    missedTasks.value = missedTasks.value.filter(t => t.id !== taskId)
    ElMessage.success('Завдання виконано')
  } catch (err) {
    ElMessage.error('Помилка виконання')
  }
}

const clientProfile = ref(null)
const showClientDrawer = ref(false)

const currentStep = computed(() => {
  if (!form.counterparty_id) return 1
  if (!form.product_id) return 2
  if (!form.warehouse_id) return 3
  return 4
})

const isPrepayActive = (pct) => {
  if (!form.total_amount) return false
  return Math.round((form.prepayment_amount || 0) / form.total_amount * 100) === pct
}

const setPrepayPercent = (pct) => {
  if (form.total_amount > 0) {
    form.prepayment_amount = Math.round(form.total_amount * (pct / 100))
  }
}

const loadClientProfile = async (id) => {
  if (!id) {
    clientProfile.value = null
    return
  }
  try {
    const res = await api.get(`/api/v1/crm/clients/${id}/profile`)
    clientProfile.value = res.data
  } catch (e) {
    console.warn('[CRM] Profile load failed', e)
  }
}

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

const formatDate = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)

const updateTotalAmount = (val) => {
  form.total_amount = val
}

const getResultHint = (code) => {
  const hints = {
    'NO_ANSWER': 'Перенести на пізніше',
    'THINKING': 'Клієнт думає',
    'REFUSED': 'Відмова / Архів',
    'CONFIRMED': 'Успішно / В роботу'
  }
  return hints[code] || ''
}

const nextTouchSummary = computed(() => {
  if (!form.next_contact_at) return 'Немає запланованих дій'
  
  const date = new Date(form.next_contact_at).toLocaleString('uk-UA', { 
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' 
  })
  
  const reasons = {
    'first_touch': 'Перший контакт',
    'retry_no_answer': 'Повтор після не відповів',
    'clarify': 'Уточнити деталі',
    'payment': 'Нагадати про оплату',
    'production': 'Погодити виробництво'
  }
  
  const reason = reasons[form.next_contact_plan_reason] || 'Контакт'
  return `${reason} (${date})`
})

const setNextContactPreset = (preset) => {
  const now = new Date()
  let target = new Date(now)
  
  if (preset.minutes) target.setMinutes(now.getMinutes() + preset.minutes)
  if (preset.hours) target.setHours(now.getHours() + preset.hours)
  if (preset.tomorrow) {
    target.setDate(now.getDate() + 1)
    if (preset.h) target.setHours(preset.h, 0, 0, 0)
  }
  if (preset.days) {
    target.setDate(now.getDate() + preset.days)
    if (preset.h) target.setHours(preset.h, 0, 0, 0)
  }
  
  // Format to local ISO (ignoring TZ for simple DB storage if needed, or use proper ISO)
  // Here we use a simple YYYY-MM-DDTHH:mm:ss format
  const pad = (n) => n.toString().padStart(2, '0')
  const iso = `${target.getFullYear()}-${pad(target.getMonth()+1)}-${pad(target.getDate())}T${pad(target.getHours())}:${pad(target.getMinutes())}:${pad(target.getSeconds())}`
  
  if (preset.syncContactLog) {
    contactNextAt.value = iso
  } else {
    form.next_contact_at = iso
    if (preset.reason) form.next_contact_plan_reason = preset.reason
  }
}

const logContact = async (data) => {
  if (!orderId.value) return
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, data)
    loadContacts()
    form.contact_attempts = (form.contact_attempts || 0) + 1
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка запису контакту')
    throw err
  }
}

const onLogContact = async () => {
  if (!contactResult.value) return
  savingContact.value = true
  try {
    await logContact({
      result: contactResult.value,
      comm_type: contactCommType.value,
      note: contactNote.value,
      next_contact_at: contactNextAt.value
    })
    
    // Clear log form
    contactResult.value = null
    contactNote.value = ''
    contactNextAt.value = null
    
    ElMessage.success('Зафіксовано')
  } catch (err) {
    // Error handled in logContact
  } finally {
    savingContact.value = false
  }
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
        loadMissedTasks()
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
watch(() => form.counterparty_id, (newVal) => {
  if (newVal) {
    loadClientProfile(newVal)
    loadContacts()
  }
})
watch(() => form.product_id, (newVal) => {
  if (newVal) checkMaterials()
})

watch(() => form.counterparty_id, (newVal) => {
  if (newVal) {
    loadClientProfile(newVal)
  } else {
    clientProfile.value = null
  }
}, { immediate: true })

watch(currentUserId, (newId) => {
  if (!orderId.value && !form.manager_id && newId) {
    form.manager_id = newId
  }
}, { immediate: true })
</script>

<style src="./styles/CrmOrderEditor.css"></style>
