import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:android_intent_plus/android_intent.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';

class UpdateService {
  static final UpdateService _instance = UpdateService._internal();
  factory UpdateService() => _instance;
  UpdateService._internal();

  final Dio _dio = Dio();
  bool _isChecking = false;
  bool _isDownloading = false;
  double _downloadProgress = 0.0;

  // Getters for UI state
  bool get isChecking => _isChecking;
  bool get isDownloading => _isDownloading;
  double get downloadProgress => _downloadProgress;

  /// Check for app updates
  Future<UpdateInfo?> checkForUpdates({bool silent = false}) async {
    if (_isChecking) return null;
    
    _isChecking = true;
    
    try {
      // Get current app version
      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;
      final currentBuildNumber = int.tryParse(packageInfo.buildNumber) ?? 0;
      
      // Get server version info
      final response = await _dio.get(
        '${ApiService.instance.baseUrl}/api/method/crm.api.app_update.get_app_version',
        options: Options(
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'EshinApp/${currentVersion}',
          },
        ),
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data;
        final serverVersion = data['version'] as String?;
        final serverBuildNumber = data['build_number'] as int?;
        final downloadUrl = data['download_url'] as String?;
        final releaseNotes = data['release_notes'] as String?;
        final isForceUpdate = data['force_update'] as bool? ?? false;
        final minSupportedVersion = data['min_supported_version'] as String?;

        if (serverVersion != null && downloadUrl != null) {
          // Compare versions
          final needsUpdate = _compareVersions(
            currentVersion, 
            currentBuildNumber,
            serverVersion, 
            serverBuildNumber ?? 0,
          );

          if (needsUpdate) {
            // Check if this is a forced update
            final isForced = isForceUpdate || 
                (minSupportedVersion != null && 
                 _compareVersions(currentVersion, currentBuildNumber, minSupportedVersion, 0));

            return UpdateInfo(
              currentVersion: currentVersion,
              currentBuildNumber: currentBuildNumber,
              latestVersion: serverVersion,
              latestBuildNumber: serverBuildNumber ?? 0,
              downloadUrl: downloadUrl,
              releaseNotes: releaseNotes ?? 'Bug fixes and improvements',
              isForceUpdate: isForced,
              fileSize: data['file_size'] as int?,
            );
          }
        }
      }
    } catch (e) {
      if (!silent) {
        debugPrint('Update check failed: $e');
      }
    } finally {
      _isChecking = false;
    }
    
