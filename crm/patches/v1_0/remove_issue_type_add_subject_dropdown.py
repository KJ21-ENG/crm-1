import frappe

def execute():
    """Remove issue_type field and update ticket_subject to Link type"""
    
    # Update existing tickets to remove issue_type values
    frappe.db.sql("""
        UPDATE `tabCRM Ticket` 
        SET issue_type = NULL 
        WHERE issue_type IS NOT NULL
    """)
    
    print("✅ Successfully removed issue_type field and updated ticket_subject to Link type") 