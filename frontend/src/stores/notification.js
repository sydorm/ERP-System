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
        const res = await api.get('/api/v1/notifications?unread_only=true')
        this.notifications = res.data
        this.unreadCount = this.notifications.length
      } catch (e) {
        console.error('Failed to fetch notifications', e)
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
