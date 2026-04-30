<template>
  <div class="crm-section crm-client-section">
    <div class="client-block-head">
      <div class="client-title-block">
        <span class="client-kicker">Дані клієнта</span>
        <h3>Клієнт і перший контакт</h3>
        <p>Вся інформація, яка потрібна менеджеру для швидкої розмови та подальшої роботи із заявкою.</p>
      </div>
      <button class="client-add-btn" type="button" @click="$emit('new-client')">
        <el-icon><Plus /></el-icon>
        <span>Новий клієнт</span>
      </button>
    </div>

    <div class="client-picker-row">
      <div class="client-picker-icon">
        <el-icon><User /></el-icon>
      </div>
      <div class="client-picker-field">
        <label class="crm-label">Клієнт із бази</label>
        <el-select
          v-model="form.counterparty_id"
          filterable
          clearable
          placeholder="Оберіть клієнта або залиште ручне введення"
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
      </div>
    </div>

    <div class="client-contact-grid">
      <div class="crm-field client-main-field">
        <label class="crm-label">Ім'я та прізвище</label>
        <el-input
          v-model="clientNameModel"
          placeholder="Наприклад: Олена Ковальчук"
          :class="{ 'field-error': vErrors.client }"
        />
      </div>
      <div class="crm-field client-main-field">
        <label class="crm-label">Телефон</label>
        <el-input v-model="clientPhoneModel" placeholder="+380 96 123 45 67" />
      </div>
    </div>

    <div class="client-contact-grid compact">
      <div class="crm-field">
        <label class="crm-label">Місто</label>
        <el-input v-model="form.city" placeholder="Київ" />
      </div>
      <div class="crm-field">
        <label class="crm-label">Доставка</label>
        <el-select v-model="form.delivery_method_id" placeholder="Оберіть спосіб доставки" clearable style="width:100%">
          <el-option
            v-for="dm in deliveryMethods"
            :key="dm.id"
            :label="dm.name"
            :value="dm.id"
          />
        </el-select>
      </div>
    </div>

    <div class="client-meta-grid">
      <div class="crm-field client-channel-field">
        <label class="crm-label">Канал звернення</label>
        <div class="channel-pills client-channel-pills">
          <button
            v-for="ch in leadSources"
            :key="ch.id"
            type="button"
            class="channel-pill client-channel-pill"
            :class="{ active: form.lead_source_id === ch.id }"
            :style="getLeadSourceStyle(ch)"
            @click="form.lead_source_id = form.lead_source_id === ch.id ? null : ch.id"
          >{{ ch.name }}</button>
        </div>
      </div>

      <CrmManagerBlock
        class="client-manager-card"
        :form="form"
        :manager-options="managerOptions"
        :can-reassign-manager="canReassignManager"
      />
    </div>

    <div v-if="form.delivery_type === 'nova_poshta'" class="crm-field nova-poshta-field">
      <label class="crm-label">Відділення Нової Пошти</label>
      <el-input v-model="form.np_branch" placeholder="Наприклад: відділення №12" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, User } from '@element-plus/icons-vue'
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
  background: props.form.lead_source_id === ch.id ? (ch.color || '#6366f1') : '#fff',
  color: props.form.lead_source_id === ch.id ? '#fff' : '#475569',
})
</script>

<style scoped>
.crm-client-section {
  padding: 18px;
  overflow: hidden;
}

.client-block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #E6ECF3;
}

.client-title-block {
  min-width: 0;
}

.client-kicker {
  display: inline-flex;
  margin-bottom: 4px;
  color: #1463FF;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.client-title-block h3 {
  margin: 0;
  color: #0F172A;
  font-size: 18px;
  font-weight: 850;
  line-height: 1.2;
}

.client-title-block p {
  margin: 5px 0 0;
  max-width: 680px;
  color: #64748B;
  font-size: 12px;
  line-height: 1.45;
}

.client-add-btn {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 13px;
  border: 1px solid #D7E3F4;
  border-radius: 12px;
  background: #FFFFFF;
  color: #1463FF;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.client-add-btn:hover {
  background: #F5F8FC;
  border-color: #BFD4F4;
  box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08);
}

.client-picker-row {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  align-items: end;
  margin-bottom: 14px;
  padding: 12px;
  border: 1px solid #E6ECF3;
  border-radius: 16px;
  background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
}

.client-picker-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: #EFF6FF;
  color: #1463FF;
}

.client-picker-field {
  min-width: 0;
}

.client-contact-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.82fr);
  gap: 12px;
}

.client-contact-grid.compact {
  grid-template-columns: minmax(0, 1fr) minmax(280px, 1fr);
}

.client-main-field :deep(.el-input__wrapper),
.client-picker-field :deep(.el-select__wrapper),
.client-contact-grid :deep(.el-input__wrapper),
.client-contact-grid :deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #DCE6F2 inset;
}

.client-main-field :deep(.el-input__inner),
.client-contact-grid :deep(.el-input__inner) {
  color: #0F172A;
  font-size: 14px;
}

.client-meta-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.78fr);
  gap: 12px;
  align-items: stretch;
  margin-top: 2px;
}

.client-channel-field,
.client-manager-card {
  min-height: 86px;
  margin-bottom: 0;
  padding: 12px;
  border: 1px solid #E6ECF3;
  border-radius: 16px;
  background: #FFFFFF;
}

.client-channel-pills {
  gap: 8px;
  margin-top: 6px;
}

.client-channel-pill {
  min-height: 30px;
  padding: 5px 12px;
  border-radius: 999px;
  font-weight: 700;
}

.client-manager-card :deep(.manager-field) {
  margin-top: 0;
}

.nova-poshta-field {
  margin-top: 12px;
}

@media (max-width: 1180px) {
  .client-contact-grid,
  .client-contact-grid.compact,
  .client-meta-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .client-block-head {
    flex-direction: column;
  }

  .client-add-btn {
    width: 100%;
  }
}
</style>
