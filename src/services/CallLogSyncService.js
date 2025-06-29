import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import ApiService from './ApiService';
import CRMAuthService from './CRMAuthService';

class CallLogSyncService {
  constructor() {
    this.syncQueue = [];
    this.isSyncing = false;
  }

  async getDeviceCallLogs() {
    try {
      // This will be implemented with actual call log library
      // For now, return empty array
      console.log('Getting device call logs...');
      return [];
    } catch (error) {
      console.error('Failed to get device call logs:', error);
      throw error;
    }
  }

  async getNewCallLogs() {
    try {
      const lastSyncTime = await AsyncStorage.getItem('last_sync_time');
      const cutoffTime = lastSyncTime ? new Date(lastSyncTime) : new Date(Date.now() - 24 * 60 * 60 * 1000); // Last 24 hours
      
      const allCallLogs = await this.getDeviceCallLogs();
      
      // Filter for new call logs since last sync
      const newCallLogs = allCallLogs.filter(log => 
        new Date(log.date) > cutoffTime
      );
      
      return newCallLogs;
    } catch (error) {
      console.error('Failed to get new call logs:', error);
      throw error;
    }
  }

  transformCallLogForCRM(callLog) {
    // Transform Android call log format to CRM format
    return {
      id: `mobile_${callLog.phoneNumber}_${callLog.timestamp}`,
      from: callLog.type === 'OUTGOING' ? 'self' : callLog.phoneNumber,
      to: callLog.type === 'OUTGOING' ? callLog.phoneNumber : 'self',
      type: callLog.type === 'INCOMING' ? 'Incoming' : 'Outgoing',
      status: this.mapCallStatus(callLog),
      duration: callLog.duration || 0,
      start_time: new Date(callLog.timestamp).toISOString(),
      end_time: callLog.duration ? 
        new Date(callLog.timestamp + (callLog.duration * 1000)).toISOString() : 
        new Date(callLog.timestamp).toISOString(),
      telephony_medium: 'Mobile App',
      caller: callLog.type === 'INCOMING' ? callLog.phoneNumber : CRMAuthService.getCurrentUser()?.email,
      receiver: callLog.type === 'OUTGOING' ? callLog.phoneNumber : CRMAuthService.getCurrentUser()?.email,
    };
  }

  mapCallStatus(callLog) {
    if (callLog.type === 'MISSED') {
      return 'No Answer';
    } else if (callLog.duration > 0) {
      return 'Completed';
    } else {
      return 'Failed';
    }
  }

  async checkNetworkConditions() {
    const netInfo = await NetInfo.fetch();
    const wifiOnlySync = await AsyncStorage.getItem('wifi_only_sync');
    
    if (wifiOnlySync === 'true' && netInfo.type !== 'wifi') {
      throw new Error('WiFi required for sync');
    }
    
    if (!netInfo.isConnected) {
      throw new Error('No internet connection');
    }
    
    return true;
  }

  async syncCallLogs(callLogs = null) {
    if (this.isSyncing) {
      throw new Error('Sync already in progress');
    }

    try {
      this.isSyncing = true;
      
      // Check authentication
      if (!CRMAuthService.isAuthenticated()) {
        throw new Error('Not authenticated');
      }
      
      // Check network conditions
      await this.checkNetworkConditions();
      
      // Get call logs to sync
      const logsToSync = callLogs || await this.getNewCallLogs();
      
      if (logsToSync.length === 0) {
        return { success: true, synced_count: 0, message: 'No new call logs to sync' };
      }
      
      // Transform call logs for CRM
      const transformedLogs = logsToSync.map(log => this.transformCallLogForCRM(log));
      
      // Send to CRM
      const result = await ApiService.syncCallLogs(transformedLogs);
      
      // Update last sync time
      await AsyncStorage.setItem('last_sync_time', new Date().toISOString());
      
      return {
        success: true,
        synced_count: transformedLogs.length,
        result: result,
      };
      
    } catch (error) {
      console.error('Sync failed:', error);
      
      // Add failed logs to sync queue for retry
      if (callLogs) {
        this.addToSyncQueue(callLogs);
      }
      
      throw error;
    } finally {
      this.isSyncing = false;
    }
  }

  addToSyncQueue(callLogs) {
    this.syncQueue.push(...callLogs);
    this.saveSyncQueue();
  }

  async saveSyncQueue() {
    try {
      await AsyncStorage.setItem('sync_queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }

  async loadSyncQueue() {
    try {
      const queueData = await AsyncStorage.getItem('sync_queue');
      this.syncQueue = queueData ? JSON.parse(queueData) : [];
    } catch (error) {
      console.error('Failed to load sync queue:', error);
      this.syncQueue = [];
    }
  }

  async retryFailedSyncs() {
    if (this.syncQueue.length === 0) {
      return { success: true, message: 'No failed syncs to retry' };
    }

    const queuedLogs = [...this.syncQueue];
    this.syncQueue = [];
    
    try {
      const result = await this.syncCallLogs(queuedLogs);
      await this.saveSyncQueue(); // Clear the queue
      return result;
    } catch (error) {
      // Logs will be re-added to queue by syncCallLogs method
      throw error;
    }
  }

  getSyncQueueCount() {
    return this.syncQueue.length;
  }
}

export default new CallLogSyncService(); 