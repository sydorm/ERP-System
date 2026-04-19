<template>
  <div class="crm-board-page">

    <!-- ===== HEADER ===== -->
    <div class="crm-board-header">
      <div class="crm-header-left">
        <h1 class="crm-title">CRM — Замовлення</h1>
        <span class="crm-subtitle">{{ totalOrders }} замовлень</span>
      </div>
      <div class="crm-header-right">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук..."
          :prefix-icon="Search"
          clearable
          class="crm-search"
        />
        <el-select v-model="filterPriority" placeholder="Пріоритет" clearable class="crm-filter-sel">
          <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-select v-model="filterManager" placeholder="Менеджер" clearable class="crm-filter-sel">
          <el-option v-for="u in users" :key="u.id" :label="u.full_name || u.email" :value="u.id" />
        </el-select>
        <button class="crm-new-btn" @click="openNewOrder">
          <el-icon><Plus /></el-icon> Нова заявка
        </button>
      </div>
    </div>

    <!-- ===== MY TASKS TODAY ===== -->
    <div class="crm-tasks-panel" v-if="todayTasks.length">
      <div class="tasks-panel-head">
        <el-icon class="tasks-icon"><Bell /></el-icon>
        <span class="tasks-title">Мої задачі на сьогодні</span>
        <span class="tasks-count">{{ todayTasks.length }}</span>
      </div>
      <div class="tasks-list">
        <div
          v-for="task in todayTasks"
          :key="task.id"
          class="task-row"
          :class="{ 'task-overdue': isTaskOverdue(task) }"
        >
          <div class="task-time">
            <span v-if="isTaskOverdue(task)" class="overdue-badge">!</span>
            <span v-else>{{ formatTaskTime(task.scheduled_at) }}</span>
          </div>
          <div class="task-info">
            <span class="task-client">{{ task.client_name || '—' }}</span>
            <span class="task-order">{{ task.order_number }}</span>
            <span v-if="task.client_phone" class="task-phone">{{ task.client_phone }}</span>
          </div>
          <div class="task-actions">
            <button class="task-btn task-call" @click="openTaskOrder(task)">Зателефонувати</button>
            <button class="task-btn task-move" @click="rescheduleTask(task)">Перенести</button>
            <button class="task-btn task-done" @click="completeTask(task)">✓</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== TODAY FOLLOW-UPS BANNER ===== -->
    <div class="crm-followup-banner" v-if="todayFollowUps.length">
      <el-icon class="fu-icon"><Bell /></el-icon>
      <span class="fu-text">
        Сьогодні потрібно передзвонити:
        <button
          v-for="o in todayFollowUps.slice(0, 5)"
          :key="o.id"
          class="fu-chip"
          @click="openEditor(o)"
        >{{ o.order_number }} — {{ getCounterpartyName(o.counterparty_id) }}</button>
        <span v-if="todayFollowUps.length > 5" class="fu-more">+{{ todayFollowUps.length - 5 }}</span>
      </span>
    </div>

    <!-- ===== KANBAN BOARD ===== -->
    <div class="crm-kanban" v-loading="loading">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="crm-column"
        :class="[`stage-${stage.key}`, dragOverStage === stage.key ? 'drag-target' : '']"
        @dragover.prevent="dragOverStage = stage.key"
        @dragleave="dragOverStage = null"
        @drop.prevent="onDrop(stage.key)"
      >
        <!-- Column Header -->
        <div class="crm-col-header" :style="{ borderColor: stage.color }">
          <div class="crm-col-title-row">
            <span class="crm-col-dot" :style="{ background: stage.color }" />
            <span class="crm-col-title">{{ stage.label }}</span>
            <span class="crm-col-count">{{ ordersInStage(stage.key).length }}</span>
          </div>
          <span class="crm-col-amount">{{ formatCurrency(stageTotal(stage.key)) }} ₴</span>
        </div>

        <!-- Cards -->
        <div class="crm-cards-list">
          <div
            v-for="order in filteredOrdersInStage(stage.key)"
            :key="order.id"
            class="crm-card"
            :class="[getPriorityClass(order.priority), { 'card-overdue': isOverdue(order) }]"
            draggable="true"
            @dragstart="onDragStart(order)"
            @dragend="dragOrderId = null"
            @click="openEditor(order)"
          >
            <!-- Card top row -->
            <div class="card-top">
              <span class="card-number">{{ order.order_number }}</span>
              <span class="card-priority-dot" :class="getPriorityClass(order.priority)" :title="getPriorityLabel(order.priority)" />
            </div>

            <!-- Client -->
            <div class="card-client">
              <el-icon class="card-client-icon"><User /></el-icon>
              <span>{{ getCounterpartyName(order.counterparty_id) || '—' }}</span>
            </div>

            <span 
              v-if="order.lead_source_id || order.channel" 
              class="card-channel-tag" 
              :style="getChannelStyle(order.lead_source_id || order.channel)"
            >
              {{ getChannelLabel(order.lead_source_id || order.channel) }}
            </span>


            <!-- Amount + payment -->
            <div class="card-finance-row">
              <span class="card-amount">{{ formatCurrency(order.total_amount) }} ₴</span>
              <span class="card-pay-badge" :class="`pay-${order.payment_status}`">
                {{ getPaymentLabel(order.payment_status) }}
              </span>
            </div>

            <!-- Deadline -->
            <div class="card-deadline" v-if="order.deadline_date" :class="getDeadlineClass(order.deadline_date)">
              <el-icon><Clock /></el-icon>
              {{ formatDate(order.deadline_date) }}
            </div>

            <!-- Footer: manager + date -->
            <div class="card-footer">
              <span class="card-date">{{ formatDate(order.order_date) }}</span>
              <span class="card-manager" v-if="order.manager_id">
                {{ getManagerInitials(order.manager_id) }}
              </span>
            </div>
          </div>

          <!-- Drop placeholder -->
          <div class="crm-drop-placeholder" v-if="dragOverStage === stage.key && dragOrderId" />
        </div>

        <!-- Add card button -->
        <button class="crm-add-card-btn" @click="openNewOrderInStage(stage.key)">
          <el-icon><Plus /></el-icon> Додати
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Plus, Bell, Clock, User } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// ─── State ────────────────────────────────────────────────────────────────────
const loading     = ref(false)
const orders      = ref([])
const counterparties = ref([])
const users       = ref([])
const todayTasks     = ref([])
const searchQuery    = ref('')
const filterPriority = ref('')
const filterManager  = ref('')
const dragOrderId    = ref(null)
const dragOverStage  = ref(null)

