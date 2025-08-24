import frappe
from frappe import _
from frappe.utils import escape_html, nowdate

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

        # If the lead is already in 'Account Opened' status, ensure account_open_date is set
        try:
            status = frappe.db.get_value('CRM Lead', lead_name, 'status')
            if status == 'Account Opened':
                current_acc_date = frappe.db.get_value('CRM Lead', lead_name, 'account_open_date')
                if not current_acc_date:
                    frappe.db.set_value(
                        'CRM Lead', lead_name, 'account_open_date', nowdate(), update_modified=False
                    )
                    frappe.db.commit()
        except Exception:
            # Non-critical: don't fail the save if this additional step errors
            pass
        
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

        # Capture previous status for creating a Version entry
        previous_status = frappe.db.get_value('CRM Lead', lead_name, 'status')

        # Then update status
        frappe.db.set_value(
            'CRM Lead',
            lead_name,
            'status',
            new_status,
            update_modified=False
        )

        # If status changed to Account Opened, set account_open_date
        try:
            if new_status == 'Account Opened':
                frappe.db.set_value(
                    'CRM Lead', lead_name, 'account_open_date', nowdate(), update_modified=False
                )
        except Exception:
            # Non-critical
            pass

        # Commit the transaction
        frappe.db.commit()

        # Create a Version entry so the status change appears in Activity
        try:
            # include meta so activities can surface client_id / rejection_reason
            lead_vals = frappe.db.get_value('CRM Lead', lead_name, ['client_id', 'rejection_reason'], as_dict=True)
            version_data = {
                'changed': [["status", previous_status, new_status]],
                'added': [],
                'removed': [],
                'row_changed': [],
                'data_import': None,
                'updater_reference': None,
                'meta': {
                    'client_id': lead_vals.get('client_id') if lead_vals else None,
                    'rejection_reason': lead_vals.get('rejection_reason') if lead_vals else None,
                },
            }
            v = frappe.get_doc({
                'doctype': 'Version',
                'ref_doctype': 'CRM Lead',
                'docname': lead_name,
                'data': frappe.as_json(version_data),
            })
            v.insert(ignore_permissions=True)
            # Also create a comment so UI can prioritise comment-based activity messages
            try:
                comment_text = f"Status changed to {new_status}."
                # Prepare escaped values
                client_html = None
                rejection_html = None
                if lead_vals:
                    if lead_vals.get('client_id'):
                        client_html = escape_html(lead_vals.get('client_id'))
                    if lead_vals.get('rejection_reason'):
                        rejection_html = escape_html(lead_vals.get('rejection_reason'))

                # Only include relevant information based on the target status
                if new_status in ['Account Opened', 'Account Activated'] and client_html:
                    comment_text += f" Client ID: <span style=\"color:#2563eb\">{client_html}</span>"
                elif new_status == 'Rejected - Follow-up Required' and rejection_html:
                    comment_text += f" Rejection Reason: <span style=\"color:#dc2626\">{rejection_html}</span>"

                c = frappe.get_doc({
                    'doctype': 'Comment',
                    'comment_type': 'Comment',
                    'reference_doctype': 'CRM Lead',
                    'reference_name': lead_name,
                    'content': comment_text,
                })
                c.insert(ignore_permissions=True)
            except Exception:
                pass
        except Exception:
            # Non-critical: if version insertion fails, continue
            pass

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
def save_rejection_reason_without_validation(lead_name, rejection_reason):
    """
    Save rejection_reason to lead document without triggering full validation
    This is used when rejecting a lead and we need to capture the reason
    """
    try:
        # Use direct SQL to avoid validation
        frappe.db.set_value(
            'CRM Lead',
            lead_name,
            'rejection_reason',
            rejection_reason,
            update_modified=False
        )
        
        # Commit the transaction
        frappe.db.commit()
        
        return {
            'success': True,
            'message': 'Rejection reason saved successfully'
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error saving rejection_reason for lead {lead_name}: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to save rejection reason: {str(e)}'
        }

