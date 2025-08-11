<template>
    <div 
      :class="[
        'request-card',
        request.status,
        { 'highlighted': isHighlighted }
      ]"
    >
      <div class="request-header">
        <span class="request-type">{{ request.request_type }}</span>
        <span :class="['status', request.status]">{{ getStatusText(request.status) }}</span>
      </div>
      <div class="request-details">
        <p><strong>{{ $t('common.user') }}:</strong> {{ request.user_name || $t('common.unknown') }}</p>
        <p v-if="request.request_type === 'timeoff'">
          <strong>{{ $t('leaveRequests.dates') }}:</strong> {{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}
        </p>
        <p v-else>
          <strong>{{ $t('common.time') }}:</strong> {{ formatDateTime(request.start_datetime) }} - {{ formatDateTime(request.end_datetime) }}
        </p>
        <p v-if="request.reason"><strong>{{ $t('common.reason') }}:</strong> {{ request.reason }}</p>
        <p v-if="request.status === 'pending'">
          <strong>{{ $t('common.created') }}:</strong> {{ formatDateTime(request.created_at) }}
        </p>
        <p v-else>
          <strong>{{ getReviewedAtLabel(request.status) }}:</strong> {{ formatDateTime(request.reviewed_at) }}
        </p>
      </div>
      <div v-if="showActions && request.status === 'pending'" class="request-actions">
        <button @click="$emit('approve', request.id)" class="approve-btn">
          {{ $t('common.approve') }}
        </button>
        <button @click="$emit('reject', request.id)" class="reject-btn">
          {{ $t('common.reject') }}
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useI18n } from 'vue-i18n'
  
  const { t } = useI18n()
  
  const props = defineProps({
    request: {
      type: Object,
      required: true
    },
    isHighlighted: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['approve', 'reject'])
  
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }
  
  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'N/A'
    return new Date(dateTimeString).toLocaleString()
  }
  
  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return t('common.pending')
      case 'approved':
        return t('common.approved')
      case 'rejected':
        return t('common.rejected')
      default:
        return status
    }
  }
  
  const getReviewedAtLabel = (status) => {
    return status === 'approved' ? t('common.approved') : t('common.rejected')
  }
  </script>
  
  <style scoped>
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
  </style>