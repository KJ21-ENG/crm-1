import frappe

def execute():
    """Add client_id field metadata to CRM Customer DocType"""
    
    # Check if DocField already exists
    if not frappe.db.exists("DocField", {"parent": "CRM Customer", "fieldname": "client_id"}):
        # Add the client_id field metadata
        frappe.get_doc({
            "doctype": "DocField",
            "parent": "CRM Customer",
            "parenttype": "DocType",
            "fieldname": "client_id",
            "fieldtype": "Data",
            "label": "Client ID",
            "description": "Unique client identifier",
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "in_global_search": 0,
            "in_preview": 0,
            "bold": 0,
            "no_copy": 0,
            "allow_in_quick_entry": 0,
            "ignore_xss_filter": 0,
            "hidden": 0,
            "print_hide": 0,
            "report_hide": 0,
            "allow_on_submit": 0,
            "set_only_once": 0,
            "fetch_if_empty": 0,
            "collapsible": 0,
            "collapsible_depends_on": "",
            "mandatory_depends_on": "",
            "read_only_depends_on": "",
            "depends_on": "",
            "permlevel": 0,
            "ignore_user_permissions": 0,
            "width": "",
            "print_width": "",
            "columns": 0,
            "default": "",
            "options": "",
            "length": 140,
            "precision": "",
            "scale": "",
            "translatable": 0,
            "hide_seconds": 0,
            "hide_days": 0,
            "non_negative": 0,
            "is_virtual": 0,
            "sort_options": 0,
            "remember_last_selected_value": 0,
            "fetch_from": "",
            "fetch_if_empty": 0,
            "on_dashboard": 0,
            "dashboard_module": "",
            "description": "Unique client identifier for tracking and reference",
        }).insert(ignore_permissions=True)
        
        print("✅ Added client_id field metadata to CRM Customer DocType")
    else:
        print("ℹ️ client_id field metadata already exists in CRM Customer DocType")
    
    # Also add referral_code field metadata if missing
    if not frappe.db.exists("DocField", {"parent": "CRM Customer", "fieldname": "referral_code"}):
        frappe.get_doc({
            "doctype": "DocField",
            "parent": "CRM Customer",
            "parenttype": "DocType",
            "fieldname": "referral_code",
            "fieldtype": "Data",
            "label": "Referral Code",
            "description": "Referral code for tracking referrals",
            "reqd": 0,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "in_global_search": 0,
            "in_preview": 0,
            "bold": 0,
            "no_copy": 0,
            "allow_in_quick_entry": 0,
            "ignore_xss_filter": 0,
            "hidden": 0,
            "print_hide": 0,
            "report_hide": 0,
            "allow_on_submit": 0,
            "set_only_once": 0,
            "fetch_if_empty": 0,
            "collapsible": 0,
            "collapsible_depends_on": "",
            "mandatory_depends_on": "",
            "read_only_depends_on": "",
            "depends_on": "",
            "permlevel": 0,
            "ignore_user_permissions": 0,
            "width": "",
            "print_width": "",
            "columns": 0,
            "default": "",
            "options": "",
            "length": 140,
            "precision": "",
            "scale": "",
            "translatable": 0,
            "hide_seconds": 0,
            "hide_days": 0,
            "non_negative": 0,
            "is_virtual": 0,
            "sort_options": 0,
            "remember_last_selected_value": 0,
            "fetch_from": "",
            "fetch_if_empty": 0,
            "on_dashboard": 0,
            "dashboard_module": "",
            "description": "Referral code for tracking customer referrals",
        }).insert(ignore_permissions=True)
        
        print("✅ Added referral_code field metadata to CRM Customer DocType")
    else:
        print("ℹ️ referral_code field metadata already exists in CRM Customer DocType")
    
    # Clear cache to ensure changes take effect
    frappe.clear_cache() 