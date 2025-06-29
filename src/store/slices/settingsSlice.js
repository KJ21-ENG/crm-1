import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  theme: 'light', // light, dark, system
  notifications: {
    syncComplete: true,
    syncError: true,
    newCallLogs: false,
  },
  privacy: {
    excludedNumbers: [],
    anonymizeData: false,
  },
  sync: {
    backgroundSync: true,
    syncFrequency: 30, // minutes
    wifiOnly: true,
    immediateSync: false,
  },
  app: {
    language: 'en',
    biometricAuth: false,
    rememberCredentials: true,
  },
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateTheme: (state, action) => {
      state.theme = action.payload;
    },
    updateNotificationSettings: (state, action) => {
      state.notifications = { ...state.notifications, ...action.payload };
    },
    updatePrivacySettings: (state, action) => {
      state.privacy = { ...state.privacy, ...action.payload };
    },
    updateSyncSettings: (state, action) => {
      state.sync = { ...state.sync, ...action.payload };
    },
    updateAppSettings: (state, action) => {
      state.app = { ...state.app, ...action.payload };
    },
    addExcludedNumber: (state, action) => {
      if (!state.privacy.excludedNumbers.includes(action.payload)) {
        state.privacy.excludedNumbers.push(action.payload);
      }
    },
    removeExcludedNumber: (state, action) => {
      state.privacy.excludedNumbers = state.privacy.excludedNumbers.filter(
        number => number !== action.payload
      );
    },
    resetSettings: () => initialState,
  },
});

export const {
  updateTheme,
  updateNotificationSettings,
  updatePrivacySettings,
  updateSyncSettings,
  updateAppSettings,
  addExcludedNumber,
  removeExcludedNumber,
  resetSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer; 