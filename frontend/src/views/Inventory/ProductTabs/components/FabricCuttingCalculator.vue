<template>
  <div class="fc-calc">
    <div class="fc-header">
      <span class="fc-icon">🧵</span>
      <span class="fc-title">Тканина / розкрій</span>
    </div>

    <el-form label-position="top" size="small" class="fc-form">

      <!-- ── Dimension sources ────────────────────────────────────────────── -->
      <div class="fc-section-title">Джерело розмірів деталі</div>
      <div class="fc-row-2">

        <el-form-item label="Ширина деталі — джерело">
          <el-select v-model="cfg.baseWidthSource" class="w-full" @change="clearPreview">
            <el-option label="Параметр товару: ширина (width_mm)" value="width_mm" />
            <el-option label="Параметр товару: довжина (length_mm)" value="length_mm" />
            <el-option label="Параметр товару: висота (height_mm)" value="height_mm" />
            <el-option label="Характеристика замовлення" value="characteristic" />
            <el-option label="Ручне значення" value="manual" />
          </el-select>
        </el-form-item>

        <el-form-item label="Довжина деталі — джерело">
          <el-select v-model="cfg.baseLengthSource" class="w-full" @change="clearPreview">
            <el-option label="Параметр товару: ширина (width_mm)" value="width_mm" />
            <el-option label="Параметр товару: довжина (length_mm)" value="length_mm" />
            <el-option label="Параметр товару: висота (height_mm)" value="height_mm" />
            <el-option label="Характеристика замовлення" value="characteristic" />
            <el-option label="Ручне значення" value="manual" />
          </el-select>
        </el-form-item>
      </div>

      <!-- Char names -->
      <div v-if="cfg.baseWidthSource === 'characteristic' || cfg.baseLengthSource === 'characteristic'" class="fc-row-2">
        <el-form-item v-if="cfg.baseWidthSource === 'characteristic'" label="Характеристика для ширини">
          <el-select v-model="cfg.baseWidthCharName" class="w-full" filterable allow-create @change="clearPreview">
            <el-option v-for="a in productAttributes" :key="a.id" :label="a.name" :value="a.name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="cfg.baseLengthSource === 'characteristic'" label="Характеристика для довжини">
          <el-select v-model="cfg.baseLengthCharName" class="w-full" filterable allow-create @change="clearPreview">
            <el-option v-for="a in productAttributes" :key="a.id" :label="a.name" :value="a.name" />
          </el-select>
        </el-form-item>
      </div>

      <!-- Manual values -->
      <div v-if="cfg.baseWidthSource === 'manual' || cfg.baseLengthSource === 'manual'" class="fc-row-2">
        <el-form-item v-if="cfg.baseWidthSource === 'manual'" label="Ширина деталі, мм">
          <el-input-number v-model="cfg.manualBaseWidthMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
        <el-form-item v-if="cfg.baseLengthSource === 'manual'" label="Довжина деталі, мм">
          <el-input-number v-model="cfg.manualBaseLengthMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
      </div>

      <!-- Dimension source preview (from product dims) -->
      <div v-if="resolvedPreviewDims" class="fc-dim-preview">
        <span>Поточні розміри товару:</span>
        <span class="fc-dim-badge">Ш {{ productDimensions.width_mm || 0 }} мм</span>
        <span class="fc-dim-badge">Д {{ productDimensions.length_mm || 0 }} мм</span>
        <span class="fc-dim-badge">В {{ productDimensions.height_mm || 0 }} мм</span>
      </div>

      <!-- ── Allowances ───────────────────────────────────────────────────── -->
      <div class="fc-section-title mt-3">Припуски на оббивку, мм</div>
      <div class="fc-allowances">
        <div></div>
        <el-form-item label="Зверху">
          <el-input-number v-model="cfg.allowanceTopMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
        <div></div>

        <el-form-item label="Зліва">
          <el-input-number v-model="cfg.allowanceLeftMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
        <div class="fc-allowances-center">деталь</div>
        <el-form-item label="Справа">
          <el-input-number v-model="cfg.allowanceRightMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>

        <div></div>
        <el-form-item label="Знизу">
          <el-input-number v-model="cfg.allowanceBottomMm" :min="0" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
        <div></div>
      </div>

      <!-- ── Roll & count ─────────────────────────────────────────────────── -->
      <div class="fc-section-title mt-3">Параметри рулону</div>
      <div class="fc-row-2">
        <el-form-item label="Ширина рулона, мм">
          <el-input-number v-model="cfg.rollWidthMm" :min="0" :precision="0" class="w-full"
            placeholder="напр. 1400" @change="clearPreview" />
          <div class="fc-field-hint">Стандарт тканин: 1400 мм</div>
        </el-form-item>
        <el-form-item label="Кількість деталей">
          <el-input-number v-model="cfg.pieceCount" :min="1" :precision="0" class="w-full" @change="clearPreview" />
        </el-form-item>
      </div>

      <!-- ── Rotation & nap ──────────────────────────────────────────────── -->
      <div class="fc-section-title mt-3">Поворот та ворс</div>
      <div class="fc-row-2 fc-checkboxes">
        <el-checkbox v-model="cfg.allowRotation" @change="clearPreview">
          Дозволити поворот деталі
        </el-checkbox>
        <el-checkbox v-model="cfg.respectNapDirection" @change="clearPreview">
          Враховувати напрямок ворсу / малюнка
        </el-checkbox>
      </div>
      <el-alert
        v-if="cfg.respectNapDirection && cfg.allowRotation"
        title="Поворот заборонено — напрямок ворсу активовано"
        type="warning" :closable="false" size="small" class="mt-1"
      />

      <!-- ── Waste ────────────────────────────────────────────────────────── -->
      <div class="fc-row-2 mt-3">
        <el-form-item label="Відходи, %">
          <el-input-number v-model="cfg.wastePercent" :min="0" :max="100" :precision="1" class="w-full" @change="clearPreview" />
          <div class="fc-field-hint">Зберігається як {{ (cfg.wastePercent / 100).toFixed(4) }} у форматі системи</div>
        </el-form-item>
        <div></div>
      </div>

      <!-- ── Material characteristic ─────────────────────────────────────── -->
      <div class="fc-section-title mt-3">Характеристика матеріалу (для перевірки залишку)</div>
      <div class="fc-row-2">
        <el-form-item label="Джерело кольору/варіанту">
          <el-select v-model="cfg.materialCharacteristicSource" class="w-full" @change="clearPreview">
            <el-option label="Ручне значення" value="manual" />
            <el-option label="З характеристики замовлення" value="order_characteristic" />
          </el-select>
        </el-form-item>
        <el-form-item label="Назва характеристики">
          <el-select v-model="cfg.materialCharacteristicName" class="w-full" filterable allow-create @change="clearPreview">
            <el-option v-for="a in productAttributes" :key="a.id" :label="a.name" :value="a.name" />
          </el-select>
          <div class="fc-field-hint">Напр.: "Колір тканини" або конкретне значення</div>
        </el-form-item>
      </div>

    </el-form>

    <!-- ── Preview button ─────────────────────────────────────────────────── -->
    <div class="fc-preview-btn-row">
      <el-button type="primary" :loading="previewLoading" @click="runPreview" :icon="Search">
        Попередній розрахунок
      </el-button>
    </div>

    <!-- ── Preview results ────────────────────────────────────────────────── -->
    <div v-if="previewResult" class="fc-result-box">

      <!-- Errors -->
      <div v-if="previewResult.errors.length" class="fc-result-errors">
        <div v-for="e in previewResult.errors" :key="e" class="fc-error-line">❌ {{ e }}</div>
      </div>

      <!-- Success -->
      <template v-if="previewResult.valid">
        <div class="fc-result-main">
          <span class="fc-result-label">Потрібно тканини:</span>
          <span class="fc-result-value">{{ previewResult.finalQty.toFixed(3) }} м.п.</span>
        </div>
        <div class="fc-result-meta">
          Заготовка: <strong>{{ previewResult.meta.cutWidthMm }} × {{ previewResult.meta.cutLengthMm }} мм</strong>
          · В ряд: <strong>{{ previewResult.meta.itemsPerRow }} шт</strong>
          · Рядів: <strong>{{ previewResult.meta.rowsNeeded }}</strong>
        </div>

        <!-- Stock availability -->
        <div class="fc-stock-row" v-if="stockInfo !== null">
          <template v-if="stockInfo.error">
            <span class="fc-stock-warn">⚠ {{ stockInfo.error }}</span>
          </template>
          <template v-else>
            <span>Залишок на складі: <strong>{{ stockInfo.available.toFixed(3) }} м.п.</strong></span>
            <span v-if="stockInfo.available >= previewResult.finalQty" class="fc-stock-ok">
              ✅ Вистачає (після використання: ≈ {{ (stockInfo.available - previewResult.finalQty).toFixed(3) }} м.п.)
            </span>
            <span v-else class="fc-stock-err">
              ❌ Не вистачає {{ (previewResult.finalQty - stockInfo.available).toFixed(3) }} м.п.
            </span>
          </template>
        </div>
        <div v-else class="fc-stock-warn">
          ⚠ Залишок не перевірено: не вказаний компонент або характеристика кольору.
        </div>

        <!-- Remnant forecast -->
        <div v-if="previewResult.meta.remnantForecast" class="fc-remnant">
          Можливий залишок після розкрою: <strong>{{ previewResult.meta.remnantForecast }}</strong>
          <span class="fc-remnant-note">(прогноз — автоматичне списання не виконується)</span>
        </div>

        <!-- Warnings -->
        <div v-for="w in previewResult.warnings" :key="w" class="fc-warn-line">⚠ {{ w }}</div>

        <!-- Breakdown toggle -->
        <div class="fc-breakdown-toggle" @click="showBreakdown = !showBreakdown">
          {{ showBreakdown ? '▲ Сховати розшифровку' : '▼ Показати розшифровку' }}
        </div>
        <div v-if="showBreakdown" class="fc-breakdown-body">
          <div v-for="(line, i) in previewResult.breakdownLines" :key="i" class="fc-bd-line">{{ line }}</div>
        </div>
      </template>

    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { computeFabricCutting } from '@/composables/useFabricCuttingCalc'
