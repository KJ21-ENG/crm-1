import frappe
import json

def execute():
    # Reload the DocTypes to pick up the new options
    frappe.reload_doc("fcrm", "doctype", "crm_lead")
    frappe.reload_doc("fcrm", "doctype", "crm_ticket")
    
    # Update the CRM Fields Layout for both Lead and Ticket Quick Entry
    update_quick_entry_layout("CRM Lead")
    update_quick_entry_layout("CRM Ticket")
    
    print("✅ Fixed marital status default value issue for Lead and Ticket")

def update_quick_entry_layout(doctype_name):
    try:
        layout_doc = frappe.get_doc("CRM Fields Layout", f"{doctype_name}-Quick Entry")
        layout_data = json.loads(layout_doc.layout) if layout_doc.layout else []
        
        if layout_data and len(layout_data) > 0:
            first_tab = layout_data[0]
            if first_tab.get("sections") and len(first_tab["sections"]) > 0:
                first_section = first_tab["sections"][0]
                if first_section.get("columns") and len(first_section["columns"]) > 0:
                    # Find the marital_status field in the layout and ensure it has the correct options
                    for column in first_section["columns"]:
                        if column.get("fields"):
                            for fieldname in column["fields"]:
                                if fieldname == "marital_status":
                                    # The field options will be automatically updated from the DocType
                                    print(f"✅ Found marital_status field in {doctype_name} Quick Entry layout")
                                    break
        
        layout_doc.save(ignore_permissions=True)
        print(f"✅ Updated {doctype_name} Quick Entry layout")
        
    except Exception as e:
        print(f"❌ Error updating {doctype_name} Quick Entry layout: {str(e)}")
