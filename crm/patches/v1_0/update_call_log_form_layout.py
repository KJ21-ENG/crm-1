import frappe
import json

def execute():
    """Update CRM Call Log Quick Entry form layout to use employee/customer fields"""
    
    # Get or create the fields layout
    if frappe.db.exists("CRM Fields Layout", {"dt": "CRM Call Log", "type": "Quick Entry"}):
        layout = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Call Log", "type": "Quick Entry"})
    else:
        layout = frappe.new_doc("CRM Fields Layout")
        layout.dt = "CRM Call Log"
        layout.type = "Quick Entry"

    # Define the new layout with employee and customer fields
    new_layout = [
        {
            "name": "details_section",
            "label": "Call Details",
            "sections": [
                {
                    "name": "call_info",
                    "label": "Call Information",
                    "columns": [
                        {
                            "name": "column_call_type",
                            "fields": [
                                "type",
                                "status",
                                "duration"
                            ]
                        },
                        {
                            "name": "column_participants",
                            "fields": [
                                "employee",
                                "customer",
                                "customer_name"
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    # Update the layout
    layout.layout = json.dumps(new_layout)
    layout.save(ignore_permissions=True)

    frappe.db.commit()
    
    print("✅ Updated CRM Call Log Quick Entry form layout to use employee/customer fields") 