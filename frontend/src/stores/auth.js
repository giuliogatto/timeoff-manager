import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isManager = computed(() => user.value?.role === 'manager')
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/'

  // Actions
  const login = async (email, password) => {
    loading.value = true
    try {
      const response = await api.post(`login`, {
        email,
        password
      })
      
      token.value = response.data.token
      user.value = response.data
      
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data))
      
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = async (reason = 'User logged out') => {
    console.log(`🔐 Logging out user: ${reason}`)
    
    // Clear state
    token.value = null
    user.value = null
    
    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Disconnect WebSocket if available
    try {
      const { useWebSocketStore } = await import('./websocket')
      const websocketStore = useWebSocketStore()
      websocketStore.disconnect()
    } catch (error) {
      console.log('WebSocket store not available during logout')
    }
    
    // Clear any pending requests
    // Note: This would require additional setup with axios cancel tokens
    console.log('🔐 User logged out successfully')
  }

  const forceLogout = async (reason = 'Session expired') => {
    console.log(`🔐 Force logging out user: ${reason}`)
    
    // Clear auth data
    await logout(reason)
    
    // Redirect to home page
    if (window.location.pathname !== '/') {
      window.location.href = '/'
    }
  }

  const validateToken = async () => {
    if (!token.value) {
      return false
    }

    try {
      // Make a request to validate the token
      // You can use any endpoint that requires authentication
      await api.get('profile')
      return true
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('🔐 Token validation failed - token is invalid')
        forceLogout('Token validation failed')
        return false
      }
      // For other errors, we'll assume the token is still valid
      return true
    }
  }

  const register = async (name, email, password) => {
    loading.value = true
    try {
      const response = await api.post(`register`, {
        name,
        email,
        password
      })
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const googleLogin = async () => {
    try {
      const response = await api.get(`google/auth-url`)
      window.location.href = response.data.auth_url
    } catch (error) {
      throw error
    }
  }

  const initializeAuth = () => {
    console.log('Initializing auth...')
    console.log('Token from localStorage:', token.value)
    
    // Don't automatically validate token on app initialization
    // This can cause issues with OAuth flows where the token is just set
    // Token validation will happen when making authenticated requests
  }

  // Debug method to test token expiration (removed in production)
  const testTokenExpiration = async () => {
    console.log('🧪 Testing token expiration...')
    await forceLogout('Manual test')
  }

  return {
    // State
    token,
    user,
    loading,
    
    // Getters
    isAuthenticated,
    isManager,
    backendUrl,
    
    // Actions
    login,
    logout,
    forceLogout,
    validateToken,
    register,
    googleLogin,
    initializeAuth,
    testTokenExpiration
  }
})
