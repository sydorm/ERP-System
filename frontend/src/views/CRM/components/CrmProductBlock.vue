<template>
  <div class="cpb-wrap">

    <!-- ═══ PRODUCT LINES ═══ -->
    <div class="cpb-lines">

      <div
        v-for="(line, idx) in productLines"
        :key="line._uid"
        class="cpb-line"
        :class="{ 'cpb-line--primary': idx === 0 }"
      >

        <!-- Line row: select + qty + price + remove -->
        <div class="cpb-line-row">

          <!-- Product select -->
          <div class="cpb-select-wrap">
            <el-select
              v-model="line.product_id"
              filterable
              clearable
              :placeholder="idx === 0 ? 'Оберіть виріб зі списку або почніть вводити...' : 'Додатковий виріб...'"
              class="w-full cpb-select"
              @change="(v) => onProductSelect(idx, v)"
            >
              <el-option
                v-for="p in products"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              >
                <div class="cpb-opt">
                  <span class="cpb-opt-name">{{ p.name }}</span>
                  <span class="cpb-opt-price">{{ formatPrice(p.price) }} ₴</span>
                </div>
              </el-option>
            </el-select>
          </div>

          <!-- Quantity -->
          <div class="cpb-qty-wrap">
            <label class="cpb-qty-label">Кількість</label>
            <div class="cpb-qty-ctrl">
              <button class="cpb-qty-btn" @click="changeQty(idx, -1)">−</button>
              <input
                type="number"
                class="cpb-qty-input"
                :value="line.quantity"
                min="1"
                @input="e => onQtyInput(idx, e.target.value)"
              />
              <button class="cpb-qty-btn" @click="changeQty(idx, +1)">+</button>
            </div>
          </div>

          <!-- Line price badge -->
          <div v-if="getLineTotalPrice(line)" class="cpb-price-badge">
            {{ getLineTotalPrice(line) }} ₴
          </div>

          <!-- Remove button (not on first line) -->
          <button v-if="idx > 0" class="cpb-remove-btn" @click="removeLine(line._uid)" title="Прибрати">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <!-- Primary product attributes -->
        <transition name="cpb-attrs">
          <div v-if="idx === 0 && productAttributes.length" class="cpb-attrs-grid">
            <div
              v-for="attr in productAttributes"
              :key="attr.id"
              class="cpb-attr-card"
            >
              <label class="cpb-attr-label">{{ attr.name }}</label>

              <!-- SELECT / COLOR chips -->
              <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="cpb-chips">
                <button
                  v-for="opt in attr.options"
                  :key="opt.id"
                  class="cpb-chip"
                  :class="{ 'cpb-chip--active': form.attributes_values?.[attr.id] === opt.value }"
                  @click="$emit('set-attr-value', attr.id, opt.value)"
                >
                  {{ opt.value }}
                </button>
              </div>

              <!-- DIMENSIONS -->
              <div v-else-if="attr.type === 'DIMENSIONS'" class="cpb-dims">
                <el-input-number
                  v-model="form.attributes_values[attr.id].w"
                  :min="1"
                  controls-position="right"
                  class="!w-[96px]"
                  @change="v => $emit('set-attr-dim', attr.id, 'w', v)"
                />
                <span class="cpb-dims-sep">×</span>
                <el-input-number
                  v-model="form.attributes_values[attr.id].h"
                  :min="1"
                  controls-position="right"
                  class="!w-[96px]"
                  @change="v => $emit('set-attr-dim', attr.id, 'h', v)"
                />
                <span class="cpb-dims-unit">мм</span>
              </div>

              <!-- TEXT / NUMBER -->
              <el-input
                v-else
                v-model="form.attributes_values[attr.id]"
                :placeholder="attr.name"
                @input="v => $emit('set-attr-value', attr.id, v)"
              />
            </div>
          </div>
        </transition>

      </div><!-- / v-for line -->

    </div><!-- / cpb-lines -->

    <!-- ─── Add line button ─── -->
    <button class="cpb-add-btn" @click="addLine">
      <el-icon><Plus /></el-icon>
      Додати ще один виріб
    </button>

    <!-- ─── Comment + Reference ─── -->
    <div class="cpb-bottom">

      <!-- Comment -->
      <div class="cpb-field">
        <label class="cpb-field-label">Коментар до замовлення</label>
        <el-input
          v-model="form.comment"
          type="textarea"
          :rows="2"
          placeholder="Наприклад, терміново, пакування преміум"
        />
      </div>

      <!-- Reference toggle button -->
      <div class="cpb-ref-section">
        <button
          class="cpb-ref-btn"
          :class="{ 'cpb-ref-btn--active': hasReference }"
          @click="refOpen = !refOpen"
        >
          <el-icon><Picture /></el-icon>
          <span>{{ hasReference ? 'Референс прикріплено' : 'Прикріпити референс' }}</span>
          <span v-if="hasReference" class="cpb-ref-dot"></span>
          <el-icon class="cpb-ref-chevron" :class="{ 'cpb-ref-chevron--open': refOpen }">
            <ArrowDown />
          </el-icon>
        </button>

        <!-- Collapsible reference panel -->
        <transition name="cpb-ref-slide">
          <div v-if="refOpen" class="cpb-ref-panel">
            <CrmReferencePhotosBlock
              :form="form"
              @upload-photo="$emit('upload-photo', $event)"
            />
          </div>
        </transition>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Close, Plus, Picture, ArrowDown } from '@element-plus/icons-vue'
