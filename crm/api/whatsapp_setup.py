import frappe
import os
import zipfile
import tempfile
import requests
import json
from frappe import _
from frappe.utils import get_site_path


@frappe.whitelist()
def download_extension():
    """Download Chrome extension as a zip file"""
    try:
        # Get the extension directory path - use bench root
        bench_root = os.path.abspath(os.path.join(get_site_path(), '..', '..'))
        extension_dir = os.path.join(bench_root, 'apps', 'crm', 'whatsapp-extension')
        
        if not os.path.exists(extension_dir):
            frappe.throw(_("Extension directory not found"))
        
        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip_path = temp_zip.name
        
        # Create zip file
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Files to include in the extension
            extension_files = [
                'manifest.json',
                'background.js',
                'content.js',
                'popup.html',
                'popup.js',
                'README.md'
            ]
            
            # Add files to zip
            for file_name in extension_files:
                file_path = os.path.join(extension_dir, file_name)
                if os.path.exists(file_path):
                    zipf.write(file_path, file_name)
            
            # Add icons directory if it exists
            icons_dir = os.path.join(extension_dir, 'icons')
            if os.path.exists(icons_dir):
                for root, dirs, files in os.walk(icons_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, extension_dir)
                        zipf.write(file_path, arc_name)
        
        # Read the zip file
        with open(temp_zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Clean up temporary file
        os.unlink(temp_zip_path)
        
        # Set response headers for file download
        frappe.response.filename = 'crm-whatsapp-extension.zip'
        frappe.response.filecontent = zip_content
        frappe.response.type = 'download'
        
        return {
            'success': True,
            'message': _('Extension downloaded successfully')
        }
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Extension Download Error: {str(e)}")
        frappe.throw(_("Failed to download extension: {0}").format(str(e)))


@frappe.whitelist()
def get_local_whatsapp_status():
    """Get WhatsApp status from local service"""
    try:
        response = requests.get('http://localhost:3001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            whatsapp_status = data.get('whatsappStatus', 'disconnected')
            return {
                'connected': whatsapp_status == 'connected',
                'phone_number': data.get('phoneNumber', None),
                'qr_code_available': whatsapp_status == 'qr_ready',
                'is_initializing': whatsapp_status == 'initializing',
                'status': whatsapp_status
            }
        else:
            return {
                'connected': False,
                'phone_number': None,
                'qr_code_available': False,
                'is_initializing': False,
                'status': 'service_unavailable'
            }
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"WhatsApp Local Service Error: {str(e)}")
        return {
            'connected': False,
            'phone_number': None,
            'qr_code_available': False,
            'is_initializing': False,
            'status': 'service_error',
            'error': str(e)
        }


@frappe.whitelist()
def get_local_whatsapp_qr():
    """Get QR code from local service"""
    try:
        response = requests.get('http://localhost:3001/qr-code', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('qrCode'):
                # Convert base64 back to data URL
                qr_data_url = f"data:image/png;base64,{data['qrCode']}"
                return {
                    'success': True,
                    'qr_code': qr_data_url
                }
            else:
                return {
                    'success': False,
                    'message': data.get('error', 'QR code not available')
                }
        else:
            return {
                'success': False,
                'message': 'Service unavailable'
            }
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"WhatsApp QR Code Error: {str(e)}")
        return {
            'success': False,
            'message': f'Service error: {str(e)}'
        }


@frappe.whitelist()
def send_local_whatsapp_message():
    """Send WhatsApp message via local service"""
    try:
        # Get parameters from request
        params = frappe.form_dict
        
        message_data = {
            'phone': params.get('to'),
            'message': params.get('message')
        }
        
        response = requests.post('http://localhost:3001/send-message', 
                               json=message_data, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    'success': True,
                    'message': 'Message sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Failed to send message')
                }
        else:
            return {
                'success': False,
                'message': 'Service unavailable'
            }
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"WhatsApp Send Message Error: {str(e)}")
        return {
            'success': False,
            'message': f'Service error: {str(e)}'
        }


@frappe.whitelist()
def disconnect_local_whatsapp():
    """Disconnect WhatsApp via local service"""
    try:
        response = requests.post('http://localhost:3001/disconnect', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'message': 'WhatsApp disconnected successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to disconnect'
            }
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"WhatsApp Disconnect Error: {str(e)}")
        return {
            'success': False,
            'message': f'Service error: {str(e)}'
        }


@frappe.whitelist()
def get_extension_info():
    """Get information about the Chrome extension"""
    try:
        # Get the extension directory path - use bench root
        bench_root = os.path.abspath(os.path.join(get_site_path(), '..', '..'))
        extension_dir = os.path.join(bench_root, 'apps', 'crm', 'whatsapp-extension')
        
        info = {
            'exists': os.path.exists(extension_dir),
            'version': '1.0.0',
            'name': 'CRM WhatsApp Extension',
            'description': 'Chrome extension for multi-user WhatsApp integration'
        }
        
        if info['exists']:
            # Check if required files exist
            required_files = ['manifest.json', 'background.js', 'content.js']
            missing_files = []
            
            for file_name in required_files:
                file_path = os.path.join(extension_dir, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            info['missing_files'] = missing_files
            info['ready'] = len(missing_files) == 0
        
        return info
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Extension Info Error: {str(e)}")
        return {
            'exists': False,
            'error': str(e)
        }


@frappe.whitelist()
def get_local_service_info():
    """Get information about the local WhatsApp service"""
    try:
        # Get the service directory path - use bench root
        bench_root = os.path.abspath(os.path.join(get_site_path(), '..', '..'))
        service_dir = os.path.join(bench_root, 'apps', 'crm', 'local-whatsapp-service')
        
        info = {
            'exists': os.path.exists(service_dir),
            'name': 'CRM Local WhatsApp Service',
            'description': 'Local Node.js service for WhatsApp integration'
        }
        
        if info['exists']:
            # Check if required files exist
            required_files = ['local-service.js', 'package.json', 'install.sh']
            missing_files = []
            
            for file_name in required_files:
                file_path = os.path.join(service_dir, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            info['missing_files'] = missing_files
            info['ready'] = len(missing_files) == 0
            
            # Check package.json for version info
            package_json_path = os.path.join(service_dir, 'package.json')
            if os.path.exists(package_json_path):
                try:
                    import json
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                        info['version'] = package_data.get('version', '1.0.0')
                        info['description'] = package_data.get('description', info['description'])
                except:
                    pass
        
        return info
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Local Service Info Error: {str(e)}")
        return {
            'exists': False,
            'error': str(e)
        }


@frappe.whitelist()
def get_setup_status():
    """Get overall setup status for WhatsApp integration"""
    try:
        extension_info = get_extension_info()
        service_info = get_local_service_info()
        
        status = {
            'extension': extension_info,
            'service': service_info,
            'overall_ready': extension_info.get('ready', False) and service_info.get('ready', False)
        }
        
        return status
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Setup Status Error: {str(e)}")
        return {
            'error': str(e),
            'overall_ready': False
        } 