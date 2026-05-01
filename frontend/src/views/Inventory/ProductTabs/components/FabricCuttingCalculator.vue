<template>
  <div class="fc-calc">
    <div class="fc-header">
      <span class="fc-icon">🧵</span>
      <span class="fc-title">Тканина / розкрій</span>
    </div>

    <el-form label-position="top" size="small" class="fc-form">

      <!-- ── Mode toggle ─────────────────────────────────────────────────── -->
      <div class="fc-mode-row">
        <el-switch
          v-model="cfg.multiPieceMode"
          active-text="Кілька типів деталей"
          inactive-text="Один тип деталі"
          @change="onModeChange"
        />
      </div>

      <!-- ══════════════════════════════════════════════════════════════════ -->
      <!--  SINGLE-PIECE MODE                                                -->
      <!-- ══════════════════════════════════════════════════════════════════ -->
      <template v-if="!cfg.multiPieceMode">

        <!-- ── Dimension sources ──────────────────────────────────────────── -->
        <div class="fc-section-title mt-3">Джерело розмірів деталі</div>
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

        <!-- Dimension preview -->
        <div v-if="resolvedPreviewDims" class="fc-dim-preview">
          <span>Поточні розміри товару:</span>
          <span class="fc-dim-badge">Ш {{ productDimensions.width_mm || 0 }} мм</span>
          <span class="fc-dim-badge">Д {{ productDimensions.length_mm || 0 }} мм</span>
          <span class="fc-dim-badge">В {{ productDimensions.height_mm || 0 }} мм</span>
        </div>

        <!-- ── Allowances ─────────────────────────────────────────────────── -->
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

        <!-- Piece count -->
        <div class="fc-row-2">
          <el-form-item label="Кількість деталей">
            <el-input-number v-model="cfg.pieceCount" :min="1" :precision="0" class="w-full" @change="clearPreview" />
          </el-form-item>
          <div></div>
        </div>

      </template>

      <!-- ══════════════════════════════════════════════════════════════════ -->
      <!--  MULTI-PIECE MODE — таблиця деталей                              -->
      <!-- ══════════════════════════════════════════════════════════════════ -->
      <template v-else>
        <div class="fc-section-title mt-3">Деталі для розкрою</div>

        <div class="fc-pieces-wrap">
          <!-- Header -->
          <div class="fc-pieces-head">
            <span>Назва деталі</span>
            <span title="Базова ширина деталі без припусків">Ш, мм</span>
            <span title="Базова довжина деталі без припусків">Д, мм</span>
            <span title="Припуск зліва (додається до ширини)">← Зліва</span>
            <span title="Припуск справа (додається до ширини)">Справа →</span>
            <span title="Припуск зверху (додається до довжини)">↑ Зверху</span>
            <span title="Припуск знизу (додається до довжини)">↓ Знизу</span>
            <span title="Кількість деталей цього типу">Шт</span>
            <span></span>
          </div>

          <!-- Rows -->
          <div v-for="(piece, idx) in (cfg.pieces || [])" :key="idx" class="fc-piece-row">
            <input
              v-model="piece.name"
              class="fc-cell-input fc-cell-name"
              placeholder="напр. Сидіння"
              @input="clearPreview"
            />
            <input
              v-model.number="piece.baseWidthMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-num"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.baseLengthMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-num"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.allowanceLeftMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-allow"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.allowanceRightMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-allow"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.allowanceTopMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-allow"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.allowanceBottomMm"
              type="number" min="0" step="1"
              class="fc-cell-input fc-cell-allow"
              placeholder="0"
              @change="clearPreview"
            />
            <input
              v-model.number="piece.count"
              type="number" min="1" step="1"
              class="fc-cell-input fc-cell-count"
              placeholder="1"
              @change="clearPreview"
            />
            <button
              class="fc-cell-del"
              @click="removePiece(idx)"
              :disabled="(cfg.pieces || []).length <= 1"
              title="Видалити рядок"
            >✕</button>
          </div>
        </div>

        <el-button size="small" type="primary" plain class="mt-2" @click="addPiece">
          + Додати деталь
        </el-button>

        <!-- Hint about multi-piece packing -->
        <div class="fc-multi-hint mt-2">
          Алгоритм: First Fit Decreasing — деталі укладаються смугами, найвищі першими.
          Деталі різних типів можуть ділити одну смугу, якщо вміщуються по ширині.
        </div>
      </template>

      <!-- ── Roll params (shared) ───────────────────────────────────────── -->
      <div class="fc-section-title mt-3">Параметри рулону</div>
      <div class="fc-row-2">
        <el-form-item label="Ширина рулона, мм">
          <el-input-number v-model="cfg.rollWidthMm" :min="0" :precision="0" class="w-full"
            placeholder="напр. 1400" @change="clearPreview" />
          <div class="fc-field-hint">Стандарт тканин: 1400 мм</div>
        </el-form-item>
        <div></div>
      </div>

      <!-- ── Rotation & nap (both modes) ─────────────────────────────── -->
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

      <!-- ── Waste (shared) ────────────────────────────────────────────── -->
      <div class="fc-row-2 mt-3">
        <el-form-item label="Відходи, %">
          <el-input-number v-model="cfg.wastePercent" :min="0" :max="100" :precision="1" class="w-full" @change="clearPreview" />
          <div class="fc-field-hint">Зберігається як {{ (cfg.wastePercent / 100).toFixed(4) }} у форматі системи</div>
        </el-form-item>
        <div></div>
      </div>

      <!-- ── Material characteristic (shared) ─────────────────────────── -->
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
        <div v-for="e in previewResult.errors" :key="e" class="fc-error-line">{{ e }}</div>
      </div>

      <!-- Success -->
      <template v-if="previewResult.valid">
        <div class="fc-result-main">
          <span class="fc-result-label">Потрібно тканини:</span>
          <span class="fc-result-value">{{ previewResult.finalQty.toFixed(3) }} м.п.</span>
        </div>

        <!-- Single-piece meta -->
        <div v-if="!previewResult.meta.isMulti" class="fc-result-meta">
          Заготовка: <strong>{{ previewResult.meta.cutWidthMm }} × {{ previewResult.meta.cutLengthMm }} мм</strong>
          · В ряд: <strong>{{ previewResult.meta.itemsPerRow }} шт</strong>
          · Рядів: <strong>{{ previewResult.meta.rowsNeeded }}</strong>
        </div>

        <!-- Multi-piece meta -->
        <div v-else class="fc-result-meta">
          Смуг розкрою: <strong>{{ previewResult.meta.strips?.length }}</strong>
          · Загальна довжина: <strong>{{ previewResult.meta.totalLengthMm }} мм</strong>
          · Деталей: <strong>{{ (cfg.pieces || []).reduce((s, p) => s + (Number(p.count)||1), 0) }} шт</strong>
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

        <!-- Remnant forecast (single-piece only) -->
        <div v-if="!previewResult.meta.isMulti && previewResult.meta.remnantForecast" class="fc-remnant">
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

        <!-- Cutting map button -->
        <div class="fc-map-btn-row">
          <el-button size="small" plain @click="showCuttingMap = true">
            🗺 Відкрити карту розкрою
          </el-button>
        </div>
      </template>

    </div>

    <!-- Cutting map modal -->
    <CuttingMapModal
      v-if="previewResult?.valid"
      v-model="showCuttingMap"
      :result="previewResult"
      :cfg="cfg"
    />

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { computeFabricCutting, PIECE_DEFAULTS } from '@/composables/useFabricCuttingCalc'
import CuttingMapModal from './CuttingMapModal.vue'
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
const showCuttingMap = ref(false)

