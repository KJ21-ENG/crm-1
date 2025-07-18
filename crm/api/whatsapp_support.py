import frappe
import requests
import json
from frappe import _
from frappe.utils import now
from datetime import datetime


@frappe.whitelist()
def send_support_page_whatsapp(
    ticket_name,
    support_page_name, 
    customer_phone,
    custom_message=None,
    message=None
):
    """Send support page link via WhatsApp to customer"""
    
    # Validate inputs
    if not ticket_name or not support_page_name or not customer_phone:
        frappe.throw(_("Missing required parameters"))
    
    # Get ticket document
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    
    # Get support page document
    support_page = frappe.get_doc("CRM Support Pages", support_page_name)
    
    if not support_page.is_active:
        frappe.throw(_("Support page is not active"))
    
    # Clean phone number
    clean_phone = clean_phone_number(customer_phone)
    
    if not message:
        # Prepare WhatsApp message
        message = prepare_support_message(support_page, custom_message)
    
    try:
        # Send via WhatsApp Web.js service
        result = send_whatsapp_message_via_service(clean_phone, message)
        
        # Log the activity
        log_whatsapp_support_activity(
            ticket_name,
            support_page_name,
            customer_phone,
            message,
            "success"
        )
        
        # Create WhatsApp message record if the system supports it
        try:
            create_whatsapp_message_record(
                ticket, 
                support_page, 
                customer_phone, 
                message
            )
        except Exception as e:
            # Don't fail the main operation if message recording fails
            frappe.log_error(f"Failed to create WhatsApp message record: {str(e)}")
        
        return {
            "success": True,
            "message": _("Support page sent successfully via WhatsApp"),
            "whatsapp_result": result
        }
        
    except Exception as e:
        # Log failed activity
        log_whatsapp_support_activity(
            ticket_name,
            support_page_name, 
            customer_phone,
            message,
            "failed",
            str(e)
        )
        
        frappe.throw(_("Failed to send WhatsApp message: {0}").format(str(e)))


def clean_phone_number(phone):
    """Clean phone number for WhatsApp format"""
    if not phone:
        return None
    
    # Remove all non-digit characters
    clean = ''.join(filter(str.isdigit, str(phone)))
    
    # Add country code if not present (assuming +91 for India)
    if len(clean) == 10:
        clean = "91" + clean
    
    return clean


def prepare_support_message(support_page, custom_message=None):
    """Prepare the WhatsApp message with support page information"""
    message_parts = []
    
    if custom_message:
        message_parts.append(custom_message)
        message_parts.append("")  # Empty line
    
    message_parts.append(f"📋 *{support_page.page_name}*")
    
    if support_page.description:
        message_parts.append(support_page.description)
        message_parts.append("")  # Empty line
    
    message_parts.append(f"🔗 Link: {support_page.support_link}")
    
    return "\n".join(message_parts)


