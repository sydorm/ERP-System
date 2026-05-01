<template>
  <div class="crm-board-page-wrapper">
    <!-- Vertical Side Nav -->
    <div class="crm-vertical-nav">
      <div 
        class="nav-item" 
        :class="{ active: viewMode === 'board' }"
        @click="viewMode = 'board'"
        title="Замовлення"
      >
        <el-icon><Grid /></el-icon>
        <span class="nav-label">Замовлення</span>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: viewMode === 'analytics' }"
        @click="viewMode = 'analytics'"
        title="Аналітика"
      >
        <el-icon><TrendCharts /></el-icon>
        <span class="nav-label">Розгорнути</span>
      </div>
      <div class="nav-spacer"></div>
      <div class="nav-item-secondary">
        <el-icon><QuestionFilled /></el-icon>
      </div>
    </div>

    <div class="crm-board-page" v-if="viewMode === 'board'">
      <div class="crm-sticky-workbar">
        <CrmSummaryCards
        :orders-count="orders.length"
        :total-pipeline-amount="totalPipelineAmount"
        :hot-sla-count="hotSlaCount"
        :payment-progress="paymentProgress"
        :today-tasks-count="todayTasks.length"
        :overdue-tasks-count="overdueTasks.length"
        :format-currency="formatCurrency"
      />

      <div class="crm-toolbar-row">
        <transition name="toolbar-fade">
          <CrmBoardToolbar
            :users="users"
            :filters="filters"
            :search-query="searchQuery"
            :sort-option="sortOption"
            :active-controls-count="activeControlsCount"
            :is-any-filter-active="isAnyFilterActive"
            @update:search-query="searchQuery = $event"
            @update:sort-option="sortOption = $event"
            @analytics="viewMode = 'analytics'"
            @reset-all="resetAll"
            @reset-filters="resetFilters"
            @apply-filters="applyFilters"
            @export="handleExport"
            @new-order="openNewOrder"
          />
        </transition>
      </div>
      </div><!-- /crm-sticky-workbar -->

      <div class="crm-board-body">

      <!-- ===== KANBAN BOARD ===== -->
      <div class="crm-kanban" v-loading="loading">
        <CrmKanbanColumn
          v-for="stage in stages"
          :key="stage.key"
          :stage="stage"
          :orders="filteredOrdersInStage(stage.key)"
          :stage-total="stageTotal(stage.key)"
          :stage-share="stageShare(stage.key)"
          :stage-has-more="Boolean(stageHasMore[stage.key])"
          :drag-over-stage="dragOverStage"
          :selected-order-ids="selectedOrderIds"
          :get-order-health-class="getOrderHealthClass"
          :get-counterparty-name="getCounterpartyName"
          :get-lead-source-label="getLeadSourceLabel"
          :get-order-deadline="getOrderDeadline"
          :get-sla-level="getSlaLevel"
          :get-sla-hours="getSlaHours"
          :get-attention-reason="getAttentionReason"
          :get-attention-class="getAttentionClass"
          :get-order-hints="getOrderHints"
          :get-manager-name="getManagerName"
          :get-manager-initials="getManagerInitials"
          :get-order-manager-id="getOrderManagerId"
          :get-priority-color="getPriorityColor"
          :get-priority-label="getPriorityLabel"
          :get-deadline-class="getDeadlineClass"
          :get-deadline-days-text="getDeadlineDaysText"
          :get-next-contact-class="getNextContactClass"
          :get-next-contact-label="getNextContactLabel"
          :get-payment-label="getPaymentLabel"
          :get-contact-result-label="getContactResultLabel"
          :get-channel-icon="getChannelIcon"
          :format-currency="formatCurrency"
          :format-date="formatDate"
          :format-relative-time="formatRelativeTime"
          :is-reminder-today="isReminderToday"
          @drag-over="dragOverStage = $event"
          @drag-leave="dragOverStage = null"
          @drop="onDrop"
          @drag-start="onDragStart"
          @drag-end="dragOrderId = null"
          @open-editor="openEditor"
          @toggle-selection="toggleSelection"
          @open-client-profile="openClientProfile"
          @comm="handleComm"
          @card-command="handleCardCommand"
          @load-more="loadMore"
          @new-order-in-stage="openNewOrderInStage"
        />
      </div>

      <!-- BULK ACTIONS BAR -->
      <transition name="el-zoom-in-bottom">
        <div v-if="selectedOrderIds.length > 1" class="selection-bar">
          <div class="selection-info">
            <el-icon @click="clearSelection" class="close-selection"><Close /></el-icon>
            <span>Вибрано: <strong>{{ selectedOrderIds.length }}</strong> замовлень</span>
          </div>
          <div class="selection-actions">
            <el-dropdown @command="handleBulkManager" trigger="click">
              <el-button type="primary" plain size="default">
                Змінити менеджера <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item 
                    v-for="u in users" 
                    :key="u.id" 
                    :command="u.id"
                  >
                    {{ u.name }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <el-dropdown @command="handleBulkStage" trigger="click">
              <el-button type="primary" plain size="default">
                Змінити статус <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item 
                    v-for="s in stages" 
                    :key="s.key" 
                    :command="s.key"
                  >
                    {{ s.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <el-button type="danger" plain @click="handleBulkCancel">Скасувати</el-button>
          </div>
        </div>
      </transition>

      <!-- Modals -->
      <el-dialog v-model="rescheduleVisible" title="Перенести передзвін" width="380px">
        <div v-if="selectedTask" class="reschedule-body">
          <label>Встановити час:</label>
          <el-date-picker
            v-model="rescheduleTime"
            type="datetime"
            placeholder="Оберіть дату та час"
            format="DD.MM.YYYY HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
          <div class="quick-reschedule-grid">
            <button class="qr-btn" @click="quickReschedule({ minutes: 60 })">+1 год</button>
            <button class="qr-btn" @click="quickReschedule({ tomorrow: true, h: 10 })">Завтра 10:00</button>
            <button class="qr-btn" @click="quickReschedule({ tomorrow: true, h: 14 })">Завтра 14:00</button>
            <button class="qr-btn" @click="quickReschedule({ days: 2, h: 10 })">+2 дні</button>
          </div>
        </div>
        <template #footer>
          <el-button @click="rescheduleVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="confirmReschedule">Перенести</el-button>
        </template>
      </el-dialog>

      <CallResultDialog 
        v-model="callVisible" 
        :task="callTask" 
        @success="onCallSuccess" 
      />

      <ClientProfile 
        v-model="clientProfileVisible"
        :client-id="selectedClientId"
      />

      </div><!-- /crm-board-body -->
    </div><!-- /crm-board-page (Board View) -->

    <!-- Analytics View -->
    <div class="crm-analytics-view fade-in" v-else-if="viewMode === 'analytics'">
      <CrmInsights />
    </div>
  </div><!-- /crm-board-page-wrapper -->
</template>

<script setup>
import './styles/CrmOrdersBoard.css'
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import { Search, Plus, Bell, Clock, Calendar, MoreFilled, Operation, ArrowDown, User as UserIcon, Phone, ChatDotRound, Close, Download, Promotion, Camera, TrendCharts, Money, Warning, MagicStick, Grid, QuestionFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'
import ClientProfile from '@/views/CRM/ClientProfile.vue'
import CrmBoardToolbar from './components/CrmBoardToolbar.vue'
import CrmSummaryCards from './components/CrmSummaryCards.vue'
import CrmKanbanColumn from './components/CrmKanbanColumn.vue'
import CrmInsights from './CrmInsights.vue'

const viewMode = ref('board') // 'board' or 'analytics'
const clientProfileVisible = ref(false)
const selectedClientId = ref(null)

const openClientProfile = (clientId) => {
  if (!clientId) return
  selectedClientId.value = clientId
  clientProfileVisible.value = true
}

const getPriorityLabel = (p) => {
  const map = { critical: 'Критичний', urgent: 'Високий', normal: 'Середній', low: 'Низький' }
  return map[p] || 'Середній'
}
const getPriorityColor = (p) => {
  const map = { critical: '#EF4444', urgent: '#F97316', normal: '#F59E0B', low: '#10B981' }
  return map[p] || '#F59E0B'
}
const getDeadlineClass = (deadlineStr) => {
  if (!deadlineStr) return ''
  const now = new Date()
  const dl = new Date(deadlineStr)
  const diffDays = (dl - now) / (1000 * 60 * 60 * 24)
  if (diffDays < 3) return 'deadline-danger'
  if (diffDays < 7) return 'deadline-warning'
  return ''
}
const getDeadlineDaysText = (deadlineStr) => {
  if (!deadlineStr) return ''
  const now = new Date()
  const dl = new Date(deadlineStr)
  const diffDays = Math.ceil((dl - now) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 'прострочено'
  if (diffDays === 0) return 'сьогодні'
  return `${diffDays} дн.`
}
const isReminderToday = (nextContactAt) => {
  if (!nextContactAt) return false
  const todayStr = new Date().toDateString()
  return new Date(nextContactAt).toDateString() === todayStr
}
const getChannelIcon = (type) => {
  const map = {
    phone: 'Phone',
    viber: 'ChatDotRound',
    telegram: 'Promotion',
    instagram: 'Camera'
  }
  return map[type] || 'ChatDotRound'
}
const getContactResultLabel = (res) => {
  const map = {
    thinking: 'Думає',
    no_answer: 'Не відповів',
    confirmed: 'Підтвердив',
    refused: 'Відмовився',
    THINKING: 'Думає',
    NO_ANSWER: 'Не відповів',
    CONFIRMED: 'Підтвердив',
    REFUSED: 'Відмовився'
  }
  return map[res] || res
}
const getPaymentLabel = (status) => {
  const map = {
    unpaid: 'Не оплачено',
    partial: 'Частково',
    paid: 'Оплачено'
  }
  return map[status] || status
}
const handleComm = (order, channel) => {
  if (channel === 'phone') {
    handleCall({
      id: order.id,
      order_id: order.id,
      order_number: order.order_number,
      client_name: getCounterpartyName(order.counterparty_id) || order.client_name,
      client_phone: order.client_phone
    })
  } else {
    ElMessage.info(`Канал зв'язку: ${channel}`)
  }
}
const formatRelativeTime = (dateStr) => {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins > 0 ? diffMins : 1} хв тому`
  if (diffHours < 24) return `${diffHours} год тому`
  if (diffDays === 1) return 'вчора'
  if (diffDays < 7) return `${diffDays} дні тому`
  return date.toLocaleDateString('uk-UA')
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const orders = ref([])
const counterparties = ref([])
const users = ref([])
const leadSources = ref([])
const todayTasks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const slaStatus = ref({})

const currentUser = computed(() => userStore.user || {})
const currentUserId = computed(() => currentUser.value?.id || null)
const canSeeAllOrders = computed(() => {
  const u = currentUser.value
  return Boolean(u?.is_superuser || ['admin', 'director'].includes(u?.role) || userStore.hasPermission?.('crm.manage'))
})
const defaultManagerScope = computed(() => canSeeAllOrders.value ? 'all' : 'mine')

const getSlaLevel = (orderId) => slaStatus.value[orderId]?.sla_level || 'ok'
const getSlaHours = (orderId) => {
  const h = slaStatus.value[orderId]?.hours_since_activity || 0
  return h % 1 === 0 ? h.toFixed(0) : h.toFixed(1)
}
const fetchSlaStatus = async () => {
  try {
    const res = await api.get('/api/v1/crm/orders/sla-status')
    slaStatus.value = res.data
  } catch { /* non-critical */ }
}

// Filter State
const filters = ref({
  priority: '',
  payment: '',
  managerScope: '',
  deadline: '',
  attentionOnly: false
})
const activeFiltersCount = computed(() => {
  return [
    filters.value.priority,
    filters.value.payment,
    filters.value.deadline,
    filters.value.attentionOnly ? 'attention' : '',
    filters.value.managerScope && filters.value.managerScope !== defaultManagerScope.value ? filters.value.managerScope : '',
  ].filter(Boolean).length
})
const activeControlsCount = computed(() => {
  return activeFiltersCount.value + (sortOption.value !== 'created_desc' ? 1 : 0)
})

// Pagination state
const stageSkip = ref({
  new: 0, processing: 0, confirmed: 0,
  payment: 0, production: 0, done: 0
})
const stageHasMore = ref({})

const selectedOrderIds = ref([])

const isAnyFilterActive = computed(() => {
  return activeFiltersCount.value > 0 || sortOption.value !== 'created_desc' || searchQuery.value !== ''
})

// Sort State
const sortOption = ref('created_desc')
const rescheduleVisible = ref(false)
const rescheduleTime = ref('')
const selectedTask = ref(null)
const callVisible = ref(false)
const callTask = ref(null)

const overdueTasks = computed(() => {
  return todayTasks.value.filter(t => isTaskOverdue(t))
})

const totalPipelineAmount = computed(() => {
  return orders.value.reduce((sum, order) => sum + (Number(order.total_amount) || 0), 0)
})

const hotSlaCount = computed(() => {
  return orders.value.filter(order => ['warning', 'critical', 'urgent'].includes(getSlaLevel(order.id))).length
})

const paymentProgress = computed(() => {
  if (!orders.value.length) return 0
  const paidCount = orders.value.filter(order => order.payment_status === 'paid').length
  return Math.round((paidCount / orders.value.length) * 100)
})

const stageShare = (stage) => {
  if (!orders.value.length) return 0
  const count = orders.value.filter(order => order.crm_stage === stage).length
  return Math.max(8, Math.round((count / orders.value.length) * 100))
}

const getOrderHealthClass = (order) => {
  const slaLevel = getSlaLevel(order.id)
  if (['critical', 'urgent'].includes(slaLevel)) return 'order-health-critical'
  if (slaLevel === 'warning') return 'order-health-warning'
  if (order.payment_status === 'paid') return 'order-health-paid'
  return 'order-health-neutral'
}

const getOrderDeadline = (order) => order.deadline || order.deadline_date || null
const getOrderManagerId = (order) => order.responsible_manager_id || order.manager_id || order.created_by || null

const getLeadSourceLabel = (order) => {
  if (order.lead_source?.name) return order.lead_source.name
  if (order.lead_source_name) return order.lead_source_name
  if (order.source) return order.source
  if (order.channel) return order.channel
  const found = leadSources.value.find(i => i.id === order.lead_source_id || i.code === order.lead_source_id)
  return found?.name || ''
}

const getNextContactDate = (order) => order.next_contact_at || order.next_contact_date || null
const getNextContactLabel = (order) => {
  const value = getNextContactDate(order)
  if (!value) return 'Контакт не заплановано'
  const date = new Date(value)
  const today = new Date().toDateString()
  const prefix = date < new Date() ? 'Контакт прострочено' : (date.toDateString() === today ? 'Наступний контакт: сьогодні' : 'Наступний контакт')
  return `${prefix} ${date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}`
}
const getNextContactClass = (order) => {
  const value = getNextContactDate(order)
  if (!value) return 'is-empty'
  return new Date(value) < new Date() ? 'is-overdue' : 'is-planned'
}

const hasPrepayment = (order) => Number(order.prepayment_amount || order.paid_amount || 0) > 0 || order.payment_status === 'paid'
const needsPaymentControl = (order) => order.payment_status !== 'paid' && Number(order.total_amount || 0) > 0 && ['payment', 'processing', 'production'].includes(order.crm_stage)

const getAttentionReasons = (order) => {
  const reasons = []
  const nextContact = getNextContactDate(order)
  const deadline = getOrderDeadline(order)
  const slaLevel = getSlaLevel(order.id)
  const stage = order.crm_stage || 'new'

  // 1. Contact-related warnings (ONLY for 'new' and 'payment')
  if (['new', 'payment'].includes(stage)) {
    if (!nextContact) {
      reasons.push({ text: 'Немає наступного контакту', level: 'warning' })
    } else if (new Date(nextContact) < new Date()) {
      reasons.push({ text: 'Контакт прострочено', level: 'critical' })
    }

    // SLA-based contact warnings
    if (['critical', 'urgent'].includes(slaLevel)) {
      reasons.push({ text: `Без дії ${getSlaHours(order.id)} год`, level: 'critical' })
    } else if (slaLevel === 'warning') {
      reasons.push({ text: `Затримка контакту: ${getSlaHours(order.id)} год`, level: 'warning' })
    }
  }

  // 2. Deadline & Payment warnings (All stages except 'done')
  if (stage !== 'done') {
    if (!deadline) {
      reasons.push({ text: 'Немає дедлайну', level: 'warning' })
    } else if (new Date(deadline) < new Date()) {
      reasons.push({ text: 'Прострочений дедлайн', level: 'critical' })
    }

    if (!hasPrepayment(order) && Number(order.total_amount || 0) > 0 && ['payment', 'processing'].includes(stage)) {
      reasons.push({ text: 'Немає передоплати', level: 'warning' })
    }

    if (needsPaymentControl(order)) {
      reasons.push({ text: 'Потрібен контроль оплати', level: 'warning' })
    }
  }

  return reasons
}

const getOrderHints = (order) => getAttentionReasons(order)

const getAttentionReason = (order) => {
  return getAttentionReasons(order)[0]?.text || ''
}

const getAttentionClass = (order) => {
  const first = getAttentionReasons(order)[0]
  if (first?.level === 'critical') return 'attention-critical'
  if (first?.level === 'warning') return 'attention-warning'
  return 'attention-info'
}

const handleExport = async (type) => {
  if (type === 'pdf') return
  
  try {
    const response = await api.get('/api/v1/orders/export', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    const date = new Date().toISOString().slice(0, 10)
    link.setAttribute('download', `orders_export_${date}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (e) {
    ElMessage.error('Помилка при експорті')
    console.error(e)
  }
}

const stages = [
  { key: 'new', label: 'Нові', color: '#3D3AA8' },
  { key: 'payment', label: 'Оплата', color: '#F97316' },
  { key: 'processing', label: 'В роботі', color: '#F59E0B' },
  { key: 'production', label: 'Виробництво', color: '#8B5CF6' },
  { key: 'done', label: 'Виконано', color: '#22C55E' }
]

const fetchStage = async (stage, reset = false) => {
  if (reset) stageSkip.value[stage] = 0
  try {
    const res = await api.get(
      `/api/v1/orders?crm_stage=${stage}&limit=20&skip=${stageSkip.value[stage]}`
    )
    
    const ordersWithContacts = await Promise.all(
      res.data.map(async (order) => {
        try {
          const contactsRes = await api.get(`/api/v1/crm/orders/${order.id}/contacts`)
          if (contactsRes.data && contactsRes.data.length > 0) {
            order.last_contact = contactsRes.data[0]
          } else {
            order.last_contact = null
          }
        } catch (err) {
          order.last_contact = null
        }
        return order
      })
    )

    if (reset) {
      orders.value = orders.value
        .filter(o => o.crm_stage !== stage)
        .concat(ordersWithContacts)
    } else {
      const newIds = new Set(ordersWithContacts.map(o => o.id))
      orders.value = orders.value.filter(o => !newIds.has(o.id)).concat(ordersWithContacts)
    }
    stageHasMore.value[stage] = res.data.length === 20
  } catch (e) {
    ElMessage.error(`Помилка завантаження стадії ${stage}`)
  }
}

const fetchAll = async () => {
  loading.value = true
  try {
    if (!userStore.user) await userStore.fetchUser().catch(() => {})
    if (!filters.value.managerScope) filters.value.managerScope = defaultManagerScope.value

    const [cpRes, usersRes, tasksRes, leadSourceRes] = await Promise.all([
      api.get('/api/v1/counterparties?limit=500'),
      api.get('/api/v1/users/colleagues'),
      api.get('/api/v1/crm/tasks/today'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] }))
    ])
    counterparties.value = cpRes.data
    users.value = usersRes.data
    todayTasks.value = tasksRes.data
    leadSources.value = leadSourceRes.data || []

    // Fetch all stages + SLA status in parallel
    await Promise.all([
      ...stages.map(s => fetchStage(s.key, true)),
      fetchSlaStatus()
    ])
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const loadMore = async (stage) => {
  stageSkip.value[stage] += 20
  await fetchStage(stage, false)
}

// Bulk Actions Logic
const toggleSelection = (id) => {
  const index = selectedOrderIds.value.indexOf(id)
  if (index === -1) {
    selectedOrderIds.value.push(id)
  } else {
    selectedOrderIds.value.splice(index, 1)
  }
}

const clearSelection = () => {
  selectedOrderIds.value = []
}

const handleBulkUpdate = async (data) => {
  try {
    const idsString = selectedOrderIds.value.join('&ids=')
    await api.patch(`/api/v1/orders/bulk-update?ids=${idsString}`, data)
    ElMessage.success(`Оновлено ${selectedOrderIds.value.length} замовлень`)
    clearSelection()
    await fetchAll()
  } catch (e) {
    ElMessage.error('Помилка групового оновлення')
  }
}

const handleBulkManager = (managerId) => handleBulkUpdate({ manager_id: managerId })
const handleBulkStage = (stage) => handleBulkUpdate({ crm_stage: stage })
const handleBulkCancel = () => {
  ElMessageBox.confirm('Ви впевнені, що хочете скасувати вибрані замовлення?', 'Увага', {
    confirmButtonText: 'Так, скасувати',
    cancelButtonText: 'Ні',
    type: 'warning'
  }).then(() => {
    handleBulkUpdate({ status: 'cancelled' })
  })
}

const getCounterpartyName = (id) => counterparties.value.find(c => c.id === id)?.name || ''

const getManagerName = (id) => {
  if (!id) return 'Без менеджера'
  const user = users.value.find(u => u.id === id)
  if (user) return user.name || user.full_name || 'Без менеджера'
  return 'Без менеджера'
}
const getManagerInitials = (id) => {
  const name = getManagerName(id)
  if (name === 'Без менеджера') return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part.charAt(0).toUpperCase())
    .join('')
}
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' })
const isTaskOverdue = (task) => new Date(task.scheduled_at) < new Date()

const normalizePhone = (phone) => {
  if (!phone) return ''
  return phone.toString().replace(/\D/g, '').slice(-9)
}

const resetFilters = () => {
  filters.value = { priority: '', payment: '', managerScope: defaultManagerScope.value, deadline: '', attentionOnly: false }
}
const resetAll = () => {
  resetFilters()
  sortOption.value = 'created_desc'
  searchQuery.value = ''
}
const applyFilters = () => { /* Popover closes automatically, computed handles it */ }

const filteredOrdersInStage = (stage) => {
  let list = orders.value.filter(o => o.crm_stage === stage)
  
  // 1. Search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    const qPhone = normalizePhone(q)
    
    list = list.filter(o => {
      const matchText = 
        o.order_number.toLowerCase().includes(q) || 
        (o.client_name && o.client_name.toLowerCase().includes(q)) ||
        (o.product_name && o.product_name.toLowerCase().includes(q)) ||
        getCounterpartyName(o.counterparty_id).toLowerCase().includes(q)

      let matchPhone = false
      if (qPhone.length >= 3) {
        const oPhone = normalizePhone(o.client_phone)
        if (oPhone && oPhone.includes(qPhone)) matchPhone = true
      } else if (o.client_phone && o.client_phone.includes(q)) {
        matchPhone = true
      }

      return matchText || matchPhone
    })
  }

  // 2. Filters
  if (filters.value.priority) list = list.filter(o => o.priority === filters.value.priority)
  if (filters.value.payment) list = list.filter(o => o.payment_status === filters.value.payment)
  const scope = filters.value.managerScope || defaultManagerScope.value
  if (scope === 'mine' && currentUserId.value) list = list.filter(o => getOrderManagerId(o) === currentUserId.value)
  if (scope.startsWith('manager:')) {
    const managerId = scope.replace('manager:', '')
    list = list.filter(o => getOrderManagerId(o) === managerId)
  }
  if (filters.value.attentionOnly) list = list.filter(o => getAttentionReasons(o).length > 0)
  if (filters.value.deadline) {
    const now = new Date()
    if (filters.value.deadline === 'overdue') {
      list = list.filter(o => getOrderDeadline(o) && new Date(getOrderDeadline(o)) < now)
    } else if (filters.value.deadline === 'today') {
      const today = now.toDateString()
      list = list.filter(o => getOrderDeadline(o) && new Date(getOrderDeadline(o)).toDateString() === today)
    }
  }

  // 3. Sorting
  list.sort((a, b) => {
    if (sortOption.value === 'deadline_asc') {
      const ad = getOrderDeadline(a); const bd = getOrderDeadline(b)
      if (!ad) return 1; if (!bd) return -1;
      return new Date(ad) - new Date(bd)
    }
    if (sortOption.value === 'amount_desc') return (b.total_amount || 0) - (a.total_amount || 0)
    if (sortOption.value === 'created_desc') return new Date(b.created_at) - new Date(a.created_at)
    if (sortOption.value === 'priority_desc') {
      const pMap = { critical: 4, urgent: 3, normal: 2, low: 1 }
      return (pMap[b.priority] || 0) - (pMap[a.priority] || 0)
    }
    return 0
  })

  return list
}

const stageTotal = (stage) => filteredOrdersInStage(stage).reduce((sum, o) => sum + (Number(o.total_amount) || 0), 0)

const openEditor = (o) => router.push(`/crm/orders/${o.id}`)
const openNewOrder = () => router.push('/crm/orders/new')
const openNewOrderInStage = (s) => router.push(`/crm/orders/new?stage=${s}`)

const handleCardCommand = async (command, order) => {
  if (command === 'open') { openEditor(order); return }
  if (command === 'client') { openClientProfile(order.counterparty_id); return }
  if (command === 'call') { handleComm(order, 'phone'); return }
  if (command === 'copy') {
    const value = order.client_phone || order.order_number || ''
    if (!value) { ElMessage.warning('Немає даних для копіювання'); return }
    try { await navigator.clipboard.writeText(value); ElMessage.success('Скопійовано') }
    catch { ElMessage.info(value) }
  }
}

const handleCall = (task) => {
  callTask.value = task
  callVisible.value = true
}
const onCallSuccess = () => fetchAll()

const quickReschedule = (opts) => {
  const d = new Date()
  if (opts.minutes) d.setMinutes(d.getMinutes() + opts.minutes)
  else if (opts.tomorrow) { d.setDate(d.getDate() + 1); d.setHours(opts.h, 0, 0, 0) }
  else if (opts.days) { d.setDate(d.getDate() + opts.days); d.setHours(opts.h, 0, 0, 0) }
  rescheduleTime.value = d.toISOString().slice(0, 19)
}

const confirmReschedule = async () => {
  try {
    await api.put(`/api/v1/crm/tasks/${selectedTask.value.id}/reschedule`, { scheduled_at: rescheduleTime.value })
    rescheduleVisible.value = false
    ElMessage.success('Завдання перенесено')
    fetchAll()
  } catch { ElMessage.error('Помилка') }
}

const dragOrderId = ref(null)
const dragOverStage = ref(null)
const onDragStart = (o) => dragOrderId.value = o.id
const onDrop = async (stage) => {
  const oid = dragOrderId.value
  const order = orders.value.find(o => o.id === oid)
  if (order && order.crm_stage !== stage) {
    order.crm_stage = stage
    try { await api.patch(`/api/v1/orders/${oid}/stage?stage=${stage}`) }
    catch { ElMessage.error('Помилка оновлення статусу') }
  }
  dragOverStage.value = null
}

onMounted(() => fetchAll())
onActivated(() => fetchAll())
watch(() => route.path, (newPath) => { if (newPath === '/crm') fetchAll() })
</script>
