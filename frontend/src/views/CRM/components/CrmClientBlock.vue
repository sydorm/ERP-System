<template>
  <div class="crm-section crm-client-section">
    <div class="client-block-head">
      <div class="client-title-block">
        <span class="client-kicker">Крок 1 · Клієнт</span>
        <h3>Дані замовника</h3>
        <p>Виберіть існуючого клієнта або введіть дані нового для швидкого старту.</p>
      </div>
      <button class="client-add-btn" type="button" @click="$emit('new-client')">
        <el-icon><Plus /></el-icon>
        <span>Новий клієнт</span>
      </button>
    </div>

    <div class="client-form-container">
      <div class="client-picker-wrapper">
        <label class="crm-label">Пошук у базі</label>
        <el-select
          v-model="form.counterparty_id"
          filterable
          clearable
          placeholder="Прізвище, ім'я або телефон..."
          class="cp-select-modern"
          :class="{ 'field-error': vErrors.client }"
          @change="$emit('counterparty-change', $event)"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <el-option
            v-for="cp in counterparties"
            :key="cp.id"
            :label="cp.name"
            :value="cp.id"
          >
            <div class="cp-option">
              <span>{{ cp.name }}</span>
              <small v-if="cp.phone">{{ cp.phone }}</small>
            </div>
          </el-option>
        </el-select>
      </div>

      <div class="client-main-grid">
        <div class="crm-field">
          <label class="crm-label">Ім'я клієнта</label>
          <el-input
            v-model="clientNameModel"
            placeholder="Олена Ковальчук"
            :class="{ 'field-error': vErrors.client }"
          >
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </div>
        <div class="crm-field">
          <label class="crm-label">Контактний телефон</label>
          <el-input v-model="clientPhoneModel" placeholder="+380..." >
            <template #prefix><el-icon><Phone /></el-icon></template>
          </el-input>
        </div>
      </div>

      <div class="client-extra-grid">
        <div class="crm-field">
          <label class="crm-label">Джерело</label>
          <div class="channel-pills-modern">
            <button
              v-for="ch in leadSources"
              :key="ch.id"
              type="button"
              class="channel-pill-modern"
              :class="{ active: form.lead_source_id === ch.id }"
              @click="form.lead_source_id = form.lead_source_id === ch.id ? null : ch.id"
            >
              <span class="ch-dot" :style="{ background: ch.color || '#94a3b8' }"></span>
              {{ ch.name }}
            </button>
          </div>
        </div>

        <div class="crm-field">
          <label class="crm-label">Менеджер</label>
          <CrmManagerBlock
            :form="form"
            :manager-options="managerOptions"
            :can-reassign-manager="canReassignManager"
          />
        </div>
      </div>

      <div class="client-delivery-grid">
        <div class="crm-field">
          <label class="crm-label">Місто та доставка</label>
          <div class="delivery-combined">
            <el-input v-model="form.city" placeholder="Місто" class="city-input" />
            <el-select v-model="form.delivery_method_id" placeholder="Спосіб" clearable class="delivery-select">
              <el-option
                v-for="dm in deliveryMethods"
                :key="dm.id"
                :label="dm.name"
                :value="dm.id"
              />
            </el-select>
          </div>
        </div>
        <div v-if="form.delivery_type === 'nova_poshta'" class="crm-field">
          <label class="crm-label">Відділення НП</label>
          <el-input v-model="form.np_branch" placeholder="№ відділення" />
        </div>
      </div>
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
  padding: 24px;
}

.client-block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F1F5F9;
}

.client-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: #6366F1;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.client-title-block h3 {
  margin: 0;
  color: #0F172A;
  font-size: 20px;
  font-weight: 800;
}

.client-title-block p {
  margin: 6px 0 0;
  color: #64748B;
  font-size: 13px;
  line-height: 1.5;
}

.client-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  background: #fff;
  color: #0F172A;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.client-add-btn:hover {
  background: #F8FAF7;
  border-color: #6366F1;
  color: #6366F1;
}

.client-form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.client-picker-wrapper {
  background: #F8FAFC;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #F1F5F9;
}

.cp-select-modern {
  width: 100%;
}

.cp-option {
  display: flex;
  flex-direction: column;
  padding: 4px 0;
}

.cp-option small {
  color: #94A3B8;
  font-size: 11px;
}

.client-main-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.client-extra-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.channel-pills-modern {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.channel-pill-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid #E2E8F0;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.channel-pill-modern.active {
  border-color: #6366F1;
  background: #EEF2FF;
  color: #6366F1;
}

.ch-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.client-delivery-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.delivery-combined {
  display: flex;
  gap: 8px;
}

.city-input { flex: 1.5; }
.delivery-select { flex: 1; }

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 0 12px;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #6366F1 inset !important;
}

@media (max-width: 1024px) {
  .client-main-grid, .client-extra-grid, .client-delivery-grid {
    grid-template-columns: 1fr;
  }
}
</style>
