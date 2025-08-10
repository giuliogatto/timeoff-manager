<template>
  <div class="register">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister" class="register-form">
      <div class="form-group">
        <label for="name">Full Name:</label>
        <input 
          type="text" 
          id="name" 
          v-model="name" 
          required 
          placeholder="Enter your full name"
        />
      </div>
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
      <div class="form-group">
        <label for="confirmPassword">Confirm Password:</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          required 
          placeholder="Confirm your password"
        />
      </div>
      <button type="submit" :disabled="loading || !passwordsMatch">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    
    <p v-if="!passwordsMatch && confirmPassword" class="error">
      Passwords do not match
    </p>
    
    <p class="login-link">
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/'

const passwordsMatch = computed(() => {
  return password.value === confirmPassword.value
})

const handleRegister = async () => {
  if (!passwordsMatch.value) {
    alert('Passwords do not match')
    return
  }
  
  loading.value = true
  try {
    const response = await axios.post(`${backendUrl}register`, {
      name: name.value,
      email: email.value,
      password: password.value
    })
    
    alert('Registration successful! Please check your email to confirm your account.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    if (error.response?.data?.detail) {
      alert(`Registration failed: ${error.response.data.detail}`)
    } else {
      alert('Registration failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.register-form {
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

.error {
  color: #e74c3c;
  text-align: center;
  margin: 10px 0;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link a {
  color: #42b983;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
