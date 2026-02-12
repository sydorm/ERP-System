import axios from 'axios'

// Create axios instance with base URL from environment variables or dynamic location
let baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// FORCE logic: If we are on a remote server (not localhost), we MUST NOT use localhost for API
if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'

    // If browser is NOT at localhost, but baseURL IS localhost -> Fix it to use browser's hostname
    if (!isLocalhost && (baseURL.includes('localhost') || baseURL.includes('127.0.0.1'))) {
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
