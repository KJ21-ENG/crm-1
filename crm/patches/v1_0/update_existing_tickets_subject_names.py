import frappe

def execute():
    """Update existing tickets to store actual subject names instead of document names"""
    
    # Get all tickets that have ticket_subject but no subject name
    tickets = frappe.get_all(
        "CRM Ticket",
        filters={"ticket_subject": ["is", "set"]},
        fields=["name", "ticket_subject"]
    )
    
    updated_count = 0
    for ticket in tickets:
        try:
            # Get the subject document
            subject_doc = frappe.get_doc("CRM Ticket Subject", ticket.ticket_subject)
            
            # Update the ticket with the actual subject name
            frappe.db.set_value(
                "CRM Ticket",
                ticket.name,
                "subject",
                subject_doc.subject_name
            )
            
            updated_count += 1
        except frappe.DoesNotExistError:
            # Subject document doesn't exist, skip
            continue
    
    print(f"✅ Successfully updated {updated_count} tickets with actual subject names") 