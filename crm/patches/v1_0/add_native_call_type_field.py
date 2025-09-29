import frappe

def execute():
    """Add native_call_type field to CRM Call Log DocType for debugging purposes"""

    # This patch ensures the native_call_type field exists in the DocType
    # Existing records won't have this field populated since it wasn't stored before
    # New records from the mobile app will populate this field for debugging

    print("Added native_call_type field to CRM Call Log DocType")
    print("This field will store the original call type from device call logs")
    print("Useful for debugging discrepancies between native call logs and CRM processing")

    # The field is already added to the DocType JSON, so this patch mainly serves as documentation
    # In a real scenario, we might want to create a migration to add default values or handle existing data

    return True

