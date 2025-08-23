# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch: Add POD ID field to CRM Lead doctype
Version: 1.0.0
Description: Adds a new POD ID field to track Proof of Delivery IDs for leads
"""

import frappe
from frappe import _

def execute():
    """Execute the patch to add POD ID field"""
    
    try:
        # Check if the field already exists
        if frappe.db.exists("Custom Field", {"dt": "CRM Lead", "fieldname": "pod_id"}):
            print("POD ID field already exists in CRM Lead doctype")
            return
        
        # Create the POD ID custom field
        pod_id_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "CRM Lead",
            "fieldname": "pod_id",
            "label": "POD ID",
            "fieldtype": "Data",
            "description": "Proof of Delivery ID - can be same for multiple leads",
            "in_list_view": 1,
            "search_index": 1,
            "insert_after": "client_id",
            "owner": "Administrator"
        })
        
        pod_id_field.insert(ignore_permissions=True)
        
        # Update the field order in the doctype
        update_field_order()
        
        print("✅ POD ID field added successfully to CRM Lead doctype")
        
    except Exception as e:
        print(f"❌ Error adding POD ID field: {str(e)}")
        frappe.log_error(f"Patch v1_add_pod_id_field failed: {str(e)}")
        raise

def update_field_order():
    """Update the field order to include POD ID after client_id"""
    try:
        # Get the current field order
        doctype = frappe.get_doc("DocType", "CRM Lead")
        
        # Find the index of client_id
        client_id_index = None
        for i, field in enumerate(doctype.fields):
            if field.fieldname == "client_id":
                client_id_index = i
                break
        
        if client_id_index is not None:
            # Insert POD ID after client_id
            pod_id_field = {
                "fieldname": "pod_id",
                "label": "POD ID",
                "fieldtype": "Data",
                "description": "Proof of Delivery ID - can be same for multiple leads",
                "in_list_view": 1,
                "search_index": 1
            }
            
            # Insert the field at the correct position
            doctype.fields.insert(client_id_index + 1, pod_id_field)
            doctype.save(ignore_permissions=True)
            
            print("✅ Field order updated successfully")
        else:
            print("⚠️ client_id field not found, field order not updated")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not update field order: {str(e)}")
        # Don't fail the patch if field order update fails
        pass

def rollback():
    """Rollback the patch by removing the POD ID field"""
    try:
        # Remove the custom field if it exists
        custom_field = frappe.db.get_value("Custom Field", {"dt": "CRM Lead", "fieldname": "pod_id"})
        if custom_field:
            frappe.delete_doc("Custom Field", custom_field, ignore_permissions=True)
            print("✅ POD ID field removed successfully")
        else:
            print("POD ID field not found for rollback")
            
    except Exception as e:
        print(f"❌ Error during rollback: {str(e)}")
        frappe.log_error(f"Patch v1_add_pod_id_field rollback failed: {str(e)}")
