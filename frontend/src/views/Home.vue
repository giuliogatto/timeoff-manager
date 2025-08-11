<template>
  <div class="home">
    <h1>{{ $t('home.welcome') }}</h1>
    <p>{{ $t('home.description') }}</p>
    
    <!-- Debug section - remove in production -->
    <!-- <div v-if="authStore.isAuthenticated" class="debug-section">
      <h3>🔧 Debug Tools</h3>
      <button @click="testTokenExpiration" class="debug-btn">
        Test Token Expiration
      </button>
      <p class="debug-info">
        Logged in as: {{ authStore.user?.name }} ({{ authStore.user?.role }})
      </p>
    </div> -->
    
    <div class="features">
      <div class="feature">
        <h3>{{ $t('home.features.easyRequestManagement') }}</h3>
        <p>{{ $t('home.features.easyRequestManagementDesc') }}</p>
      </div>
      <div class="feature">
        <h3>{{ $t('home.features.managerApproval') }}</h3>
        <p>{{ $t('home.features.managerApprovalDesc') }}</p>
      </div>
      <div class="feature">
        <h3>{{ $t('home.features.googleOAuth') }}</h3>
        <p>{{ $t('home.features.googleOAuthDesc') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()
const authStore = useAuthStore()
const backendUrl = ref(import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/')

const testTokenExpiration = async () => {
  await authStore.testTokenExpiration()
}

onMounted(() => {
  console.log('Backend URL:', backendUrl.value)
})
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.debug-section {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin: 20px 0;
  border: 1px solid #ddd;
}

.debug-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.debug-btn:hover {
  background: #ff5252;
}

.debug-info {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.feature {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-align: center;
}

.feature h3 {
  color: #42b983;
  margin-bottom: 10px;
}
</style>
