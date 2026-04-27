import { defineStore } from 'pinia'
import api from '@/api'

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
        this.notifications = notifRes.data
        const tasksCount = tasksRes.data.length
        this.unreadCount = this.notifications.length + tasksCount
      } catch (e) {
        console.error('Failed to fetch notifications or tasks', e)
      } finally {
        this.loading = false
      }
    },

    async markAsRead(id) {
      try {
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
      // Initial fetch
      this.fetchNotifications()
      // Setup interval every 60 seconds
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
