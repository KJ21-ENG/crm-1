// Placeholder for native headless integration or Expo BackgroundFetch bridge
// This file can be used to register OS-level periodic sync when app is not in foreground.
// For production, wire one of the following:
// - Expo BackgroundFetch + TaskManager (recommended in Expo-managed env)
// - Android Headless JS (react-native-background-actions or a custom Service)

import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';
import callLogSyncService from './CallLogSyncService';
import DebugLogger from './DebugLogger';

export const BACKGROUND_SYNC_TASK = 'crm-background-calllog-sync';

export function registerBackgroundFetch(intervalSeconds = 60) {
  try {
    TaskManager.defineTask(BACKGROUND_SYNC_TASK, async () => {
      try {
        await DebugLogger.log('BGF', 'Task tick')
        await callLogSyncService.init();
        await DebugLogger.log('BGF', 'init ok')
        const result = await callLogSyncService.syncCallLogs();
        await DebugLogger.log('BGF', 'sync result', result)
        return result?.success ? BackgroundFetch.BackgroundFetchResult.NewData : BackgroundFetch.BackgroundFetchResult.Failed;
      } catch (e) {
        await DebugLogger.error('BGF', 'Task error', { message: e?.message })
        return BackgroundFetch.BackgroundFetchResult.Failed;
      }
    });

    return BackgroundFetch.registerTaskAsync(BACKGROUND_SYNC_TASK, {
      minimumInterval: intervalSeconds,
      stopOnTerminate: false,
      startOnBoot: true,
      requiredNetworkType: BackgroundFetch.NetworkType.ANY,
      forceAlarmManager: true,
      enableHeadless: true,
    });
  } catch (_) {
    return Promise.resolve();
  }
}

export function unregisterBackgroundFetch() {
  return BackgroundFetch.unregisterTaskAsync(BACKGROUND_SYNC_TASK).catch(() => {});
}


