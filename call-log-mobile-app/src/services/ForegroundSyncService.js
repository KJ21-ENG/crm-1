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
    // Update notification countdown each second
    let remaining = Math.floor(delay / 1000)
    while (remaining > 0 && BackgroundService.isRunning?.()) {
      try {
        await BackgroundService.updateNotification({
          taskDesc: `Next sync in ${remaining}s`,
        })
      } catch (_) {}
      await sleep(1000)
      remaining -= 1
    }
  }
}

const notificationOptions = {
  taskName: 'CRM Sync',
  taskTitle: 'CRM Call Logs Sync',
  taskDesc: 'Next sync in 60s',
  taskIcon: { name: 'ic_launcher', type: 'mipmap' },
  color: '#10B981',
  linkingURI: 'crm-call-log-sync://',
  parameters: { delay: 60_000 },
}

export async function startForegroundSync(delayMs = 60_000) {
  if (Platform.OS !== 'android' || !BackgroundService) return
  try {
    if (BackgroundService.isRunning?.()) return
    const opts = {
      ...notificationOptions,
      parameters: { delay: delayMs },
      allowExecutionInForeground: true,
      stopWithTask: false,
      // Some versions of the lib expect these top-level keys
      notificationTitle: notificationOptions.taskTitle,
      notificationText: notificationOptions.taskDesc,
      notificationIcon: notificationOptions.taskIcon,
      notificationColor: notificationOptions.color,
    }
    await BackgroundService.start(syncLoop, opts)
    // Try to show floating bubble as a background indicator (optional)
    try {
      // eslint-disable-next-line global-require
      const bubble = require('react-native-floating-bubble')
      const granted = await bubble.requestPermission()
      if (granted) {
        await bubble.showFloatingBubble(80, 200)
      }
    } catch (_) {}
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


