// Placeholder for native headless integration or Expo BackgroundFetch bridge
// This file can be used to register OS-level periodic sync when app is not in foreground.
// For production, wire one of the following:
// - Expo BackgroundFetch + TaskManager (recommended in Expo-managed env)
// - Android Headless JS (react-native-background-actions or a custom Service)

import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';
import callLogSyncService from './CallLogSyncService';

export const BACKGROUND_SYNC_TASK = 'crm-background-calllog-sync';

export function registerBackgroundFetch(intervalSeconds = 60) {
  try {
    TaskManager.defineTask(BACKGROUND_SYNC_TASK, async () => {
      try {
        await callLogSyncService.init();
        const result = await callLogSyncService.syncCallLogs();
        return result?.success ? BackgroundFetch.BackgroundFetchResult.NewData : BackgroundFetch.BackgroundFetchResult.Failed;
      } catch (e) {
        return BackgroundFetch.BackgroundFetchResult.Failed;
      }
    });

    return BackgroundFetch.registerTaskAsync(BACKGROUND_SYNC_TASK, {
      minimumInterval: intervalSeconds,
      stopOnTerminate: false,
      startOnBoot: true,
      requiredNetworkType: BackgroundFetch.NetworkType.ANY,
    });
  } catch (_) {
    return Promise.resolve();
  }
}

export function unregisterBackgroundFetch() {
  return BackgroundFetch.unregisterTaskAsync(BACKGROUND_SYNC_TASK).catch(() => {});
}


