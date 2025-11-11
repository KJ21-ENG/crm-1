import frappe


def execute():
    """Add Lead Expired status with unique pink color"""
    status_name = "Lead Expired"
    
    try:
        if frappe.db.exists("CRM Lead Status", status_name):
            # Update existing status
            doc = frappe.get_doc("CRM Lead Status", status_name)
            doc.color = "pink"
            doc.position = 12  # Position after existing statuses
            doc.save()
            frappe.logger().info(f"Updated existing lead status: {status_name}")
        else:
            # Add new status
            doc = frappe.new_doc("CRM Lead Status")
            doc.lead_status = status_name
            doc.color = "pink"
            doc.position = 12  # Position after existing statuses
            doc.insert()
            frappe.logger().info(f"Added new lead status: {status_name}")
    except Exception as e:
        frappe.log_error(f"Error adding/updating lead status {status_name}: {e}")

    frappe.db.commit()
    frappe.logger().info("Lead Expired status patch completed successfully")
