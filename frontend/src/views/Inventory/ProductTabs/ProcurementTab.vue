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
  </div>
</template>

<script setup>
import { Warning, Van, InfoFilled } from '@element-plus/icons-vue'

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
</script>

<style scoped>
.procurement-tab {
  padding: 32px;
  background: #fcfdfe;
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
