<template>
  <div class="procurement-tab">
    <el-row :gutter="40">
      <!-- === LEFT COLUMN: Stock Management === -->
      <el-col :span="12">
        <div class="section-title">
          <el-icon><Warning /></el-icon>
          <h3>Управління запасами</h3>
        </div>
        <p class="section-desc">Налаштуйте автоматичний контроль залишків для цього матеріалу.</p>

        <div class="config-grid shadow-sm">
          <div class="config-item">
            <div class="label-box">
              <span class="label">Мінімальний залишок</span>
              <el-tooltip content="Коли залишок опуститься нижче, система повідомить про необхідність закупівлі.">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <el-input-number 
              v-model="modelValue.min_stock" 
              :precision="3" 
              :step="1" 
              class="w-full"
              controls-position="right"
            />
            <span class="unit-label">{{ modelValue.unit_of_measure }}</span>
          </div>

          <div class="config-item">
            <div class="label-box">
              <span class="label">Оптимальний залишок</span>
              <el-tooltip content="Кількість, до якої система буде пропонувати поповнити запас.">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <el-input-number 
              v-model="modelValue.optimal_stock" 
              :precision="3" 
              :step="1" 
              class="w-full"
              controls-position="right"
            />
            <span class="unit-label">{{ modelValue.unit_of_measure }}</span>
          </div>
        </div>
      </el-col>

      <!-- === RIGHT COLUMN: Logistics === -->
      <el-col :span="12">
        <div class="section-title">
          <el-icon><Van /></el-icon>
          <h3>Логістика та Постачальник</h3>
        </div>
        <p class="section-desc">Параметри закупівлі за замовчуванням для швидкого оформлення замовлень.</p>

        <div class="config-grid shadow-sm">
          <div class="config-item full-width">
            <div class="label-box">
              <span class="label">Основний постачальник</span>
            </div>
            <el-select 
              v-model="modelValue.default_supplier_id" 
              placeholder="Оберіть постачальника"
              clearable
              filterable
              class="w-full"
            >
              <el-option
                v-for="s in suppliers"
                :key="s.id"
                :label="s.name"
                :value="s.id"
              />
            </el-select>
          </div>

          <div class="config-item">
            <div class="label-box">
              <span class="label">Термін доставки</span>
              <el-tooltip content="Середня кількість днів від замовлення до отримання товару.">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <el-input-number 
              v-model="modelValue.delivery_days" 
              :min="0" 
              :max="365"
              class="w-full"
              controls-position="right"
            />
            <span class="unit-label">днів</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <div class="info-banner mt-8">
      <el-alert
        title="Як це працює"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #default>
          <p class="text-xs leading-relaxed opacity-80">
            Система автоматично аналізує залишки на всіх складах. Якщо <b>Поточний залишок &lt; Мінімум</b>, 
            позиція з'явиться в Дашборді закупівель. Замовлення буде запропоновано на кількість 
            <b>(Оптимальний - Поточний)</b>.
          </p>
        </template>
      </el-alert>
    </div>

    <div class="supplier-links-panel mt-8">
      <div class="supplier-links-head">
        <div>
          <div class="section-title compact">
            <el-icon><Link /></el-icon>
            <h3>Постачальники товару / Посилання для закупівлі</h3>
          </div>
          <p class="section-desc">Додайте швидкі посилання на сторінку товару, кабінет або форму замовлення постачальника.</p>
        </div>
        <el-button type="primary" plain :icon="Plus" @click="addSupplierLink">Додати постачальника</el-button>
      </div>

      <div v-if="supplierLinks.length" class="supplier-link-list">
        <div
          v-for="(link, index) in supplierLinks"
          :key="`${link.supplier_id || 'supplier'}-${index}`"
          class="supplier-link-card"
          :class="{ inactive: !link.is_active, default: link.is_default_supplier }"
        >
          <div class="supplier-link-grid">
            <div class="config-item">
              <div class="label-box"><span class="label">Постачальник</span></div>
              <el-select
                v-model="link.supplier_id"
                filterable
                clearable
                placeholder="Оберіть постачальника"
                class="w-full"
                @change="syncSupplierName(link)"
              >
                <el-option
                  v-for="s in suppliers"
                  :key="s.id"
                  :label="s.name"
                  :value="s.id"
                />
              </el-select>
            </div>
            <div class="config-item">
              <div class="label-box"><span class="label">Артикул постачальника</span></div>
              <el-input v-model="link.supplier_sku" placeholder="SKU / код у постачальника" />
            </div>
            <div class="config-item">
              <div class="label-box"><span class="label">Тип посилання</span></div>
              <el-select v-model="link.url_type" class="w-full">
                <el-option v-for="type in urlTypes" :key="type" :label="type" :value="type" />
              </el-select>
            </div>
            <div class="config-item supplier-url-field">
              <div class="label-box"><span class="label">URL для замовлення</span></div>
              <el-input v-model="link.order_url" placeholder="https://..." />
            </div>
            <div class="config-item full-width">
              <div class="label-box"><span class="label">Нотатка</span></div>
              <el-input v-model="link.note" type="textarea" :rows="2" placeholder="Умови, мінімальна партія, контакт, нюанси замовлення..." />
            </div>
          </div>

          <div class="supplier-link-actions">
            <el-switch v-model="link.is_active" active-text="Активно" />
            <el-switch
              :model-value="Boolean(link.is_default_supplier)"
              active-text="Основний"
              @change="setDefaultSupplier(index, $event)"
            />
            <el-button v-if="link.order_url" :icon="TopRight" @click="openSupplierUrl(link)">Відкрити</el-button>
            <el-button type="danger" plain :icon="Delete" @click="removeSupplierLink(index)">Видалити</el-button>
          </div>
        </div>
      </div>

      <div v-else class="supplier-links-empty">
        <el-empty description="Посилання для закупівлі ще не додані">
          <el-button type="primary" plain :icon="Plus" @click="addSupplierLink">Додати постачальника</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Warning, Van, InfoFilled, Link, Plus, Delete, TopRight } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  suppliers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const urlTypes = [
  'Сторінка товару',
  'Кабінет замовлення',
  'Кабінет розкрою',
  'Форма замовлення',
  'Прайс / каталог',
  'Інше'
]