import CrmReferencePhotosBlock from './CrmReferencePhotosBlock.vue'

const props = defineProps({
  form:              { type: Object, required: true },
  products:          { type: Array,  required: true },
  productAttributes: { type: Array,  required: true },
})

const emit = defineEmits(['product-change', 'set-attr-value', 'set-attr-dim', 'upload-photo'])

// ─── Product lines state ───────────────────────────────────────────────────
let _uid = 1
const makeUid = () => ++_uid

const productLines = ref([
  { _uid: makeUid(), product_id: null, quantity: 1 },
])

// Init from form on mount
onMounted(() => {
  if (props.form.product_lines?.length) {
    productLines.value = props.form.product_lines.map(l => ({
      _uid:       makeUid(),
      product_id: l.product_id ?? null,
      quantity:   l.quantity   ?? 1,
    }))
  } else if (props.form.product_id) {
    productLines.value = [{ _uid: makeUid(), product_id: props.form.product_id, quantity: 1 }]
  }
})

// Sync when order loads externally (e.g. edit mode)
watch(() => props.form.product_id, (id) => {
  if (!props.form.product_lines?.length && productLines.value[0]?.product_id !== id) {
    productLines.value[0].product_id = id ?? null
  }
})

const syncToForm = () => {
  props.form.product_id    = productLines.value[0]?.product_id ?? null
  props.form.product_lines = productLines.value.map(l => ({
    product_id: l.product_id,
    quantity:   l.quantity,
  }))
}

const onProductSelect = (idx, id) => {
  productLines.value[idx].product_id = id ?? null
  syncToForm()
  if (idx === 0) emit('product-change', id)
}

const onQtyInput = (idx, val) => {
  const n = Math.max(1, parseInt(val) || 1)
  productLines.value[idx].quantity = n
  syncToForm()
}

const changeQty = (idx, delta) => {
  const n = Math.max(1, (productLines.value[idx].quantity || 1) + delta)
  productLines.value[idx].quantity = n
  syncToForm()
}

const addLine = () => {
  productLines.value.push({ _uid: makeUid(), product_id: null, quantity: 1 })
  syncToForm()
}

const removeLine = (uid) => {
  productLines.value = productLines.value.filter(l => l._uid !== uid)
  syncToForm()
  // Re-emit first product so parent can reload attributes
  emit('product-change', productLines.value[0]?.product_id ?? null)
}

// ─── Price helpers ─────────────────────────────────────────────────────────
const getProduct = (id) => props.products.find(p => String(p.id) === String(id))

const formatPrice = (v) => v ? new Intl.NumberFormat('uk-UA').format(v) : ''

const getLineTotalPrice = (line) => {
  if (!line.product_id) return null
  const p = getProduct(line.product_id)
  if (!p?.price) return null
  return formatPrice(p.price * line.quantity)
}

// ─── Reference toggle ──────────────────────────────────────────────────────
const refOpen     = ref(false)
const hasReference = computed(() => !!props.form.reference_photo)

// Auto-open panel when reference exists (e.g. on order load)
watch(hasReference, (v) => { if (v) refOpen.value = true }, { immediate: true })
</script>

<style scoped>
/* ─── Root ─── */
.cpb-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ─── Lines ─── */
.cpb-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cpb-line {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  transition: border-color 0.2s;
}

.cpb-line--primary {
  background: #fff;
  border-color: #E0E9FF;
}

.cpb-line:focus-within {
  border-color: #93C5FD;
}

/* ─── Line row ─── */
.cpb-line-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cpb-select-wrap {
  flex: 1;
  min-width: 0;
}

.cpb-select :deep(.el-select__wrapper) {
  height: 36px !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 4px !important;
}

.cpb-select :deep(.el-select__placeholder),
.cpb-select :deep(.el-select__selected-item) {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #1F2937 !important;
}

/* Primary line: bigger select */
.cpb-line--primary .cpb-select :deep(.el-select__wrapper) {
  height: 38px !important;
}

