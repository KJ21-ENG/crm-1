import frappe

def execute():
    """Fix existing CRM Call Log records where native call type was not properly prioritized over duration"""

    # Find records that are likely incorrectly labeled due to the old logic
    # These are calls with very short durations that were marked as "Completed"
    # but should probably be "No Answer" based on typical call patterns

    # Conservative approach: Only fix records with duration <= 10 seconds that are marked as "Completed"
    # This catches the most obvious cases where missed calls were incorrectly labeled

    records_to_fix = frappe.db.sql("""
        SELECT name, type, status, duration
        FROM `tabCRM Call Log`
        WHERE status = 'Completed'
        AND duration > 0
        AND duration <= 10
        AND (type = 'Incoming' OR type = 'Outgoing')
    """, as_dict=True)

    print(f"Found {len(records_to_fix)} records that may need status correction")

    fixed_count = 0

    for record in records_to_fix:
        old_status = record['status']
        duration = record['duration'] or 0

        # Apply the corrected logic
        if duration <= 10:  # Very short calls are likely unanswered
            if record['type'] == 'Outgoing':
                new_status = 'Did Not Picked'
            else:  # Incoming
                new_status = 'Missed Call'

            # Update the record
            frappe.db.sql("""
                UPDATE `tabCRM Call Log`
                SET status = %s, modified = NOW(), modified_by = 'Administrator'
                WHERE name = %s
            """, (new_status, record['name']))

            print(f"Fixed {record['name']}: {record['type']} call, {duration}s duration → {new_status} (was {old_status})")
            fixed_count += 1

    if fixed_count > 0:
        frappe.db.commit()
        print(f"Successfully fixed {fixed_count} call log records")
    else:
        print("No records needed fixing")

    return fixed_count

