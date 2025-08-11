import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('../views/AuthCallback.vue')
  },
  {
    path: '/leave_requests',
    name: 'LeaveRequests',
    component: () => import('../views/LeaveRequests.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // If not authenticated, redirect to login
    if (!authStore.isAuthenticated) {
      console.log('🔐 Route requires auth but user not authenticated, redirecting to login')
      next('/login')
      return
    }
    
    // If authenticated but token might be expired, validate it
    if (authStore.token) {
      // For now, we'll let the axios interceptor handle token validation
      // In a more robust implementation, you could validate the token here
      next()
    } else {
      console.log('🔐 Token not found, redirecting to login')
      next('/login')
    }
  } else {
    // If user is authenticated and trying to access login/register, redirect to home
    if (authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      console.log('🔐 User already authenticated, redirecting to home')
      next('/')
      return
    }
    next()
  }
})

export default router
