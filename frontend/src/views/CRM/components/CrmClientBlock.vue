<template>
  <div class="crm-client-block-2026 overflow-hidden transition-all duration-500">
    <!-- ─── HEADER: Premium Layer ─── -->
    <div class="block-header-premium">
      <div class="flex items-center gap-4">
        <!-- Modern Step Pill -->
        <div class="step-pill-modern">
          <span class="label">Крок</span>
          <span class="number">01</span>
        </div>
        
        <!-- Icon & Titles -->
        <div class="flex items-center gap-3">
          <div class="header-icon-box">
            <el-icon><User /></el-icon>
          </div>
          <div>
            <h3 class="title">Дані замовника</h3>
            <p class="subtitle">Керування базою та новими контактами</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Completion Status -->
        <div class="status-badge-premium" :class="{ 'is-complete': isBlockComplete }">
          <el-icon><CircleCheck v-if="isBlockComplete" /><InfoFilled v-else /></el-icon>
          <span>{{ clientStatusLabel }}</span>
          <b>{{ clientCompletionPct }}%</b>
        </div>

        <button 
          type="button"
          @click="$emit('new-client')"
          class="btn-new-client"
        >
          <el-icon><Plus /></el-icon>
          <span>Новий клієнт</span>
        </button>
      </div>
    </div>

    <!-- ─── CONTENT: Depth Grid ─── -->
    <div class="client-block-body">
      
      <div class="search-section-premium">
        <div class="client-search-kicker">
          <span>База клієнтів</span>
          <em>{{ selectedCounterparty ? 'контакт знайдено' : 'можна створити нового' }}</em>
        </div>
        <div v-if="form.counterparty_id" class="client-pill-active">
          <el-icon><Check /></el-icon>
          <span>Клієнта обрано</span>
        </div>
        <el-select
          v-model="form.counterparty_id"
          filterable
          clearable
          placeholder="Почніть вводити ім'я або номер телефону..."
          class="master-search-select"
          @change="$emit('counterparty-change', $event)"
        >
          <template #prefix>
            <el-icon class="text-indigo-500"><Search /></el-icon>
          </template>
          <el-option
            v-for="cp in counterparties"
            :key="cp.id"
            :label="cp.name"
            :value="cp.id"
          >
            <div class="flex items-center justify-between w-full">
              <span class="font-bold text-slate-700">{{ cp.name }}</span>
              <span class="text-[10px] text-slate-400 font-mono">{{ cp.phone }}</span>
            </div>
          </el-option>
        </el-select>
        <div v-if="selectedCounterparty" class="selected-client-glance">
          <div class="selected-client-avatar">{{ clientInitials }}</div>
          <div class="selected-client-copy">
            <strong>{{ selectedCounterparty.name }}</strong>
            <span>{{ selectedCounterparty.phone || form.client_phone || 'Телефон не вказано' }}</span>
          </div>
          <div class="client-status-pill">
            Активний контакт
          </div>
        </div>
      </div>

      <!-- 2. Unified Grid -->
      <div class="client-fields-grid">
        
        <!-- Row 1 -->
        <div class="input-card-premium" :class="{ 'is-selected': !!form.counterparty_id }">
          <label><el-icon><User /></el-icon> Ім'я клієнта</label>
          <el-input v-model="clientNameModel" :readonly="!!form.counterparty_id" placeholder="Прізвище та ім'я" />
        </div>

        <div class="input-card-premium" :class="{ 'is-selected': !!form.counterparty_id }">
          <label><el-icon><Phone /></el-icon> Телефон</label>
          <el-input v-model="clientPhoneModel" :readonly="!!form.counterparty_id" placeholder="+380..." />
        </div>

        <div class="input-card-premium">
          <label><el-icon><Location /></el-icon> Місто</label>
          <el-input v-model="form.city" placeholder="Напр. Київ" />
        </div>

        <!-- Row 2: Enhanced Selects -->
        <div class="input-card-premium">
          <label><el-icon><MagicStick /></el-icon> Джерело</label>
          <el-select v-model="form.lead_source_id" placeholder="Обрати канал" class="w-full" clearable>
            <template #prefix v-if="selectedSource">
              <el-icon class="text-indigo-400 text-xs mr-1">
                <component :is="getSourceIcon(selectedSource.name)" />
              </el-icon>
            </template>
            <el-option v-for="ch in leadSources" :key="ch.id" :label="ch.name" :value="ch.id">
              <div class="flex items-center gap-2">
                <el-icon class="text-slate-400 text-xs">
                  <component :is="getSourceIcon(ch.name)" />
                </el-icon>
                <span class="text-xs">{{ ch.name }}</span>
              </div>
            </el-option>
          </el-select>
        </div>

        <div class="input-card-premium">
          <label><el-icon><Avatar /></el-icon> Менеджер</label>
          <CrmManagerBlock
            :form="form"
            :manager-options="managerOptions"
            :can-reassign-manager="canReassignManager"
          />
        </div>

        <div class="input-card-premium">
          <label><el-icon><Van /></el-icon> Доставка</label>
          <el-select v-model="form.delivery_method_id" placeholder="Спосіб доставки" class="w-full" clearable>
            <template #prefix v-if="selectedDelivery">
              <el-icon class="text-indigo-400 text-xs mr-1">
                <component :is="getDeliveryIcon(selectedDelivery.name)" />
              </el-icon>
            </template>
            <el-option v-for="dm in deliveryMethods" :key="dm.id" :label="dm.name" :value="dm.id">
              <div class="flex items-center gap-2">
                <el-icon class="text-slate-400 text-xs">
                  <component :is="getDeliveryIcon(dm.name)" />
                </el-icon>
                <span class="text-xs">{{ dm.name }}</span>
              </div>
            </el-option>
          </el-select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Plus, User, Search, Phone, MagicStick, Avatar, Location, Check, Van, 
  Camera, Collection, DataLine, Link, ChatRound, ShoppingBag, Refresh, Star, Shop,
  Box, Bicycle, CircleCheck, InfoFilled
} from '@element-plus/icons-vue'
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

