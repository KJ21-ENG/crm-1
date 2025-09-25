# Eshin CRM App - In-App Update System

## Overview

This document explains the in-app update system implemented for the Eshin CRM Flutter app. The system allows users to receive updates directly within the app without going through app stores, since the app is distributed via direct APK downloads from `eshin.in`.

## Features

- ✅ **Automatic Update Checking**: Checks for updates when the app starts
- ✅ **Manual Update Check**: Users can manually check for updates via menu
- ✅ **Force Update Support**: Critical updates can be forced
- ✅ **Download Progress**: Shows download progress with visual indicators
- ✅ **Release Notes**: Displays what's new in each update
- ✅ **Dismissible Updates**: Users can dismiss non-critical updates
- ✅ **Error Handling**: Comprehensive error handling and user feedback
- ✅ **Permission Management**: Handles Android installation permissions

## How It Works

### 1. Version Checking
- App checks server for latest version on startup (after authentication)
- Compares current app version with server version
- Uses both version string and build number for accurate comparison

### 2. Update Flow
1. **Check**: App queries `/api/method/crm.api.app_update.get_app_version`
2. **Compare**: Compares versions using semantic versioning
3. **Notify**: Shows update dialog if newer version available
4. **Download**: Downloads APK from server
5. **Install**: Triggers Android package installer

### 3. User Experience
- **Silent Check**: Automatic checking in background
- **Update Dialog**: Beautiful, informative update dialog
- **Progress Tracking**: Real-time download progress
- **Error Recovery**: Clear error messages and retry options

## Implementation Details

### Backend API (`apps/crm/crm/api/app_update.py`)

```python
@frappe.whitelist(allow_guest=True)
def get_app_version():
    """Returns current app version information"""
    return {
        'version': '1.1.0',
        'build_number': 3,
        'download_url': 'https://eshin.in/api/method/crm.api.whatsapp_setup.download_eshen_app_apk',
        'release_notes': 'Bug fixes and improvements',
        'force_update': False,
        'min_supported_version': '1.0.0',
        'file_size': 12345678,
    }
```

### Flutter Service (`lib/update_service.dart`)

Key methods:
- `checkForUpdates()`: Checks server for updates
- `downloadAndInstallUpdate()`: Downloads and installs APK
- `hasUserDismissedUpdate()`: Checks if user dismissed this version
- `dismissUpdate()`: Marks version as dismissed

### UI Components (`lib/ui/update_dialog.dart`)

- `UpdateDialog`: Main update dialog widget
- `showUpdateDialog()`: Helper function to show dialog
- `showUpdateAvailableSnackbar()`: Shows update notification

## Configuration

### Version Management

1. **Update Version**: Modify `pubspec.yaml`:
   ```yaml
   version: 1.2.0+4  # version+build_number
   ```

2. **Build APK**: 
   ```bash
   cd apps/crm/flutter-call-log-mobile-app
   flutter build apk --release
   ```

3. **Server Detection**: The API automatically detects the latest APK from the build directory

### Force Update Configuration

In `apps/crm/crm/api/app_update.py`, modify `_should_force_update()`:

```python
def _should_force_update(current_version, current_build):
    """Force update if version is below 1.1.0"""
    try:
        version_parts = current_version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        
        # Force update if major version is 0 or minor is below 1
        return major < 1 or (major == 1 and minor < 1)
    except:
        return False
```

### Release Notes

Add release notes in `_get_release_notes()`:

```python
release_notes_map = {
    "1.2.0": """
• New feature: Enhanced call logging
• Improved sync performance
• Bug fixes and stability improvements
    """.strip(),
    "1.1.0": """
• Improved call log synchronization
• Enhanced background sync reliability
• Better error handling and user feedback
    """.strip(),
}
```

## User Experience Flow

### Automatic Update Check
1. User opens app
2. App authenticates with server
3. App silently checks for updates
4. If update available and not dismissed, shows update dialog

### Manual Update Check
1. User taps menu (⋮) in home screen
2. Selects "Check for Updates"
3. App shows loading indicator
4. Shows update dialog or "latest version" message

### Update Installation
1. User taps "Update Now" in dialog
2. App requests storage permissions
3. Downloads APK with progress indicator
4. Triggers Android package installer
5. User completes installation manually

## Permissions Required

### Android Manifest (`android/app/src/main/AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />
<uses-permission android:name="android.permission.MANAGE_UNKNOWN_APP_SOURCES" />
```

### Runtime Permissions
- Storage permission for downloading APK
- Install packages permission for Android 8.0+
- Unknown sources permission for sideloading

## Testing the Update System

### 1. Simulate Update Available
1. Change version in `pubspec.yaml` to a higher number
2. Build new APK: `flutter build apk --release`
3. Change version back to original
4. Run app - it should detect the "newer" version

### 2. Test Force Update
1. Modify `_should_force_update()` to return `True`
2. Run app - update dialog should not be dismissible

### 3. Test Dismissal
1. Show update dialog
2. Tap "Later" - dialog should close
3. Restart app - dialog should not appear again

## Troubleshooting

### Common Issues

1. **Update Check Fails**
   - Check network connectivity
   - Verify API endpoint is accessible
   - Check server logs for errors

2. **Download Fails**
   - Check storage permissions
   - Verify APK file exists on server
   - Check available storage space

3. **Installation Fails**
   - Check "Install from unknown sources" setting
   - Verify APK file integrity
   - Check Android version compatibility

### Debug Information

Enable debug logging in `UpdateService`:

```dart
debugPrint('Update check: version=$currentVersion, build=$currentBuildNumber');
debugPrint('Server response: $response.data');
```

## Security Considerations

1. **APK Verification**: Consider adding APK signature verification
2. **HTTPS Only**: Ensure all downloads use HTTPS
3. **File Integrity**: Verify downloaded APK checksums
4. **Permission Scope**: Request minimal required permissions

## Future Enhancements

1. **Delta Updates**: Download only changed parts
2. **Background Downloads**: Download updates in background
3. **Scheduled Updates**: Install updates at optimal times
4. **Rollback Support**: Ability to rollback to previous version
5. **Update Analytics**: Track update adoption rates

## Deployment Checklist

Before deploying updates:

- [ ] Update version in `pubspec.yaml`
- [ ] Add release notes
- [ ] Build release APK
- [ ] Test update flow
- [ ] Verify API endpoint
- [ ] Check permissions
- [ ] Test on different Android versions
- [ ] Document changes

## Support

For issues with the update system:
1. Check server logs: `tail -f sites/crm.localhost/logs/web.error.log`
2. Check app logs: Android Studio Logcat
3. Verify API response: Test endpoint manually
4. Check permissions: Android Settings > Apps > Eshin > Permissions
