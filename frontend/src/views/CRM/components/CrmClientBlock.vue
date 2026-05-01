<template>
  <div class="crm-section crm-client-section-premium">
    <div class="product-block-header">
      <div class="header-main">
        <div class="step-badge step-1">Крок 1</div>
        <div class="title-group">
          <h3>Дані замовника</h3>
          <p>Виберіть існуючого клієнта або введіть дані нового для швидкого старту.</p>
        </div>
      </div>
      <div class="header-actions">
        <div v-if="form.counterparty_id" class="glass-pill success mr-2">
          <el-icon><Check /></el-icon>
          <span>Клієнта обрано</span>
        </div>
        <button class="client-add-btn-premium" type="button" @click="$emit('new-client')">
          <el-icon><Plus /></el-icon>
          <span>Новий клієнт</span>
        </button>
      </div>
    </div>

    <div class="premium-form-zone">
      <div class="selection-card client-search-card">
        <label class="premium-label">
          <el-icon><Search /></el-icon>
          Пошук у базі
        </label>
        <el-select
          v-model="form.counterparty_id"
          filterable
          clearable
          placeholder="Прізвище, ім'я або телефон..."
          class="premium-select"
          :class="{ 'field-error': vErrors.client }"
          @change="$emit('counterparty-change', $event)"
        >
          <template #prefix>
            <el-icon class="select-icon-modern"><Search /></el-icon>
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

      <div class="client-info-grid">
        <div class="info-card">
          <label class="premium-label">
            <el-icon><User /></el-icon>
            Ім'я клієнта
          </label>
          <el-input
            v-model="clientNameModel"
            placeholder="Олена Ковальчук"
            class="premium-input"
            :class="{ 'field-error': vErrors.client }"
          />
        </div>

        <div class="info-card">
          <label class="premium-label">
            <el-icon><Phone /></el-icon>
            Контактний телефон
          </label>
          <el-input 
            v-model="clientPhoneModel" 
            placeholder="+380..." 
            class="premium-input"
          />
        </div>
      </div>

      <div class="client-details-row">
        <div class="details-card sources-block">
          <label class="premium-label">
            <el-icon><MagicStick /></el-icon>
            Джерело звернення
          </label>
          <div class="channel-pills-premium">
            <button
              v-for="ch in leadSources"
              :key="ch.id"
              type="button"
              class="pill-choice"
              :class="{ active: form.lead_source_id === ch.id }"
              @click="form.lead_source_id = form.lead_source_id === ch.id ? null : ch.id"
            >
              <span class="color-indicator" :style="{ background: ch.color || '#94a3b8' }"></span>
              {{ ch.name }}
            </button>
          </div>
        </div>

        <div class="details-card manager-block">
          <label class="premium-label">
            <el-icon><Avatar /></el-icon>
            Менеджер
          </label>
          <CrmManagerBlock
            :form="form"
            :manager-options="managerOptions"
            :can-reassign-manager="canReassignManager"
          />
        </div>
      </div>

      <div class="delivery-zone">
        <div class="details-card full-width">
          <label class="premium-label">
            <el-icon><Location /></el-icon>
            Місто та доставка
          </label>
          <div class="delivery-combined-premium">
            <el-input v-model="form.city" placeholder="Місто" class="premium-input city-input" />
            <el-select v-model="form.delivery_method_id" placeholder="Спосіб доставки" clearable class="premium-select delivery-select">
              <el-option
                v-for="dm in deliveryMethods"
                :key="dm.id"
                :label="dm.name"
                :value="dm.id"
              />
            </el-select>
            <el-input 
              v-if="form.delivery_type === 'nova_poshta' || form.delivery_method_id" 
              v-model="form.np_branch" 
              placeholder="№ відділення / адреса" 
              class="premium-input branch-input"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, User, Search, Phone, MagicStick, Avatar, Location } from '@element-plus/icons-vue'
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
</script>

<style scoped>
.crm-client-section-premium {
  padding: 32px;
  background: #fff;
  border-radius: 24px;
}

.step-badge.step-1 {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
}

.glass-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
}

.glass-pill.success {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.mr-2 { margin-right: 8px; }

.product-block-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-main {
  display: flex;
  gap: 16px;
  align-items: center;
}

.step-badge {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  color: #fff;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.title-group h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 850;
  color: #0F172A;
  letter-spacing: -0.02em;
}

.title-group p {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.client-add-btn-premium {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  background: #fff;
  color: #0F172A;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.client-add-btn-premium:hover {
  background: #F8FAFC;
  border-color: #6366F1;
  color: #6366F1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.premium-form-zone {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.selection-card {
  background: #F8FAFC;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid #F1F5F9;
  transition: all 0.3s ease;
}

.selection-card:hover {
  background: #fff;
  border-color: #6366F1;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
}

.premium-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 12px;
}

.premium-label .el-icon {
  color: #6366F1;
  font-size: 16px;
}

.client-info-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}

.info-card {
  display: flex;
  flex-direction: column;
}

.client-details-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}

.details-card {
  display: flex;
  flex-direction: column;
}

.channel-pills-premium {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-choice {
  padding: 8px 16px;
  border-radius: 12px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.pill-choice:hover {
  border-color: #6366F1;
  color: #4F46E5;
}

.pill-choice.active {
  background: #6366F1;
  color: #fff;
  border-color: #6366F1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.color-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.delivery-combined-premium {
  display: flex;
  gap: 12px;
}

.delivery-combined-premium .city-input { flex: 1.5; }
.delivery-combined-premium .delivery-select { flex: 1; }
.delivery-combined-premium .branch-input { flex: 1.2; }

.cp-option {
  display: flex;
  flex-direction: column;
  padding: 4px 0;
}

.cp-option small {
  color: #94A3B8;
  font-size: 11px;
}

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  border-radius: 14px !important;
  box-shadow: 0 0 0 1px #E2E8F0 inset !important;
  padding: 8px 14px !important;
  height: 42px !important;
  transition: all 0.2s;
}

:deep(.el-input__wrapper.is-focus), :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #6366F1 inset !important;
  background: #F5F7FF !important;
}

.field-error :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #EF4444 inset !important;
}

@media (max-width: 1024px) {
  .client-info-grid, .client-details-row, .delivery-combined-premium {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
