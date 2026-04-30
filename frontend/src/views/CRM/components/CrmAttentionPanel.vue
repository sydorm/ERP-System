<template>
  <div
    v-if="attentionOrders.length"
    class="director-attention-strip"
    :class="{ 'is-expanded': attentionExpanded }"
  >
    <button class="attention-strip-title" @click="$emit('update:attentionExpanded', !attentionExpanded)">
      <span></span>
      <strong>Потребують уваги</strong>
      <small>{{ attentionOrders.length }} заявок</small>
      <em>{{ attentionExpanded ? 'Згорнути' : 'Розгорнути' }}</em>
    </button>
    <button
      class="attention-filter-toggle"
      :class="{ active: attentionOnly }"
      @click.stop="$emit('update:attentionOnly', !attentionOnly)"
    >
      {{ attentionOnly ? 'Показані тільки ці' : 'Показати на дошці' }}
    </button>
    <template v-if="attentionExpanded">
      <button
        v-for="order in attentionOrders.slice(0, 6)"
        :key="order.id"
        class="attention-order-pill"
        @click="$emit('openOrder', order)"
      >
        <b>#{{ order.order_number }}</b>
        <span>{{ getAttentionReasons(order).map(r => r.text).join(' · ') }}</span>
      </button>
    </template>
  </div>
</template>

<script setup>
defineProps({
  attentionOrders: { type: Array, default: () => [] },
  attentionExpanded: { type: Boolean, default: false },
  attentionOnly: { type: Boolean, default: false },
  getAttentionReasons: { type: Function, required: true }
})

defineEmits(['update:attentionExpanded', 'update:attentionOnly', 'openOrder'])
</script>
