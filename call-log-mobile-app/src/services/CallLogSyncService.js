import apiService from './ApiService';
import deviceCallLogService from './DeviceCallLogService';
import AsyncStorage from '@react-native-async-storage/async-storage';

class CallLogSyncService {
  constructor() {
    this.isInitialized = false;
    this.isSyncing = false;
    this.syncStats = {
      totalSynced: 0,
      lastSyncTime: null,
      errors: [],
      pending: 0,
    };
    this.backgroundTask = null;
    this.listeners = new Set();
  }

  /**
   * Initialize the sync service
   */
  async init() {
    if (this.isInitialized) return true;

    try {
      console.log('Initializing CallLogSyncService...');
      
      // Initialize device call log service
      await deviceCallLogService.init();
      // Ensure user mobile number is known for direction detection
      try {
        const storedNumber = await AsyncStorage.getItem('userMobileNumber');
        if (storedNumber) {
          deviceCallLogService.setUserMobileNumber(storedNumber);
        } else {
          // Best-effort fetch from server
          const profile = await apiService.getUserProfile();
          const mobile = profile?.message?.data?.mobile_no || profile?.data?.mobile_no;
          if (mobile) {
            await AsyncStorage.setItem('userMobileNumber', mobile);
            deviceCallLogService.setUserMobileNumber(mobile);
          }
        }
      } catch (e) {
        // ignore, will fallback inside device service
      }
      
      // Load sync stats
      await this.loadSyncStats();
      
      this.isInitialized = true;
      console.log('CallLogSyncService initialized:', this.syncStats);
      
      return true;
    } catch (error) {
      console.error('Failed to initialize CallLogSyncService:', error);
      return false;
    }
  }

  /**
   * Check if the service is ready for syncing
   */
  async isReadyForSync() {
    const deviceStatus = deviceCallLogService.getStatus();
    const apiReady = await apiService.isAuthenticated();
    
    return {
      ready: deviceStatus.isInitialized && deviceStatus.hasPermission && apiReady,
      deviceInitialized: deviceStatus.isInitialized,
      hasPermission: deviceStatus.hasPermission,
      apiAuthenticated: apiReady,
      isSupported: deviceStatus.isSupported,
      errors: []
    };
  }

  /**
   * Request necessary permissions for syncing
   */
  async requestPermissions() {
    try {
      console.log('Requesting sync permissions...');
      const granted = await deviceCallLogService.requestPermissions();
      return granted;
    } catch (error) {
      console.error('Error requesting sync permissions:', error);
      return false;
    }
  }

