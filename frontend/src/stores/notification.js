import { defineStore } from 'pinia'
import api from '@/api'

const getOrderNumber = (item = {}) => (
  item.order_number
  || item.crm_order_number
  || item.number
  || item.data?.order_number
  || item.data?.crm_order_number
  || item.data?.number
)

const getOrderId = (item = {}) => {
  const data = item.data || {}
  return item.order_id || item.real_order_id || item.crm_order_id || data.order_id || data.real_order_id || data.crm_order_id
}

const getNotificationKey = (n) => {
  const data = n?.data || {}
  return [
    n?.type || 'INFO',
    data.order_id || data.real_order_id || data.task_id || n?.id || '',
    data.crm_stage || data.reason || '',
  ].join(':')
}

const normalizeNotification = (n) => ({
  ...n,
  id: n.id || getNotificationKey(n),
  created_at: n.created_at || new Date().toISOString(),
  title: n.title || 'Сповіщення',
  message: n.message || '',
  data: {
    ...(n.data || {}),
    order_id: getOrderId(n),
    order_number: getOrderNumber(n),
  },
  is_virtual: Boolean(n.is_virtual),
})

const normalizeTaskNotification = (task) => {
  const orderId = getOrderId(task)
  const orderNumber = getOrderNumber(task)
  const taskId = task.id || task.task_id || orderId || orderNumber || 'unknown'
  const type = task.type || task.notification_type || 'CRM_TASK'

  return {
    id: `crm-task:${type}:${taskId}`,
    type,
    title: task.title || (orderNumber ? `CRM: ${orderNumber}` : 'CRM: потрібна дія'),
    message: task.message || task.description || task.client_name || 'Потрібна дія менеджера по CRM-заявці',
    created_at: task.created_at || task.last_activity_at || task.due_at || task.next_contact_at || new Date().toISOString(),
    data: {
      ...task,
      task_id: task.id || task.task_id,
      order_id: orderId,
      real_order_id: task.real_order_id || orderId,
      order_number: orderNumber,
      client_phone: task.client_phone,
      module: 'CRM',
    },
    is_virtual: true,
    source: 'crm',
  }
}

const mergeNotifications = (notifications = [], tasks = []) => {
  const map = new Map()

  notifications.map(normalizeNotification).forEach((item) => {
    map.set(getNotificationKey(item), item)
  })

  tasks.map(normalizeTaskNotification).forEach((item) => {
    const key = getNotificationKey(item)
    if (!map.has(key)) map.set(key, item)
  })

  return Array.from(map.values()).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    pollingInterval: null
  }),

  actions: {
    async fetchNotifications() {
      this.loading = true
      try {
        const [notifRes, tasksRes] = await Promise.all([
          api.get('/api/v1/notifications?unread_only=true'),
          api.get('/api/v1/crm/tasks/today')
        ])
        this.notifications = mergeNotifications(notifRes.data, tasksRes.data)
        this.unreadCount = this.notifications.length
      } catch (e) {
        console.error('Failed to fetch notifications or tasks', e)
      } finally {
        this.loading = false
      }
    },

    async markAsRead(id) {
      try {
        const item = this.notifications.find(n => n.id === id)
        if (item?.is_virtual) return
        await api.patch(`/api/v1/notifications/${id}/read`)
        await this.fetchNotifications()
      } catch (e) {
        console.error('Failed to mark notification as read', e)
      }
    },

    async readAll() {
      try {
        await api.post('/api/v1/notifications/read-all')
        await this.fetchNotifications()
      } catch (e) {
        console.error('Failed to mark all as read', e)
      }
    },

    startPolling() {
      if (this.pollingInterval) return
      this.fetchNotifications()
      this.pollingInterval = setInterval(() => {
        this.fetchNotifications()
      }, 60000)
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    }
  }
})
