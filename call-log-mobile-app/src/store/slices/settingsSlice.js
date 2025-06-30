import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  serverUrl: 'http://192.168.29.94:8000',
  autoSync: true,
  syncInterval: 15, // minutes
  wifiOnly: false,
  notifications: true,
  theme: 'light',
  language: 'en',
  privacySettings: {
    excludeNumbers: [],
    anonymizeData: false,
  },
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateServerUrl: (state, action) => {
      state.serverUrl = action.payload;
    },
    toggleAutoSync: (state) => {
      state.autoSync = !state.autoSync;
    },
    setSyncInterval: (state, action) => {
      state.syncInterval = action.payload;
    },
    toggleWifiOnly: (state) => {
      state.wifiOnly = !state.wifiOnly;
    },
    toggleNotifications: (state) => {
      state.notifications = !state.notifications;
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
    addExcludedNumber: (state, action) => {
      if (!state.privacySettings.excludeNumbers.includes(action.payload)) {
        state.privacySettings.excludeNumbers.push(action.payload);
      }
    },
    removeExcludedNumber: (state, action) => {
      state.privacySettings.excludeNumbers = state.privacySettings.excludeNumbers.filter(
        number => number !== action.payload
      );
    },
    toggleAnonymizeData: (state) => {
      state.privacySettings.anonymizeData = !state.privacySettings.anonymizeData;
    },
    resetSettings: (state) => {
      return { ...initialState };
    },
  },
});

export const {
  updateServerUrl,
  toggleAutoSync,
  setSyncInterval,
  toggleWifiOnly,
  toggleNotifications,
  setTheme,
  setLanguage,
  addExcludedNumber,
  removeExcludedNumber,
  toggleAnonymizeData,
  resetSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer; 