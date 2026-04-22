<template>
  <div class="crm-board-page">

    <!-- ===== HEADER ===== -->
    <div class="crm-board-header">
      <div class="crm-header-left">
        <h1 class="crm-title">CRM — Замовлення</h1>
        <span class="crm-subtitle">{{ orders.length }} замовлень</span>
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
            <button class="task-btn task-call" @click="handleCall(task)">Зателефонувати</button>
            <button class="task-btn task-move" @click="openReschedule(task)">Перенести</button>
            <button class="task-btn task-done" @click="completeTask(task)">✓</button>
          </div>
        </div>
      </div>
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
            <div class="card-top">
              <span class="card-number">{{ order.order_number }}</span>
              <span class="card-priority-dot" :class="getPriorityClass(order.priority)" />
            </div>
            <div class="card-client">
              <el-icon class="card-client-icon"><UserIcon /></el-icon>
              <span>{{ getCounterpartyName(order.counterparty_id) || '—' }}</span>
            </div>
            <div class="card-finance-row">
              <span class="card-amount">{{ formatCurrency(order.total_amount) }} ₴</span>
              <span class="card-pay-badge" :class="'pay-' + order.payment_status">
                {{ getPaymentLabel(order.payment_status) }}
              </span>
            </div>
          </div>
        </div>
        
        <button class="crm-add-card-btn" @click="openNewOrderInStage(stage.key)">
          <el-icon><Plus /></el-icon> Додати замовлення
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

    <!-- Call Results Dialog -->
    <CallResultDialog 
      v-model="callVisible" 
      :task="callTask" 
      @success="onCallSuccess" 
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { Search, Plus, Bell, Right, Check, User as UserIcon } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'

const router = useRouter()
const orders = ref([])
const counterparties = ref([])
const users = ref([])
const todayTasks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterPriority = ref('')
const filterManager = ref('')

const rescheduleVisible = ref(false)
const rescheduleTime = ref('')
const selectedTask = ref(null)

const callVisible = ref(false)
const callTask = ref(null)

const stages = [
  { key: 'new', label: 'Нова заявка', color: '#6366f1' },
  { key: 'processing', label: 'В обробці', color: '#f59e0b' },
  { key: 'confirmed', label: 'Підтверджено', color: '#22c55e' },
  { key: 'payment', label: 'Оплата', color: '#8b5cf6' },
  { key: 'production', label: 'У виробництві', color: '#ec4899' },
  { key: 'done', label: 'Виконано', color: '#3b82f6' }
]

const priorities = [
  { value: 'normal', label: 'Звичайний' },
  { value: 'urgent', label: 'Терміновий' },
  { value: 'critical', label: 'Критичний' }
]

const fetchAll = async () => {
  loading.value = true
  try {
    const [ordersRes, cpRes, usersRes, tasksRes] = await Promise.all([
      api.get('/api/v1/orders?limit=500'),
      api.get('/api/v1/counterparties?limit=500'),
      api.get('/users/colleagues'),
      api.get('/api/v1/crm/tasks/today')
    ])
    orders.value = ordersRes.data
    counterparties.value = cpRes.data
    users.value = usersRes.data
    todayTasks.value = tasksRes.data
  } catch (e) {
    ElMessage.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

const getCounterpartyName = (id) => counterparties.value.find(c => c.id === id)?.name || id
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatTaskTime = (ts) => new Date(ts).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
const isTaskOverdue = (task) => new Date(task.scheduled_at) < new Date()

const ordersInStage = (stage) => orders.value.filter(o => o.crm_stage === stage)
const filteredOrdersInStage = (stage) => {
  let list = ordersInStage(stage)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => 
      o.order_number.toLowerCase().includes(q) || 
      getCounterpartyName(o.counterparty_id).toLowerCase().includes(q)
    )
  }
  if (filterPriority.value) list = list.filter(o => o.priority === filterPriority.value)
  if (filterManager.value) list = list.filter(o => o.manager_id === filterManager.value)
  return list
}
const stageTotal = (stage) => ordersInStage(stage).reduce((sum, o) => sum + (Number(o.total_amount) || 0), 0)

const getPriorityClass = (p) => `priority-${p}`
const getPaymentLabel = (s) => ({ unpaid: 'Не опл.', partial: 'Частково', paid: 'Оплачено' }[s] || s)
const isOverdue = (o) => o.deadline && new Date(o.deadline) < new Date()

const openEditor = (o) => router.push(`/crm/orders/${o.id}`)
const openNewOrder = () => router.push('/crm/orders/new')
const openNewOrderInStage = (s) => router.push(`/crm/orders/new?stage=${s}`)

