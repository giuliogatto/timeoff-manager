import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const socket = ref(null)
  const isConnected = ref(false)
  const notifications = ref([])
  const connectionError = ref(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  // Getters
  const hasNotifications = computed(() => notifications.value.length > 0)
  const unreadNotifications = computed(() => notifications.value.filter(n => !n.read).length)

  const authStore = useAuthStore()
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/'

  // Actions
  const connect = () => {
    console.log('Attempting to connect to WebSocket...')
    console.log('Auth token available:', !!authStore.token)
    console.log('Token:', authStore.token ? authStore.token.substring(0, 50) + '...' : 'None')
    
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    if (!authStore.token) {
      console.log('No auth token available for WebSocket connection')
      return
    }

    try {
      // Convert HTTP URL to WebSocket URL
      const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://')
      const fullWsUrl = `${wsUrl}ws?token=${authStore.token}`
      
      console.log('Connecting to WebSocket:', fullWsUrl)
      
      socket.value = new WebSocket(fullWsUrl)
      
      socket.value.onopen = () => {
        console.log('✅ WebSocket connected successfully!')
        isConnected.value = true
        connectionError.value = null
        reconnectAttempts.value = 0
        
        // Start ping interval to keep connection alive
        startPingInterval()
      }
      
      socket.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      socket.value.onclose = (event) => {
        console.log('❌ WebSocket disconnected:', event.code, event.reason)
        isConnected.value = false
        stopPingInterval()
        
        // Handle reconnection
        if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.value++
            console.log(`🔄 Reconnecting... Attempt ${reconnectAttempts.value}`)
            connect()
          }, 2000 * reconnectAttempts.value) // Exponential backoff
        }
      }
      
      socket.value.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        connectionError.value = 'Connection failed'
      }
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      connectionError.value = error.message
    }
  }

  const disconnect = () => {
    if (socket.value) {
      stopPingInterval()
      socket.value.close(1000, 'User disconnected')
      socket.value = null
    }
    isConnected.value = false
  }

  const sendMessage = (message) => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  const ping = () => {
    sendMessage({ type: 'ping' })
  }

  const getConnectedUsers = () => {
    sendMessage({ type: 'get_connected_users' })
  }

  const handleMessage = (message) => {
    console.log('📨 WebSocket message received:', message)
    
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket connection established:', message.message)
        break
        
      case 'notification':
        addNotification(message)
        break
        
      case 'manager_notification':
        addNotification(message)
        break
        
      case 'pong':
        // Handle ping response
        break
        
      case 'connected_users':
        console.log('Connected users:', message.users)
        break
        
      case 'error':
        console.error('WebSocket error:', message.message)
        break
        
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  const addNotification = (message) => {
    console.log('🔔 Adding notification:', message)
    
    const notification = {
      id: Date.now() + Math.random(),
      type: message.notification_type || message.type,
      data: message.data,
      timestamp: message.timestamp || new Date().toISOString(),
      read: false,
      message: generateNotificationMessage(message)
    }
    
    console.log('📝 Generated notification:', notification)
    
    notifications.value.unshift(notification)
    
    // Keep only last 50 notifications
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }
    
    // Show browser notification if supported
    if ('Notification' in window && Notification.permission === 'granted') {
      console.log('🖥️ Showing browser notification')
      new Notification(notification.message, {
        body: notification.data?.reason || 'Check the application for details',
        icon: '/favicon.ico'
      })
    } else {
      console.log('⚠️ Browser notifications not available or not granted')
    }
  }

  const generateNotificationMessage = (message) => {
    const data = message.data
    const status = data?.status
    const requestType = data?.request_type
    const reviewerName = data?.reviewer_name
    const notificationType = message.notification_type
    
    if (message.type === 'manager_notification') {
      if (notificationType === 'new_leave_request') {
        return `New ${requestType} request from ${data?.user_name || 'a user'}`
      } else if (notificationType === 'leave_request_status_changed') {
        return `${data?.user_name || 'A user'}'s ${requestType} request was ${status} by ${reviewerName}`
      }
    } else {
      return `Your ${requestType} request was ${status} by ${reviewerName}`
    }
    
    return 'New notification received'
  }

  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(notification => {
      notification.read = true
    })
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  const removeNotification = (notificationId) => {
    notifications.value = notifications.value.filter(n => n.id !== notificationId)
  }

  // Ping interval management
  let pingInterval = null

  const startPingInterval = () => {
    if (pingInterval) clearInterval(pingInterval)
    pingInterval = setInterval(() => {
      if (isConnected.value) {
        ping()
      }
    }, 30000) // Ping every 30 seconds
  }

  const stopPingInterval = () => {
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }
  }

  // Request notification permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return Notification.permission === 'granted'
  }

  return {
    // State
    socket,
    isConnected,
    notifications,
    connectionError,
    reconnectAttempts,
    
    // Getters
    hasNotifications,
    unreadNotifications,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    ping,
    getConnectedUsers,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearNotifications,
    removeNotification,
    requestNotificationPermission
  }
})