import api from '@/api'

const props = defineProps({
  config:            { type: Object, required: true },
  componentId:       { type: String, default: null },
  productDimensions: { type: Object, default: () => ({}) },
  productAttributes: { type: Array,  default: () => [] },
})

// Direct mutation of the config object (consistent with SpecificationTab pattern)
const cfg = props.config

const previewResult  = ref(null)
const previewLoading = ref(false)
const stockInfo      = ref(null)
const showBreakdown  = ref(false)

const clearPreview = () => { previewResult.value = null; stockInfo.value = null }

const resolvedPreviewDims = computed(() =>
  props.productDimensions.width_mm != null ||
  props.productDimensions.length_mm != null ||
  props.productDimensions.height_mm != null
)

// Build dims object for the calculator (includes product physical dims)
const buildDims = () => ({
  width_mm:  Number(props.productDimensions.width_mm)  || 0,
  length_mm: Number(props.productDimensions.length_mm) || 0,
  height_mm: Number(props.productDimensions.height_mm) || 0,
  // characteristic values would come from order context; here we use 0 as fallback
})

const runPreview = async () => {
  previewLoading.value = true
  showBreakdown.value  = false
  stockInfo.value      = null
  try {
    const dims   = buildDims()
    const result = computeFabricCutting(cfg, dims, false)
    previewResult.value = result

    // ── Stock check ──────────────────────────────────────────────────────
    if (result.valid && props.componentId) {
      try {
        const res = await api.get(`/api/v1/products/${props.componentId}/stock`)
        // stock endpoint returns { total, by_variant, ... } or number — handle both
        const data = res.data
        let available = 0
        if (typeof data === 'number') {
          available = data
        } else if (data && typeof data.total !== 'undefined') {
          available = Number(data.total) || 0
        } else if (data && typeof data.balance !== 'undefined') {
          available = Number(data.balance) || 0
        } else if (typeof data === 'object') {
          // sum all variant balances
          available = Object.values(data).reduce((s, v) => s + (Number(v) || 0), 0)
        }
        if (!cfg.materialCharacteristicName) {
          stockInfo.value = { error: 'Не вибрано характеристику кольору — залишок показано загальний.' , available }
        } else {
          stockInfo.value = { available }
        }
      } catch {
        stockInfo.value = { error: 'Не вдалося отримати залишок зі складу.' }
      }
    }
  } finally {
    previewLoading.value = false
  }
}
</script>

