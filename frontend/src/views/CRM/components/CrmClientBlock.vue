<template>
  <div class="crm-client-block-2026 overflow-hidden transition-all duration-500">
    <!-- ─── HEADER: Premium Layer ─── -->
    <div class="space-y-6">
      <!-- Search & Quick Selection -->
      <div class="relative">
        <el-select
          v-model="form.counterparty_id"
          filterable
          remote
          placeholder="Пошук клієнта за іменем або телефоном..."
          class="w-full master-search-select"
          @change="$emit('counterparty-change', $event)"
        >
          <template #prefix>
            <el-icon class="text-blue-600"><Search /></el-icon>
          </template>
          <el-option
            v-for="cp in counterparties"
            :key="cp.id"
            :label="cp.name"
            :value="cp.id"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold">{{ cp.name }}</span>
              <span class="text-xs text-gray-400">{{ cp.phone }}</span>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- Selected Client Card or New Form -->
      <div v-if="selectedCounterparty" class="p-4 bg-blue-50/50 rounded-xl border border-blue-100 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-blue-600 text-white rounded-xl flex items-center justify-center text-lg font-black shadow-lg shadow-blue-200">
            {{ clientInitials }}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-black text-green-600 uppercase tracking-wider">Активний контакт</span>
              <h3 class="text-lg font-bold text-gray-900">{{ selectedCounterparty.name }}</h3>
            </div>
            <div class="flex items-center gap-4 mt-0.5">
              <span class="text-sm font-medium text-gray-500 flex items-center gap-1.5">
                <el-icon><Phone /></el-icon> {{ selectedCounterparty.phone }}
              </span>
              <span v-if="selectedCounterparty.city" class="text-sm font-medium text-gray-400 flex items-center gap-1.5">
                <el-icon><Location /></el-icon> {{ selectedCounterparty.city }}
              </span>
            </div>
          </div>
        </div>
        <button 
          @click="form.counterparty_id = null" 
          class="px-4 py-2 text-sm font-bold text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
        >
          Змінити
        </button>
      </div>

      <!-- New Client Form (Grid 2+2) -->
      <div v-else class="grid grid-cols-2 gap-4">
        <div class="input-card-premium col-span-1">
          <label>Прізвище та ім'я</label>
          <el-input v-model="clientNameModel" placeholder="Наприклад, Шевченко Андрій" />
        </div>
        <div class="input-card-premium col-span-1">
          <label>Номер телефону</label>
          <el-input v-model="clientPhoneModel" placeholder="+38 (0__) ___ __ __" />
        </div>
        <div class="input-card-premium col-span-1">
          <label>Місто (автодоповнення)</label>
          <el-input v-model="form.city" placeholder="Введіть місто..." />
        </div>
        <div class="input-card-premium col-span-1">
          <label>Джерело залучення</label>
          <el-select v-model="form.lead_source_id" placeholder="Оберіть джерело" class="w-full">
             <el-option v-for="ch in leadSources" :key="ch.id" :label="ch.name" :value="ch.id" />
          </el-select>
        </div>
      </div>

      <!-- Logistics Section -->
      <div class="grid grid-cols-2 gap-4 pt-2">
        <div class="input-card-premium">
          <label>Спосіб доставки</label>
          <el-select v-model="form.delivery_method_id" placeholder="Оберіть доставку" class="w-full">
            <el-option v-for="dm in deliveryMethods" :key="dm.id" :label="dm.name" :value="dm.id" />
          </el-select>
        </div>
        <div class="input-card-premium">
          <label>Відповідальний менеджер</label>
          <CrmManagerBlock
            :form="form"
            :manager-options="managerOptions"
            :can-reassign-manager="canReassignManager"
          />
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

.input-card-premium {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 14px;
  border-radius: 12px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  min-height: 64px;
}
.input-card-premium label {
  font-size: 11px;
  font-weight: 700;
  color: #6B7280;
  text-transform: none;
}
.master-search-select :deep(.el-select__wrapper) {
  height: 48px !important;
  background: #F9FAFB !important;
  border-radius: 12px !important;
}
</style>
