import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  ApiService._internal();
  static final ApiService instance = ApiService._internal();

  final _dio = Dio();
  final _secure = const FlutterSecureStorage();
  String _baseUrl = 'https://eshin.in';
  String? _sessionId;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _baseUrl = prefs.getString('server_url') ?? _baseUrl;
    _sessionId = await _secure.read(key: 'session_id');
    _dio.options.baseUrl = _baseUrl;
    if (_sessionId != null) {
      _dio.options.headers['Cookie'] = 'sid=$_sessionId';
    }
  }

  void setBaseUrl(String url) {
    // remove trailing slashes
    _baseUrl = url.replaceAll(RegExp(r'/+$'), '');
    _dio.options.baseUrl = _baseUrl;
  }

  Future<void> saveBaseUrl(String url) async {
    setBaseUrl(url);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_url', _baseUrl);
  }

  Future<void> setSessionId(String sid) async {
    _sessionId = sid;
    await _secure.write(key: 'session_id', value: sid);
    _dio.options.headers['Cookie'] = 'sid=$sid';
  }

  Future<bool> login(String username, String password) async {
    try {
      final res = await _dio.post(
        '/api/method/login',
        data: {'usr': username, 'pwd': password},
        options: Options(
          contentType: Headers.formUrlEncodedContentType,
          followRedirects: false,
          validateStatus: (_) => true,
        ),
      );

      final cookies = res.headers.map['set-cookie'] ?? <String>[];
      final cookieStr = cookies.join('; ');
      final match = RegExp(r'sid=([^;]+)').firstMatch(cookieStr);
      final sid = match != null ? match.group(1) : null;
      if (sid != null && sid!.isNotEmpty) {
        await setSessionId(sid);
        return true;
      }
      return await isAuthenticated();
    } catch (_) {
      return false;
    }
  }

  Future<void> logout() async {
    try { await _dio.get('/api/method/logout'); } catch (_) {}
    _sessionId = null;
    await _secure.delete(key: 'session_id');
    _dio.options.headers.remove('Cookie');
  }

  Future<bool> isAuthenticated() async {
    try {
      final res = await _dio.get('/api/method/frappe.auth.get_logged_user');
      return res.data != null && res.data['message'] != null;
    } catch (_) {
      return false;
    }
  }

  Future<String?> getLoggedUser() async {
    try {
      final res = await _dio.get('/api/method/frappe.auth.get_logged_user');
      return res.data?['message'] as String?;
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>> getUserProfile() async {
    final res = await _dio.post('/api/method/crm.api.mobile_sync.get_user_profile');
    return Map<String, dynamic>.from(res.data ?? {});
  }

  Future<Map<String, dynamic>> syncCallLogs(List<Map<String, dynamic>> logs) async {
    final res = await _dio.post(
      '/api/method/crm.api.mobile_sync.sync_call_logs',
      data: {
        'call_logs_data': logs,
      },
    );
    return Map<String, dynamic>.from(res.data ?? {});
  }

  Future<List<Map<String, dynamic>>> getUserCallLogs({int limit = 20, String? fromDate, String? toDate}) async {
    final data = <String, dynamic>{'limit': limit};
    if (fromDate != null) data['from_date'] = fromDate;
    if (toDate != null) data['to_date'] = toDate;
    final res = await _dio.post('/api/method/crm.api.mobile_sync.get_user_call_logs', data: data);
    final msg = res.data is Map ? (res.data['message'] ?? res.data) : res.data;
    if (msg is Map && (msg['success'] == true || msg['data'] != null)) {
      final list = (msg['data'] ?? msg['message'] ?? []) as List<dynamic>;
      return list.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    }
    return <Map<String, dynamic>>[];
  }

  Future<Map<String, dynamic>> getSyncStats() async {
    final res = await _dio.post('/api/method/crm.api.mobile_sync.get_sync_stats');
    final msg = res.data is Map ? (res.data['message'] ?? res.data) : res.data;
    return msg is Map<String, dynamic> ? msg : <String, dynamic>{};
  }
}
