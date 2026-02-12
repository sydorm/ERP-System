import axios from 'axios'

// Create axios instance with base URL from environment variables or dynamic location
let baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// If running on a remote server (not localhost) and no env var is set, use the current hostname
if (!import.meta.env.VITE_API_URL && typeof window !== 'undefined') {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        baseURL = `${window.location.protocol}//${window.location.hostname}:8000`
    }
}

const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor for handling 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Token expired or invalid
            const token = localStorage.getItem('token')
            if (token) {
                localStorage.removeItem('token')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default api