def send_whatsapp_message_via_service(phone, message):
    """Send message via WhatsApp Web.js service"""
    
    # WhatsApp service URL (configurable)
    service_url = frappe.conf.get("whatsapp_service_url", "http://localhost:3001")
    
    try:
        response = requests.post(
            f"{service_url}/send",
            json={
                "phoneNumber": phone,
                "message": message
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"WhatsApp service error: {response.status_code} - {response.text}"
            frappe.log_error(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to WhatsApp service: {str(e)}"
        frappe.log_error(error_msg)
        raise Exception(error_msg)


def log_whatsapp_support_activity(
    ticket_name, 
    support_page_name, 
    customer_phone, 
    message, 
    status, 
    error_message=None
):
    """Log WhatsApp support activity"""
    
    try:
        activity_data = {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "CRM Ticket",
            "reference_name": ticket_name,
            "content": prepare_activity_content(
                support_page_name, 
                customer_phone, 
                status, 
                error_message
            ),
            "comment_email": frappe.session.user,
            "creation": now(),
        }
        
        activity = frappe.get_doc(activity_data)
        activity.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Failed to log WhatsApp support activity: {str(e)}")


def prepare_activity_content(support_page_name, customer_phone, status, error_message=None):
    """Prepare activity content for logging"""
    
    if status == "success":
        content = [
            "📱 *WhatsApp Support Activity*",
            f"*Status*: ✅ Sent successfully",
            f"*Support Page*: {support_page_name}",
            f"*Customer Phone*: {customer_phone}",
            f"*Sent by*: {frappe.session.user}"
        ]
        return "\n".join(content)
    else:
        content = [
            "📱 *WhatsApp Support Activity*",
            f"*Status*: ❌ Failed to send",
            f"*Support Page*: {support_page_name}",
            f"*Customer Phone*: {customer_phone}",
            f"*Attempted by*: {frappe.session.user}"
        ]
        if error_message:
            content.append(f"*Error*: {error_message}")
        return "\n".join(content)


def create_whatsapp_message_record(ticket, support_page, customer_phone, message):
    """Create WhatsApp message record in the system if supported"""
    
    # Check if WhatsApp Message doctype exists
    if not frappe.db.exists("DocType", "WhatsApp Message"):
        return
    
    try:
        whatsapp_msg = frappe.get_doc({
            "doctype": "WhatsApp Message",
            "reference_doctype": "CRM Ticket", 
            "reference_name": ticket.name,
            "message": message,
            "to": customer_phone,
            "type": "Outgoing",
            "content_type": "text",
            "status": "Sent",
            "message_type": "Text"
        })
        
        whatsapp_msg.insert(ignore_permissions=True)
        
    except Exception as e:
        # Don't fail if this doesn't work
        pass


def get_whatsapp_service_url():
    """Get WhatsApp service URL from site config"""
    return frappe.conf.get('whatsapp_service_url', 'http://localhost:3001')

@frappe.whitelist()
def send_support_pages(doctype, docname, customer_mobile, support_pages, message):
    """Send multiple support pages to customer via WhatsApp"""
    try:
        # Validate inputs
        if not customer_mobile:
            return {"success": False, "message": "Customer mobile number is required"}
        
        if not support_pages:
            return {"success": False, "message": "At least one support page is required"}
        
        # Get support page details
        support_page_details = []
        for page_name in support_pages:
            page = frappe.get_doc('CRM Support Pages', page_name)
            if page.is_active:
                support_page_details.append({
                    'name': page.page_name,
                    'link': page.support_link,
                    'description': page.description
                })
        
        if not support_page_details:
            return {"success": False, "message": "No active support pages found"}
        
        # Send message via WhatsApp service
        service_url = get_whatsapp_service_url()
        response = requests.post(f"{service_url}/send-message", json={
            'to': customer_mobile,
            'message': message
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # Log activity
                frappe.get_doc({
                    'doctype': 'Comment',
                    'comment_type': 'Info',
                    'reference_doctype': doctype,
                    'reference_name': docname,
                    'content': f"📱 WhatsApp Support: Sent {len(support_page_details)} support page(s) to {customer_mobile}",
                    'comment_email': frappe.session.user,
                    'creation': now(),
                }).insert(ignore_permissions=True)
                
                return {"success": True, "message": "Support pages sent successfully"}
            else:
                return {"success": False, "message": result.get('message', 'Failed to send message')}
        else:
            return {"success": False, "message": "WhatsApp service unavailable"}
    
    except Exception as e:
        frappe.log_error(f"WhatsApp Support Error: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def send_support_pages_without_ticket(customer_mobile, support_pages, message=None):
    """Send multiple support pages to customer via WhatsApp without requiring a ticket"""
    try:
        # Validate inputs
        if not customer_mobile:
            return {"success": False, "message": "Customer mobile number is required"}
        
        if not support_pages:
            return {"success": False, "message": "At least one support page is required"}
        
        # Get support page details
        support_page_details = []
        for page_name in support_pages:
            page = frappe.get_doc('CRM Support Pages', page_name)
            if page.is_active:
                support_page_details.append({
                    'name': page.page_name,
                    'link': page.support_link,
                    'description': page.description
                })
        
        if not support_page_details:
            return {"success": False, "message": "No active support pages found"}
        
        # Generate message if not provided
        if not message:
            message = "Hi! Here are some helpful support pages:\n\n"
            for page in support_page_details:
                message += f"📋 *{page['name']}*\n"
                if page['description']:
                    message += f"{page['description']}\n"
                message += f"🔗 {page['link']}\n\n"
            message = message.strip()
        
        # Send message via WhatsApp service
        service_url = get_whatsapp_service_url()
        response = requests.post(f"{service_url}/send-message", json={
            'to': customer_mobile,
            'message': message
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {"success": True, "message": "Support pages sent successfully"}
            else:
                return {"success": False, "message": result.get('message', 'Failed to send message')}
        else:
            return {"success": False, "message": "WhatsApp service unavailable"}
    
    except Exception as e:
        frappe.log_error(f"WhatsApp Support Error: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_qr_code():
    """Get QR code for WhatsApp login"""
    try:
        service_url = get_whatsapp_service_url()
        response = requests.get(f"{service_url}/qr-code", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {"success": True, "qr_code": result.get('qr_code')}
            else:
                return {"success": False, "message": result.get('message', 'Failed to generate QR code')}
        else:
            return {"success": False, "message": "WhatsApp service unavailable"}
    
    except Exception as e:
        frappe.log_error(f"WhatsApp QR Code Error: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_status():
    """Get WhatsApp connection status"""
    try:
        service_url = get_whatsapp_service_url()
        response = requests.get(f"{service_url}/status", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "connected": result.get('connected', False),
                "phone_number": result.get('phone_number', None),
                "qr_code_available": result.get('qr_code_available', False),
                "is_initializing": result.get('is_initializing', False)
            }
        else:
            return {
                "connected": False, 
                "phone_number": None,
                "qr_code_available": False,
                "is_initializing": False
            }
    
    except Exception as e:
        frappe.log_error(f"WhatsApp Status Error: {str(e)}")
        return {
            "connected": False, 
            "phone_number": None,
            "qr_code_available": False,
            "is_initializing": False
        }

@frappe.whitelist()
def disconnect():
    """Disconnect WhatsApp"""
    try:
        service_url = get_whatsapp_service_url()
        response = requests.post(f"{service_url}/disconnect", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {"success": result.get('success', False), "message": result.get('message', '')}
        else:
            return {"success": False, "message": "WhatsApp service unavailable"}
    
    except Exception as e:
        frappe.log_error(f"WhatsApp Disconnect Error: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

@frappe.whitelist()
def get_usage_data():
    """Get WhatsApp support usage statistics"""
    try:
        # Get usage data from comments
        activities = frappe.get_all('Comment', 
            filters={
                'comment_type': 'Info',
                'content': ['like', '%WhatsApp Support%']
            },
            fields=['reference_doctype', 'reference_name', 'creation', 'content'],
            limit=100,
            order_by='creation desc'
        )
        
        usage_data = {
            'total_messages': len(activities),
            'recent_activities': activities[:10]
        }
        
        return usage_data
    
    except Exception as e:
        frappe.log_error(f"WhatsApp Usage Data Error: {str(e)}")
        return {'total_messages': 0, 'recent_activities': []}

@frappe.whitelist()
def is_whatsapp_support_enabled():
    """Check if WhatsApp Support feature is enabled"""
    # For our WhatsApp support feature, we just need to check if the service is available
    # This is independent of the WhatsApp Settings DocType
    return True 