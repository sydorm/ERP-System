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
            <div style="display: flex; gap: 8px; align-items: center; width: 100%;">
              <el-input-number
                v-model="modelValue.cost"
                :precision="2"
                :step="1"
                controls-position="right"
                style="flex: 1"
                class="styled-number"
              />
              <el-tooltip content="Розрахувати собівартість (BOM + Етапи)" placement="top" v-if="modelValue.id">
                <el-button
                  type="primary"
                  plain
                  :icon="Refresh"
                  :loading="calculatingCost"
                  @click="calculateCost"
                />
              </el-tooltip>
            </div>
            <!-- Cost source badge -->
            <div v-if="modelValue.cost_source" class="cost-source-badge">
              <el-icon><DocumentChecked /></el-icon>
              {{ modelValue.cost_source }}
            </div>
            <p v-else-if="modelValue.id" class="cost-hint">
              <el-icon><InfoFilled /></el-icon> Розрахунок собівартості включає матеріали (BOM) та виробничі етапи.
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
            <span class="stats-value">{{ ((modelValue.price || 0) - (modelValue.cost || 0)).toFixed(2) }} {{ modelValue.currency }}</span>
          </div>

          <!-- Cost history -->
          <div class="cost-history-block" v-if="modelValue.id">
            <div class="cost-history-header">
              <span class="cost-history-title">Історія собівартості</span>
              <el-tag v-if="costMethod" size="small" effect="plain" type="info">{{ METHOD_LABELS[costMethod] || costMethod }}</el-tag>
            </div>
            <div v-if="historyLoading" class="cost-history-loading">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="costHistory.length === 0" class="cost-history-empty">
              <el-icon><Clock /></el-icon>
              Ще не було надходжень
            </div>
            <div v-else class="cost-history-list">
              <div
                v-for="row in costHistory"
                :key="row.id"
                class="cost-history-row"
              >
                <div class="ch-top">
                  <span class="ch-doc">{{ row.document_number }}</span>
                  <span class="ch-date">{{ formatDate(row.created_at) }}</span>
                </div>
                <div class="ch-details">
                  <span class="ch-supplier" v-if="row.supplier_name">{{ row.supplier_name }}</span>
                  <span class="ch-prices">
                    {{ row.incoming_qty }} × {{ row.incoming_price.toFixed(2) }} грн
                  </span>
                  <span class="ch-arrow">→</span>
                  <span class="ch-new-cost">{{ row.new_cost.toFixed(2) }} грн</span>
                  <span v-if="row.old_cost !== null" class="ch-old-cost">(було {{ row.old_cost?.toFixed(2) }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { InfoFilled, Refresh, DocumentChecked, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: { type: Object, required: true },
  currencyOptions: { type: Array, default: () => [] },
  hasSpecification: { type: Boolean, default: false }
})

const calculatingCost = ref(false)
const costHistory = ref([])
const historyLoading = ref(false)
const costMethod = ref(null)

const METHOD_LABELS = {
  last_price: 'Остання ціна',
  weighted_average: 'Середньозважена',
  none: 'Не оновлювати',
}

const fetchCostHistory = async () => {
  if (!props.modelValue.id) return
  historyLoading.value = true
  try {
    const res = await api.get(`/api/v1/products/${props.modelValue.id}/cost-history`)
    costHistory.value = res.data
  } catch { /* non-critical */ }
  finally { historyLoading.value = false }
}

const fetchCostMethod = async () => {
  try {
    const res = await api.get('/api/v1/companies/default')
    costMethod.value = res.data?.cost_method || 'last_price'
  } catch { /* non-critical */ }
}

onMounted(() => {
  fetchCostHistory()
  fetchCostMethod()
})

watch(() => props.modelValue.id, (id) => {
  if (id) fetchCostHistory()
})

const calculateCost = async () => {
  if (!props.modelValue.id) return
  calculatingCost.value = true
  try {
    const res = await api.get(`/api/v1/products/${props.modelValue.id}/calculate-cost`)
    if (res.data.detail) {
      ElMessage.warning(res.data.detail)
    } else {
      props.modelValue.cost = res.data.cost
      ElMessage.success(`Собівартість розраховано: ${res.data.cost} ${props.modelValue.currency}`)
    }
  } catch {
    ElMessage.error('Помилка розрахунку собівартості')
  } finally {
    calculatingCost.value = false
  }
}

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('uk-UA')
}

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
  padding: 16px 24px;
}

.section-divider {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 12px;
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
  margin-bottom: 12px;
}

.cost-source-badge {
  margin-top: 6px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #16a34a;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 3px 8px;
}

.cost-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

.markup-panel {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  margin-top: 4px;
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
.text-danger  { color: #f43f5e; }
.markup-progress { margin-top: 8px; }

/* === VISUALS === */
.pricing-visuals {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

/* === COST HISTORY === */
.cost-history-block {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
}
.cost-history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.cost-history-title {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.cost-history-loading { padding: 4px 0; }
.cost-history-empty {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #94a3b8;
  padding: 8px 0;
}
.cost-history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 260px;
  overflow-y: auto;
}
.cost-history-row {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 10px;
}
.cost-history-row:last-child { border-bottom: none; padding-bottom: 0; }

.ch-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.ch-doc {
  font-size: 13px;
  font-weight: 600;
  color: #3b82f6;
}
.ch-date {
  font-size: 12px;
  color: #94a3b8;
}
.ch-details {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: #475569;
}
.ch-supplier {
  color: #64748b;
  font-weight: 500;
  background: #f1f5f9;
  border-radius: 4px;
  padding: 1px 6px;
}
.ch-arrow { color: #94a3b8; }
.ch-new-cost {
  font-weight: 700;
  color: #16a34a;
}
.ch-old-cost { color: #94a3b8; }
</style>
