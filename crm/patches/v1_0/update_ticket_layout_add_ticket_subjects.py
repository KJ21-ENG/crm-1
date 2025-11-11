import json
import frappe


def _insert_after(lst, needle, to_insert):
    try:
        idx = lst.index(needle)
    except ValueError:
        return False
    if to_insert in lst:
        return False
    lst.insert(idx + 1, to_insert)
    return True


def _ensure_field_in_layout(layout_json: str) -> str:
    if not layout_json:
        return layout_json
    try:
        data = json.loads(layout_json)
    except Exception:
        return layout_json

    def insert_in_sections(sections):
        changed = False
        for section in sections or []:
            for column in (section.get("columns") or []):
                fields = column.get("fields") or []
                if _insert_after(fields, "ticket_subject", "ticket_subjects"):
                    changed = True
                column["fields"] = fields
        return changed

    changed_any = False
    # Support both tabbed and non-tabbed structures
    if isinstance(data, list):
        # detect tab structure
        if data and isinstance(data[0], dict) and "sections" in data[0]:
            for tab in data:
                if insert_in_sections(tab.get("sections") or []):
                    changed_any = True
        else:
            if insert_in_sections(data):
                changed_any = True

    if changed_any:
        return json.dumps(data)
    return layout_json


def execute():
    for layout_type in ["Quick Entry", "Data Fields", "Side Panel"]:
        if not frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": layout_type}):
            continue
        doc = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": layout_type})
        new_layout = _ensure_field_in_layout(doc.layout or "")
        if new_layout != (doc.layout or ""):
            doc.layout = new_layout
            doc.save(ignore_permissions=True)



