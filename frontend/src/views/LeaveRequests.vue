<template>
  <div class="leave-requests">
    <div class="header">
      <h2>Leave Requests</h2>
      <button @click="showCreateForm = true" class="create-btn">
        Create New Request
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="leaveRequestsStore.error" class="error-message">
      {{ leaveRequestsStore.error }}
      <button @click="leaveRequestsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="leaveRequestsStore.loading" class="loading">
      Loading leave requests...
    </div>

    <!-- Leave Requests List -->
    <div v-else-if="leaveRequestsStore.leaveRequests.length > 0" class="requests-container">
      <!-- Pending Requests -->
      <div v-if="leaveRequestsStore.pendingRequests.length > 0" class="request-section">
        <h3>Pending Requests</h3>
        <div class="requests-grid">
          <div 
            v-for="request in leaveRequestsStore.pendingRequests" 
            :key="request.id" 
            :class="[
              'request-card',
              'pending',
              { 'highlighted': leaveRequestsStore.isHighlighted(request.id) }
            ]"
          >
            <div class="request-header">
              <span class="request-type">{{ request.request_type }}</span>
              <span class="status pending">Pending</span>
            </div>
            <div class="request-details">
              <p><strong>User:</strong> {{ request.user_name || 'Unknown' }}</p>
              <p v-if="request.request_type === 'timeoff'">
                <strong>Dates:</strong> {{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}
              </p>
              <p v-else>
                <strong>Time:</strong> {{ formatDateTime(request.start_datetime) }} - {{ formatDateTime(request.end_datetime) }}
              </p>
              <p v-if="request.reason"><strong>Reason:</strong> {{ request.reason }}</p>
              <p><strong>Created:</strong> {{ formatDateTime(request.created_at) }}</p>
            </div>
            <div v-if="authStore.isManager" class="request-actions">
              <button @click="approveRequest(request.id)" class="approve-btn">
                Approve
              </button>
              <button @click="rejectRequest(request.id)" class="reject-btn">
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Approved Requests -->
      <div v-if="leaveRequestsStore.approvedRequests.length > 0" class="request-section">
        <h3>Approved Requests</h3>
        <div class="requests-grid">
          <div 
            v-for="request in leaveRequestsStore.approvedRequests" 
            :key="request.id" 
            :class="[
              'request-card',
              'approved',
              { 'highlighted': leaveRequestsStore.isHighlighted(request.id) }
            ]"
          >
            <div class="request-header">
              <span class="request-type">{{ request.request_type }}</span>
              <span class="status approved">Approved</span>
            </div>
            <div class="request-details">
              <p><strong>User:</strong> {{ request.user_name || 'Unknown' }}</p>
              <p v-if="request.request_type === 'timeoff'">
                <strong>Dates:</strong> {{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}
              </p>
              <p v-else>
                <strong>Time:</strong> {{ formatDateTime(request.start_datetime) }} - {{ formatDateTime(request.end_datetime) }}
              </p>
              <p v-if="request.reason"><strong>Reason:</strong> {{ request.reason }}</p>
              <p><strong>Approved:</strong> {{ formatDateTime(request.reviewed_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Rejected Requests -->
      <div v-if="leaveRequestsStore.rejectedRequests.length > 0" class="request-section">
        <h3>Rejected Requests</h3>
        <div class="requests-grid">
          <div 
            v-for="request in leaveRequestsStore.rejectedRequests" 
            :key="request.id" 
            :class="[
              'request-card',
              'rejected',
              { 'highlighted': leaveRequestsStore.isHighlighted(request.id) }
            ]"
          >
            <div class="request-header">
              <span class="request-type">{{ request.request_type }}</span>
              <span class="status rejected">Rejected</span>
            </div>
            <div class="request-details">
              <p><strong>User:</strong> {{ request.user_name || 'Unknown' }}</p>
              <p v-if="request.request_type === 'timeoff'">
                <strong>Dates:</strong> {{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}
              </p>
              <p v-else>
                <strong>Time:</strong> {{ formatDateTime(request.start_datetime) }} - {{ formatDateTime(request.end_datetime) }}
              </p>
              <p v-if="request.reason"><strong>Reason:</strong> {{ request.reason }}</p>
              <p><strong>Rejected:</strong> {{ formatDateTime(request.reviewed_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No leave requests found.</p>
    </div>

    <!-- Create Request Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click="showCreateForm = false">
      <div class="modal" @click.stop>
        <h3>Create Leave Request</h3>
        <form @submit.prevent="createRequest" class="create-form">
          <div class="form-group">
            <label for="requestType">Request Type:</label>
            <select id="requestType" v-model="newRequest.request_type" required>
              <option value="timeoff">Time Off (Days)</option>
              <option value="permission">Permission (Hours)</option>
            </select>
          </div>

          <div v-if="newRequest.request_type === 'timeoff'" class="form-group">
            <label for="startDate">Start Date:</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="newRequest.start_date" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'timeoff'" class="form-group">
            <label for="endDate">End Date:</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="newRequest.end_date" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'permission'" class="form-group">
            <label for="startDateTime">Start Date & Time:</label>
            <input 
              type="datetime-local" 
              id="startDateTime" 
              v-model="newRequest.start_datetime" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'permission'" class="form-group">
            <label for="endDateTime">End Date & Time:</label>
            <input 
              type="datetime-local" 
              id="endDateTime" 
              v-model="newRequest.end_datetime" 
              required
            />
          </div>

          <div class="form-group">
            <label for="reason">Reason:</label>
            <textarea 
              id="reason" 
              v-model="newRequest.reason" 
              rows="3"
              placeholder="Please provide a reason for your request..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" :disabled="leaveRequestsStore.loading" class="submit-btn">
              {{ leaveRequestsStore.loading ? 'Creating...' : 'Create Request' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLeaveRequestsStore } from '../stores/leaveRequests'

const authStore = useAuthStore()
const leaveRequestsStore = useLeaveRequestsStore()

const showCreateForm = ref(false)
const newRequest = ref({
  request_type: 'timeoff',
  start_date: '',
  end_date: '',
  start_datetime: '',
  end_datetime: '',
  reason: ''
})

onMounted(async () => {
  console.log('LeaveRequests mounted')
  console.log('Auth store state:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user,
    isManager: authStore.isManager
  })
  
  if (authStore.isAuthenticated) {
    console.log('User is authenticated, fetching leave requests...')
    await leaveRequestsStore.fetchLeaveRequests()
  } else {
    console.log('User is not authenticated')
  }
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'N/A'
  return new Date(dateTimeString).toLocaleString()
}

const createRequest = async () => {
  try {
    const requestData = {
      request_type: newRequest.value.request_type,
      reason: newRequest.value.reason
    }

    if (newRequest.value.request_type === 'timeoff') {
      requestData.start_date = newRequest.value.start_date
      requestData.end_date = newRequest.value.end_date
    } else {
      requestData.start_datetime = newRequest.value.start_datetime
      requestData.end_datetime = newRequest.value.end_datetime
    }

    await leaveRequestsStore.createLeaveRequest(requestData)
    showCreateForm.value = false
    resetForm()
  } catch (error) {
    console.error('Failed to create request:', error)
  }
}

const approveRequest = async (requestId) => {
  try {
    await leaveRequestsStore.updateRequestStatus(requestId, 'approved')
  } catch (error) {
    console.error('Failed to approve request:', error)
  }
}

const rejectRequest = async (requestId) => {
  try {
    await leaveRequestsStore.updateRequestStatus(requestId, 'rejected')
  } catch (error) {
    console.error('Failed to reject request:', error)
  }
}

const resetForm = () => {
  newRequest.value = {
    request_type: 'timeoff',
    start_date: '',
    end_date: '',
    start_datetime: '',
    end_datetime: '',
    reason: ''
  }
}
</script>

<style scoped>
.leave-requests {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.create-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.create-btn:hover {
  background-color: #3aa876;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  color: #c33;
  font-size: 20px;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.request-section {
  margin-bottom: 40px;
}

.request-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
}

.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.request-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.request-card.pending {
  border-left: 4px solid #f39c12;
}

.request-card.approved {
  border-left: 4px solid #27ae60;
}

.request-card.rejected {
  border-left: 4px solid #e74c3c;
}

.request-card.highlighted {
  animation: highlight-pulse 2s ease-in-out;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  border: 2px solid #3498db;
}

@keyframes highlight-pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  }
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.request-type {
  background-color: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  text-transform: uppercase;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.pending {
  background-color: #f39c12;
  color: white;
}

.status.approved {
  background-color: #27ae60;
  color: white;
}

.status.rejected {
  background-color: #e74c3c;
  color: white;
}

.request-details p {
  margin: 8px 0;
  color: #2c3e50;
}

.request-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.approve-btn {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.approve-btn:hover {
  background-color: #229954;
}

.reject-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.reject-btn:hover {
  background-color: #c0392b;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #666;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: bold;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.cancel-btn {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn:hover {
  background-color: #7f8c8d;
}

.submit-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn:hover:not(:disabled) {
  background-color: #3aa876;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
