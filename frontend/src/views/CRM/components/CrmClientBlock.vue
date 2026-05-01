<template>
  <div class="crm-client-block-2026 overflow-hidden transition-all duration-500">
    <!-- ─── HEADER: Premium Layer ─── -->
    <div class="flex items-center justify-between px-5 py-3.5 bg-white/40 backdrop-blur-md border-b border-slate-100/50">
      <div class="flex items-center gap-3">
        <div class="flex items-center justify-center px-3 py-1 bg-indigo-600 text-white text-[11px] font-bold rounded-full shadow-sm">
          Крок 1
        </div>
        <div>
          <h3 class="text-[16px] font-extrabold text-slate-800 leading-none">Дані замовника</h3>
          <p class="text-[10px] text-slate-400 mt-0.5 font-medium">Керування базою та новими контактами</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <transition name="el-fade-in-linear">
          <div v-if="form.counterparty_id" class="flex items-center gap-2 px-2.5 py-1.5 bg-emerald-50 border border-emerald-100 rounded-full cursor-default">
            <div class="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_4px_rgba(16,185,129,0.4)]"></div>
            <span class="text-[10px] font-bold text-emerald-700">Клієнта обрано</span>
          </div>
        </transition>

        <button 
          type="button"
          @click="$emit('new-client')"
          class="flex items-center gap-2 px-3.5 py-2 bg-white text-slate-700 border border-slate-200 rounded-xl text-[11px] font-bold hover:border-indigo-400 hover:text-indigo-600 transition-all active:scale-95 group"
        >
          <el-icon class="text-xs"><Plus /></el-icon>
          <span>Новий клієнт</span>
        </button>
      </div>
    </div>

    <!-- ─── CONTENT: Depth Grid ─── -->
    <div class="p-4 space-y-4 bg-[#FDFDFF]">
      
      <!-- 1. Master Search -->
      <div class="relative group">
        <div class="absolute inset-0 bg-indigo-500/5 blur-lg rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
        <div class="relative bg-white border border-slate-200/60 rounded-xl p-0.5 shadow-sm focus-within:border-indigo-300 transition-all">
          <el-select
            v-model="form.counterparty_id"
            filterable
            clearable
            placeholder="Почніть вводити ім'я або номер телефону..."
            class="premium-search-select w-full"
            @change="$emit('counterparty-change', $event)"
          >
            <template #prefix>
              <el-icon class="text-indigo-400 ml-2 text-sm"><Search /></el-icon>
            </template>
            <el-option
              v-for="cp in counterparties"
              :key="cp.id"
              :label="cp.name"
              :value="cp.id"
            >
              <div class="flex items-center justify-between w-full py-0.5">
                <span class="font-bold text-slate-700 text-xs">{{ cp.name }}</span>
                <span class="text-[10px] text-slate-400 font-mono">{{ cp.phone }}</span>
              </div>
            </el-option>
          </el-select>
        </div>
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
  Box, Bicycle
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
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.045);
  border: 1px solid #EAF0F7;
}

.input-card-premium {
  @apply flex flex-col gap-1 p-2.5 rounded-xl transition-all duration-200;
  background: #FFFFFF;
  border: 1px solid #E5EAF2;
  min-height: 64px; /* Target total height constraint */
}

.input-card-premium label {
  @apply flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 px-0.5;
}

.input-card-premium label .el-icon {
  @apply text-indigo-400/70 text-[12px];
}

.input-card-premium:focus-within {
  @apply border-indigo-300 ring-4 ring-indigo-50/50 bg-white;
}

.input-card-premium.is-selected {
  background: #F8FAFF;
  border-color: #E0E7FF;
}

/* Control zone height unification */
:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  @apply shadow-none bg-transparent border-none p-0 h-7 !important;
  box-shadow: none !important;
  min-height: 28px !important;
}

:deep(.el-input__inner) {
  @apply font-bold text-slate-700 text-[13px] !important;
}

:deep(.el-select__placeholder) {
  @apply font-semibold text-slate-400 text-[12px] !important;
}

.premium-search-select :deep(.el-select__wrapper) {
  @apply h-10 !important;
}

:deep(.el-select__tags) {
  display: none !important;
}
</style>
