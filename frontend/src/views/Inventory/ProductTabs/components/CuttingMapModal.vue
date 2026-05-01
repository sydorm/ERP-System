<template>
  <el-dialog
    v-model="visible"
    title="Карта розкрою"
    width="940px"
    top="3vh"
    destroy-on-close
  >
    <div class="cm-root">

      <!-- Info bar -->
      <div class="cm-infobar">
        <span>Ширина рулону: <b>{{ rollWidthMm }} мм</b></span>
        <span>Довжина: <b>{{ totalLengthMm }} мм</b></span>
        <span>Смуг: <b>{{ renderStrips.length }}</b></span>
        <span>Масштаб: <b>1мм ≈ {{ scale.toFixed(3) }}px</b></span>
      </div>

      <!-- SVG diagram -->
      <div class="cm-scroll">
        <svg
          :width="SVG_LEFT + svgWidth + SVG_RIGHT"
          :height="svgTotalHeight + SVG_BOTTOM"
          class="cm-svg"
        >
          <g :transform="`translate(${SVG_LEFT}, 0)`">

            <!-- Roll background -->
            <rect x="0" y="0" :width="svgWidth" :height="svgTotalHeight"
                  fill="#fafafa" stroke="#b0bec5" stroke-width="1.5" />

            <!-- Horizontal grid every 100 mm -->
            <g v-for="tick in yTicks" :key="tick">
              <line :x1="0" :y1="tick * scale" :x2="svgWidth" :y2="tick * scale"
                    stroke="#eceff1" stroke-width="1" />
              <text :x="-4" :y="tick * scale + 3"
                    text-anchor="end" font-size="8" fill="#b0bec5">{{ tick }}</text>
            </g>

            <!-- Strips -->
            <g v-for="(strip, si) in renderStrips" :key="si">

              <!-- Strip separator -->
              <line v-if="si > 0"
                :x1="0" :y1="strip.svgY" :x2="svgWidth" :y2="strip.svgY"
                stroke="#cfd8dc" stroke-width="1" stroke-dasharray="6,3"
              />

              <!-- Pieces -->
              <g v-for="(piece, pi) in strip.svgPieces" :key="pi">
                <rect
                  :x="piece.svgX + 1"
                  :y="strip.svgY + 1"
                  :width="Math.max(piece.svgW - 2, 1)"
                  :height="Math.max(piece.svgPieceH - 2, 1)"
                  :fill="COLORS[piece.colorIdx % COLORS.length]"
                  fill-opacity="0.82"
                  stroke="white"
                  stroke-width="1.5"
                  rx="2"
                />
                <text
                  v-if="piece.svgW >= 26 && piece.svgPieceH >= 18"
                  :x="piece.svgX + piece.svgW / 2"
                  :y="strip.svgY + piece.svgPieceH / 2"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  font-size="10"
                  font-weight="600"
                  fill="white"
                  style="pointer-events:none; user-select:none"
                >{{ piece.label }}</text>
                <text
                  v-if="piece.svgW >= 46 && piece.svgPieceH >= 30"
                  :x="piece.svgX + piece.svgW / 2"
                  :y="strip.svgY + piece.svgPieceH / 2 + 12"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  font-size="8"
                  fill="rgba(255,255,255,0.9)"
                  style="pointer-events:none; user-select:none"
                >{{ piece.cutW }}×{{ piece.cutL }}</text>
              </g>

              <!-- Remnant zone -->
              <rect
                v-if="strip.remnantSvgW > 1"
                :x="strip.remnantSvgX"
                :y="strip.svgY + 1"
                :width="strip.remnantSvgW - 1"
                :height="strip.svgH - 2"
                fill="#eceff1"
                stroke="#cfd8dc"
                stroke-dasharray="5,3"
                stroke-width="1"
              />
              <text
                v-if="strip.remnantSvgW >= 32"
                :x="strip.remnantSvgX + strip.remnantSvgW / 2"
                :y="strip.svgY + strip.svgH / 2"
                text-anchor="middle"
                dominant-baseline="middle"
                font-size="8"
                fill="#90a4ae"
                style="user-select:none"
              >{{ strip.remnantMm }}мм</text>

              <!-- Strip height label (right side) -->
              <text
                :x="svgWidth + 4"
                :y="strip.svgY + strip.svgH / 2"
                dominant-baseline="middle"
                font-size="8"
                fill="#78909c"
              >{{ strip.height }}мм</text>
            </g>

          </g>

          <!-- Roll width label (bottom center) -->
          <text
            :x="SVG_LEFT + svgWidth / 2"
            :y="svgTotalHeight + SVG_BOTTOM - 4"
            text-anchor="middle"
            font-size="10"
            fill="#546e7a"
          >← {{ rollWidthMm }} мм →</text>

          <!-- Y=0 label -->
          <text :x="SVG_LEFT - 4" :y="10"
                text-anchor="end" font-size="8" fill="#b0bec5">0</text>

        </svg>
      </div>

      <!-- Legend -->
      <div v-if="legendItems.length > 0" class="cm-legend">
        <div v-for="item in legendItems" :key="item.label" class="cm-legend-item">
          <span class="cm-swatch" :style="{ background: COLORS[item.colorIdx % COLORS.length] }"></span>
          <span class="cm-swatch-label">{{ item.label }}</span>
          <span class="cm-swatch-dim">{{ item.cutW }}×{{ item.cutL }} мм · {{ item.count }} шт</span>
        </div>
        <div class="cm-legend-item cm-legend-remnant">
          <span class="cm-swatch cm-swatch-remnant"></span>
          <span class="cm-swatch-label">Залишок</span>
        </div>
      </div>

    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  result:     { type: Object,  required: true },
  cfg:        { type: Object,  required: true },
})
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get:  () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const COLORS = [
  '#1976d2', '#388e3c', '#f57c00', '#7b1fa2',
  '#c62828', '#00838f', '#558b2f', '#d84315',
  '#0288d1', '#5d4037', '#455a64', '#ad1457',
]

