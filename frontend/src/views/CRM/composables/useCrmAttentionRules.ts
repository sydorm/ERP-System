export const getNextContactDate = (order: any) => order?.next_contact_at || order?.next_contact_date || null

export const getOrderDeadline = (order: any) => order?.deadline || order?.deadline_date || null

export const getNextContactLabel = (order: any) => {
  const value = getNextContactDate(order)
  if (!value) return 'РљРѕРЅС‚Р°РєС‚ РЅРµ Р·Р°РїР»Р°РЅРѕРІР°РЅРѕ'
  const date = new Date(value)
  const today = new Date().toDateString()
  const prefix = date < new Date()
    ? 'РљРѕРЅС‚Р°РєС‚ РїСЂРѕСЃС‚СЂРѕС‡РµРЅРѕ'
    : (date.toDateString() === today ? 'РќР°СЃС‚СѓРїРЅРёР№ РєРѕРЅС‚Р°РєС‚: СЃСЊРѕРіРѕРґРЅС–' : 'РќР°СЃС‚СѓРїРЅРёР№ РєРѕРЅС‚Р°РєС‚')
  return `${prefix} ${date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}`
}

export const getNextContactClass = (order: any) => {
  const value = getNextContactDate(order)
  if (!value) return 'is-empty'
  return new Date(value) < new Date() ? 'is-overdue' : 'is-planned'
}

export const hasPrepayment = (order: any) =>
  Number(order?.prepayment_amount || order?.paid_amount || 0) > 0 || order?.payment_status === 'paid'

export const needsPaymentControl = (order: any) =>
  order?.payment_status !== 'paid'
  && Number(order?.total_amount || 0) > 0
  && ['payment', 'processing', 'production'].includes(order?.crm_stage)

export const createAttentionRules = ({ getSlaLevel, getSlaHours }: any) => {
  const getAttentionReasons = (order: any) => {
    const reasons: Array<{ text: string; level: string }> = []
    const nextContact = getNextContactDate(order)
    const deadline = getOrderDeadline(order)
    const slaLevel = getSlaLevel(order.id)
    const stage = order.crm_stage || 'new'

    if (['new', 'payment'].includes(stage)) {
      if (!nextContact) {
        reasons.push({ text: 'РќРµРјР°С” РЅР°СЃС‚СѓРїРЅРѕРіРѕ РєРѕРЅС‚Р°РєС‚Сѓ', level: 'warning' })
      } else if (new Date(nextContact) < new Date()) {
        reasons.push({ text: 'РљРѕРЅС‚Р°РєС‚ РїСЂРѕСЃС‚СЂРѕС‡РµРЅРѕ', level: 'critical' })
      }

      if (['critical', 'urgent'].includes(slaLevel)) {
        reasons.push({ text: `Р‘РµР· РґС–С— ${getSlaHours(order.id)} РіРѕРґ`, level: 'critical' })
      } else if (slaLevel === 'warning') {
        reasons.push({ text: `Р—Р°С‚СЂРёРјРєР° РєРѕРЅС‚Р°РєС‚Сѓ: ${getSlaHours(order.id)} РіРѕРґ`, level: 'warning' })
      }
    }

    if (stage !== 'done') {
      if (!deadline) {
        reasons.push({ text: 'РќРµРјР°С” РґРµРґР»Р°Р№РЅСѓ', level: 'warning' })
      } else if (new Date(deadline) < new Date()) {
        reasons.push({ text: 'РџСЂРѕСЃС‚СЂРѕС‡РµРЅРёР№ РґРµРґР»Р°Р№РЅ', level: 'critical' })
      }

      if (!hasPrepayment(order) && Number(order.total_amount || 0) > 0 && ['payment', 'processing'].includes(stage)) {
        reasons.push({ text: 'РќРµРјР°С” РїРµСЂРµРґРѕРїР»Р°С‚Рё', level: 'warning' })
      }

      if (needsPaymentControl(order)) {
        reasons.push({ text: 'РџРѕС‚СЂС–Р±РµРЅ РєРѕРЅС‚СЂРѕР»СЊ РѕРїР»Р°С‚Рё', level: 'warning' })
      }
    }

    return reasons
  }

  const getAttentionScore = (order: any) =>
    getAttentionReasons(order).reduce((score, reason) => score + (reason.level === 'critical' ? 40 : 18), 0)

  const getAttentionReason = (order: any) => getAttentionReasons(order)[0]?.text || ''

  const getAttentionClass = (order: any) => {
    const first = getAttentionReasons(order)[0]
    if (first?.level === 'critical') return 'attention-critical'
    if (first?.level === 'warning') return 'attention-warning'
    return 'attention-info'
  }

  return {
    getAttentionReasons,
    getOrderHints: getAttentionReasons,
    getAttentionScore,
    getAttentionReason,
    getAttentionClass
  }
}
