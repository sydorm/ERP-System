<template>
  <el-dialog v-model="visible" title="Результат дзвінка" width="420px" append-to-body @close="$emit('close')">
    <div class="call-dialog-body" v-if="task">
      <div class="call-client-info">
        <div class="call-info-left">
          <span class="call-client-name">{{ task.client_name }}</span>
          <span class="call-client-phone">{{ task.client_phone }}</span>
        </div>
        <div class="call-info-right">
          <span class="call-order-num">{{ task.order_number }}</span>
        </div>
      </div>

      <div class="crm-field">
        <label class="crm-label">Вид комунікації</label>
        <el-select v-model="form.communication_type" style="width:100%">
          <el-option
            v-for="ct in dictionaryStore.communicationTypes"
            :key="ct.code"
            :label="`${ct.icon} ${ct.name}`"
            :value="ct.code"
          />
        </el-select>
      </div>

      <div class="crm-field">
        <label class="crm-label">Результат</label>
        <div class="call-result-grid">
          <button
            v-for="cr in dictionaryStore.contactResults"
            :key="cr.code"
            class="cr-grid-btn"
            :class="{ active: form.result === cr.code }"
            :style="form.result === cr.code ? { borderColor: cr.color, background: cr.color + '15', color: cr.color } : {}"
            @click="form.result = cr.code"
          >
            <span v-if="cr.icon" style="margin-bottom:4px; font-size:1.5em">{{ cr.icon }}</span>
            {{ cr.name }}
          </button>
        </div>
      </div>

      <div class="crm-field" v-if="['THINKING', 'NO_ANSWER'].includes(form.result)">
        <label class="crm-label">Коли передзвонити?</label>
        <el-date-picker
          v-model="form.next_contact_at"
          type="datetime"
          format="DD.MM.YYYY HH:mm"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width:100%"
        />
      </div>

      <div class="crm-field">
        <label class="crm-label">{{ form.result === 'REFUSED' ? 'Причина відмови' : 'Коментар' }}</label>
        <el-input 
          v-model="form.note" 
          type="textarea" 
          :rows="2" 
          :placeholder="form.result === 'REFUSED' ? 'Чому відмовився...' : 'Нотатка менеджера...'" 
        />
      </div>
    </div>
    <template #footer>
      <el-button @click="visible = false">Скасувати</el-button>
      <el-button type="primary" :loading="loading" @click="submit">Записати результат</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean,
  task: Object
})
const emit = defineEmits(['update:modelValue', 'success', 'close'])

const visible = ref(props.modelValue)
const loading = ref(false)

const form = reactive({
  result: null,
  communication_type: 'CALL',
  note: '',
  next_contact_at: null,
})

const dictionaryStore = reactive({
  communicationTypes: [],
  contactResults: []
})

watch(() => props.modelValue, (val) => visible.value = val)
watch(visible, (val) => emit('update:modelValue', val))

watch(() => props.task, (newTask) => {
  if (newTask) {
    Object.assign(form, {
      result: null,
      communication_type: 'CALL',
      note: '',
      next_contact_at: null,
    })
  }
})

const fetchDictionaries = async () => {
  try {
    const [ct, cr] = await Promise.all([
      api.get('/api/v1/dictionaries/COMMUNICATION_TYPE'),
      api.get('/api/v1/dictionaries/CONTACT_RESULT')
    ])
    dictionaryStore.communicationTypes = ct.data
    dictionaryStore.contactResults = cr.data.length ? cr.data : [
      { code: 'NO_ANSWER', name: 'Не відповів', icon: '📵', color: '#f97316' },
      { code: 'THINKING',  name: 'Думає',      icon: '🤔', color: '#eab308' },
      { code: 'REFUSED',   name: 'Відмовився',  icon: '❌', color: '#ef4444' },
      { code: 'CONFIRMED', name: 'Підтвердив замовлення', icon: '✅', color: '#22c55e' },
    ]
  } catch (e) {
    console.error('Failed to load dictionaries in CallResultDialog', e)
  }
}

onMounted(fetchDictionaries)

const submit = async () => {
  if (!form.result) return
  loading.value = true
  try {
    const orderId = props.task.order_id
    await api.post(`/api/v1/crm/orders/${orderId}/contacts`, {
      result: form.result,
      communication_type: form.communication_type,
      note: form.note || null,
      next_contact_at: form.next_contact_at || null,
    })
    
    // Complete task
    await api.put(`/api/v1/crm/tasks/${props.task.id}/complete`)
    
    ElMessage.success('Результат записано')
    visible.value = false
    emit('success', { result: form.result, orderId })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Помилка')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.call-client-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 20px;
}
.call-info-left {
  display: flex;
  flex-direction: column;
}
.call-client-name {
  font-weight: 600;
  font-size: 16px;
}
.call-client-phone {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
.call-order-num {
  font-weight: 600;
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
}
.crm-field {
  margin-bottom: 20px;
}
.crm-label {
  display: block;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.call-result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.cr-grid-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}
.cr-grid-btn:hover {
  background: var(--el-fill-color-light);
}
.cr-grid-btn.active {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
