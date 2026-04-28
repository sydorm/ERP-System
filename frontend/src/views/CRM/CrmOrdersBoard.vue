<template>
  <div class="crm-board-page">

    <!-- ===== HEADER ===== -->
    <div class="crm-board-header">
      <div class="crm-header-left">
        <div class="crm-title-row">
          <h1 class="crm-title">Дошка замовлень</h1>
          <span class="crm-count-badge">{{ orders.length }} замовлень</span>
        </div>
        <p class="crm-subtitle">Керування меблевим виробництвом</p>
      </div>
      <div class="crm-header-right">
        <div class="crm-view-switch">
          <button class="view-btn active">Kanban</button>
          <button class="view-btn" @click="router.push('/crm/analytics')">Аналітика</button>
        </div>

        <!-- SEARCH -->
        <el-input
          v-model="searchQuery"
          placeholder="Пошук клієнта, тел, виробу..."
          class="crm-search-input"
          clearable
          :prefix-icon="Search"
        />

        <!-- RESET ALL -->
        <button 
          v-if="isAnyFilterActive" 
          class="crm-reset-all-btn" 
          @click="resetAll"
        >
          ✕ Скинути все
        </button>

        <!-- FILTERS -->
        <el-popover placement="bottom-end" :width="300" trigger="click">
          <template #reference>
            <button class="crm-filter-btn">
              <el-icon><Operation /></el-icon> Фільтри
              <el-badge v-if="activeFiltersCount" :value="activeFiltersCount" class="filter-badge" />
            </button>
          </template>
          <div class="filter-popover-content">
            <div class="filter-section">
              <label>Пріоритет</label>
              <el-select v-model="filters.priority" placeholder="Всі" clearable>
                <el-option label="Критичний" value="critical" />
                <el-option label="Високий" value="urgent" />
                <el-option label="Середній" value="normal" />
                <el-option label="Низький" value="low" />
              </el-select>
            </div>
            <div class="filter-section">
              <label>Статус оплати</label>
              <el-select v-model="filters.payment" placeholder="Всі" clearable>
                <el-option label="Не оплачено" value="unpaid" />
                <el-option label="Часткова" value="partial" />
                <el-option label="Оплачено" value="paid" />
              </el-select>
            </div>
            <div class="filter-section">
              <label>Менеджер</label>
              <el-select v-model="filters.manager" placeholder="Всі" clearable>
                <el-option v-for="u in users" :key="u.id" :label="u.name" :value="u.id" />
              </el-select>
            </div>
            <div class="filter-section">
              <label>Дедлайн</label>
              <el-select v-model="filters.deadline" placeholder="Всі" clearable>
                <el-option label="Прострочені" value="overdue" />
                <el-option label="Сьогодні" value="today" />
                <el-option label="Цього тижня" value="this_week" />
              </el-select>
            </div>
            <div class="filter-footer">
              <el-button @click="resetFilters" size="small">Скинути</el-button>
              <el-button type="primary" size="small" @click="applyFilters">Застосувати</el-button>
            </div>
          </div>
        </el-popover>

        <el-dropdown trigger="click" @command="handleExport">
          <button class="crm-export-btn">
            <el-icon><Download /></el-icon> Експорт
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="excel">Excel (.csv)</el-dropdown-item>
              <el-dropdown-item command="pdf" disabled>PDF (скоро)</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <button class="crm-new-btn-indigo" @click="openNewOrder">
          <el-icon><Plus /></el-icon> Нове замовлення
        </button>
      </div>
    </div>

    <!-- ===== TOOLS (SORT) ===== -->
    <div class="crm-tools-row">
      <el-dropdown trigger="click" @command="handleSort">
        <div class="tool-item">
          Сортувати: {{ currentSortLabel }} <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="created_desc">За датою (нові)</el-dropdown-item>
            <el-dropdown-item command="deadline_asc">За дедлайном</el-dropdown-item>
            <el-dropdown-item command="amount_desc">За сумою (спадання)</el-dropdown-item>
            <el-dropdown-item command="priority_desc">За пріоритетом</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- ===== KANBAN BOARD ===== -->
    <div class="crm-kanban" v-loading="loading">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="kanban-column"
        :class="[dragOverStage === stage.key ? 'drag-target' : '']"
        @dragover.prevent="dragOverStage = stage.key"
        @dragleave="dragOverStage = null"
        @drop.prevent="onDrop(stage.key)"
      >
        <!-- Column Header -->
        <div class="kanban-column-header" :style="{ borderTopColor: stage.color }">
          <div class="crm-col-title-row">
            <div class="crm-col-title-left">
              <span class="crm-col-dot" :style="{ background: stage.color }" />
              <span class="crm-col-title">{{ stage.label }}</span>
            </div>
            <span class="crm-col-count-badge" :style="{ background: `${stage.color}33`, color: stage.color }">
              {{ filteredOrdersInStage(stage.key).length }}
            </span>
          </div>
          <div class="crm-col-subheader" :style="{ color: stage.color }">
            ВСЬОГО: {{ formatCurrency(stageTotal(stage.key)) }} ₴
          </div>
        </div>

        <!-- Cards -->
        <div class="kanban-column-content">
          <div
            v-for="(order, index) in filteredOrdersInStage(stage.key)"
            :key="order.id"
            class="order-card"
            :class="{ 'is-selected': selectedOrderIds.includes(order.id) }"
            :style="{ animationDelay: `${index * 50}ms` }"
            draggable="true"
            @dragstart="onDragStart(order)"
            @dragend="dragOrderId = null"
            @click="openEditor(order)"
          >
            <!-- CHECKBOX FOR BULK ACTIONS -->
            <div class="card-selection-overlay" @click.stop="toggleSelection(order.id)">
              <el-checkbox 
                :model-value="selectedOrderIds.includes(order.id)" 
                @change="toggleSelection(order.id)" 
                @click.stop
              />
            </div>

            <!-- Рядок 1 -->
            <div class="card-row-1">
              <span class="card-order-no">#{{ order.order_number }}</span>
              <div class="priority-wrapper" :class="order.priority">
                <span class="priority-dot" :style="{ background: getPriorityColor(order.priority) }" />
                <span class="priority-text" :style="{ color: getPriorityColor(order.priority) }">
                  {{ getPriorityLabel(order.priority) }}
                </span>
              </div>
            </div>

            <!-- Рядок 2 (джерело/компанія) -->
            <div class="card-row-2" v-if="order.source || getCounterpartyName(order.counterparty_id)">
              {{ order.source || getCounterpartyName(order.counterparty_id) }}
            </div>

            <!-- Назва виробу -->
            <div class="order-card-title">
              {{ order.product_name || 'Індивідуальне замовлення' }}
            </div>

            <!-- Рядок 4: Сума + Дедлайн -->
            <div class="card-row-financial">
              <span class="card-price">{{ formatCurrency(order.total_amount) }} ₴</span>
              <span 
                class="deadline-chip" 
                v-if="order.deadline"
                :class="getDeadlineClass(order.deadline)"
              >
                📅 {{ formatDate(order.deadline) }} <span v-if="getDeadlineDaysText(order.deadline)">· {{ getDeadlineDaysText(order.deadline) }}</span>
              </span>
            </div>

            <!-- Рядок 5: Бейдж оплати -->
            <div class="card-badges">
              <span class="payment-badge" :class="`payment-${order.payment_status}`">
                ● {{ getPaymentLabel(order.payment_status) }}
              </span>
            </div>

            <!-- Розділювач -->
            <div class="card-divider"></div>

            <!-- Останній контакт -->
            <div class="card-last-contact" v-if="order.last_contact">
              <el-icon v-if="isReminderToday(order.next_contact_at)" class="contact-channel-icon reminder"><Bell /></el-icon>
              <el-icon v-else class="contact-channel-icon" :class="order.last_contact.communication_type">
                <component :is="getChannelIcon(order.last_contact.communication_type)" />
              </el-icon>
              <span class="contact-result" :class="order.last_contact.result">
                {{ getContactResultLabel(order.last_contact.result) }}
              </span>
              <span class="contact-time">{{ formatRelativeTime(order.last_contact.contacted_at) }}</span>
            </div>

            <!-- Іконки + аватар -->
            <div class="card-footer-new">
              <div class="card-comm-channels">
                <span class="channel-icon phone" @click.stop="handleComm(order, 'phone')"><el-icon><Phone /></el-icon></span>
                <span class="channel-icon viber" @click.stop="handleComm(order, 'viber')"><el-icon><ChatDotRound /></el-icon></span>
                <span class="channel-icon telegram" @click.stop="handleComm(order, 'telegram')"><el-icon><Promotion /></el-icon></span>
                <span class="channel-icon instagram" @click.stop="handleComm(order, 'instagram')"><el-icon><Camera /></el-icon></span>
              </div>
              <div class="card-meta-right">
                <el-tooltip :content="getManagerName(order.manager_id)" placement="top">
                  <div class="card-avatar">{{ (getManagerName(order.manager_id) || '?').charAt(0) }}</div>
                </el-tooltip>
                <button class="card-arrow-btn" @click.stop="openEditor(order)">→</button>
              </div>
            </div>
          </div>

          <!-- LOAD MORE BUTTON -->
          <div v-if="stageHasMore[stage.key]" 
               @click.stop="loadMore(stage.key)"
               class="load-more-btn">
            Завантажити ще ↓
          </div>
        </div>
        
        <button class="add-order-button" @click="openNewOrderInStage(stage.key)">
          <el-icon><Plus /></el-icon> + ДОДАТИ ЗАМОВЛЕННЯ
        </button>
      </div>
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
    <el-dialog v-model="rescheduleVisible" title="Перенести передзвон" width="380px">
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import { Search, Plus, Bell, Clock, Calendar, MoreFilled, Operation, ArrowDown, User as UserIcon, Phone, ChatDotRound, Close, Download, Promotion, Camera } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'

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
const getChannelName = (type) => {
  const map = { phone: '📞 Телефон', viber: '💬 Viber', telegram: '✈ Telegram', instagram: '📸 Instagram' }
  return map[type] || type
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
const orders = ref([])
const counterparties = ref([])
const users = ref([])
const todayTasks = ref([])
const loading = ref(false)
const searchQuery = ref('')

// Filter State
const filters = ref({
  priority: '',
  payment: '',
  manager: '',
  deadline: ''
})
const activeFiltersCount = computed(() => {
  return Object.values(filters.value).filter(v => v !== '').length
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
const currentSortLabel = computed(() => {
  const map = {
    'deadline_asc': 'За дедлайном',
    'amount_desc': 'За сумою',
    'created_desc': 'За датою',
    'priority_desc': 'За пріоритетом'
  }
  return map[sortOption.value]
})

const rescheduleVisible = ref(false)
const rescheduleTime = ref('')
const selectedTask = ref(null)
const callVisible = ref(false)
const callTask = ref(null)

const overdueTasks = computed(() => {
  return todayTasks.value.filter(t => isTaskOverdue(t))
})

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
    const [cpRes, usersRes, tasksRes] = await Promise.all([
      api.get('/api/v1/counterparties?limit=500'),
      api.get('/users/colleagues'),
      api.get('/api/v1/crm/tasks/today')
    ])
    counterparties.value = cpRes.data
    users.value = usersRes.data
    todayTasks.value = tasksRes.data

    // Fetch all stages
    await Promise.all(stages.map(s => fetchStage(s.key, true)))
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
const getManagerName = (id) => users.value.find(u => u.id === id)?.name || id
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' })
const isTaskOverdue = (task) => new Date(task.scheduled_at) < new Date()

const normalizePhone = (phone) => {
  if (!phone) return ''
  return phone.toString().replace(/\D/g, '').slice(-9)
}

const handleSort = (cmd) => { sortOption.value = cmd }
const resetFilters = () => {
  filters.value = { priority: '', payment: '', manager: '', deadline: '' }
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
      // Name, Number, Product search
      const matchText = 
        o.order_number.toLowerCase().includes(q) || 
        (o.client_name && o.client_name.toLowerCase().includes(q)) ||
        (o.product_name && o.product_name.toLowerCase().includes(q)) ||
        getCounterpartyName(o.counterparty_id).toLowerCase().includes(q)

      // Normalized Phone search
      let matchPhone = false
      if (qPhone.length >= 3) { // only normalize search if query has enough digits
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
  if (filters.value.manager) list = list.filter(o => o.manager_id === filters.value.manager)
  if (filters.value.deadline) {
    const now = new Date()
    if (filters.value.deadline === 'overdue') {
      list = list.filter(o => o.deadline && new Date(o.deadline) < now)
    } else if (filters.value.deadline === 'today') {
      const today = now.toDateString()
      list = list.filter(o => o.deadline && new Date(o.deadline).toDateString() === today)
    }
  }

  // 3. Sorting
  list.sort((a, b) => {
    if (sortOption.value === 'deadline_asc') {
      if (!a.deadline) return 1; if (!b.deadline) return -1;
      return new Date(a.deadline) - new Date(b.deadline)
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

const getPriorityDotClass = (p) => {
  if (p === 'critical') return 'dot-red'
  if (p === 'urgent') return 'dot-orange'
  if (p === 'normal') return 'dot-yellow'
  return 'dot-green'
}
const getPaymentLabel = (s) => ({ unpaid: 'НЕ ОПЛАЧЕНО', partial: 'ЧАСТКОВА', paid: 'ОПЛАЧЕНО' }[s] || s)

const openEditor = (o) => router.push(`/crm/orders/${o.id}`)
const openNewOrder = () => router.push('/crm/orders/new')
const openNewOrderInStage = (s) => router.push(`/crm/orders/new?stage=${s}`)

const handleCall = (task) => {
  callTask.value = task
  callVisible.value = true
}
const onCallSuccess = () => fetchAll()
const completeTask = async (task) => {
  try {
    await api.put(`/api/v1/crm/tasks/${task.id}/complete`)
    fetchAll()
  } catch { ElMessage.error('Помилка') }
}

const openReschedule = (task) => {
  selectedTask.value = task
  rescheduleTime.value = task.scheduled_at
  rescheduleVisible.value = true
}

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
    try {
      await api.patch(`/api/v1/orders/${oid}/stage?stage=${stage}`)
    } catch { ElMessage.error('Помилка оновлення статусу') }
  }
  dragOverStage.value = null
}

onMounted(() => fetchAll())
onActivated(() => fetchAll())
watch(() => route.path, (newPath) => { if (newPath === '/crm') fetchAll() })
</script>

<style scoped>
.crm-board-page {
  padding: 16px;
  background: #F4F5F7;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ─── Header ─── */
.crm-board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.crm-title-row { display: flex; align-items: center; gap: 12px; }
.crm-title { font-size: 24px; font-weight: 800; color: #1e293b; margin: 0; }
.crm-count-badge { font-size: 14px; color: #94a3b8; font-weight: 500; }
.crm-subtitle { font-size: 13px; color: #64748b; margin: 2px 0 0; }

.crm-header-right { display: flex; gap: 10px; align-items: center; }
.crm-view-switch { background: #e2e8f0; padding: 2px; border-radius: 8px; display: flex; margin-right: 8px; }
.view-btn { padding: 4px 10px; border: none; background: transparent; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: #64748b; }
.view-btn.active { background: #fff; color: #1e293b; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

.crm-search-input { width: 220px; }
:deep(.el-input__wrapper) { border-radius: 8px; }

.crm-filter-btn { 
  background: #fff; border: 1px solid #e2e8f0; padding: 8px 14px; border-radius: 8px; 
  font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; color: #475569; position: relative;
}
.crm-export-btn {
  background: #fff; border: 1px solid #e2e8f0; padding: 8px 14px; border-radius: 8px; 
  font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; color: #475569;
  transition: all 0.2s;
}
.crm-export-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
.crm-reset-all-btn {
  background: transparent; border: none; color: #ef4444; font-size: 12px; font-weight: 700; cursor: pointer; padding: 0 8px; transition: color 0.2s;
}
.crm-reset-all-btn:hover { color: #b91c1c; text-decoration: underline; }
.filter-badge { margin-left: 4px; }

.crm-new-btn-indigo { background: #3D3AA8; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 13px; }

.crm-tools-row { display: flex; gap: 16px; margin-bottom: 16px; align-items: center; }
.tool-item { font-size: 12px; color: #64748b; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 4px; background: #fff; padding: 4px 10px; border-radius: 6px; border: 1px solid #e2e8f0; }

/* ─── Kanban Board ─── */
.crm-kanban {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 20px;
  align-items: flex-start;
}

.kanban-column {
  flex-shrink: 0;
  width: 280px;
  flex: 1;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 200px);
  background: white;
  border-radius: 16px;
  border-top: 3px solid #3D3AA8; /* Updated dynamically in inline style */
  padding: 16px;
}

.kanban-column-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.crm-col-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.crm-col-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.crm-col-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.crm-col-title {
  font-weight: 700;
  font-size: 14px;
  color: #111827;
}

.crm-col-count-badge {
  border-radius: 20px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
}

.crm-col-subheader {
  font-size: 12px;
  font-weight: 600;
}

.kanban-column-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  flex: 1;
}

/* ─── Order Card ─── */
@keyframes cardIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.order-card {
  width: 100%;
  min-height: 160px;
  border-radius: 16px;
  background: #FFFFFF;
  border: 1px solid #F0F0F8;
  box-shadow: 0 4px 20px rgba(61,58,168,0.06);
  transition: all 0.2s ease;
  padding: 16px;
  cursor: pointer;
  position: relative;
  opacity: 0;
  animation: cardIn 0.3s ease forwards;
}

.order-card:hover {
  box-shadow: 0 8px 32px rgba(61,58,168,0.14);
  transform: translateY(-2px);
  border-color: #C7C4F0;
}

.order-card.is-selected {
  border: 2px solid #3D3AA8;
  background: #F5F3FF;
}

.card-selection-overlay {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.2s;
}
.order-card:hover .card-selection-overlay,
.order-card.is-selected .card-selection-overlay {
  opacity: 1;
}

/* Рядок 1 */
.card-row-1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.card-order-no {
  font-size: 11px;
  color: #9CA3AF;
}
.priority-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
}
.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* Рядок 2 */
.card-row-2 {
  font-size: 11px;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

/* Назва виробу */
.order-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin: 8px 0;
}

/* Сума + Дедлайн */
.card-row-financial {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-price {
  font-size: 17px;
  font-weight: 700;
  color: #3D3AA8;
}
.deadline-chip {
  font-size: 12px;
  color: #6B7280;
  padding: 2px 6px;
  border-radius: 4px;
}
.deadline-chip.deadline-danger {
  color: #EF4444;
  background: #FEF2F2;
}
.deadline-chip.deadline-warning {
  color: #F59E0B;
  background: #FFFBEB;
}

/* Бейдж оплати */
.payment-badge {
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
}
.payment-badge.payment-paid { background: #ECFDF5; color: #065F46; }
.payment-badge.payment-partial { background: #FFFBEB; color: #92400E; }
.payment-badge.payment-unpaid { background: #F9FAFB; color: #6B7280; }

/* Розділювач */
.card-divider {
  border-top: 1px solid #F3F4F6;
  margin: 10px 0;
}

/* Останній контакт */
.card-last-contact {
  font-size: 12px;
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 12px;
}
.contact-channel-icon {
  font-size: 14px;
}
.contact-channel-icon.reminder {
  color: #EF4444;
}
.contact-channel-icon.phone { color: #16A34A; }
.contact-channel-icon.viber { color: #7C3AED; }
.contact-channel-icon.telegram { color: #2563EB; }
.contact-channel-icon.instagram { color: #DB2777; }

.contact-result {
  font-weight: 600;
}
.contact-result.thinking { color: #F59E0B; }
.contact-result.no_answer { color: #EF4444; }
.contact-result.confirmed { color: #10B981; }
.contact-result.refused { color: #6B7280; }

.contact-time {
  color: #9CA3AF;
}

/* Іконки каналів + аватар */
.card-footer-new {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-comm-channels {
  display: flex;
  gap: 8px;
  align-items: center;
}

.channel-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.channel-icon.phone { background: #F0FDF4; color: #16A34A; border: 1px solid rgba(22, 163, 74, 0.3); }
.channel-icon.viber { background: #F5F3FF; color: #7C3AED; border: 1px solid rgba(124, 58, 237, 0.3); }
.channel-icon.telegram { background: #EFF6FF; color: #2563EB; border: 1px solid rgba(37, 99, 235, 0.3); }
.channel-icon.instagram { background: #FDF2F8; color: #DB2777; border: 1px solid rgba(219, 39, 119, 0.3); }

.channel-icon:hover {
  filter: brightness(0.95);
  transform: scale(1.05);
}

.card-meta-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #3D3AA8;
  color: white;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-arrow-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #F5F3FF;
  color: #3D3AA8;
  border: 1px solid #E0E0FF;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s;
}
.card-arrow-btn:hover {
  background: #3D3AA8;
  color: white;
}

.add-order-button {
  margin: 6px; padding: 8px 0; border: 1px dashed #cbd5e1; border-radius: 8px; background: transparent; 
  color: #94a3b8; font-size: 10px; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.add-order-button:hover { background: #fff; border-color: #3D3AA8; color: #3D3AA8; }

/* Filter Popover Styles */
.filter-popover-content { padding: 4px; }
.filter-section { margin-bottom: 12px; }
.filter-section label { display: block; font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px; text-transform: uppercase; }
.filter-footer { display: flex; justify-content: flex-end; gap: 8px; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 4px; }

/* Task Panel Overlay (simplified) */
.crm-tasks-panel { background: #fff; border-radius: 10px; padding: 12px; margin-bottom: 16px; border: 1px solid #e2e8f0; }

.load-more-btn {
  text-align: center;
  padding: 10px;
  margin-top: 4px;
  cursor: pointer;
  color: #3D3AA8;
  font-size: 12px;
  font-weight: 700;
  background: rgba(61, 58, 168, 0.05);
  border-radius: 8px;
  transition: all 0.2s;
}
.load-more-btn:hover {
  background: rgba(61, 58, 168, 0.1);
  color: #2a287a;
}

/* SELECTION BAR */
.selection-bar {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: #3D3AA8;
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 32px;
  box-shadow: 0 10px 30px rgba(61, 58, 168, 0.4);
  z-index: 2000;
}
.selection-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
}
.close-selection {
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.2s;
}
.close-selection:hover {
  transform: scale(1.2);
}
.selection-actions {
  display: flex;
  gap: 12px;
}
.selection-actions .el-button--primary.is-plain {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}
.selection-actions .el-button--primary.is-plain:hover {
  background: white;
  color: #3D3AA8;
}
</style>
