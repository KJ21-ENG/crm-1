import frappe
from frappe import _
from frappe.utils import now, get_datetime, cstr, flt
import json
import time
from datetime import datetime, timedelta


@frappe.whitelist()
def sync_call_logs(call_logs_data):
    """
    Sync call logs from mobile app to CRM
    
    Args:
        call_logs_data: JSON string containing array of call log objects
        
    Returns:
        dict: Sync results with success/failure counts
    """
    try:
        # Parse call logs data
        if isinstance(call_logs_data, str):
            call_logs = json.loads(call_logs_data)
        else:
            call_logs = call_logs_data
            
        if not isinstance(call_logs, list):
            call_logs = [call_logs]
        
        frappe.logger().info(f"Mobile sync: Processing {len(call_logs)} call logs")
        
        results = {
            'success_count': 0,
            'failure_count': 0,
            'duplicate_count': 0,
            'errors': [],
            'processed_ids': []
        }
        
        for call_log_data in call_logs:
            try:
                result = process_single_call_log(call_log_data)
                if result['status'] == 'success':
                    results['success_count'] += 1
                    results['processed_ids'].append(result['name'])
                elif result['status'] == 'duplicate':
                    results['duplicate_count'] += 1
                    results['processed_ids'].append(result['name'])
                else:
                    results['failure_count'] += 1
                    results['errors'].append(result['error'])
                    
            except Exception as e:
                frappe.logger().error(f"Error processing call log: {e}")
                results['failure_count'] += 1
                results['errors'].append(str(e))
        
        # Commit the transaction
        frappe.db.commit()
        
        frappe.logger().info(f"Mobile sync completed: {results}")
        return {
            'success': True,
            'message': f"Synced {results['success_count']} call logs, {results['duplicate_count']} duplicates skipped",
            'data': results
        }
        
    except Exception as e:
        frappe.logger().error(f"Mobile sync failed: {e}")
        frappe.db.rollback()
        return {
            'success': False,
            'message': f"Sync failed: {str(e)}",
            'error': str(e)
        }


