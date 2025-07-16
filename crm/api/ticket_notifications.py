import frappe
from frappe import _
from frappe.utils import now, get_datetime

def create_ticket_assignment_notification(ticket_doc, assigned_user, tasks=None, is_reassignment=False):
    """
    Create a ticket assignment notification. If tasks are involved, use Task Notification system.
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
                    create_task_with_ticket_notification(task_doc, ticket_doc, is_assignment=True)
                except:
                    continue
        else:
            # For tickets without tasks, still create a task-style notification
            # but we'll create a virtual task notification for ticket assignment
            create_ticket_only_task_notification(ticket_doc, assigned_user, is_reassignment)
        
        frappe.logger().info(f"Ticket assignment notification sent to {assigned_user} for ticket {ticket_doc.name}")
        return True
        
    except Exception as e:
        frappe.logger().error(f"Error creating ticket assignment notification: {str(e)}")
        return None


def create_ticket_only_task_notification(ticket_doc, assigned_user, is_reassignment=False):
    """
    Create a task notification for ticket assignment when no tasks are involved
    """
    try:
        # Create a CRM Task Notification for ticket assignment
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        
        message = f"{'Ticket reassigned' if is_reassignment else 'New ticket assigned'}: {ticket_doc.ticket_subject}"
        
        notification = create_task_notification(
            task_name=None,
            notification_type="Ticket Assignment",
            assigned_to=assigned_user,
            message=message,
            reference_doctype="CRM Ticket",
            reference_docname=ticket_doc.name
        )
        
        if notification:
            # Set custom notification text with ticket context
            notification_text = build_ticket_assignment_notification_text(ticket_doc, is_reassignment)
            notification.db_set("notification_text", notification_text)
            
            # Mark as sent to trigger real-time notification
            notification.mark_as_sent()
            
            frappe.logger().info(f"Ticket assignment notification sent to {assigned_user} for ticket {ticket_doc.name}")
            return notification
        
    except Exception as e:
        frappe.logger().error(f"Error creating ticket-only task notification: {str(e)}")
        return None


def create_task_with_ticket_notification(task_doc, ticket_doc, is_assignment=False):
    """
    Create a task notification that includes ticket context and goes to Task Reminder section
    """
    try:
        if not task_doc.assigned_to or task_doc.assigned_to == frappe.session.user:
            return None
            
        # Use the CRM Task Notification system for task-related notifications
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        
        # Create enhanced message with ticket context
        notification_type = "Task Assignment" if is_assignment else "Task Assignment"
        message = f"Task '{task_doc.title}' assigned for ticket '{ticket_doc.ticket_subject}'"
        
        # Create the task notification using the existing system
        notification = create_task_notification(
            task_name=task_doc.name,
            notification_type=notification_type,
            assigned_to=task_doc.assigned_to,
            message=message
        )
        
        if notification:
            # Set custom notification text with ticket context
            notification_text = build_task_with_ticket_notification_text(task_doc, ticket_doc)
            notification.db_set("notification_text", notification_text)
            
            # Mark as sent to trigger real-time notification
            notification.mark_as_sent()
            
            frappe.logger().info(f"Task notification with ticket context sent to {task_doc.assigned_to} for task {task_doc.name}")
            return notification
        
    except Exception as e:
        frappe.logger().error(f"Error creating task notification with ticket context: {str(e)}")
        return None


def build_ticket_assignment_notification_text(ticket_doc, is_reassignment=False):
    """
    Build notification text for ticket assignments
    """
    assignment_text = "Ticket Reassigned" if is_reassignment else "New Ticket Assigned"
    
    notification_text = f"""
    <div class="mb-2 leading-5 text-ink-gray-5">
        <span class="font-medium text-ink-gray-9">{assignment_text}</span>
        <div class="mt-1">
            <span class="font-medium text-ink-gray-9">{ticket_doc.ticket_subject}</span>
            <span> has been assigned to you</span>
        </div>
        {f'<div class="text-sm text-ink-gray-6">Customer: {ticket_doc.customer_name}</div>' if ticket_doc.customer_name else ''}
        {f'<div class="text-sm text-ink-gray-6">Priority: {ticket_doc.priority}</div>' if ticket_doc.priority else ''}
        {f'<div class="text-sm text-ink-gray-6">Contact: {ticket_doc.mobile_no or ticket_doc.email or "N/A"}</div>' if (ticket_doc.mobile_no or ticket_doc.email) else ''}
    </div>
    """
    return notification_text


def build_task_with_ticket_notification_text(task_doc, ticket_doc):
    """
    Build notification text for task assignments with ticket context
    """
    notification_text = f"""
    <div class="mb-2 leading-5 text-ink-gray-5">
        <span class="font-medium text-ink-gray-9">Task Assignment</span>
        <div class="mt-1">
            <span class="font-medium text-ink-gray-9">{task_doc.title}</span>
        </div>
        <div class="text-sm text-ink-gray-6">Related to ticket: {ticket_doc.ticket_subject}</div>
        <div class="text-sm text-ink-gray-6">Customer: {ticket_doc.customer_name or 'N/A'}</div>
        {f'<div class="text-sm text-ink-gray-6">Due: {frappe.format(task_doc.due_date, "datetime")}</div>' if task_doc.due_date else ''}
        <div class="text-sm text-ink-gray-6">Priority: {task_doc.priority or 'Medium'}</div>
    </div>
    """
    return notification_text


def handle_ticket_assignment_change(ticket_doc, method=None):
    """
    Handle ticket assignment changes and send appropriate notifications
    """
    try:
        # Only process if ticket_owner changed and exists
        if not ticket_doc.ticket_owner:
            return
            
        # Check if this is an assignment change (not a new ticket)
        is_reassignment = False
        if method == "validate" and not ticket_doc.is_new():
            old_owner = ticket_doc.get_doc_before_save().ticket_owner if ticket_doc.get_doc_before_save() else None
            if old_owner == ticket_doc.ticket_owner:
                return  # No change in assignment
            is_reassignment = bool(old_owner)
        
        # Get related tasks for this ticket to include in notification
        related_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "reference_doctype": "CRM Ticket",
                "reference_docname": ticket_doc.name,
                "status": ["not in", ["Done", "Canceled"]]
            },
            fields=["name", "title", "due_date", "priority", "assigned_to"],
            limit=5
        )
        
        # Send ticket assignment notification (now goes to Task Reminder)
        create_ticket_assignment_notification(
            ticket_doc=ticket_doc,
            assigned_user=ticket_doc.ticket_owner,
            tasks=related_tasks,
            is_reassignment=is_reassignment
        )
        
        frappe.logger().info(f"Ticket assignment change handled for {ticket_doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"Error handling ticket assignment change: {str(e)}") 