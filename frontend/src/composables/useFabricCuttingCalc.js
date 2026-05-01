/**
 * Fabric Cutting Calculator — pure calculation logic (no Vue dependencies).
 *
 * Mirror formula exists in:
 *   backend/app/services/specification_service.py  → _calc_fabric_cutting()
 *
 * Single-piece formula:
 *   cutWidthMm  = baseWidthMm  + allowanceLeft  + allowanceRight
 *   cutLengthMm = baseLengthMm + allowanceTop   + allowanceBottom
 *   itemsPerRow = floor(rollWidthMm / cutWidthMm)
 *   rowsNeeded  = ceil(pieceCount / itemsPerRow)
 *   linearMeters = (rowsNeeded * cutLengthMm) / 1000
 *   finalQty    = linearMeters * (1 + wastePercent / 100)
 *
 * Multi-piece formula (strip packing — First Fit Decreasing Height):
 *   1. Expand all pieces into individual cut instances
 *   2. Sort by cutLength desc (tallest first)
 *   3. Greedily fill each strip left-to-right, scanning ALL remaining pieces
 *   4. Strip height = max cutLength of pieces placed in that strip
 *   5. totalLengthMm = sum of strip heights
 *   6. finalQty = (totalLengthMm / 1000) * (1 + wastePercent / 100)
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
  // Multi-piece mode
  multiPieceMode:           false,
  pieces:                   [],
}

export const PIECE_DEFAULTS = {
  name:               '',
  baseWidthMm:        0,
  baseLengthMm:       0,
  allowanceLeftMm:    0,
  allowanceRightMm:   0,
  allowanceTopMm:     0,
  allowanceBottomMm:  0,
  count:              1,
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

// ─── Multi-piece strip packing ─────────────────────────────────────────────

/**
 * First Fit Decreasing Height strip packing for multiple piece types.
 * @param {Object} config  full fabric cutting config (with .pieces array)
 * @param {Object} dims    { width_mm, height_mm, length_mm, ... }
 * @param {boolean} ignoreWaste
 */
