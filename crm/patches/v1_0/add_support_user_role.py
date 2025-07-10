import frappe

def execute():
    # Create new role if it doesn't exist
    if not frappe.db.exists("Role", "Support User"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Support User",
            "desk_access": 1,
            "two_factor_auth": 0,
            "search_bar": 1,
            "is_custom": 1,
            "disabled": 0
        })
        role.insert(ignore_permissions=True)
        
        # Add same permissions as Sales User
        doctype_permissions = [
            {"doctype": "Address", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 0},
            {"doctype": "Contact", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 0},
            {"doctype": "CRM Call Log", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Communication Status", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Deal", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Deal Status", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Global Settings", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Holiday List", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Industry", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Invitation", "permlevel": 0, "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Lead", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Lead Source", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Lead Status", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Notification", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Organization", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Task", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM Territory", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "CRM View Settings", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1},
            {"doctype": "Currency", "permlevel": 0, "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "report": 0, "export": 0},
            {"doctype": "FCRM Note", "permlevel": 0, "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1}
        ]
        
        # Add permissions for each doctype
        for perm in doctype_permissions:
            doc = frappe.get_doc({
                "doctype": "DocPerm",
                "role": "Support User",
                "parent": perm["doctype"],
                "parenttype": "DocType",
                "parentfield": "permissions",
                "permlevel": perm["permlevel"],
                "read": perm["read"],
                "write": perm["write"],
                "create": perm["create"],
                "delete": perm["delete"],
                "submit": perm["submit"],
                "cancel": perm["cancel"],
                "amend": perm["amend"],
                "report": perm["report"],
                "export": perm["export"]
            })
            doc.insert(ignore_permissions=True) 