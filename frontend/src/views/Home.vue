<template>
  <div class="home">
    <h1>{{ $t('home.welcome') }}</h1>
    <p>{{ $t('home.description') }}</p>
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

const { t } = useI18n()
const backendUrl = ref(import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/')

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
