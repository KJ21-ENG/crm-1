import 'dart:async';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';

import 'background_task.dart';
import 'call_log_sync_service.dart';

class WidgetBridge {
  static const MethodChannel _channel = MethodChannel('crm/widget');

  /// Initialize widget bridge and register handlers for native -> Dart calls.
  static Future<void> init() async {
    _channel.setMethodCallHandler(_handleCall);
  }

  static Future<dynamic> _handleCall(MethodCall call) async {
    switch (call.method) {
      case 'manualSync':
        final res = await CallLogSyncService.instance.syncOnce();
        return res;
      case 'toggleBackground':
        return await _toggleBackground();
      case 'getLastSync':
        return await _getLastSync();
      case 'isBackgroundRunning':
        return await FlutterForegroundTask.isRunningService;
      default:
        throw MissingPluginException('Not implemented: ${call.method}');
    }
  }

  static Future<Map<String, dynamic>> _getLastSync() async {
    final prefs = await SharedPreferences.getInstance();
    final ts = prefs.getInt('last_call_log_sync') ?? prefs.getInt('flutter.last_call_log_sync') ?? 0;
    return {'last_call_ms': ts};
  }

  static Future<Map<String, dynamic>> _toggleBackground() async {
    final running = await FlutterForegroundTask.isRunningService;
    if (running) {
      await FlutterForegroundTask.stopService();
      return {'running': false};
    }

    // Try to start service similarly to HomePage._startForeground()
    FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        channelId: 'crm_sync',
        channelName: 'CRM Sync',
        channelDescription: 'Syncs call logs periodically',
        channelImportance: NotificationChannelImportance.HIGH,
        priority: NotificationPriority.HIGH,
        iconData: const NotificationIconData(
          resType: ResourceType.mipmap,
          resPrefix: ResourcePrefix.ic,
          name: 'launcher',
        ),
        buttons: const [NotificationButton(id: 'stop', text: 'Stop')],
      ),
      iosNotificationOptions: const IOSNotificationOptions(showNotification: false),
      foregroundTaskOptions: const ForegroundTaskOptions(
        interval: 1000,
        autoRunOnBoot: false,
        allowWakeLock: true,
      ),
    );
    await FlutterForegroundTask.startService(
      notificationTitle: 'CRM Call Logs Sync',
      notificationText: 'Running background sync',
      callback: startCallback,
    );
    final after = await FlutterForegroundTask.isRunningService;
    return {'running': after};
  }
}


