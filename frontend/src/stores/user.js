import { defineStore } from 'pinia'
import { ref } from 'vue'

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

    return {
        user,
        token,
        setUser,
        setToken,
        logout,
        isAuthenticated
    }
})
