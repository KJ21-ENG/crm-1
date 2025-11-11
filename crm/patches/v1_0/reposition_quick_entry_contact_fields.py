import json
import frappe


def execute():
    """Reposition fields in Quick Entry for Lead and Ticket per 3-column sketch.

    Columns per sketch (top to bottom):
    - Left: first_name, last_name, pan_card_number
    - Middle: email, mobile_no, aadhaar_card_number
    - Right: marital_status, date_of_birth, anniversary
    """
    layouts = [
        ("CRM Lead-Quick Entry", {
            "left": ["first_name", "last_name", "pan_card_number"],
            "middle": ["email", "mobile_no", "aadhaar_card_number"],
            "right": ["marital_status", "date_of_birth", "anniversary"],
        }),
        ("CRM Ticket-Quick Entry", {
            "left": ["first_name", "last_name", "pan_card_number"],
            "middle": ["email", "mobile_no", "aadhaar_card_number"],
            "right": ["marital_status", "date_of_birth", "anniversary"],
        }),
    ]

    for layout_name, cols in layouts:
        try:
            reposition_layout(layout_name, cols)
        except Exception:
            # Skip silently if layout not present
            pass


def reposition_layout(layout_name: str, cols: dict) -> None:
    layout_doc = frappe.get_doc("CRM Fields Layout", layout_name)
    if not layout_doc.layout:
        return
    data = json.loads(layout_doc.layout)
    if not isinstance(data, list) or not data:
        return

    # Helper to locate the first section containing any of the target fields
    target_fields = set(cols["left"] + cols["middle"] + cols["right"])
    target_tab = None
    target_section = None
    target_columns = None

    for tab in data:
        for section in tab.get("sections", []):
            for column in section.get("columns", []):
                fields = column.get("fields", [])
                names = [f if isinstance(f, str) else f.get("fieldname") for f in fields]
                if any(f in target_fields for f in names):
                    target_tab = tab
                    target_section = section
                    target_columns = section.get("columns", [])
                    break
            if target_section:
                break
        if target_section:
            break

    if not target_section:
        return

    # Ensure at least 3 columns present
    while len(target_columns) < 3:
        target_columns.append({"name": f"auto_col_{len(target_columns)+1}", "fields": []})

    # Build new columns strictly as per order
    left_fields = list(cols["left"]) 
    mid_fields = list(cols["middle"]) 
    right_fields = list(cols["right"]) 

    # Assign
    target_columns[0]["fields"] = left_fields
    target_columns[1]["fields"] = mid_fields
    target_columns[2]["fields"] = right_fields

    # Remove duplicates of these fields from any other columns in this section
    placed = set(left_fields + mid_fields + right_fields)
    for idx, column in enumerate(target_columns):
        if idx > 2:
            filtered = []
            for f in column.get("fields", []):
                fname = f if isinstance(f, str) else f.get("fieldname")
                if fname not in placed:
                    filtered.append(f)
            column["fields"] = filtered

    # Persist
    layout_doc.layout = json.dumps(data, indent=2)
    layout_doc.save(ignore_permissions=True)


