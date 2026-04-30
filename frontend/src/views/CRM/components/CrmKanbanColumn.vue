<template>
  <div
    class="kanban-column"
    :class="[dragOverStage === stage.key ? 'drag-target' : '']"
    @dragover.prevent="$emit('dragOver', stage.key)"
    @dragleave="$emit('dragLeave')"
    @drop.prevent="$emit('drop', stage.key)"
  >
    <div class="kanban-column-header" :style="{ borderTopColor: stage.color }">
      <div class="crm-col-title-row">
        <div class="crm-col-title-left">
          <span class="crm-col-dot" :style="{ background: stage.color }" />
          <span class="crm-col-title">{{ stage.label }}</span>
        </div>
        <span class="crm-col-count-badge" :style="{ background: `${stage.color}33`, color: stage.color }">
          {{ orders.length }}
        </span>
      </div>
      <div class="crm-col-subheader" :style="{ color: stage.color }">
        ВСЬОГО: {{ formatCurrency(stageTotal) }} ₴
      </div>
      <div class="stage-meter" aria-hidden="true">
        <span :style="{ width: `${stageShare}%`, background: stage.color }" />
      </div>
    </div>

    <div class="kanban-column-content">
      <div v-if="!orders.length" class="stage-empty-state">
        <span :style="{ background: stage.color }"></span>
        <strong>Немає заявок</strong>
        <small>Стадія готова прийняти нові замовлення</small>
      </div>

      <CrmOrderCard
        v-for="(order, index) in orders"
        :key="order.id"
        :order="order"
        :index="index"
        :selected="selectedOrderIds.includes(order.id)"
        :health-class="getOrderHealthClass(order)"
        :counterparty-name="getCounterpartyName(order.counterparty_id)"
        :lead-source-label="getLeadSourceLabel(order)"
        :order-deadline="getOrderDeadline(order)"
        :sla-level="getSlaLevel(order.id)"
        :sla-hours="getSlaHours(order.id)"
        :attention-reason="getAttentionReason(order)"
        :attention-class="getAttentionClass(order)"
        :order-hints="getOrderHints(order)"
        :manager-name="getManagerName(getOrderManagerId(order))"
        :manager-initials="getManagerInitials(getOrderManagerId(order))"
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
        @drag-start="$emit('dragStart', $event)"
        @drag-end="$emit('dragEnd')"
        @open-editor="$emit('openEditor', $event)"
        @toggle-selection="$emit('toggleSelection', $event)"
        @open-client-profile="$emit('openClientProfile', $event)"
        @comm="(order, channel) => $emit('comm', order, channel)"
        @card-command="(cmd, order) => $emit('cardCommand', cmd, order)"
      />

      <div
        v-if="stageHasMore"
        @click.stop="$emit('loadMore', stage.key)"
        class="load-more-btn"
      >
        Завантажити ще ↓
      </div>
    </div>

    <button class="add-order-button" @click="$emit('newOrderInStage', stage.key)">
      <el-icon><Plus /></el-icon> + ДОДАТИ ЗАМОВЛЕННЯ
    </button>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import CrmOrderCard from './CrmOrderCard.vue'

defineProps({
  stage: { type: Object, required: true },
  orders: { type: Array, default: () => [] },
  stageTotal: { type: Number, default: 0 },
  stageShare: { type: Number, default: 0 },
  stageHasMore: { type: Boolean, default: false },
  dragOverStage: { type: String, default: null },
  selectedOrderIds: { type: Array, default: () => [] },
  getOrderHealthClass: { type: Function, required: true },
  getCounterpartyName: { type: Function, required: true },
  getLeadSourceLabel: { type: Function, required: true },
  getOrderDeadline: { type: Function, required: true },
  getSlaLevel: { type: Function, required: true },
  getSlaHours: { type: Function, required: true },
  getAttentionReason: { type: Function, required: true },
  getAttentionClass: { type: Function, required: true },
  getOrderHints: { type: Function, required: true },
  getManagerName: { type: Function, required: true },
  getManagerInitials: { type: Function, required: true },
  getOrderManagerId: { type: Function, required: true },
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
  'dragOver',
  'dragLeave',
  'drop',
  'dragStart',
  'dragEnd',
  'openEditor',
  'toggleSelection',
  'openClientProfile',
  'comm',
  'cardCommand',
  'loadMore',
  'newOrderInStage'
])
</script>
