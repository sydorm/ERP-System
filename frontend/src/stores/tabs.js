import { defineStore } from 'pinia'
import router from '@/router'

export const useTabsStore = defineStore('tabs', {
    state: () => ({
        tabs: [
            {
                title: 'Головна',
                path: '/dashboard',
                name: 'dashboard',
                closable: false
            }
        ],
        activeTabPath: '/dashboard'
    }),

    actions: {
        addTab(route) {
            const isExist = this.tabs.some(tab => tab.path === route.path)

            if (!isExist) {
                // Don't add login, signup or 404 pages
                if (['login', 'signup', 'not-found'].includes(route.name)) return

                this.tabs.push({
                    title: route.meta?.title || route.name || 'Untitled',
                    path: route.path,
                    name: route.name,
                    query: route.query,
                    params: route.params,
                    closable: true
                })
            }
            this.activeTabPath = route.path
        },

        closeTab(targetPath) {
            const tabs = this.tabs
            let activePath = this.activeTabPath

            if (activePath === targetPath) {
                tabs.forEach((tab, index) => {
                    if (tab.path === targetPath) {
                        const nextTab = tabs[index + 1] || tabs[index - 1]
                        if (nextTab) {
                            activePath = nextTab.path
                        }
                    }
                })
            }

            this.activeTabPath = activePath
            this.tabs = tabs.filter(tab => tab.path !== targetPath)

            if (router.currentRoute.value.path !== activePath) {
                router.push(activePath)
            }
        },

        closeOthers(path) {
            this.tabs = this.tabs.filter(tab => tab.path === path || !tab.closable)
            this.activeTabPath = path
            if (router.currentRoute.value.path !== path) {
                router.push(path)
            }
        },

        closeAll() {
            this.tabs = this.tabs.filter(tab => !tab.closable)
            const firstTab = this.tabs[0]
            if (firstTab) {
                this.activeTabPath = firstTab.path
                router.push(firstTab.path)
            }
        }
    },

    persist: true // Requires pinia-plugin-persistedstate if we want browser persistence, skipping for MVP or adding later
})
