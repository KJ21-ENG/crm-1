import 'dart:async';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';

import 'background_task.dart';
import 'call_log_sync_service.dart';

@pragma('vm:entry-point')
void widgetBackgroundMain() {
  // This entrypoint runs in a headless engine started by the native widget provider.
  WidgetsFlutterBinding.ensureInitialized();

  const MethodChannel channel = MethodChannel('crm/widget');
  channel.setMethodCallHandler((call) async {
    switch (call.method) {
      case 'manualSync':
        return await CallLogSyncService.instance.syncOnce();
      case 'toggleBackground':
        final running = await FlutterForegroundTask.isRunningService;
        if (running) {
          await FlutterForegroundTask.stopService();
          return {'running': false};
        }
        FlutterForegroundTask.init(
          androidNotificationOptions: AndroidNotificationOptions(
                // Use a new channel id to ensure channel is created with LOW importance
                channelId: 'crm_sync_low',
            channelName: 'CRM Sync',
            channelDescription: 'Syncs call logs periodically',
        // Use LOW importance and priority so notification appears only in drawer
        channelImportance: NotificationChannelImportance.LOW,
        priority: NotificationPriority.LOW,
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
            autoRunOnBoot: true,
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
      case 'getLastSync':
        final prefs = await SharedPreferences.getInstance();
        final ts = prefs.getInt('last_call_log_sync') ?? prefs.getInt('flutter.last_call_log_sync') ?? 0;
        return {'last_call_ms': ts};
      default:
        throw MissingPluginException('Not implemented: ${call.method}');
    }
  });
}



