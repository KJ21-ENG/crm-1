import frappe
import json

def execute():
    """
    Enable and configure quick filters for CRM Lead, CRM Ticket, CRM Deal, Contact, CRM Organization, CRM Task, CRM Call Log.
    This ensures all team members get the same quick filter configuration after running bench migrate.
    """
    # --- CRM Lead ---
    lead_fields = [
        'status', 'lead_owner', 'source', 'territory', 'mobile_no', 'industry',
        'pan_card_number', 'aadhaar_card_number', 'email', 'first_name', 'last_name', 'lead_name', 'converted_from_lead'
    ]
    set_in_standard_filter('CRM Lead', lead_fields)
    set_quick_filter_global_settings('CRM Lead', lead_fields)

    # --- CRM Ticket ---
    ticket_fields = [
        'status', 'priority', 'ticket_owner', 'department', 'mobile_no', 'issue_type',
        'customer_name', 'first_name', 'last_name', 'email', 'resolved', 'creation'
    ]
    set_in_standard_filter('CRM Ticket', ticket_fields)
    set_quick_filter_global_settings('CRM Ticket', ticket_fields)

    # --- CRM Deal ---
    deal_fields = [
        'status', 'deal_owner', 'organization', 'territory', 'close_date', 'annual_revenue',
        'probability', 'industry', 'deal_value', 'creation'
    ]
    set_in_standard_filter('CRM Deal', deal_fields)
    set_quick_filter_global_settings('CRM Deal', deal_fields)

    # --- Contact ---
    contact_fields = [
        'company_name', 'mobile_no', 'email_id', 'gender', 'designation',
        'is_primary_contact', 'first_name', 'last_name', 'creation', 'status'
    ]
    set_in_standard_filter('Contact', contact_fields)
    set_quick_filter_global_settings('Contact', contact_fields)

    # --- CRM Organization ---
    org_fields = [
        'territory', 'industry', 'annual_revenue', 'no_of_employees', 'organization_name', 'website', 'creation'
    ]
    set_in_standard_filter('CRM Organization', org_fields)
    set_quick_filter_global_settings('CRM Organization', org_fields)

    # --- CRM Task ---
    task_fields = [
        'due_date', 'reference_doctype', 'task_type', 'status', 'creation'
    ]
    set_in_standard_filter('CRM Task', task_fields)
    set_quick_filter_global_settings('CRM Task', task_fields)

    # --- CRM Call Log ---
    call_log_fields = [
        'duration', 'recording_available', 'created_on', 'status', 'creation'
    ]
    set_in_standard_filter('CRM Call Log', call_log_fields)
    set_quick_filter_global_settings('CRM Call Log', call_log_fields)

    frappe.db.commit()
    print("Quick filter configuration applied for all major CRM doctypes.")

def set_in_standard_filter(doctype, fieldnames):
    """Enable in_standard_filter for given fields in DocField table."""
    if not fieldnames:
        return
    frappe.db.sql(f"""
        UPDATE `tabDocField`
        SET in_standard_filter = 1
        WHERE parent = %s AND fieldname IN ({','.join(['%s']*len(fieldnames))})
    """, [doctype] + fieldnames)

def set_quick_filter_global_settings(doctype, fieldnames):
    """Insert or update CRM Global Settings for quick filters."""
    filters_json = json.dumps(fieldnames)
    frappe.db.sql("""
        INSERT INTO `tabCRM Global Settings` (name, dt, type, json, docstatus)
        VALUES (%s, %s, 'Quick Filters', %s, 0)
        ON DUPLICATE KEY UPDATE json=VALUES(json)
    """, [f"Quick Filters-{doctype}", doctype, filters_json]) 