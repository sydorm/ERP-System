<template>
  <RelatedDocumentsBlock
    v-if="orderId"
    ref="relatedDocsRef"
    source-type="crm_lead"
    :source-id="orderId"
  />
</template>

<script setup>
import { ref } from 'vue'
import RelatedDocumentsBlock from '@/components/RelatedDocumentsBlock.vue'

defineProps({
  orderId: { type: [String, Number], default: null }
})

const relatedDocsRef = ref(null)

defineExpose({
  refresh: () => relatedDocsRef.value?.refresh()
})
</script>