.cpb-opt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
}
.cpb-opt-name  { font-weight: 600; font-size: 13px; color: #1F2937; }
.cpb-opt-price { font-size: 11px; font-weight: 700; color: #2563EB; margin-left: 8px; }

/* ─── Quantity ─── */
.cpb-qty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.cpb-qty-label {
  font-size: 9px;
  font-weight: 700;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  line-height: 1;
}

.cpb-qty-ctrl {
  display: flex;
  align-items: center;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.cpb-qty-btn {
  width: 24px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #6B7280;
  background: #F9FAFB;
  border: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  line-height: 1;
}

.cpb-qty-btn:hover { background: #E5E7EB; color: #1F2937; }
.cpb-qty-btn:active { background: #D1D5DB; }

.cpb-qty-input {
  width: 36px;
  height: 28px;
  text-align: center;
  border: none;
  font-size: 13px;
  font-weight: 700;
  color: #1F2937;
  background: #fff;
  outline: none;
  padding: 0;
  -moz-appearance: textfield;
}
.cpb-qty-input::-webkit-outer-spin-button,
.cpb-qty-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }

/* ─── Price badge ─── */
.cpb-price-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 7px;
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  font-size: 11.5px;
  font-weight: 800;
  color: #1D4ED8;
  white-space: nowrap;
}

/* ─── Remove ─── */
.cpb-remove-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 7px;
  border: 1px solid #FECACA;
  background: #FFF5F5;
  color: #EF4444;
  cursor: pointer;
  flex-shrink: 0;
  font-size: 12px;
  transition: all 0.15s;
}
.cpb-remove-btn:hover { background: #FEE2E2; border-color: #FCA5A5; }

/* ─── Attributes grid ─── */
.cpb-attrs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding-top: 4px;
  border-top: 1px dashed #E5E7EB;
}

.cpb-attr-card {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #F9FAFB;
  border: 1px solid #F3F4F6;
}

.cpb-attr-label {
  font-size: 10.5px;
  font-weight: 700;
  color: #6B7280;
  line-height: 1;
}

.cpb-chips { display: flex; flex-wrap: wrap; gap: 6px; }

.cpb-chip {
  padding: 4px 12px;
  border-radius: 7px;
  border: 1px solid #E5E7EB;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s;
}
.cpb-chip:hover { border-color: #93C5FD; color: #1D4ED8; }
.cpb-chip--active { background: #2563EB; border-color: #2563EB; color: #fff; }

.cpb-dims { display: flex; align-items: center; gap: 6px; }
.cpb-dims-sep { font-size: 14px; color: #CBD5E1; font-weight: 400; }
.cpb-dims-unit { font-size: 11px; font-weight: 700; color: #9CA3AF; }

/* ─── Add line ─── */
.cpb-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1px dashed #93C5FD;
  background: transparent;
  color: #3B82F6;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  align-self: flex-start;
}
.cpb-add-btn:hover { background: #EFF6FF; border-color: #3B82F6; }

/* ─── Bottom section ─── */
.cpb-bottom {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 4px;
  border-top: 1px solid #F3F4F6;
}

.cpb-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cpb-field-label {
  font-size: 10.5px;
  font-weight: 700;
  color: #6B7280;
}

.cpb-field :deep(.el-textarea__inner) {
  border-radius: 10px !important;
  font-size: 13px !important;
  resize: vertical;
}

/* ─── Reference button ─── */
.cpb-ref-section {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.cpb-ref-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 14px;
  border-radius: 9px;
  border: 1px solid #E5E7EB;
  background: #fff;
  color: #6B7280;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  align-self: flex-start;
}

.cpb-ref-btn:hover {
  border-color: #93C5FD;
  color: #2563EB;
  background: #F0F7FF;
}

.cpb-ref-btn--active {
  border-color: #93C5FD;
  color: #1D4ED8;
  background: #EFF6FF;
}

.cpb-ref-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  flex-shrink: 0;
}

.cpb-ref-chevron {
  font-size: 11px;
  color: #9CA3AF;
  transition: transform 0.25s ease;
}
.cpb-ref-chevron--open { transform: rotate(180deg); }

/* ─── Reference panel ─── */
.cpb-ref-panel {
  margin-top: 8px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  overflow: hidden;
  background: #FAFAFA;
}

/* ─── Transitions ─── */
.cpb-ref-slide-enter-active, .cpb-ref-slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.cpb-ref-slide-enter-from, .cpb-ref-slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}
.cpb-ref-slide-enter-to, .cpb-ref-slide-leave-from {
  opacity: 1;
  max-height: 400px;
  margin-top: 8px;
}

.cpb-attrs-enter-active, .cpb-attrs-leave-active { transition: all 0.2s ease; }
.cpb-attrs-enter-from, .cpb-attrs-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
