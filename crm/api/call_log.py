"""Call log specific API helpers."""

import frappe
from frappe import _
from frappe.utils import cint


@frappe.whitelist()
def set_cold_call(call_log: str, cold_call: int | str | bool = 1):
    """Mark or unmark a call log as a cold call.

    Args:
        call_log: Name of the ``CRM Call Log`` document to update.
        cold_call: Truthy value marks as cold, falsy removes the flag.
    """
    if not call_log:
        frappe.throw(_("Call log name is required"))

    doc = frappe.get_doc("CRM Call Log", call_log)
    if not doc.has_permission("write"):
        frappe.throw(_("Not permitted to update this call log"), frappe.PermissionError)

    flag = 1 if cint(cold_call) else 0
    # set_value can raise QueryDeadlockError (Record has changed since last read).
    # Retry a couple of times to handle transient snapshot isolation / deadlock errors.
    from time import sleep

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            frappe.db.set_value(
                "CRM Call Log",
                call_log,
                "is_cold_call",
                flag,
                update_modified=True,
            )
            break
        except frappe.QueryDeadlockError:
            if attempt == max_retries:
                raise
            # small backoff before retrying
            sleep(0.1 * attempt)

    return {"name": doc.name, "is_cold_call": flag}
