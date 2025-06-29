import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import ApiService from './ApiService';

class CRMAuthService {
  constructor() {
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;
    
    try {
      // Check if user is already authenticated
      const token = await SecureStore.getItemAsync('auth_token');
      const userData = await AsyncStorage.getItem('user_data');
      const serverUrl = await AsyncStorage.getItem('server_url');
      
      if (token && userData && serverUrl) {
        this.currentUser = JSON.parse(userData);
        this.token = token;
        this.serverUrl = serverUrl;
      }
      
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize auth service:', error);
      this.isInitialized = true;
    }
  }

  async login(username, password, serverUrl) {
    try {
      const response = await ApiService.login(username, password, serverUrl);
      
      if (response.message && response.message.sid) {
        // Store credentials securely
        await SecureStore.setItemAsync('auth_token', response.message.sid);
        await AsyncStorage.setItem('user_data', JSON.stringify(response.message));
        await AsyncStorage.setItem('server_url', serverUrl);
        
        this.currentUser = response.message;
        this.token = response.message.sid;
        this.serverUrl = serverUrl;
        
        return {
          success: true,
          user: response.message,
          token: response.message.sid,
        };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  }

  async logout() {
    try {
      // Call logout API if authenticated
      if (this.token) {
        await ApiService.logout();
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      // Clear local storage regardless of API call result
      await this.clearCredentials();
    }
  }

  async clearCredentials() {
    try {
      await SecureStore.deleteItemAsync('auth_token');
      await AsyncStorage.removeItem('user_data');
      await AsyncStorage.removeItem('server_url');
      
      this.currentUser = null;
      this.token = null;
      this.serverUrl = null;
    } catch (error) {
      console.error('Failed to clear credentials:', error);
    }
  }

  async refreshToken() {
    // Implement token refresh logic if your CRM supports it
    // For now, just check if current token is still valid
    try {
      const response = await ApiService.get('/api/method/frappe.auth.get_logged_user');
      return response.message ? true : false;
    } catch (error) {
      return false;
    }
  }

  isAuthenticated() {
    return !!(this.token && this.currentUser);
  }

  getCurrentUser() {
    return this.currentUser;
  }

  getToken() {
    return this.token;
  }

  getServerUrl() {
    return this.serverUrl;
  }
}

export default new CRMAuthService(); 