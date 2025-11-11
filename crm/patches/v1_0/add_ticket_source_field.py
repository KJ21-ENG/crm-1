import frappe

def execute():
    """Add ticket_source field to CRM Ticket DocType"""
    
    # Check if the field already exists
    if not frappe.db.exists("DocField", {"parent": "CRM Ticket", "fieldname": "ticket_source"}):
        # Add the field to the DocType
        frappe.get_doc({
            "doctype": "DocField",
            "parent": "CRM Ticket",
            "fieldname": "ticket_source",
            "fieldtype": "Select",
            "label": "Ticket Source",
            "options": "On Call\nOffice Visit",
            "default": "On Call",
            "reqd": 1,
            "in_list_view": 0,
            "in_standard_filter": 0,
            "in_global_search": 0,
            "permlevel": 0,
            "ignore_user_permissions": 0,
            "report_hide": 0,
            "print_hide": 0,
            "print_hide_if_no_value": 0,
            "no_copy": 0,
            "allow_on_submit": 0,
            "collapsible": 0,
            "collapsible_depends_on": "",
            "bold": 0,
            "depends_on": "",
            "mandatory_depends_on": "",
            "read_only_depends_on": "",
            "description": "Source of the ticket (On Call or Office Visit)",
            "modified": frappe.utils.now(),
            "owner": "Administrator"
        }).insert(ignore_permissions=True)
        
        # Update the field order
        field_order = frappe.get_meta("CRM Ticket").get_field_order()
        if "ticket_source" not in field_order:
            # Insert after department field
            dept_index = field_order.index("department") if "department" in field_order else -1
            if dept_index >= 0:
                field_order.insert(dept_index + 1, "ticket_source")
            else:
                field_order.append("ticket_source")
            
            # Update the DocType
            doc = frappe.get_doc("DocType", "CRM Ticket")
            doc.field_order = field_order
            doc.save(ignore_permissions=True)
        
        print("✅ Added ticket_source field to CRM Ticket DocType")
    else:
        print("ℹ️ ticket_source field already exists in CRM Ticket DocType")
    
    # Update existing tickets to have default value
    frappe.db.sql("""
        UPDATE `tabCRM Ticket` 
        SET ticket_source = 'On Call' 
        WHERE ticket_source IS NULL OR ticket_source = ''
    """)
    
    print("✅ Updated existing tickets with default ticket_source value") 