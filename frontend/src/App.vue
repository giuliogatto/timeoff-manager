<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link>
      <template v-if="authStore.isAuthenticated">
        | <router-link to="/leave_requests">Leave Requests</router-link>
        | <span class="user-info">Welcome, {{ authStore.user?.name }}</span>
        | <NotificationCenter />
        | <button @click="logout" class="logout-btn">Logout</button>
      </template>
      <template v-else>
        | <router-link to="/login">Login</router-link>
        | <router-link to="/register">Register</router-link>
      </template>
    </nav>
    <router-view />
    <Toast />
  </div>
</template>

<script setup>
// Vue 3 Composition API with script setup
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import NotificationCenter from './components/NotificationCenter.vue'
import Toast from './components/Toast.vue'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  console.log('Timeoff Manager Frontend loaded!')
  authStore.initializeAuth()
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.user-info {
  color: #2c3e50;
  font-weight: bold;
}

.logout-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.logout-btn:hover {
  color: #c0392b;
}
</style>
