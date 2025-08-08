import frappe


def execute():
    """
    Add a unique device_call_id field to CRM Call Log for mobile sync de-duplication.

    This aligns the database with crm.api.mobile_sync which checks/sets `device_call_id`.
    """
    doctype = "CRM Call Log"
    fieldname = "device_call_id"

    # If DocField already exists, nothing to do
    if frappe.db.exists("DocField", {"parent": doctype, "fieldname": fieldname}):
        return

    # Create DocField on the DocType so schema sync can add the column
    df = frappe.get_doc({
        "doctype": "DocField",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "fields",
        "fieldname": fieldname,
        "fieldtype": "Data",
        "label": "Device Call ID",
        "unique": 1,
        "in_list_view": 0,
        "reqd": 0,
        "read_only": 0,
        "no_copy": 1,
        "hidden": 0,
        "insert_after": "id",  # place next to existing id
    })
    df.insert(ignore_permissions=True)

    # Ensure it appears in field_order sensibly (best-effort; ignore if not present)
    try:
        doc = frappe.get_doc("DocType", doctype)
        field_order = list(doc.field_order or [])
        if fieldname not in field_order:
            try:
                idx_after = field_order.index("id") + 1 if "id" in field_order else len(field_order)
                field_order.insert(idx_after, fieldname)
            except Exception:
                field_order.append(fieldname)
            doc.field_order = field_order
            doc.save(ignore_permissions=True)
    except Exception:
        # Non-fatal; field exists and schema migration will add the column
        pass

    frappe.db.commit()