<style scoped>
.fc-calc { display: flex; flex-direction: column; gap: 0; }

.fc-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 0 6px;
  border-bottom: 2px solid #e8f5e9;
  margin-bottom: 12px;
}
.fc-icon  { font-size: 20px; }
.fc-title { font-size: 14px; font-weight: 700; color: #2e7d32; }

.fc-section-title {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .05em; color: #78909c; margin-bottom: 6px;
}

.fc-form { width: 100%; }

.fc-row-2 {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 4px;
}
.fc-checkboxes { align-items: center; padding: 4px 0; }

/* Allowances compass layout */
.fc-allowances {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 6px;
  margin-bottom: 4px;
}
.fc-allowances-center {
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: #90a4ae; border: 1px dashed #cfd8dc; border-radius: 6px;
}

.fc-field-hint { font-size: 10px; color: #90a4ae; margin-top: 2px; }

.fc-dim-preview {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  font-size: 11px; color: #607d8b; margin-bottom: 4px;
}
.fc-dim-badge {
  background: #e3f2fd; color: #1565c0; border-radius: 4px;
  padding: 1px 6px; font-weight: 600;
}

.fc-preview-btn-row { margin: 14px 0 0; }

/* Result box */
.fc-result-box {
  margin-top: 12px;
  background: #f9fbe7;
  border: 1px solid #c5e1a5;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.fc-result-errors { display: flex; flex-direction: column; gap: 4px; }
.fc-error-line { color: #c62828; font-size: 13px; }

.fc-result-main {
  display: flex; align-items: baseline; gap: 10px;
}
.fc-result-label { font-size: 13px; color: #555; }
.fc-result-value { font-size: 22px; font-weight: 700; color: #2e7d32; }

.fc-result-meta { font-size: 12px; color: #607d8b; }

.fc-stock-row { font-size: 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.fc-stock-ok  { color: #2e7d32; font-weight: 600; }
.fc-stock-err { color: #c62828; font-weight: 600; }
.fc-stock-warn { color: #e65100; font-size: 12px; }

.fc-remnant { font-size: 12px; color: #37474f; }
.fc-remnant-note { color: #90a4ae; font-style: italic; margin-left: 4px; }

.fc-warn-line { font-size: 12px; color: #e65100; }

.fc-breakdown-toggle {
  font-size: 11px; color: #1565c0; cursor: pointer;
  user-select: none; margin-top: 2px;
}
.fc-breakdown-toggle:hover { text-decoration: underline; }

.fc-breakdown-body {
  background: #f5f5f5; border-radius: 6px;
  padding: 8px 10px; margin-top: 4px;
}
.fc-bd-line { font-size: 11px; color: #37474f; font-family: monospace; padding: 1px 0; }

.w-full { width: 100%; }
.mt-1   { margin-top: 4px; }
.mt-3   { margin-top: 12px; }
</style>
