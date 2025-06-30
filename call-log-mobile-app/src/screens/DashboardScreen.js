import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  FlatList,
  TextInput,
  Modal,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/slices/authSlice';
import apiService from '../services/ApiService';
import callLogSyncService from '../services/CallLogSyncService';
import deviceCallLogService from '../services/DeviceCallLogService';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DashboardScreen = () => {
  const [callLogs, setCallLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalCallLogs: 0,
    lastSync: null,
    pendingSync: 0,
  });
  const [userMobileNumber, setUserMobileNumber] = useState('');
  const [showMobileConfig, setShowMobileConfig] = useState(false);
  const [tempMobileNumber, setTempMobileNumber] = useState('');
  const [debugInfo, setDebugInfo] = useState({
    latestDeviceLog: null,
    latestTransformedLog: null,
    latestCrmLog: null,
    debugVisible: false,
  });

  const dispatch = useDispatch();
  const { user, serverUrl, sessionId } = useSelector((state) => state.auth);

  useEffect(() => {
    console.log('Dashboard mounted with user:', user);
    initializeApiService();
    loadCallLogs();
    loadUserMobileNumber();
  }, [sessionId, serverUrl]);

  const initializeApiService = async () => {
    if (serverUrl && sessionId) {
      console.log('Initializing API service with:', { serverUrl, sessionId: !!sessionId });
      apiService.setBaseURL(serverUrl);
      apiService.setSessionId(sessionId);
      await apiService.init();
    }
  };

  const loadCallLogs = async () => {
    if (!sessionId) {
      console.log('No session ID, skipping call log loading');
      return;
    }
    
    setLoading(true);
    try {
      console.log('Loading call logs...');
      const response = await apiService.getCallLogs({}, 20);
      const logs = response.message || [];
      console.log('Call logs loaded:', logs.length);
      setCallLogs(logs);
      setStats(prev => ({
        ...prev,
        totalCallLogs: logs.length,
        lastSync: new Date().toISOString(),
      }));
    } catch (error) {
      console.error('Failed to load call logs:', error);
      Alert.alert('Error', 'Failed to load call logs from CRM');
    } finally {
      setLoading(false);
    }
  };

  const loadUserMobileNumber = async () => {
    try {
      const storedNumber = await AsyncStorage.getItem('userMobileNumber');
      if (storedNumber) {
        setUserMobileNumber(storedNumber);
        deviceCallLogService.setUserMobileNumber(storedNumber);
        console.log('Loaded user mobile number:', storedNumber);
      }
    } catch (error) {
      console.error('Error loading user mobile number:', error);
    }
  };

  const saveMobileNumber = async (number) => {
    try {
      const cleanNumber = number.trim();
      if (!cleanNumber) {
        Alert.alert('Error', 'Please enter a valid mobile number');
        return;
      }
      
      await AsyncStorage.setItem('userMobileNumber', cleanNumber);
      setUserMobileNumber(cleanNumber);
      deviceCallLogService.setUserMobileNumber(cleanNumber);
      setShowMobileConfig(false);
      setTempMobileNumber('');
      
      Alert.alert(
        'Success', 
        'Mobile number saved! This will be used to correctly identify incoming vs outgoing calls.',
        [{ text: 'OK' }]
      );
      console.log('Saved user mobile number:', cleanNumber);
    } catch (error) {
      console.error('Error saving mobile number:', error);
      Alert.alert('Error', 'Failed to save mobile number');
    }
  };

  const openMobileConfig = () => {
    setTempMobileNumber(userMobileNumber);
    setShowMobileConfig(true);
  };

  const handleDebugLatestLog = async () => {
    try {
      console.log('=== DEBUG: Getting latest call logs ===');
      
      // Initialize device service
      await callLogSyncService.init();
      
      // Get latest device call log
      console.log('Fetching latest device call log...');
      const deviceLogs = await deviceCallLogService.getDeviceCallLogs({ limit: 1 });
      const latestDeviceLog = deviceLogs[0] || null;
      
      console.log('Latest device call log:', JSON.stringify(latestDeviceLog, null, 2));
      
      // Transform it to CRM format
      let latestTransformedLog = null;
      if (latestDeviceLog) {
        latestTransformedLog = deviceCallLogService.transformCallLogToCRM(latestDeviceLog);
        console.log('Latest transformed call log:', JSON.stringify(latestTransformedLog, null, 2));
      }
      
      // Get latest CRM call log
      console.log('Fetching latest CRM call log...');
      const crmResponse = await apiService.getCallLogs({}, 1);
      const latestCrmLog = crmResponse.message && crmResponse.message[0] ? crmResponse.message[0] : null;
      
      console.log('Latest CRM call log:', JSON.stringify(latestCrmLog, null, 2));
      
      // Update debug state
      setDebugInfo({
        latestDeviceLog,
        latestTransformedLog,
        latestCrmLog,
        debugVisible: true,
      });
      
      Alert.alert(
        'Debug Information Captured',
        'Latest call log information has been captured. Check the debug section for details.',
        [{ text: 'OK' }]
      );
      
    } catch (error) {
      console.error('Debug error:', error);
      Alert.alert(
        'Debug Error',
        `Failed to get debug information: ${error.message}`,
        [{ text: 'OK' }]
      );
    }
  };

  const toggleDebugVisibility = () => {
    setDebugInfo(prev => ({
      ...prev,
      debugVisible: !prev.debugVisible,
    }));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadCallLogs();
    setRefreshing(false);
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: () => {
            console.log('Logging out...');
            apiService.clearSession();
            dispatch(logout());
          }
        },
      ]
    );
  };

  const handleTestDeviceAccess = async () => {
    try {
      console.log('Testing device call log access...');
      
      // First check current permission status
      const { PermissionsAndroid, Platform } = require('react-native');
      
      if (Platform.OS === 'android') {
        console.log('Checking current permission status...');
        const currentStatus = await PermissionsAndroid.check(
          PermissionsAndroid.PERMISSIONS.READ_CALL_LOG
        );
        console.log('Current call log permission status:', currentStatus);
        
        if (!currentStatus) {
          Alert.alert(
            'Permission Status',
            'Call log permission is not granted. Let\'s request it now.',
            [
              { text: 'Cancel', style: 'cancel' },
              { 
                text: 'Request Permission', 
                onPress: async () => {
                  console.log('Requesting permission directly...');
                  try {
                    const result = await PermissionsAndroid.request(
                      PermissionsAndroid.PERMISSIONS.READ_CALL_LOG,
                      {
                        title: 'Call Log Access',
                        message: 'This app needs access to your call logs to sync with CRM.',
                        buttonNeutral: 'Ask Me Later',
                        buttonNegative: 'Cancel',
                        buttonPositive: 'OK',
                      }
                    );
                    console.log('Direct permission request result:', result);
                    
                    if (result === PermissionsAndroid.RESULTS.GRANTED) {
                      Alert.alert('Success', 'Permission granted! Now testing call log access...');
                      // Continue with device test
                      await callLogSyncService.init();
                      const testResult = await callLogSyncService.testDeviceAccess();
                      if (testResult.success) {
                        Alert.alert(
                          'Device Access Successful',
                          `${testResult.message}\nCall logs found: ${testResult.count}`,
                          [{ text: 'OK' }]
                        );
                      }
                    } else {
                      Alert.alert('Permission Denied', `Permission result: ${result}`);
                    }
                  } catch (permError) {
                    console.error('Direct permission request failed:', permError);
                    Alert.alert('Permission Error', `Failed to request permission: ${permError.message}`);
                  }
                }
              }
            ]
          );
          return;
        } else {
          console.log('Permission already granted, testing access...');
        }
      }
      
      // Initialize sync service if needed
      await callLogSyncService.init();
      
      // Test device access
      const result = await callLogSyncService.testDeviceAccess();
      
      if (result.success) {
        Alert.alert(
          'Device Access Test Successful',
          `${result.message}\n\nCall logs found: ${result.count}\n\n${result.sampleLog ? `Sample log: ${result.sampleLog.phoneNumber || 'Unknown'} (${new Date(result.sampleLog.timestamp).toLocaleString()})` : 'No call logs available'}`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert(
          'Device Access Test Failed',
          result.message,
          [{ text: 'OK' }]
        );
      }
      
    } catch (error) {
      console.error('Device access test error:', error);
      Alert.alert(
        'Test Error',
        `Failed to test device access: ${error.message}`,
        [{ text: 'OK' }]
      );
    }
  };

  const handleTestCRMAPI = async () => {
    try {
      console.log('Testing CRM API endpoints...');
      
      // Test the mobile sync API
      const result = await apiService.testMobileSync();
      
      if (result.success) {
        Alert.alert(
          'CRM API Test Successful',
          `${result.message}\n\nTest Result: ${result.test_result?.status}\nUser: ${result.user}\nTime: ${new Date(result.timestamp).toLocaleString()}`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert(
          'CRM API Test Failed',
          result.message,
          [{ text: 'OK' }]
        );
      }
      
    } catch (error) {
      console.error('CRM API test error:', error);
      Alert.alert(
        'API Test Error',
        `Failed to test CRM API: ${error.message}`,
        [{ text: 'OK' }]
      );
    }
  };

  const handleSyncCallLogs = async () => {
    try {
      console.log('Starting device call log sync...');
      
      // Initialize sync service if needed
      await callLogSyncService.init();
      
      // Check readiness
      const readiness = await callLogSyncService.isReadyForSync();
      
      if (!readiness.isSupported) {
        Alert.alert(
          'Not Supported',
          'Device call log sync is only available on Android devices.',
          [{ text: 'OK' }]
        );
        return;
      }
      
      if (!readiness.hasPermission) {
        Alert.alert(
          'Permission Required',
          'This app needs permission to access your call logs to sync them with the CRM system. Would you like to grant permission?',
          [
            { text: 'Cancel', style: 'cancel' },
            { 
              text: 'Grant Permission', 
              onPress: async () => {
                const granted = await callLogSyncService.requestPermissions();
                if (granted) {
                  // Try sync again after permission granted
                  handleSyncCallLogs();
                }
              }
            }
          ]
        );
        return;
      }
      
      // Show sync in progress
      Alert.alert(
        'Syncing Call Logs',
        'Syncing your device call logs with the CRM system...',
        [],
        { cancelable: false }
      );
      
      // Perform sync
      const result = await callLogSyncService.syncCallLogs();
      
              // Show result
        if (result.success) {
          const details = [
            `Synced: ${result.synced}`,
            `Total processed: ${result.total}`,
            result.duplicates > 0 ? `Duplicates skipped: ${result.duplicates}` : null,
            result.failed > 0 ? `Failed: ${result.failed}` : null
          ].filter(Boolean).join('\n');
          
          Alert.alert(
            'Sync Successful',
            `${result.message}\n\n${details}`,
            [{ 
              text: 'OK',
              onPress: () => {
                // Refresh call logs display
                loadCallLogs();
              }
            }]
          );
        } else {
          Alert.alert(
            'Sync Failed',
            `${result.message}\n\n${result.errors?.length > 0 ? 'Errors:\n' + result.errors.join('\n') : ''}`,
            [{ text: 'OK' }]
          );
        }
      
    } catch (error) {
      console.error('Sync error:', error);
      Alert.alert(
        'Sync Error',
        `Failed to sync call logs: ${error.message}`,
        [{ text: 'OK' }]
      );
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const formatDuration = (duration) => {
    if (!duration) return '0s';
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
  };

  const renderCallLogItem = ({ item }) => (
    <View style={styles.callLogItem}>
      <View style={styles.callLogHeader}>
        <Text style={styles.callLogNumber}>
          {item.from === item.to ? item.from : `${item.from} → ${item.to}`}
        </Text>
        <Text style={[styles.callLogType, getTypeStyle(item.type)]}>
          {item.type?.toUpperCase() || 'UNKNOWN'}
        </Text>
      </View>
      <View style={styles.callLogDetails}>
        <Text style={styles.callLogTime}>
          {formatDateTime(item.start_time)}
        </Text>
        <Text style={styles.callLogDuration}>
          Duration: {formatDuration(item.duration)}
        </Text>
      </View>
      {item.status && (
        <Text style={[styles.callLogStatus, getStatusStyle(item.status)]}>
          Status: {item.status}
        </Text>
      )}
    </View>
  );

  const getTypeStyle = (type) => {
    switch (type?.toLowerCase()) {
      case 'incoming': return styles.incoming;
      case 'outgoing': return styles.outgoing;
      case 'missed': return styles.missed;
      default: return styles.unknown;
    }
  };

  const getStatusStyle = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return styles.completed;
      case 'failed': return styles.failed;
      case 'busy': return styles.busy;
      default: return styles.unknown;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome back!</Text>
          <Text style={styles.userText}>{user?.full_name || user?.username}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Mobile Number Configuration */}
        <View style={styles.configSection}>
          <Text style={styles.sectionTitle}>Mobile Number Configuration</Text>
          <View style={styles.configCard}>
            <View style={styles.configInfo}>
              <Text style={styles.configLabel}>Your Mobile Number:</Text>
              <Text style={styles.configValue}>
                {userMobileNumber || 'Not Set'}
              </Text>
              <Text style={styles.configDescription}>
                Set your mobile number to correctly identify incoming vs outgoing calls
              </Text>
            </View>
            <TouchableOpacity 
              style={styles.configButton}
              onPress={openMobileConfig}
            >
              <Text style={styles.configButtonText}>
                {userMobileNumber ? 'Update' : 'Set'} Number
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.totalCallLogs}</Text>
            <Text style={styles.statLabel}>Call Logs</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.pendingSync}</Text>
            <Text style={styles.statLabel}>Pending Sync</Text>
          </View>
        </View>

        {/* Sync Status */}
        <View style={styles.syncSection}>
          <Text style={styles.sectionTitle}>Device Call Log Sync</Text>
          <View style={styles.syncCard}>
            <View style={styles.syncInfo}>
              <Text style={styles.syncLabel}>Last Sync:</Text>
              <Text style={styles.syncValue}>
                {stats.lastSync ? formatDateTime(stats.lastSync) : 'Never'}
              </Text>
            </View>
            <View style={styles.buttonContainer}>
              <View style={styles.buttonRow}>
                <TouchableOpacity 
                  style={[styles.syncButton, styles.testButton]}
                  onPress={handleTestDeviceAccess}
                >
                  <Text style={styles.syncButtonText}>Test Device</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.syncButton, styles.apiTestButton]}
                  onPress={handleTestCRMAPI}
                >
                  <Text style={styles.syncButtonText}>Test API</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.buttonRow}>
                <TouchableOpacity 
                  style={[styles.syncButton, styles.debugButton]}
                  onPress={handleDebugLatestLog}
                >
                  <Text style={styles.syncButtonText}>Debug Latest Log</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.syncButton, styles.toggleButton]}
                  onPress={toggleDebugVisibility}
                >
                  <Text style={styles.syncButtonText}>
                    {debugInfo.debugVisible ? 'Hide' : 'Show'} Debug
                  </Text>
                </TouchableOpacity>
              </View>
              <TouchableOpacity 
                style={[styles.syncButton, styles.fullWidthButton]}
                onPress={handleSyncCallLogs}
              >
                <Text style={styles.syncButtonText}>Start Device Call Log Sync</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Debug Information Section */}
        {debugInfo.debugVisible && (
          <View style={styles.debugSection}>
            <Text style={styles.sectionTitle}>Debug Information</Text>
            
            {/* Latest Device Call Log */}
            <View style={styles.debugCard}>
              <Text style={styles.debugTitle}>Latest Device Call Log:</Text>
              {debugInfo.latestDeviceLog ? (
                <View style={styles.debugContent}>
                  <Text style={styles.debugText}>
                    Phone: {debugInfo.latestDeviceLog.phoneNumber || 'Unknown'}
                  </Text>
                  <Text style={styles.debugText}>
                    Type: {debugInfo.latestDeviceLog.type} 
                  </Text>
                  <Text style={styles.debugText}>
                    Timestamp: {debugInfo.latestDeviceLog.timestamp} 
                  </Text>
                  <Text style={styles.debugText}>
                    Date: {debugInfo.latestDeviceLog.timestamp ? new Date(debugInfo.latestDeviceLog.timestamp).toLocaleString() : 'Invalid'}
                  </Text>
                  <Text style={styles.debugText}>
                    Duration: {debugInfo.latestDeviceLog.duration}s
                  </Text>
                  <Text style={styles.debugText}>
                    Name: {debugInfo.latestDeviceLog.name || 'No name'}
                  </Text>
                </View>
              ) : (
                <Text style={styles.debugText}>No device call log found</Text>
              )}
            </View>

            {/* Latest Transformed Call Log */}
            <View style={styles.debugCard}>
              <Text style={styles.debugTitle}>Latest Transformed Call Log:</Text>
              {debugInfo.latestTransformedLog ? (
                <View style={styles.debugContent}>
                  <Text style={styles.debugText}>
                    From: {debugInfo.latestTransformedLog.from}
                  </Text>
                  <Text style={styles.debugText}>
                    To: {debugInfo.latestTransformedLog.to}
                  </Text>
                  <Text style={styles.debugText}>
                    Type: {debugInfo.latestTransformedLog.type}
                  </Text>
                  <Text style={styles.debugText}>
                    Status: {debugInfo.latestTransformedLog.status}
                  </Text>
                  <Text style={styles.debugText}>
                    Start Time: {debugInfo.latestTransformedLog.start_time}
                  </Text>
                  <Text style={styles.debugText}>
                    Duration: {debugInfo.latestTransformedLog.duration}s
                  </Text>
                </View>
              ) : (
                <Text style={styles.debugText}>No transformed call log</Text>
              )}
            </View>

            {/* Latest CRM Call Log */}
            <View style={styles.debugCard}>
              <Text style={styles.debugTitle}>Latest CRM Call Log:</Text>
              {debugInfo.latestCrmLog ? (
                <View style={styles.debugContent}>
                  <Text style={styles.debugText}>
                    From: {debugInfo.latestCrmLog.from}
                  </Text>
                  <Text style={styles.debugText}>
                    To: {debugInfo.latestCrmLog.to}
                  </Text>
                  <Text style={styles.debugText}>
                    Type: {debugInfo.latestCrmLog.type}
                  </Text>
                  <Text style={styles.debugText}>
                    Status: {debugInfo.latestCrmLog.status}
                  </Text>
                  <Text style={styles.debugText}>
                    Start Time: {debugInfo.latestCrmLog.start_time}
                  </Text>
                  <Text style={styles.debugText}>
                    Duration: {debugInfo.latestCrmLog.duration}s
                  </Text>
                  <Text style={styles.debugText}>
                    Created: {debugInfo.latestCrmLog.creation}
                  </Text>
                  <Text style={styles.debugText}>
                    Modified: {debugInfo.latestCrmLog.modified}
                  </Text>
                </View>
              ) : (
                <Text style={styles.debugText}>No CRM call log found</Text>
              )}
            </View>
          </View>
        )}

        {/* Call Logs Section */}
        <View style={styles.callLogsSection}>
          <Text style={styles.sectionTitle}>Recent Call Logs</Text>
          {loading ? (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>Loading call logs...</Text>
            </View>
          ) : callLogs.length > 0 ? (
            <FlatList
              data={callLogs}
              renderItem={renderCallLogItem}
              keyExtractor={(item) => item.name}
              scrollEnabled={false}
              showsVerticalScrollIndicator={false}
            />
          ) : (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No call logs found</Text>
              <Text style={styles.emptySubtext}>
                Call logs will appear here once they are synced from your device
              </Text>
            </View>
          )}
        </View>

        {/* Connection Info */}
        <View style={styles.connectionSection}>
          <Text style={styles.sectionTitle}>Connection Info</Text>
          <View style={styles.connectionCard}>
            <Text style={styles.connectionLabel}>Server:</Text>
            <Text style={styles.connectionValue}>{serverUrl}</Text>
            <Text style={styles.connectionLabel}>Status:</Text>
            <Text style={[styles.connectionValue, styles.connected]}>Connected</Text>
          </View>
        </View>
      </ScrollView>

      {/* Mobile Number Configuration Modal */}
      <Modal
        visible={showMobileConfig}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowMobileConfig(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Configure Mobile Number</Text>
            <Text style={styles.modalDescription}>
              Enter your mobile number (with country code) to correctly identify call directions
            </Text>
            
            <TextInput
              style={styles.mobileInput}
              value={tempMobileNumber}
              onChangeText={setTempMobileNumber}
              placeholder="+1234567890"
              keyboardType="phone-pad"
              autoFocus={true}
            />
            
            <View style={styles.modalButtons}>
              <TouchableOpacity 
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowMobileConfig(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.modalButton, styles.saveButton]}
                onPress={() => saveMobileNumber(tempMobileNumber)}
              >
                <Text style={styles.saveButtonText}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 24,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  welcomeText: {
    fontSize: 16,
    color: '#6B7280',
  },
  userText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  logoutButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#EF4444',
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#3B82F6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  syncSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  syncCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  syncInfo: {
    marginBottom: 16,
  },
  syncLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  syncValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '500',
  },
  buttonContainer: {
    gap: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  syncButton: {
    backgroundColor: '#10B981',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    flex: 1,
  },
  fullWidthButton: {
    flex: 0,
    width: '100%',
  },
  testButton: {
    backgroundColor: '#3B82F6',
  },
  apiTestButton: {
    backgroundColor: '#8B5CF6',
  },
  debugButton: {
    backgroundColor: '#F59E0B',
  },
  toggleButton: {
    backgroundColor: '#6B7280',
  },
  syncButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  callLogsSection: {
    marginBottom: 24,
  },
  loadingContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  emptyContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  callLogItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  callLogHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  callLogNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  callLogType: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  incoming: {
    backgroundColor: '#D1FAE5',
    color: '#065F46',
  },
  outgoing: {
    backgroundColor: '#DBEAFE',
    color: '#1E40AF',
  },
  missed: {
    backgroundColor: '#FEE2E2',
    color: '#991B1B',
  },
  unknown: {
    backgroundColor: '#F3F4F6',
    color: '#374151',
  },
  callLogDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  callLogTime: {
    fontSize: 14,
    color: '#6B7280',
  },
  callLogDuration: {
    fontSize: 14,
    color: '#6B7280',
  },
  callLogStatus: {
    fontSize: 12,
    fontWeight: '500',
  },
  completed: {
    color: '#059669',
  },
  failed: {
    color: '#DC2626',
  },
  busy: {
    color: '#D97706',
  },
  connectionSection: {
    marginBottom: 40,
  },
  connectionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  connectionLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  connectionValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '500',
    marginBottom: 12,
  },
  connected: {
    color: '#059669',
  },
  configSection: {
    marginBottom: 24,
  },
  configCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  configInfo: {
    marginBottom: 16,
  },
  configLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  configValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '600',
    marginBottom: 8,
  },
  configDescription: {
    fontSize: 12,
    color: '#9CA3AF',
    lineHeight: 16,
  },
  configButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  configButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  modalDescription: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  mobileInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 24,
    backgroundColor: '#F9FAFB',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    backgroundColor: '#10B981',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  debugSection: {
    marginBottom: 24,
  },
  debugCard: {
    backgroundColor: '#1F2937',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F9FAFB',
    marginBottom: 8,
  },
  debugContent: {
    backgroundColor: '#111827',
    borderRadius: 4,
    padding: 12,
  },
  debugText: {
    fontSize: 12,
    color: '#D1D5DB',
    fontFamily: 'monospace',
    marginBottom: 4,
  },
});

export default DashboardScreen; 