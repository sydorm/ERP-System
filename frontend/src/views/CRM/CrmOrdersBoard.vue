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
            <span class="crm-col-dot" :style="{ background: stage.color }" />
            <span class="crm-col-title">{{ stage.label }}</span>
            <span class="crm-col-count-bubble">{{ filteredOrdersInStage(stage.key).length }}</span>
          </div>
          <div class="crm-col-subheader">
            ВСЬОГО: {{ formatCurrency(stageTotal(stage.key)) }} ГРН
          </div>
        </div>

        <!-- Cards -->
        <div class="kanban-column-content">
          <div
            v-for="order in filteredOrdersInStage(stage.key)"
            :key="order.id"
            class="order-card"
            draggable="true"
            @dragstart="onDragStart(order)"
            @dragend="dragOrderId = null"
            @click="openEditor(order)"
          >
            <div class="card-header">
              <span class="card-order-no">#{{ order.order_number }}</span>
              <!-- Priority Dot (Top Right) -->
              <div class="priority-dot-indicator" :class="getPriorityDotClass(order.priority)" />
            </div>
            
            <div class="card-main">
              <div class="order-card-title">{{ getCounterpartyName(order.counterparty_id) || order.client_name || '—' }}</div>
              <div class="order-card-details">{{ order.product_name || 'Індивідуальне замовлення' }}</div>
            </div>

            <div class="card-financial">
              <span class="card-price">{{ formatCurrency(order.total_amount) }} ₴</span>
              <span class="deadline-chip" v-if="order.deadline">
                <el-icon><Calendar /></el-icon> {{ formatDate(order.deadline) }}
              </span>
            </div>

            <div class="card-footer">
              <div class="card-badges">
                <span class="payment-badge" :class="`payment-${order.payment_status}`">
                  {{ getPaymentLabel(order.payment_status) }}
                </span>
              </div>
              <div class="card-meta">
                <el-tooltip :content="getManagerName(order.manager_id)" placement="top">
                  <div class="card-avatar">{{ (getManagerName(order.manager_id) || '?').charAt(0) }}</div>
                </el-tooltip>
                <div class="card-comm-icons">
                  <el-icon class="comm-icon"><ChatDotRound /></el-icon>
                  <el-icon class="comm-icon"><Phone /></el-icon>
                </div>
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
import { Search, Plus, Bell, Clock, Calendar, MoreFilled, Operation, ArrowDown, User as UserIcon, Phone, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'

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

const stages = [
  { key: 'new', label: 'Нові', color: '#3D3AA8' },
  { key: 'processing', label: 'В роботі', color: '#F59E0B' },
  { key: 'confirmed', label: 'Підтверджено', color: '#3B82F6' },
  { key: 'payment', label: 'Оплата', color: '#F97316' },
  { key: 'production', label: 'Виробництво', color: '#8B5CF6' },
  { key: 'done', label: 'Виконано', color: '#22C55E' }
]

const fetchStage = async (stage, reset = false) => {
  if (reset) stageSkip.value[stage] = 0
  try {
    const res = await api.get(
      `/api/v1/orders?crm_stage=${stage}&limit=20&skip=${stageSkip.value[stage]}`
    )
    if (reset) {
      orders.value = orders.value
        .filter(o => o.crm_stage !== stage)
        .concat(res.data)
    } else {
      // Avoid duplicates
      const newIds = new Set(res.data.map(o => o.id))
      orders.value = orders.value.filter(o => !newIds.has(o.id)).concat(res.data)
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
  width: 220px;
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 200px);
  background-color: rgba(249, 250, 251, 0.5);
  border-radius: 12px;
}

.kanban-column-header {
  padding: 12px;
  background-color: #ffffff;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  border: 1px solid #f3f4f6;
  border-top-width: 3px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.crm-col-title-row { display: flex; align-items: center; gap: 6px; position: relative; }
.crm-col-dot { width: 8px; height: 8px; border-radius: 50%; }
.crm-col-title { font-weight: 700; color: #1e293b; font-size: 13px; }
.crm-col-count-bubble { 
  background: #f1f5f9; color: #94a3b8; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; margin-left: 4px; 
}
.crm-col-menu { position: absolute; right: 0; color: #cbd5e1; cursor: pointer; font-size: 16px; }
.crm-col-subheader { font-size: 9px; color: #94a3b8; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }

.kanban-column-content {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
}

/* ─── Order Card ─── */
.order-card {
  background-color: #ffffff;
  padding: 12px;
  border-radius: 10px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}
.order-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-color: #e5e7eb; }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-order-no { font-size: 10px; color: #94a3b8; font-weight: 600; }

/* Priority Dot Indicator */
.priority-dot-indicator { width: 8px; height: 8px; border-radius: 50%; }
.dot-red { background: #ef4444; box-shadow: 0 0 4px rgba(239, 68, 68, 0.5); }
.dot-orange { background: #f97316; }
.dot-yellow { background: #eab308; }
.dot-green { background: #22c55e; }

.order-card-title { font-weight: 700; font-size: 13px; color: #1e293b; margin-bottom: 2px; }
.order-card-details { font-size: 11px; color: #64748b; margin-bottom: 8px; }

.card-financial { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.card-price { font-weight: 700; color: #1e293b; font-size: 13px; }

.deadline-chip {
  display: flex; align-items: center; gap: 4px; padding: 2px 6px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; 
  font-size: 9px; font-weight: 600; color: #64748b;
}

.card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 8px; margin-top: 4px; }
.payment-badge { padding: 1px 6px; border-radius: 4px; font-size: 9px; font-weight: 800; text-transform: uppercase; }
.payment-paid { background-color: #dcfce7; color: #15803d; }
.payment-partial { background-color: #fef9c3; color: #a16207; }
.payment-unpaid { background-color: #f1f5f9; color: #475569; }

.card-meta { display: flex; align-items: center; gap: 6px; }
.card-avatar {
  width: 20px; height: 20px; background: #3D3AA8; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 800;
}
.card-comm-icons { display: flex; align-items: center; gap: 4px; color: #94a3b8; font-size: 14px; }
.comm-icon:hover { color: #3D3AA8; }

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
</style>
