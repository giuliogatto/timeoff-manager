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

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
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
    // No need to set headers manually - axios interceptor handles it
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
    register,
    googleLogin,
    initializeAuth
  }
})
