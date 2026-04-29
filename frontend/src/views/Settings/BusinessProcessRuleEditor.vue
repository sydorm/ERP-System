<template>
  <el-dialog
    v-model="visible"
    :title="isNew ? 'Нове правило' : 'Редагувати правило'"
    width="580px"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <!-- ОСНОВНЕ -->
      <div class="section-title">Основне</div>
      <el-form-item label="Назва правила" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="Опис">
        <el-input v-model="form.description" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.is_active">Активне</el-checkbox>
      </el-form-item>

      <!-- УМОВА -->
      <div class="section-title">Умова запуску</div>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Об'єкт" prop="source_type">
            <el-select v-model="form.source_type" style="width:100%">
              <el-option label="CRM-заявка" value="crm_lead" />
              <el-option label="Замовлення покупця" value="customer_order" />
              <el-option label="Виробниче завдання" value="production_task" />
              <el-option label="Видаткова накладна" value="sales_invoice" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Подія" prop="event_type">
            <el-select v-model="form.event_type" style="width:100%">
              <el-option label="Зміна статусу" value="status_changed" />
              <el-option label="Створення" value="created" />
              <el-option label="Оновлення" value="updated" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="З якого статусу">
            <el-input v-model="form.from_status" placeholder="new, in_progress, ..." />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="У який статус" prop="to_status">
            <el-input v-model="form.to_status" placeholder="processing, completed, ..." />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- ДІЯ -->
      <div class="section-title">Дія</div>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Тип дії" prop="action_type">
            <el-select v-model="form.action_type" style="width:100%">
              <el-option label="Створити Замовлення покупця" value="create_customer_order" />
              <el-option label="Створити Видаткову накладну" value="create_sales_invoice" />
              <el-option label="Створити Рахунок на оплату" value="create_invoice" />
              <el-option label="Створити Виробниче завдання" value="create_production_task" />
              <el-option label="Зарезервувати матеріали" value="reserve_materials" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Режим виконання" prop="mode">
            <el-select v-model="form.mode" style="width:100%">
              <el-option label="Автоматично" value="automatic" />
              <el-option label="Запитувати підтвердження" value="ask_confirmation" />
              <el-option label="Вимкнено" value="disabled" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- ЗАХИСТ -->
      <div class="section-title">Захист</div>
      <el-form-item>
        <el-checkbox v-model="form.prevent_duplicates">Не створювати дублікат</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.log_execution">Логувати виконання</el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">Скасувати</el-button>
      <el-button type="primary" @click="save" :loading="saving">Зберегти</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean,
  rule: Object,
})
const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
const isNew = computed(() => !props.rule?.id)

const formRef = ref()
const saving = ref(false)
const form = ref({
  name: '',
  description: '',
  is_active: true,
  source_type: 'crm_lead',
  event_type: 'status_changed',
  from_status: '',
  to_status: 'processing',
  action_type: 'create_customer_order',
  mode: 'ask_confirmation',
  prevent_duplicates: true,
  log_execution: true,
})

watch(() => props.rule, (r) => {
  if (r) {
    Object.assign(form.value, r)
  } else {
    form.value = {
      name: '', description: '', is_active: true,
      source_type: 'crm_lead', event_type: 'status_changed',
      from_status: '', to_status: 'processing',
      action_type: 'create_customer_order', mode: 'ask_confirmation',
      prevent_duplicates: true, log_execution: true,
    }
  }
}, { immediate: true })

const rules = {
  name: [{ required: true, message: "Введіть назву", trigger: 'blur' }],
  source_type: [{ required: true, trigger: 'change' }],
  event_type: [{ required: true, trigger: 'change' }],
  to_status: [{ required: true, message: "Введіть статус", trigger: 'blur' }],
  action_type: [{ required: true, trigger: 'change' }],
  mode: [{ required: true, trigger: 'change' }],
}

const save = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = { ...form.value, from_status: form.value.from_status || null }
      if (isNew.value) {
        await api.post('/api/v1/business-process/rules', payload)
        ElMessage.success('Правило створено')
      } else {
        await api.put(`/api/v1/business-process/rules/${props.rule.id}`, payload)
        ElMessage.success('Правило оновлено')
      }
      emit('saved')
      visible.value = false
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || 'Помилка збереження')
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped>
.section-title {
  font-size: 11px;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 16px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #F1F5F9;
}
.section-title:first-of-type { margin-top: 0; }
</style>