const supplierLinks = computed(() => props.modelValue.supplier_links || [])

const ensureSupplierLinks = () => {
  if (!Array.isArray(props.modelValue.supplier_links)) props.modelValue.supplier_links = []
}

const addSupplierLink = () => {
  ensureSupplierLinks()
  props.modelValue.supplier_links.push({
    supplier_id: null,
    supplier_name: '',
    supplier_sku: '',
    order_url: '',
    url_type: 'Сторінка товару',
    note: '',
    is_active: true,
    is_default_supplier: props.modelValue.supplier_links.length === 0
  })
}

const removeSupplierLink = (index) => {
  props.modelValue.supplier_links.splice(index, 1)
}

const syncSupplierName = (link) => {
  const supplier = props.suppliers.find(s => s.id === link.supplier_id)
  link.supplier_name = supplier?.name || ''
}

const setDefaultSupplier = (index, value) => {
  ensureSupplierLinks()
  props.modelValue.supplier_links.forEach((link, i) => {
    link.is_default_supplier = Boolean(value) && i === index
  })
  if (value) {
    const link = props.modelValue.supplier_links[index]
    props.modelValue.default_supplier_id = link?.supplier_id || props.modelValue.default_supplier_id
  }
}

const openSupplierUrl = (link) => {
  if (!link?.order_url) return
  window.open(link.order_url, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.procurement-tab {
  padding: 0;
  background: transparent;
  min-height: 400px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.section-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.section-title .el-icon {
  font-size: 18px;
  color: #6366f1;
}

.section-desc {
  margin: 0 0 20px 0;
  font-size: 13px;
  color: #64748b;
}

.config-grid {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eef2f7;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.config-item.full-width {
  grid-column: span 2;
}

.label-box {
  display: flex;
  align-items: center;
  gap: 6px;
}

.label {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.label-box .el-icon {
  font-size: 12px;
  color: #cbd5e1;
  cursor: help;
}

.unit-label {
  position: absolute;
  right: 40px;
  bottom: 8px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
  pointer-events: none;
}

.w-full { width: 100%; }
.mt-8 { margin-top: 2rem; }
.shadow-sm { box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }

.section-title.compact { margin-bottom: 4px; }

.supplier-links-panel {
  background: #ffffff;
  border: 1px solid #E6ECF3;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 12px 28px rgba(16, 24, 40, 0.06);
}

.supplier-links-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.supplier-link-list {
  display: grid;
  gap: 12px;
}

.supplier-link-card {
  border: 1px solid #E6ECF3;
  border-radius: 14px;
  padding: 16px;
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.04);
}

.supplier-link-card.default {
  border-color: #A5B4FC;
  box-shadow: inset 3px 0 0 #6366F1, 0 4px 12px rgba(16, 24, 40, 0.04);
}

.supplier-link-card.inactive {
  opacity: .65;
}

.supplier-link-grid {
  display: grid;
  grid-template-columns: 1.1fr .9fr .8fr 1.4fr;
  gap: 14px;
}

.supplier-url-field { min-width: 0; }

.supplier-link-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #EEF2F7;
}

.supplier-links-empty {
  border: 1px dashed #CBD5E1;
  border-radius: 14px;
  background: #F8FAFC;
}

@media (max-width: 1200px) {
  .supplier-link-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 720px) {
  .supplier-links-head,
  .supplier-link-actions { flex-direction: column; align-items: stretch; }
  .supplier-link-grid { grid-template-columns: 1fr; }
}

:deep(.el-input-number.is-controls-right .el-input__wrapper) {
  padding-left: 12px;
  padding-right: 40px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: left;
  font-weight: 600;
  color: #334155;
}
</style>
