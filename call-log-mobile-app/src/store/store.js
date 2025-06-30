import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import callLogReducer from './slices/callLogSlice';
import syncReducer from './slices/syncSlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    callLog: callLogReducer,
    sync: syncReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export default store; 