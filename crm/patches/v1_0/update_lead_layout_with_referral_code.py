import frappe
import json

def execute():
    """Update CRM Lead Quick Entry layout to include referral_code field"""
    
    # Get the existing layout
    layout_doc = frappe.get_doc("CRM Fields Layout", "CRM Lead-Quick Entry")
    
    if layout_doc.layout:
        layout = frappe.parse_json(layout_doc.layout)
        
        # Find the lead_source_section and add referral_code field
        for tab in layout:
            for section in tab.get("sections", []):
                if section.get("name") == "lead_source_section":
                    for column in section.get("columns", []):
                        if column.get("name") == "column_source":
                            # Add referral_code to the fields array
                            if "referral_code" not in column.get("fields", []):
                                column["fields"].append("referral_code")
                                print("✅ Added referral_code to lead_source_section")
                            else:
                                print("ℹ️ referral_code already exists in lead_source_section")
                            break
        
        # Update the layout
        layout_doc.layout = json.dumps(layout, indent=2)
        layout_doc.save()
        print("✅ Updated CRM Lead Quick Entry layout")
    else:
        print("⚠️ No existing layout found for CRM Lead Quick Entry") 