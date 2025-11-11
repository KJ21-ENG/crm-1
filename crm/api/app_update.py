import os
import json
import frappe
from frappe import _
from frappe.utils import get_site_path

@frappe.whitelist(allow_guest=True)
def get_app_version():
    """Get current app version information for update checking.
    
    Returns:
        dict: Version information including latest version, download URL, etc.
    """
    try:
        # Get app version from pubspec.yaml
        bench_root = os.path.abspath(os.path.join(get_site_path(), '..', '..'))
        pubspec_path = os.path.join(
            bench_root,
            'apps', 'crm', 'flutter-call-log-mobile-app',
            'pubspec.yaml'
        )
        
        current_version = "1.1.0"
        current_build = 3
        
        if os.path.exists(pubspec_path):
            with open(pubspec_path, 'r') as f:
                content = f.read()
                # Extract version from pubspec.yaml
                import re
                version_match = re.search(r'version:\s*([0-9.]+)\+([0-9]+)', content)
                if version_match:
                    current_version = version_match.group(1)
                    current_build = int(version_match.group(2))
        
        # Get latest APK info
        apk_dir = os.path.join(
            bench_root,
            'apps', 'crm', 'flutter-call-log-mobile-app',
            'build', 'app', 'outputs', 'flutter-apk'
        )
        
        # Check for APK files
        apk_files = []
        if os.path.isdir(apk_dir):
            for file in os.listdir(apk_dir):
                if file.endswith('.apk'):
                    file_path = os.path.join(apk_dir, file)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        apk_files.append({
                            'name': file,
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        })
        
        # Sort by modification time (newest first)
        apk_files.sort(key=lambda x: x['modified'], reverse=True)
        
        # Get the latest APK
        latest_apk = apk_files[0] if apk_files else None
        
        # Build download URL
        download_url = None
        if latest_apk:
            # Use the existing download endpoint
            download_url = f"{frappe.utils.get_url()}/api/method/crm.api.whatsapp_setup.download_eshen_app_apk"
        
        # Get release notes from a file or database
        release_notes = _get_release_notes(current_version)
        
        # Check if this is a force update (you can customize this logic)
        is_force_update = _should_force_update(current_version, current_build)
        
        # Minimum supported version
        min_supported_version = "1.0.0"
        
        return {
            'success': True,
            'current_version': current_version,
            'current_build': current_build,
            'version': current_version,  # Latest version (same as current for now)
            'build_number': current_build,
            'download_url': download_url,
            'release_notes': release_notes,
            'force_update': is_force_update,
            'min_supported_version': min_supported_version,
            'file_size': latest_apk['size'] if latest_apk else None,
            'last_updated': latest_apk['modified'] if latest_apk else None,
        }
        
    except Exception as e:
        frappe.log_error(f"App version check failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': _('Failed to get app version information')
        }

def _get_release_notes(version):
    """Get release notes for the given version."""
    # You can store release notes in a DocType or file
    # For now, return a default message
    release_notes_map = {
        "1.1.0": """
• Improved call log synchronization
• Enhanced background sync reliability
• Better error handling and user feedback
• Performance optimizations
• Bug fixes and stability improvements
        """.strip(),
        "1.0.0": """
• Initial release
• Call log synchronization
• Background sync support
• User authentication
        """.strip(),
    }
    
    return release_notes_map.get(version, "Bug fixes and improvements")

def _should_force_update(current_version, current_build):
    """Determine if update should be forced."""
    # Example logic: force update if version is below 1.1.0
    try:
        version_parts = current_version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        
        # Force update if major version is 0 or minor is below 1
        return major < 1 or (major == 1 and minor < 1)
    except:
        return False

@frappe.whitelist(allow_guest=True)
def get_update_settings():
    """Get update settings and configuration."""
    try:
        # You can store these settings in a DocType or Site Config
        return {
            'success': True,
            'auto_check_enabled': True,
            'check_interval_hours': 24,
            'force_update_threshold_days': 30,
            'update_server_url': frappe.utils.get_url(),
        }
    except Exception as e:
        frappe.log_error(f"Update settings failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@frappe.whitelist(allow_guest=True)
def log_update_check(version, build_number, user_agent=None):
    """Log update check for analytics."""
    try:
        # You can create a DocType to track update checks
        # For now, just log it
        frappe.logger().info(f"Update check: version={version}, build={build_number}, user_agent={user_agent}")
        
        return {'success': True}
    except Exception as e:
        frappe.log_error(f"Update check logging failed: {str(e)}")
        return {'success': False, 'error': str(e)}
