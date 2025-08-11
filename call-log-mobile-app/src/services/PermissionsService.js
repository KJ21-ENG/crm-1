import { Platform, PermissionsAndroid, Alert, Linking } from 'react-native'
import DebugLogger from './DebugLogger'

let Bubble = null
try {
  // eslint-disable-next-line global-require
  Bubble = require('react-native-floating-bubble')
} catch (_) {
  Bubble = null
}

export async function requestNotificationPermissionIfNeeded() {
  if (Platform.OS !== 'android') return true
  try {
    // Android 13+ (API 33) requires explicit POST_NOTIFICATIONS
    const apiLevel = Platform.Version
    const isApi33Plus = typeof apiLevel === 'number' ? apiLevel >= 33 : parseInt(String(apiLevel), 10) >= 33
    if (!isApi33Plus) return true
    const granted = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS)
    try { await DebugLogger.log('PERM', 'POST_NOTIFICATIONS result', { granted }) } catch (_) {}
    return granted === PermissionsAndroid.RESULTS.GRANTED
  } catch (_) {
    return true
  }
}

export async function requestCallLogPermission() {
  if (Platform.OS !== 'android') return false
  try {
    const has = await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.READ_CALL_LOG)
    try { await DebugLogger.log('PERM', 'READ_CALL_LOG status', { has }) } catch (_) {}
    if (has) return true
    const granted = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.READ_CALL_LOG)
    try { await DebugLogger.log('PERM', 'READ_CALL_LOG request', { granted }) } catch (_) {}
    return granted === PermissionsAndroid.RESULTS.GRANTED
  } catch (e) {
    Alert.alert('Permission Error', 'Failed to request call log permission.')
    return false
  }
}

export async function requestOverlayPermissionIfAvailable() {
  if (!Bubble || Platform.OS !== 'android') return true
  try {
    const granted = await Bubble.requestPermission()
    try { await DebugLogger.log('PERM', 'OVERLAY result', { granted }) } catch (_) {}
    return !!granted
  } catch (_) {
    return false
  }
}

export async function openBatteryOptimizationSettings() {
  if (Platform.OS !== 'android') return
  try {
    // Open the battery optimization settings screen
    await Linking.openSettings()
  } catch (_) {}
}

export async function requestAllStartupPermissions() {
  const notif = await requestNotificationPermissionIfNeeded()
  const calllog = await requestCallLogPermission()
  const overlay = await requestOverlayPermissionIfAvailable()
  if (!calllog) {
    Alert.alert('Permission Required', 'Call log permission is required for auto-sync to work.')
  }
  return notif && calllog && overlay
}


