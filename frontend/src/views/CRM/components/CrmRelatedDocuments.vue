<template>
  <RelatedDocumentsBlock
    v-if="orderId"
    ref="inner"
    source-type="crm_lead"
    :source-id="orderId"
  />
</template>

<script setup>
import { ref } from 'vue'
import RelatedDocumentsBlock from '@/components/RelatedDocumentsBlock.vue'

defineProps({
  orderId: { type: [String, Number, null], default: null },
})

const inner = ref(null)

defineExpose({
  refresh: () => inner.value?.refresh?.(),
})
</script>
