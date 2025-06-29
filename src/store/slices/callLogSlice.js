import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching call logs
export const fetchCallLogs = createAsyncThunk(
  'callLog/fetchCallLogs',
  async (_, { rejectWithValue }) => {
    try {
      // This will be implemented with actual call log API
      // For now, return empty array
      return [];
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  callLogs: [],
  filteredCallLogs: [],
  loading: false,
  error: null,
  lastFetch: null,
  filters: {
    dateRange: 'today',
    callType: 'all', // all, incoming, outgoing, missed
    syncStatus: 'all', // all, synced, pending, failed
  },
};

const callLogSlice = createSlice({
  name: 'callLog',
  initialState,
  reducers: {
    addCallLog: (state, action) => {
      state.callLogs.unshift(action.payload);
    },
    updateCallLog: (state, action) => {
      const index = state.callLogs.findIndex(log => log.id === action.payload.id);
      if (index !== -1) {
        state.callLogs[index] = { ...state.callLogs[index], ...action.payload };
      }
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearCallLogs: (state) => {
      state.callLogs = [];
      state.filteredCallLogs = [];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCallLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCallLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.callLogs = action.payload;
        state.lastFetch = new Date().toISOString();
      })
      .addCase(fetchCallLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { 
  addCallLog, 
  updateCallLog, 
  setFilters, 
  clearCallLogs, 
  clearError 
} = callLogSlice.actions;

export default callLogSlice.reducer; 