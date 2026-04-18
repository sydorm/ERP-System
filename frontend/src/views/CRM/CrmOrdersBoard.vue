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

            <!-- Channel tag -->
            <span v-if="order.channel" class="card-channel-tag" :class="`channel-${order.channel}`">
              {{ getChannelLabel(order.channel) }}
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
import apiClient from '@/api/index.js'

const router = useRouter()

// ─── State ────────────────────────────────────────────────────────────────────
const loading     = ref(false)
const orders      = ref([])
const counterparties = ref([])
const users       = ref([])
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
  return orders.value.filter(o => o.next_contact_date === today)
})

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

const getPriorityLabel = (p) =>
  priorities.find(x => x.value === p)?.label || 'Звичайний'

const getPaymentLabel = (s) =>
  ({ unpaid: 'Не опл.', partial: 'Частково', paid: 'Оплачено' }[s] || s)

const getChannelLabel = (ch) =>
  ({ instagram: 'Instagram', website: 'Сайт', referral: 'Сарафанка',
     telegram: 'Telegram', olx: 'OLX', phone: 'Телефон' }[ch] || ch)

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
    await apiClient.patch(`/orders/${order.id}/stage?stage=${targetStage}`)
  } catch {
    order.crm_stage = prevStage
    ElMessage.error('Не вдалося змінити етап')
  }
  dragOrderId.value = null
}

// ─── Navigation ───────────────────────────────────────────────────────────────
const openEditor   = (order) => router.push(`/crm/orders/${order.id}`)
const openNewOrder = () => router.push('/crm/orders/new')
const openNewOrderInStage = (stage) => router.push(`/crm/orders/new?stage=${stage}`)

// ─── Fetch ────────────────────────────────────────────────────────────────────
const fetchAll = async () => {
  loading.value = true
  try {
    const [ordersRes, cpRes, usersRes] = await Promise.allSettled([
      apiClient.get('/orders?limit=500'),
      apiClient.get('/counterparties?limit=500'),
      apiClient.get('/users/colleagues'),
    ])
    orders.value         = ordersRes.status === 'fulfilled' ? ordersRes.value.data : []
    counterparties.value = cpRes.status === 'fulfilled' ? cpRes.value.data : []
    users.value          = usersRes.status === 'fulfilled' ? usersRes.value.data : []
  } catch (e) {
    ElMessage.error('Помилка завантаження даних: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    loading.value = false
  }
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