const handleCall = (task) => {
  if (task.client_phone && navigator.clipboard) {
    navigator.clipboard.writeText(task.client_phone)
    ElMessage.success(`Номер скопійовано`)
  }
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
      await api.patch(`/api/v1/orders/${oid}`, { crm_stage: stage })
    } catch { ElMessage.error('Помилка оновлення статусу') }
  }
  dragOverStage.value = null
}

onMounted(fetchAll)
</script>

<style scoped>
.crm-board-page { display: flex; flex-direction: column; height: 100vh; overflow: hidden; background: #f1f5f9; }
.crm-board-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; background: #fff; border-bottom: 1px solid #e2e8f0; }
.crm-header-left { display: flex; align-items: baseline; gap: 10px; }
.crm-title { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.crm-subtitle { font-size: 13px; color: #94a3b8; }
.crm-header-right { display: flex; align-items: center; gap: 8px; }
.crm-search { width: 220px; }
.crm-filter-sel { width: 140px; }
.crm-new-btn { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 8px; border: none; background: #6366f1; color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; }
.crm-tasks-panel { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px; }
.tasks-panel-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.tasks-icon { color: #6366f1; }
.tasks-title { font-size: 13px; font-weight: 700; }
.tasks-count { font-size: 11px; background: #6366f1; color: #fff; padding: 1px 8px; border-radius: 99px; }
.tasks-list { display: flex; flex-direction: column; gap: 5px; }
.task-row { display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; }
.task-row.task-overdue { background: #fff1f2; border-color: #fca5a5; }
.task-time { font-size: 12px; font-weight: 700; color: #6366f1; width: 60px; }
.overdue-badge { background: #ef4444; color: #fff; padding: 0 6px; border-radius: 10px; font-size: 11px; }
.task-info { flex: 1; display: flex; gap: 8px; align-items: center; }
.task-client { font-weight: 600; font-size: 13px; }
.task-order { font-size: 11px; color: #6366f1; background: #eef2ff; padding: 1px 6px; border-radius: 10px; }
.task-phone { font-size: 11px; color: #64748b; }
.task-actions { display: flex; gap: 5px; }
.task-btn { padding: 4px 10px; border-radius: 6px; border: none; font-size: 11px; font-weight: 600; cursor: pointer; }
.task-call { background: #dbeafe; color: #1e40af; }
.task-move { background: #f1f5f9; color: #475569; }
.task-done { background: #d1fae5; color: #065f46; }
.crm-kanban { display: flex; gap: 16px; padding: 16px 24px; overflow-x: auto; flex: 1; align-items: flex-start; }
.crm-column { flex: 0 0 280px; background: #f8fafc; border-radius: 12px; max-height: 100%; display: flex; flex-direction: column; border: 2px solid transparent; }
.crm-column.drag-target { border-color: #6366f1; background: #eef2ff; }
.crm-col-header { padding: 12px 16px; border-top: 3px solid; border-radius: 10px 10px 0 0; }
.crm-col-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.crm-col-title { font-weight: 600; font-size: 14px; }
.crm-col-count { font-size: 11px; background: #e2e8f0; padding: 1px 8px; border-radius: 10px; float: right; }
.crm-col-amount { display: block; font-size: 11px; color: #94a3b8; margin-top: 4px; }
.crm-cards-list { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 10px; min-height: 100px; }
.crm-card { background: #fff; border-radius: 10px; padding: 12px; border: 1px solid #e2e8f0; border-left: 3px solid #e2e8f0; cursor: pointer; transition: transform 0.1s; }
.crm-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.priority-critical { border-left-color: #ef4444; }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-number { font-size: 12px; font-weight: 700; color: #6366f1; }
.card-priority-dot { width: 8px; height: 8px; border-radius: 50%; }
.card-priority-dot.priority-critical { background: #ef4444; }
.card-client { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 500; margin-bottom: 8px; }
.card-client-icon { font-size: 13px; color: #94a3b8; }
.card-finance-row { display: flex; justify-content: space-between; align-items: center; }
.card-amount { font-weight: 700; font-size: 13px; }
.card-pay-badge { font-size: 10px; padding: 1px 8px; border-radius: 10px; }
.pay-unpaid { background: #fee2e2; color: #991b1b; }
.pay-paid { background: #d1fae5; color: #065f46; }
.crm-add-card-btn { padding: 10px; border: none; background: transparent; color: #94a3b8; font-size: 12px; cursor: pointer; }
.crm-add-card-btn:hover { color: #6366f1; }
.reschedule-body { display: flex; flex-direction: column; gap: 12px; }
.quick-reschedule-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qr-btn { padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; cursor: pointer; font-size: 12px; font-weight: 600; }
.qr-btn:hover { background: #eef2ff; border-color: #6366f1; color: #6366f1; }
</style>
