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

  const dispatch = useDispatch();
  const { user, serverUrl, sessionId } = useSelector((state) => state.auth);

  useEffect(() => {
    initializeApiService();
    loadUserProfileAndNumber();
    loadCallLogs();
  }, []);
  const loadUserProfileAndNumber = async () => {
    try {
      // Fetch profile from backend to get agent mobile no
      const profile = await apiService.apiCall('/api/method/crm.api.mobile_sync.get_user_profile', {
        method: 'POST',
      });
      const mobile = profile?.message?.data?.mobile_no;
      if (mobile) {
        await AsyncStorage.setItem('userMobileNumber', mobile);
        deviceCallLogService.setUserMobileNumber(mobile);
      }
    } catch (e) {
      // Fallback: keep any previously stored value
    }
  };

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
      console.log('Loading user-specific call logs...');
      // Use getUserCallLogs to get only current user's call logs
      const response = await apiService.getUserCallLogs(20);
      
      // Handle the correct response structure: response.message.success and response.message.data
      const apiResult = response.message || response;
      
      if (apiResult.success) {
        const logs = apiResult.data || [];
        // Sort logs by start_time in descending order
        const sortedLogs = logs.sort((a, b) => {
          const dateA = new Date(a.start_time);
          const dateB = new Date(b.start_time);
          return dateB - dateA;
        });
        
        setCallLogs(sortedLogs);
        setStats(prev => ({
          ...prev,
          totalCallLogs: logs.length,
          lastSync: new Date().toISOString(),
        }));
      } else {
        console.error('Failed to load user call logs:', apiResult.message || apiResult.error);
        Alert.alert('Error', apiResult.message || apiResult.error || 'Failed to load your call logs from CRM');
      }
    } catch (error) {
      console.error('Failed to load call logs:', error);
      Alert.alert('Error', 'Failed to load your call logs from CRM');
    } finally {
      setLoading(false);
    }
  };

  const loadUserMobileNumber = async () => {
    try {
      const storedNumber = await AsyncStorage.getItem('userMobileNumber');
      if (storedNumber) {
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
      deviceCallLogService.setUserMobileNumber(cleanNumber);
      console.log('Saved user mobile number:', cleanNumber);
    } catch (error) {
      console.error('Error saving mobile number:', error);
      Alert.alert('Error', 'Failed to save mobile number');
    }
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

  const handleSyncCallLogs = async () => {
    try {
      console.log('Starting call log sync...');
      await callLogSyncService.init();
      const result = await callLogSyncService.syncCallLogs();
      
      if (!result.success) {
        if (result.error === 'PERMISSION_DENIED') {
          Alert.alert(
            'Permission Required',
            'Call log permission is required to sync call logs. Please grant permission in app settings.',
            [{ text: 'OK' }]
          );
        } else {
          Alert.alert(
            'Sync Error',
            result.message || 'Failed to sync call logs',
            [{ text: 'OK' }]
          );
        }
        return;
      }
      
      await loadCallLogs();
      Alert.alert('Success', result.message || 'Call logs synced successfully!');
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
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Invalid Date';
      
      // Format: "DD/MM/YYYY HH:MM AM/PM"
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      const hours = date.getHours();
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const formattedHours = (hours % 12 || 12).toString().padStart(2, '0');
      
      return `${day}/${month}/${year} ${formattedHours}:${minutes} ${ampm}`;
    } catch (error) {
      console.error('Date formatting error:', error);
      return 'Invalid Date';
    }
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
              <TouchableOpacity 
                style={[styles.syncButton, styles.fullWidthButton]}
                onPress={handleSyncCallLogs}
              >
                <Text style={styles.syncButtonText}>Start Device Call Log Sync</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

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