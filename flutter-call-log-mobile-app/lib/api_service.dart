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
  String? lastLoginDebug;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _baseUrl = prefs.getString('server_url') ?? _baseUrl;
    _sessionId = await _secure.read(key: 'session_id');
    _dio.options.baseUrl = _baseUrl;
    _dio.options.headers['Accept'] = 'application/json, text/plain, */*';
    _dio.options.headers['X-Requested-With'] = 'XMLHttpRequest';
    _dio.options.headers['User-Agent'] =
        'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 EshinApp/1.0';
    _dio.options.headers['Referer'] = _baseUrl;
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
          // Consider 3xx/4xx as responses we can parse
          validateStatus: (s) => (s ?? 0) < 500,
          headers: {
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            // Prevent gzip issues on some proxies
            'Accept-Encoding': 'identity',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 EshinApp/1.0',
            'Referer': _baseUrl,
          },
        ),
      );

      // Robust cookie extraction when multiple Set-Cookie headers are present
      final Map<String, List<String>> hmap = res.headers.map;
      final List<String> cookies = [];
      for (final entry in hmap.entries) {
        if (entry.key.toLowerCase() == 'set-cookie') {
          cookies.addAll(entry.value);
        }
      }
      String? sid;
      for (final c in cookies) {
        final m = RegExp(r'(^|[;\s])sid=([^;]+)').firstMatch(c);
        if (m != null) {
          sid = m.group(2);
          break;
        }
      }

      if (sid != null && sid!.isNotEmpty) {
        await setSessionId(sid);
        lastLoginDebug = 'OK: sid captured; status=' + (res.statusCode?.toString() ?? '');
        return true;
      }

      // Fallback: some servers return JSON message on success; verify session explicitly
      final ok = await isAuthenticated();
      if (ok) {
        // Try to grab sid from any Set-Cookie in current cookie jar if present
        try {
          final resp = await _dio.get('/api/method/frappe.auth.get_logged_user');
          final v = _dio.options.headers['Cookie']?.toString() ?? '';
          if (!v.contains('sid=')) {
            // attempt from collected cookies
            for (final c in cookies) {
              final m = RegExp(r'(^|[;\s])sid=([^;]+)').firstMatch(c);
              final s = m?.group(2);
              if (s != null && s.isNotEmpty) { await setSessionId(s); break; }
            }
          }
        } catch (_) {}
        lastLoginDebug = 'OK: session validated; status=' + (res.statusCode?.toString() ?? '');
        return true;
      }
      final hasSetCookie = cookies.isNotEmpty;
      String? location;
      for (final entry in res.headers.map.entries) {
        if (entry.key.toLowerCase() == 'location' && entry.value.isNotEmpty) {
          location = entry.value.first;
          break;
        }
      }
      final body = res.data;
      String bodySnippet;
      if (body is String) {
        bodySnippet = body.length > 200 ? body.substring(0, 200) + '…' : body;
      } else if (body is Map) {
        bodySnippet = body.toString();
      } else {
        bodySnippet = (body ?? '').toString();
      }
      lastLoginDebug = 'FAIL status=' + (res.statusCode?.toString() ?? '') + '; set-cookie=' + hasSetCookie.toString() + '; location=' + (location ?? '-') + '; baseUrl=' + _baseUrl + '; body=' + bodySnippet;
      return false;
    } catch (e) {
      lastLoginDebug = 'EXCEPTION: ' + e.runtimeType.toString() + ': ' + e.toString();
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
      final res = await _dio.get('/api/method/frappe.auth.get_logged_user', options: Options(validateStatus: (s) => (s ?? 0) < 500));
      final data = res.data;
      if (data is Map && (data['message'] != null || data['full_name'] != null)) return true;
      // Some setups return plain string
      if (data is String && data.isNotEmpty && data != 'Guest') return true;
      return false;
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

  Future<List<Map<String, dynamic>>> getUserCallLogs({int limit = 20, int offset = 0, String? fromDate, String? toDate}) async {
    final data = <String, dynamic>{'limit': limit, 'offset': offset};
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
