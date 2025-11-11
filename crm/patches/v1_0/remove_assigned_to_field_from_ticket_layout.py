import frappe
import json

def execute():
    """Remove assigned_to field from CRM Ticket field layout"""
    
    try:
        # Get the current layout configuration
        layout_doc = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
        
        if not layout_doc:
            print("❌ No CRM Ticket layout found")
            return
            
        # Parse the current layout
        layout_config = json.loads(layout_doc.layout)
        
        # Navigate through the layout structure to find and remove assigned_to field
        for tab in layout_config:
            for section in tab.get("sections", []):
                for column in section.get("columns", []):
                    if "fields" in column:
                        # Remove assigned_to field if it exists
                        if "assigned_to" in column["fields"]:
                            column["fields"].remove("assigned_to")
                            print(f"✅ Removed assigned_to field from {section.get('name', 'unknown')} section")
        
        # Save the updated layout
        layout_doc.layout = json.dumps(layout_config, indent=2)
        layout_doc.save(ignore_permissions=True)
        
        print("✅ Successfully updated CRM Ticket field layout")
            
    except Exception as e:
        print(f"❌ Error updating CRM Ticket field layout: {str(e)}")
        frappe.log_error(f"Patch error: {str(e)}", "Remove assigned_to Field Layout Patch") 