@frappe.whitelist()
def update_lead_status_with_rejection_reason(lead_name, new_status, rejection_reason=None):
    """
    Update lead status and optionally save rejection_reason in a single operation
    This handles the case where rejection_reason needs to be saved before status change
    """
    try:
        # First save rejection_reason if provided
        if rejection_reason:
            frappe.db.set_value(
                'CRM Lead',
                lead_name,
                'rejection_reason',
                rejection_reason,
                update_modified=False
            )

        # Capture previous status for creating a Version entry
        previous_status = frappe.db.get_value('CRM Lead', lead_name, 'status')

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

        # Create a Version entry so the status change appears in Activity
        try:
            # include meta so activities can surface client_id / rejection_reason
            lead_vals = frappe.db.get_value('CRM Lead', lead_name, ['client_id', 'rejection_reason'], as_dict=True)
            version_data = {
                'changed': [["status", previous_status, new_status]],
                'added': [],
                'removed': [],
                'row_changed': [],
                'data_import': None,
                'updater_reference': None,
                'meta': {
                    'client_id': lead_vals.get('client_id') if lead_vals else None,
                    'rejection_reason': lead_vals.get('rejection_reason') if lead_vals else None,
                },
            }
            v = frappe.get_doc({
                'doctype': 'Version',
                'ref_doctype': 'CRM Lead',
                'docname': lead_name,
                'data': frappe.as_json(version_data),
            })
            v.insert(ignore_permissions=True)
            # Also create a comment so UI can prioritise comment-based activity messages
            try:
                comment_text = f"Status changed to {new_status}."
                # Prepare escaped values
                client_html = None
                rejection_html = None
                if lead_vals:
                    if lead_vals.get('client_id'):
                        client_html = escape_html(lead_vals.get('client_id'))
                    if lead_vals.get('rejection_reason'):
                        rejection_html = escape_html(lead_vals.get('rejection_reason'))

                # Only include relevant information based on the target status
                if new_status in ['Account Opened', 'Account Activated'] and client_html:
                    comment_text += f" Client ID: <span style=\"color:#2563eb\">{client_html}</span>"
                elif new_status == 'Rejected - Follow-up Required' and rejection_html:
                    comment_text += f" Rejection Reason: <span style=\"color:#dc2626\">{rejection_html}</span>"

                c = frappe.get_doc({
                    'doctype': 'Comment',
                    'comment_type': 'Comment',
                    'reference_doctype': 'CRM Lead',
                    'reference_name': lead_name,
                    'content': comment_text,
                })
                c.insert(ignore_permissions=True)
            except Exception:
                pass
        except Exception:
            # Non-critical: if version insertion fails, continue
            pass

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
        
        # Check if status requires rejection_reason
        if target_status in ['Rejected - Follow-up Required']:
            if not lead.rejection_reason:
                errors.append('Rejection reason is required for this status')
        
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

@frappe.whitelist()
def bulk_insert_pod_id(doctype, docnames, pod_id):
    """
    Bulk insert POD ID to multiple leads
    """
    try:
        if not doctype or not docnames or not pod_id:
            frappe.throw("Missing required parameters")
        
        if doctype != "CRM Lead":
            frappe.throw("This function is only available for CRM Lead doctype")
        
        # Convert docnames to list if it's a string
        if isinstance(docnames, str):
            docnames = frappe.parse_json(docnames)
        
        if not isinstance(docnames, list):
            frappe.throw("Invalid docnames format")
        
        # Validate POD ID
        pod_id = str(pod_id).strip()
        if not pod_id:
            frappe.throw("POD ID cannot be empty")
        
        # Check permissions
        if not frappe.has_permission("CRM Lead", "write"):
            frappe.throw("Insufficient permissions to update leads")
        
        updated_count = 0
        failed_leads = []
        
        for lead_name in docnames:
            try:
                # Check if lead exists
                if not frappe.db.exists("CRM Lead", lead_name):
                    failed_leads.append(f"{lead_name} (not found)")
                    continue
                
                # Update POD ID
                frappe.db.set_value(
                    'CRM Lead',
                    lead_name,
                    'pod_id',
                    pod_id,
                    update_modified=False
                )
                updated_count += 1
                
            except Exception as e:
                failed_leads.append(f"{lead_name} ({str(e)})")
                frappe.log_error(f"Error updating POD ID for lead {lead_name}: {str(e)}")
        
        # Commit all changes
        frappe.db.commit()
        
        # Prepare response
        result = {
            "success": True,
            "message": f"POD ID '{pod_id}' inserted successfully for {updated_count} lead(s)",
            "data": {
                "pod_id": pod_id,
                "total_leads": len(docnames),
                "updated_count": updated_count,
                "failed_count": len(failed_leads),
                "failed_leads": failed_leads
            }
        }
        
        # Log the operation
        frappe.logger().info(f"Bulk POD ID insertion: {result['message']}")
        
        return result
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error in bulk_insert_pod_id: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 