<template>
  <div class="home">
    <h1>Welcome to Timeoff Manager</h1>
    <p>Manage your time-off requests efficiently</p>
    <div class="features">
      <div class="feature">
        <h3>Easy Request Management</h3>
        <p>Submit and track your time-off requests</p>
      </div>
      <div class="feature">
        <h3>Manager Approval</h3>
        <p>Streamlined approval process for managers</p>
      </div>
      <div class="feature">
        <h3>Google OAuth</h3>
        <p>Quick login with your Google account</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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
