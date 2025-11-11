import json
import frappe


def execute():
    """Update CRM Lead Quick Entry layout to a 3-column aligned layout similar to Ticket."""
    layout = (
        frappe.get_doc("CRM Fields Layout", {"dt": "CRM Lead", "type": "Quick Entry"})
        if frappe.db.exists("CRM Fields Layout", {"dt": "CRM Lead", "type": "Quick Entry"})
        else frappe.new_doc("CRM Fields Layout")
    )

    layout.dt = "CRM Lead"
    layout.type = "Quick Entry"

    new_layout = [
        {
            "name": "details",
            "label": "Details",
            "sections": [
                {
                    "name": "contact_information",
                    "label": "Contact Information",
                    "columns": [
                        {"name": "contact_col_1", "fields": ["first_name", "last_name", "pan_card_number"]},
                        {"name": "contact_col_2", "fields": ["email", "mobile_no", "aadhaar_card_number"]},
                        {"name": "contact_col_3", "fields": ["marital_status", "date_of_birth", "anniversary"]},
                    ],
                },
                {
                    "name": "lead_information",
                    "label": "Lead Information",
                    "columns": [
                        {"name": "lead_col_1", "fields": ["lead_source", "lead_category", "referral_through"]},
                        {"name": "lead_col_2", "fields": ["client_id", "description", "status"]},
                        {"name": "lead_col_3", "fields": ["account_type", "lead_owner", "assign_to_role"]},
                    ],
                },
            ],
        }
    ]

    layout.layout = json.dumps(new_layout)
    layout.save(ignore_permissions=True)
    frappe.db.commit()


