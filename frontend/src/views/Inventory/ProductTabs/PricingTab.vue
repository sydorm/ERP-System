<template>
  <div class="pricing-tab-content">
    <div class="section-divider">Фінансова інформація</div>
    
    <el-row :gutter="60">
      <el-col :span="12">
        <el-form label-position="top" class="pricing-form">
          <el-row :gutter="16">
            <el-col :span="16">
              <el-form-item>
                <template #label><span class="field-label">Ціна продажу</span></template>
                <el-input-number 
                  v-model="modelValue.price" 
                  :precision="2" 
                  :step="1" 
                  controls-position="right"
                  style="width: 100%" 
                  class="styled-number"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label><span class="field-label">Валюта</span></template>
                <el-select v-model="modelValue.currency" style="width: 100%" class="styled-select">
                  <el-option v-for="c in currencyOptions" :key="c.code" :label="c.code" :value="c.code" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <template #label>
              <span class="field-label">Собівартість</span>
            </template>
            <el-input-number 
              v-model="modelValue.cost" 
              :precision="2" 
              :step="1" 
              controls-position="right"
              style="width: 100%" 
              class="styled-number"
            />
            <p v-if="hasSpecification" class="cost-hint">
              <el-icon><InfoFilled /></el-icon> Розраховується за специфікацією (BOM)
            </p>
          </el-form-item>

          <div class="markup-panel">
            <span class="markup-label">Рентабельність (Націнка)</span>
            <div class="markup-value-row">
              <span class="markup-percentage" :class="markupClass">{{ calculateMarkup }}%</span>
              <el-tag :type="markupTagType" size="small" effect="light" round>
                {{ markupStatusText }}
              </el-tag>
            </div>
            <el-progress 
              :percentage="Math.min(100, Math.max(0, calculateMarkup))" 
              :status="calculateMarkup < 15 ? 'exception' : (calculateMarkup < 30 ? 'warning' : 'success')"
              :show-text="false"
              class="markup-progress"
            />
          </div>
        </el-form>
      </el-col>
      
      <el-col :span="12">
        <div class="pricing-visuals">
          <div class="stats-mini-card">
            <span class="stats-label">Прибуток з одиниці</span>
            <span class="stats-value">{{ (modelValue.price - modelValue.cost).toFixed(2) }} {{ modelValue.currency }}</span>
          </div>
          <div class="chart-area">
            <el-empty description="Тут буде графік історії цін" :image-size="80" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  currencyOptions: { type: Array, default: () => [] },
  hasSpecification: { type: Boolean, default: false }
})

const calculateMarkup = computed(() => {
  if (!props.modelValue.price || !props.modelValue.cost || props.modelValue.cost === 0) return 0
  return (((props.modelValue.price - props.modelValue.cost) / props.modelValue.cost) * 100).toFixed(1)
})

const markupClass = computed(() => {
  const m = parseFloat(calculateMarkup.value)
  if (m >= 30) return 'text-success'
  if (m >= 15) return 'text-warning'
  return 'text-danger'
})

const markupTagType = computed(() => {
  const m = parseFloat(calculateMarkup.value)
  if (m >= 30) return 'success'
  if (m >= 15) return 'warning'
  return 'danger'
})

const markupStatusText = computed(() => {
  const m = parseFloat(calculateMarkup.value)
  if (m >= 30) return 'Висока маржа'
  if (m >= 15) return 'Нормальна'
  if (m <= 0) return 'Збиток'
  return 'Низька маржа'
})
</script>

<style scoped>
.pricing-tab-content {
  padding: 32px;
}

/* === SECTION DIVIDERS === */
.section-divider {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #f1f5f9;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.pricing-form :deep(.el-input__wrapper),
.pricing-form :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 10px !important;
  background-color: #f8fafc !important;
  padding: 8px 12px !important;
  transition: all 0.2s ease;
}

.pricing-form :deep(.el-input__wrapper:hover),
.pricing-form :deep(.el-select__wrapper:hover) {
  border-color: #cbd5e1 !important;
  background-color: #f1f5f9 !important;
}

.pricing-form :deep(.el-input__wrapper.is-focus),
.pricing-form :deep(.el-select__wrapper.is-focused) {
  border-color: #6366f1 !important;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
}

.pricing-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.cost-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* === MARKUP PANEL === */
.markup-panel {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  margin-top: 8px;
}

.markup-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  display: block;
  margin-bottom: 8px;
}

.markup-value-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
}

.markup-percentage {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.text-success { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-danger { color: #f43f5e; }

.markup-progress {
  margin-top: 8px;
}

/* === VISUALS === */
.pricing-visuals {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-mini-card {
  background: #ffffff;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.stats-label {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stats-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.chart-area {
  height: 240px;
  background: #fdfdfd;
  border: 1px dashed #e2e8f0;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
