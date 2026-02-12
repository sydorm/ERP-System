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
        fetchUser
    }
})
