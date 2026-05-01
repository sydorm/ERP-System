<template>
  <div class="crm-editor-page" v-loading="loading">
    <!-- ─── STICKY HEADER & STEPPER ─── -->
    <div class="crm-sticky-wrapper">
      <div class="crm-header-premium">
        <div class="hp-left">
          <el-button circle class="btn-back-saas" @click="router.push('/crm')">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <div class="hp-titles">
            <span class="hp-pre">CRM / ЗАМОВЛЕННЯ</span>
            <h1>{{ orderId ? 'Редагування заявки' : 'Створення нової заявки' }} <span v-if="form.order_number" class="order-id-tag">#{{ form.order_number }}</span></h1>
          </div>
        </div>
        
        <div class="hp-actions">
          <el-tooltip content="Друк" placement="bottom">
            <el-button class="btn-icon-saas"><el-icon><Printer /></el-icon></el-button>
          </el-tooltip>
          <el-button class="btn-secondary-saas" @click="save('draft')">Записати чернетку</el-button>
          <el-button type="primary" class="btn-primary-saas" :loading="saving" @click="saveAndClose">
            <el-icon><Promotion /></el-icon> Зберегти та передати
          </el-button>
        </div>
      </div>

      <div class="crm-stepper-modern">
        <div 
          v-for="(step, idx) in editorSteps" 
          :key="step.id"
          class="step-node"
          :class="{ active: currentSection === step.id, done: isStepCompleted(step.id) }"
          @click="scrollToSection(step.id)"
        >
          <div class="step-marker">
            <el-icon v-if="isStepCompleted(step.id)"><Check /></el-icon>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span class="step-text">{{ step.label }}</span>
          <div class="step-line" v-if="idx < editorSteps.length - 1"></div>
        </div>
      </div>
    </div>

    <div class="crm-editor-body">
      <div class="crm-layout-container">
        <!-- ─── MAIN CONTENT (70%) ─── -->
        <div class="crm-main-content">
          
          <!-- SECTION 1: КЛІЄНТ -->
          <div id="section-client" class="crm-section-card">
            <div class="section-header">
              <div class="sh-title">
                <el-icon class="icon-pulse-blue"><User /></el-icon>
                <span>Дані клієнта</span>
              </div>
              <div class="sh-actions">
                <el-button v-if="form.counterparty_id" link @click="showClientDrawer = true">
                  Повний профіль та історія <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <div class="section-body">
              <div class="client-selection-row-saas">
                <el-select
                  v-model="form.counterparty_id"
                  filterable
                  remote
                  :remote-method="searchCounterparties"
                  placeholder="Пошук клієнта за ім'ям або телефоном..."
                  class="select-saas-large"
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
                <el-button @click="openCreateCounterparty" type="primary" class="btn-new-client">
                  <el-icon><Plus /></el-icon> Новий клієнт
                </el-button>
              </div>

              <div class="lead-source-section">
                <span class="mini-label-saas">Джерело клієнта (Звідки дізнався про нас?)</span>
                <div class="source-tiles-saas">
                  <div 
                    v-for="src in leadSourceIcons" 
                    :key="src.id"
                    class="source-tile-saas"
                    :class="[src.id, { active: form.lead_source_id === src.id }]"
                    @click="form.lead_source_id = src.id"
                  >
                    <div class="st-icon">
                      <component :is="src.icon" />
                    </div>
                    <span class="st-label">{{ src.name }}</span>
                    <el-icon v-if="form.lead_source_id === src.id" class="st-check"><CircleCheckFilled /></el-icon>
                  </div>
                </div>
              </div>

              <div class="client-meta-row-saas">
                <div class="meta-field">
                  <span class="mini-label-saas">Місто</span>
                  <el-input v-model="form.city" placeholder="Напр. Київ" />
                </div>
                <div class="meta-field">
                  <span class="mini-label-saas">Канал зв'язку</span>
                  <el-select v-model="form.channel" style="width: 100%">
                    <el-option label="Instagram" value="instagram" />
                    <el-option label="Viber" value="viber" />
                    <el-option label="Telegram" value="telegram" />
                    <el-option label="Сайт" value="website" />
                    <el-option label="Дзвінок" value="phone" />
                  </el-select>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 2: ВИРІБ -->
          <div id="section-product" class="crm-section-card">
            <div class="section-header">
              <div class="sh-title">
                <el-icon><Box /></el-icon>
                <span>Виріб / Номенклатура</span>
              </div>
            </div>

            <div class="section-body">
              <div class="product-search-row">
                <el-select
                  v-model="form.product_id"
                  filterable
                  placeholder="Оберіть модель виробу..."
                  class="select-saas-large"
                  @change="onProductChange"
                >
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </div>

              <!-- SECTION 3: ХАРАКТЕРИСТИКИ -->
              <div id="section-specs" class="specs-configurator-saas" v-if="form.product_id">
                <div class="specs-divider">
                  <span>Конфігурація характеристик</span>
                </div>
                
                <div v-if="!productAttributes.length" class="specs-empty-state">
                  <el-icon><InfoFilled /></el-icon>
                  <span>Для цього товару характеристики не задані.</span>
                </div>
                
                <div v-else class="specs-grid-saas">
                  <div v-for="attr in productAttributes" :key="attr.id" class="spec-field-saas">
                    <span class="mini-label-saas">{{ attr.name }}</span>
                    
                    <!-- Chips for 2-6 options -->
                    <div v-if="attr.options && attr.options.length <= 6" class="spec-chips-saas">
                      <div 
                        v-for="opt in attr.options" 
                        :key="opt"
                        class="spec-chip-saas"
                        :class="{ active: form.attributes_values[attr.id] === opt }"
                        @click="form.attributes_values[attr.id] = opt"
                      >
                        {{ opt }}
                      </div>
                    </div>
                    
                    <!-- Select for more options -->
                    <el-select 
                      v-else 
                      v-model="form.attributes_values[attr.id]" 
                      filterable 
                      placeholder="Оберіть значення..."
                      style="width: 100%"
                    >
                      <el-option v-for="opt in attr.options" :key="opt" :label="opt" :value="opt" />
                    </el-select>
                  </div>
                </div>
              </div>

              <div class="product-details-row-saas">
                <div class="pdr-left">
                  <span class="mini-label-saas">Коментар до виробу</span>
                  <el-input 
                    v-model="form.comment" 
                    type="textarea" 
                    :rows="3" 
                    placeholder="Додайте важливі деталі для виробництва..." 
                  />
                </div>
                <div class="pdr-right">
                   <span class="mini-label-saas">Фото референс</span>
                   <div class="photo-upload-saas" @click="triggerPhotoUpload">
                      <img v-if="form.reference_photo" :src="form.reference_photo" class="preview-img" />
                      <div v-else class="upload-hint">
                        <el-icon><Picture /></el-icon>
                        <span>Завантажити фото</span>
                      </div>
                   </div>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 4: АНАЛІЗ ТА ЛОГІСТИКА -->
          <div id="section-analysis" class="crm-section-card">
            <div class="section-header">
              <div class="sh-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Аналіз та логістика</span>
              </div>
            </div>

            <div class="section-body">
              <div class="analysis-status-card" :class="matStatusClass" v-if="form.product_id">
                <div class="as-header">
                  <div class="as-indicator-group">
                    <div class="as-dot"></div>
                    <span class="as-label">{{ matStatusLabel }}</span>
                  </div>
                  <el-button link size="small" :icon="Refresh" @click="checkMaterials">Оновити аналіз</el-button>
                </div>

                <div class="materials-list-saas" v-if="materials.length">
                  <div class="ml-head">
                    <span class="ml-col-name">Матеріал / Компонент</span>
                    <span class="ml-col-val">Потрібно</span>
                    <span class="ml-col-val">Є на складі</span>
                    <span class="ml-col-status">Статус</span>
                  </div>
                  <div v-for="m in materials" :key="m.id" class="ml-row" :class="m.status">
                    <span class="ml-col-name">{{ m.component_name || m.name }}</span>
                    <span class="ml-col-val">{{ m.required_qty || m.required }}</span>
                    <span class="ml-col-val">{{ m.available_qty || m.available }}</span>
                    <span class="ml-col-status">
                      <el-icon v-if="m.status === 'ok'"><CircleCheckFilled /></el-icon>
                      <el-icon v-else><WarningFilled /></el-icon>
                    </span>
                  </div>
                </div>
                
                <div v-else class="analysis-no-data">
                  Специфікація (BOM) для обраного товару не знайдена.
                </div>
              </div>
              <div v-else class="analysis-placeholder-saas">
                Будь ласка, оберіть виріб для автоматичного аналізу складських залишків.
              </div>

              <div class="logistics-config-saas">
                 <div class="config-field">
                   <span class="mini-label-saas">Склад відвантаження</span>
                   <el-select v-model="form.warehouse_id" style="width: 100%">
                      <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
                   </el-select>
                 </div>
                 <div class="config-field">
                   <span class="mini-label-saas">Тип оплати</span>
                   <el-select v-model="form.payment_status_id" style="width: 100%">
                      <el-option v-for="ps in paymentStatuses" :key="ps.id" :label="ps.name" :value="ps.id" />
                   </el-select>
                 </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── SIDEBAR RIGHT (30%) - STICKY ─── -->
        <div class="crm-sidebar-right">
          
          <div class="sidebar-tabs-saas">
            <div class="sb-tab" :class="{ active: activeSidebarTab === 'summary' }" @click="activeSidebarTab = 'summary'">
              <el-icon><Wallet /></el-icon> ПІДСУМОК
            </div>
            <div class="sb-tab" :class="{ active: activeSidebarTab === 'activity' }" @click="activeSidebarTab = 'activity'">
              <el-icon><List /></el-icon> АКТИВНІСТЬ
              <span class="tab-badge" v-if="contactHistory.length">{{ contactHistory.length }}</span>
            </div>
          </div>

          <!-- SECTION 5: ФІНАНСИ -->
          <div id="section-finance" v-if="activeSidebarTab === 'summary'" class="summary-card-saas saas-premium-shadow">
             <div class="summary-price-zone">
                <span class="mini-label-saas">Загальна сума</span>
                <div class="price-input-saas">
                   <el-input-number 
                     v-model="form.total_amount" 
                     :controls="false" 
                     class="total-amount-field"
                   />
                   <span class="currency-tag">₴</span>
                </div>
                <div class="price-origin-hint" :class="{ auto: isAutoPrice }">
                   <el-icon><component :is="isAutoPrice ? 'CircleCheckFilled' : 'EditPen'" /></el-icon>
                   {{ isAutoPrice ? 'Ціну підтягнуто з номенклатури' : 'Введіть суму вручну' }}
                </div>
             </div>

             <div class="summary-finance-section">
                <span class="mini-label-saas">Предоплата</span>
                <div class="prepay-quick-buttons">
                   <div 
                     v-for="p in [0, 30, 50, 100]" 
                     :key="p"
                     class="prepay-btn-saas"
                     :class="{ active: isPrepayActive(p) }"
                     @click="setPrepayPercent(p)"
                   >
                     {{ p === 0 ? 'Без' : p + '%' }}
                   </div>
                </div>
                <el-input-number 
                  v-model="form.prepayment_amount" 
                  :controls="false" 
                  style="width: 100%; margin-top: 12px;"
                  placeholder="Сума предоплати"
                />
             </div>

             <div class="summary-manager-section">
                <span class="mini-label-saas">Відповідальний менеджер</span>
                <div class="manager-card-saas">
                   <div class="manager-avatar-saas">
                      {{ getManagerInitials(form.manager_id || currentUserId) }}
                   </div>
                   <el-select v-model="form.manager_id" class="manager-select-saas">
                      <el-option v-for="u in users" :key="u.id" :label="`${u.first_name} ${u.last_name}`" :value="u.id" />
                   </el-select>
                </div>
             </div>

             <!-- SECTION 6: ДЕДЛАЙН -->
             <div id="section-deadline" class="summary-deadline-section">
                <span class="mini-label-saas">Дедлайн виготовлення <span class="required">*</span></span>
                <el-date-picker 
                  v-model="form.deadline_date" 
                  type="date" 
                  placeholder="Оберіть дату" 
                  style="width: 100%"
                  class="deadline-picker-saas"
                />
                <div v-if="!form.deadline_date" class="deadline-alert-saas">
                   <el-icon><Warning /></el-icon> Обов'язково для виробництва
                </div>
             </div>

             <div class="summary-priority-section">
                <span class="mini-label-saas">Пріоритет замовлення</span>
                <div class="priority-grid-saas">
                   <div 
                     v-for="p in priorities" 
                     :key="p.id"
                     class="priority-card-saas"
                     :class="[p.code, { active: form.priority === p.code }]"
                     @click="form.priority = p.code; form.priority_id = p.id"
                   >
                     {{ p.name }}
                   </div>
                </div>
             </div>

             <div class="order-checklist-saas">
                <div class="checklist-header">Готовність заявки</div>
                <div class="checklist-body">
                   <div class="check-item" :class="{ done: !!form.counterparty_id }">
                      <el-icon><component :is="form.counterparty_id ? 'CircleCheckFilled' : 'CircleCloseFilled'" /></el-icon>
                      Клієнт обраний
                   </div>
                   <div class="check-item" :class="{ done: !!form.product_id }">
                      <el-icon><component :is="form.product_id ? 'CircleCheckFilled' : 'CircleCloseFilled'" /></el-icon>
                      Виріб обраний
                   </div>
                   <div class="check-item" :class="{ done: form.total_amount > 0 }">
                      <el-icon><component :is="form.total_amount > 0 ? 'CircleCheckFilled' : 'CircleCloseFilled'" /></el-icon>
                      Сума вказана
                   </div>
                   <div class="check-item" :class="{ done: !!form.deadline_date }">
                      <el-icon><component :is="form.deadline_date ? 'CircleCheckFilled' : 'CircleCloseFilled'" /></el-icon>
                      Дедлайн встановлено
                   </div>
                </div>
             </div>
          </div>

          <!-- ACTIVITY FEED TAB -->
          <div v-if="activeSidebarTab === 'activity'" class="activity-feed-saas">
             <div class="af-header">
                <span>Стрічка активності</span>
                <el-button link :icon="Refresh" @click="loadContacts" />
             </div>
             <div class="af-list">
                <div v-for="log in contactHistory" :key="log.id" class="af-item">
                   <div class="af-line"></div>
                   <div class="af-icon-wrap" :class="log.communication_type.toLowerCase()">
                      <el-icon><component :is="getChannelIcon(log.communication_type)" /></el-icon>
                   </div>
                   <div class="af-body">
                      <div class="af-time">{{ formatDate(log.contacted_at) }}</div>
                      <div class="af-title">{{ getResultHint(log.result) }}</div>
                      <div class="af-note" v-if="log.note">{{ log.note }}</div>
                   </div>
                </div>
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
  View, Edit, CopyDocument, Delete, TrendCharts, Grid, QuestionFilled,
  Position, Refresh, ShoppingBag, MoreFilled
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

