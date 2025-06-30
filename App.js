import React, { useEffect } from 'react';
import { StatusBar, View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { store } from './src/store/store';
import { validateSession } from './src/store/slices/authSlice';
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';

const AppContent = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, isValidating, loading } = useSelector((state) => state.auth);

  useEffect(() => {
    // Check for existing session on app start
    dispatch(validateSession());
  }, [dispatch]);

  // Show loading screen during validation
  if (isValidating || loading) {
    return (
      <View style={styles.loadingContainer}>
        <View style={styles.loadingContent}>
          <View style={styles.logoContainer}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>CRM</Text>
            </View>
          </View>
          <Text style={styles.loadingTitle}>CRM Call Log Sync</Text>
          <ActivityIndicator size="large" color="#3B82F6" style={styles.spinner} />
          <Text style={styles.loadingText}>
            {isValidating ? 'Checking session...' : 'Signing in...'}
          </Text>
        </View>
      </View>
    );
  }

  // Navigate based on authentication status
  return isAuthenticated ? <DashboardScreen /> : <LoginScreen />;
};

export default function App() {
  return (
    <Provider store={store}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <AppContent />
    </Provider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContent: {
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  logoContainer: {
    marginBottom: 24,
  },
  logo: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoText: {
    color: '#FFFFFF',
    fontSize: 32,
    fontWeight: 'bold',
  },
  loadingTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 32,
    textAlign: 'center',
  },
  spinner: {
    marginBottom: 16,
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
}); 