// ─── Config ───────────────────────────────────────────────────────────────────
const stages = [
  { key: 'new',        label: 'Нова заявка',            color: '#94a3b8' },
  { key: 'processing', label: 'В обробці',               color: '#6366f1' },
  { key: 'confirmed',  label: 'Підтверджено',            color: '#0ea5e9' },
  { key: 'payment',    label: 'Оплата',                  color: '#f59e0b' },
  { key: 'production', label: 'У виробництві',           color: '#8b5cf6' },
  { key: 'done',       label: 'Виконано',                color: '#10b981' },
]

const priorities = [
  { value: 'low',      label: 'Низький' },
  { value: 'normal',   label: 'Звичайний' },
  { value: 'urgent',   label: 'Терміновий' },
  { value: 'critical', label: 'Критичний' },
]

// ─── Computed ─────────────────────────────────────────────────────────────────
const totalOrders = computed(() => orders.value.length)

const todayFollowUps = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return orders.value.filter(o =>
    (o.next_contact_date === today) ||
    (o.next_contact_at && o.next_contact_at.slice(0, 10) === today)
  )
})

const isTaskOverdue = (task) => new Date(task.scheduled_at) < new Date(new Date().toDateString())

const ordersInStage = (stageKey) =>
  orders.value.filter(o => o.crm_stage === stageKey)

const filteredOrdersInStage = (stageKey) => {
  let list = ordersInStage(stageKey)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o =>
      o.order_number.toLowerCase().includes(q) ||
      (getCounterpartyName(o.counterparty_id) || '').toLowerCase().includes(q)
    )
  }
  if (filterPriority.value) {
    list = list.filter(o => o.priority === filterPriority.value)
  }
  if (filterManager.value) {
    list = list.filter(o => o.manager_id === filterManager.value)
  }
  return list
}

const stageTotal = (stageKey) =>
  ordersInStage(stageKey).reduce((s, o) => s + (+o.total_amount || 0), 0)

// ─── Helpers ──────────────────────────────────────────────────────────────────
const getCounterpartyName = (id) =>
  counterparties.value.find(c => c.id === id)?.name || '—'

