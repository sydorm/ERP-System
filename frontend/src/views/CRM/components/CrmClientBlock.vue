<template>
  <div class="crm-section">
    <div class="crm-section-head">
      <span class="crm-section-title">Клієнт</span>
      <el-select
        v-model="form.counterparty_id"
        filterable
        clearable
        placeholder="Оберіть або введіть клієнта"
        class="cp-select"
        :class="{ 'field-error': vErrors.client }"
        @change="$emit('counterparty-change', $event)"
      >
        <el-option
          v-for="cp in counterparties"
          :key="cp.id"
          :label="cp.name"
          :value="cp.id"
        />
      </el-select>
      <button class="crm-link-btn" @click="$emit('new-client')">
        <el-icon><Plus /></el-icon> Новий клієнт
      </button>
    </div>

    <div class="crm-grid-2">
      <div class="crm-field">
        <label class="crm-label">Ім'я та прізвище</label>
        <el-input v-model="clientNameModel" placeholder="Олена Ковальчук" :class="{ 'field-error': vErrors.client }" />
      </div>
      <div class="crm-field">
        <label class="crm-label">Телефон</label>
        <el-input v-model="clientPhoneModel" placeholder="+380 96 123 45 67" />
      </div>
    </div>

    <div class="crm-field">
      <label class="crm-label">Канал звернення</label>
      <div class="channel-pills">
        <button
          v-for="ch in leadSources"
          :key="ch.id"
          class="channel-pill"
          :class="{ active: form.lead_source_id === ch.id }"
          :style="getLeadSourceStyle(ch)"
          @click="form.lead_source_id = form.lead_source_id === ch.id ? null : ch.id"
        >{{ ch.name }}</button>
      </div>
    </div>

    <div class="crm-grid-2">
      <div class="crm-field">
        <label class="crm-label">Місто</label>
        <el-input v-model="form.city" placeholder="Київ" />
      </div>
      <div class="crm-field">
        <label class="crm-label">Доставка</label>
        <el-select v-model="form.delivery_method_id" placeholder="Оберіть" clearable style="width:100%">
          <el-option
            v-for="dm in deliveryMethods"
            :key="dm.id"
            :label="dm.name"
            :value="dm.id"
          />
        </el-select>
      </div>
    </div>

    <CrmManagerBlock
      :form="form"
      :manager-options="managerOptions"
      :can-reassign-manager="canReassignManager"
    />

    <div v-if="form.delivery_type === 'nova_poshta'" class="crm-field">
      <label class="crm-label">Відділення Нової Пошти</label>
      <el-input v-model="form.np_branch" placeholder="Наприклад: відділення №12" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import CrmManagerBlock from './CrmManagerBlock.vue'

const props = defineProps({
  form: { type: Object, required: true },
  vErrors: { type: Object, required: true },
  counterparties: { type: Array, required: true },
  leadSources: { type: Array, required: true },
  deliveryMethods: { type: Array, required: true },
  managerOptions: { type: Array, required: true },
  canReassignManager: { type: Boolean, default: false },
  clientName: { type: String, default: '' },
  clientPhone: { type: String, default: '' },
})

const emit = defineEmits(['update:clientName', 'update:clientPhone', 'counterparty-change', 'new-client'])

const clientNameModel = computed({
  get: () => props.clientName,
  set: value => emit('update:clientName', value),
})

const clientPhoneModel = computed({
  get: () => props.clientPhone,
  set: value => emit('update:clientPhone', value),
})

const getLeadSourceStyle = (ch) => ({
  '--pill-color': ch.color || '#94a3b8',
  borderColor: props.form.lead_source_id === ch.id ? (ch.color || '#6366f1') : '#e2e8f0',
  background: props.form.lead_source_id === ch.id ? (ch.color || '#6366f1') : 'transparent',
  color: props.form.lead_source_id === ch.id ? '#fff' : '#475569',
})
</script>
