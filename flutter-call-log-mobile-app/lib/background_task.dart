import 'dart:async';
import 'dart:isolate';

import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';
import 'call_log_sync_service.dart';

@pragma('vm:entry-point')
void startCallback() {
  FlutterForegroundTask.setTaskHandler(SyncTaskHandler());
}

class SyncTaskHandler extends TaskHandler {
  Timer? _timer;
  int _countdown = 60;

  @override
  Future<void> onStart(DateTime timestamp, SendPort? sendPort) async {
    await ApiService.instance.init();
    _timer = Timer.periodic(const Duration(seconds: 1), (t) async {
      if (_countdown <= 0) {
        _countdown = 60;
        try {
          await CallLogSyncService.instance.syncOnce();
        } catch (_) {}
      } else {
        _countdown -= 1;
      }
      try {
        await FlutterForegroundTask.updateService(
          notificationText: 'Next sync in ${_countdown}s',
        );
      } catch (_) {}
    });
  }

  @override
  Future<void> onDestroy(DateTime timestamp, SendPort? sendPort) async {
    _timer?.cancel();
  }

  @override
  Future<void> onRepeatEvent(DateTime timestamp, SendPort? sendPort) async {}
}


