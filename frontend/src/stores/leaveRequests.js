import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/axios'

export const useLeaveRequestsStore = defineStore('leaveRequests', () => {
  // State
  const leaveRequests = ref([])
  const loading = ref(false)
  const error = ref(null)
  const highlightedRequests = ref(new Set()) // Track highlighted requests

  // Getters
  const pendingRequests = computed(() => 
    leaveRequests.value.filter(request => request.status === 'pending')
  )
  
  const approvedRequests = computed(() => 
    leaveRequests.value.filter(request => request.status === 'approved')
  )
  
  const rejectedRequests = computed(() => 
    leaveRequests.value.filter(request => request.status === 'rejected')
  )

  // Actions
  const fetchLeaveRequests = async () => {
    loading.value = true
    error.value = null
    try {
      console.log('Fetching leave requests...')
      const response = await api.get(`leave_requests`)
      console.log('Leave requests response:', response.data)
      leaveRequests.value = response.data.leave_requests || response.data
      return response.data.leave_requests || response.data
    } catch (err) {
      console.error('Error fetching leave requests:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch leave requests'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createLeaveRequest = async (requestData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`leave_requests`, requestData)
      // Refresh the list after creating
      await fetchLeaveRequests()
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create leave request'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateRequestStatus = async (requestId, status, reviewComment) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`leave_requests/${requestId}/status`, {
        status,
        review_comment: reviewComment
      })
      // Refresh the list after updating
      await fetchLeaveRequests()
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update request status'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const highlightRequest = (requestId) => {
    highlightedRequests.value.add(requestId)
    // Remove highlight after 5 seconds
    setTimeout(() => {
      highlightedRequests.value.delete(requestId)
    }, 5000)
  }

  const isHighlighted = (requestId) => {
    return highlightedRequests.value.has(requestId)
  }

  const clearHighlights = () => {
    highlightedRequests.value.clear()
  }

  return {
    // State
    leaveRequests,
    loading,
    error,
    highlightedRequests,
    
    // Getters
    pendingRequests,
    approvedRequests,
    rejectedRequests,
    
    // Actions
    fetchLeaveRequests,
    createLeaveRequest,
    updateRequestStatus,
    clearError,
    highlightRequest,
    isHighlighted,
    clearHighlights
  }
})
