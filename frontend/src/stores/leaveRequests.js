import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useLeaveRequestsStore = defineStore('leaveRequests', () => {
  // State
  const leaveRequests = ref([])
  const loading = ref(false)
  const error = ref(null)

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

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/'

  // Actions
  const fetchLeaveRequests = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get(`${backendUrl}leave_requests`)
      leaveRequests.value = response.data
      return response.data
    } catch (err) {
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
      const response = await axios.post(`${backendUrl}leave_requests`, requestData)
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
      const response = await axios.put(`${backendUrl}leave_requests/${requestId}/status`, {
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

  return {
    // State
    leaveRequests,
    loading,
    error,
    
    // Getters
    pendingRequests,
    approvedRequests,
    rejectedRequests,
    backendUrl,
    
    // Actions
    fetchLeaveRequests,
    createLeaveRequest,
    updateRequestStatus,
    clearError
  }
})
