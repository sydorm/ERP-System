<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="460px"
    :close-on-click-modal="false"
    class="automation-confirm-modal"
  >
    <div class="modal-body">
      <div class="modal-icon">
        <el-icon class="icon-automation"><MagicStick /></el-icon>
      </div>
      <p class="modal-description">{{ description }}</p>
      <div class="rule-info-box" v-if="rule">
        <div class="rule-info-row">
          <span class="rule-info-label">Правило:</span>
          <span class="rule-info-value">{{ rule.rule_name }}</span>
        </div>
        <div class="rule-info-row">
          <span class="rule-info-label">Дія:</span>
          <span class="rule-info-value">{{ actionLabel }}</span>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="modal-footer">
        <el-button @click="handleSkip" :loading="loading">Не створювати</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">
          <el-icon><Check /></el-icon> Створити
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MagicStick, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean,
  rule: Object,       // { rule_id, rule_name, action_type, mode }
  sourceType: String,
  sourceId: String,
})
const emit = defineEmits(['update:modelValue', 'confirmed', 'skipped'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
const loading = ref(false)

const ACTION_LABELS = {
  create_customer_order: 'Створити Замовлення покупця',
  create_sales_invoice: 'Створити Видаткову накладну',
  create_invoice: 'Створити Рахунок на оплату',
  create_production_task: 'Створити Виробниче завдання',
  reserve_materials: 'Зарезервувати матеріали',
}

const actionLabel = computed(() =>
  ACTION_LABELS[props.rule?.action_type] || props.rule?.action_type || '—'
)

const title = computed(() => {
  if (props.rule?.action_type === 'create_customer_order') return 'Підтвердити передачу в роботу'
  if (props.rule?.action_type === 'create_sales_invoice') return 'Виробництво завершено'
  return 'Автоматизація'
})

const description = computed(() => {
  if (props.rule?.action_type === 'create_customer_order')
    return 'Заявка перейшла у статус «В роботі». Створити Замовлення покупця на основі цієї заявки?'
  if (props.rule?.action_type === 'create_sales_invoice')
    return 'Виробниче завдання завершено. Створити Видаткову накладну на основі цього завдання?'
  return 'Правило автоматизації пропонує виконати дію. Продовжити?'
})

const handleConfirm = async () => {
  loading.value = true
  try {
    const res = await api.post('/api/v1/business-process/execute', {
      rule_id: props.rule.rule_id,
      source_type: props.sourceType,
      source_id: props.sourceId,
    })
    const data = res.data
    if (data.status === 'success') {
      ElMessage.success(data.message)
      emit('confirmed', data)
    } else if (data.status === 'skipped') {
      ElMessage.info(data.message)
      emit('skipped', data)
    } else {
      ElMessage.warning(data.message || 'Дія виконана з попередженням')
      emit('confirmed', data)
    }
    visible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Помилка виконання')
  } finally {
    loading.value = false
  }
}

const handleSkip = async () => {
  try {
    await api.post('/api/v1/business-process/skip', {
      rule_id: props.rule.rule_id,
      source_type: props.sourceType,
      source_id: props.sourceId,
    })
  } catch { /* non-critical */ }
  emit('skipped', null)
  visible.value = false
}
</script>

<style scoped>
.modal-body {
  text-align: center;
  padding: 8px 0 4px;
}
.modal-icon {
  width: 56px;
  height: 56px;
  background: #EFF6FF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
.icon-automation {
  font-size: 24px;
  color: #3B82F6;
}
.modal-description {
  font-size: 15px;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 16px;
}
.rule-info-box {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 12px 16px;
  text-align: left;
}
.rule-info-row {
  display: flex;
  gap: 8px;
  font-size: 13px;
  margin-bottom: 4px;
}
.rule-info-row:last-child { margin-bottom: 0; }
.rule-info-label { color: #94A3B8; min-width: 60px; }
.rule-info-value { color: #1E293B; font-weight: 500; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
