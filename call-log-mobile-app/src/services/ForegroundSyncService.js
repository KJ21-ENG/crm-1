// Android Foreground Service using react-native-background-actions
// Shows a persistent notification and runs a sync loop every N ms
import { Platform } from 'react-native'
import callLogSyncService from './CallLogSyncService'

let BackgroundService = null
try {
  // eslint-disable-next-line global-require
  BackgroundService = require('react-native-background-actions')
} catch (_) {
  BackgroundService = null
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function syncLoop(taskData) {
  const delay = taskData?.delay ?? 60_000
  try {
    await callLogSyncService.init()
  } catch (_) {}

  // Keep syncing while the service is running
  // BackgroundService.isRunning() is available on the instance
  while (BackgroundService && BackgroundService.isRunning?.()) {
    try {
      await callLogSyncService.syncCallLogs()
    } catch (_) {}
    await sleep(delay)
  }
}

const notificationOptions = {
  taskName: 'CRM Sync',
  taskTitle: 'CRM Call Logs Sync',
  taskDesc: 'Syncing device call logs every minute',
  taskIcon: { name: 'ic_launcher', type: 'mipmap' },
  color: '#10B981',
  linkingURI: 'crm-call-log-sync://',
  parameters: { delay: 60_000 },
}

export async function startForegroundSync(delayMs = 60_000) {
  if (Platform.OS !== 'android' || !BackgroundService) return
  try {
    if (BackgroundService.isRunning?.()) return
    const opts = { ...notificationOptions, parameters: { delay: delayMs } }
    await BackgroundService.start(syncLoop, opts)
  } catch (_) {}
}

export async function stopForegroundSync() {
  if (!BackgroundService) return
  try {
    if (BackgroundService.isRunning?.()) {
      await BackgroundService.stop()
    }
  } catch (_) {}
}


