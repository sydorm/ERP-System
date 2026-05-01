<template>
  <div class="cbc-wrap">

    <!-- ① Search field -->
    <div class="cbc-search-row">
      <el-select
        v-model="form.counterparty_id"
        filterable
        remote
        clearable
        placeholder="Пошук клієнта за іменем або телефоном..."
        class="cbc-search-select w-full"
        @change="$emit('counterparty-change', $event)"
      >
        <template #prefix>
          <el-icon class="cbc-search-icon"><Search /></el-icon>
        </template>
        <el-option
          v-for="cp in counterparties"
          :key="cp.id"
          :label="cp.name"
          :value="cp.id"
        >
          <div class="cbc-option">
            <span class="cbc-option-name">{{ cp.name }}</span>
            <span class="cbc-option-phone">{{ cp.phone }}</span>
          </div>
        </el-option>
      </el-select>
    </div>

    <!-- ② Selected client compact bar -->
    <transition name="cbc-slide">
      <div v-if="selectedCounterparty" class="cbc-client-bar">
        <div class="cbc-avatar">{{ clientInitials }}</div>
        <div class="cbc-client-info">
          <div class="cbc-active-label">Активний контакт</div>
          <div class="cbc-client-name-row">
            <span class="cbc-client-name">{{ selectedCounterparty.name }}</span>
            <span v-if="selectedCounterparty.phone" class="cbc-client-phone">
              <el-icon class="text-[10px]"><Phone /></el-icon>
              {{ selectedCounterparty.phone }}
            </span>
          </div>
        </div>
        <button class="cbc-change-btn" type="button" @click="form.counterparty_id = null">
          Змінити
        </button>
      </div>
    </transition>

    <!-- ③ New client form (only when no client selected) -->
    <div v-if="!selectedCounterparty" class="cbc-grid">
      <div class="cbc-field">
        <label>Прізвище та ім'я</label>
        <el-input v-model="clientNameModel" placeholder="Шевченко Андрій" />
      </div>
      <div class="cbc-field">
        <label>Телефон</label>
        <el-input v-model="clientPhoneModel" placeholder="+38 (0__) ___ __ __" />
      </div>
      <div class="cbc-field">
        <label>Місто</label>
        <el-input v-model="form.city" placeholder="Введіть місто..." />
      </div>
      <div class="cbc-field">
        <label>Джерело залучення</label>
        <el-select v-model="form.lead_source_id" placeholder="Оберіть канал" class="w-full" clearable>
          <el-option v-for="ch in leadSources" :key="ch.id" :label="ch.name" :value="ch.id" />
        </el-select>
      </div>
    </div>

    <!-- ④ Logistics — always shown -->
    <div class="cbc-grid cbc-grid--logistics">
      <div class="cbc-field">
        <label>Спосіб доставки</label>
        <el-select v-model="form.delivery_method_id" placeholder="Оберіть доставку" class="w-full" clearable>
          <el-option v-for="dm in deliveryMethods" :key="dm.id" :label="dm.name" :value="dm.id" />
        </el-select>
      </div>
      <div class="cbc-field">
        <label>Відповідальний менеджер</label>
        <CrmManagerBlock
          :form="form"
          :manager-options="managerOptions"
          :can-reassign-manager="canReassignManager"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Search, Phone, MagicStick, User } from '@element-plus/icons-vue'
import CrmManagerBlock from './CrmManagerBlock.vue'

const props = defineProps({
  form:               { type: Object,  required: true },
  vErrors:            { type: Object,  required: true },
  counterparties:     { type: Array,   required: true },
  leadSources:        { type: Array,   required: true },
  deliveryMethods:    { type: Array,   required: true },
  managerOptions:     { type: Array,   required: true },
  canReassignManager: { type: Boolean, default: false },
  clientName:         { type: String,  default: '' },
  clientPhone:        { type: String,  default: '' },
})

const emit = defineEmits(['update:clientName', 'update:clientPhone', 'counterparty-change', 'new-client'])

const clientNameModel = computed({
  get:  () => props.clientName,
  set: v => emit('update:clientName', v),
})
const clientPhoneModel = computed({
  get:  () => props.clientPhone,
  set: v => emit('update:clientPhone', v),
})

const selectedCounterparty = computed(() =>
  props.counterparties.find(cp => String(cp.id) === String(props.form.counterparty_id)) ?? null
)

const clientInitials = computed(() => {
  const name = selectedCounterparty.value?.name || props.clientName || ''
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase() || 'К'
})
</script>

<style scoped>
/* ─── Wrapper ─── */
.cbc-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ─── Search ─── */
.cbc-search-row {
  position: relative;
}

.cbc-search-icon {
  color: #3B82F6;
  margin-left: 4px;
}

.cbc-search-select :deep(.el-select__wrapper) {
  height: 40px !important;
  background: #F9FAFB !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  padding: 0 12px !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.cbc-search-select :deep(.el-select__wrapper:hover) {
  border-color: #3B82F6 !important;
}

.cbc-search-select :deep(.el-select__wrapper.is-focus) {
  border-color: #2563EB !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

.cbc-search-select :deep(.el-select__placeholder) {
  font-size: 13px;
  color: #9CA3AF;
}

.cbc-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
}
.cbc-option-name  { font-weight: 600; font-size: 13px; color: #1F2937; }
.cbc-option-phone { font-size: 11px; color: #9CA3AF; margin-left: 12px; }

/* ─── Selected client bar ─── */
.cbc-client-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 10px;
}

.cbc-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 900;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.cbc-client-info {
  flex: 1;
  min-width: 0;
}

.cbc-active-label {
  font-size: 9.5px;
  font-weight: 800;
  color: #16A34A;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  line-height: 1;
  margin-bottom: 3px;
}

.cbc-client-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.cbc-client-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cbc-client-phone {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #6B7280;
  font-weight: 500;
}

.cbc-change-btn {
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: 8px;
  border: 1px solid #BFDBFE;
  background: white;
  color: #2563EB;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}

.cbc-change-btn:hover {
  background: #DBEAFE;
  border-color: #93C5FD;
}

/* ─── Fields grid ─── */
.cbc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.cbc-grid--logistics {
  padding-top: 2px;
}

.cbc-field {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 8px 12px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #E5E7EB;
  transition: border-color 0.15s;
}

.cbc-field:focus-within {
  border-color: #93C5FD;
}

.cbc-field label {
  font-size: 10.5px;
  font-weight: 700;
  color: #6B7280;
  line-height: 1;
  pointer-events: none;
}

.cbc-field :deep(.el-input__wrapper),
.cbc-field :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  height: 26px !important;
  min-height: 26px !important;
}

.cbc-field :deep(.el-input__inner) {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #1F2937 !important;
  padding: 0 !important;
}

.cbc-field :deep(.el-select__placeholder),
.cbc-field :deep(.el-input__inner::placeholder) {
  font-size: 12.5px !important;
  color: #9CA3AF !important;
  font-weight: 400 !important;
}

/* ─── Transition ─── */
.cbc-slide-enter-active, .cbc-slide-leave-active {
  transition: all 0.2s ease;
}
.cbc-slide-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.cbc-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