const getManagerInitials = (id) => {
  const u = users.value.find(u => u.id === id)
  if (!u) return ''
  const name = u.full_name || u.email || ''
  return name.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
}

const formatCurrency = (v) =>
  Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 0, maximumFractionDigits: 0 })

const formatDate = (d) => {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return `${day}.${m}.${y}`
}

const isOverdue = (order) => {
  if (!order.deadline_date) return false
  return order.deadline_date < new Date().toISOString().slice(0, 10) && order.crm_stage !== 'done'
}

const getDeadlineClass = (d) => {
  if (!d) return ''
  const today = new Date().toISOString().slice(0, 10)
  const diff = Math.ceil((new Date(d) - new Date(today)) / 86400000)
  if (diff < 0) return 'deadline-overdue'
  if (diff <= 2) return 'deadline-soon'
  return ''
}

const getPriorityClass = (p) => ({
  'priority-low': p === 'low',
  'priority-normal': p === 'normal' || !p,
  'priority-urgent': p === 'urgent',
  'priority-critical': p === 'critical',
})




// ─── Drag & Drop ──────────────────────────────────────────────────────────────
const onDragStart = (order) => { dragOrderId.value = order.id }

const onDrop = async (targetStage) => {
  dragOverStage.value = null
  if (!dragOrderId.value) return
  const order = orders.value.find(o => o.id === dragOrderId.value)
  if (!order || order.crm_stage === targetStage) { dragOrderId.value = null; return }

  const prevStage = order.crm_stage
  order.crm_stage = targetStage // optimistic update

  try {
    await api.patch(`/api/v1/orders/${order.id}/stage?stage=${targetStage}`)
  } catch {
    order.crm_stage = prevStage
    ElMessage.error('Не вдалося змінити етап')
  }
  dragOrderId.value = null
}

