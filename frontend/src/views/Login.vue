<template>
  <div class="login">
    <h2>{{ $t('auth.login') }}</h2>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="email">{{ $t('auth.email') }}:</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          :placeholder="$t('auth.emailPlaceholder')"
        />
      </div>
      <div class="form-group">
        <label for="password">{{ $t('auth.password') }}:</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          :placeholder="$t('auth.passwordPlaceholder')"
        />
      </div>
      <button type="submit" :disabled="authStore.loading">
        {{ authStore.loading ? $t('auth.loggingIn') : $t('auth.login') }}
      </button>
    </form>
    
    <div class="oauth-section">
      <p>{{ $t('auth.orLoginWith') }}</p>
      <button @click="googleLogin" class="google-btn">
        {{ $t('auth.loginWithGoogle') }}
      </button>
    </div>
    
    <p class="register-link">
      {{ $t('auth.dontHaveAccount') }} <router-link to="/register">{{ $t('auth.registerHere') }}</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (error) {
    console.error('Login error:', error)
    alert('Login failed. Please check your credentials.')
  }
}

const googleLogin = async () => {
  try {
    await authStore.googleLogin()
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
