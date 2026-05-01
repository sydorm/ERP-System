<template>
  <div
    class="order-card"
    :class="[{ 'is-selected': selected }, healthClass]"
    :style="{ animationDelay }"
    draggable="true"
    @dragstart="$emit('dragStart', order)"
    @dragend="$emit('dragEnd')"
    @click="$emit('openEditor', order)"
  >
    <span class="card-health-rail" />
    <div class="card-selection-overlay" @click.stop="$emit('toggleSelection', order.id)">
      <el-checkbox
        :model-value="selected"
        @change="$emit('toggleSelection', order.id)"
        @click.stop
      />
    </div>

    <div class="card-row-1">
      <div class="card-id-manager">
        <span class="card-order-no">#{{ order.order_number }}</span>
        <el-tooltip :content="managerName || 'Не призначено'" placement="top">
          <div class="mini-manager-avatar">
            {{ getManagerInitials(order) || '?' }}
          </div>
        </el-tooltip>
      </div>
      <div class="priority-wrapper" :class="order.priority">
        <span class="priority-dot" :style="{ background: getPriorityColor(order.priority) }" />
        <span class="priority-text" :style="{ color: getPriorityColor(order.priority) }">
          {{ getPriorityLabel(order.priority) }}
        </span>
      </div>
    </div>

    <div class="card-row-2 card-source-row" v-if="leadSourceLabel || counterpartyName">
      <span
        class="clickable-client"
        v-if="counterpartyName"
        @click.stop="$emit('openClientProfile', order.counterparty_id)"
      >
        {{ counterpartyName }}
      </span>
      <span v-if="leadSourceLabel" class="lead-source-badge">
        {{ leadSourceLabel }}
      </span>
    </div>

    <div class="order-card-title">
      {{ order.product_name || 'Індивідуальне замовлення' }}
    </div>

    <div class="card-row-financial">
      <span class="card-price">{{ formatCurrency(order.total_amount) }} ₴</span>
      <span
        class="deadline-chip"
        v-if="orderDeadline"
        :class="getDeadlineClass(orderDeadline)"
      >
        📅 {{ formatDate(orderDeadline) }} <span v-if="getDeadlineDaysText(orderDeadline)">· {{ getDeadlineDaysText(orderDeadline) }}</span>
      </span>
    </div>

    <div class="card-badges">
      <span class="payment-badge" :class="`payment-${order.payment_status}`">
        ● {{ getPaymentLabel(order.payment_status) }}
      </span>
      <span v-if="slaLevel === 'warning'" class="sla-badge sla-warning">⏱ {{ slaHours }} год</span>
      <span v-else-if="slaLevel === 'critical' || slaLevel === 'urgent'" class="sla-badge sla-critical">🔴 {{ slaHours }} год</span>
    </div>

    <!-- Toggle bar — always visible -->
    <div class="card-actions-bar" @click.stop="actionsOpen = !actionsOpen">
      <el-icon class="actions-chevron" :class="{ 'is-open': actionsOpen }"><ArrowDown /></el-icon>
      <span class="actions-bar-label">
        <span v-if="attentionReason && !actionsOpen" class="actions-bar-alert">⚠</span>
        Деталі та дії
      </span>
      <div class="actions-channel-preview">
        <span class="ch-dot ch-phone" />
        <span class="ch-dot ch-viber" />
        <span class="ch-dot ch-telegram" />
        <span class="ch-dot ch-instagram" />
      </div>
    </div>

    <!-- Expandable: details + icons -->
    <transition name="actions-slide">
      <div v-if="actionsOpen" class="card-detail-section" @click.stop>

        <template v-if="['new', 'payment'].includes(order.crm_stage)">
          <div v-if="attentionReason" class="card-next-action" :class="attentionClass">
            <el-icon><Bell /></el-icon>
            <span>{{ attentionReason }}</span>
          </div>
          <div class="next-contact-chip" :class="getNextContactClass(order)">
            <el-icon><Clock /></el-icon>
            <span>{{ getNextContactLabel(order) }}</span>
          </div>
        </template>

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

        <el-tooltip :content="managerName" placement="top">
          <div class="card-manager-row">
            <span class="manager-label">Менеджер:</span>
            <span class="manager-name">{{ managerName }}</span>
          </div>
        </el-tooltip>

        <div class="card-divider" />

        <div class="card-footer-new">
          <div class="card-comm-channels">
            <el-tooltip content="Подзвонити" placement="top">
              <span class="channel-icon phone" @click.stop="$emit('comm', order, 'phone')"><el-icon><Phone /></el-icon></span>
            </el-tooltip>
            <el-tooltip content="Viber / коментар" placement="top">
              <span class="channel-icon viber" @click.stop="$emit('comm', order, 'viber')"><el-icon><ChatDotRound /></el-icon></span>
            </el-tooltip>
            <el-tooltip content="Telegram" placement="top">
              <span class="channel-icon telegram" @click.stop="$emit('comm', order, 'telegram')"><el-icon><Promotion /></el-icon></span>
            </el-tooltip>
            <el-tooltip content="Instagram" placement="top">
              <span class="channel-icon instagram" @click.stop="$emit('comm', order, 'instagram')"><el-icon><Camera /></el-icon></span>
            </el-tooltip>
          </div>
          <div class="card-meta-right">
            <el-tooltip content="Підказка по заявці" placement="top">
              <CrmAiHintPopover :hints="orderHints" />
            </el-tooltip>
            <el-dropdown trigger="click" @command="(cmd) => $emit('cardCommand', cmd, order)" @click.stop>
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
          </div>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bell, Clock, MoreFilled, Phone, ChatDotRound, Promotion, Camera, ArrowDown } from '@element-plus/icons-vue'
