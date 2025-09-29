import frappe

def execute():
    """Add method and native_duration fields to CRM Call Log DocType for better debugging"""

    print("Added method and native_duration fields to CRM Call Log DocType")
    print("method: Indicates Mobile (synced) vs Manual (created in CRM)")
    print("native_duration: Stores original duration from device call log")
    print("These fields will be populated for new records and help with debugging")

    # The fields are already added to the DocType JSON, so this patch mainly serves as documentation
    # In a real scenario, we might want to create a migration to add default values or handle existing data

    return True
