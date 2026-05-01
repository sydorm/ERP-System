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
          <span>{{ isBlockComplete ? 'Заповнено' : 'Очікує даних' }}</span>
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
    <div class="p-4 space-y-4 bg-[#FDFDFF]">
      
      <div class="search-section-premium">
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
      </div>

      <!-- 2. Unified Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        
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
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.03), 0 0 0 1px rgba(15, 23, 42, 0.05);
  overflow: hidden;
}

/* --- HEADER PREMIUM --- */
.block-header-premium {
  padding: 16px 24px;
  background: linear-gradient(90deg, #F8FAFF 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-pill-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #6366F1;
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.step-pill-modern .label { font-size: 8px; font-weight: 800; text-transform: uppercase; opacity: 0.8; line-height: 1; }
.step-pill-modern .number { font-size: 16px; font-weight: 900; line-height: 1.1; }

.header-icon-box {
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #6366F1;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  border: 1px solid #EEF2FF;
}

.block-header-premium .title { font-size: 16px; font-weight: 800; color: #1E293B; margin: 0; }
.block-header-premium .subtitle { font-size: 11px; color: #94A3B8; margin: 0; font-weight: 500; }

.status-badge-premium {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #F1F5F9;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  transition: all 0.3s ease;
}
.status-badge-premium.is-complete { background: #ECFDF5; color: #059669; }

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
.btn-new-client:hover { border-color: #6366F1; color: #6366F1; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08); }

/* --- SEARCH SECTION --- */
.search-section-premium {
  position: relative;
  background: #fff;
  border: 1px solid #E5EAF2;
  border-radius: 16px;
  padding: 4px;
  transition: all 0.3s;
}
.search-section-premium:focus-within { border-color: #6366F1; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.05); }

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

/* --- INPUT CARDS --- */
.input-card-premium {
  @apply flex flex-col gap-1 p-3 rounded-xl transition-all duration-200;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 68px;
}
.input-card-premium label { @apply flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1; }
.input-card-premium label .el-icon { @apply text-indigo-400/80 text-[12px]; }
.input-card-premium:focus-within { border-color: #6366F1; background: #fff; }

.input-card-premium.is-selected { background: #F8FAFF; border-color: #E0E7FF; }

:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  @apply shadow-none bg-transparent border-none p-0 h-8 !important;
}
:deep(.el-input__inner) { @apply font-bold text-slate-700 text-[14px] !important; }
:deep(.el-select__placeholder) { @apply font-semibold text-slate-400 text-[13px] !important; }

.master-search-select :deep(.el-select__wrapper) { height: 44px !important; }
</style>
