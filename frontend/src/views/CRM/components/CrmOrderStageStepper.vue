<template>
  <div class="crm-top-stages">
    <button
      v-for="(stage, idx) in stages"
      :key="stage.key"
      class="stage-pill"
      :class="{ active: activeStage === stage.key, past: isPassedStage(idx) }"
      @click="$emit('set-stage', stage.key)"
    >
      <span class="stage-pill-num">{{ idx + 1 }}</span>
      {{ stage.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  stages: { type: Array, required: true },
  activeStage: { type: String, required: true },
  isPassedStage: { type: Function, required: true },
})

defineEmits(['set-stage'])
</script>
