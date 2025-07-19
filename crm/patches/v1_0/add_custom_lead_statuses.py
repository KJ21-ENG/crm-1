import frappe

def execute():
    """
    Add custom lead statuses for broking business workflow
    These statuses are specific to the broking/financial services business process
    """
    
    # Define custom lead statuses for broking workflow
    custom_statuses = {
        "Follow-up Scheduled": {
            "color": "cyan",
            "position": 2,
        },
        "Follow-up Complete": {
            "color": "teal", 
            "position": 3,
        },
        "Documents Collected": {
            "color": "blue",
            "position": 4,
        },
        "Sent to Bangalore": {
            "color": "purple",
            "position": 5,
        },
        "Documents Verified": {
            "color": "amber",
            "position": 6,
        },
        "Account Opened": {
            "color": "green",
            "position": 7,
        },
        "Rejected - Follow-up Required": {
            "color": "red",
            "position": 8,
        },
        "Account Activated": {
            "color": "violet",
            "position": 9,
        },
    }

    # Add or update each custom status
    for status_name, config in custom_statuses.items():
        if frappe.db.exists("CRM Lead Status", status_name):
            # Update existing status
            doc = frappe.get_doc("CRM Lead Status", status_name)
            doc.color = config["color"]
            doc.position = config["position"]
            doc.save()
            frappe.logger().info(f"Updated existing lead status: {status_name}")
        else:
            # Add new status
            doc = frappe.new_doc("CRM Lead Status")
            doc.lead_status = status_name
            doc.color = config["color"]
            doc.position = config["position"]
            doc.insert()
            frappe.logger().info(f"Added new lead status: {status_name}")
    
    frappe.db.commit()
    frappe.logger().info("Custom lead statuses patch completed successfully") 