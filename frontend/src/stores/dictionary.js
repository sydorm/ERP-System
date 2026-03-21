import { defineStore } from 'pinia'
import api from '@/api'

export const useDictionaryStore = defineStore('dictionary', {
  state: () => ({
    dictionaries: {}, // Format: { CATEGORY_CODE: [items...] }
    loading: false,
    lastUpdated: null
  }),

  getters: {
    getCategory: (state) => (category) => {
      return state.dictionaries[category] || []
    },
    
    // Helper to get name by code
    getName: (state) => (category, code) => {
      const items = state.dictionaries[category] || []
      const item = items.find(i => i.code === code)
      return item ? item.name : code
    },

    // Helper to get code by code (effectively identity, but useful for user's preference for short names)
    getShortName: (state) => (category, code) => {
      const items = state.dictionaries[category] || []
      const item = items.find(i => i.code === code)
      // For now, code is the short name (e.g. 'шт')
      return item ? item.code : code
    }
  },

  actions: {
    async fetchCategory(category, force = false) {
      if (!force && this.dictionaries[category] && this.dictionaries[category].length > 0) {
        return this.dictionaries[category]
      }

      this.loading = true
      try {
        const response = await api.get(`/api/v1/dictionaries/${category}`)
        this.dictionaries[category] = response.data
        this.lastUpdated = new Date()
        return response.data
      } catch (error) {
        console.error(`Failed to fetch dictionary: ${category}`, error)
        return []
      } finally {
        this.loading = false
      }
    },

    async fetchMultiple(categories, force = false) {
      const promises = categories.map(cat => this.fetchCategory(cat, force))
      return Promise.all(promises)
    },

    // Update local state after an item is edited/added elsewhere
    updateLocalCategory(category, items) {
      this.dictionaries[category] = items
    }
  }
})
