import frappe
import json
from frappe.utils import now_datetime

def execute():
    """
    Add table_update_history field to existing CRM Customer records
    """
    
    # First, ensure the field exists in the DocType
    frappe.reload_doc("fcrm", "doctype", "crm_customer")
    
    # Initialize update history for existing customers
    initialize_customer_update_history()
    
    frappe.db.commit()
    print("Successfully added update history field to CRM Customer")

def initialize_customer_update_history():
    """Initialize update history for existing customers"""
    
    customers = frappe.get_list(
        "CRM Customer",
        fields=["name", "creation", "owner"],
        filters={"table_update_history": ["is", "not set"]}
    )
    
    for customer in customers:
        try:
            # Create initial history entry
            initial_history = [{
                "timestamp": customer.creation.strftime("%Y-%m-%d %H:%M:%S") if customer.creation else now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
                "user": customer.owner or "Administrator",
                "action": "Customer created (historical)",
                "changes": {}
            }]
            
            # Update the customer with initial history
            frappe.db.set_value(
                "CRM Customer",
                customer.name,
                "table_update_history",
                json.dumps(initial_history, indent=2)
            )
            
        except Exception as e:
            frappe.log_error(f"Failed to initialize history for customer {customer.name}: {str(e)}", "Customer History Init Error")
    
    print(f"Initialized update history for {len(customers)} customers") 