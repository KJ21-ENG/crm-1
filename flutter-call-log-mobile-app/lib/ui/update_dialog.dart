import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../update_service.dart';

class UpdateDialog extends StatefulWidget {
  final UpdateInfo updateInfo;
  final VoidCallback? onDismiss;
  final bool isForceUpdate;

  const UpdateDialog({
    super.key,
    required this.updateInfo,
    this.onDismiss,
    this.isForceUpdate = false,
  });

  @override
  State<UpdateDialog> createState() => _UpdateDialogState();
}

class _UpdateDialogState extends State<UpdateDialog> {
  final UpdateService _updateService = UpdateService();
  bool _isDownloading = false;
  double _downloadProgress = 0.0;
  String? _errorMessage;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return WillPopScope(
      onWillPop: () async => !widget.isForceUpdate,
      child: Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: colorScheme.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.system_update,
                      color: colorScheme.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.isForceUpdate ? 'Update Required' : 'Update Available',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Version ${widget.updateInfo.versionDisplay}',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: colorScheme.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (!widget.isForceUpdate)
                    IconButton(
                      onPressed: () {
                        _updateService.dismissUpdate(widget.updateInfo.latestVersion);
                        Navigator.of(context).pop();
                        widget.onDismiss?.call();
                      },
                      icon: const Icon(Icons.close),
                    ),
                ],
              ),

              const SizedBox(height: 20),

              // Current version info
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceVariant.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      size: 16,
                      color: colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Current: ${widget.updateInfo.currentVersion} (${widget.updateInfo.currentBuildNumber})',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Release notes
              if (widget.updateInfo.releaseNotes.isNotEmpty) ...[
                Text(
                  'What\'s New',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceVariant.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    widget.updateInfo.releaseNotes,
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // File size info
              if (widget.updateInfo.fileSize != null) ...[
                Row(
                  children: [
                    Icon(
                      Icons.storage,
                      size: 16,
                      color: colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Download size: ${widget.updateInfo.fileSizeDisplay}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
              ],

              // Download progress
              if (_isDownloading) ...[
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Downloading update...',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(
                      value: _downloadProgress,
                      backgroundColor: colorScheme.surfaceVariant,
                      valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${(_downloadProgress * 100).toStringAsFixed(1)}%',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
              ],

              // Error message
              if (_errorMessage != null) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: colorScheme.errorContainer.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: colorScheme.error.withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: colorScheme.error,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.error,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Action buttons
              Row(
                children: [
                  if (!widget.isForceUpdate) ...[
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _isDownloading ? null : () {
                          _updateService.dismissUpdate(widget.updateInfo.latestVersion);
                          Navigator.of(context).pop();
                          widget.onDismiss?.call();
                        },
                        child: const Text('Later'),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _isDownloading ? null : _startUpdate,
                      child: _isDownloading
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Update Now'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _startUpdate() async {
    setState(() {
      _isDownloading = true;
      _errorMessage = null;
    });

    try {
      final success = await _updateService.downloadAndInstallUpdate(
        widget.updateInfo,
        onProgress: (progress) {
          setState(() {
            _downloadProgress = progress;
          });
        },
        onError: (error) {
          setState(() {
            _errorMessage = error;
            _isDownloading = false;
          });
        },
      );

      if (success && mounted) {
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Update downloaded successfully! Please install the APK.'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Close dialog
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Update failed: ${e.toString()}';
        _isDownloading = false;
      });
    }
  }
}

/// Show update dialog
Future<void> showUpdateDialog(
  BuildContext context, {
  required UpdateInfo updateInfo,
  bool isForceUpdate = false,
  VoidCallback? onDismiss,
}) async {
  return showDialog<void>(
    context: context,
    barrierDismissible: !isForceUpdate,
    builder: (context) => UpdateDialog(
      updateInfo: updateInfo,
      isForceUpdate: isForceUpdate,
      onDismiss: onDismiss,
    ),
  );
}

/// Show update available snackbar
void showUpdateAvailableSnackbar(
  BuildContext context, {
  required UpdateInfo updateInfo,
  VoidCallback? onTap,
}) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.system_update, color: Colors.white),
          const SizedBox(width: 8),
          Expanded(
            child: Text('Update available: ${updateInfo.versionDisplay}'),
          ),
        ],
      ),
      action: SnackBarAction(
        label: 'Update',
        onPressed: onTap ?? () {
          showUpdateDialog(context, updateInfo: updateInfo);
        },
      ),
      duration: const Duration(seconds: 5),
    ),
  );
}
