import frappe
import json


def execute():
    """Remove 'department' from CRM Ticket Quick Entry fields layout if present."""
    try:
        if not frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"}):
            return

        doc = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
        layout = json.loads(doc.layout or '[]')

        def remove_department(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'fields' and isinstance(v, list):
                        if 'department' in v:
                            v[:] = [f for f in v if f != 'department']
                    else:
                        try:
                            remove_department(v)
                        except Exception:
                            pass
            elif isinstance(obj, list):
                for item in obj:
                    try:
                        remove_department(item)
                    except Exception:
                        pass

        remove_department(layout)

        doc.layout = json.dumps(layout)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'remove_department_from_ticket_quick_entry_layout')


