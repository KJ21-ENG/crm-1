import 'package:flutter/material.dart';
import 'dart:async';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:android_intent_plus/android_intent.dart';
import 'package:intl/intl.dart';
import 'package:flutter/rendering.dart';

import '../api_service.dart';
import '../call_log_sync_service.dart';
import '../background_task.dart';
import 'login_page.dart';
import 'permissions_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String _lastSync = 'Never';
  String _lastSyncLabel = 'Never';
  int _syncedCount = 0;
  int _pendingCount = 0;
  bool _serviceRunning = false;
  List<Map<String, dynamic>> _recent = [];
  bool _loading = true;
  Timer? _ticker;
  final ScrollController _scrollController = ScrollController();
  bool _isUserScrolling = false;
  Timer? _scrollIdleDebounce;

  @override
  void initState() {
    super.initState();
    _init();
  }

  String _formatRelative(int? ts) {
    if (ts == null) return 'Never';
    final dt = DateTime.fromMillisecondsSinceEpoch(ts);
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inSeconds < 60) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }

  Future<void> _init() async {
    await ApiService.instance.init();
    await _ensureCriticalPermissions();
    await _refreshStats();
    await _loadRecent();
    _serviceRunning = await FlutterForegroundTask.isRunningService;
    if (mounted) setState(() => _loading = false);
    // periodic real-time refresh
    _ticker = Timer.periodic(const Duration(seconds: 10), (_) async {
      await _refreshStats();
      await _loadRecent();
    });
  }

  Future<void> _refreshStats() async {
    final prefs = await SharedPreferences.getInstance();
    int? localTs = prefs.getInt('last_call_log_sync');
    try {
      // Prefer server stats so auto-sync is reflected
      final server = await ApiService.instance.getSyncStats();
      final data = (server['data'] ?? server['message'] ?? {}) as Map?;
      if (data != null) {
        final todayLogs = data['today_logs'] as int?;
        final lastSyncStr = data['last_sync_time']?.toString();
        DateTime? lastDt;
        if (lastSyncStr != null && lastSyncStr.isNotEmpty) {
          lastDt = DateTime.tryParse(lastSyncStr);
        }
        setState(() {
          _syncedCount = todayLogs ?? _syncedCount;
          if (lastDt != null) {
            _lastSync = lastDt.toIso8601String();
            _lastSyncLabel = _formatRelative(lastDt.millisecondsSinceEpoch);
          } else {
            // fallback to local preference timestamp
            _lastSync = localTs != null
                ? DateTime.fromMillisecondsSinceEpoch(localTs).toIso8601String()
                : 'Never';
            _lastSyncLabel = _formatRelative(localTs);
          }
        });
      }
    } catch (_) {
      // fallback to local
      setState(() {
        _lastSync = localTs != null
            ? DateTime.fromMillisecondsSinceEpoch(localTs).toIso8601String()
            : 'Never';
        _lastSyncLabel = _formatRelative(localTs);
      });
    }
  }

  Future<void> _ensureCriticalPermissions() async {
    // Phone permission (call logs)
    final phoneStatus = await Permission.phone.status;
    if (!phoneStatus.isGranted) {
      await Permission.phone.request();
    }
    // Notifications (Android 13+)
    final noti = await Permission.notification.status;
    if (!noti.isGranted) {
      await Permission.notification.request();
    }
  }

  @override
  void dispose() {
    _ticker?.cancel();
    _scrollIdleDebounce?.cancel();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadRecent() async {
    try {
      final list = await ApiService.instance.getUserCallLogs(limit: 30);
      if (mounted) setState(() => _recent = list);
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
  
  static int _asInt(dynamic v) {
    if (v is int) return v;
    if (v is double) return v.toInt();
    if (v is String) return int.tryParse(v) ?? 0;
    return 0;
  }

  static String _formatDuration(int seconds) {
    final d = Duration(seconds: seconds);
    final mm = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final ss = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    final hh = d.inHours;
    if (hh > 0) {
      return '${hh}h ${mm}m ${ss}s';
    }
    if (d.inMinutes > 0) {
      return '${d.inMinutes}m ${ss}s';
    }
    return '${d.inSeconds}s';
  }

  static String _formatListDate(String raw) {
    if (raw.isEmpty) return '—';
    // Try robust parsing and convert to 12-hour format with AM/PM
    DateTime? dt = DateTime.tryParse(raw);
    dt ??= DateTime.tryParse(raw.replaceFirst(' ', 'T'));
    if (dt != null) {
      return DateFormat('yyyy-MM-dd hh:mm:ss a').format(dt);
    }
    // Fallback: normalize then convert hour part manually
    final normalized = raw.replaceFirst('T', ' ').split('.').first;
    final parts = normalized.split(' ');
    if (parts.length == 2) {
      final date = parts[0];
      final timeParts = parts[1].split(':');
      if (timeParts.length >= 2) {
        final h = int.tryParse(timeParts[0]) ?? 0;
        final m = timeParts[1];
        final s = timeParts.length > 2 ? timeParts[2] : '00';
        final isPm = h >= 12;
        final hh = (h % 12 == 0) ? 12 : h % 12;
        final hhStr = hh.toString().padLeft(2, '0');
        return '$date $hhStr:$m:$s ${isPm ? 'PM' : 'AM'}';
      }
    }
    return normalized;
  }

  Future<void> _startForeground() async {
    // Ensure notification permission (Android 13+)
    final notifStatus = await Permission.notification.status;
    if (!notifStatus.isGranted) {
      final granted = await Permission.notification.request();
      if (!granted.isGranted) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Enable notifications to show background sync indicator.')),
          );
        }
        return;
      }
    }

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
    _serviceRunning = await FlutterForegroundTask.isRunningService;
    setState(() {});
  }

  Future<void> _stopForeground() async {
    await FlutterForegroundTask.stopService();
    _serviceRunning = false;
    setState(() {});
  }

  Future<void> _manualSync() async {
    final res = await CallLogSyncService.instance.syncOnce();
    await _refreshStats();
    await _loadRecent();
    if (!(res['success'] == true)) {
      final msg = (res['error'] ?? res['message'] ?? 'Unknown error').toString();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Sync failed: $msg')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      floatingActionButton: _loading
          ? null
          : FloatingActionButton.extended(
              onPressed: _manualSync,
              icon: const Icon(Icons.sync),
              label: const Text('Sync Now'),
            ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () async {
                await _refreshStats();
                await _loadRecent();
              },
              child: NotificationListener<UserScrollNotification>(
                onNotification: (n) {
                  if (n.direction == ScrollDirection.idle) {
                    _scrollIdleDebounce?.cancel();
                    _scrollIdleDebounce = Timer(const Duration(milliseconds: 250), () {
                      _isUserScrolling = false;
                    });
                  } else {
                    _isUserScrolling = true;
                  }
                  return false;
                },
                child: CustomScrollView(
                  controller: _scrollController,
                  cacheExtent: 800,
                  physics: const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
                  slivers: [
                  SliverAppBar(
                    pinned: true,
                    expandedHeight: 140,
                    actions: [
                      PopupMenuButton<String>(
                        icon: const Icon(Icons.menu),
                        onSelected: (value) async {
                          switch (value) {
                            case 'permissions':
                              if (!mounted) return;
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => const PermissionsPage()),
                              );
                              break;
                            case 'logout':
                              final confirm = await showDialog<bool>(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: const Text('Logout'),
                                  content: const Text('Are you sure you want to logout?'),
                                  actions: [
                                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                                    TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Logout')),
                                  ],
                                ),
                              );
                              if (confirm != true) return;
                              try { await FlutterForegroundTask.stopService(); } catch (_) {}
                              await ApiService.instance.logout();
                              if (!mounted) return;
                              Navigator.of(context).pushAndRemoveUntil(
                                MaterialPageRoute(
                                  builder: (_) => LoginPage(
                                    onLoggedIn: () {
                                      Navigator.of(_).pushAndRemoveUntil(
                                        MaterialPageRoute(builder: (_) => const HomePage()),
                                        (route) => false,
                                      );
                                    },
                                  ),
                                ),
                                (route) => false,
                              );
                              break;
                          }
                        },
                        itemBuilder: (ctx) => const [
                          PopupMenuItem(value: 'permissions', child: Text('Request Permissions')),
                          PopupMenuItem(value: 'logout', child: Text('Logout')),
                        ],
                      ),
                    ],
                    flexibleSpace: FlexibleSpaceBar(
                      titlePadding: const EdgeInsetsDirectional.only(start: 16, bottom: 16),
                      title: Text(
                        'Eshin',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      background: Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [cs.primary, cs.primary.withOpacity(0.6)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SliverToBoxAdapter(child: SizedBox(height: 12)),
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: _OverviewRow(
                    lastSync: _lastSyncLabel,
                    syncedCount: _syncedCount,
                  ),
                    ),
                  ),
                  const SliverToBoxAdapter(child: SizedBox(height: 16)),
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: _BackgroundControl(
                        running: _serviceRunning,
                        onToggle: (value) async {
                          if (value) {
                            await _startForeground();
                          } else {
                            await _stopForeground();
                          }
                        },
                      ),
                    ),
                  ),
                  const SliverToBoxAdapter(child: SizedBox(height: 20)),
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: const Text(
                        'Recent Call Logs',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SliverToBoxAdapter(child: SizedBox(height: 8)),
                  if (_recent.isEmpty)
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            boxShadow: const [
                              BoxShadow(color: Color(0x14000000), blurRadius: 6, offset: Offset(0, 2)),
                            ],
                          ),
                          child: Row(
                            children: const [
                              Icon(Icons.history, color: Color(0xFF6B7280)),
                              SizedBox(width: 12),
                              Expanded(child: Text('No logs yet')),
                            ],
                          ),
                        ),
                      ),
                    )
                  else
                    SliverList.builder(
                      itemCount: _recent.length,
                      itemBuilder: (ctx, i) => Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: _CallLogTile(item: _recent[i]),
                      ),
                    ),
                  const SliverToBoxAdapter(child: SizedBox(height: 80)),
                  ],
                ),
              ),
            ),
    );
  }
}