// ─── Task helpers ─────────────────────────────────────────────────────────────
const formatTaskTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  const today = new Date().toDateString()
  if (d.toDateString() === today) {
    return d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' }) +
    ' ' + d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

const openTaskOrder = (task) => router.push(`/crm/orders/${task.order_id}`)

const completeTask = async (task) => {
  try {
    await api.put(`/api/v1/crm/tasks/${task.id}/complete`)
    todayTasks.value = todayTasks.value.filter(t => t.id !== task.id)
  } catch {
    ElMessage.error('Помилка')
  }
}

const rescheduleTask = async (task) => {
  const newTime = prompt('Новий час (YYYY-MM-DDTHH:mm:ss):')
  if (!newTime) return
  try {
    await api.put(`/api/v1/crm/tasks/${task.id}/reschedule`, { scheduled_at: newTime })
    await fetchTasks()
  } catch {
    ElMessage.error('Помилка')
  }
}

const fetchTasks = async () => {
  try {
    const res = await api.get('/api/v1/crm/tasks/today')
    todayTasks.value = res.data
  } catch { /* silent */ }
}

// ─── Navigation ───────────────────────────────────────────────────────────────
const openEditor   = (order) => router.push(`/crm/orders/${order.id}`)
const openNewOrder = () => router.push('/crm/orders/new')
const openNewOrderInStage = (stage) => router.push(`/crm/orders/new?stage=${stage}`)

const dictionaryStore = ref({
  leadSources: [],
  priorities: [],
  paymentStatuses: []
})

const fetchDictionaries = async () => {
  try {
    const [ls, pr, ps] = await Promise.all([
      api.get('/api/v1/dictionaries/LEAD_SOURCE'),
      api.get('/api/v1/dictionaries/PRIORITY'),
      api.get('/api/v1/dictionaries/PAYMENT_STATUS')
    ])
    dictionaryStore.value.leadSources = ls.data
    dictionaryStore.value.priorities = pr.data
    dictionaryStore.value.paymentStatuses = ps.data
  } catch (e) {
    console.error('Failed to load dictionaries', e)
  }
}

// ─── Fetch ────────────────────────────────────────────────────────────────────
const fetchAll = async () => {
  loading.value = true
  try {
    const [ordersRes, cpRes, usersRes] = await Promise.allSettled([
      api.get('/api/v1/orders?limit=500'),
      api.get('/api/v1/counterparties?limit=500'),
      api.get('/users/colleagues'),
    ])
    orders.value         = ordersRes.status === 'fulfilled' ? ordersRes.value.data : []
    counterparties.value = cpRes.status === 'fulfilled' ? cpRes.value.data : []
    users.value          = usersRes.status === 'fulfilled' ? usersRes.value.data : []
    
    await Promise.all([fetchTasks(), fetchDictionaries()])
  } catch (e) {
    ElMessage.error('Помилка завантаження даних: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    loading.value = false
  }
}

const getChannelLabel = (ch) => {
  const source = dictionaryStore.value.leadSources.find(s => s.id === ch || s.code === ch)
  return source ? source.name : ch
}

const getChannelStyle = (ch) => {
  const source = dictionaryStore.value.leadSources.find(s => s.id === ch || s.code === ch)
  if (source && source.color) {
    return {
      backgroundColor: `${source.color}20`, // low opacity bg
      color: source.color,
      borderColor: source.color
    }
  }
  return {}
}

const getPriorityLabel = (p) => {
  const prio = dictionaryStore.value.priorities.find(s => s.id === p || s.code === p)
  return prio ? prio.name : (priorities.find(x => x.value === p)?.label || 'Звичайний')
}

const getPaymentLabel = (s) => {
  const status = dictionaryStore.value.paymentStatuses.find(i => i.id === s || i.code === s)
  return status ? status.name : ({ unpaid: 'Не опл.', partial: 'Частково', paid: 'Оплачено' }[s] || s)
}

onMounted(fetchAll)
</script>


<style scoped>
/* ─── Page Layout ─────────────────────────────────────────────────────────── */
.crm-board-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f1f5f9;
  font-family: 'Inter', sans-serif;
}

/* ─── Header ──────────────────────────────────────────────────────────────── */
.crm-board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}
.crm-header-left { display: flex; align-items: baseline; gap: 10px; }
.crm-title { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.crm-subtitle { font-size: 13px; color: #94a3b8; }
.crm-header-right { display: flex; align-items: center; gap: 8px; }
.crm-search { width: 220px; }
.crm-filter-sel { width: 140px; }
.crm-new-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.crm-new-btn:hover { background: #4f46e5; }

/* ─── Tasks Panel ─────────────────────────────────────────────────────────── */
.crm-tasks-panel {
  background: #fff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px;
  flex-shrink: 0;
}
.tasks-panel-head {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}
.tasks-icon  { color: #6366f1; font-size: 15px; }
.tasks-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.tasks-count {
  font-size: 11px; font-weight: 700; background: #6366f1; color: #fff;
  padding: 1px 8px; border-radius: 99px;
}
.tasks-list  { display: flex; flex-direction: column; gap: 5px; }
.task-row {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: 8px; background: #f8fafc;
  border: 1px solid #e2e8f0;
}
.task-row.task-overdue { background: #fff1f2; border-color: #fca5a5; }
.task-time  { font-size: 12px; font-weight: 700; color: #6366f1; width: 50px; flex-shrink: 0; }
.overdue-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 50%;
  background: #ef4444; color: #fff; font-size: 11px; font-weight: 800;
}
.task-info  { flex: 1; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.task-client { font-size: 13px; font-weight: 600; color: #1e293b; }
.task-order  { font-size: 11px; color: #6366f1; background: #eef2ff; padding: 1px 7px; border-radius: 99px; }
.task-phone  { font-size: 11px; color: #64748b; }
.task-actions { display: flex; gap: 5px; flex-shrink: 0; }
.task-btn {
  padding: 4px 10px; border-radius: 6px; border: none;
  font-size: 11px; font-weight: 600; cursor: pointer; transition: opacity 0.12s;
}
.task-btn:hover { opacity: .85; }
.task-call { background: #dbeafe; color: #1e40af; }
.task-move { background: #f1f5f9; color: #475569; }
.task-done { background: #d1fae5; color: #065f46; }

/* ─── Follow-up Banner ────────────────────────────────────────────────────── */
.crm-followup-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 24px;
  background: #fef3c7; border-bottom: 1px solid #fcd34d;
  flex-shrink: 0;
}
.fu-icon { color: #d97706; font-size: 16px; }
.fu-text { font-size: 13px; color: #92400e; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.fu-chip {
  display: inline-block; padding: 2px 10px; border-radius: 99px;
  background: #fbbf24; color: #78350f; font-size: 12px; font-weight: 600;
  border: none; cursor: pointer;
}
.fu-chip:hover { background: #f59e0b; }
.fu-more { color: #b45309; font-size: 12px; }

/* ─── Kanban Board ────────────────────────────────────────────────────────── */
.crm-kanban {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  overflow-x: auto;
  flex: 1;
  align-items: flex-start;
}

/* ─── Column ──────────────────────────────────────────────────────────────── */
.crm-column {
  flex: 0 0 260px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  max-height: 100%;
  transition: border-color 0.15s, background 0.15s;
}
.crm-column.drag-target {
  border-color: #6366f1;
  background: #eef2ff;
}

.crm-col-header {
  padding: 12px 14px 8px;
  border-top: 3px solid;
  border-radius: 10px 10px 0 0;
}
.crm-col-title-row { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.crm-col-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.crm-col-title { font-size: 13px; font-weight: 600; color: #1e293b; flex: 1; }
.crm-col-count {
  font-size: 11px; font-weight: 700;
  background: #e2e8f0; color: #64748b;
  padding: 1px 7px; border-radius: 99px;
}
.crm-col-amount { font-size: 11px; color: #94a3b8; padding-left: 14px; }

.crm-cards-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 80px;
}

.crm-add-card-btn {
  display: flex; align-items: center; gap: 4px; justify-content: center;
  width: 100%; padding: 8px; border: none; background: transparent;
  color: #94a3b8; font-size: 12px; cursor: pointer; border-radius: 0 0 10px 10px;
  transition: background 0.12s, color 0.12s;
}
.crm-add-card-btn:hover { background: #e2e8f0; color: #475569; }

/* ─── Card ────────────────────────────────────────────────────────────────── */
.crm-card {
  background: #fff;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #e2e8f0;
  transition: box-shadow 0.15s, transform 0.1s;
  user-select: none;
}
.crm-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); transform: translateY(-1px); }
.crm-card.card-overdue { border-left-color: #f43f5e !important; }

/* Priority border colors */
.crm-card.priority-low    { border-left-color: #94a3b8; }
.crm-card.priority-normal { border-left-color: #6366f1; }
.crm-card.priority-urgent { border-left-color: #f59e0b; }
.crm-card.priority-critical { border-left-color: #ef4444; }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-number { font-size: 12px; font-weight: 700; color: #6366f1; }

.card-priority-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.card-priority-dot.priority-low    { background: #94a3b8; }
.card-priority-dot.priority-normal { background: #6366f1; }
.card-priority-dot.priority-urgent { background: #f59e0b; }
.card-priority-dot.priority-critical { background: #ef4444; }

.card-client {
  display: flex; align-items: center; gap: 5px;
  font-size: 13px; font-weight: 500; color: #1e293b;
  margin-bottom: 5px;
}
.card-client-icon { font-size: 13px; color: #94a3b8; flex-shrink: 0; }

.card-channel-tag {
  display: inline-block; padding: 1px 8px; border-radius: 99px;
  font-size: 10px; font-weight: 600; margin-bottom: 6px;
}
.channel-instagram { background: #fce7f3; color: #9d174d; }
.channel-website   { background: #dbeafe; color: #1e40af; }
.channel-referral  { background: #d1fae5; color: #065f46; }
.channel-telegram  { background: #e0f2fe; color: #0369a1; }
.channel-olx       { background: #fef3c7; color: #92400e; }
.channel-phone     { background: #f3e8ff; color: #6b21a8; }

.card-finance-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 4px;
}
.card-amount { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-pay-badge {
  font-size: 10px; font-weight: 600; padding: 1px 7px; border-radius: 99px;
}
.pay-unpaid  { background: #fee2e2; color: #991b1b; }
.pay-partial { background: #fef3c7; color: #92400e; }
.pay-paid    { background: #d1fae5; color: #065f46; }

.card-deadline {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; color: #64748b; margin-bottom: 4px;
}
.deadline-overdue { color: #dc2626; font-weight: 600; }
.deadline-soon    { color: #d97706; font-weight: 600; }

.card-footer {
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid #f1f5f9; padding-top: 5px; margin-top: 3px;
}
.card-date { font-size: 10px; color: #94a3b8; }
.card-manager {
  width: 22px; height: 22px; border-radius: 50%;
  background: #6366f1; color: #fff;
  font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.crm-drop-placeholder {
  height: 60px;
  border: 2px dashed #6366f1;
  border-radius: 8px;
  background: #eef2ff;
  opacity: 0.6;
}
</style>
