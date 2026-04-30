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
    <transition-group name="pill-fade">
      <button
        v-for="order in (attentionExpanded ? attentionOrders.slice(0, 8) : [])"
        :key="order.id"
        class="attention-order-pill"
        @click="$emit('openOrder', order)"
      >
        <b>#{{ order.order_number }}</b>
        <span>{{ getAttentionReasons(order).map(r => r.text).join(' · ') }}</span>
      </button>
    </transition-group>
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
