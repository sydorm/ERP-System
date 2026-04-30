export const CRM_STAGES = [
  { key: 'new', label: 'РќРѕРІС–', color: '#3D3AA8' },
  { key: 'payment', label: 'РћРїР»Р°С‚Р°', color: '#F97316' },
  { key: 'processing', label: 'Р’ СЂРѕР±РѕС‚С–', color: '#F59E0B' },
  { key: 'production', label: 'Р’РёСЂРѕР±РЅРёС†С‚РІРѕ', color: '#8B5CF6' },
  { key: 'done', label: 'Р’РёРєРѕРЅР°РЅРѕ', color: '#22C55E' }
]

export const createStageSkip = () => ({
  new: 0,
  processing: 0,
  confirmed: 0,
  payment: 0,
  production: 0,
  done: 0
})

export const getOrderManagerId = (order: any) =>
  order?.responsible_manager_id || order?.manager_id || order?.created_by || null

export const formatCurrency = (val: any) => new Intl.NumberFormat('uk-UA').format(val || 0)

export const formatDate = (dateStr: any) =>
  new Date(dateStr).toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' })

export const normalizePhone = (phone: any) => {
  if (!phone) return ''
  return phone.toString().replace(/\D/g, '').slice(-9)
}

export const getPriorityLabel = (p: string) => {
  const map: Record<string, string> = { critical: 'РљСЂРёС‚РёС‡РЅРёР№', urgent: 'Р’РёСЃРѕРєРёР№', normal: 'РЎРµСЂРµРґРЅС–Р№', low: 'РќРёР·СЊРєРёР№' }
  return map[p] || 'РЎРµСЂРµРґРЅС–Р№'
}

export const getPriorityColor = (p: string) => {
  const map: Record<string, string> = { critical: '#EF4444', urgent: '#F97316', normal: '#F59E0B', low: '#10B981' }
  return map[p] || '#F59E0B'
}

export const getPaymentLabel = (s: string) =>
  ({ unpaid: 'РќР• РћРџР›РђР§Р•РќРћ', partial: 'Р§РђРЎРўРљРћР’Рђ', paid: 'РћРџР›РђР§Р•РќРћ' } as Record<string, string>)[s] || s

export const getDeadlineClass = (deadlineStr: any) => {
  if (!deadlineStr) return ''
  const now = new Date()
  const dl = new Date(deadlineStr)
  const diffDays = (dl.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  if (diffDays < 3) return 'deadline-danger'
  if (diffDays < 7) return 'deadline-warning'
  return ''
}

export const getDeadlineDaysText = (deadlineStr: any) => {
  if (!deadlineStr) return ''
  const now = new Date()
  const dl = new Date(deadlineStr)
  const diffDays = Math.ceil((dl.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 'РїСЂРѕСЃС‚СЂРѕС‡РµРЅРѕ'
  if (diffDays === 0) return 'СЃСЊРѕРіРѕРґРЅС–'
  return `${diffDays} РґРЅ.`
}

export const isReminderToday = (nextContactAt: any) => {
  if (!nextContactAt) return false
  return new Date(nextContactAt).toDateString() === new Date().toDateString()
}

export const formatRelativeTime = (dateStr: any) => {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins > 0 ? diffMins : 1} С…РІ С‚РѕРјСѓ`
  if (diffHours < 24) return `${diffHours} РіРѕРґ С‚РѕРјСѓ`
  if (diffDays === 1) return 'РІС‡РѕСЂР°'
  if (diffDays < 7) return `${diffDays} РґРЅС– С‚РѕРјСѓ`
  return date.toLocaleDateString('uk-UA')
}

export const getChannelIcon = (type: string) => {
  const map: Record<string, string> = {
    phone: 'Phone',
    viber: 'ChatDotRound',
    telegram: 'Promotion',
    instagram: 'Camera'
  }
  return map[type] || 'ChatDotRound'
}

export const getContactResultLabel = (res: string) => {
  const map: Record<string, string> = {
    thinking: 'Р”СѓРјР°С”',
    no_answer: 'РќРµ РІС–РґРїРѕРІС–РІ',
    confirmed: 'РџС–РґС‚РІРµСЂРґРёРІ',
    refused: 'Р’С–РґРјРѕРІРёРІСЃСЏ',
    THINKING: 'Р”СѓРјР°С”',
    NO_ANSWER: 'РќРµ РІС–РґРїРѕРІС–РІ',
    CONFIRMED: 'РџС–РґС‚РІРµСЂРґРёРІ',
    REFUSED: 'Р’С–РґРјРѕРІРёРІСЃСЏ'
  }
  return map[res] || res
}
