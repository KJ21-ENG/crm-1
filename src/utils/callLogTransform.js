// Utility functions for call log data transformation

export const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return '';
  
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // Format based on length
  if (cleaned.length === 10) {
    return `+1${cleaned}`;
  } else if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+${cleaned}`;
  }
  
  return phoneNumber;
};

export const formatCallDuration = (durationInSeconds) => {
  if (!durationInSeconds || durationInSeconds === 0) {
    return 'N/A';
  }
  
  const hours = Math.floor(durationInSeconds / 3600);
  const minutes = Math.floor((durationInSeconds % 3600) / 60);
  const seconds = durationInSeconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  } else {
    return `${seconds}s`;
  }
};

export const getCallTypeIcon = (type) => {
  switch (type?.toLowerCase()) {
    case 'incoming':
      return '📞';
    case 'outgoing':
      return '📤';
    case 'missed':
      return '❌';
    default:
      return '📱';
  }
};

export const getCallStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return '#4CAF50'; // Green
    case 'no answer':
    case 'missed':
      return '#FF9800'; // Orange
    case 'failed':
    case 'busy':
      return '#F44336'; // Red
    case 'in progress':
      return '#2196F3'; // Blue
    default:
      return '#757575'; // Gray
  }
};

export const getSyncStatusInfo = (syncStatus) => {
  switch (syncStatus?.toLowerCase()) {
    case 'synced':
      return {
        text: 'Synced',
        color: '#4CAF50',
        icon: '✅'
      };
    case 'pending':
      return {
        text: 'Pending',
        color: '#FF9800',
        icon: '⏳'
      };
    case 'failed':
      return {
        text: 'Failed',
        color: '#F44336',
        icon: '❌'
      };
    default:
      return {
        text: 'Unknown',
        color: '#757575',
        icon: '❓'
      };
  }
};

export const generateCallLogId = (phoneNumber, timestamp) => {
  return `mobile_${phoneNumber}_${timestamp}`;
};

export const isValidPhoneNumber = (phoneNumber) => {
  const phoneRegex = /^[\+]?[1-9][\d]{3,14}$/;
  return phoneRegex.test(phoneNumber?.replace(/\D/g, ''));
}; 