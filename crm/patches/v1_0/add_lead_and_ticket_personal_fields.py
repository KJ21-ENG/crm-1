import frappe


def execute():
    """Reload doctypes and update Quick Entry layouts to include personal fields.

    Adds fields to layouts after last_name for both Lead and Ticket.
    """
    # Reload doctypes to pick up JSON changes
    frappe.reload_doc("fcrm", "doctype", "crm_lead")
    frappe.reload_doc("fcrm", "doctype", "crm_ticket")

    # Update CRM Fields Layout entries if present
    try:
        update_layout("CRM Lead-Quick Entry", [
            "marital_status",
            "date_of_birth",
            "anniversary",
        ], after_field="last_name")
    except Exception:
        pass

    try:
        update_layout("CRM Ticket-Quick Entry", [
            "marital_status",
            "date_of_birth",
            "anniversary",
        ], after_field="last_name")
    except Exception:
        pass


def update_layout(layout_name: str, fields_to_add: list[str], after_field: str = "last_name") -> None:
    import json

    layout_doc = frappe.get_doc("CRM Fields Layout", layout_name)
    if not layout_doc.layout:
        return

    layout_data = json.loads(layout_doc.layout)
    if not layout_data:
        return

    # naive walk: add to the first tab/section/column where after_field exists
    for tab in layout_data:
        for section in tab.get("sections", []):
            for column in section.get("columns", []):
                col_fields = column.get("fields", [])
                # fields may be array of string names or objects
                # Normalize to list of fieldnames for search
                names = [f if isinstance(f, str) else f.get("fieldname") for f in col_fields]
                if after_field in names:
                    idx = names.index(after_field)
                    # Insert in order right after the anchor
                    insertion = [f for f in fields_to_add if f not in names]
                    for offset, fname in enumerate(insertion, start=1):
                        col_fields.insert(idx + offset, fname)
                    column["fields"] = col_fields
                    layout_doc.layout = json.dumps(layout_data, indent=2)
                    layout_doc.save(ignore_permissions=True)
                    return