import CrmAiHintPopover from './CrmAiHintPopover.vue'

const props = defineProps({
  order: { type: Object, required: true },
  index: { type: Number, default: 0 },
  selected: { type: Boolean, default: false },
  healthClass: { type: String, default: '' },
  counterpartyName: { type: String, default: '' },
  leadSourceLabel: { type: String, default: '' },
  orderDeadline: { type: [String, Date], default: null },
  slaLevel: { type: String, default: 'ok' },
  slaHours: { type: [String, Number], default: 0 },
  attentionReason: { type: String, default: '' },
  attentionClass: { type: String, default: '' },
  orderHints: { type: Array, default: () => [] },
  managerName: { type: String, default: '' },
  managerInitials: { type: String, default: '?' },
  getPriorityColor: { type: Function, required: true },
  getPriorityLabel: { type: Function, required: true },
  getDeadlineClass: { type: Function, required: true },
  getDeadlineDaysText: { type: Function, required: true },
  getNextContactClass: { type: Function, required: true },
  getNextContactLabel: { type: Function, required: true },
  getPaymentLabel: { type: Function, required: true },
  getContactResultLabel: { type: Function, required: true },
  getChannelIcon: { type: Function, required: true },
  formatCurrency: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  formatRelativeTime: { type: Function, required: true },
  isReminderToday: { type: Function, required: true }
})

defineEmits([
  'dragStart',
  'dragEnd',
  'openEditor',
  'toggleSelection',
  'openClientProfile',
  'comm',
  'cardCommand'
])

const animationDelay = computed(() => `${props.index * 50}ms`)
const actionsOpen = ref(false)
</script>

<style scoped>
/* ── Actions toggle bar ── */
.card-actions-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 5px 0 1px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 6px;
  user-select: none;
  transition: opacity 0.15s;
}
.card-actions-bar:hover { opacity: 0.7; }

.actions-chevron {
  font-size: 10px;
  color: #9CA3AF;
  transition: transform 0.2s;
  flex-shrink: 0;
}
.actions-chevron.is-open { transform: rotate(180deg); }

.actions-bar-label {
  font-size: 11px;
  font-weight: 500;
  color: #9CA3AF;
  flex: 1;
}

/* Colored channel dots shown in collapsed state */
.actions-channel-preview {
  display: flex;
  gap: 4px;
  align-items: center;
}
.ch-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.ch-dot.ch-phone    { background: #22C55E; }
.ch-dot.ch-viber    { background: #8B5CF6; }
.ch-dot.ch-telegram { background: #3B82F6; }
.ch-dot.ch-instagram { background: #EC4899; }

.actions-bar-alert {
  color: #F59E0B;
  margin-right: 2px;
  font-size: 10px;
}

.card-detail-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 6px;
}

/* ── Slide transition ── */
.actions-slide-enter-active,
.actions-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
  overflow: hidden;
}
.actions-slide-enter-from,
.actions-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
