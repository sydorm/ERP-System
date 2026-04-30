<template>
  <div class="crm-board-page">
    <div class="crm-sticky-workbar">

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
        <el-select
          v-model="filters.managerScope"
          class="manager-scope-select"
          placeholder="Менеджер"
        >
          <el-option label="Мої заявки" value="mine" />
          <el-option label="Усі заявки" value="all" />
          <el-option
            v-for="u in users"
            :key="u.id"
            :label="u.name"
            :value="`manager:${u.id}`"
          />
        </el-select>

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
              <el-badge v-if="activeControlsCount" :value="activeControlsCount" class="filter-badge" />
            </button>
          </template>
          <div class="filter-popover-content">
            <div class="filter-section">
              <label>Сортування</label>
              <el-select v-model="sortOption" placeholder="Сортувати">
                <el-option label="За датою (нові)" value="created_desc" />
                <el-option label="За дедлайном" value="deadline_asc" />
                <el-option label="За сумою (спадання)" value="amount_desc" />
                <el-option label="За пріоритетом" value="priority_desc" />
              </el-select>
            </div>
            <div class="filter-section">
              <label>Пріоритет</label>
              <el-select v-model="filters.priority" placeholder="Всі" clearable>
                <el-option label="Терміново" value="critical" />
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
              <el-select v-model="filters.managerScope" placeholder="Всі">
                <el-option label="Мої заявки" value="mine" />
                <el-option label="Усі заявки" value="all" />
                <el-option
                  v-for="u in users"
                  :key="u.id"
                  :label="u.name"
                  :value="`manager:${u.id}`"
                />
              </el-select>
            </div>
            <div class="filter-section">
              <el-checkbox v-model="filters.attentionOnly">Тільки потребують уваги</el-checkbox>
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
    <div class="crm-insights-row">
      <div class="crm-insight-card primary">
        <div class="insight-icon-badge"><el-icon><TrendCharts /></el-icon></div>
        <div class="insight-content">
          <span class="insight-label">Pipeline</span>
          <div class="insight-value-row">
            <strong>{{ formatCurrency(totalPipelineAmount) }} ₴</strong>
            <div class="insight-sparkline">
              <svg width="56" height="20" viewBox="0 0 64 28">
                <path d="M0 22C12 18 24 20 36 13C48 6 56 10 64 6" stroke="rgba(255,255,255,0.6)" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
          <small>{{ orders.length }} активних замовлень</small>
        </div>
      </div>
      <div class="crm-insight-card sla-card">
        <div class="insight-icon-badge"><el-icon><Bell /></el-icon></div>
        <div class="insight-content">
          <span class="insight-label">Гарячі SLA</span>
          <strong>{{ hotSlaCount }}</strong>
          <small>потребують уваги</small>
        </div>
      </div>
      <div class="crm-insight-card payment-card">
        <div class="insight-icon-badge"><el-icon><Money /></el-icon></div>
        <div class="insight-content">
          <span class="insight-label">Оплата</span>
          <strong>{{ paymentProgress }}%</strong>
          <small>сплачених замовлень</small>
        </div>
      </div>
      <div class="crm-insight-card today-card">
        <div class="insight-icon-badge"><el-icon><Calendar /></el-icon></div>
        <div class="insight-content">
          <span class="insight-label">Сьогодні</span>
          <strong>{{ todayTasks.length }}</strong>
          <small>{{ overdueTasks.length }} прострочено</small>
        </div>
      </div>
    </div>

    <div
      v-if="attentionOrders.length"
      class="director-attention-strip"
      :class="{ 'is-expanded': attentionExpanded }"
    >
      <button class="attention-strip-title" @click="attentionExpanded = !attentionExpanded">
        <span></span>
        <strong>Потребують уваги</strong>
        <small>{{ attentionOrders.length }} заявок</small>
        <em>{{ attentionExpanded ? 'Згорнути' : 'Розгорнути' }}</em>
      </button>
      <button
        class="attention-filter-toggle"
        :class="{ active: filters.attentionOnly }"
        @click.stop="filters.attentionOnly = !filters.attentionOnly"
      >
        {{ filters.attentionOnly ? 'Показані тільки ці' : 'Показати на дошці' }}
      </button>
      <template v-if="attentionExpanded">
        <button
          v-for="order in attentionOrders.slice(0, 6)"
          :key="order.id"
          class="attention-order-pill"
          @click="openEditor(order)"
        >
          <b>#{{ order.order_number }}</b>
          <span>{{ getAttentionReasons(order).map(r => r.text).join(' · ') }}</span>
        </button>
      </template>
    </div><!-- /director-attention-strip -->
    </div><!-- /crm-sticky-workbar -->

    <div class="crm-board-body">

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
          <div class="stage-meter" aria-hidden="true">
            <span :style="{ width: `${stageShare(stage.key)}%`, background: stage.color }" />
          </div>
        </div>

        <!-- Cards -->
        <div class="kanban-column-content">
          <div v-if="!filteredOrdersInStage(stage.key).length" class="stage-empty-state">
            <span :style="{ background: stage.color }"></span>
            <strong>Немає заявок</strong>
            <small>Стадія готова прийняти нові замовлення</small>
          </div>

          <div
            v-for="(order, index) in filteredOrdersInStage(stage.key)"
            :key="order.id"
            class="order-card"
            :class="[{ 'is-selected': selectedOrderIds.includes(order.id) }, getOrderHealthClass(order)]"
            :style="{ animationDelay: `${index * 50}ms` }"
            draggable="true"
            @dragstart="onDragStart(order)"
            @dragend="dragOrderId = null"
            @click="openEditor(order)"
          >
            <span class="card-health-rail" />
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
            <div class="card-row-2 card-source-row" v-if="getLeadSourceLabel(order) || getCounterpartyName(order.counterparty_id)">
              <span
                class="clickable-client"
                v-if="getCounterpartyName(order.counterparty_id)"
                @click.stop="openClientProfile(order.counterparty_id)"
              >
                {{ getCounterpartyName(order.counterparty_id) }}
              </span>
              <span v-if="getLeadSourceLabel(order)" class="lead-source-badge">
                {{ getLeadSourceLabel(order) }}
              </span>
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
                v-if="getOrderDeadline(order)"
                :class="getDeadlineClass(getOrderDeadline(order))"
              >
                📅 {{ formatDate(getOrderDeadline(order)) }} <span v-if="getDeadlineDaysText(getOrderDeadline(order))">· {{ getDeadlineDaysText(getOrderDeadline(order)) }}</span>
              </span>
            </div>

            <!-- Рядок 5: Бейдж оплати + SLA таймер -->
            <div class="card-badges">
              <span class="payment-badge" :class="`payment-${order.payment_status}`">
                ● {{ getPaymentLabel(order.payment_status) }}
              </span>
              <span
                v-if="getSlaLevel(order.id) === 'warning'"
                class="sla-badge sla-warning"
              >⏱ {{ getSlaHours(order.id) }} год</span>
              <span
                v-else-if="getSlaLevel(order.id) === 'critical' || getSlaLevel(order.id) === 'urgent'"
                class="sla-badge sla-critical"
              >🔴 {{ getSlaHours(order.id) }} год</span>
            </div>

            <!-- Contact Warnings (Only for New and Payment stages) -->
            <template v-if="['new', 'payment'].includes(order.crm_stage)">
              <div v-if="getAttentionReason(order)" class="card-next-action" :class="getAttentionClass(order)">
                <el-icon><Bell /></el-icon>
                <span>{{ getAttentionReason(order) }}</span>
              </div>

              <div class="next-contact-chip" :class="getNextContactClass(order)">
                <el-icon><Clock /></el-icon>
                <span>{{ getNextContactLabel(order) }}</span>
              </div>
            </template>

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
                <el-tooltip content="Подзвонити" placement="top">
                  <span class="channel-icon phone" @click.stop="handleComm(order, 'phone')"><el-icon><Phone /></el-icon></span>
                </el-tooltip>
                <el-tooltip content="Viber / коментар" placement="top">
                  <span class="channel-icon viber" @click.stop="handleComm(order, 'viber')"><el-icon><ChatDotRound /></el-icon></span>
                </el-tooltip>
                <el-tooltip content="Telegram" placement="top">
                  <span class="channel-icon telegram" @click.stop="handleComm(order, 'telegram')"><el-icon><Promotion /></el-icon></span>
                </el-tooltip>
                <el-tooltip content="Instagram" placement="top">
                  <span class="channel-icon instagram" @click.stop="handleComm(order, 'instagram')"><el-icon><Camera /></el-icon></span>
                </el-tooltip>
              </div>
              <div class="card-meta-right">
                <el-tooltip content="Підказка по заявці" placement="top">
                  <el-popover placement="top-end" :width="290" trigger="click" popper-class="crm-hint-popover">
                    <template #reference>
                      <button class="card-hint-btn" @click.stop>
                        <el-icon><MagicStick /></el-icon>
                      </button>
                    </template>
                    <div class="hint-popover-content" @click.stop>
                      <div class="hint-popover-title">
                        <el-icon><MagicStick /></el-icon>
                        Підказка по заявці
                      </div>
                      <ul v-if="getOrderHints(order).length" class="hint-list">
                        <li v-for="hint in getOrderHints(order)" :key="hint.text" :class="hint.level">
                          {{ hint.text }}
                        </li>
                      </ul>
                      <div v-else class="hint-good">Все добре. Критичних проблем немає.</div>
                    </div>
                  </el-popover>
                </el-tooltip>
                <el-tooltip :content="getManagerName(getOrderManagerId(order))" placement="top">
                  <div class="manager-chip">
                    <span class="card-avatar">{{ getManagerInitials(getOrderManagerId(order)) }}</span>
                    <span class="manager-name">{{ getManagerName(getOrderManagerId(order)) }}</span>
                  </div>
                </el-tooltip>
                <el-dropdown trigger="click" @command="(cmd) => handleCardCommand(cmd, order)" @click.stop>
                  <button class="card-more-btn" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="open">Відкрити заявку</el-dropdown-item>
                      <el-dropdown-item command="client" :disabled="!order.counterparty_id">Картка клієнта</el-dropdown-item>
                      <el-dropdown-item command="call">Подзвонити</el-dropdown-item>
                      <el-dropdown-item command="copy">Скопіювати номер</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
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

    <ClientProfile 
      v-model="clientProfileVisible"
      :client-id="selectedClientId"
    />

    </div><!-- /crm-board-body -->
  </div><!-- /crm-board-page -->