const isBlockComplete = computed(() => {
  return (props.form.counterparty_id || (props.clientName && props.clientPhone)) &&
         props.form.lead_source_id &&
         props.form.manager_id &&
         props.form.delivery_method_id
})

const selectedSource = computed(() => props.leadSources.find(s => s.id === props.form.lead_source_id))
const selectedDelivery = computed(() => props.deliveryMethods.find(d => d.id === props.form.delivery_method_id))
const selectedCounterparty = computed(() => props.counterparties.find(cp => String(cp.id) === String(props.form.counterparty_id)))

const filledClientFields = computed(() => {
  const checks = [
    props.form.counterparty_id || props.clientName,
    props.clientPhone,
    props.form.lead_source_id,
    props.form.manager_id,
    props.form.delivery_method_id,
    props.form.city,
  ]
  return checks.filter(Boolean).length
})

const clientCompletionPct = computed(() => Math.round((filledClientFields.value / 6) * 100))
const clientStatusLabel = computed(() => {
  if (isBlockComplete.value) return 'Готово до роботи'
  if (filledClientFields.value >= 3) return 'Майже заповнено'
  return 'Очікує даних'
})

const clientInitials = computed(() => {
  const name = selectedCounterparty.value?.name || props.clientName || 'Клієнт'
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'К'
})

const getSourceIcon = (name) => {
  const n = name.toLowerCase()
  if (n.includes('inst')) return Camera
  if (n.includes('fb') || n.includes('face')) return Collection
  if (n.includes('google')) return DataLine
  if (n.includes('сайт')) return Link
  if (n.includes('тел')) return Phone
  if (n.includes('viber') || n.includes('tele') || n.includes('chat')) return ChatRound
  if (n.includes('olx') || n.includes('prom') || n.includes('roz')) return ShoppingBag
  if (n.includes('повт')) return Refresh
  if (n.includes('рек')) return Star
  if (n.includes('офл') || n.includes('маг') || n.includes('шоу')) return Shop
  return MagicStick
}

const getDeliveryIcon = (name) => {
  const n = name.toLowerCase()
  if (n.includes('сам')) return User
  if (n.includes('кур')) return Bicycle
  return Box
}
</script>

<style scoped>
.crm-client-block-2026 {
  background: #fff;
  border-radius: 24px;
  border: 1px solid rgba(226, 232, 240, .9);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07), 0 1px 0 rgba(255, 255, 255, .9) inset;
  overflow: hidden;
  position: relative;
  isolation: isolate;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.crm-client-block-2026:hover {
  transform: translateY(-2px);
  border-color: rgba(199, 210, 254, .95);
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.09), 0 1px 0 rgba(255, 255, 255, .9) inset;
}

.crm-client-block-2026::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: linear-gradient(180deg, #6366F1, #1463FF);
  opacity: .95;
  z-index: 1;
}

