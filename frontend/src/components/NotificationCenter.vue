<template>
  <div class="notification-center">
    <!-- Notification Bell Icon -->
    <div class="notification-bell" @click="toggleNotifications">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
        <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
      </svg>
      
      <!-- Notification Badge -->
      <span v-if="websocketStore.unreadNotifications > 0" class="notification-badge">
        {{ websocketStore.unreadNotifications > 99 ? '99+' : websocketStore.unreadNotifications }}
      </span>
      
      <!-- Connection Status Indicator -->
      <div class="connection-status" :class="{ connected: websocketStore.isConnected }"></div>
    </div>

    <!-- Notification Panel -->
    <div v-if="showNotifications" class="notification-panel">
      <div class="notification-header">
        <h3>{{ $t('notifications.title') }}</h3>
        <div class="notification-actions">
          <button @click="markAllAsRead" class="action-btn">
            {{ $t('notifications.markAllAsRead') }}
          </button>
          <button @click="clearNotifications" class="action-btn">
            {{ $t('notifications.clearAll') }}
          </button>
        </div>
      </div>

      <!-- Connection Status -->
      <div class="connection-info">
        <span class="status-dot" :class="{ connected: websocketStore.isConnected }"></span>
        {{ websocketStore.isConnected ? $t('notifications.connected') : $t('notifications.disconnected') }}
        <button v-if="!websocketStore.isConnected" @click="reconnect" class="reconnect-btn">
          {{ $t('notifications.reconnect') }}
        </button>
      </div>

      <!-- Notifications List -->
      <div class="notifications-list">
        <div v-if="websocketStore.notifications.length === 0" class="no-notifications">
          <p>{{ $t('notifications.noNotifications') }}</p>
        </div>
        
        <div 
          v-for="notification in websocketStore.notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.read }"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-content">
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">
              {{ formatTime(notification.timestamp) }}
            </div>
          </div>
          <button @click.stop="removeNotification(notification.id)" class="remove-btn">
            ×
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWebSocketStore } from '../stores/websocket'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()

const websocketStore = useWebSocketStore()
const authStore = useAuthStore()

const showNotifications = ref(false)

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
}

const markAsRead = (notificationId) => {
  websocketStore.markAsRead(notificationId)
}

const markAllAsRead = () => {
  websocketStore.markAllAsRead()
}

const clearNotifications = () => {
  websocketStore.clearNotifications()
}

const removeNotification = (notificationId) => {
  websocketStore.removeNotification(notificationId)
}

const reconnect = () => {
  websocketStore.connect()
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // Less than 1 minute
    return 'Just now'
  } else if (diff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(diff / 60000)
    return `${minutes}m ago`
  } else if (diff < 86400000) { // Less than 1 day
    const hours = Math.floor(diff / 3600000)
    return `${hours}h ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Close notifications when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.notification-center')) {
    showNotifications.value = false
  }
}

onMounted(async () => {
  // Request notification permission
  await websocketStore.requestNotificationPermission()
  
  // Connect WebSocket when user is authenticated
  if (authStore.isAuthenticated) {
    websocketStore.connect()
  }
  
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  websocketStore.disconnect()
})
</script>

<style scoped>
.notification-center {
  position: relative;
  display: inline-block;
}

.notification-bell {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
  color: #2c3e50;
}

.notification-bell:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  min-width: 18px;
  height: 18px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.connection-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #95a5a6;
  border: 2px solid white;
}

.connection-status.connected {
  background-color: #27ae60;
}

.notification-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 500px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.notification-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #e3f2fd;
}

.connection-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 12px;
  color: #666;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #95a5a6;
}

.status-dot.connected {
  background-color: #27ae60;
}

.reconnect-btn {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  font-size: 12px;
  text-decoration: underline;
}

.notifications-list {
  max-height: 350px;
  overflow-y: auto;
}

.no-notifications {
  padding: 40px;
  text-align: center;
  color: #666;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #e3f2fd;
}

.notification-item.unread:hover {
  background-color: #bbdefb;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: #666;
}

.remove-btn {
  background: none;
  border: none;
  color: #95a5a6;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  margin-left: 8px;
  line-height: 1;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #e74c3c;
}

/* Scrollbar styling */
.notifications-list::-webkit-scrollbar {
  width: 6px;
}

.notifications-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.notifications-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.notifications-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
