import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for syncing call logs
export const syncCallLogs = createAsyncThunk(
  'sync/syncCallLogs',
  async (callLogs, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      
      if (!auth.isAuthenticated) {
        throw new Error('Not authenticated');
      }

      // This will be implemented with actual CRM API call
      const response = await fetch(`${auth.serverUrl}/api/method/crm.mobile_sync.sync_call_logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.token}`,
        },
        body: JSON.stringify({ call_logs: callLogs }),
      });

      if (!response.ok) {
        throw new Error('Sync failed');
      }

      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  isSyncing: false,
  lastSyncTime: null,
  syncProgress: 0,
  error: null,
  syncHistory: [],
  autoSyncEnabled: true,
  syncInterval: 30, // minutes
  wifiOnlySync: true,
};

const syncSlice = createSlice({
  name: 'sync',
  initialState,
  reducers: {
    setAutoSync: (state, action) => {
      state.autoSyncEnabled = action.payload;
    },
    setSyncInterval: (state, action) => {
      state.syncInterval = action.payload;
    },
    setWifiOnlySync: (state, action) => {
      state.wifiOnlySync = action.payload;
    },
    addSyncHistory: (state, action) => {
      state.syncHistory.unshift({
        ...action.payload,
        timestamp: new Date().toISOString(),
      });
      
      // Keep only last 50 sync history entries
      if (state.syncHistory.length > 50) {
        state.syncHistory = state.syncHistory.slice(0, 50);
      }
    },
    clearSyncHistory: (state) => {
      state.syncHistory = [];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(syncCallLogs.pending, (state) => {
        state.isSyncing = true;
        state.error = null;
        state.syncProgress = 0;
      })
      .addCase(syncCallLogs.fulfilled, (state, action) => {
        state.isSyncing = false;
        state.lastSyncTime = new Date().toISOString();
        state.syncProgress = 100;
        
        // Add successful sync to history
        state.syncHistory.unshift({
          status: 'success',
          count: action.payload.synced_count || 0,
          timestamp: new Date().toISOString(),
        });
      })
      .addCase(syncCallLogs.rejected, (state, action) => {
        state.isSyncing = false;
        state.error = action.payload;
        state.syncProgress = 0;
        
        // Add failed sync to history
        state.syncHistory.unshift({
          status: 'failed',
          error: action.payload,
          timestamp: new Date().toISOString(),
        });
      });
  },
});

export const { 
  setAutoSync, 
  setSyncInterval, 
  setWifiOnlySync, 
  addSyncHistory, 
  clearSyncHistory, 
  clearError 
} = syncSlice.actions;

export default syncSlice.reducer; 