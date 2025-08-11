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
  async (error) => {
    if (error.response?.status === 401) {
      console.log('🔐 401 Unauthorized - Token expired, logging out user')
      
      // Get stores
      const authStore = useAuthStore()
      const toastStore = useToastStore()
      
      // Show user-friendly toast message
      toastStore.warning('Your session has expired. Please login again.', 8000)
      
      // Use the new forceLogout method which handles both logout and redirect
      await authStore.forceLogout('Token expired')
    }
    
    return Promise.reject(error)
  }
)

export default api
