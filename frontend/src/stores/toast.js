import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  const nextId = ref(1)

  const addToast = (message, type = 'info', duration = 5000) => {
    const id = nextId.value++
    const toast = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration
    }
    
    toasts.value.push(toast)
    
    // Auto remove after duration
    setTimeout(() => {
      removeToast(id)
    }, duration)
    
    return id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const clearToasts = () => {
    toasts.value = []
  }

  // Convenience methods
  const success = (message, duration) => addToast(message, 'success', duration)
  const error = (message, duration) => addToast(message, 'error', duration)
  const warning = (message, duration) => addToast(message, 'warning', duration)
  const info = (message, duration) => addToast(message, 'info', duration)

  return {
    toasts,
    addToast,
    removeToast,
    clearToasts,
    success,
    error,
    warning,
    info
  }
})