  /**
   * Perform a full sync of call logs
   */
  async syncCallLogs(options = {}) {
    if (this.isSyncing) {
      console.log('Sync already in progress');
      return { success: false, message: 'Sync already in progress' };
    }

    this.isSyncing = true;
    
    try {
      console.log('Starting call log sync...');
      
      // Check if ready
      const readiness = await this.isReadyForSync();
      if (!readiness.ready) {
        // If permission is not granted, request it
        if (!readiness.hasPermission) {
          const granted = await deviceCallLogService.requestPermissions();
          if (!granted) {
            return {
              success: false,
              message: 'Call log permission is required to sync call logs. Please grant permission in app settings.',
              error: 'PERMISSION_DENIED'
            };
          }
          // Recheck readiness after permission granted
          const newReadiness = await this.isReadyForSync();
          if (!newReadiness.ready) {
            const missingItems = [];
            if (!newReadiness.deviceInitialized) missingItems.push('Device service not initialized');
            if (!newReadiness.apiAuthenticated) missingItems.push('Not authenticated with CRM');
            if (!newReadiness.isSupported) missingItems.push('Platform not supported');
            
            return {
              success: false,
              message: `Cannot sync: ${missingItems.join(', ')}`,
              error: 'SYNC_PREREQUISITES_FAILED'
            };
          }
        } else {
          const missingItems = [];
          if (!readiness.deviceInitialized) missingItems.push('Device service not initialized');
          if (!readiness.apiAuthenticated) missingItems.push('Not authenticated with CRM');
          if (!readiness.isSupported) missingItems.push('Platform not supported');
          
          return {
            success: false,
            message: `Cannot sync: ${missingItems.join(', ')}`,
            error: 'SYNC_PREREQUISITES_FAILED'
          };
        }
      }

      // Get new call logs from device
      console.log('Fetching new call logs from device...');
      const deviceCallLogs = await deviceCallLogService.getNewCallLogs();
      // Update pending to reflect unsynced items before pushing
      await this.updateSyncStats({ pending: deviceCallLogs.length });
      this.notifySync({ success: true, synced: 0, failed: 0, duplicates: 0, total: deviceCallLogs.length });
      
      if (deviceCallLogs.length === 0) {
        console.log('No new call logs to sync');
        await this.updateSyncStats({ lastSyncTime: Date.now() });
        this.notifySync({
          success: true,
          synced: 0,
          failed: 0,
          duplicates: 0,
          total: 0,
        });
        return { 
          success: true, 
          message: 'No new call logs to sync',
          synced: 0,
          total: 0
        };
      }

      // Transform call logs to CRM format
      console.log(`Transforming ${deviceCallLogs.length} call logs...`);
      const transformedLogs = deviceCallLogService.transformCallLogsToCRM(deviceCallLogs);

      // Send to CRM using the new batch sync endpoint
      const results = await this.syncBatchToCRM(transformedLogs);

      // Update sync stats
      const successCount = results.success_count || 0;
      const errorCount = results.failure_count || 0;
      const duplicateCount = results.duplicate_count || 0;
      
      await this.updateSyncStats({
        totalSynced: this.syncStats.totalSynced + successCount,
        lastSyncTime: Date.now(),
        errors: results.errors || [],
        pending: errorCount,
      });
      this.notifySync({
        success: errorCount === 0,
        synced: successCount,
        failed: errorCount,
        duplicates: duplicateCount,
        total: transformedLogs.length,
      });

      // Update device service last sync timestamp
      if (successCount > 0) {
        await deviceCallLogService.saveLastSyncTimestamp();
      }

      console.log(`Sync completed: ${successCount} synced, ${errorCount} failed`);
      
      return {
        success: errorCount === 0,
        message: `Synced ${successCount} call logs${duplicateCount > 0 ? `, ${duplicateCount} duplicates skipped` : ''}${errorCount > 0 ? `, ${errorCount} failed` : ''}`,
        synced: successCount,
        failed: errorCount,
        duplicates: duplicateCount,
        total: transformedLogs.length,
        errors: results.errors || []
      };

    } catch (error) {
      console.error('Sync failed:', error);
      
      await this.updateSyncStats({
        errors: [...this.syncStats.errors, error.message],
        lastSyncTime: Date.now()
      });
      this.notifySync({ success: false, synced: 0, failed: 0, duplicates: 0, total: 0, error: error.message });
      
      return {
        success: false,
        message: error.message,
        synced: 0,
        failed: 0,
        total: 0,
        errors: [error.message]
      };
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Start continuous background sync every 60 seconds.
   * Uses a lightweight in-app scheduler; for true OS-level background,
   * wire this through a native headless task or Expo BackgroundFetch.
   */
  startAutoSync(intervalMs = 60_000) {
    if (this.backgroundTask) return; // already running
    this.backgroundTask = setInterval(async () => {
      try {
        await this.init();
        await this.syncCallLogs();
      } catch (_) {}
    }, intervalMs);
  }

  stopAutoSync() {
    if (this.backgroundTask) {
      clearInterval(this.backgroundTask);
      this.backgroundTask = null;
    }
  }

  /**
   * Sync call logs to CRM using the new batch endpoint
   */
  async syncBatchToCRM(callLogs) {
    try {
      console.log(`Syncing ${callLogs.length} call logs to CRM...`);
      
      // Use the new batch sync endpoint
      const response = await apiService.syncCallLogs(callLogs);
      console.log('Raw API response:', response);
      
      if (response.message && response.message.success) {
        console.log('Batch sync successful:', response.message);
        return response.message;
      } else if (response.success) {
        console.log('Batch sync successful (legacy format):', response.data || response);
        return response.data || response;
      } else {
        const errorMsg = response.message || response.error || 'Batch sync failed';
        console.error('API returned error:', errorMsg);
        throw new Error(errorMsg);
      }
      
    } catch (error) {
      console.error('Batch sync failed:', error);
      // Better error handling for object errors
      let errorMessage = 'Unknown batch sync error';
      if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'object') {
        try {
          errorMessage = JSON.stringify(error);
        } catch (e) {
          errorMessage = String(error);
        }
      } else {
        errorMessage = String(error);
      }
      
      // Return error in expected format
      return {
        success_count: 0,
        failure_count: callLogs.length,
        duplicate_count: 0,
        errors: [errorMessage],
        processed_ids: []
      };
    }
  }

  /**
   * Sync call logs in batches to avoid overwhelming the server (DEPRECATED - keeping for fallback)
   */
  async syncInBatches(callLogs, batchSize = 10) {
    const results = [];
    
    for (let i = 0; i < callLogs.length; i += batchSize) {
      const batch = callLogs.slice(i, i + batchSize);
      console.log(`Syncing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(callLogs.length / batchSize)}`);
      
      const batchResults = await Promise.allSettled(
        batch.map(callLog => this.syncSingleCallLog(callLog))
      );
      
      batchResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results.push({ success: true, data: result.value });
        } else {
          results.push({ 
            success: false, 
            error: result.reason.message || 'Unknown error',
            callLog: batch[index]
          });
        }
      });
      
