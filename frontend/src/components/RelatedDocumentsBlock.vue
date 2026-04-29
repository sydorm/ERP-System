<template>
  <div class="related-docs-block" v-if="docs.length || loading">
    <div class="related-docs-header">
      <el-icon class="header-icon"><Connection /></el-icon>
      <span>Пов'язані документи</span>
    </div>
    <div v-if="loading" class="related-docs-loading">
      <el-skeleton :rows="2" animated />
    </div>
    <div v-else class="related-docs-list">
      <template v-for="type in displayTypes" :key="type.key">
        <div class="related-doc-row">
          <span class="doc-type-label">{{ type.label }}:</span>
          <template v-if="getDoc(type.key)">
            <router-link :to="getDoc(type.key).url" class="doc-link">
              {{ getDoc(type.key).number || getDoc(type.key).doc_id }}
            </router-link>
          </template>
          <span v-else class="doc-empty">— не створено</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Connection } from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  sourceType: { type: String, required: true },
  sourceId: { type: String, default: null },
})

const docs = ref([])
const loading = ref(false)

// Which related document types to display based on source type
const DISPLAY_TYPES = {
  crm_lead: [
    { key: 'customer_order', label: 'Замовлення покупця' },
    { key: 'production_task', label: 'Виробниче завдання' },
    { key: 'sales_invoice', label: 'Видаткова накладна' },
  ],
  customer_order: [
    { key: 'crm_lead', label: 'CRM-заявка' },
    { key: 'production_task', label: 'Виробниче завдання' },
    { key: 'sales_invoice', label: 'Видаткова накладна' },
  ],
  production_task: [
    { key: 'crm_lead', label: 'CRM-заявка' },
    { key: 'customer_order', label: 'Замовлення покупця' },
    { key: 'sales_invoice', label: 'Видаткова накладна' },
  ],
}

const displayTypes = DISPLAY_TYPES[props.sourceType] || []

const getDoc = (type) =>
  docs.value.find(d => d.doc_type === type)

const fetchDocs = async () => {
  if (!props.sourceId) return
  loading.value = true
  try {
    const res = await api.get('/api/v1/business-process/related-documents', {
      params: { source_type: props.sourceType, source_id: props.sourceId },
    })
    docs.value = res.data
  } catch { /* non-critical */ }
  finally { loading.value = false }
}

onMounted(fetchDocs)
watch(() => props.sourceId, fetchDocs)

defineExpose({ refresh: fetchDocs })
</script>

<style scoped>
.related-docs-block {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 14px 16px;
}
.related-docs-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}
.header-icon { color: #94A3B8; }
.related-doc-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 5px 0;
  border-bottom: 1px solid #F1F5F9;
}
.related-doc-row:last-child { border-bottom: none; }
.doc-type-label {
  color: #94A3B8;
  min-width: 155px;
  flex-shrink: 0;
}
.doc-link {
  color: #3B82F6;
  font-weight: 600;
  text-decoration: none;
}
.doc-link:hover { text-decoration: underline; }
.doc-empty { color: #CBD5E1; font-style: italic; }
.related-docs-loading { padding: 4px 0; }
</style>
