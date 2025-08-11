// Android Foreground Service using react-native-background-actions
// Shows a persistent notification and runs a sync loop every N ms
import { Platform } from 'react-native'
import callLogSyncService from './CallLogSyncService'
import DebugLogger from './DebugLogger'
import { ensureNotificationChannel, CRM_SYNC_CHANNEL_ID } from './NotificationHelper'

let BackgroundService = null
try {
  // Prefer default export from 2.6.x
  // eslint-disable-next-line global-require
  const mod = require('react-native-background-actions')
  BackgroundService = mod?.default || mod
} catch (_) {
  BackgroundService = null
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function syncLoop(taskData) {
  const delay = taskData?.delay ?? 60_000
  await DebugLogger.log('FG', 'syncLoop start', { delay })
  try {
    await callLogSyncService.init()
    await DebugLogger.log('FG', 'callLogSyncService.init ok')
  } catch (_) {}

  // Keep syncing while the service is running
  // BackgroundService.isRunning() is available on the instance
  while (BackgroundService && BackgroundService.isRunning?.()) {
    try {
      await DebugLogger.log('FG', 'syncCallLogs tick')
      const res = await callLogSyncService.syncCallLogs()
      await DebugLogger.log('FG', 'syncCallLogs result', res)
    } catch (_) {}
    // Update notification countdown each second
    let remaining = Math.floor(delay / 1000)
    while (remaining > 0 && BackgroundService.isRunning?.()) {
      try {
        await BackgroundService.updateNotification({
          taskDesc: `Next sync in ${remaining}s`,
        })
        if (remaining % 10 === 0) {
          await DebugLogger.log('FG', 'countdown', { remaining })
        }
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
  if (Platform.OS !== 'android') {
    await DebugLogger.log('FG', 'skip start: not android')
    return
  }
  if (!BackgroundService) {
    await DebugLogger.error('FG', 'skip start: background-actions not available (Expo Go or module not linked)')
    return
  }
  try {
    if (BackgroundService.isRunning?.()) return
    await DebugLogger.log('FG', 'starting foreground service', { delayMs })
    await ensureNotificationChannel()
    const opts = {
      ...notificationOptions,
      parameters: { delay: delayMs },
      allowExecutionInForeground: true,
      stopWithTask: false,
      // Ensure proper foreground service classification on Android 10+
      foregroundServiceType: 'dataSync',
      // Try to bind to our high-importance channel id
      notificationChannelId: CRM_SYNC_CHANNEL_ID,
      // Some versions of the lib expect these top-level keys
      notificationTitle: notificationOptions.taskTitle,
      notificationText: notificationOptions.taskDesc,
      notificationIcon: notificationOptions.taskIcon,
      notificationColor: notificationOptions.color,
    }
    await DebugLogger.log('FG', 'opts', opts)
    await BackgroundService.start(syncLoop, opts)
    await DebugLogger.log('FG', 'foreground service started')
    // Try to show floating bubble as a background indicator (optional)
    // Bubble removed (optional module caused install conflicts). No-op.
  } catch (e) {
    try { console.error('startForegroundSync failed:', e?.message || e) } catch (_) {}
    await DebugLogger.error('FG', 'start failed', { message: e?.message })
  }
}

export async function stopForegroundSync() {
  if (!BackgroundService) return
  try {
    if (BackgroundService.isRunning?.()) {
      await BackgroundService.stop()
    }
  } catch (_) {}
}

export function isForegroundServiceAvailable() {
  return !!BackgroundService
}

export function isForegroundServiceRunning() {
  try {
    return !!(BackgroundService && BackgroundService.isRunning?.())
  } catch (_) {
    return false
  }
}

export function getForegroundDebugInfo() {
  let running = null
  try { running = BackgroundService?.isRunning?.() ?? null } catch (_) { running = null }
  return {
    hasModule: !!BackgroundService,
    isRunning: running,
    platform: Platform.OS,
  }
}

export async function pingForegroundNotification(text = 'Ping') {
  if (!BackgroundService) return false
  try {
    await BackgroundService.updateNotification({ taskDesc: String(text) })
    await DebugLogger.log('FG', 'pingForegroundNotification', { text })
    return true
  } catch (e) {
    await DebugLogger.error('FG', 'pingForegroundNotification failed', { message: e?.message })
    return false
  }
}

