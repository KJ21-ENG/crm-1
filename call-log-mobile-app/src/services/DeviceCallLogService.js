import { PermissionsAndroid, Platform, Alert } from 'react-native';
import CallLogs from 'react-native-call-log';
import AsyncStorage from '@react-native-async-storage/async-storage';

class DeviceCallLogService {
  constructor() {
    this.isInitialized = false;
    this.hasPermission = false;
    this.lastSyncTimestamp = null;
    this.userMobileNumber = null; // Will be set dynamically
  }

  /**
   * Set the user's mobile number for call direction detection
   */
  setUserMobileNumber(phoneNumber) {
    this.userMobileNumber = phoneNumber;
    console.log('User mobile number set to:', phoneNumber);
  }

  /**
   * Get user mobile number, try to detect from device if not set
   */
  getUserMobileNumber() {
    if (!this.userMobileNumber) {
      // Try to get from device if possible, otherwise use a default
      this.userMobileNumber = '+911234567890'; // Default fallback
      console.log('Using default mobile number:', this.userMobileNumber);
    }
    return this.userMobileNumber;
  }

  /**
   * Initialize the service
   */
  async init() {
    if (this.isInitialized) return true;
    
    try {
      console.log('Initializing DeviceCallLogService...');
      
      if (Platform.OS !== 'android') {
        console.log('Call log service is only supported on Android');
        this.isInitialized = true;
        return true;
      }

      // Load stored data
      await this.loadLastSyncTimestamp();
      
      // Check permissions
      this.hasPermission = await this.checkPermissions();
      
      this.isInitialized = true;
      console.log('DeviceCallLogService initialized successfully:', {
        hasPermission: this.hasPermission,
        userMobileNumber: this.userMobileNumber,
        lastSyncTimestamp: this.lastSyncTimestamp
      });
      
      return true;
    } catch (error) {
      console.error('Error initializing DeviceCallLogService:', error);
      this.isInitialized = false;
      return false;
    }
  }