    return null;
  }

  /// Compare version strings and build numbers
  bool _compareVersions(String currentVersion, int currentBuild, String serverVersion, int serverBuild) {
    // First compare build numbers (more reliable)
    if (serverBuild > currentBuild) return true;
    if (serverBuild < currentBuild) return false;
    
    // If build numbers are equal, compare version strings
    final currentParts = currentVersion.split('.').map(int.tryParse).toList();
    final serverParts = serverVersion.split('.').map(int.tryParse).toList();
    
    // Pad with zeros to make same length
    while (currentParts.length < serverParts.length) currentParts.add(0);
    while (serverParts.length < currentParts.length) serverParts.add(0);
    
    for (int i = 0; i < currentParts.length; i++) {
      final current = currentParts[i] ?? 0;
      final server = serverParts[i] ?? 0;
      
      if (server > current) return true;
      if (server < current) return false;
    }
    
    return false;
  }

  /// Download and install update
  Future<bool> downloadAndInstallUpdate(UpdateInfo updateInfo, {
    required Function(double) onProgress,
    required Function(String) onError,
  }) async {
    if (_isDownloading) return false;
    
    _isDownloading = true;
    _downloadProgress = 0.0;
    
    try {
      // Request storage permission
      if (Platform.isAndroid) {
        final status = await Permission.storage.request();
        if (!status.isGranted) {
          onError('Storage permission required to download update');
          return false;
        }
      }

      // Get download directory
      final directory = await getExternalStorageDirectory() ?? await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/Eshin_Update_${updateInfo.latestVersion}.apk');

      // Download file
      await _dio.download(
        updateInfo.downloadUrl,
        file.path,
        onReceiveProgress: (received, total) {
          if (total != -1) {
            _downloadProgress = received / total;
            onProgress(_downloadProgress);
          }
        },
        options: Options(
          headers: {
            'Accept': 'application/vnd.android.package-archive, */*',
            'User-Agent': 'EshinApp/${updateInfo.currentVersion}',
          },
        ),
      );

      // Verify file was downloaded
      if (!await file.exists()) {
        onError('Download failed - file not found');
        return false;
      }

      // Install APK
      await _installApk(file.path);
      
      // Save update info
      await _saveUpdateInfo(updateInfo);
      
      return true;
    } catch (e) {
      onError('Download failed: ${e.toString()}');
      return false;
    } finally {
      _isDownloading = false;
      _downloadProgress = 0.0;
    }
  }

  /// Install APK file
  Future<void> _installApk(String apkPath) async {
    if (Platform.isAndroid) {
      // For Android 8.0+ (API 26+), we need to request INSTALL_PACKAGES permission
      final deviceInfo = DeviceInfoPlugin();
      final androidInfo = await deviceInfo.androidInfo;
      
      if (androidInfo.version.sdkInt >= 26) {
        // Request install permission
        final intent = AndroidIntent(
          action: 'android.settings.MANAGE_UNKNOWN_APP_SOURCES',
          data: 'package:com.eshin.crm',
        );
        await intent.launch();
      }

      // Install the APK
      final installIntent = AndroidIntent(
        action: 'android.intent.action.VIEW',
        data: 'file://$apkPath',
        type: 'application/vnd.android.package-archive',
        flags: <int>[
          0x10000000, // FLAG_ACTIVITY_NEW_TASK
          0x00000001, // FLAG_GRANT_READ_URI_PERMISSION
        ],
      );
      
      await installIntent.launch();
    }
  }

  /// Save update information to preferences
  Future<void> _saveUpdateInfo(UpdateInfo updateInfo) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('last_update_version', updateInfo.latestVersion);
    await prefs.setInt('last_update_build', updateInfo.latestBuildNumber);
    await prefs.setString('last_update_time', DateTime.now().toIso8601String());
  }

  /// Get last update information
  Future<Map<String, dynamic>?> getLastUpdateInfo() async {
    final prefs = await SharedPreferences.getInstance();
    final version = prefs.getString('last_update_version');
    final build = prefs.getInt('last_update_build');
    final time = prefs.getString('last_update_time');
    
    if (version != null && build != null && time != null) {
      return {
        'version': version,
        'build': build,
        'time': time,
      };
    }
    
    return null;
  }

  /// Check if user has dismissed update
  Future<bool> hasUserDismissedUpdate(String version) async {
    final prefs = await SharedPreferences.getInstance();
    final dismissedVersion = prefs.getString('dismissed_update_version');
    return dismissedVersion == version;
  }

  /// Mark update as dismissed
  Future<void> dismissUpdate(String version) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('dismissed_update_version', version);
  }

  /// Clear dismissed update (for testing)
  Future<void> clearDismissedUpdate() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('dismissed_update_version');
  }
}

/// Update information model
class UpdateInfo {
  final String currentVersion;
  final int currentBuildNumber;
  final String latestVersion;
  final int latestBuildNumber;
  final String downloadUrl;
  final String releaseNotes;
  final bool isForceUpdate;
  final int? fileSize;

  UpdateInfo({
    required this.currentVersion,
    required this.currentBuildNumber,
    required this.latestVersion,
    required this.latestBuildNumber,
    required this.downloadUrl,
    required this.releaseNotes,
    required this.isForceUpdate,
    this.fileSize,
  });

  String get versionDisplay => '$latestVersion ($latestBuildNumber)';
  String get fileSizeDisplay {
    if (fileSize == null) return 'Unknown size';
    final sizeInMB = fileSize! / (1024 * 1024);
    return '${sizeInMB.toStringAsFixed(1)} MB';
  }
}
