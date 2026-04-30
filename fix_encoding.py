import os

files = {
    r"frontend/src/views/CRM/composables/useCrmBoard.ts": """export const CRM_STAGES = [
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
  return phone.toString().replace(/\\D/g, '').slice(-9)
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
""",
    r"frontend/src/views/CRM/composables/useCrmAttentionRules.ts": """export const getNextContactDate = (order: any) => order?.next_contact_at || order?.next_contact_date || null

export const getOrderDeadline = (order: any) => order?.deadline || order?.deadline_date || null

export const getNextContactLabel = (order: any) => {
  const value = getNextContactDate(order)
  if (!value) return 'Контакт не заплановано'
  const date = new Date(value)
  const today = new Date().toDateString()
  const prefix = date < new Date()
    ? 'Контакт прострочено'
    : (date.toDateString() === today ? 'Наступний контакт: сьогодні' : 'Наступний контакт')
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
        reasons.push({ text: 'Немає наступного контакту', level: 'warning' })
      } else if (new Date(nextContact) < new Date()) {
        reasons.push({ text: 'Контакт прострочено', level: 'critical' })
      }

      if (['critical', 'urgent'].includes(slaLevel)) {
        reasons.push({ text: `Без дії ${getSlaHours(order.id)} год`, level: 'critical' })
      } else if (slaLevel === 'warning') {
        reasons.push({ text: `Затримка контакту: ${getSlaHours(order.id)} год`, level: 'warning' })
      }
    }

    if (stage !== 'done') {
      if (!deadline) {
        reasons.push({ text: 'Немає дедлайну', level: 'warning' })
      } else if (new Date(deadline) < new Date()) {
        reasons.push({ text: 'Прострочений дедлайн', level: 'critical' })
      }

      if (!hasPrepayment(order) && Number(order.total_amount || 0) > 0 && ['payment', 'processing'].includes(stage)) {
        reasons.push({ text: 'Немає передоплати', level: 'warning' })
      }

      if (needsPaymentControl(order)) {
        reasons.push({ text: 'Потрібен контроль оплати', level: 'warning' })
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
"""
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed {path}")
