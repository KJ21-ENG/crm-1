import frappe
from frappe import _
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


def create_lead_assignment_notification(lead_doc, assigned_to, assignment_type="assigned"):
    """
    Create a notification when a lead is assigned to a user.
    
    Args:
        lead_doc: CRM Lead document
        assigned_to: User who is being assigned
        assignment_type: 'assigned' for new assignment, 'reassigned' for changed assignment
    """
    if not assigned_to or assigned_to == frappe.session.user:
        return
    
    # Check for any tasks associated with this lead
    tasks = frappe.get_all(
        "CRM Task",
        filters={
            "reference_doctype": "CRM Lead",
            "reference_docname": lead_doc.name,
            "status": ["not in", ["Done", "Canceled"]],
            "assigned_to": assigned_to
        },
        fields=["name", "title", "due_date", "priority", "status"],
        order_by="creation desc"
    )
    
    # Build notification message based on lead and task info
    lead_name = lead_doc.lead_name or lead_doc.first_name or "Lead"
    lead_info = f"{lead_name}"
    if lead_doc.organization:
        lead_info += f" ({lead_doc.organization})"
    
    # Base notification message
    if assignment_type == "reassigned":
        notification_text = f"🔄 Lead '{lead_info}' has been reassigned to you"
    else:
        notification_text = f"🎯 New lead '{lead_info}' has been assigned to you"
    
    # Add task information if any tasks exist
    if tasks:
        if len(tasks) == 1:
            task = tasks[0]
            notification_text += f"\n\n📋 Related Task: '{task.title}'"
            if task.due_date:
                notification_text += f" (Due: {frappe.format(task.due_date, 'datetime')})"
            notification_text += f" - Priority: {task.priority}"
        else:
            notification_text += f"\n\n📋 {len(tasks)} related tasks assigned:"
            for task in tasks[:3]:  # Show max 3 tasks
                notification_text += f"\n• {task.title}"
                if task.due_date:
                    notification_text += f" (Due: {frappe.format(task.due_date, 'datetime')})"
            if len(tasks) > 3:
                notification_text += f"\n• ...and {len(tasks) - 3} more tasks"
    
    # Add lead details
    notification_text += f"\n\n📞 Contact:"
    if lead_doc.mobile_no:
        notification_text += f"\nMobile: {lead_doc.mobile_no}"
    if lead_doc.email:
        notification_text += f"\nEmail: {lead_doc.email}"
    if lead_doc.lead_source:
        notification_text += f"\nSource: {lead_doc.lead_source}"
    
    # Create the notification using existing CRM notification system
    try:
        notify_user({
            "owner": frappe.session.user,
            "assigned_to": assigned_to,
            "notification_type": "Assignment",
            "message": notification_text,
            "notification_text": notification_text,
            "reference_doctype": "CRM Lead",
            "reference_docname": lead_doc.name,
            "redirect_to_doctype": "CRM Lead",
            "redirect_to_docname": lead_doc.name,
        })
        
        frappe.logger().info(f"✅ Enhanced lead assignment notification sent to {assigned_to} for lead {lead_doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"❌ Failed to send lead assignment notification: {str(e)}")
        frappe.log_error(f"Lead notification error: {str(e)}")


def handle_lead_assignment_change(lead_doc, method=None):
    """
    Handle lead assignment changes and send notifications accordingly.
    This function is called from lead hooks.
    
    Args:
        lead_doc: CRM Lead document
        method: The method that triggered this (after_insert, validate, etc.)
    """
    
    # For new leads (after_insert)
    if method == "after_insert" and lead_doc.lead_owner:
        create_lead_assignment_notification(
            lead_doc, 
            lead_doc.lead_owner, 
            assignment_type="assigned"
        )
        return
    
    # For existing leads (validate/on_update)
    if method == "validate" and not lead_doc.is_new():
        if lead_doc.has_value_changed("lead_owner") and lead_doc.lead_owner:
            # Lead owner changed - send reassignment notification
            create_lead_assignment_notification(
                lead_doc, 
                lead_doc.lead_owner, 
                assignment_type="reassigned"
            )
        return


def create_task_with_lead_notification(task_doc, lead_doc):
    """
    Create a combined notification when a task is created for an assigned lead.
    This provides context about the lead assignment along with the task.
    
    Args:
        task_doc: CRM Task document
        lead_doc: CRM Lead document
    """
    if not task_doc.assigned_to or task_doc.assigned_to == frappe.session.user:
        return
    
    lead_name = lead_doc.lead_name or lead_doc.first_name or "Lead"
    lead_info = f"{lead_name}"
    if lead_doc.organization:
        lead_info += f" ({lead_doc.organization})"
    
    # Build comprehensive notification
    notification_text = f"📋 New task assigned for lead '{lead_info}'"
    notification_text += f"\n\nTask: '{task_doc.title}'"
    if task_doc.description:
        notification_text += f"\nDescription: {task_doc.description[:100]}..."
    if task_doc.due_date:
        notification_text += f"\nDue Date: {frappe.format(task_doc.due_date, 'datetime')}"
    notification_text += f"\nPriority: {task_doc.priority}"
    
    # Add lead context
    notification_text += f"\n\n📞 Lead Contact:"
    if lead_doc.mobile_no:
        notification_text += f"\nMobile: {lead_doc.mobile_no}"
    if lead_doc.email:
        notification_text += f"\nEmail: {lead_doc.email}"
    if lead_doc.lead_source:
        notification_text += f"\nSource: {lead_doc.lead_source}"
    
    try:
        notify_user({
            "owner": frappe.session.user,
            "assigned_to": task_doc.assigned_to,
            "notification_type": "Task",
            "message": notification_text,
            "notification_text": notification_text,
            "reference_doctype": "CRM Task",
            "reference_docname": task_doc.name,
            "redirect_to_doctype": "CRM Lead",
            "redirect_to_docname": lead_doc.name,
        })
        
        frappe.logger().info(f"✅ Combined task-lead notification sent to {task_doc.assigned_to} for task {task_doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"❌ Failed to send task-lead notification: {str(e)}")
        frappe.log_error(f"Task-lead notification error: {str(e)}") 