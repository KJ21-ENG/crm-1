import frappe
import json

def execute():
    # Get or create the fields layout
    if frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"}):
        layout = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
    else:
        layout = frappe.new_doc("CRM Fields Layout")
        layout.dt = "CRM Ticket"
        layout.type = "Quick Entry"

    # Define the new layout with contact fields in Details tab
    new_layout = [
        {
            "name": "details",
            "label": "Details",
            "sections": [
                {
                    "name": "contact_info",
                    "label": "Contact Information",
                    "columns": [
                        {
                            "name": "contact_fields",
                            "fields": [
                                "first_name",
                                "last_name",
                                "email",
                                "mobile_no"
                            ]
                        }
                    ]
                },
                {
                    "name": "ticket_info",
                    "label": "Ticket Information",
                    "columns": [
                        {
                            "name": "ticket_fields",
                            "fields": [
                                "ticket_subject",
                                "description",
                                "priority",
                                "issue_type",
                                "department",
                                "assigned_to",
                                "status"
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