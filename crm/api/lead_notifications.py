import frappe
from frappe import _
from frappe.utils import now, get_datetime

def create_lead_assignment_notification(lead_doc, assigned_user, tasks=None, is_reassignment=False):
    """
    Create a lead assignment notification. If tasks are involved, use Task Notification system.
    """
    try:
        if not assigned_user or assigned_user == frappe.session.user:
            return None
            
        # If there are related tasks, create a task notification for each task
        # This ensures notifications appear in Task Reminder section
        if tasks and len(tasks) > 0:
            for task in tasks:
                try:
                    task_doc = frappe.get_doc("CRM Task", task.name)
                    create_task_with_lead_notification(task_doc, lead_doc, is_assignment=True)
                except:
                    continue
        else:
            # For leads without tasks, still create a task-style notification
            # but we'll create a virtual task notification for lead assignment
            create_lead_only_task_notification(lead_doc, assigned_user, is_reassignment)
        
        frappe.logger().info(f"Lead assignment notification sent to {assigned_user} for lead {lead_doc.name}")
        return True
        
    except Exception as e:
        frappe.logger().error(f"Error creating lead assignment notification: {str(e)}")
        return None


def create_lead_only_task_notification(lead_doc, assigned_user, is_reassignment=False):
    """
    Create a task notification for lead assignment when no tasks are involved
    """
    try:
        # Create a CRM Task Notification for lead assignment
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        
        message = f"{'Lead reassigned' if is_reassignment else 'New lead assigned'}: {lead_doc.lead_name}"
        
        notification = create_task_notification(
            task_name=None,
            notification_type="Lead Assignment",
            assigned_to=assigned_user,
            message=message,
            reference_doctype="CRM Lead",
            reference_docname=lead_doc.name
        )
        
        if notification:
            # Set custom notification text with lead context
            notification_text = build_lead_assignment_notification_text(lead_doc, is_reassignment)
            notification.db_set("notification_text", notification_text)
            
            # Mark as sent to trigger real-time notification
            notification.mark_as_sent()
            
            frappe.logger().info(f"Lead assignment notification sent to {assigned_user} for lead {lead_doc.name}")
            return notification
        
    except Exception as e:
        frappe.logger().error(f"Error creating lead-only task notification: {str(e)}")
        return None


def create_task_with_lead_notification(task_doc, lead_doc, is_assignment=False):
    """
    Create a task notification that includes lead context and goes to Task Reminder section
    """
    try:
        if not task_doc.assigned_to or task_doc.assigned_to == frappe.session.user:
            return None
            
        # Use the CRM Task Notification system for task-related notifications
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        
        # Create enhanced message with lead context
        notification_type = "Task Assignment" if is_assignment else "Task Assignment"
        message = f"Task '{task_doc.title}' assigned for lead '{lead_doc.lead_name}'"
        
        # Create the task notification using the existing system
        notification = create_task_notification(
            task_name=task_doc.name,
            notification_type=notification_type,
            assigned_to=task_doc.assigned_to,
            message=message
        )
        
        if notification:
            # Set custom notification text with lead context
            notification_text = build_task_with_lead_notification_text(task_doc, lead_doc)
            notification.db_set("notification_text", notification_text)
            
            # Mark as sent to trigger real-time notification
            notification.mark_as_sent()
            
            frappe.logger().info(f"Task notification with lead context sent to {task_doc.assigned_to} for task {task_doc.name}")
            return notification
        
    except Exception as e:
        frappe.logger().error(f"Error creating task notification with lead context: {str(e)}")
        return None


def build_lead_assignment_notification_text(lead_doc, is_reassignment=False):
    """Build simple notification text for lead assignment (Task Reminder style)"""
    try:
        action = "Lead Reassigned" if is_reassignment else "New Lead Assigned"
        lead_name = lead_doc.lead_name or 'Unknown Lead'
        
        return f"""
            <div class="mb-2 leading-5">
                <div class="font-medium text-ink-gray-9">
                    {action}: {lead_name}
                </div>
            </div>
        """
        
    except Exception as e:
        frappe.logger().error(f"Error building lead assignment notification text: {str(e)}")
        return f"{action}: {lead_name}"


def build_task_with_lead_notification_text(task_doc, lead_doc):
    """Build simple notification text for task assignment with lead context"""
    try:
        lead_name = lead_doc.lead_name or 'Unknown Lead'
        task_title = task_doc.title or 'Untitled Task'
        
        return f"""
            <div class="mb-2 leading-5">
                <div class="font-medium text-ink-gray-9">
                    New Lead Assigned: {lead_name}
                </div>
                <div class="mt-1 text-sm text-ink-gray-7">
                    Task: {task_title}
                </div>
            </div>
        """
        
    except Exception as e:
        frappe.logger().error(f"Error building task notification text: {str(e)}")
        return f"New Lead Assigned: {lead_name}\nTask: {task_title}"


def handle_lead_assignment_change(lead_doc, method=None):
    """
    Handle lead assignment changes and send appropriate notifications
    """
    try:
        # Only process if lead_owner changed and exists
        if not lead_doc.lead_owner:
            return
            
        # Check if this is an assignment change (not a new lead)
        is_reassignment = False
        if method == "validate" and not lead_doc.is_new():
            old_owner = lead_doc.get_doc_before_save().lead_owner if lead_doc.get_doc_before_save() else None
            if old_owner == lead_doc.lead_owner:
                return  # No change in assignment
            is_reassignment = bool(old_owner)
        
        # Get related tasks for this lead to include in notification
        related_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "reference_doctype": "CRM Lead",
                "reference_docname": lead_doc.name,
                "status": ["not in", ["Done", "Canceled"]]
            },
            fields=["name", "title", "due_date", "priority", "assigned_to"],
            limit=5
        )
        
        # Send lead assignment notification (now goes to Task Reminder)
        create_lead_assignment_notification(
            lead_doc=lead_doc,
            assigned_user=lead_doc.lead_owner,
            tasks=related_tasks,
            is_reassignment=is_reassignment
        )
        
        frappe.logger().info(f"Lead assignment change handled for {lead_doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"Error handling lead assignment change: {str(e)}") 