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
    loadCallLogs();
  }, [sessionId, serverUrl]);

  const initializeApiService = async () => {
    if (serverUrl && sessionId) {
      apiService.setBaseURL(serverUrl);
      apiService.setSessionId(sessionId);
      await apiService.init();
    }
  };

  const loadCallLogs = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    try {
      const response = await apiService.getCallLogs({}, 20);
      const logs = response.message || [];
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
            apiService.clearSession();
            dispatch(logout());
          }
        },
      ]
    );
  };

  const handleSyncCallLogs = () => {
    Alert.alert(
      'Call Log Sync',
      'Call log sync feature will be implemented in the next phase. This will automatically sync your device call logs with the CRM system.',
      [{ text: 'OK' }]
    );
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
          <Text style={styles.sectionTitle}>Sync Status</Text>
          <View style={styles.syncCard}>
            <View style={styles.syncInfo}>
              <Text style={styles.syncLabel}>Last Sync:</Text>
              <Text style={styles.syncValue}>
                {stats.lastSync ? formatDateTime(stats.lastSync) : 'Never'}
              </Text>
            </View>
            <TouchableOpacity 
              style={styles.syncButton}
              onPress={handleSyncCallLogs}
            >
              <Text style={styles.syncButtonText}>Start Sync</Text>
            </TouchableOpacity>
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
  syncButton: {
    backgroundColor: '#10B981',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
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
});

export default DashboardScreen; 