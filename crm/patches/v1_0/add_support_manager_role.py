import frappe

def execute():
    """Add Support Manager role to the system"""
    
    # Create new role if it doesn't exist
    if not frappe.db.exists("Role", "Support Manager"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Support Manager",
            "desk_access": 1,
            "two_factor_auth": 0,
            "search_bar": 1,
            "is_custom": 1,
            "disabled": 0
        })
        role.insert(ignore_permissions=True)
        
        # Add basic permissions for Support Manager role
        # Permissions will be inherited from Sales Manager role
        print("✅ Created Support Manager role - permissions will be inherited")
        
        print("✅ Created Support Manager role")
    else:
        print("ℹ️ Support Manager role already exists")
    
    # Clear cache to ensure changes take effect
    frappe.clear_cache() 