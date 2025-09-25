import 'package:flutter/material.dart';
import 'lib/update_service.dart';
import 'lib/ui/update_dialog.dart';

/// Test script to verify the update system functionality
/// Run this in a Flutter test environment or as a standalone test

void main() {
  runApp(UpdateTestApp());
}

class UpdateTestApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Update System Test',
      home: UpdateTestPage(),
    );
  }
}

class UpdateTestPage extends StatefulWidget {
  @override
  _UpdateTestPageState createState() => _UpdateTestPageState();
}

class _UpdateTestPageState extends State<UpdateTestPage> {
  final UpdateService _updateService = UpdateService();
  String _status = 'Ready to test';
  UpdateInfo? _lastUpdateInfo;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Update System Test'),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Update System Test',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            
            // Status display
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Status: $_status',
                style: TextStyle(fontSize: 16),
              ),
            ),
            
            SizedBox(height: 20),
            
            // Test buttons
            ElevatedButton(
              onPressed: _testVersionCheck,
              child: Text('Test Version Check'),
            ),
            
            SizedBox(height: 10),
            
            ElevatedButton(
              onPressed: _testUpdateDialog,
              child: Text('Test Update Dialog'),
            ),
            
            SizedBox(height: 10),
            
            ElevatedButton(
              onPressed: _testDismissal,
              child: Text('Test Update Dismissal'),
            ),
            
            SizedBox(height: 10),
            
            ElevatedButton(
              onPressed: _clearDismissal,
              child: Text('Clear Dismissal'),
            ),
            
            SizedBox(height: 20),
            
            // Last update info
            if (_lastUpdateInfo != null) ...[
              Text(
                'Last Update Info:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 10),
              Container(
                width: double.infinity,
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Current: ${_lastUpdateInfo!.currentVersion} (${_lastUpdateInfo!.currentBuildNumber})'),
                    Text('Latest: ${_lastUpdateInfo!.latestVersion} (${_lastUpdateInfo!.latestBuildNumber})'),
                    Text('Force Update: ${_lastUpdateInfo!.isForceUpdate}'),
                    Text('File Size: ${_lastUpdateInfo!.fileSizeDisplay}'),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _testVersionCheck() async {
    setState(() {
      _status = 'Checking for updates...';
    });

    try {
      final updateInfo = await _updateService.checkForUpdates(silent: false);
      
      if (updateInfo != null) {
        setState(() {
          _status = 'Update available: ${updateInfo.versionDisplay}';
          _lastUpdateInfo = updateInfo;
        });
      } else {
        setState(() {
          _status = 'No updates available';
          _lastUpdateInfo = null;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Error: $e';
      });
    }
  }

  Future<void> _testUpdateDialog() async {
    if (_lastUpdateInfo == null) {
      setState(() {
        _status = 'No update info available. Run version check first.';
      });
      return;
    }

    showUpdateDialog(
      context,
      updateInfo: _lastUpdateInfo!,
      isForceUpdate: _lastUpdateInfo!.isForceUpdate,
    );
  }

  Future<void> _testDismissal() async {
    if (_lastUpdateInfo == null) {
      setState(() {
        _status = 'No update info available. Run version check first.';
      });
      return;
    }

    await _updateService.dismissUpdate(_lastUpdateInfo!.latestVersion);
    setState(() {
      _status = 'Update dismissed for version ${_lastUpdateInfo!.latestVersion}';
    });
  }

  Future<void> _clearDismissal() async {
    await _updateService.clearDismissedUpdate();
    setState(() {
      _status = 'Dismissal cleared';
    });
  }
}

/// Mock UpdateInfo for testing
class MockUpdateInfo extends UpdateInfo {
  MockUpdateInfo() : super(
    currentVersion: '1.0.0',
    currentBuildNumber: 1,
    latestVersion: '1.1.0',
    latestBuildNumber: 2,
    downloadUrl: 'https://example.com/app.apk',
    releaseNotes: 'Test update with new features',
    isForceUpdate: false,
    fileSize: 10240000,
  );
}
