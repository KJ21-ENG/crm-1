import frappe

def execute():
    # Ensure DocType is installed and seed defaults if table exists
    if not frappe.db.table_exists('CRM Account Type'):
        return
    defaults = [
        'Individual','HUF','Corporate','NRI','LLP','Minor','Partnership','Others'
    ]
    for name in defaults:
        if not frappe.db.exists('CRM Account Type', {'account_type': name}):
            doc = frappe.new_doc('CRM Account Type')
            doc.account_type = name
            doc.is_active = 1
            doc.insert(ignore_permissions=True)

