# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _

def execute():
    """Update CRM Lead form fields to include referral_through and account_type"""
    frappe.reload_doc("fcrm", "doctype", "crm_lead")
    
    # Update the Quick Entry form layout
    update_quick_entry_layout()
    
    # Update the Side Panel layout
    update_side_panel_layout()
    
    print("✅ Lead form fields updated successfully!")

def update_quick_entry_layout():
    """Update the Quick Entry form layout"""
    try:
        # Get the current layout
        layout_doc = frappe.get_doc("CRM Fields Layout", "CRM Lead-Quick Entry")
        
        # Parse the JSON layout
        if layout_doc.layout:
            layout_data = json.loads(layout_doc.layout)
        else:
            layout_data = []
        
        # Find the first tab and lead_source_section
        if layout_data and len(layout_data) > 0:
            first_tab = layout_data[0]
            lead_source_section = None
            
            for section in first_tab.get("sections", []):
                if section.get("name") == "lead_source_section":
                    lead_source_section = section
                    break
            
            if lead_source_section:
                # Add referral_through field after lead_category in the first column
                for column in lead_source_section.get("columns", []):
                    if column.get("name") == "column_source":
                        fields = column.get("fields", [])
                        if "lead_category" in fields:
                            # Insert referral_through after lead_category
                            lead_category_index = fields.index("lead_category")
                            fields.insert(lead_category_index + 1, "referral_through")
                            column["fields"] = fields
                            print("✅ Added referral_through to Quick Entry layout")
                            break
        
        # Update the layout
        layout_doc.layout = json.dumps(layout_data, indent=2)
        layout_doc.save(ignore_permissions=True)
        print("✅ Quick Entry layout updated")
            
    except Exception as e:
        print(f"❌ Error updating Quick Entry layout: {str(e)}")

def update_side_panel_layout():
    """Update the Side Panel layout"""
    try:
        # Get the current layout
        layout_doc = frappe.get_doc("CRM Fields Layout", "CRM Lead-Side Panel")
        
        # Parse the JSON layout
        if layout_doc.layout:
            layout_data = json.loads(layout_doc.layout)
        else:
            layout_data = []
        
        # Find the lead_details tab
        lead_details_tab = None
        for tab in layout_data:
            if tab.get("name") == "lead_details":
                lead_details_tab = tab
                break
        
        if lead_details_tab:
            # Update the lead_details column
            for column in lead_details_tab.get("columns", []):
                if column.get("name") == "column_lead_details":
                    fields = column.get("fields", [])
                    
                    # Replace referral_code with referral_through
                    if "referral_code" in fields:
                        referral_code_index = fields.index("referral_code")
                        fields[referral_code_index] = "referral_through"
                    
                    # Add account_type if not present
                    if "account_type" not in fields:
                        fields.append("account_type")
                    
                    # Remove client_id (hide it)
                    if "client_id" in fields:
                        fields.remove("client_id")
                    
                    # Remove referrer_customer (old field)
                    if "referrer_customer" in fields:
                        fields.remove("referrer_customer")
                    
                    column["fields"] = fields
                    print("✅ Updated Side Panel layout fields")
                    break
        
        # Update the layout
        layout_doc.layout = json.dumps(layout_data, indent=2)
        layout_doc.save(ignore_permissions=True)
        print("✅ Side Panel layout updated")
            
    except Exception as e:
        print(f"❌ Error updating Side Panel layout: {str(e)}") 