import frappe


def execute():
    """Add Table MultiSelect field 'ticket_subjects' to CRM Ticket and backfill rows.
    Also ensure child doctype exists (migrated via model sync) and update layouts if needed.
    """
    try:
        # Ensure field exists on DocType (safe to run multiple times)
        if not frappe.db.exists("DocField", {"parent": "CRM Ticket", "fieldname": "ticket_subjects"}):
            df = frappe.get_doc({
                "doctype": "DocField",
                "parent": "CRM Ticket",
                "fieldname": "ticket_subjects",
                "fieldtype": "Table MultiSelect",
                "label": "Subjects",
                "options": "CRM Ticket Subject Item",
                "insert_after": "ticket_subject",
                "reqd": 0,
                "description": "Select one or more subjects",
            })
            df.insert(ignore_permissions=True)

        # Backfill: for tickets that have ticket_subject but no child rows yet
        tickets = frappe.get_all(
            "CRM Ticket",
            filters=[["ticket_subject", "is", "set"]],
            fields=["name"],
        )
        for t in tickets:
            try:
                exists = frappe.db.exists(
                    "CRM Ticket Subject Item",
                    {"parenttype": "CRM Ticket", "parent": t.name},
                )
                if exists:
                    continue
                ticket_subject = frappe.db.get_value("CRM Ticket", t.name, "ticket_subject")
                if not ticket_subject:
                    continue
                child = frappe.get_doc({
                    "doctype": "CRM Ticket Subject Item",
                    "parenttype": "CRM Ticket",
                    "parent": t.name,
                    "parentfield": "ticket_subjects",
                    "subject": ticket_subject,
                })
                child.insert(ignore_permissions=True)
            except Exception:
                frappe.db.rollback()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()



