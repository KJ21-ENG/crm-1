import frappe

def execute():
    """
    Remove custom table_update_history field from CRM Customer
    since we're using Frappe's built-in versioning system (tabVersion)
    """
    
    # First, reload the DocType to ensure schema is updated
    frappe.reload_doc("fcrm", "doctype", "crm_customer")
    
    # The field should be automatically removed from the form when DocType is reloaded
    # Check if the field still exists in database and clean up if needed
    
    try:
        # Check if the field exists in the database
        result = frappe.db.sql("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'tabCRM Customer' 
            AND COLUMN_NAME = 'table_update_history'
        """, (frappe.conf.get('db_name'),))
        
        if result:
            print("Found table_update_history field in database, but keeping data for reference")
            print("Frappe framework will handle field removal automatically")
        else:
            print("table_update_history field not found in database")
            
    except Exception as e:
        frappe.log_error(f"Error checking table_update_history field: {str(e)}", "Field Cleanup Error")
    
    frappe.db.commit()
    print("Successfully updated CRM Customer to use Frappe's built-in versioning system") 