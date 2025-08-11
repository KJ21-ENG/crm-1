import 'package:call_log/call_log.dart';
import 'dart:math' as math;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/services.dart';

import 'api_service.dart';
import 'phone_transform.dart';

class CallLogSyncService {
  CallLogSyncService._internal();
  static final CallLogSyncService instance = CallLogSyncService._internal();

  Future<int> _getLastSyncMillis() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('last_call_log_sync') ?? 0;
  }

  Future<void> _setLastSyncMillis(int ts) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('last_call_log_sync', ts);
  }

  Future<void> _setLastCounts({int success = 0, int failure = 0, int duplicate = 0}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('last_sync_success_count', success);
    await prefs.setInt('last_sync_failure_count', failure);
    await prefs.setInt('last_sync_duplicate_count', duplicate);
  }

  Future<void> _incrementTodaySuccess(int success) async {
    final prefs = await SharedPreferences.getInstance();
    final now = DateTime.now();
    final dayKey = '${now.year.toString().padLeft(4, '0')}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
    final storedDay = prefs.getString('today_sync_date');
    int total = 0;
    if (storedDay == dayKey) {
      total = prefs.getInt('today_sync_success_total') ?? 0;
    }
    total += success;
    await prefs.setString('today_sync_date', dayKey);
    await prefs.setInt('today_sync_success_total', total);
  }

  Future<String?> _getUserMobile() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString('user_mobile');
    if (stored != null && stored.isNotEmpty) return stored;
    try {
      final profile = await ApiService.instance.getUserProfile();
      final msg = profile['message'] as Map<String, dynamic>?;
      final data = msg?['data'] as Map<String, dynamic>?;
      final mobile = data?['mobile_no'] as String?;
      if (mobile != null && mobile.isNotEmpty) {
        await prefs.setString('user_mobile', mobile);
      }
      return mobile;
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>> syncOnce() async {
    // Ensure call log permission at runtime (explicit READ_CALL_LOG via platform)
    const channel = MethodChannel('crm/permissions');
    var hasRead = false;
    try {
      hasRead = (await channel.invokeMethod<bool>('hasReadCallLog')) ?? false;
    } catch (_) {}
    if (!hasRead) {
      try {
        hasRead = (await channel.invokeMethod<bool>('requestReadCallLog')) ?? false;
      } catch (_) {}
    }
    if (!hasRead) {
      // Fallback to PermissionHandler phone group
      final phoneStatus = await Permission.phone.status;
      if (!phoneStatus.isGranted) {
        final req = await Permission.phone.request();
        if (!req.isGranted) {
          return { 'success': false, 'error': 'PERMISSION_DENIED' };
        }
      }
    }

    final authed = await ApiService.instance.isAuthenticated();
    if (!authed) {
      return { 'success': false, 'error': 'NOT_AUTHENTICATED' };
    }

    final last = await _getLastSyncMillis();
    // Safety window so we don't miss calls that OEMs write late or with slightly older timestamps
    final safetyWindowMs = 2 * 60 * 1000; // 2 minutes
    final since = last > 0 ? math.max(0, last - safetyWindowMs) : 0;
    final userMobile = (await _getUserMobile()) ?? '+911234567890';
    final now = DateTime.now().millisecondsSinceEpoch;

    final Iterable<CallLogEntry> entries = await CallLog.query(dateFrom: since);
    final logs = entries.toList()
      ..sort((a,b) => (b.timestamp ?? 0).compareTo(a.timestamp ?? 0));

    if (logs.isEmpty) {
      await _setLastSyncMillis(now);
      await _setLastCounts(success: 0, failure: 0, duplicate: 0);
      return { 'success': true, 'message': 'No new call logs' };
    }

    final mapped = logs.map((e) => toCrmCallLog(e, userMobile)).toList();
    final res = await ApiService.instance.syncCallLogs(mapped);

    // Accept both {message:{success:..}} and {success:..}
    final payload = res['message'] ?? res;
    if (payload is Map && (payload['success'] == true || payload['success_count'] != null)) {
      // Advance sync cursor to the latest call timestamp we processed to avoid gaps
      final latestTs = logs.isNotEmpty
          ? (logs.map((e) => e.timestamp ?? 0).fold<int>(0, (p, n) => n > p ? n : p))
          : now;
      await _setLastSyncMillis(latestTs);
      final sc = (payload['success_count'] ?? 0) as int;
      final fc = (payload['failure_count'] ?? 0) as int;
      final dc = (payload['duplicate_count'] ?? 0) as int;
      await _setLastCounts(success: sc, failure: fc, duplicate: dc);
      if (sc > 0) {
        await _incrementTodaySuccess(sc);
      }
    }
    return payload is Map<String, dynamic> ? payload : { 'success': true };
  }
}


