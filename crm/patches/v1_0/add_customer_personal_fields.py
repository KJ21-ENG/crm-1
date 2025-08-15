import frappe
import json

def execute():
    # Reload the Customer DocType to pick up the new fields
    frappe.reload_doc("fcrm", "doctype", "crm_customer")
    
    # Update the CRM Fields Layout for Customer forms
    update_customer_layouts()
    
    print("✅ Added personal fields to Customer forms")

def update_customer_layouts():
    try:
        # Update Customer Quick Entry layout if it exists
        try:
            quick_entry_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Quick Entry")
            update_layout_with_personal_fields(quick_entry_layout, "Quick Entry")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Quick Entry layout not found, skipping...")
        
        # Update Customer Side Panel layout if it exists
        try:
            side_panel_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Side Panel")
            update_layout_with_personal_fields(side_panel_layout, "Side Panel")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Side Panel layout not found, skipping...")
        
        # Update Customer Full Form layout if it exists
        try:
            full_form_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Full Form")
            update_layout_with_personal_fields(full_form_layout, "Full Form")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Full Form layout not found, skipping...")
            
    except Exception as e:
        print(f"❌ Error updating Customer layouts: {str(e)}")

def update_layout_with_personal_fields(layout_doc, layout_type):
    try:
        layout_data = json.loads(layout_doc.layout) if layout_doc.layout else []
        
        if layout_data and len(layout_data) > 0:
            first_tab = layout_data[0]
            if first_tab.get("sections") and len(first_tab["sections"]) > 0:
                first_section = first_tab["sections"][0]
                if first_section.get("columns") and len(first_section["columns"]) > 0:
                    # Find the first column and add personal fields after gender
                    first_column = first_section["columns"][0]
                    fields = first_column.get("fields", [])
                    
                    # Add personal fields after gender if not already present
                    gender_index = -1
                    if "gender" in fields:
                        gender_index = fields.index("gender")
                    
                    new_fields_to_add = ["marital_status", "date_of_birth", "anniversary"]
                    current_index = gender_index + 1
                    
                    for fieldname in new_fields_to_add:
                        if fieldname not in fields:
                            fields.insert(current_index, fieldname)
                            current_index += 1
                    
                    first_column["fields"] = fields
                    layout_doc.layout = json.dumps(layout_data, indent=2)
                    layout_doc.save(ignore_permissions=True)
                    print(f"✅ Updated CRM Customer-{layout_type} layout for personal fields")
                    
    except Exception as e:
        print(f"❌ Error updating CRM Customer-{layout_type} layout: {str(e)}")
