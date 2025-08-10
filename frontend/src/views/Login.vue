<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          placeholder="Enter your email"
        />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          placeholder="Enter your password"
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
    
    <div class="oauth-section">
      <p>Or login with:</p>
      <button @click="googleLogin" class="google-btn">
        Login with Google
      </button>
    </div>
    
    <p class="register-link">
      Don't have an account? <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/'

const handleLogin = async () => {
  loading.value = true
  try {
    const response = await axios.post(`${backendUrl}login`, {
      email: email.value,
      password: password.value
    })
    
    // Store token
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data))
    
    // Redirect to home
    router.push('/')
  } catch (error) {
    console.error('Login error:', error)
    alert('Login failed. Please check your credentials.')
  } finally {
    loading.value = false
  }
}

const googleLogin = async () => {
  try {
    const response = await axios.get(`${backendUrl}google/auth-url`)
    window.location.href = response.data.auth_url
  } catch (error) {
    console.error('Google OAuth error:', error)
    alert('Google OAuth not available.')
  }
}
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: bold;
  color: #2c3e50;
}

.form-group input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button {
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #3aa876;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.oauth-section {
  text-align: center;
  margin: 30px 0;
  padding: 20px;
  border-top: 1px solid #eee;
}

.google-btn {
  background-color: #4285f4;
  margin-top: 10px;
}

.google-btn:hover {
  background-color: #3367d6;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

.register-link a {
  color: #42b983;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
