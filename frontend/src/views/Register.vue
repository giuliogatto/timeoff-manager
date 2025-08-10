<template>
  <div class="register">
    <h2>{{ $t('auth.register') }}</h2>
    <form @submit.prevent="handleRegister" class="register-form">
      <div class="form-group">
        <label for="name">{{ $t('auth.fullName') }}:</label>
        <input 
          type="text" 
          id="name" 
          v-model="name" 
          required 
          :placeholder="$t('auth.fullNamePlaceholder')"
        />
      </div>
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
      <div class="form-group">
        <label for="confirmPassword">{{ $t('auth.confirmPassword') }}:</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          required 
          :placeholder="$t('auth.confirmPasswordPlaceholder')"
        />
      </div>
      <button type="submit" :disabled="authStore.loading || !passwordsMatch">
        {{ authStore.loading ? $t('auth.registering') : $t('auth.register') }}
      </button>
    </form>
    
    <p v-if="!passwordsMatch && confirmPassword" class="error">
      {{ $t('auth.passwordsDoNotMatch') }}
    </p>
    
    <p class="login-link">
      {{ $t('auth.alreadyHaveAccount') }} <router-link to="/login">{{ $t('auth.loginHere') }}</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()

const router = useRouter()
const authStore = useAuthStore()
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const passwordsMatch = computed(() => {
  return password.value === confirmPassword.value
})

const handleRegister = async () => {
  if (!passwordsMatch.value) {
    alert('Passwords do not match')
    return
  }
  
  try {
    await authStore.register(name.value, email.value, password.value)
    alert('Registration successful! Please check your email to confirm your account.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    if (error.response?.data?.detail) {
      alert(`Registration failed: ${error.response.data.detail}`)
    } else {
      alert('Registration failed. Please try again.')
    }
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
