import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || null)

    const setUser = (userData) => {
        user.value = userData
    }

    const setToken = (newToken) => {
        token.value = newToken
        localStorage.setItem('token', newToken)
    }

    const logout = () => {
        user.value = null
        token.value = null
        localStorage.removeItem('token')
    }

    const isAuthenticated = () => {
        return !!token.value
    }

    const hasPermission = (permission) => {
        if (!user.value) return false
        if (user.value.is_superuser || user.value.role === 'admin') return true
        
        const perms = user.value.permissions || {}
        if (perms[permission]) return true
        
        // Check for module-level permission
        const module = permission.split('.')[0]
        if (perms[`${module}.all`]) return true
        
        return false
    }

    const fetchUser = async () => {
        try {
            const response = await api.get('/auth/me')
            user.value = response.data
        } catch (error) {
            console.error('Failed to fetch user profile', error)
            logout()
        }
    }

    return {
        user,
        token,
        setUser,
        setToken,
        logout,
        isAuthenticated,
        hasPermission,
        fetchUser
    }
})
