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
      <span class="card-order-no">#{{ order.order_number }}</span>
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
        в—Џ {{ getPaymentLabel(order.payment_status) }}
      </span>
      <span v-if="slaLevel === 'warning'" class="sla-badge sla-warning">⏱ {{ slaHours }} год</span>
      <span v-else-if="slaLevel === 'critical' || slaLevel === 'urgent'" class="sla-badge sla-critical">🔴 {{ slaHours }} год</span>
    </div>

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

    <div class="card-divider"></div>

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
        <span class="card-avatar">{{ managerInitials }}</span>
        <span class="manager-label">Менеджер:</span>
        <span class="manager-name">{{ managerName }}</span>
      </div>
    </el-tooltip>

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
        <button class="card-arrow-btn" @click.stop="$emit('openEditor', order)">→</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bell, Clock, MoreFilled, Phone, ChatDotRound, Promotion, Camera } from '@element-plus/icons-vue'
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
</script>
