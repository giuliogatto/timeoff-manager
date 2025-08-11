<template>
  <div class="auth-callback">
    <div class="loading-container">
      <div class="spinner"></div>
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toastStore = useToastStore()

const message = ref('Processing authentication...')

onMounted(async () => {
  try {
    // Extract parameters from URL
    const token = route.query.token
    const userId = route.query.user_id
    const email = route.query.email
    const name = route.query.name

    console.log('AuthCallback: Received parameters:', { token: token ? 'present' : 'missing', userId, email, name })

    if (!token) {
      throw new Error('No authentication token received')
    }

    // Store the authentication data
    authStore.token = token
    authStore.user = {
      id: parseInt(userId),
      email: email,
      name: name,
      auth_provider: 'google'
    }
    
    // Also store in localStorage to persist the session
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(authStore.user))

    console.log('AuthCallback: Authentication data stored successfully')

    message.value = 'Authentication successful! Redirecting...'
    
    // Show success message
    toastStore.success('Successfully logged in with Google!')
    
    // Redirect to home page after a short delay
    setTimeout(() => {
      router.push('/')
    }, 1000)

  } catch (error) {
    console.error('Auth callback error:', error)
    message.value = 'Authentication failed. Please try again.'
    
    // Show error message
    toastStore.error('Authentication failed. Please try again.')
    
    // Redirect to login page after a short delay
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  }
})
</script>

<style scoped>
.auth-callback {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.loading-container {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  margin: 0;
  color: #666;
  font-size: 1.1rem;
}
</style>