class _OverviewRow extends StatelessWidget {
  final String lastSync;
  final int syncedCount;
  const _OverviewRow({
    required this.lastSync,
    required this.syncedCount,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: _StatCard(title: 'Last Sync', value: lastSync, icon: Icons.history)),
        const SizedBox(width: 12),
        Expanded(child: _StatCard(title: 'Synced (Today)', value: '$syncedCount', icon: Icons.cloud_done_outlined)),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData? icon;
  const _StatCard({required this.title, required this.value, this.icon});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(color: Color(0x14000000), blurRadius: 8, offset: Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (icon != null)
            Container(
              width: 36,
              height: 36,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: cs.primary.withOpacity(0.08),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: cs.primary),
            ),
          const SizedBox(height: 8),
          Text(
            value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: cs.primary),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(color: Color(0xFF6B7280)),
          ),
        ],
      ),
    );
  }
}

class _BackgroundControl extends StatelessWidget {
  final bool running;
  final ValueChanged<bool> onToggle;
  const _BackgroundControl({required this.running, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Color(0x14000000), blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          Icon(running ? Icons.play_circle_fill : Icons.pause_circle_filled, color: cs.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Background Sync', style: TextStyle(fontWeight: FontWeight.w700)),
                Text(
                  running ? 'Running in background' : 'Stopped',
                  style: const TextStyle(color: Color(0xFF6B7280)),
                ),
              ],
            ),
          ),
          Switch.adaptive(value: running, onChanged: onToggle),
        ],
      ),
    );
  }
}

