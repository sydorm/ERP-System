<template>
  <el-dialog
    v-model="visible"
    title="Історія змін"
    width="800px"
    class="audit-log-dialog"
    destroy-on-close
  >
    <div v-loading="loading" class="audit-log-container">
      <el-empty v-if="!loading && logs.length === 0" description="Історія порожня" />
      
      <el-timeline v-else>
        <el-timeline-item
          v-for="log in logs"
          :key="log.id"
          :timestamp="formatDateTime(log.created_at)"
          :type="getActionColor(log.action)"
          placement="top"
        >
          <el-card class="log-card" shadow="hover">
            <div class="log-header">
              <span class="log-action">
                <el-tag size="small" :type="getActionColor(log.action)">{{ log.action }}</el-tag>
              </span>
              <span class="log-user" v-if="log.user_name">
                <el-icon><User /></el-icon> {{ log.user_name }}
              </span>
            </div>
            
            <div class="log-changes" v-if="log.action === 'UPDATE' && Object.keys(log.changes).length > 0">
              <table class="changes-table">
                <thead>
                  <tr>
                    <th>Поле</th>
                    <th>Було</th>
                    <th>Стало</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(change, field) in log.changes" :key="field">
                    <td class="field-name">{{ formatFieldName(field) }}</td>
                    <td class="old-value">{{ formatValue(change.old, field === 'counterparty_id') }}</td>
                    <td class="new-value">{{ formatValue(change.new, field === 'counterparty_id') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else-if="log.action === 'CREATE'" class="log-text">
              Документ створено
            </div>
            <div v-else-if="log.action === 'DELETE'" class="log-text">
              Документ видалено
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { User } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import axios from 'axios'
import api from '@/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  entityType: { type: String, required: true },
  entityId: { type: String, required: true }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const loading = ref(false)
const logs = ref([])
const counterpartiesCache = ref({})

const resolveCounterpartyName = async (id) => {
  if (!id || id === 'None') return id
  if (counterpartiesCache.value[id]) return counterpartiesCache.value[id]
  
  try {
    const res = await api.get(`/counterparties/${id}`)
    counterpartiesCache.value[id] = res.data.name
    return res.data.name
  } catch (e) {
    return id
  }
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.entityId) {
    fetchLogs()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await api.get(`/api/v1/audit-logs/${props.entityType}/${props.entityId}`)
    
    // Pre-fetch counterparty names if any changes involve counterparty_id
    const fetchedLogs = response.data
    for (const log of fetchedLogs) {
      if (log.changes?.counterparty_id) {
        if (log.changes.counterparty_id.old) await resolveCounterpartyName(log.changes.counterparty_id.old)
        if (log.changes.counterparty_id.new) await resolveCounterpartyName(log.changes.counterparty_id.new)
      }
    }
    
    logs.value = fetchedLogs
  } catch (error) {
    console.error('Error fetching audit logs:', error)
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('DD.MM.YYYY HH:mm:ss')
}

const getActionColor = (action) => {
  switch (action) {
    case 'CREATE': return 'success'
    case 'UPDATE': return 'warning'
    case 'DELETE': return 'danger'
    case 'POST': return 'primary'
    case 'UNPOST': return 'info'
    default: return ''
  }
}

const fieldNamesDict = {
  'status': 'Статус',
  'total_amount': 'Загальна сума',
  'order_date': 'Дата документа',
  'shipping_date': 'Дата відвантаження',
  'order_number': 'Номер',
  'counterparty_id': 'Контрагент',
  'warehouse_id': 'Склад',
  'comment': 'Коментар',
  'contract': 'Договір',
  'discount_percent': 'Відсоток знижки',
  'company_id': 'Компанія',
  'created_by': 'Автор',
  'lines': 'Список товарів'
}

const formatFieldName = (field) => {
  return fieldNamesDict[field] || field
}

const formatValue = (val, isCounterpartyField = false) => {
  if (val === null || val === undefined || val === 'None') return '—'
  
  if (Array.isArray(val)) {
    if (val.length === 0) return '[]'
    // Format each item in the array for order lines or general objects
    return val.map((item, index) => {
      // Create a nice string representation for known fields
      const parts = []
      if (item.product_id) parts.push(`Товар`)
      if (item.quantity !== undefined) parts.push(`к-сть: ${item.quantity}`)
      if (item.price !== undefined) parts.push(`ціна: ${item.price}`)
      if (item.total !== undefined) parts.push(`сума: ${item.total}`)
      
      if (parts.length > 0) return `${index + 1}. ${parts.join(', ')}`
      
      // Fallback for simple values or unknown objects
      return `${index + 1}. ${typeof item === 'object' ? JSON.stringify(item).substring(0, 50) + '...' : String(item)}`
    }).join('\n')
  }
  
  if (typeof val === 'object') {
     return JSON.stringify(val)
  }

  // Try to parse floats to keep it clean if it's a number
  if (!isNaN(val) && val !== '') {
    const num = parseFloat(val)
    if (!Number.isInteger(num)) {
       return num.toFixed(2)
    }
  }
  
  if (isCounterpartyField) {
    return counterpartiesCache.value[val] || val
  }
  
  return val
}
</script>

<style scoped>
.audit-log-container {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px 20px;
}
.log-card {
  margin-bottom: 8px;
}
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.log-user {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}
.log-text {
  font-size: 13px;
  color: #606266;
}
.changes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.changes-table th, .changes-table td {
  border: 1px solid #ebeef5;
  padding: 6px 12px;
  text-align: left;
}
.changes-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
.field-name {
  font-weight: 500;
  color: #303133;
  width: 30%;
}
.old-value {
  color: #f56c6c;
  text-decoration: line-through;
  width: 35%;
  white-space: pre-wrap;
}
.new-value {
  color: #67c23a;
  font-weight: 500;
  width: 35%;
  white-space: pre-wrap;
}
</style>
