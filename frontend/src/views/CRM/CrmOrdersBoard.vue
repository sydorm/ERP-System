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
          <button class="view-btn">Список</button>
        </div>
        <button class="crm-filter-btn">
          <el-icon><Operation /></el-icon> Фільтри
        </button>
        <button class="crm-new-btn-indigo" @click="openNewOrder">
          <el-icon><Plus /></el-icon> Нове замовлення
        </button>
      </div>
    </div>

    <div class="crm-tools-row">
      <div class="tool-item">Сортувати <el-icon><ArrowDown /></el-icon></div>
      <div class="tool-item">Групувати <el-icon><ArrowDown /></el-icon></div>
      <div class="tool-item">Вигляд <el-icon><ArrowDown /></el-icon></div>
    </div>

    <!-- ===== MY TASKS TODAY ===== -->
    <div class="crm-tasks-panel" v-if="overdueTasks.length">
      <div class="tasks-panel-head">
        <el-icon class="tasks-icon"><Bell /></el-icon>
        <span class="tasks-title">Мої задачі на сьогодні (горить)</span>
        <span class="tasks-count">{{ overdueTasks.length }}</span>
      </div>
      <div class="tasks-list">
        <div
          v-for="task in overdueTasks"
          :key="task.id"
          class="task-row task-overdue"
        >
          <div class="task-time">
            <span class="overdue-badge">!</span>
            <span class="task-time-val">{{ formatTaskTime(task.scheduled_at) }}</span>
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
        <div class="crm-col-header" :style="{ borderTopColor: stage.color }">
          <div class="crm-col-title-row">
            <span class="crm-col-dot" :style="{ background: stage.color }" />
            <span class="crm-col-title">{{ stage.label }}</span>
            <span class="crm-col-count-bubble">{{ ordersInStage(stage.key).length }}</span>
            <el-icon class="crm-col-menu"><MoreFilled /></el-icon>
          </div>
          <div class="crm-col-subheader">
            ВСЬОГО: {{ formatCurrency(stageTotal(stage.key)) }} ГРН
          </div>
        </div>

        <!-- Cards -->
        <div class="crm-cards-list">
          <div
            v-for="order in filteredOrdersInStage(stage.key)"
            :key="order.id"
            class="crm-card"
            draggable="true"
            @dragstart="onDragStart(order)"
            @dragend="dragOrderId = null"
            @click="openEditor(order)"
          >
            <div class="card-header">
              <span class="card-order-no">#{{ order.order_number }}</span>
              <span class="card-priority-mark" :style="{ background: stage.color }" />
            </div>
            
            <div class="card-main">
              <div class="card-customer">{{ getCounterpartyName(order.counterparty_id) || '—' }}</div>
              <div class="card-product">{{ order.product_name || 'Індивідуальне замовлення' }}</div>
            </div>

            <div class="card-financial">
              <span class="card-price">{{ formatCurrency(order.total_amount) }} ₴</span>
              <span class="card-deadline-pill" v-if="order.deadline">
                <el-icon><Calendar /></el-icon> {{ formatDate(order.deadline) }}
              </span>
            </div>

            <div class="card-footer">
              <div class="card-badges">
                <span class="payment-badge" :class="`pay-${order.payment_status}`">
                  {{ getPaymentLabel(order.payment_status) }}
                </span>
              </div>
              <div class="card-meta">
                <div class="card-avatar">{{ (getCounterpartyName(order.counterparty_id) || '?').charAt(0) }}</div>
                <div class="card-comm-icons">
                  <span class="comm-status-dot">●</span>
                  <span class="comm-status-text">Контакт</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button class="crm-add-card-btn" @click="openNewOrderInStage(stage.key)">
          <el-icon><Plus /></el-icon> + ДОДАТИ ЗАМОВЛЕННЯ
        </button>

        <div v-if="hasMore" class="crm-load-more-container">
          <button class="crm-load-more-btn" @click="loadMore">
            Завантажити ще...
          </button>
        </div>
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
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import { Search, Plus, Bell, Clock, Calendar, MoreFilled, Operation, ArrowDown, User as UserIcon } from '@element-plus/icons-vue'
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
const filterPriority = ref('')
const filterManager = ref('')
const limit = 50
const offset = ref(0)
const hasMore = ref(true)

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

