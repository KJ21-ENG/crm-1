import frappe


def execute():
    """Remove Lead Expiry status from CRM Lead Status"""
    status_name = "Lead Expiry"
    
    try:
        if frappe.db.exists("CRM Lead Status", status_name):
            # Delete the status
            frappe.delete_doc("CRM Lead Status", status_name)
            frappe.logger().info(f"Successfully removed lead status: {status_name}")
        else:
            frappe.logger().info(f"Lead status '{status_name}' does not exist, nothing to remove")
    except Exception as e:
        frappe.log_error(f"Error removing lead status {status_name}: {e}")

    frappe.db.commit()
    frappe.logger().info("Lead Expiry status removal patch completed successfully")
