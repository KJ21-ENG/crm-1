# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _

def execute():
    """Fix missing referral fields in CRM Lead Quick Entry modal"""
    
    print("🔧 Fixing missing referral fields in Create Lead modal...")
    
    try:
        # Get the current layout
        layout_doc = frappe.get_doc("CRM Fields Layout", "CRM Lead-Quick Entry")
        
        if layout_doc.layout:
            # Parse the current layout
            layout_data = json.loads(layout_doc.layout)
            
            # Find the lead_source_section and update it
            for tab in layout_data:
                for section in tab.get("sections", []):
                    if section.get("name") == "lead_source_section":
                        for column in section.get("columns", []):
                            if column.get("name") == "column_source":
                                # Replace referral_code with referral_through and add lead_category
                                fields = column.get("fields", [])
                                
                                # Remove old referral_code field if it exists
                                if "referral_code" in fields:
                                    fields.remove("referral_code")
                                    print("✅ Removed old referral_code field")
                                
                                # Add lead_category if not present
                                if "lead_category" not in fields:
                                    # Insert after lead_source
                                    if "lead_source" in fields:
                                        lead_source_index = fields.index("lead_source")
                                        fields.insert(lead_source_index + 1, "lead_category")
                                    else:
                                        fields.insert(0, "lead_category")
                                    print("✅ Added lead_category field")
                                
                                # Add referral_through if not present
                                if "referral_through" not in fields:
                                    # Insert after lead_category
                                    if "lead_category" in fields:
                                        lead_category_index = fields.index("lead_category")
                                        fields.insert(lead_category_index + 1, "referral_through")
                                    else:
                                        fields.append("referral_through")
                                    print("✅ Added referral_through field")
                                
                                column["fields"] = fields
                                break
                        
                        # Update the layout
                        layout_doc.layout = json.dumps(layout_data, indent=2)
                        layout_doc.save(ignore_permissions=True)
                        print("✅ Updated CRM Lead Quick Entry layout with referral fields")
                        break
            else:
                print("⚠️ Could not find lead_source_section in layout")
        else:
            print("⚠️ No existing layout found for CRM Lead Quick Entry")
            
    except Exception as e:
        print(f"❌ Error updating field layout: {str(e)}")
        frappe.log_error(f"Error updating CRM Lead field layout: {str(e)}")

def rollback():
    """Rollback the changes if needed"""
    try:
        # Restore the original layout (if we have a backup)
        print("🔄 Rolling back field layout changes...")
        
        # For now, just log the rollback attempt
        print("ℹ️ Rollback functionality not implemented - manual intervention required")
        
    except Exception as e:
        print(f"❌ Error during rollback: {str(e)}") 