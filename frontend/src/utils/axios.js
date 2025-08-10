import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      console.log('🔐 401 Unauthorized - Token expired, logging out user')
      
      // Get stores
      const authStore = useAuthStore()
      const toastStore = useToastStore()
      
      // Clear auth data
      authStore.logout()
      
      // Show user-friendly toast message
      toastStore.warning('Your session has expired. Please login again.', 8000)
      
      // Redirect to home page using window.location
      // Use setTimeout to ensure the toast is shown before redirect
      setTimeout(() => {
        if (window.location.pathname !== '/') {
          window.location.href = '/'
        }
      }, 100)
    }
    
    return Promise.reject(error)
  }
)

export default api