class _CallLogTile extends StatelessWidget {
  final Map<String, dynamic> item;
  const _CallLogTile({required this.item});

  @override
  Widget build(BuildContext context) {
    final from = (item['from'] ?? '').toString();
    final to = (item['to'] ?? '').toString();
    final type = (item['type'] ?? '').toString();
    final status = (item['status'] ?? '').toString();
    final durationSec = _HomePageState._asInt(item['duration']);
    final durationText = _HomePageState._formatDuration(durationSec);
    final startRaw = (item['start_time'] ?? '').toString();
    final startText = _HomePageState._formatListDate(startRaw);

    Color chipBg = const Color(0xFFE5E7EB);
    Color chipFg = const Color(0xFF374151);
    switch (type.toLowerCase()) {
      case 'incoming':
        chipBg = const Color(0xFFD1FAE5);
        chipFg = const Color(0xFF065F46);
        break;
      case 'outgoing':
        chipBg = const Color(0xFFDBEAFE);
        chipFg = const Color(0xFF1E40AF);
        break;
      case 'missed':
        chipBg = const Color(0xFFFEE2E2);
        chipFg = const Color(0xFF991B1B);
        break;
    }

    return RepaintBoundary(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {},
        child: Container(
          margin: const EdgeInsets.only(bottom: 10),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: const [
              BoxShadow(color: Color(0x1A000000), blurRadius: 4, offset: Offset(0, 2)),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Builder(
                      builder: (context) {
                        final tl = type.toLowerCase();
                        final showNumber = tl == 'outgoing' ? to : from; // incoming/missed -> from, outgoing -> to
                        return Text(
                          showNumber,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                        );
                      },
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: chipBg,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      type.toUpperCase(),
                      style: TextStyle(color: chipFg, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(startText, style: const TextStyle(color: Color(0xFF6B7280))),
                  Text('Duration: $durationText', style: const TextStyle(color: Color(0xFF6B7280))),
                ],
              ),
              const SizedBox(height: 4),
              Text('Status: ${status.isNotEmpty ? status : '—'}', style: const TextStyle(fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}


