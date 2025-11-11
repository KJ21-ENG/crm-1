import frappe

def execute():
    # Delete existing lead layouts
    layouts_to_delete = [
        "CRM Lead-Quick Entry",
        "CRM Lead-Side Panel",
        "CRM Lead-Data Fields"
    ]
    
    for layout in layouts_to_delete:
        if frappe.db.exists("CRM Fields Layout", layout):
            frappe.delete_doc("CRM Fields Layout", layout)
    
    # Force create new layouts
    from crm.install import add_default_fields_layout
    add_default_fields_layout(force=True) 