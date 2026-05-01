/**
 * Fabric Cutting Calculator — pure calculation logic (no Vue dependencies).
 *
 * Mirror formula exists in:
 *   backend/app/services/specification_service.py  → _calc_fabric_cutting()
 *
 * Formula:
 *   cutWidthMm  = baseWidthMm  + allowanceLeft  + allowanceRight
 *   cutLengthMm = baseLengthMm + allowanceTop   + allowanceBottom
 *   itemsPerRow = floor(rollWidthMm / cutWidthMm)
 *   rowsNeeded  = ceil(pieceCount / itemsPerRow)
 *   linearMeters = (rowsNeeded * cutLengthMm) / 1000
 *   finalQty    = linearMeters * (1 + wastePercent / 100)
 */

export const FABRIC_CUTTING_DEFAULTS = {
  baseWidthSource:          'width_mm',   // width_mm | length_mm | height_mm | characteristic | manual
  baseLengthSource:         'length_mm',
  baseWidthCharName:        '',
  baseLengthCharName:       '',
  manualBaseWidthMm:        0,
  manualBaseLengthMm:       0,
  allowanceLeftMm:          0,
  allowanceRightMm:         0,
  allowanceTopMm:           0,
  allowanceBottomMm:        0,
  pieceCount:               1,
  rollWidthMm:              0,
  allowRotation:            false,
  respectNapDirection:      false,
  wastePercent:             0,
  materialCharacteristicSource: 'manual', // manual | order_characteristic
  materialCharacteristicName:   '',
}

// ─── Internal helpers ──────────────────────────────────────────────────────

function resolveDim(source, dims, charName, manualValue) {
  switch (source) {
    case 'width_mm':      return Number(dims.width_mm)  || 0
    case 'length_mm':     return Number(dims.length_mm) || 0
    case 'height_mm':     return Number(dims.height_mm) || 0
    case 'characteristic': return Number(dims[charName]) || 0
    case 'manual':
    default:              return Number(manualValue) || 0
  }
}

function tryOrientation(cutW, cutL, rollWidth, pieceCount) {
  if (rollWidth < cutW || cutW <= 0) return null
  const itemsPerRow = Math.floor(rollWidth / cutW)
  if (itemsPerRow < 1) return null
  const rowsNeeded = Math.ceil(pieceCount / itemsPerRow)
  const requiredLengthMm = rowsNeeded * cutL
  const requiredLinearMeters = requiredLengthMm / 1000
  return { itemsPerRow, rowsNeeded, requiredLengthMm, requiredLinearMeters, cutW, cutL }
}

// ─── Public API ────────────────────────────────────────────────────────────

/**
 * @param {Object} config    calc_dim_config.fabric_cutting
 * @param {Object} dims      { width_mm, height_mm, length_mm, [charName]: value }
 * @param {boolean} ignoreWaste  Pass true for base-qty calculation without waste
 * @returns {{ finalQty, valid, errors, warnings, breakdownLines, meta }}
 */
