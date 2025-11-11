import frappe
import json

def execute():
    # Reload the Customer DocType to pick up the field changes
    frappe.reload_doc("fcrm", "doctype", "crm_customer")
    
    # Update the CRM Fields Layout for Customer forms
    update_customer_layouts()
    
    print("✅ Updated Customer personal fields - removed gender, added empty marital status option")

def update_customer_layouts():
    try:
        # Update Customer Quick Entry layout if it exists
        try:
            quick_entry_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Quick Entry")
            update_layout_with_updated_fields(quick_entry_layout, "Quick Entry")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Quick Entry layout not found, skipping...")
        
        # Update Customer Side Panel layout if it exists
        try:
            side_panel_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Side Panel")
            update_layout_with_updated_fields(side_panel_layout, "Side Panel")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Side Panel layout not found, skipping...")
        
        # Update Customer Full Form layout if it exists
        try:
            full_form_layout = frappe.get_doc("CRM Fields Layout", "CRM Customer-Full Form")
            update_layout_with_updated_fields(full_form_layout, "Full Form")
        except frappe.DoesNotExistError:
            print("ℹ️ CRM Customer-Full Form layout not found, skipping...")
            
    except Exception as e:
        print(f"❌ Error updating Customer layouts: {str(e)}")

def update_layout_with_updated_fields(layout_doc, layout_type):
    try:
        layout_data = json.loads(layout_doc.layout) if layout_doc.layout else []
        
        if layout_data and len(layout_data) > 0:
            first_tab = layout_data[0]
            if first_tab.get("sections") and len(first_tab["sections"]) > 0:
                first_section = first_tab["sections"][0]
                if first_section.get("columns") and len(first_section["columns"]) > 0:
                    # Find the first column and update fields
                    first_column = first_section["columns"][0]
                    fields = first_column.get("fields", [])
                    
                    # Remove gender field if it exists
                    if "gender" in fields:
                        fields.remove("gender")
                        print(f"✅ Removed gender field from CRM Customer-{layout_type}")
                    
                    # Ensure personal fields are in correct order
                    personal_fields = ["marital_status", "date_of_birth", "anniversary"]
                    current_index = 0
                    
                    # Find where to insert personal fields (after salutation if it exists)
                    if "salutation" in fields:
                        current_index = fields.index("salutation") + 1
                    
                    # Add personal fields if not already present
                    for fieldname in personal_fields:
                        if fieldname not in fields:
                            fields.insert(current_index, fieldname)
                            current_index += 1
                    
                    first_column["fields"] = fields
                    layout_doc.layout = json.dumps(layout_data, indent=2)
                    layout_doc.save(ignore_permissions=True)
                    print(f"✅ Updated CRM Customer-{layout_type} layout with updated personal fields")
                    
    except Exception as e:
        print(f"❌ Error updating CRM Customer-{layout_type} layout: {str(e)}")