      // Add small delay between batches
      if (i + batchSize < callLogs.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    return results;
  }

  /**
   * Sync a single call log to CRM
   */
  async syncSingleCallLog(callLog) {
    try {
      console.log('Syncing single call log:', callLog.device_call_id);
      
      // Check if call log already exists in CRM
      const existingCallLog = await this.checkDuplicateCallLog(callLog);
      if (existingCallLog) {
        console.log('Call log already exists, skipping:', callLog.device_call_id);
        return { skipped: true, existing: existingCallLog };
      }
      
      // Create call log in CRM
      const response = await apiService.createCallLog(callLog);
      console.log('Call log synced successfully:', response);
      
      return response;
    } catch (error) {
      console.error('Failed to sync call log:', error);
      throw error;
    }
  }

  /**
   * Check if a call log already exists in CRM to prevent duplicates
   */
  async checkDuplicateCallLog(callLog) {
    try {
      // Search for existing call logs within user's own call logs only
      // Use the backend duplicate check instead of client-side check
      // The mobile sync API already handles duplicate detection properly
      console.log('Duplicate check will be handled by backend mobile sync API');
      return null; // Let the backend handle duplicate detection
      
    } catch (error) {
      console.log('Error checking for duplicate call log:', error);
      // If we can't check for duplicates, proceed with sync
      return null;
    }
  }

  /**
   * Get sync status and statistics
   */
  getSyncStatus() {
    const deviceStatus = deviceCallLogService.getStatus();
    
    return {
      ...this.syncStats,
      isSyncing: this.isSyncing,
      isInitialized: this.isInitialized,
      deviceStatus,
      readyForSync: this.isReadyForSync(),
    };
  }

  /**
   * Load sync statistics from storage
   */
  async loadSyncStats() {
    try {
      const stored = await AsyncStorage.getItem('callLogSyncStats');
      if (stored) {
        this.syncStats = { ...this.syncStats, ...JSON.parse(stored) };
        console.log('Loaded sync stats:', this.syncStats);
      }
    } catch (error) {
      console.error('Error loading sync stats:', error);
    }
  }

  /**
   * Update and save sync statistics
   */
  async updateSyncStats(updates) {
    try {
      this.syncStats = { ...this.syncStats, ...updates };
      await AsyncStorage.setItem('callLogSyncStats', JSON.stringify(this.syncStats));
      console.log('Updated sync stats:', this.syncStats);
    } catch (error) {
      console.error('Error updating sync stats:', error);
    }
  }

  /**
   * Subscribe to sync completion events
   */
  onSync(callback) {
    if (typeof callback !== 'function') return () => {};
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifySync(payload) {
    try {
      this.listeners.forEach((cb) => {
        try { cb({ stats: this.syncStats, ...payload }); } catch (_) {}
      });
    } catch (_) {}
  }

  /**
   * Get last persisted sync stats
   */
  getStoredSyncStats() {
    return { ...this.syncStats };
  }

  /**
   * Clear all sync data (for logout/reset)
   */
  async clearSyncData() {
    try {
      await AsyncStorage.removeItem('callLogSyncStats');
      await deviceCallLogService.clearStoredData();
      
      this.syncStats = {
        totalSynced: 0,
        lastSyncTime: null,
        errors: [],
        pending: 0,
      };
      
      console.log('Cleared all sync data');
    } catch (error) {
      console.error('Error clearing sync data:', error);
    }
  }

  /**
   * Test device call log access
   */
  async testDeviceAccess() {
    try {
      console.log('Testing device call log access...');
      
      const deviceStatus = deviceCallLogService.getStatus();
      if (!deviceStatus.isSupported) {
        return { success: false, message: 'Platform not supported for call log access' };
      }
      
      if (!deviceStatus.hasPermission) {
        const granted = await deviceCallLogService.requestPermissions();
        if (!granted) {
          return { success: false, message: 'Call log permission not granted' };
        }
      }
      
      // Try to fetch a small number of call logs
      const testLogs = await deviceCallLogService.getDeviceCallLogs({ limit: 5 });
      
      return {
        success: true,
        message: `Successfully accessed device call logs`,
        count: testLogs.length,
        sampleLog: testLogs[0] || null
      };
      
    } catch (error) {
      console.error('Device access test failed:', error);
      return {
        success: false,
        message: error.message,
        error: error
      };
    }
  }
}

// Export singleton instance
const callLogSyncService = new CallLogSyncService();
export default callLogSyncService; 