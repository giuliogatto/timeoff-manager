<template>
  <div class="toast-container">
    <TransitionGroup name="toast" tag="div">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="toastStore.removeToast(toast.id)"
      >
        <div class="toast-content">
          <span class="toast-message">{{ toast.message }}</span>
          <button class="toast-close" @click.stop="toastStore.removeToast(toast.id)">
            ×
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  pointer-events: none;
}

.toast {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 10px;
  min-width: 300px;
  max-width: 400px;
  pointer-events: auto;
  border-left: 4px solid #3498db;
}

.toast-success {
  border-left-color: #27ae60;
}

.toast-error {
  border-left-color: #e74c3c;
}

.toast-warning {
  border-left-color: #f39c12;
}

.toast-info {
  border-left-color: #3498db;
}

.toast-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.toast-message {
  flex: 1;
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  margin-left: 12px;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.toast-close:hover {
  background-color: #ecf0f1;
  color: #2c3e50;
}

/* Toast animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