const priorities = [
  { value: 'normal', label: 'Звичайний' },
  { value: 'urgent', label: 'Терміновий' },
  { value: 'critical', label: 'Критичний' }
]

const fetchAll = async () => {
  loading.value = true
  offset.value = 0
  try {
    const [ordersRes, cpRes, usersRes, tasksRes] = await Promise.all([
      api.get(`/api/v1/orders?limit=${limit}&offset=0`),
      api.get('/api/v1/counterparties?limit=500'),
      api.get('/users/colleagues'),
      api.get('/api/v1/crm/tasks/today')
    ])
    orders.value = ordersRes.data
    counterparties.value = cpRes.data
    users.value = usersRes.data
    todayTasks.value = tasksRes.data
    hasMore.value = ordersRes.data.length === limit
  } catch (e) {
    ElMessage.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  loading.value = true
  offset.value += limit
  try {
    const res = await api.get(`/api/v1/orders?limit=${limit}&offset=${offset.value}`)
    if (res.data.length > 0) {
      orders.value = [...orders.value, ...res.data]
    }
    hasMore.value = res.data.length === limit
  } catch (e) {
    ElMessage.error('Помилка завантаження додаткових даних')
  } finally {
    loading.value = false
  }
}

const getCounterpartyName = (id) => counterparties.value.find(c => c.id === id)?.name || id
const formatCurrency = (val) => new Intl.NumberFormat('uk-UA').format(val || 0)
const formatTaskTime = (ts) => new Date(ts).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' })
const isTaskOverdue = (task) => new Date(task.scheduled_at) < new Date()

const ordersInStage = (stage) => orders.value.filter(o => o.crm_stage === stage)
const filteredOrdersInStage = (stage) => {
  let list = ordersInStage(stage)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => 
      o.order_number.toLowerCase().includes(q) || 
      getCounterpartyName(o.counterparty_id).toLowerCase().includes(q) ||
      (o.client_name && o.client_name.toLowerCase().includes(q))
    )
  }
  if (filterPriority.value) list = list.filter(o => o.priority === filterPriority.value)
  if (filterManager.value) list = list.filter(o => o.manager_id === filterManager.value)
  return list
}
const stageTotal = (stage) => ordersInStage(stage).reduce((sum, o) => sum + (Number(o.total_amount) || 0), 0)

const getPaymentLabel = (s) => ({ unpaid: 'НЕ ОПЛАЧЕНО', partial: 'ЧАСТКОВО', paid: 'ОПЛАЧЕНО' }[s] || s)

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
  padding: 24px;
  background: #F4F5F7;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ─── Header ─── */
