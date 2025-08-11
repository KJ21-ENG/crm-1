import * as Notifications from 'expo-notifications'
import { Platform } from 'react-native'
import DebugLogger from './DebugLogger'

export const CRM_SYNC_CHANNEL_ID = 'crm-sync'

export async function ensureNotificationChannel() {
  if (Platform.OS !== 'android') return true
  try {
    await Notifications.setNotificationChannelAsync(CRM_SYNC_CHANNEL_ID, {
      name: 'CRM Sync',
      importance: Notifications.AndroidImportance.HIGH,
      lights: true,
      vibrationPattern: [0, 250, 250, 250],
      lockscreenVisibility: Notifications.AndroidNotificationVisibility.PUBLIC,
      bypassDnd: false,
      enableVibrate: true,
    })
    await DebugLogger.log('NTF', 'channel ensured', { id: CRM_SYNC_CHANNEL_ID })
    return true
  } catch (e) {
    await DebugLogger.error('NTF', 'ensureNotificationChannel failed', { message: e?.message })
    return false
  }
}

export async function sendTestLocalNotification(body = 'Test local notification') {
  try {
    await ensureNotificationChannel()
    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: 'CRM Sync',
        body,
        sound: null,
      },
      trigger: null,
    })
    await DebugLogger.log('NTF', 'local notification scheduled', { id })
    return true
  } catch (e) {
    await DebugLogger.error('NTF', 'sendTestLocalNotification failed', { message: e?.message })
    return false
  }
}

export async function getNotificationPermissionStatus() {
  try {
    const settings = await Notifications.getPermissionsAsync()
    const canAskAgain = settings?.canAskAgain ?? null
    const status = settings?.status ?? null
    await DebugLogger.log('NTF', 'permission status', { status, canAskAgain })
    return { status, canAskAgain }
  } catch (e) {
    await DebugLogger.error('NTF', 'getNotificationPermissionStatus failed', { message: e?.message })
    return { status: null, canAskAgain: null }
  }
}


