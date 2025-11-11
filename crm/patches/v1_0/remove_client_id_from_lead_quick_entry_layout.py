import json
import frappe


def execute():
    """Remove `client_id` from CRM Lead Quick Entry layout if present."""
    if not frappe.db.exists("CRM Fields Layout", {"dt": "CRM Lead", "type": "Quick Entry"}):
        return

    layout_doc = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Lead", "type": "Quick Entry"})
    try:
        layout = json.loads(layout_doc.layout or '[]')
    except Exception:
        layout = []

    modified = False
    for tab in layout:
        for section in tab.get('sections', []):
            for column in section.get('columns', []):
                fields = column.get('fields', [])
                if 'client_id' in fields:
                    fields = [f for f in fields if f != 'client_id']
                    column['fields'] = fields
                    modified = True

    if modified:
        layout_doc.layout = json.dumps(layout)
        layout_doc.save(ignore_permissions=True)
        frappe.db.commit()