const editorSteps = [
  { id: 'client',    label: 'Клієнт',      icon: 'User' },
  { id: 'product',   label: 'Виріб',       icon: 'Box' },
  { id: 'specs',     label: 'Характеристики', icon: 'MagicStick' },
  { id: 'analysis',  label: 'Аналіз та логістика', icon: 'DataAnalysis' },
  { id: 'finance',   label: 'Фінанси',     icon: 'Wallet' },
  { id: 'deadline',  label: 'Дедлайн',     icon: 'Clock' }
]

const currentSection = ref('client')

const leadSourceIcons = [
  { id: 'phone',       name: 'Дзвінок',       icon: 'Phone' },
  { id: 'instagram',   name: 'Instagram',     icon: 'Camera' },
  { id: 'viber',       name: 'Viber',         icon: 'ChatDotRound' },
  { id: 'telegram',    name: 'Telegram',      icon: 'Promotion' },
  { id: 'website',     name: 'Сайт',          icon: 'Position' },
  { id: 'referral',    name: 'Рекомендація',  icon: 'Star' },
  { id: 'returning',   name: 'Повторний',     icon: 'Refresh' },
  { id: 'marketplace', name: 'Marketplace',   icon: 'ShoppingBag' },
  { id: 'other',       name: 'Інше',          icon: 'More' }
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

const getManagerInitials = (userId) => {
  const user = users.value.find(u => u.id === userId)
  if (!user || (!user.name && !user.username)) return '??'
  const displayName = user.name || user.username || '?'
  const names = displayName.split(' ')
  return names.filter(Boolean).map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const onClientChange = (val) => {
  form.counterparty_id = val
  if (val) loadClientProfile(val)
}

const isStepCompleted = (stepId) => {
  switch (stepId) {
    case 'client': return !!form.counterparty_id && !!form.lead_source_id
    case 'product': return !!form.product_id
    case 'specs': return Object.keys(form.attributes_values).length > 0
    case 'analysis': return !!form.warehouse_id
    case 'finance': return form.total_amount > 0
    case 'deadline': return !!form.deadline_date
    default: return false
  }
}

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
    const attrRes = await api.get(`/api/v1/products/${val}/attributes`)
    productAttributes.value = attrRes.data
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

const scrollToSection = (sectionId) => {
  const el = document.getElementById(sectionId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    currentSection.value = sectionId
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)

const isAutoPrice = computed(() => {
  if (!form.product_id) return false
  const prod = products.value.find(p => p.id === form.product_id)
  return prod && Math.abs(prod.price - form.total_amount) < 0.01
})

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

const saveAndClose = async () => {
  await save()
  router.push('/crm')
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
  } else {
    clientProfile.value = null
  }
}, { immediate: true })

watch(() => form.product_id, (newVal) => {
  if (newVal) checkMaterials()
})

watch(currentUserId, (newId) => {
  if (!orderId.value && !form.manager_id && newId) {
    form.manager_id = newId
  }
}, { immediate: true })
</script>

<style src="./styles/CrmOrderEditor.css"></style>
