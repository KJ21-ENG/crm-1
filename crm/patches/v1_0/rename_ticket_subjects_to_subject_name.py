import frappe


def execute():
    """
    Ensure CRM Ticket Subject docname equals subject_name for all records,
    and update tickets to point to the new names. Idempotent.
    """
    subjects = frappe.get_all(
        "CRM Ticket Subject", fields=["name", "subject_name"], order_by="creation asc"
    )

    for subj in subjects:
        subject_name = (subj.subject_name or "").strip()
        if not subject_name:
            continue

        old = subj.name
        new = subject_name

        if old == new:
            continue

        try:
            # If target exists, merge into it; else rename
            target_exists = frappe.db.exists("CRM Ticket Subject", new)
            if target_exists:
                # Update tickets to target name, then delete/merge old
                frappe.db.sql(
                    """
                    UPDATE `tabCRM Ticket`
                    SET ticket_subject = %(new)s
                    WHERE ticket_subject = %(old)s
                    """,
                    {"new": new, "old": old},
                )
                # Delete old subject if safe
                if frappe.db.count("CRM Ticket", {"ticket_subject": old}) == 0:
                    try:
                        frappe.delete_doc("CRM Ticket Subject", old, ignore_permissions=True)
                    except Exception:
                        pass
            else:
                # Rename subject to new value
                frappe.rename_doc(
                    "CRM Ticket Subject", old, new, force=False, merge=False
                )
                # Update tickets referencing old (in case rename didn't cascade)
                frappe.db.sql(
                    """
                    UPDATE `tabCRM Ticket`
                    SET ticket_subject = %(new)s
                    WHERE ticket_subject = %(old)s
                    """,
                    {"new": new, "old": old},
                )
        except Exception as e:
            frappe.log_error(
                f"Failed to normalize CRM Ticket Subject name for '{old}' -> '{new}': {e}"
            )


