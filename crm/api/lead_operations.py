import frappe
from frappe import _

@frappe.whitelist()
def save_client_id_without_validation(lead_name, client_id):
    """
    Save client_id to lead document without triggering full validation
    This is used when the lead has missing required fields but we need to save client_id
    """
    try:
        # Use direct SQL to avoid validation
        frappe.db.set_value(
            'CRM Lead',
            lead_name,
            'client_id',
            client_id,
            update_modified=False
        )
        
        # Commit the transaction
        frappe.db.commit()
        
        return {
            'success': True,
            'message': 'Client ID saved successfully'
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error saving client_id for lead {lead_name}: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to save Client ID: {str(e)}'
        }

@frappe.whitelist()
def update_customer_with_client_id(customer_name, client_id, accounts_json):
    """
    Update customer with referral_code and accounts in a single operation
    Note: client_id field in customer table is NOT updated
    """
    try:
        # Update only referral_code and accounts fields
        frappe.db.set_value(
            'CRM Customer',
            customer_name,
            {
                'referral_code': client_id,  # Store Client ID as referral_code
                'accounts': accounts_json
            },
            update_modified=False
        )
        
        # Commit the transaction
        frappe.db.commit()
        
        return {
            'success': True,
            'message': 'Customer updated successfully with Client ID'
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error updating customer {customer_name}: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to update customer: {str(e)}'
        }

@frappe.whitelist()
def update_lead_status_with_client_id(lead_name, new_status, client_id=None):
    """
    Update lead status and optionally save client_id in a single operation
    This handles the case where client_id needs to be saved before status change
    """
    try:
        # First save client_id if provided
        if client_id:
            frappe.db.set_value(
                'CRM Lead',
                lead_name,
                'client_id',
                client_id,
                update_modified=False
            )
        
        # Then update status
        frappe.db.set_value(
            'CRM Lead',
            lead_name,
            'status',
            new_status,
            update_modified=False
        )
        
        # Commit the transaction
        frappe.db.commit()
        
        return {
            'success': True,
            'message': f'Lead status updated to {new_status} successfully'
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error updating lead {lead_name}: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to update lead: {str(e)}'
        }

@frappe.whitelist()
def validate_lead_for_status_change(lead_name, target_status):
    """
    Validate if a lead can be moved to the target status
    Returns validation errors if any
    """
    try:
        lead = frappe.get_doc('CRM Lead', lead_name)
        errors = []
        
        # Check if status requires client_id
        if target_status in ['Account Opened', 'Account Activated']:
            if not lead.client_id:
                errors.append('Client ID is required for this status')
        
        # Check for other required fields based on status
        if target_status in ['Account Opened', 'Account Activated']:
            if not lead.first_name:
                errors.append('First Name is required for account operations')
            if not lead.mobile_no:
                errors.append('Mobile Number is required for account operations')
            if not lead.account_type:
                errors.append('Account Type is required for account operations')
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'can_proceed': len(errors) == 0
        }
        
    except Exception as e:
        frappe.log_error(f"Error validating lead {lead_name}: {str(e)}")
        return {
            'success': False,
            'errors': [f'Validation error: {str(e)}'],
            'can_proceed': False
        } 