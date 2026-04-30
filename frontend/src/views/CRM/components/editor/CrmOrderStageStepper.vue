<template>
  <div class="crm-top-stages">
    <button
      v-for="(stage, idx) in stages"
      :key="stage.key"
      class="stage-pill"
      :class="{ active: currentStage === stage.key, past: isPassedStage(idx) }"
      @click="$emit('set-stage', stage.key)"
    >
      <span class="stage-pill-num">{{ idx + 1 }}</span>
      {{ stage.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  stages: { type: Array, default: () => [] },
  currentStage: { type: String, default: 'new' },
  isPassedStage: { type: Function, required: true }
})

defineEmits(['set-stage'])
</script>