export function computeFabricCuttingMulti(config, dims = {}, ignoreWaste = false) {
  const cfg = { ...FABRIC_CUTTING_DEFAULTS, ...(config || {}) }
  const errors = []
  const warnings = []

  const rollWidthMm = Number(cfg.rollWidthMm) || 0
  if (rollWidthMm <= 0) {
    errors.push('Не вказана ширина рулона.')
    return { finalQty: 0, valid: false, errors, warnings, breakdownLines: errors.map(e => `❌ ${e}`), meta: {} }
  }

  const pieces = cfg.pieces || []
  if (!pieces.length) {
    errors.push('Немає деталей для розкрою. Додайте хоча б одну.')
    return { finalQty: 0, valid: false, errors, warnings, breakdownLines: errors.map(e => `❌ ${e}`), meta: {} }
  }

  const wastePercent  = ignoreWaste ? 0 : Math.max(0, Number(cfg.wastePercent) || 0)
  const allowRotation = Boolean(cfg.allowRotation)
  const respectNap    = Boolean(cfg.respectNapDirection)

  // Expand pieces into individual cut instances
  const allPieces = []
  for (const p of pieces) {
    const bW = Number(p.baseWidthMm) || 0
    const bL = Number(p.baseLengthMm) || 0
    const aL = Number(p.allowanceLeftMm) || 0
    const aR = Number(p.allowanceRightMm) || 0
    const aT = Number(p.allowanceTopMm) || 0
    const aB = Number(p.allowanceBottomMm) || 0
    const cutW = bW + aL + aR
    const cutL = bL + aT + aB
    const cnt = Math.max(1, Math.round(Number(p.count) || 1))
    const label = p.name || `${bW}×${bL}`

    if (bW <= 0 || bL <= 0) {
      errors.push(`Деталь "${label}": не вказані базові розміри.`)
      continue
    }
    if (cutW > rollWidthMm) {
      errors.push(`Деталь "${label}": ширина заготовки ${cutW}мм > ширина рулону ${rollWidthMm}мм.`)
      continue
    }
    for (let i = 0; i < cnt; i++) {
      allPieces.push({ cutW, cutL, label })
    }
  }

  if (errors.length) {
    return { finalQty: 0, valid: false, errors, warnings, breakdownLines: errors.map(e => `❌ ${e}`), meta: {} }
  }
  if (!allPieces.length) {
    return { finalQty: 0, valid: false, errors: ['Немає валідних деталей.'], warnings, breakdownLines: [], meta: {} }
  }

  // Sort by cutLength desc, then cutWidth desc (tallest + widest first)
  const remaining = [...allPieces].sort((a, b) => b.cutL - a.cutL || b.cutW - a.cutW)

  let totalLengthMm = 0
  const strips = []

  while (remaining.length > 0) {
    let usedWidth = 0
    let stripHeight = 0
    const inStrip = []

    // Scan ALL remaining pieces, place anything that fits (FFDH + optional rotation)
    let i = 0
    while (i < remaining.length) {
      const p = remaining[i]
      const canNormal  = usedWidth + p.cutW <= rollWidthMm
      const canRotated = allowRotation && !respectNap && p.cutW !== p.cutL
                         && usedWidth + p.cutL <= rollWidthMm

      if (canNormal || canRotated) {
        let placedW = p.cutW, placedL = p.cutL
        if (canNormal && canRotated) {
          // Both fit — rotate if normal height (cutL) > rotated height (cutW)
          if (p.cutL > p.cutW) { placedW = p.cutL; placedL = p.cutW }
        } else if (canRotated) {
          placedW = p.cutL; placedL = p.cutW
        }
        inStrip.push({ ...p, cutW: placedW, cutL: placedL })
        usedWidth += placedW
        stripHeight = Math.max(stripHeight, placedL)
        remaining.splice(i, 1)
      } else {
        i++
      }
    }

    if (!inStrip.length) break // safety
    totalLengthMm += stripHeight
    strips.push({ pieces: inStrip, height: stripHeight, usedWidth, remnantMm: rollWidthMm - usedWidth })
  }

  const linearMeters = totalLengthMm / 1000
  const finalQty = linearMeters * (1 + wastePercent / 100)

  // Breakdown
  const bd = []
  bd.push('Тип: Тканина / розкрій (мульти-деталі)')
  bd.push(`Ширина рулона: ${rollWidthMm} мм`)
  pieces.forEach(p => {
    const cutW = (Number(p.baseWidthMm)||0) + (Number(p.allowanceLeftMm)||0) + (Number(p.allowanceRightMm)||0)
    const cutL = (Number(p.baseLengthMm)||0) + (Number(p.allowanceTopMm)||0) + (Number(p.allowanceBottomMm)||0)
    const lbl = p.name || `${p.baseWidthMm}×${p.baseLengthMm}`
    bd.push(`Деталь "${lbl}": ${p.baseWidthMm}×${p.baseLengthMm} + припуски → заготовка ${cutW}×${cutL}мм × ${p.count}шт`)
  })
  bd.push(`Смуг розкрою: ${strips.length}`)
  strips.forEach((s, idx) => {
    const names = s.pieces.map(p => `${p.label}(${p.cutW}×${p.cutL})`).join(', ')
    bd.push(`  Смуга ${idx + 1}: висота ${s.height}мм — ${names} — залишок ${s.remnantMm}мм`)
  })
  bd.push(`Загальна довжина: ${totalLengthMm}мм`)
  bd.push(`Погонні метри: ${linearMeters.toFixed(3)} м.п.`)
  bd.push(`Відходи: ${wastePercent}%`)
  bd.push(`Разом: ${finalQty.toFixed(3)} м.п.`)

  return {
    finalQty,
    valid: true,
    errors,
    warnings,
    breakdownLines: bd,
    meta: { strips, totalLengthMm, linearMeters, wastePercent, isMulti: true },
  }
}

// ─── Public API ────────────────────────────────────────────────────────────

/**
 * @param {Object} config    calc_dim_config (flat — fabric cutting settings stored at top level)
 * @param {Object} dims      { width_mm, height_mm, length_mm, [charName]: value }
 * @param {boolean} ignoreWaste  Pass true for base-qty calculation without waste
 * @returns {{ finalQty, valid, errors, warnings, breakdownLines, meta }}
 */
export function computeFabricCutting(config, dims = {}, ignoreWaste = false) {
  const cfg = { ...FABRIC_CUTTING_DEFAULTS, ...(config || {}) }

  // Delegate to multi-piece algorithm when mode is active
  if (cfg.multiPieceMode && cfg.pieces?.length > 0) {
    return computeFabricCuttingMulti(cfg, dims, ignoreWaste)
  }

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
