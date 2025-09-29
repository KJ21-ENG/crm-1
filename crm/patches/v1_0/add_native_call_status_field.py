import frappe


def execute():
    """
    Add `native_call_status` field to `CRM Call Log` and backfill values
    from existing fields (`native_call_type`, `status`, `duration`).
    """
    # Reload DocType to ensure the new field exists from JSON
    try:
        frappe.reload_doc("fcrm", "doctype", "crm_call_log")
    except Exception:
        # Some setups may use module name case as "FCRM"
        try:
            frappe.reload_doc("FCRM", "doctype", "crm_call_log")
        except Exception:
            pass

    # Ensure column exists before backfill
    if not frappe.db.has_column("CRM Call Log", "native_call_status"):
        return

    # Backfill from native_call_type short codes where available
    # native_call_type values we used earlier: 'missed', 'rej', 'in', 'out', 'unk'
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'missed'
        where coalesce(native_call_type, '') = 'missed'
        """
    )
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'rejected'
        where coalesce(native_call_type, '') = 'rej'
        """
    )

    # From high-level status where native_call_type was not present
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'missed'
        where coalesce(native_call_status, '') = '' and status = 'Missed Call'
        """
    )
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'rejected'
        where coalesce(native_call_status, '') = '' and status = 'Canceled'
        """
    )
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'no_answer'
        where coalesce(native_call_status, '') = '' and status = 'Did Not Picked'
        """
    )
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = 'completed'
        where coalesce(native_call_status, '') = '' and status = 'Completed' and ifnull(duration, 0) > 0
        """
    )

    # As a final fallback, mirror a normalized version of status
    frappe.db.sql(
        """
        update `tabCRM Call Log`
        set native_call_status = lower(status)
        where coalesce(native_call_status, '') = '' and ifnull(status, '') != ''
        """
    )


