import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

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
      const response = await axios.post(`${backendUrl}login`, {
        email,
        password
      })
      
      token.value = response.data.token
      user.value = response.data
      
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data))
      
      // Set default authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      
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
    delete axios.defaults.headers.common['Authorization']
  }

  const register = async (name, email, password) => {
    loading.value = true
    try {
      const response = await axios.post(`${backendUrl}register`, {
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
      const response = await axios.get(`${backendUrl}google/auth-url`)
      window.location.href = response.data.auth_url
    } catch (error) {
      throw error
    }
  }

  const initializeAuth = () => {
    // Set authorization header if token exists
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
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
