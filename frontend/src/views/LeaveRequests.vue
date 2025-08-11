<template>
  <div class="leave-requests">
    <div class="header">
      <h2>{{ $t('leaveRequests.title') }}</h2>
      <button @click="showCreateForm = true" v-if="!authStore.isManager" class="create-btn">
        {{ $t('leaveRequests.createNewRequest') }}
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="leaveRequestsStore.error" class="error-message">
      {{ leaveRequestsStore.error }}
      <button @click="leaveRequestsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="leaveRequestsStore.loading" class="loading">
      {{ $t('leaveRequests.loading') }}
    </div>

    <!-- Leave Requests List -->
    <div v-else-if="leaveRequestsStore.leaveRequests.length > 0" class="requests-container">
      <!-- Pending Requests -->
      <div v-if="leaveRequestsStore.pendingRequests.length > 0" class="request-section">
        <h3>{{ $t('leaveRequests.pendingRequests') }}</h3>
        <div class="requests-grid">
          <LeaveRequestCard
            v-for="request in leaveRequestsStore.pendingRequests"
            :key="request.id"
            :request="{ ...request, status: 'pending' }"
            :is-highlighted="leaveRequestsStore.isHighlighted(request.id)"
            :show-actions="authStore.isManager"
            @approve="approveRequest"
            @reject="rejectRequest"
          />
        </div>
      </div>

      <!-- Approved Requests -->
      <div v-if="leaveRequestsStore.approvedRequests.length > 0" class="request-section">
        <h3>{{ $t('leaveRequests.approvedRequests') }}</h3>
        <div class="requests-grid">
          <LeaveRequestCard
            v-for="request in leaveRequestsStore.approvedRequests"
            :key="request.id"
            :request="{ ...request, status: 'approved' }"
            :is-highlighted="leaveRequestsStore.isHighlighted(request.id)"
            :show-actions="false"
          />
        </div>
      </div>

      <!-- Rejected Requests -->
      <div v-if="leaveRequestsStore.rejectedRequests.length > 0" class="request-section">
        <h3>{{ $t('leaveRequests.rejectedRequests') }}</h3>
        <div class="requests-grid">
          <LeaveRequestCard
            v-for="request in leaveRequestsStore.rejectedRequests"
            :key="request.id"
            :request="{ ...request, status: 'rejected' }"
            :is-highlighted="leaveRequestsStore.isHighlighted(request.id)"
            :show-actions="false"
          />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('leaveRequests.noRequestsFound') }}</p>
    </div>

    <!-- Create Request Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click="showCreateForm = false">
      <div class="modal" @click.stop>
        <h3>{{ $t('leaveRequests.createRequest') }}</h3>
        <form @submit.prevent="createRequest" class="create-form">
          <div class="form-group">
            <label for="requestType">{{ $t('leaveRequests.requestType') }}:</label>
            <select id="requestType" v-model="newRequest.request_type" required>
              <option value="timeoff">{{ $t('leaveRequests.timeoff') }}</option>
              <option value="permission">{{ $t('leaveRequests.permission') }}</option>
            </select>
          </div>

          <div v-if="newRequest.request_type === 'timeoff'" class="form-group">
            <label for="startDate">{{ $t('leaveRequests.startDate') }}:</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="newRequest.start_date" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'timeoff'" class="form-group">
            <label for="endDate">{{ $t('leaveRequests.endDate') }}:</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="newRequest.end_date" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'permission'" class="form-group">
            <label for="startDateTime">{{ $t('leaveRequests.startDateTime') }}:</label>
            <input 
              type="datetime-local" 
              id="startDateTime" 
              v-model="newRequest.start_datetime" 
              required
            />
          </div>

          <div v-if="newRequest.request_type === 'permission'" class="form-group">
            <label for="endDateTime">{{ $t('leaveRequests.endDateTime') }}:</label>
            <input 
              type="datetime-local" 
              id="endDateTime" 
              v-model="newRequest.end_datetime" 
              required
            />
          </div>

          <div class="form-group">
            <label for="reason">{{ $t('common.reason') }}:</label>
            <textarea 
              id="reason" 
              v-model="newRequest.reason" 
              rows="3"
              :placeholder="$t('leaveRequests.reasonPlaceholder')"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="cancel-btn">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" :disabled="leaveRequestsStore.loading" class="submit-btn">
              {{ leaveRequestsStore.loading ? $t('leaveRequests.creating') : $t('leaveRequests.createRequest') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useLeaveRequestsStore } from '../stores/leaveRequests'
import LeaveRequestCard from '../components/LeaveRequestsCard.vue'

const { t } = useI18n()

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