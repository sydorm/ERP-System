import { computed } from 'vue'
import { getOrderManagerId, normalizePhone } from './useCrmBoard'
import { getOrderDeadline } from './useCrmAttentionRules'

export const createCrmFiltersState = () => ({
  priority: '',
  payment: '',
  managerScope: '',
  deadline: '',
  attentionOnly: false
})

export const useCrmFilters = ({
  filters,
  sortOption,
  searchQuery,
  defaultManagerScope,
  currentUserId,
  getCounterpartyName,
  getAttentionReasons
}: any) => {
  const activeFiltersCount = computed(() => {
    return [
      filters.value.priority,
      filters.value.payment,
      filters.value.deadline,
      filters.value.attentionOnly ? 'attention' : '',
      filters.value.managerScope && filters.value.managerScope !== defaultManagerScope.value ? filters.value.managerScope : '',
    ].filter(Boolean).length
  })

  const activeControlsCount = computed(() => activeFiltersCount.value + (sortOption.value !== 'created_desc' ? 1 : 0))

  const isAnyFilterActive = computed(() =>
    activeFiltersCount.value > 0 || sortOption.value !== 'created_desc' || searchQuery.value !== ''
  )

  const resetFilters = () => {
    filters.value = { ...createCrmFiltersState(), managerScope: defaultManagerScope.value }
  }

  const resetAll = () => {
    resetFilters()
    sortOption.value = 'created_desc'
    searchQuery.value = ''
  }

  const applyFilters = () => {}

  const filterOrdersInStage = (orders: any[], stage: string) => {
    let list = orders.filter(o => o.crm_stage === stage)

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const qPhone = normalizePhone(q)

      list = list.filter(o => {
        const matchText =
          o.order_number.toLowerCase().includes(q) ||
          (o.client_name && o.client_name.toLowerCase().includes(q)) ||
          (o.product_name && o.product_name.toLowerCase().includes(q)) ||
          getCounterpartyName(o.counterparty_id).toLowerCase().includes(q)

        let matchPhone = false
        if (qPhone.length >= 3) {
          const oPhone = normalizePhone(o.client_phone)
          if (oPhone && oPhone.includes(qPhone)) matchPhone = true
        } else if (o.client_phone && o.client_phone.includes(q)) {
          matchPhone = true
        }

        return matchText || matchPhone
      })
    }

    if (filters.value.priority) list = list.filter(o => o.priority === filters.value.priority)
    if (filters.value.payment) list = list.filter(o => o.payment_status === filters.value.payment)

    const scope = filters.value.managerScope || defaultManagerScope.value
    if (scope === 'mine' && currentUserId.value) list = list.filter(o => getOrderManagerId(o) === currentUserId.value)
    if (scope.startsWith('manager:')) {
      const managerId = scope.replace('manager:', '')
      list = list.filter(o => getOrderManagerId(o) === managerId)
    }

    if (filters.value.attentionOnly) list = list.filter(o => getAttentionReasons(o).length > 0)
    if (filters.value.deadline) {
      const now = new Date()
      if (filters.value.deadline === 'overdue') {
        list = list.filter(o => getOrderDeadline(o) && new Date(getOrderDeadline(o)) < now)
      } else if (filters.value.deadline === 'today') {
        const today = now.toDateString()
        list = list.filter(o => getOrderDeadline(o) && new Date(getOrderDeadline(o)).toDateString() === today)
      }
    }

    list.sort((a, b) => {
      if (sortOption.value === 'deadline_asc') {
        const ad = getOrderDeadline(a); const bd = getOrderDeadline(b)
        if (!ad) return 1; if (!bd) return -1
        return new Date(ad).getTime() - new Date(bd).getTime()
      }
      if (sortOption.value === 'amount_desc') return (b.total_amount || 0) - (a.total_amount || 0)
      if (sortOption.value === 'created_desc') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      if (sortOption.value === 'priority_desc') {
        const pMap: Record<string, number> = { critical: 4, urgent: 3, normal: 2, low: 1 }
        return (pMap[b.priority] || 0) - (pMap[a.priority] || 0)
      }
      return 0
    })

    return list
  }

  return {
    activeFiltersCount,
    activeControlsCount,
    isAnyFilterActive,
    resetFilters,
    resetAll,
    applyFilters,
    filterOrdersInStage
  }
}
