import frappe

def execute():
    """Update mobile number field validation for CRM Lead and CRM Ticket"""
    
    # Update CRM Lead mobile_no field
    if frappe.db.exists("DocField", {"parent": "CRM Lead", "fieldname": "mobile_no"}):
        frappe.db.set_value("DocField", 
            {"parent": "CRM Lead", "fieldname": "mobile_no"}, 
            "length", 10
        )
        frappe.db.set_value("DocField", 
            {"parent": "CRM Lead", "fieldname": "mobile_no"}, 
            "description", "Enter 10-digit mobile number only"
        )
        print("✅ Updated CRM Lead mobile_no field validation")
    
    # Update CRM Ticket mobile_no field
    if frappe.db.exists("DocField", {"parent": "CRM Ticket", "fieldname": "mobile_no"}):
        frappe.db.set_value("DocField", 
            {"parent": "CRM Ticket", "fieldname": "mobile_no"}, 
            "length", 10
        )
        frappe.db.set_value("DocField", 
            {"parent": "CRM Ticket", "fieldname": "mobile_no"}, 
            "description", "Enter 10-digit mobile number only"
        )
        print("✅ Updated CRM Ticket mobile_no field validation")
    
    # Clear cache to ensure changes are reflected
    frappe.clear_cache()
    print("✅ Mobile number validation updated successfully") 