.crm-board-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.crm-title-row { display: flex; align-items: center; gap: 12px; }
.crm-title { font-size: 28px; font-weight: 800; color: #1e293b; margin: 0; }
.crm-count-badge { font-size: 16px; color: #94a3b8; font-weight: 500; }
.crm-subtitle { font-size: 14px; color: #64748b; margin: 4px 0 0; }

.crm-header-right { display: flex; gap: 12px; align-items: center; }
.crm-view-switch { background: #e2e8f0; padding: 2px; border-radius: 8px; display: flex; }
.view-btn { padding: 6px 12px; border: none; background: transparent; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; color: #64748b; }
.view-btn.active { background: #fff; color: #1e293b; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

.crm-filter-btn { background: #fff; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; color: #475569; }
.crm-new-btn-indigo { background: #3D3AA8; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }

.crm-tools-row { display: flex; gap: 20px; margin-bottom: 24px; }
.tool-item { font-size: 13px; color: #64748b; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 4px; }

/* ─── Tasks Panel ─── */
.crm-tasks-panel {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
}
.tasks-panel-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.tasks-icon { color: #f59e0b; font-size: 20px; }
.tasks-title { font-weight: 700; color: #1e293b; }
.tasks-count { background: #fee2e2; color: #ef4444; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 700; }

.tasks-list { display: flex; flex-direction: column; gap: 8px; }
.task-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
}
.task-time { display: flex; align-items: center; gap: 6px; width: 100px; }
.overdue-badge { background: #ef4444; color: #fff; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 11px; font-weight: 800; }
.task-time-val { font-weight: 600; font-size: 13px; color: #ef4444; }
.task-info { flex: 1; display: flex; flex-direction: column; }
.task-client { font-weight: 600; color: #1e293b; }
.task-order { font-size: 12px; color: #64748b; }
.task-actions { display: flex; gap: 8px; }
.task-btn { padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: 1px solid #e2e8f0; background: #fff; }
.task-call { background: #3D3AA8; color: #fff; border: none; }
.task-done { color: #22c55e; }

/* ─── Kanban ─── */
.crm-kanban {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 20px;
  align-items: flex-start;
}
.crm-column {
  flex: 1;
  min-width: 280px;
  background: #FFFFFF;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-top: 3px solid #e2e8f0;
}
.crm-col-header { padding: 16px 16px 12px; }
.crm-col-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; position: relative; }
.crm-col-dot { width: 10px; height: 10px; border-radius: 50%; }
.crm-col-title { font-weight: 700; color: #1e293b; font-size: 15px; }
.crm-col-count-bubble { 
  background: #f1f5f9; 
  color: #94a3b8; 
  font-size: 11px; 
  font-weight: 700; 
  padding: 2px 8px; 
  border-radius: 4px; 
  margin-left: 8px; 
}
.crm-col-menu { position: absolute; right: 0; color: #cbd5e1; cursor: pointer; font-size: 18px; }
.crm-col-subheader { font-size: 10px; color: #94a3b8; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }

.crm-cards-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100px;
  background: transparent;
  margin: 0;
}

/* ─── Card ─── */
.crm-card {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.crm-card:hover { border-color: #3D3AA8; transform: translateY(-1px); }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-order-no { font-size: 11px; color: #94a3b8; font-weight: 600; }
.card-priority-mark { width: 8px; height: 8px; border-radius: 50%; }

.card-main { margin-bottom: 10px; }
.card-customer { font-weight: 700; color: #1e293b; font-size: 15px; margin-bottom: 2px; }
.card-product { font-size: 13px; color: #64748b; }

.card-financial {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-price { font-weight: 700; color: #1e293b; font-size: 15px; }
.card-deadline-pill { 
  font-size: 11px; 
  color: #64748b; 
  display: flex; 
  align-items: center; 
  gap: 4px; 
  background: #f8fafc;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
}

.card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px; }
.payment-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
}
.pay-unpaid { background: #f1f5f9; color: #64748b; }
.pay-partial { background: #fef3c7; color: #92400e; }
.pay-paid    { background: #d1fae5; color: #065f46; }

.card-meta { display: flex; align-items: center; gap: 8px; }
.card-avatar {
  width: 26px;
  height: 26px;
  background: #e2e8f0;
  color: #475569;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}
.card-comm-icons { display: flex; align-items: center; gap: 4px; }
.comm-status-dot { font-size: 8px; color: #3D3AA8; }
.comm-status-text { font-size: 11px; color: #3D3AA8; font-weight: 600; }

/* ─── Add Button ─── */
.crm-add-card-btn {
  margin: 8px 12px 12px;
  height: 40px;
  border: 1.5px dashed #CBD5E1;
  background: transparent;
  border-radius: 8px;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.crm-add-card-btn:hover { border-color: #3D3AA8; color: #3D3AA8; background: #f5f3ff; }

.crm-load-more-btn { background: none; border: none; color: #3D3AA8; font-size: 11px; font-weight: 600; cursor: pointer; padding: 12px; }

.reschedule-body { display: flex; flex-direction: column; gap: 12px; }
.quick-reschedule-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qr-btn { padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; cursor: pointer; font-size: 12px; font-weight: 600; }
.qr-btn:hover { background: #eef2ff; border-color: #3D3AA8; color: #3D3AA8; }

</style>
