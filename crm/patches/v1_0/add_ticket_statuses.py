import frappe

def execute():
    """
    Add custom ticket statuses for ticket workflow
    These statuses are specific to the ticket support workflow
    """
    
    # Define custom ticket statuses for support workflow
    custom_statuses = {
        "New": {
            "color": "blue",
            "position": 1,
        },
        "Open": {
            "color": "orange",
            "position": 2,
        },
        "In Progress": {
            "color": "yellow",
            "position": 3,
        },
        "Follow-up Scheduled": {
            "color": "cyan",
            "position": 4,
        },
        "Follow-up Complete": {
            "color": "teal",
            "position": 5,
        },
        "Resolved": {
            "color": "green",
            "position": 6,
        },
        "Closed": {
            "color": "gray",
            "position": 7,
        },
    }

    # Add or update each custom status
    for status_name, config in custom_statuses.items():
        if frappe.db.exists("CRM Ticket Status", status_name):
            # Update existing status
            doc = frappe.get_doc("CRM Ticket Status", status_name)
            doc.color = config["color"]
            doc.position = config["position"]
            doc.save()
            frappe.logger().info(f"Updated existing ticket status: {status_name}")
        else:
            # Add new status
            doc = frappe.new_doc("CRM Ticket Status")
            doc.ticket_status = status_name
            doc.color = config["color"]
            doc.position = config["position"]
            doc.insert()
            frappe.logger().info(f"Added new ticket status: {status_name}")
    
    frappe.db.commit()
    frappe.logger().info("Custom ticket statuses patch completed successfully")
