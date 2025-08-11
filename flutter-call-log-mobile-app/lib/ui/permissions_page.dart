import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:android_intent_plus/android_intent.dart';

class PermissionsPage extends StatelessWidget {
  const PermissionsPage({super.key});

  Future<void> _openBatteryOptimization() async {
    const intent = AndroidIntent(
      action: 'android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS',
      data: 'package:com.example.flutter_call_log_mobile_app',
    );
    await intent.launch();
  }

  @override
  Widget build(BuildContext context) {
    final items = <_PermItem>[
      _PermItem(
        title: 'Phone (Call Logs)',
        description: 'Allow reading call logs to sync with CRM.',
        request: () async {
          final status = await Permission.phone.status;
          if (!status.isGranted) {
            final res = await Permission.phone.request();
            if (!res.isGranted) {
              await openAppSettings();
            }
          } else {
            await openAppSettings();
          }
        },
      ),
      _PermItem(
        title: 'Notifications',
        description: 'Allow notifications for background sync status.',
        request: () async {
          final status = await Permission.notification.status;
          if (!status.isGranted) {
            final res = await Permission.notification.request();
            if (!res.isGranted) {
              await openAppSettings();
            }
          } else {
            await openAppSettings();
          }
        },
      ),
      _PermItem(
        title: 'Battery Optimization',
        description: 'Exclude app from battery optimization for reliable background sync.',
        request: _openBatteryOptimization,
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Request Permissions')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (ctx, i) {
          final it = items[i];
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
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.security, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(it.title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      const SizedBox(height: 6),
                      Text(it.description, style: const TextStyle(color: Color(0xFF6B7280))),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                FilledButton(
                  onPressed: it.request,
                  child: const Text('Open'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _PermItem {
  final String title;
  final String description;
  final Future<void> Function() request;
  _PermItem({required this.title, required this.description, required this.request});
}




