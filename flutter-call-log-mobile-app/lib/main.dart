import 'package:flutter/material.dart';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:android_intent_plus/android_intent.dart';

import 'background_task.dart';
import 'call_log_sync_service.dart';
import 'api_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // TRY THIS: Try running your application with "flutter run". You'll see
        // the application has a purple toolbar. Then, without quitting the app,
        // try changing the seedColor in the colorScheme below to Colors.green
        // and then invoke "hot reload" (save your changes or press the "hot
        // reload" button in a Flutter-supported IDE, or press "r" if you used
        // the command line to start the app).
        //
        // Notice that the counter didn't reset back to zero; the application
        // state is not lost during the reload. To reset the state, use hot
        // restart instead.
        //
        // This works for code too, not just values: Most code changes can be
        // tested with just a hot reload.
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _lastSync = 'Never';
  int _pending = 0;
  bool _serviceRunning = false;
  List<Map<String, dynamic>> _recent = [];
  int _lastSyncedCount = 0;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await ApiService.instance.init();
    final prefs = await SharedPreferences.getInstance();
    final ts = prefs.getInt('last_call_log_sync');
    setState(() {
      _lastSync = ts != null ? DateTime.fromMillisecondsSinceEpoch(ts).toIso8601String() : 'Never';
    });
    _serviceRunning = await FlutterForegroundTask.isRunningService;
    await _loadRecent();
    setState(() {});
  }

  Future<void> _loadRecent() async {
    try {
      final list = await ApiService.instance.getUserCallLogs(limit: 20);
      setState(() { _recent = list; });
    } catch (_) {}
  }

  Future<void> _requestPermissions() async {
    await Permission.notification.request();
    await Permission.phone.request();
    final status = await Permission.phone.status;
    if (!status.isGranted) {
      openAppSettings();
    }
  }

  Future<void> _requestIgnoreBatteryOptimizations() async {
    const intent = AndroidIntent(
      action: 'android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS',
      data: 'package:com.example.flutter_call_log_mobile_app',
    );
    await intent.launch();
  }

  Future<void> _startForeground() async {
    FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        channelId: 'crm_sync',
        channelName: 'CRM Sync',
        channelDescription: 'Syncs call logs every 60s',
        channelImportance: NotificationChannelImportance.HIGH,
        priority: NotificationPriority.HIGH,
        iconData: const NotificationIconData(
          resType: ResourceType.mipmap,
          resPrefix: ResourcePrefix.ic,
          name: 'launcher',
        ),
        buttons: const [NotificationButton(id: 'stop', text: 'Stop')],
        // foregroundServiceType only in newer package versions; omit for 6.x
      ),
      iosNotificationOptions: IOSNotificationOptions(showNotification: false),
      foregroundTaskOptions: const ForegroundTaskOptions(
        interval: 1000,
        autoRunOnBoot: false,
        allowWakeLock: true,
      ),
    );
    await FlutterForegroundTask.startService(
      notificationTitle: 'CRM Call Logs Sync',
      notificationText: 'Next sync in 60s',
      callback: startCallback,
    );
    _serviceRunning = true;
    setState(() {});
  }

  Future<void> _stopForeground() async {
    await FlutterForegroundTask.stopService();
    _serviceRunning = false;
    setState(() {});
  }

  Future<void> _manualSync() async {
    final res = await CallLogSyncService.instance.syncOnce();
    final prefs = await SharedPreferences.getInstance();
    final ts = prefs.getInt('last_call_log_sync');
    final sc = prefs.getInt('last_sync_success_count') ?? 0;
    final fc = prefs.getInt('last_sync_failure_count') ?? 0;
    final dc = prefs.getInt('last_sync_duplicate_count') ?? 0;
    setState(() {
      _lastSync = ts != null ? DateTime.fromMillisecondsSinceEpoch(ts).toIso8601String() : 'Never';
      _pending = (res['failure_count'] as int?) ?? 0;
      _lastSyncedCount = sc;
    });
    await _loadRecent();
    if (!(res['success'] == true)) {
      final msg = (res['error'] ?? res['message'] ?? 'Unknown error').toString();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Sync failed: $msg')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Quick settings row for URL and SID
            Row(children: [
              ElevatedButton(
                onPressed: () async {
                  final controller = TextEditingController(text: 'https://eshin.in');
                  await showDialog(context: context, builder: (_) => AlertDialog(
                    title: const Text('Set Server URL'),
                    content: TextField(controller: controller, decoration: const InputDecoration(hintText: 'https://eshin.in')),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                      TextButton(onPressed: () async { await ApiService.instance.saveBaseUrl(controller.text.trim()); if (context.mounted) Navigator.pop(context); }, child: const Text('Save'))
                    ],
                  ));
                },
                child: const Text('Server URL'),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: () async {
                  final controller = TextEditingController();
                  await showDialog(context: context, builder: (_) => AlertDialog(
                    title: const Text('Set Session ID (sid)'),
                    content: TextField(controller: controller, decoration: const InputDecoration(hintText: 'sid=...')),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                      TextButton(onPressed: () async { await ApiService.instance.setSessionId(controller.text.trim()); if (context.mounted) Navigator.pop(context); }, child: const Text('Save'))
                    ],
                  ));
                },
                child: const Text('Set SID'),
              )
            ]),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () async {
                final userCtrl = TextEditingController();
                final passCtrl = TextEditingController();
                final ok = await showDialog<bool>(context: context, builder: (_) => AlertDialog(
                  title: const Text('CRM Login'),
                  content: Column(mainAxisSize: MainAxisSize.min, children: [
                    TextField(controller: userCtrl, decoration: const InputDecoration(labelText: 'Username / Email')),
                    TextField(controller: passCtrl, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
                  ]),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                    TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Login')),
                  ],
                ));
                if (ok == true) {
                  final success = await ApiService.instance.login(userCtrl.text.trim(), passCtrl.text);
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(success ? 'Login successful' : 'Login failed')));
                  }
                }
              },
              child: const Text('Login (auto sid)'),
            ),
            const SizedBox(height: 12),
            Text('Last Sync: $_lastSync'),
            const SizedBox(height: 8),
            Row(children: [
              _StatCard(title: 'Synced', value: '$_lastSyncedCount', color: const Color(0xFF10B981)),
              const SizedBox(width: 12),
              _StatCard(title: 'Pending', value: '$_pending'),
            ]),
            const SizedBox(height: 16),
            Wrap(spacing: 8, runSpacing: 8, children: [
              ElevatedButton(onPressed: _requestPermissions, child: const Text('Request Permissions')),
              ElevatedButton(onPressed: _requestIgnoreBatteryOptimizations, child: const Text('Battery Optimization')),
              ElevatedButton(onPressed: _manualSync, child: const Text('Manual Sync')),
              _serviceRunning
                  ? ElevatedButton(onPressed: _stopForeground, child: const Text('Stop Foreground'))
                  : ElevatedButton(onPressed: _startForeground, child: const Text('Start Foreground')),
            ])
            , const SizedBox(height: 20),
            const Text('Recent Call Logs', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _recent.isEmpty
              ? const Text('No logs yet')
              : Expanded(
                  child: ListView.builder(
                    itemCount: _recent.length,
                    itemBuilder: (ctx, i) {
                      final it = _recent[i];
                      final from = (it['from'] ?? '').toString();
                      final to = (it['to'] ?? '').toString();
                      final type = (it['type'] ?? '').toString();
                      final status = (it['status'] ?? '').toString();
                      final duration = (it['duration'] ?? 0).toString();
                      final start = (it['start_time'] ?? '').toString();
                      Color chipBg = const Color(0xFFE5E7EB); Color chipFg = const Color(0xFF374151);
                      switch (type.toLowerCase()) {
                        case 'incoming': chipBg = const Color(0xFFD1FAE5); chipFg = const Color(0xFF065F46); break;
                        case 'outgoing': chipBg = const Color(0xFFDBEAFE); chipFg = const Color(0xFF1E40AF); break;
                        case 'missed': chipBg = const Color(0xFFFEE2E2); chipFg = const Color(0xFF991B1B); break;
                      }
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), boxShadow: const [BoxShadow(color: Color(0x1A000000), blurRadius: 4, offset: Offset(0,2))]),
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                            Expanded(child: Text('$from → $to', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600))),
                            Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: chipBg, borderRadius: BorderRadius.circular(6)), child: Text(type.toUpperCase(), style: TextStyle(color: chipFg, fontWeight: FontWeight.w600)))
                          ]),
                          const SizedBox(height: 6),
                          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                            Text(start.isNotEmpty ? start : '—', style: const TextStyle(color: Color(0xFF6B7280))),
                            Text('Duration: ${duration}s', style: const TextStyle(color: Color(0xFF6B7280)))
                          ]),
                          const SizedBox(height: 4),
                          Text('Status: ${status.isNotEmpty ? status : '—'}', style: const TextStyle(fontSize: 12))
                        ]),
                      );
                    },
                  ),
                )
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;
  const _StatCard({super.key, required this.title, required this.value, this.color = const Color(0xFF3B82F6)});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: const [BoxShadow(color: Color(0x14000000), blurRadius: 6, offset: Offset(0, 2))],
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(value, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: color)),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(color: Color(0xFF6B7280))),
        ]),
      ),
    );
  }
}