const SVG_LEFT   = 32  // space for y-axis labels
const SVG_RIGHT  = 52  // space for strip-height labels
const SVG_BOTTOM = 22  // space for x-axis label

const rollWidthMm = computed(() => Number(props.cfg.rollWidthMm) || 1)
const isMulti     = computed(() => Boolean(props.cfg.multiPieceMode) && Boolean(props.result.meta?.isMulti))

const totalLengthMm = computed(() => {
  if (isMulti.value) return props.result.meta.totalLengthMm || 1
  const { rowsNeeded = 1, cutLengthMm = 1 } = props.result.meta
  return rowsNeeded * cutLengthMm
})

// Scale: fit into display area, never magnify
const MAX_W = 820
const MAX_H = 560
const scale = computed(() => {
  const sw = MAX_W / rollWidthMm.value
  const sh = MAX_H / totalLengthMm.value
  return Math.min(sw, sh, 1.0)
})

const svgWidth       = computed(() => Math.round(rollWidthMm.value * scale.value))
const svgTotalHeight = computed(() => Math.round(totalLengthMm.value * scale.value))

// Horizontal grid ticks every 100mm
const yTicks = computed(() => {
  const ticks = []
  for (let mm = 100; mm < totalLengthMm.value; mm += 100) ticks.push(mm)
  return ticks
})

// Reconstruct strip data for single-piece mode
const buildSinglePieceStrips = () => {
  const { cutWidthMm, cutLengthMm, itemsPerRow, rowsNeeded } = props.result.meta
  const pieceCount = Number(props.cfg.pieceCount) || 1
  let remaining = pieceCount
  const strips = []
  for (let r = 0; r < rowsNeeded; r++) {
    const inRow = Math.min(itemsPerRow, remaining)
    strips.push({
      pieces:    Array(inRow).fill(null).map(() => ({ cutW: cutWidthMm, cutL: cutLengthMm, label: 'Деталь' })),
      height:    cutLengthMm,
      usedWidth: inRow * cutWidthMm,
      remnantMm: rollWidthMm.value - inRow * cutWidthMm,
    })
    remaining -= inRow
  }
  return strips
}

// Assign consistent color per unique label
const labelColorMap = computed(() => {
  const map = {}
  let counter = 0
  const stripsData = isMulti.value ? (props.result.meta.strips || []) : buildSinglePieceStrips()
  for (const strip of stripsData) {
    for (const piece of strip.pieces) {
      const key = piece.label || 'Деталь'
      if (!(key in map)) map[key] = counter++
    }
  }
  return map
})

const renderStrips = computed(() => {
  const stripsData = isMulti.value ? (props.result.meta.strips || []) : buildSinglePieceStrips()
  const cmap = labelColorMap.value
  let currentYmm = 0

  return stripsData.map(strip => {
    const svgY = Math.round(currentYmm * scale.value)
    const svgH = Math.round(strip.height * scale.value)
    currentYmm += strip.height

    let currentXmm = 0
    const svgPieces = strip.pieces.map(piece => {
      const svgX      = Math.round(currentXmm * scale.value)
      const svgW      = Math.round(piece.cutW * scale.value)
      const svgPieceH = Math.round(piece.cutL * scale.value)
      const colorIdx  = cmap[piece.label || 'Деталь'] ?? 0
      currentXmm += piece.cutW
      return { ...piece, svgX, svgW, svgPieceH, colorIdx }
    })

    const remnantSvgX = Math.round(currentXmm * scale.value)
    const remnantSvgW = Math.round(strip.remnantMm * scale.value)

    return { ...strip, svgY, svgH, svgPieces, remnantSvgX, remnantSvgW }
  })
})

// Legend — unique piece types with total count
const legendItems = computed(() => {
  const seen = {}
  const counts = {}
  const items = []
  const stripsData = isMulti.value ? (props.result.meta.strips || []) : buildSinglePieceStrips()

  for (const strip of stripsData) {
    for (const piece of strip.pieces) {
      const key = piece.label || 'Деталь'
      counts[key] = (counts[key] || 0) + 1
      if (!seen[key]) {
        seen[key] = true
        items.push({ label: key, cutW: piece.cutW, cutL: piece.cutL, colorIdx: labelColorMap.value[key] ?? 0, count: 0 })
      }
    }
  }
  items.forEach(item => { item.count = counts[item.label] || 0 })
  return items
})
</script>

<style scoped>
.cm-root { display: flex; flex-direction: column; gap: 12px; }

.cm-infobar {
  display: flex; flex-wrap: wrap; gap: 16px;
  font-size: 12px; color: #546e7a;
  padding: 6px 12px;
  background: #f5f5f5;
  border-radius: 6px;
}
.cm-infobar b { color: #263238; }

.cm-scroll { overflow-x: auto; }
.cm-svg { display: block; font-family: sans-serif; }

.cm-legend {
  display: flex; flex-wrap: wrap; gap: 10px 18px;
  padding: 8px 12px;
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}
.cm-legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.cm-swatch {
  width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0;
  opacity: 0.82;
}
.cm-swatch-remnant { background: #eceff1; border: 1px dashed #b0bec5; opacity: 1; }
.cm-swatch-label { font-weight: 600; color: #263238; }
.cm-swatch-dim { color: #90a4ae; font-size: 11px; }
</style>
