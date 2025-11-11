import frappe

def execute():
    """Rename CRM Ticket Subject docs so that name == subject_name, and update tickets.
    Safe to run multiple times.
    """
    # Find subjects where name != subject_name
    subjects = frappe.get_all(
        "CRM Ticket Subject",
        fields=["name", "subject_name"],
    )

    for s in subjects:
        try:
            if not s.subject_name:
                continue

            # Skip if already matching
            if s.name == s.subject_name:
                continue

            # If a doc with target name exists, skip renaming and just update tickets
            target_exists = frappe.db.exists("CRM Ticket Subject", s.subject_name)

            if not target_exists:
                # Rename subject to subject_name (merge disabled, force=False)
                frappe.rename_doc("CRM Ticket Subject", s.name, s.subject_name, force=False, merge=False)

            # Update any tickets referencing old name to point to new name
            frappe.db.sql(
                """
                UPDATE `tabCRM Ticket`
                SET ticket_subject = %(new)s
                WHERE ticket_subject = %(old)s
                """,
                {"new": s.subject_name, "old": s.name},
            )
        except Exception:
            frappe.log_error(f"Failed updating CRM Ticket Subject rename for {s.name}")

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