</template>

<script setup>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import { Search, Plus, Bell, Clock, Calendar, MoreFilled, Operation, ArrowDown, User as UserIcon, Phone, ChatDotRound, Close, Download, Promotion, Camera, TrendCharts, Money, Warning, MagicStick } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'
import ClientProfile from '@/views/CRM/ClientProfile.vue'

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
const userStore = useUserStore()
const orders = ref([])
const counterparties = ref([])
const users = ref([])
const leadSources = ref([])
const todayTasks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const slaStatus = ref({})
const attentionExpanded = ref(false)

const currentUser = computed(() => userStore.user || {})
const currentUserId = computed(() => currentUser.value?.id || null)
const currentUserRole = computed(() => currentUser.value?.role || '')
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

const attentionOrders = computed(() => {
  return orders.value
    .filter(order => getAttentionScore(order) > 0)
    .slice()
    .sort((a, b) => getAttentionScore(b) - getAttentionScore(a))
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

  if (!nextContact) reasons.push({ text: 'Немає наступного контакту', level: 'warning' })
  else if (new Date(nextContact) < new Date()) reasons.push({ text: 'Контакт прострочено', level: 'critical' })

  if (!hasPrepayment(order) && Number(order.total_amount || 0) > 0) reasons.push({ text: 'Немає передоплати', level: 'warning' })
  if (!deadline) reasons.push({ text: 'Немає дедлайну', level: 'warning' })
  else if (new Date(deadline) < new Date()) reasons.push({ text: 'Прострочений дедлайн', level: 'critical' })

  if (['critical', 'urgent'].includes(slaLevel)) reasons.push({ text: `Заявка довго на етапі: ${getSlaHours(order.id)} год`, level: 'critical' })
  else if (slaLevel === 'warning') reasons.push({ text: `Наближається SLA: ${getSlaHours(order.id)} год`, level: 'warning' })

  if (needsPaymentControl(order)) reasons.push({ text: 'Потрібен контроль оплати', level: 'warning' })

  return reasons
}

const getOrderHints = (order) => getAttentionReasons(order)

const getAttentionScore = (order) => {
  return getAttentionReasons(order).reduce((score, reason) => score + (reason.level === 'critical' ? 40 : 18), 0)
}

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
      api.get('/users/colleagues'),
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
  // Never show raw UUID/ID on UI
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

const handleCardCommand = async (command, order) => {
  if (command === 'open') {
    openEditor(order)
    return
  }

  if (command === 'client') {
    openClientProfile(order.counterparty_id)
    return
  }

  if (command === 'call') {
    handleComm(order, 'phone')
    return
  }

  if (command === 'copy') {
    const value = order.client_phone || order.order_number || ''
    if (!value) {
      ElMessage.warning('Немає даних для копіювання')
      return
    }
    try {
      await navigator.clipboard.writeText(value)
      ElMessage.success('Скопійовано')
    } catch {
      ElMessage.info(value)
    }
  }
}

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
/* ============================================================
   CRM BOARD — Unified design system (matches Purchases module)
   Tokens: primary #1463FF · bg #F5F8FC · border #E6ECF3
           success #15B97A · warning #F59E0B · danger #F04452
   ============================================================ */

/* ───── Page ───── */
.crm-board-page {
  background: var(--erp-bg-page, #F5F8FC);
  min-height: calc(100vh - 60px);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding: 0 0 32px;
}

/* ───── Sticky workbar ───── */
.crm-sticky-workbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(245, 248, 252, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--erp-border, #E6ECF3);
  padding: 14px 24px 12px;
  margin-bottom: 0;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08);
}

/* ───── Header ───── */
.crm-board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.crm-title-row { display: flex; align-items: center; gap: 10px; }

.crm-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--erp-text-heading, #0F172A);
  margin: 0;
  letter-spacing: -0.5px;
}

