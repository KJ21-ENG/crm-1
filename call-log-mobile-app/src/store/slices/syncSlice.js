import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isSync: false,
  syncProgress: 0,
  lastSyncTime: null,
  pendingSync: 0,
  syncErrors: [],
  syncStatus: 'idle', // 'idle', 'syncing', 'success', 'error'
  autoSync: true,
};

const syncSlice = createSlice({
  name: 'sync',
  initialState,
  reducers: {
    startSync: (state) => {
      state.isSync = true;
      state.syncStatus = 'syncing';
      state.syncProgress = 0;
      state.syncErrors = [];
    },
    setSyncProgress: (state, action) => {
      state.syncProgress = action.payload;
    },
    syncComplete: (state, action) => {
      state.isSync = false;
      state.syncStatus = 'success';
      state.syncProgress = 100;
      state.lastSyncTime = new Date().toISOString();
      state.pendingSync = action.payload?.pendingSync || 0;
    },
    syncError: (state, action) => {
      state.isSync = false;
      state.syncStatus = 'error';
      state.syncErrors.push(action.payload);
    },
    clearSyncErrors: (state) => {
      state.syncErrors = [];
    },
    setPendingSync: (state, action) => {
      state.pendingSync = action.payload;
    },
    setAutoSync: (state, action) => {
      state.autoSync = action.payload;
    },
    resetSyncStatus: (state) => {
      state.syncStatus = 'idle';
      state.syncProgress = 0;
    },
  },
});

export const {
  startSync,
  setSyncProgress,
  syncComplete,
  syncError,
  clearSyncErrors,
  setPendingSync,
  setAutoSync,
  resetSyncStatus,
} = syncSlice.actions;

export default syncSlice.reducer; 