import frappe

def execute():
    """Remove read_only property from customer fields in CRM Ticket and CRM Lead DocTypes"""
    
    # Fix CRM Ticket fields
    ticket_fields_to_fix = [
        'first_name', 'last_name', 'email', 'mobile_no', 
        'pan_card_number', 'aadhaar_card_number'
    ]
    
    for fieldname in ticket_fields_to_fix:
        frappe.db.sql("""
            UPDATE `tabDocField` 
            SET read_only = 0 
            WHERE parent = 'CRM Ticket' AND fieldname = %s
        """, fieldname)
    
    # Fix CRM Lead fields
    lead_fields_to_fix = [
        'first_name', 'last_name', 'email', 'mobile_no', 
        'pan_card_number', 'aadhaar_card_number'
    ]
    
    for fieldname in lead_fields_to_fix:
        frappe.db.sql("""
            UPDATE `tabDocField` 
            SET read_only = 0 
            WHERE parent = 'CRM Lead' AND fieldname = %s
        """, fieldname)
    
    frappe.db.commit()
    print("✅ Removed read_only property from customer fields in CRM Ticket and CRM Lead DocTypes") 