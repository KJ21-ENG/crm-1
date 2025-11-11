import frappe

def execute():
    """
    Add final_overdue and final_overdue_task fields to CRM Task, CRM Lead, and CRM Ticket DocTypes
    """
    frappe.logger().info("🔧 Adding final overdue fields to CRM DocTypes...")
    
    # Add final_overdue field to CRM Task
    try:
        if not frappe.db.exists("Custom Field", "CRM Task-final_overdue"):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "CRM Task",
                "fieldname": "final_overdue",
                "label": "Final Overdue",
                "fieldtype": "Check",
                "default": 0,
                "description": "Indicates if this task has been marked as final overdue and reassigned to all available users",
                "insert_after": "status"
            }).insert()
            frappe.logger().info("✅ Added final_overdue field to CRM Task")
        else:
            frappe.logger().info("ℹ️ final_overdue field already exists in CRM Task")
    except Exception as e:
        frappe.logger().error(f"❌ Error adding final_overdue field to CRM Task: {str(e)}")
    
    # Add final_overdue_task field to CRM Lead
    try:
        if not frappe.db.exists("Custom Field", "CRM Lead-final_overdue_task"):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "CRM Lead",
                "fieldname": "final_overdue_task",
                "label": "Final Overdue Task",
                "fieldtype": "Link",
                "options": "CRM Task",
                "description": "Reference to the task that was marked as final overdue for this lead",
                "insert_after": "assigned_to"
            }).insert()
            frappe.logger().info("✅ Added final_overdue_task field to CRM Lead")
        else:
            frappe.logger().info("ℹ️ final_overdue_task field already exists in CRM Lead")
    except Exception as e:
        frappe.logger().error(f"❌ Error adding final_overdue_task field to CRM Lead: {str(e)}")
    
    # Add final_overdue_task field to CRM Ticket
    try:
        if not frappe.db.exists("Custom Field", "CRM Ticket-final_overdue_task"):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "CRM Ticket",
                "fieldname": "final_overdue_task",
                "label": "Final Overdue Task",
                "fieldtype": "Link",
                "options": "CRM Task",
                "description": "Reference to the task that was marked as final overdue for this ticket",
                "insert_after": "assigned_to"
            }).insert()
            frappe.logger().info("✅ Added final_overdue_task field to CRM Ticket")
        else:
            frappe.logger().info("ℹ️ final_overdue_task field already exists in CRM Ticket")
    except Exception as e:
        frappe.logger().error(f"❌ Error adding final_overdue_task field to CRM Ticket: {str(e)}")
    
    frappe.logger().info("✅ Final overdue fields added successfully!") 