.crm-count-badge {
  font-size: 13px;
  font-weight: 600;
  color: var(--erp-text-muted, #7A88A0);
  background: #FFF;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 999px;
  padding: 2px 10px;
}

.crm-subtitle {
  font-size: 13px;
  color: var(--erp-text-muted, #7A88A0);
  margin: 3px 0 0;
}

.crm-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.manager-scope-select { width: 176px; }

/* View switch */
.crm-view-switch {
  display: flex;
  background: var(--erp-bg-surface-soft, #EEF3FA);
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
}

.view-btn {
  height: 30px;
  padding: 0 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: var(--erp-text-secondary, #5A6A80);
  transition: all 0.18s;
}
.view-btn.active {
  background: #FFF;
  color: var(--erp-text-heading, #0F172A);
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* Search */
.crm-search-input { width: 240px; }
:deep(.el-input__wrapper) {
  border-radius: 10px !important;
  box-shadow: none !important;
  border: 1px solid var(--erp-border, #E6ECF3) !important;
  height: 42px !important;
}

/* Reset */
.crm-reset-all-btn {
  background: transparent;
  border: none;
  color: var(--erp-status-danger, #F04452);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  padding: 0 6px;
  transition: opacity 0.18s;
}
.crm-reset-all-btn:hover { opacity: 0.72; }

/* Filter button */
.crm-filter-btn {
  height: 42px;
  padding: 0 14px;
  background: #FFF;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--erp-text-secondary, #5A6A80);
  transition: all 0.18s;
  position: relative;
}
.crm-filter-btn:hover {
  border-color: var(--erp-primary, #1463FF);
  color: var(--erp-primary, #1463FF);
}
.filter-badge { margin-left: 4px; }

/* Export button */
.crm-export-btn {
  height: 42px;
  padding: 0 14px;
  background: #FFF;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--erp-text-secondary, #5A6A80);
  transition: all 0.18s;
}
.crm-export-btn:hover {
  border-color: var(--erp-primary, #1463FF);
  color: var(--erp-primary, #1463FF);
}

/* New order button */
.crm-new-btn-indigo {
  height: 42px;
  padding: 0 18px;
  background: var(--erp-primary, #1463FF);
  border: none;
  border-radius: 10px;
  color: #FFF;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(20, 99, 255, 0.22);
  transition: all 0.18s;
}
.crm-new-btn-indigo:hover {
  background: #0F52E0;
  box-shadow: 0 6px 18px rgba(20, 99, 255, 0.3);
}

/* ───── Filter popover ───── */
.filter-popover-content { padding: 4px 0; }
.filter-section { margin-bottom: 12px; }
.filter-section label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--erp-text-muted, #7A88A0);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.filter-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid var(--erp-border, #E6ECF3);
  padding-top: 10px;
  margin-top: 4px;
}

/* ───── KPI Insight Cards ───── */
.crm-insights-row {
  display: grid;
  grid-template-columns: 1.25fr repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.crm-insight-card {
  background: #FFF;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.05);
  display: flex;
  align-items: flex-start;
  gap: 14px;
  transition: transform 0.18s, box-shadow 0.18s;
}
.crm-insight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(15,23,42,0.09);
}

.insight-icon-badge {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 20px;
  flex-shrink: 0;
  background: var(--erp-primary-light, #EEF4FF);
  color: var(--erp-primary, #1463FF);
}
.crm-insight-card.sla-card .insight-icon-badge {
  background: var(--erp-status-danger-bg, #FEF2F4);
  color: var(--erp-status-danger, #F04452);
}
.crm-insight-card.payment-card .insight-icon-badge {
  background: var(--erp-status-success-bg, #EDFAF4);
  color: var(--erp-status-success, #15B97A);
}
.crm-insight-card.today-card .insight-icon-badge {
  background: #F0EBFF;
  color: #7C4DFF;
}

.insight-content { flex: 1; min-width: 0; }

.insight-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--erp-text-muted, #7A88A0);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 4px;
}

.insight-value-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 4px;
}

.crm-insight-card strong {
  display: block;
  font-size: 22px;
  font-weight: 800;
  color: var(--erp-text-heading, #0F172A);
  line-height: 1.1;
  margin-bottom: 4px;
}

.insight-sparkline { opacity: 0.7; }

.crm-insight-card small {
  display: block;
  font-size: 12px;
  color: var(--erp-text-muted, #7A88A0);
}

/* Pipeline card (primary) */
.crm-insight-card.primary {
  background: var(--erp-primary, #1463FF);
  border-color: transparent;
  box-shadow: 0 4px 16px rgba(20, 99, 255, 0.25);
}
.crm-insight-card.primary .insight-icon-badge {
  background: rgba(255,255,255,0.2);
  color: #FFF;
}
.crm-insight-card.primary .insight-label { color: rgba(255,255,255,0.72); }
.crm-insight-card.primary strong { color: #FFF; }
.crm-insight-card.primary small { color: rgba(255,255,255,0.68); }
.crm-insight-card.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(20,99,255,0.35); }

/* ───── Attention strip ───── */
.director-attention-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  padding: 7px 10px;
  border: 1px solid rgba(245, 158, 11, 0.28);
  border-radius: 10px;
  background: #FFFBEB;
  margin-bottom: 2px;
}
.director-attention-strip.is-expanded { flex-wrap: wrap; }
.director-attention-strip:not(.is-expanded) { width: fit-content; max-width: 100%; padding-right: 10px; }

.attention-strip-title {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
  min-height: 24px;
  border: 0;
  color: #92400E;
  background: transparent;
  cursor: pointer;
}
.attention-strip-title span {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #F59E0B;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.15);
}
.attention-strip-title strong { font-size: 12px; }
.attention-strip-title small { color: #B45309; font-size: 11px; }
.attention-strip-title em {
  padding: 2px 8px;
  border-radius: 999px;
  color: #78350F;
  background: rgba(255,255,255,0.72);
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}

.attention-order-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 24px;
  max-width: 220px;
  padding: 3px 9px;
  border: 1px solid rgba(245,158,11,0.24);
  border-radius: 999px;
  color: #78350F;
  background: rgba(255,255,255,0.76);
  cursor: pointer;
  font-size: 12px;
}
.attention-order-pill b,
.attention-order-pill span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.attention-order-pill span { min-width: 0; color: #92400E; font-size: 11px; }

.attention-filter-toggle {
  height: 28px;
  border: 1px solid rgba(245, 158, 11, 0.25);
  background: rgba(255, 255, 255, 0.72);
  color: #92400E;
  border-radius: 999px;
  padding: 0 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}
.attention-filter-toggle.active {
  background: #92400E;
  border-color: #92400E;
  color: #FFF;
}

/* ───── Kanban Board ───── */
.crm-kanban {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 20px 24px 28px;
  align-items: flex-start;
  scroll-snap-type: x proximity;
  height: calc(100vh - 230px);
  min-height: 440px;
}

/* Column tint per stage */
.crm-kanban .kanban-column:nth-child(1) { background: #F7F9FF; }
.crm-kanban .kanban-column:nth-child(2) { background: #FFFAF4; }
.crm-kanban .kanban-column:nth-child(3) { background: #F5FFF9; }
.crm-kanban .kanban-column:nth-child(4) { background: #FAF6FF; }
.crm-kanban .kanban-column:nth-child(5) { background: #F4FDF8; }

.kanban-column {
  flex-shrink: 0;
  flex: 1;
  min-width: 274px;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 260px);
  max-height: 100%;
  border-radius: 14px;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-top-width: 3px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.04);
  scroll-snap-align: start;
  transition: outline 0.15s;
}

.kanban-column.drag-target {
  outline: 2px solid rgba(20, 99, 255, 0.28);
  outline-offset: 2px;
}

.kanban-column-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
  position: sticky;
  top: -12px; /* Pull up to match column padding */
  z-index: 10;
  padding: 12px 0 10px;
  background: inherit;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.crm-col-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.crm-col-title-left {
  display: flex;
  align-items: center;
  gap: 7px;
}

.crm-col-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.crm-col-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--erp-text-heading, #0F172A);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.crm-col-count-badge {
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}

.crm-col-subheader {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 999px;
  width: fit-content;
  background: rgba(255,255,255,0.7);
}

.stage-meter {
  height: 3px;
  border-radius: 999px;
  background: rgba(0,0,0,0.06);
  overflow: hidden;
}
.stage-meter span {
  display: block;
  height: 100%;
  border-radius: inherit;
  opacity: 0.8;
  min-width: 12px;
}

.kanban-column-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  padding-right: 2px;
}

/* Empty state */
.stage-empty-state {
  display: grid;
  place-items: center;
  min-height: 110px;
  padding: 16px;
  border: 1px dashed rgba(148,163,184,0.4);
  border-radius: 10px;
  text-align: center;
  background: rgba(255,255,255,0.4);
}
.stage-empty-state span {
  width: 10px; height: 10px;
  border-radius: 50%;
  margin-bottom: 8px;
  opacity: 0.6;
}
.stage-empty-state strong { font-size: 13px; color: var(--erp-text-secondary, #5A6A80); }
.stage-empty-state small {
  max-width: 180px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--erp-text-muted, #7A88A0);
  line-height: 1.4;
}

/* Add order button */
.add-order-button {
  margin: 8px 2px 2px;
  padding: 8px 0;
  min-height: 34px;
  width: calc(100% - 4px);
  border: 1px dashed var(--erp-border, #E6ECF3);
  border-radius: 10px;
  background: transparent;
  color: var(--erp-text-muted, #7A88A0);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.18s;
}
.add-order-button:hover {
  background: #FFF;
  border-color: var(--erp-primary, #1463FF);
  color: var(--erp-primary, #1463FF);
}

/* Load more */
.load-more-btn {
  text-align: center;
  padding: 8px;
  cursor: pointer;
  color: var(--erp-primary, #1463FF);
  font-size: 12px;
  font-weight: 700;
  background: rgba(20,99,255,0.05);
  border-radius: 8px;
  transition: background 0.18s;
}
.load-more-btn:hover { background: rgba(20,99,255,0.1); }

/* ───── Order Card ───── */
@keyframes cardIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.order-card {
  background: #FFF;
  border: 1px solid var(--erp-border, #E6ECF3);
  border-radius: 12px;
  padding: 12px 12px 12px 16px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  opacity: 0;
  animation: cardIn 0.28s ease forwards;
  box-shadow: 0 2px 8px rgba(15,23,42,0.04);
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.18s;
}

.order-card:hover {
  border-color: rgba(20, 99, 255, 0.28);
  box-shadow: 0 6px 20px rgba(15,23,42,0.09);
  transform: translateY(-1px);
}

.order-card.is-selected {
  border: 2px solid var(--erp-primary, #1463FF);
  background: #F0F5FF;
}

/* Health rail */
.card-health-rail {
  position: absolute;
  left: 0; top: 0;
  width: 4px; height: 100%;
  background: var(--erp-border, #E6ECF3);
}
.order-health-critical .card-health-rail { background: linear-gradient(180deg, #F04452, #FB7185); }
.order-health-warning .card-health-rail { background: linear-gradient(180deg, #F59E0B, #FBBF24); }
.order-health-paid .card-health-rail { background: linear-gradient(180deg, #15B97A, #34D399); }
.order-health-neutral .card-health-rail { background: linear-gradient(180deg, #CBD5E1, #E2E8F0); }

.card-selection-overlay {
  position: absolute;
  top: 8px; left: 8px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.18s;
}
.order-card:hover .card-selection-overlay,
.order-card.is-selected .card-selection-overlay { opacity: 1; }

/* Row 1 */
.card-row-1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  gap: 6px;
}
.card-order-no {
  font-size: 11px;
  font-weight: 600;
  color: var(--erp-text-muted, #7A88A0);
  background: var(--erp-bg-page, #F5F8FC);
  padding: 2px 7px;
  border-radius: 999px;
}
.priority-wrapper {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--erp-bg-page, #F5F8FC);
}
.priority-dot { width: 6px; height: 6px; border-radius: 50%; }

/* Row 2 */
.card-row-2 {
  font-size: 11px;
  color: var(--erp-text-muted, #7A88A0);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 6px;
}
.card-source-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.lead-source-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 2px 7px;
  background: #EEF4FF;
  color: #1463FF;
  font-size: 10px;
  font-weight: 800;
  text-transform: none;
  letter-spacing: 0;
}

/* Title */
.order-card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--erp-text-heading, #0F172A);
  margin: 5px 0;
  line-height: 1.35;
}

/* Financial */
.card-row-financial {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.card-price {
  font-size: 15px;
  font-weight: 800;
  color: var(--erp-primary, #1463FF);
}
.deadline-chip {
  font-size: 11px;
  color: var(--erp-text-secondary, #5A6A80);
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--erp-bg-page, #F5F8FC);
}
.deadline-chip.deadline-danger {
  color: var(--erp-status-danger, #F04452);
  background: #FEF2F4;
}
.deadline-chip.deadline-warning { color: #92400E; background: #FFFBEB; }

/* Badges */
.card-badges { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 2px; }

.payment-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
}
.payment-badge.payment-paid { background: #EDFAF4; color: #0F5C3A; }
.payment-badge.payment-partial { background: #FFFBEB; color: #92400E; }
.payment-badge.payment-unpaid { background: var(--erp-bg-page, #F5F8FC); color: var(--erp-text-muted, #7A88A0); }

/* SLA badges */
.sla-badge {
  display: inline-flex;
  align-items: center;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
}
.sla-warning { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.sla-critical { background: #FEF2F4; color: var(--erp-status-danger, #F04452); border: 1px solid #FECACA; }

/* Next action strip */
.card-next-action {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 6px 0 0;
  padding: 5px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
}
.card-next-action.attention-critical { color: #991B1B; background: #FEE2E2; }
.card-next-action.attention-warning { color: #92400E; background: #FEF3C7; }
.card-next-action.attention-info { color: var(--erp-text-secondary, #5A6A80); background: var(--erp-bg-page, #F5F8FC); }

.next-contact-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  max-width: 100%;
  margin-top: 6px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid transparent;
}
.next-contact-chip.is-empty {
  color: #64748B;
  background: #F8FAFC;
  border-color: #E2E8F0;
}
.next-contact-chip.is-planned {
  color: #0F766E;
  background: #ECFDF5;
  border-color: #A7F3D0;
}
.next-contact-chip.is-overdue {
  color: #92400E;
  background: #FFFBEB;
  border-color: #FDE68A;
}

/* Divider */
.card-divider { border-top: 1px solid var(--erp-border, #E6ECF3); margin: 8px 0; }

/* Last contact */
.card-last-contact {
  font-size: 12px;
  display: flex;
  gap: 5px;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px 8px;
  border-radius: 8px;
  background: var(--erp-bg-page, #F5F8FC);
}
.contact-channel-icon { font-size: 13px; }
.contact-channel-icon.reminder { color: var(--erp-status-danger, #F04452); }
.contact-channel-icon.phone { color: var(--erp-status-success, #15B97A); }
.contact-channel-icon.viber { color: #7C3AED; }
.contact-channel-icon.telegram { color: #2563EB; }
.contact-channel-icon.instagram { color: #DB2777; }

.contact-result { font-weight: 700; }
.contact-result.thinking { color: #F59E0B; }
.contact-result.no_answer { color: var(--erp-status-danger, #F04452); }
.contact-result.confirmed { color: var(--erp-status-success, #15B97A); }
.contact-result.refused { color: var(--erp-text-muted, #7A88A0); }
.contact-time { color: var(--erp-text-muted, #7A88A0); }

/* Card footer */
.card-footer-new { display: flex; justify-content: space-between; align-items: center; }

.card-comm-channels { display: flex; gap: 6px; align-items: center; }

.channel-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.18s;
}
.channel-icon.phone { background: #EDFAF4; color: var(--erp-status-success, #15B97A); border: 1px solid rgba(21,185,122,0.24); }
.channel-icon.viber { background: #F5F3FF; color: #7C3AED; border: 1px solid rgba(124,58,237,0.24); }
.channel-icon.telegram { background: #EFF6FF; color: #2563EB; border: 1px solid rgba(37,99,235,0.24); }
.channel-icon.instagram { background: #FDF2F8; color: #DB2777; border: 1px solid rgba(219,39,119,0.24); }
.channel-icon:hover { filter: brightness(0.92); transform: scale(1.06); }

.card-meta-right { display: flex; align-items: center; gap: 7px; }

.manager-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  max-width: 112px;
  padding: 2px 7px 2px 2px;
  border-radius: 10px;
  background: #F8FAFC;
  border: 1px solid #E6ECF3;
}

.card-avatar {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--erp-primary, #1463FF);
  color: #FFF;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.manager-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  font-weight: 700;
  color: #334155;
}

.card-hint-btn {
  width: 28px; height: 28px;
  border-radius: 8px;
  border: 1px solid #D8B4FE;
  color: #7E22CE;
  background: #FAF5FF;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.18s;
}
.card-hint-btn:hover {
  background: #7E22CE;
  color: #FFF;
  border-color: #7E22CE;
}

.hint-popover-content { padding: 4px 2px; }
.hint-popover-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #111827;
  font-size: 13px;
  font-weight: 800;
}
.hint-list {
  display: grid;
  gap: 6px;
  padding: 0;
  margin: 0;
  list-style: none;
}
.hint-list li {
  padding: 7px 9px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
}
.hint-list li.warning { background: #FFFBEB; color: #92400E; }
.hint-list li.critical { background: #FEF2F4; color: #991B1B; }
.hint-good {
  padding: 10px;
  border-radius: 10px;
  background: #ECFDF5;
  color: #047857;
  font-size: 12px;
  font-weight: 700;
}

.card-arrow-btn {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--erp-primary-light, #EEF4FF);
  color: var(--erp-primary, #1463FF);
  border: 1px solid rgba(20, 99, 255, 0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0;
  transition: all 0.18s;
}
.card-arrow-btn::before { content: "›"; font-size: 18px; line-height: 1; }
.card-arrow-btn:hover { background: var(--erp-primary, #1463FF); color: #FFF; }

.card-more-btn {
  width: 28px; height: 28px;
  border-radius: 8px;
  border: 1px solid var(--erp-border, #E6ECF3);
  color: var(--erp-text-secondary, #5A6A80);
  background: #FFF;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.18s;
}
.card-more-btn:hover {
  border-color: var(--erp-primary, #1463FF);
  color: var(--erp-primary, #1463FF);
  background: var(--erp-primary-light, #EEF4FF);
}

/* Clickable client */
.clickable-client { cursor: pointer; color: var(--erp-primary, #1463FF); font-weight: 600; }
.clickable-client:hover { text-decoration: underline; }

/* ───── Selection bar ───── */
.selection-bar {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  background: #1B2430;
  color: #FFF;
  padding: 12px 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.25);
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
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.25);
  color: #FFF;
}
.selection-actions .el-button--primary.is-plain:hover {
  background: #FFF;
  color: #1B2430;
}

/* ───── Responsive ───── */

@media (max-width: 1280px) {
  .crm-board-header { flex-direction: column; align-items: flex-start; }
  .crm-header-right { justify-content: flex-start; }
  .crm-insights-row { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 760px) {
  .crm-sticky-workbar { padding: 10px 14px 8px; }
  .crm-kanban { padding: 14px 14px 20px; }
  .crm-title { font-size: 22px; }
  .crm-insights-row { grid-template-columns: 1fr; }
  .kanban-column { min-width: 80vw; }
  .crm-search-input,
  .manager-scope-select,
  .crm-filter-btn,
  .crm-new-btn-indigo { width: 100%; }
  .selection-bar {
    width: calc(100vw - 24px);
    bottom: 14px;
    flex-direction: column;
    align-items: stretch;
    border-radius: 14px;
    gap: 12px;
  }
  .selection-actions { flex-wrap: wrap; }
}

/* ─── keep ─── */
.crm-board-header {
  align-items: center;
}

/* ─── end of styles ─── */

.ai-sparkle-btn {
  background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
  color: #0D9488;
  border: 1px solid #99F6E4;
  box-shadow: 0 2px 6px rgba(13, 148, 136, 0.15);
}
.ai-sparkle-btn:hover {
  background: linear-gradient(135deg, #CCFBF1 0%, #99F6E4 100%);
  transform: scale(1.05);
}

.manager-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #F1F5F9;
  padding: 2px 8px 2px 4px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
}
.card-avatar {
  width: 20px;
  height: 20px;
  background: #3D3AA8;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 800;
}
</style>
