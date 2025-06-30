import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  callLogs: [],
  loading: false,
  error: null,
  lastSync: null,
  totalCount: 0,
};

const callLogSlice = createSlice({
  name: 'callLog',
  initialState,
  reducers: {
    setCallLogs: (state, action) => {
      state.callLogs = action.payload;
      state.totalCount = action.payload.length;
    },
    addCallLog: (state, action) => {
      state.callLogs.unshift(action.payload);
      state.totalCount += 1;
    },
    updateCallLog: (state, action) => {
      const index = state.callLogs.findIndex(log => log.id === action.payload.id);
      if (index !== -1) {
        state.callLogs[index] = action.payload;
      }
    },
    clearCallLogs: (state) => {
      state.callLogs = [];
      state.totalCount = 0;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setLastSync: (state, action) => {
      state.lastSync = action.payload;
    },
  },
});

export const {
  setCallLogs,
  addCallLog,
  updateCallLog,
  clearCallLogs,
  setLoading,
  setError,
  clearError,
  setLastSync,
} = callLogSlice.actions;

export default callLogSlice.reducer; 