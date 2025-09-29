import frappe
import json

def execute():
    filters = {
        "dt": "CRM Lead",
        "type": "Quick Entry"
    }

    # get the name and layout column
    record = frappe.get_value("CRM Fields Layout", filters, ["name", "layout"], as_dict=True)
    if not record:
        frappe.log_error("No CRM Fields Layout record found for CRM Lead Quick Entry", "Patch Error")
        return

    try:
        layout = json.loads(record.layout)
    except Exception:
        frappe.log_error("Invalid JSON in layout for CRM Lead Quick Entry", "Patch Error")
        return

    modified = False

    # Go through sections → contact_information → contact_col_1
    for section in layout[0].get("sections", []):
        if section.get("name") == "contact_information":
            for column in section.get("columns", []):
                if column.get("name") == "contact_col_1":
                    fields = column.get("fields", [])
                    if "alternative_mobile_no" not in fields:
                        fields.append("alternative_mobile_no")
                        column["fields"] = fields
                        modified = True
            break  # no need to loop further

    if modified:
        frappe.db.set_value("CRM Fields Layout", record.name, "layout", json.dumps(layout))
        frappe.db.commit()
        frappe.msgprint("Added 'alternative_mobile_no' to Quick Entry layout for CRM Lead")
    else:
        frappe.msgprint("'alternative_mobile_no' already present in Quick Entry layout for CRM Lead")
