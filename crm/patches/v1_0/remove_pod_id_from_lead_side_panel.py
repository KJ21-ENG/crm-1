import json
import frappe


def execute():
    """
    Remove `pod_id` from CRM Lead Side Panel layout so it only shows in header.
    Safe to re-run.
    """
    try:
        layout_name = "CRM Lead-Side Panel"
        if not frappe.db.exists("CRM Fields Layout", layout_name):
            return

        layout_doc = frappe.get_doc("CRM Fields Layout", layout_name)
        layout_data = []
        if layout_doc.layout:
            try:
                layout_data = json.loads(layout_doc.layout)
            except Exception:
                layout_data = []

        changed = False
        for section in layout_data or []:
            for column in section.get("columns", []) or []:
                fields = column.get("fields") or []
                if "pod_id" in fields:
                    fields = [f for f in fields if f != "pod_id"]
                    column["fields"] = fields
                    changed = True

        if changed:
            layout_doc.layout = json.dumps(layout_data, indent=2)
            layout_doc.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"remove_pod_id_from_lead_side_panel patch failed: {str(e)}")
        raise