const clearPreview = () => { previewResult.value = null; stockInfo.value = null }

const resolvedPreviewDims = computed(() =>
  props.productDimensions.width_mm != null ||
  props.productDimensions.length_mm != null ||
  props.productDimensions.height_mm != null
)

// ── Multi-piece helpers ──────────────────────────────────────────────────

const onModeChange = () => {
  clearPreview()
  if (cfg.multiPieceMode) {
    if (!cfg.pieces) cfg.pieces = []
    if (cfg.pieces.length === 0) cfg.pieces.push({ ...PIECE_DEFAULTS })
  }
}

const addPiece = () => {
  if (!cfg.pieces) cfg.pieces = []
  cfg.pieces.push({ ...PIECE_DEFAULTS })
  clearPreview()
}

const removePiece = (idx) => {
  if (!cfg.pieces || cfg.pieces.length <= 1) return
  cfg.pieces.splice(idx, 1)
  clearPreview()
}

// ── Preview ──────────────────────────────────────────────────────────────

const buildDims = () => ({
  width_mm:  Number(props.productDimensions.width_mm)  || 0,
  length_mm: Number(props.productDimensions.length_mm) || 0,
  height_mm: Number(props.productDimensions.height_mm) || 0,
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
        const data = res.data
        let available = 0
        if (typeof data === 'number') {
          available = data
        } else if (data && typeof data.total !== 'undefined') {
          available = Number(data.total) || 0
        } else if (data && typeof data.balance !== 'undefined') {
          available = Number(data.balance) || 0
        } else if (typeof data === 'object') {
          available = Object.values(data).reduce((s, v) => s + (Number(v) || 0), 0)
        }
        if (!cfg.materialCharacteristicName) {
          stockInfo.value = { error: 'Не вибрано характеристику кольору — залишок показано загальний.', available }
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

.fc-mode-row {
  display: flex; align-items: center;
  padding: 6px 0 4px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 2px;
}

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

/* Multi-piece table */
.fc-pieces-wrap {
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 4px;
}
.fc-pieces-head,
.fc-piece-row {
  display: grid;
  grid-template-columns: 160px 80px 80px 72px 72px 72px 72px 56px 28px;
  gap: 0;
  align-items: center;
  min-width: 700px;
}
.fc-pieces-head {
  background: #f0f4f8;
  border-bottom: 2px solid #dde3ea;
  font-size: 10px;
  font-weight: 700;
  color: #546e7a;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.fc-pieces-head span {
  padding: 6px 8px;
  border-right: 1px solid #dde3ea;
}
.fc-pieces-head span:last-child { border-right: none; }
.fc-piece-row {
  border-bottom: 1px solid #f0f0f0;
}
.fc-piece-row:last-child { border-bottom: none; }
.fc-piece-row:nth-child(odd) { background: #fafbfc; }

/* Compact native inputs for table cells */
.fc-cell-input {
  width: 100%;
  height: 32px;
  padding: 0 8px;
  border: none;
  border-right: 1px solid #ebebeb;
  background: transparent;
  font-size: 13px;
  color: #263238;
  outline: none;
  box-sizing: border-box;
}
.fc-cell-input:focus {
  background: #fffde7;
  border-right-color: #fbc02d;
}
.fc-cell-input::placeholder { color: #bdbdbd; font-size: 11px; }
.fc-cell-num   { text-align: right; font-weight: 600; color: #1565c0; }
.fc-cell-allow { text-align: right; color: #2e7d32; }
.fc-cell-count { text-align: center; font-weight: 700; }
.fc-cell-name  { font-style: italic; }

.fc-cell-del {
  width: 28px; height: 32px;
  border: none; background: transparent;
  color: #bdbdbd; cursor: pointer;
  font-size: 12px; display: flex; align-items: center; justify-content: center;
}
.fc-cell-del:hover:not(:disabled) { color: #c62828; background: #fce4e4; }
.fc-cell-del:disabled { opacity: 0.3; cursor: not-allowed; }

.fc-multi-hint {
  font-size: 10px;
  color: #90a4ae;
  line-height: 1.4;
  padding: 4px 6px;
  background: #f9f9f9;
  border-radius: 4px;
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

.fc-map-btn-row { margin-top: 6px; padding-top: 6px; border-top: 1px solid #e8f5e9; }

.w-full { width: 100%; }
.mt-1   { margin-top: 4px; }
.mt-2   { margin-top: 8px; }
.mt-3   { margin-top: 12px; }
</style>
