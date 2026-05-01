<template>
  <div class="crm-section crm-product-block-premium">
    <div class="space-y-6">
      <!-- Base Nomenclature -->
      <div class="input-card-premium">
        <label>Базова номенклатура</label>
        <el-select
          v-model="form.product_id"
          filterable
          placeholder="Оберіть виріб зі списку або почніть вводити..."
          class="w-full master-search-select"
          @change="$emit('product-change', $event)"
        >
          <el-option
            v-for="p in products"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-sm">{{ p.name }}</span>
              <span class="text-xs text-blue-600 font-black">{{ p.price }} ₴</span>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- Dynamic Attributes Grid -->
      <transition name="el-zoom-in-top">
        <div v-if="productAttributes.length" class="grid grid-cols-2 gap-4">
          <div v-for="attr in productAttributes" :key="attr.id" class="input-card-premium">
            <label>{{ attr.name }}</label>
            
            <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="flex flex-wrap gap-2 mt-1">
              <button
                v-for="opt in attr.options"
                :key="opt.id"
                class="px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
                :class="form.attributes_values?.[attr.id] === opt.value ? 'bg-blue-600 border-blue-600 text-white shadow-md' : 'bg-white border-gray-200 text-gray-600 hover:border-blue-400'"
                @click="$emit('set-attr-value', attr.id, opt.value)"
              >
                {{ opt.value }}
              </button>
            </div>

            <div v-else-if="attr.type === 'DIMENSIONS'" class="flex items-center gap-2 mt-1">
              <el-input-number v-model="form.attributes_values[attr.id].w" :min="1" controls-position="right" class="!w-24" @change="v => $emit('set-attr-dim', attr.id, 'w', v)" />
              <span class="text-gray-300">×</span>
              <el-input-number v-model="form.attributes_values[attr.id].h" :min="1" controls-position="right" class="!w-24" @change="v => $emit('set-attr-dim', attr.id, 'h', v)" />
              <span class="text-xs font-bold text-gray-400">см</span>
            </div>

            <el-input v-else v-model="form.attributes_values[attr.id]" :placeholder="attr.name" class="mt-1" @input="v => $emit('set-attr-value', attr.id, v)" />
          </div>
        </div>
      </transition>

      <!-- Comment & References -->
      <div class="grid grid-cols-1 gap-6 pt-4">
        <div class="input-card-premium">
          <label>Коментар до замовлення</label>
          <el-input
            v-model="form.comment"
            type="textarea"
            :rows="2"
            placeholder="Наприклад, терміново, пакування преміум"
            class="max-h-[80px] overflow-hidden"
          />
        </div>

        <div class="space-y-3">
          <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest">Візуальні референси</label>
          <div class="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center hover:border-blue-400 hover:bg-blue-50/30 transition-all cursor-pointer group">
            <CrmReferencePhotosBlock :form="form" @upload-photo="$emit('upload-photo', $event)" />
            <div v-if="!form.reference_photo" class="mt-2">
              <p class="text-sm font-bold text-gray-600">Перетягніть файл сюди або натисніть, щоб завантажити</p>
              <p class="text-xs text-gray-400 mt-1">JPG, PNG, WEBP до 10 МБ</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Box, EditPen, Picture, Operation, CircleCheck, InfoFilled } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

const props = defineProps({
  form: { type: Object, required: true },
  products: { type: Array, required: true },
  productAttributes: { type: Array, required: true },
})

defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])

const isBlockComplete = computed(() => {
  return props.form.product_id && (Object.keys(props.form.attributes_values || {}).length > 0)
})

const selectedProduct = computed(() => props.products.find(p => String(p.id) === String(props.form.product_id)))
const filledAttributes = computed(() => (
  Object.values(props.form.attributes_values || {}).filter(value => {
    if (value == null || value === '') return false
    if (typeof value === 'object') return Object.values(value).some(Boolean)
    return true
  }).length
))
const productCompletionPct = computed(() => {
  const checks = [props.form.product_id, filledAttributes.value > 0, props.form.comment]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
})
const productStatusLabel = computed(() => {
  if (isBlockComplete.value) return 'Конфігуровано'
  if (props.form.product_id) return 'Потрібні параметри'
  return 'Оберіть виріб'
})
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
