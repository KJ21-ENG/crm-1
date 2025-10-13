import frappe


def execute():
    """
    Update `pod_id` Custom Field on `CRM Lead`:
    - Make it Read Only (non-editable)
    - Show only when it has a value (depends_on = eval:doc.pod_id)
    """
    try:
        if not frappe.db.exists("Custom Field", {"dt": "CRM Lead", "fieldname": "pod_id"}):
            return

        cf_name = frappe.db.get_value(
            "Custom Field", {"dt": "CRM Lead", "fieldname": "pod_id"}, "name"
        )
        cf = frappe.get_doc("Custom Field", cf_name)

        # Ensure read-only and conditional visibility
        cf.fieldtype = "Read Only"
        cf.read_only = 1
        cf.depends_on = "eval:doc.pod_id"
        # Keep it searchable/list if already set
        cf.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"update_pod_id_field_properties patch failed: {str(e)}")
        raise


