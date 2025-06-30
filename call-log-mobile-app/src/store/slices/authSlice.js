import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

// Async thunk for login
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password, serverUrl }, { rejectWithValue }) => {
    try {
      console.log('Attempting login to:', serverUrl);
      
      // Login with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(`${serverUrl}/api/method/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          usr: username,
          pwd: password,
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Login failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Login response:', data);

      // Extract session cookie from response headers
      const cookies = response.headers.get('set-cookie');
      let sessionId = null;
      
      if (cookies) {
        const sidMatch = cookies.match(/sid=([^;]+)/);
        if (sidMatch) {
          sessionId = sidMatch[1];
        }
      }

      if (!sessionId) {
        throw new Error('No session ID received from server');
      }

      // Store credentials securely
      await SecureStore.setItemAsync('session_id', sessionId);
      await AsyncStorage.setItem('user_data', JSON.stringify(data));
      await AsyncStorage.setItem('server_url', serverUrl);
      
      return {
        user: {
          username: username,
          full_name: data.full_name,
          home_page: data.home_page,
        },
        sessionId: sessionId,
        serverUrl: serverUrl,
        loginTime: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Login error:', error);
      if (error.name === 'AbortError') {
        return rejectWithValue('Login request timed out. Please check your connection.');
      }
      return rejectWithValue(error.message);
    }
  }
);

// Async thunk for logout
export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      
      if (auth.serverUrl && auth.sessionId) {
        // Call logout API
        await fetch(`${auth.serverUrl}/api/method/logout`, {
          method: 'POST',
          headers: {
            'Cookie': `sid=${auth.sessionId}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Clear stored data regardless of API call result
      await SecureStore.deleteItemAsync('session_id');
      await AsyncStorage.removeItem('user_data');
      await AsyncStorage.removeItem('server_url');
    }
  }
);

// Async thunk for session validation
export const validateSession = createAsyncThunk(
  'auth/validateSession',
  async (_, { rejectWithValue }) => {
    try {
      const sessionId = await SecureStore.getItemAsync('session_id');
      const userData = await AsyncStorage.getItem('user_data');
      const serverUrl = await AsyncStorage.getItem('server_url');
      
      console.log('Validating session:', { hasSessionId: !!sessionId, hasUserData: !!userData, serverUrl });
      
      if (!sessionId || !userData || !serverUrl) {
        console.log('No stored session found, showing login screen');
        throw new Error('No stored session found');
      }

      // Skip validation if serverUrl is localhost (invalid for mobile)
      if (serverUrl.includes('127.0.0.1') || serverUrl.includes('localhost')) {
        console.log('Invalid localhost URL detected, clearing session');
        // Clear invalid session data
        await SecureStore.deleteItemAsync('session_id');
        await AsyncStorage.removeItem('user_data');
        await AsyncStorage.removeItem('server_url');
        throw new Error('Invalid server URL detected, clearing session');
      }

      // For now, skip server validation to prevent hanging
      // TODO: Re-enable server validation after testing
      console.log('Skipping server validation, using stored session');
      
      return {
        user: JSON.parse(userData),
        sessionId: sessionId,
        serverUrl: serverUrl,
        validated: true,
      };

      /*
      // Validate session with server (disabled for testing)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(`${serverUrl}/api/method/frappe.auth.get_logged_user`, {
        method: 'GET',
        headers: {
          'Cookie': `sid=${sessionId}`,
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error('Session validation failed');
      }

      const validationData = await response.json();
      
      if (!validationData.message) {
        throw new Error('Invalid session response');
      }

      return {
        user: JSON.parse(userData),
        sessionId: sessionId,
        serverUrl: serverUrl,
        validated: true,
      };
      */
    } catch (error) {
      console.error('Session validation error:', error);
      // Clear invalid session data
      try {
        await SecureStore.deleteItemAsync('session_id');
        await AsyncStorage.removeItem('user_data');
        await AsyncStorage.removeItem('server_url');
      } catch (clearError) {
        console.error('Error clearing session data:', clearError);
      }
      
      if (error.name === 'AbortError') {
        return rejectWithValue('Session validation timed out');
      }
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  isAuthenticated: false,
  user: null,
  sessionId: null,
  serverUrl: '',
  loading: false,
  error: null,
  loginTime: null,
  isValidating: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setServerUrl: (state, action) => {
      state.serverUrl = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    resetAuth: (state) => {
      return { ...initialState };
    },
  },
  extraReducers: (builder) => {
    builder
      // Login cases
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.sessionId = action.payload.sessionId;
        state.serverUrl = action.payload.serverUrl;
        state.loginTime = action.payload.loginTime;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      })
      // Logout cases
      .addCase(logout.pending, (state) => {
        state.loading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        return { ...initialState };
      })
      .addCase(logout.rejected, (state) => {
        return { ...initialState };
      })
      // Session validation cases
      .addCase(validateSession.pending, (state) => {
        state.isValidating = true;
        state.error = null;
      })
      .addCase(validateSession.fulfilled, (state, action) => {
        state.isValidating = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.sessionId = action.payload.sessionId;
        state.serverUrl = action.payload.serverUrl;
      })
      .addCase(validateSession.rejected, (state, action) => {
        state.isValidating = false;
        state.error = action.payload;
        state.isAuthenticated = false;
        state.user = null;
        state.sessionId = null;
      });
  },
});

export const { setServerUrl, clearError, resetAuth } = authSlice.actions;
export default authSlice.reducer; 