def process_single_call_log(call_log_data):
    """
    Process a single call log and create CRM Call Log document
    
    Args:
        call_log_data: Dictionary containing call log data
        
    Returns:
        dict: Processing result
    """
    try:
        # Validate required fields
        required_fields = ['from', 'to', 'type', 'start_time']
        for field in required_fields:
            if not call_log_data.get(field):
                return {
                    'status': 'error',
                    'error': f"Missing required field: {field}"
                }
        
        # Check for duplicates
        duplicate = check_duplicate_call_log(call_log_data)
        if duplicate:
            return {
                'status': 'duplicate',
                'name': duplicate,
                'message': 'Call log already exists'
            }
        
        # Prepare call log document
        call_log_doc = prepare_call_log_document(call_log_data)
        
        # Create the document
        doc = frappe.get_doc(call_log_doc)
        doc.insert()
        
        frappe.logger().info(f"Created call log: {doc.name}")
        
        return {
            'status': 'success',
            'name': doc.name,
            'message': 'Call log created successfully'
        }
        
    except Exception as e:
        frappe.logger().error(f"Error processing single call log: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def check_duplicate_call_log(call_log_data):
    """
    Check if a call log already exists to prevent duplicates
    
    Args:
        call_log_data: Call log data dictionary
        
    Returns:
        str: Name of existing call log document if duplicate, None otherwise
    """
    try:
        # Check by device call ID if available
        if call_log_data.get('device_call_id'):
            existing = frappe.db.get_value(
                'CRM Call Log',
                {'device_call_id': call_log_data['device_call_id']},
                'name'
            )
            if existing:
                return existing
        
        # Check by timestamp, phone numbers, and duration
        start_time = get_datetime(call_log_data['start_time'])
        
        # Search within 1 minute window to account for timing differences
        time_window = timedelta(minutes=1)
        start_range = start_time - time_window
        end_range = start_time + time_window
        
        filters = {
            'from': call_log_data['from'],
            'to': call_log_data['to'],
            'start_time': ['between', [start_range, end_range]]
        }
        
        # Add duration filter if available
        if call_log_data.get('duration'):
            filters['duration'] = call_log_data['duration']
        
        existing = frappe.db.get_value('CRM Call Log', filters, 'name')
        return existing
        
    except Exception as e:
        frappe.logger().error(f"Error checking duplicate call log: {e}")
        return None


def prepare_call_log_document(call_log_data):
    """
    Prepare call log document for creation
    
    Args:
        call_log_data: Raw call log data from mobile app
        
    Returns:
        dict: Formatted document ready for insertion
    """
    current_user = frappe.session.user
    
    # Convert phone numbers and handle user identification
    from_number = clean_phone_number(call_log_data['from'])
    to_number = clean_phone_number(call_log_data['to'])
    
    # Try to identify contacts/leads
    contact_info = identify_contact(from_number, to_number, call_log_data['type'])
    
    # Generate unique ID for the call log
    call_log_id = call_log_data.get('device_call_id') or f"mobile_{int(time.time() * 1000)}_{from_number}"
    
    # Map call type to valid options (only Incoming/Outgoing allowed)
    call_type = call_log_data['type']
    if call_type not in ['Incoming', 'Outgoing']:
        # Map other types to Incoming/Outgoing based on logic
        if call_type in ['Missed', 'Rejected', 'Blocked']:
            call_type = 'Incoming'
        else:
            call_type = 'Outgoing'
    
    # Map status to valid options
    status = call_log_data.get('status', 'Completed')
    valid_statuses = ['Initiated', 'Ringing', 'In Progress', 'Completed', 'Failed', 'Busy', 'No Answer', 'Queued', 'Canceled']
    if status not in valid_statuses:
        if status in ['Missed']:
            status = 'No Answer'
        elif status in ['Rejected']:
            status = 'Canceled'
        elif status in ['Blocked']:
            status = 'Failed'
        else:
            status = 'Completed'

    # Determine employee and customer based on call type
    employee = current_user  # The mobile app user is always the employee
    customer = None
    customer_name = None
    
    if call_type == 'Outgoing':
        # Employee made the call to customer
        customer = to_number
        # Legacy fields for backward compatibility
        caller = current_user
        receiver = None
    else:  # Incoming
        # Customer called employee
        customer = from_number
        # Legacy fields for backward compatibility
        caller = None
        receiver = current_user
    
    # Get customer name from contact/lead/customer info or generate default
    if contact_info and contact_info.get('contact_name'):
        customer_name = contact_info['contact_name']
    else:
        # Try to get customer name directly from CRM Customer table as fallback
        try:
            customer_record = search_crm_customer_by_phone(customer)
            if customer_record:
                customer_name = customer_record.get('customer_name') or customer_record.get('full_name')
                if not customer_name:
                    first_name = customer_record.get('first_name', '')
                    last_name = customer_record.get('last_name', '')
                    customer_name = f"{first_name} {last_name}".strip()
        except Exception as e:
            frappe.logger().error(f"Error getting customer name for {customer}: {e}")
        
        # If still no customer name, generate default
        if not customer_name:
            customer_name = f"Lead from call {customer}"

    doc_data = {
        'doctype': 'CRM Call Log',
        'id': call_log_id,
        'from': from_number,
        'to': to_number,
        'type': call_type,
        'status': status,
        'duration': flt(call_log_data.get('duration', 0)),
        'start_time': get_datetime(call_log_data['start_time']),
        'end_time': get_datetime(call_log_data.get('end_time', call_log_data['start_time'])),
        'telephony_medium': 'Manual',  # Indicates mobile app source
        'medium': 'Mobile App',
        'owner': current_user,
        
        # New employee/customer fields
        'employee': employee,
        'customer': customer,
        'customer_name': customer_name,
        
        # Legacy fields for backward compatibility during migration
        'caller': caller,
        'receiver': receiver,
    }
    
    # Add optional fields
    optional_fields = [
        'device_call_id', 'contact_name', 'recording_url',
        'reference_doctype', 'reference_docname'
    ]
    
    for field in optional_fields:
        if call_log_data.get(field):
            doc_data[field] = call_log_data[field]
    
    # Add contact/lead references if found
    if contact_info:
        # Don't overwrite if we already have reference info
        if not doc_data.get('reference_doctype'):
            doc_data.update(contact_info)
    
    return doc_data


def identify_contact(from_number, to_number, call_type):
    """
    Try to identify contact, lead, or CRM customer based on phone numbers
    
    Args:
        from_number: Caller number
        to_number: Receiver number
        call_type: Type of call (Incoming/Outgoing)
        
    Returns:
        dict: Contact/Lead/Customer information if found
    """
    try:
        # Determine which number to search for
        search_number = from_number if call_type == 'Incoming' else to_number
        
        # First, search in CRM Customer table (highest priority)
        customer = search_crm_customer_by_phone(search_number)
        if customer:
            return {
                'reference_doctype': 'CRM Customer',
                'reference_docname': customer['name'],
                'contact_name': customer.get('customer_name', ''),
            }
        
        # Search in contacts
        contact = search_contact_by_phone(search_number)
        if contact:
            return {
                'reference_doctype': 'Contact',
                'reference_docname': contact['name'],
                'contact_name': contact.get('first_name', '') + ' ' + contact.get('last_name', ''),
            }
        
        # Search in leads
        lead = search_lead_by_phone(search_number)
        if lead:
            return {
                'reference_doctype': 'Lead',
                'reference_docname': lead['name'],
                'contact_name': lead.get('lead_name', ''),
            }
        
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error identifying contact: {e}")
        return None


def search_contact_by_phone(phone_number):
    """Search for contact by phone number"""
    try:
        clean_phone = clean_phone_number(phone_number)
        
        # Search in multiple phone fields
        phone_fields = ['phone', 'mobile_no']
        
        for field in phone_fields:
            contact = frappe.db.get_value(
                'Contact',
                {field: ['like', f'%{clean_phone}%']},
                ['name', 'first_name', 'last_name', 'phone', 'mobile_no'],
                as_dict=True
            )
            if contact:
                return contact
        
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error searching contact: {e}")
        return None


def search_lead_by_phone(phone_number):
    """Search for lead by phone number"""
    try:
        clean_phone = clean_phone_number(phone_number)
        
        # Search in multiple phone fields
        phone_fields = ['phone', 'mobile_no']
        
        for field in phone_fields:
            lead = frappe.db.get_value(
                'Lead',
                {field: ['like', f'%{clean_phone}%']},
                ['name', 'lead_name', 'phone', 'mobile_no'],
                as_dict=True
            )
            if lead:
                return lead
        
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error searching lead: {e}")
        return None


def search_crm_customer_by_phone(phone_number):
    """Search for CRM customer by phone number"""
    try:
        clean_phone = clean_phone_number(phone_number)
        
        # Search in CRM Customer table by mobile_no field
        customer = frappe.db.get_value(
            'CRM Customer',
            {'mobile_no': phone_number},  # Exact match first
            ['name', 'customer_name', 'first_name', 'last_name', 'full_name', 'mobile_no'],
            as_dict=True
        )
        
        if customer:
            return customer
        
        # If not found, try with cleaned number
        if clean_phone != phone_number:
            customer = frappe.db.get_value(
                'CRM Customer',
                {'mobile_no': clean_phone},
                ['name', 'customer_name', 'first_name', 'last_name', 'full_name', 'mobile_no'],
                as_dict=True
            )
            if customer:
                return customer
        
        # Also search in phone field if it exists
        customer = frappe.db.get_value(
            'CRM Customer',
            {'phone': phone_number},
            ['name', 'customer_name', 'first_name', 'last_name', 'full_name', 'phone'],
            as_dict=True
        )
        
        if customer:
            return customer
        
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error searching CRM customer: {e}")
        return None


def clean_phone_number(phone_number):
    """Clean and normalize phone number"""
    if not phone_number:
        return ''
    
    # Remove common formatting characters
    clean = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Handle country codes (basic implementation)
    if clean.startswith('91') and len(clean) == 12:  # India
        return clean[2:]  # Remove country code
    elif clean.startswith('1') and len(clean) == 11:  # US/Canada
        return clean[1:]  # Remove country code
    
    return clean


@frappe.whitelist()
def get_user_call_logs(limit=50, from_date=None, to_date=None):
    """
    Get call logs for the current user
    
    Args:
        limit: Number of records to return
        from_date: Start date filter
        to_date: End date filter
        
    Returns:
        dict: Call logs data
    """
    try:
        current_user = frappe.session.user
        
        filters = {'owner': current_user}
        
        if from_date:
            filters['start_time'] = ['>=', get_datetime(from_date)]
        
        if to_date:
            if 'start_time' in filters:
                filters['start_time'] = ['between', [get_datetime(from_date), get_datetime(to_date)]]
            else:
                filters['start_time'] = ['<=', get_datetime(to_date)]
        
        fields = [
            'name', 'from', 'to', 'type', 'status', 'duration',
            'start_time', 'end_time', 'telephony_medium', 'medium',
            'employee', 'customer', 'customer_name',
            'caller', 'receiver', 'reference_doctype', 'reference_docname', 'creation'
        ]
        
        call_logs = frappe.get_list(
            'CRM Call Log',
            filters=filters,
            fields=fields,
            order_by='start_time desc',
            limit=limit
        )
        
        return {
            'success': True,
            'message': f'Retrieved {len(call_logs)} call logs',
            'data': call_logs
        }
        
    except Exception as e:
        frappe.logger().error(f"Error getting user call logs: {e}")
        return {
            'success': False,
            'message': f'Failed to get call logs: {str(e)}',
            'error': str(e)
        }


@frappe.whitelist()
def get_sync_stats():
    """
    Get sync statistics for the current user
    
    Returns:
        dict: Sync statistics
    """
    try:
        current_user = frappe.session.user
        
        # Total call logs
        total_logs = frappe.db.count('CRM Call Log', {'owner': current_user})
        
        # Mobile app logs (using telephony_medium = 'Manual' as indicator)
        mobile_logs = frappe.db.count('CRM Call Log', {
            'owner': current_user,
            'telephony_medium': 'Manual'
        })
        
        # Today's logs
        today = frappe.utils.today()
        today_logs = frappe.db.count('CRM Call Log', {
            'owner': current_user,
            'creation': ['>=', today]
        })
        
        # Last sync time (last mobile app call log)
        last_sync = frappe.db.get_value(
            'CRM Call Log',
            {
                'owner': current_user,
                'telephony_medium': 'Manual'
            },
            'creation',
            order_by='creation desc'
        )
        
        return {
            'success': True,
            'data': {
                'total_call_logs': total_logs,
                'mobile_synced_logs': mobile_logs,
                'today_logs': today_logs,
                'last_sync_time': last_sync,
                'sync_percentage': round((mobile_logs / total_logs * 100) if total_logs > 0 else 0, 2)
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"Error getting sync stats: {e}")
        return {
            'success': False,
            'message': f'Failed to get sync stats: {str(e)}',
            'error': str(e)
        }


@frappe.whitelist()
def test_mobile_sync():
    """
    Test endpoint for mobile sync functionality
    
    Returns:
        dict: Test results
    """
    try:
        current_user = frappe.session.user
        
        # Sample call log for testing
        test_call_log = {
            'from': '1234567890',
            'to': '0987654321',
            'type': 'Outgoing',
            'status': 'Completed',
            'duration': 120,
            'start_time': now(),
            'end_time': now(),
            'device_call_id': f'test_{int(time.time() * 1000)}'
        }
        
        # Test sync
        result = process_single_call_log(test_call_log)
        
        return {
            'success': True,
            'message': 'Mobile sync test completed successfully',
            'test_result': result,
            'user': current_user,
            'timestamp': now()
        }
        
    except Exception as e:
        frappe.logger().error(f"Mobile sync test failed: {e}")
        return {
            'success': False,
            'message': f'Mobile sync test failed: {str(e)}',
            'error': str(e)
        }


@frappe.whitelist()
def get_user_profile():
    """
    Get current user's profile information including mobile number
    
    Returns:
        dict: User profile data
    """
    try:
        current_user = frappe.session.user
        
        # Get user info
        user_doc = frappe.get_doc('User', current_user)
        
        # Try to get mobile number from CRM Telephony Agent
        mobile_no = None
        if frappe.db.exists('CRM Telephony Agent', current_user):
            telephony_agent = frappe.get_doc('CRM Telephony Agent', current_user)
            mobile_no = telephony_agent.mobile_no
        
        # Fallback to user's mobile_no field
        if not mobile_no:
            mobile_no = user_doc.mobile_no
        
        # Default phone number if none found
        if not mobile_no:
            mobile_no = '+911234567890'  # Default placeholder
        
        return {
            'success': True,
            'data': {
                'user': current_user,
                'full_name': user_doc.full_name,
                'mobile_no': mobile_no,
                'email': user_doc.email,
                'first_name': user_doc.first_name,
                'last_name': user_doc.last_name,
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"Error getting user profile: {e}")
        return {
            'success': False,
            'message': f'Failed to get user profile: {str(e)}',
            'error': str(e)
        } 