/* --- HEADER PREMIUM --- */
.block-header-premium {
  padding: 18px 24px 16px 28px;
  background:
    radial-gradient(circle at 10% 0%, rgba(99, 102, 241, .14), transparent 28%),
    linear-gradient(90deg, #F8FAFF 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}

.step-pill-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #7C3AED 0%, #1463FF 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.28);
  position: relative;
  overflow: hidden;
}
.step-pill-modern::after {
  content: '';
  position: absolute;
  inset: -40% -20% auto auto;
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, .25);
  border-radius: 999px;
}
.step-pill-modern .label { font-size: 8px; font-weight: 800; text-transform: uppercase; opacity: 0.8; line-height: 1; }
.step-pill-modern .number { font-size: 16px; font-weight: 900; line-height: 1.1; }

.header-icon-box {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, .9);
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #6366F1;
  box-shadow: 0 8px 18px rgba(99,102,241,.11);
  border: 1px solid #EEF2FF;
}

.block-header-premium .title { font-size: 17px; font-weight: 850; color: #0F172A; margin: 0; letter-spacing: -0.02em; }
.block-header-premium .subtitle { font-size: 11px; color: #94A3B8; margin: 0; font-weight: 500; }

.status-badge-premium {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(241, 245, 249, .82);
  border: 1px solid rgba(226, 232, 240, .9);
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  transition: all 0.3s ease;
  white-space: nowrap;
}
.status-badge-premium b {
  color: #312E81;
  font-size: 10px;
  font-weight: 900;
}
.status-badge-premium.is-complete { background: #ECFDF5; border-color: #BBF7D0; color: #059669; }
.status-badge-premium.is-complete b { color: #047857; }

.btn-new-client {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  transition: all 0.2s;
  cursor: pointer;
}
.btn-new-client:hover { border-color: #6366F1; color: #6366F1; box-shadow: 0 12px 22px rgba(99, 102, 241, 0.10); transform: translateY(-1px); }

.client-block-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background:
    linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%);
}

/* --- SEARCH SECTION --- */
.search-section-premium {
  position: relative;
  background: #fff;
  border: 1px solid #E5EAF2;
  border-radius: 16px;
  padding: 20px 12px 10px;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(15, 23, 42, .035);
}
.search-section-premium:hover { border-color: #CBD5E1; }
.search-section-premium:focus-within { border-color: #6366F1; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.06), 0 14px 32px rgba(99,102,241,.08); }

.client-search-kicker {
  position: absolute;
  top: -10px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  background: #fff;
}
.client-search-kicker span {
  color: #6366F1;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.client-search-kicker em {
  color: #94A3B8;
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
}

.client-pill-active {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #10B981;
  color: white;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
}

.selected-client-glance {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 8px 2px 0;
  padding: 8px 10px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(238, 242, 255, .78), rgba(255, 255, 255, .95));
  border: 1px solid #EEF2FF;
}
.selected-client-avatar {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, #6366F1, #1463FF);
  font-size: 11px;
  font-weight: 900;
  box-shadow: 0 8px 14px rgba(99,102,241,.22);
}
.selected-client-copy {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
  line-height: 1.15;
}
.selected-client-copy strong {
  overflow: hidden;
  color: #0F172A;
  font-size: 12px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.selected-client-copy span {
  color: #64748B;
  font-size: 10px;
  font-weight: 700;
}
.client-status-pill {
  padding: 5px 8px;
  border-radius: 999px;
  color: #047857;
  background: #ECFDF5;
  border: 1px solid #BBF7D0;
  font-size: 10px;
  font-weight: 850;
  white-space: nowrap;
}

.client-fields-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

/* --- INPUT CARDS --- */
.input-card-premium {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease, background .18s ease;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 68px;
}
.input-card-premium:hover {
  border-color: #CBD5E1;
  box-shadow: 0 10px 24px rgba(15,23,42,.045);
  transform: translateY(-1px);
}
.input-card-premium label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  color: #94A3B8;
  font-size: 10px;
  font-weight: 850;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.input-card-premium label .el-icon { color: rgba(99,102,241,.82); font-size: 12px; }
.input-card-premium:focus-within { border-color: #6366F1; background: #fff; box-shadow: 0 0 0 4px rgba(99,102,241,.06); }

.input-card-premium.is-selected { background: #F8FAFF; border-color: #E0E7FF; }

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  box-shadow: none !important;
  background: transparent !important;
  border: 0 !important;
  padding: 0 !important;
  min-height: 34px !important;
}
:deep(.el-input__inner) { color: #334155 !important; font-size: 14px !important; font-weight: 750 !important; }
:deep(.el-select__placeholder) { color: #94A3B8 !important; font-size: 13px !important; font-weight: 700 !important; }

.master-search-select :deep(.el-select__wrapper) { height: 44px !important; }

@media (max-width: 980px) {
  .block-header-premium {
    align-items: flex-start;
    flex-direction: column;
  }
  .client-fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
