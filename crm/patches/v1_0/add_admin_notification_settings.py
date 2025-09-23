import frappe


def execute():
    """Ensure a minimal 'Notification Settings' for Administrator exists.

    This patch inserts a lightweight record if missing so session boot
    (which expects Notification Settings for the session user) does not fail.
    """
    try:
        if not frappe.db.exists("Notification Settings", "Administrator"):
            frappe.get_doc({
                "doctype": "Notification Settings",
                "name": "Administrator",
                "user": "Administrator",
                "enabled": 1,
            }).insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "add_admin_notification_settings patch")