export function computeFabricCutting(config, dims = {}, ignoreWaste = false) {
  const cfg = { ...FABRIC_CUTTING_DEFAULTS, ...(config || {}) }
  const errors = []
  const warnings = []

  // ── Resolve base piece dimensions ────────────────────────────────────────
  const baseWidthMm  = resolveDim(cfg.baseWidthSource,  dims, cfg.baseWidthCharName,  cfg.manualBaseWidthMm)
  const baseLengthMm = resolveDim(cfg.baseLengthSource, dims, cfg.baseLengthCharName, cfg.manualBaseLengthMm)

  if (baseWidthMm  <= 0) errors.push('Не вказана базова ширина деталі.')
  if (baseLengthMm <= 0) errors.push('Не вказана базова довжина деталі.')

  // ── Cut piece with allowances ────────────────────────────────────────────
  const aL = Number(cfg.allowanceLeftMm)   || 0
  const aR = Number(cfg.allowanceRightMm)  || 0
  const aT = Number(cfg.allowanceTopMm)    || 0
  const aB = Number(cfg.allowanceBottomMm) || 0

  const cutWidthMm  = baseWidthMm  + aL + aR
  const cutLengthMm = baseLengthMm + aT + aB

  // ── Roll & count ─────────────────────────────────────────────────────────
  const rollWidthMm = Number(cfg.rollWidthMm) || 0
  if (rollWidthMm <= 0) errors.push('Не вказана ширина рулона.')

  const pieceCount = Math.max(1, Math.round(Number(cfg.pieceCount) || 1))

  // ── Waste ────────────────────────────────────────────────────────────────
  const wastePercent = ignoreWaste ? 0 : Math.max(0, Number(cfg.wastePercent) || 0)

  // ── Early return on critical errors ──────────────────────────────────────
  if (errors.length > 0) {
    return {
      finalQty: 0, valid: false,
      errors, warnings, breakdownLines: errors.map(e => `❌ ${e}`),
      meta: { baseWidthMm, baseLengthMm, cutWidthMm, cutLengthMm },
    }
  }

  // ── Orientation / rotation ───────────────────────────────────────────────
  const allowRotation  = Boolean(cfg.allowRotation)
  const respectNap     = Boolean(cfg.respectNapDirection)
  let chosen = null
  let altVariant = null
  let rotationNote = ''

  const varA = tryOrientation(cutWidthMm, cutLengthMm, rollWidthMm, pieceCount)

  if (allowRotation && !respectNap) {
    const varB = tryOrientation(cutLengthMm, cutWidthMm, rollWidthMm, pieceCount)
    if (varA && varB) {
      if (varB.requiredLinearMeters < varA.requiredLinearMeters) {
        chosen = varB; altVariant = varA
        rotationNote = 'Обрано варіант з поворотом (економніший)'
      } else {
        chosen = varA; altVariant = varB
        rotationNote = 'Обрано варіант без повороту (економніший або рівний)'
      }
    } else if (varA)  { chosen = varA; rotationNote = 'Поворот неможливий — заготовка ширша за рулон у повернутому стані' }
    else if (varB)    { chosen = varB; rotationNote = 'Використано поворот — без нього заготовка ширша за рулон' }
  } else {
    if (respectNap && allowRotation)
      warnings.push('Поворот не використано через напрямок ворсу / малюнка.')
    chosen = varA
  }

  if (!chosen) {
    errors.push('Заготовка ширша за рулон. Деталь не поміщається.')
    return {
      finalQty: 0, valid: false,
      errors, warnings,
      breakdownLines: [...errors.map(e => `❌ ${e}`), `  Заготовка: ${cutWidthMm} × ${cutLengthMm} мм`, `  Ширина рулона: ${rollWidthMm} мм`],
      meta: { baseWidthMm, baseLengthMm, cutWidthMm, cutLengthMm },
    }
  }

  // ── Final quantity ────────────────────────────────────────────────────────
  const finalQty = chosen.requiredLinearMeters * (1 + wastePercent / 100)

  // ── Remnant forecast ──────────────────────────────────────────────────────
  const usedWidthMm    = chosen.itemsPerRow * chosen.cutW
  const remnantWidthMm = rollWidthMm - usedWidthMm
  const remnantForecast = remnantWidthMm > 0 ? `${remnantWidthMm} × ${chosen.cutL} мм` : null

  // ── Breakdown ─────────────────────────────────────────────────────────────
  const bd = []
  bd.push(`Тип: Тканина / розкрій`)
  bd.push(`Базова деталь: ${baseWidthMm} × ${baseLengthMm} мм`)
  bd.push(`Припуски: Л ${aL} / П ${aR} / В ${aT} / Н ${aB} мм`)
  bd.push(`Заготовка: ${cutWidthMm} × ${cutLengthMm} мм`)
  bd.push(`Ширина рулона: ${rollWidthMm} мм`)
  bd.push(`Кількість деталей: ${pieceCount}`)
  bd.push(`В ряд поміщається: ${chosen.itemsPerRow} шт`)
  bd.push(`Рядів потрібно: ${chosen.rowsNeeded}`)
  bd.push(`Потрібна довжина: ${chosen.requiredLengthMm} мм`)
  bd.push(`Погонні метри: ${chosen.requiredLinearMeters.toFixed(3)} м.п.`)
  bd.push(`Відходи: ${wastePercent}%`)
  bd.push(`Разом: ${finalQty.toFixed(3)} м.п.`)
  if (rotationNote) bd.push(`Поворот: ${rotationNote}`)
  if (altVariant) {
    const altFinal = altVariant.requiredLinearMeters * (1 + wastePercent / 100)
    bd.push(`Альтернатива (${altVariant.cutW}×${altVariant.cutL} мм): ${altFinal.toFixed(3)} м.п.`)
  }
  if (remnantForecast) bd.push(`Можливий залишок: ${remnantForecast}`)
  warnings.forEach(w => bd.push(`⚠ ${w}`))

  return {
    finalQty,
    valid: true,
    errors,
    warnings,
    breakdownLines: bd,
    meta: {
      baseWidthMm, baseLengthMm,
      cutWidthMm, cutLengthMm,
      itemsPerRow: chosen.itemsPerRow,
      rowsNeeded: chosen.rowsNeeded,
      requiredLengthMm: chosen.requiredLengthMm,
      requiredLinearMeters: chosen.requiredLinearMeters,
      remnantForecast,
      wastePercent,
    },
  }
}
