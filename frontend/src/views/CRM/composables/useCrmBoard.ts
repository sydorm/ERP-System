export const CRM_STAGES = [
  { key: 'new', label: 'Нові', color: '#3D3AA8' },
  { key: 'payment', label: 'Оплата', color: '#F97316' },
  { key: 'processing', label: 'В роботі', color: '#F59E0B' },
  { key: 'production', label: 'Виробництво', color: '#8B5CF6' },
  { key: 'done', label: 'Виконано', color: '#22C55E' }
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
  const map: Record<string, string> = { critical: 'Критичний', urgent: 'Високий', normal: 'Середній', low: 'Низький' }
  return map[p] || 'Середній'
}

export const getPriorityColor = (p: string) => {
  const map: Record<string, string> = { critical: '#EF4444', urgent: '#F97316', normal: '#F59E0B', low: '#10B981' }
  return map[p] || '#F59E0B'
}

export const getPaymentLabel = (s: string) =>
  ({ unpaid: 'НЕ ОПЛАЧЕНО', partial: 'ЧАСТКОВА', paid: 'ОПЛАЧЕНО' } as Record<string, string>)[s] || s

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
  if (diffDays < 0) return 'прострочено'
  if (diffDays === 0) return 'сьогодні'
  return `${diffDays} дн.`
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

  if (diffMins < 60) return `${diffMins > 0 ? diffMins : 1} хв тому`
  if (diffHours < 24) return `${diffHours} год тому`
  if (diffDays === 1) return 'вчора'
  if (diffDays < 7) return `${diffDays} дні тому`
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
    thinking: 'Думає',
    no_answer: 'Не відповів',
    confirmed: 'Підтвердив',
    refused: 'Відмовився',
    THINKING: 'Думає',
    NO_ANSWER: 'Не відповів',
    CONFIRMED: 'Підтвердив',
    REFUSED: 'Відмовився'
  }
  return map[res] || res
}
