import frappe

def execute():
    """Update existing CRM Call Log records to use frontend-compatible status values"""

    # Update records with status 'No Answer' to use the new status labels
    # based on call type and duration logic

    frappe.db.sql("""
        UPDATE `tabCRM Call Log`
        SET status = CASE
            WHEN status = 'No Answer' AND type = 'Incoming' THEN 'Missed Call'
            WHEN status = 'No Answer' AND type = 'Outgoing' THEN 'Did Not Picked'
            ELSE status
        END
        WHERE status = 'No Answer'
    """)

    # Also update any records that might have been affected by the old frontend override logic
    # These would be records with duration = 0 that were incorrectly labeled as 'Completed'
    frappe.db.sql("""
        UPDATE `tabCRM Call Log`
        SET status = CASE
            WHEN duration = 0 AND type = 'Incoming' THEN 'Missed Call'
            WHEN duration = 0 AND type = 'Outgoing' THEN 'Did Not Picked'
            ELSE status
        END
        WHERE duration = 0 AND status = 'Completed'
    """)

    frappe.db.commit()
    print("Updated CRM Call Log statuses for frontend compatibility")