  /**
   * Check if call log permissions are granted
   */
  async checkPermissions() {
    if (Platform.OS !== 'android') {
      console.log('Call log access only available on Android');
      return false;
    }

    try {
      const granted = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.READ_CALL_LOG
      );
      
      console.log('Call log permission status:', granted);
      return granted;
    } catch (error) {
      console.error('Error checking call log permissions:', error);
      return false;
    }
  }

  /**
   * Request call log permissions from user
   */
  async requestPermissions() {
    if (Platform.OS !== 'android') {
      Alert.alert(
        'Not Supported',
        'Call log access is only available on Android devices.',
        [{ text: 'OK' }]
      );
      return false;
    }

    try {
      console.log('Requesting call log permissions...');
      
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.READ_CALL_LOG,
        {
          title: 'Call Log Access Permission',
          message: 'CRM Call Log Sync needs access to your call logs to sync them with your CRM system.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        }
      );

      const isGranted = granted === PermissionsAndroid.RESULTS.GRANTED;
      this.hasPermission = isGranted;
      
      console.log('Call log permission result:', granted, 'isGranted:', isGranted);
      
      if (!isGranted) {
        Alert.alert(
          'Permission Required',
          'Call log access is required to sync your call logs with the CRM system. Please enable it in app settings.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Open Settings', onPress: this.openAppSettings }
          ]
        );
      }
      
      return isGranted;
    } catch (error) {
      console.error('Error requesting call log permissions:', error);
      Alert.alert('Error', 'Failed to request call log permissions.');
      return false;
    }
  }

  /**
   * Open app settings for manual permission management
   */
  openAppSettings() {
    // This would open the app settings page
    Alert.alert(
      'Manual Permission Setup',
      'Please go to your device Settings > Apps > CRM Call Log Sync > Permissions and enable Call Log access.',
      [{ text: 'OK' }]
    );
  }

  /**
   * Get device call logs with filtering options
   */
  async getDeviceCallLogs(options = {}) {
    if (!this.hasPermission) {
      console.log('No call log permission, requesting...');
      const granted = await this.requestPermissions();
      if (!granted) {
        throw new Error('Call log permission not granted');
      }
    }

    try {
      console.log('Fetching device call logs...');
      
      const defaultOptions = {
        limit: 100,
        offset: 0,
        minTimestamp: this.lastSyncTimestamp || 0,
      };
      
      const callLogOptions = { ...defaultOptions, ...options };
      console.log('Call log fetch options:', callLogOptions);
      
      const callLogs = await CallLogs.load(callLogOptions.limit, callLogOptions.offset);
      
      // Filter by timestamp if needed
      let filteredLogs = callLogs;
      if (callLogOptions.minTimestamp > 0) {
        filteredLogs = callLogs.filter(log => 
          log.timestamp > callLogOptions.minTimestamp
        );
      }
      
      console.log(`Fetched ${filteredLogs.length} call logs from device`);
      return filteredLogs;
      
    } catch (error) {
      console.error('Error fetching device call logs:', error);
      throw new Error(`Failed to fetch call logs: ${error.message}`);
    }
  }

  /**
   * Get new call logs since last sync
   */
  async getNewCallLogs() {
    try {
      const lastSync = await this.getLastSyncTimestamp();
      console.log('Getting new call logs since:', new Date(lastSync));
      
      const callLogs = await this.getDeviceCallLogs({
        minTimestamp: lastSync,
        limit: 50
      });
      
      // Sort by timestamp (newest first)
      const sortedLogs = callLogs.sort((a, b) => b.timestamp - a.timestamp);
      
      console.log(`Found ${sortedLogs.length} new call logs`);
      return sortedLogs;
      
    } catch (error) {
      console.error('Error getting new call logs:', error);
      throw error;
    }
  }

  /**
   * Transform a single call log from device format to CRM format
   */
  transformCallLogToCRM(deviceCallLog) {
    try {
      console.log('Raw device call log:', JSON.stringify(deviceCallLog, null, 2));
      
      // Map Android call types to CRM types
      const typeMapping = {
        '1': 'Incoming',
        '2': 'Outgoing', 
        '3': 'Missed',
        '4': 'Voicemail',
        '5': 'Rejected',
        '6': 'Blocked',
        // Also handle numeric values
        1: 'Incoming',
        2: 'Outgoing', 
        3: 'Missed',
        4: 'Voicemail',
        5: 'Rejected',
        6: 'Blocked',
        // Handle string values that might come from some devices
        'INCOMING': 'Incoming',
        'OUTGOING': 'Outgoing',
        'MISSED': 'Missed',
        'VOICEMAIL': 'Voicemail',
        'REJECTED': 'Rejected',
        'BLOCKED': 'Blocked',
      };

      console.log('Device call log type:', deviceCallLog.type, 'Mapped to:', typeMapping[deviceCallLog.type]);

      // Determine call status based on type and duration
      let status = 'Completed';
      if (deviceCallLog.type === 3 || deviceCallLog.type === '3' || deviceCallLog.type === 'MISSED') {
        status = 'Missed';
      } else if (deviceCallLog.type === 5 || deviceCallLog.type === '5' || deviceCallLog.type === 'REJECTED') {
        status = 'Rejected';
      } else if (deviceCallLog.type === 6 || deviceCallLog.type === '6' || deviceCallLog.type === 'BLOCKED') {
        status = 'Blocked';
      } else if (deviceCallLog.duration === 0) {
        status = 'No Answer';
      }

      // Validate and sanitize timestamp - be less aggressive with validation
      let validTimestamp = deviceCallLog.timestamp;

      // Convert to number if it's a string
      if (typeof validTimestamp === 'string') {
        validTimestamp = parseInt(validTimestamp, 10);
      }

      console.log('Original timestamp:', deviceCallLog.timestamp, 'Converted:', validTimestamp, 'Date test:', new Date(validTimestamp));

      // Check if timestamp is valid - only fallback for truly invalid values
      if (!validTimestamp || isNaN(validTimestamp) || validTimestamp < 0) {
        console.warn('Invalid timestamp detected, using current time:', validTimestamp);
        validTimestamp = Date.now();
      } else {
        // Only check for extremely unreasonable values (before year 2000 or far future)
        const year2000 = new Date('2000-01-01').getTime();
        const tenYearsFromNow = Date.now() + (10 * 365 * 24 * 60 * 60 * 1000);
        
        if (validTimestamp < year2000 || validTimestamp > tenYearsFromNow) {
          console.warn('Timestamp seems unreasonable, but keeping it:', new Date(validTimestamp));
          // Keep the original timestamp even if it seems odd
        }
      }

      // Validate duration
      let validDuration = deviceCallLog.duration || 0;
      if (isNaN(validDuration) || validDuration < 0) {
        validDuration = 0;
      }
      
      console.log('Using timestamp:', validTimestamp, 'Duration:', validDuration);

      // Create dates with validated values
      let startTime, endTime;
      try {
        startTime = new Date(validTimestamp);
        endTime = new Date(validTimestamp + (validDuration * 1000));
        
        console.log('Created dates - Start:', startTime, 'End:', endTime);
        
        // Double-check the dates are valid
        if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
          throw new Error('Invalid date after creation');
        }
      } catch (dateError) {
        console.warn('Date creation failed, using current time:', dateError);
        startTime = new Date();
        endTime = new Date(Date.now() + (validDuration * 1000));
      }

      // Format datetime for CRM compatibility (no microseconds, no timezone)
      const formatDateForCRM = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      };

      const crmCallLog = {
        // CRM required fields
        from: deviceCallLog.phoneNumber || 'Unknown',
        to: deviceCallLog.phoneNumber || 'Unknown', // This will be adjusted based on type
        type: typeMapping[deviceCallLog.type] || 'Unknown',
        status: status,
        duration: validDuration,
        start_time: formatDateForCRM(startTime),
        end_time: formatDateForCRM(endTime),
        
        // Additional metadata
        device_call_id: `device_${validTimestamp}_${deviceCallLog.phoneNumber}`,
        source: 'Mobile App',
        contact_name: deviceCallLog.name || null,
        
        // Reference fields (will be populated based on CRM contacts)
        reference_doctype: null,
        reference_docname: null,
      };

      // Adjust from/to based on call direction
      const userNumber = this.getUserMobileNumber();
      const cleanUserNumber = userNumber.replace(/[^\d]/g, ''); // Remove non-digits for comparison
      const cleanPhoneNumber = (deviceCallLog.phoneNumber || '').replace(/[^\d]/g, '');
      
      // First set the from/to based on the device call type
      if (deviceCallLog.type === 2 || deviceCallLog.type === '2' || deviceCallLog.type === 'OUTGOING') { // Outgoing
        crmCallLog.from = userNumber;
        crmCallLog.to = deviceCallLog.phoneNumber;
        crmCallLog.type = 'Outgoing';
      } else { // Incoming, Missed, etc.
        crmCallLog.from = deviceCallLog.phoneNumber;
        crmCallLog.to = userNumber;
        crmCallLog.type = typeMapping[deviceCallLog.type] || 'Unknown';
      }

      // Double check and correct the type based on the actual numbers
      if (cleanPhoneNumber && cleanUserNumber) {
        // If the 'to' number matches user's number, it's an incoming call
        if (crmCallLog.to.replace(/[^\d]/g, '') === cleanUserNumber) {
          crmCallLog.type = 'Incoming';
        }
        // If the 'from' number matches user's number, it's an outgoing call
        else if (crmCallLog.from.replace(/[^\d]/g, '') === cleanUserNumber) {
          crmCallLog.type = 'Outgoing';
        }
      }

      console.log(`Call direction: ${crmCallLog.from} → ${crmCallLog.to} (${crmCallLog.type})`);
      console.log('User number:', userNumber, 'Phone number:', deviceCallLog.phoneNumber);
      console.log('Transformed call log:', crmCallLog);
      return crmCallLog;
      
    } catch (error) {
      console.error('Error transforming call log:', error);
      throw new Error(`Failed to transform call log: ${error.message}`);
    }
  }

  /**
   * Transform multiple call logs to CRM format
   */
  transformCallLogsToCRM(deviceCallLogs) {
    try {
      const transformedLogs = deviceCallLogs.map(log => 
        this.transformCallLogToCRM(log)
      );
      
      console.log(`Transformed ${transformedLogs.length} call logs to CRM format`);
      return transformedLogs;
      
    } catch (error) {
      console.error('Error transforming call logs:', error);
      throw error;
    }
  }

  /**
   * Save last sync timestamp
   */
  async saveLastSyncTimestamp(timestamp = null) {
    try {
      const syncTime = timestamp || Date.now();
      await AsyncStorage.setItem('lastCallLogSync', syncTime.toString());
      this.lastSyncTimestamp = syncTime;
      console.log('Saved last sync timestamp:', new Date(syncTime));
    } catch (error) {
      console.error('Error saving last sync timestamp:', error);
    }
  }

  /**
   * Get last sync timestamp
   */
  async getLastSyncTimestamp() {
    try {
      const stored = await AsyncStorage.getItem('lastCallLogSync');
      const timestamp = stored ? parseInt(stored, 10) : 0;
      this.lastSyncTimestamp = timestamp;
      return timestamp;
    } catch (error) {
      console.error('Error getting last sync timestamp:', error);
      return 0;
    }
  }

  /**
   * Load last sync timestamp on initialization
   */
  async loadLastSyncTimestamp() {
    this.lastSyncTimestamp = await this.getLastSyncTimestamp();
  }

  /**
   * Clear all stored data (for logout/reset)
   */
  async clearStoredData() {
    try {
      await AsyncStorage.removeItem('lastCallLogSync');
      this.lastSyncTimestamp = null;
      console.log('Cleared device call log service data');
    } catch (error) {
      console.error('Error clearing stored data:', error);
    }
  }

  /**
   * Get service status
   */
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      hasPermission: this.hasPermission,
      lastSyncTimestamp: this.lastSyncTimestamp,
      lastSyncDate: this.lastSyncTimestamp ? new Date(this.lastSyncTimestamp) : null,
      platform: Platform.OS,
      isSupported: Platform.OS === 'android',
    };
  }
}

// Export singleton instance
const deviceCallLogService = new DeviceCallLogService();
export default deviceCallLogService; 