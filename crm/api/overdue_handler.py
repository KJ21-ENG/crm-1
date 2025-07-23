import frappe
from frappe import _
from frappe.utils import now, add_to_date, get_datetime
from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
import json


def check_and_reassign_overdue_tasks():
    """
    Check for tasks overdue by 1 hour + 30 minutes and reassign them
    This function is called by the scheduler every 5 minutes
    """
    try:
        # Calculate overdue threshold (2 minutes for testing)
        overdue_threshold = add_to_date(now(), minutes=-2)
        
        # Find overdue tasks that haven't been processed for reassignment
        overdue_tasks = frappe.get_all(
            "CRM Task",
            filters={
                "due_date": ["<=", overdue_threshold],
                "status": ["not in", ["Done", "Canceled"]],
                "reassignment_processed": ["!=", 1]  # Only unprocessed tasks
            },
            fields=[
                "name", "title", "assigned_to", "due_date", 
                "reference_doctype", "reference_docname", "priority"
            ]
        )
        
        reassigned_count = 0
        
        for task in overdue_tasks:
            try:
                # Process reassignment
                success = process_task_reassignment(task)
                if success:
                    reassigned_count += 1
                    frappe.logger().info(f"Successfully reassigned overdue task: {task.name}")
                else:
                    frappe.logger().error(f"Failed to reassign task: {task.name}")
                    
            except Exception as e:
                frappe.logger().error(f"Error reassigning task {task.name}: {str(e)}")
        
        frappe.db.commit()
        
        if reassigned_count > 0:
            frappe.logger().info(f"Reassigned {reassigned_count} overdue tasks")
        
        return {
            "success": True,
            "tasks_checked": len(overdue_tasks),
            "tasks_reassigned": reassigned_count
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in check_and_reassign_overdue_tasks: {str(e)}")
        return {"success": False, "error": str(e)}


def process_task_reassignment(task):
    """
    Process reassignment for a single overdue task
    """
    try:
        task_doc = frappe.get_doc("CRM Task", task.name)
        old_user = task_doc.assigned_to

        # Get next user via round-robin
        new_user = get_next_user_for_reassignment(task_doc)

        if not new_user:
            frappe.logger().error(f"No available user found for reassignment of task {task.name}")
            return False

        if new_user == old_user:
            frappe.logger().info(f"Same user assigned, skipping reassignment for task {task.name}")
            # Mark as processed to avoid repeated checks
            frappe.db.set_value("CRM Task", task.name, "reassignment_processed", 1)
            return True

        # 1. Cancel the old task
        frappe.db.set_value("CRM Task", task_doc.name, {"status": "Canceled", "reassignment_processed": 1})

        # 2. Create a new task with same details, assigned to new user, owner=Administrator
        new_task = frappe.get_doc({
            "doctype": "CRM Task",
            "title": task_doc.title,
            "description": task_doc.description,
            "assigned_to": new_user,
            "reference_doctype": task_doc.reference_doctype,
            "reference_docname": task_doc.reference_docname,
            "priority": task_doc.priority,
            "due_date": now(),  # Optionally set a new due date, or copy old one
            "status": "Backlog",
            "owner": "Administrator"
        })
        new_task.insert(ignore_permissions=True)

        # 3. Reassign linked lead/ticket to new user
        reassign_linked_document(new_task, new_user)

        # 4. Send notifications (reference new task)
        send_reassignment_notifications(new_task, old_user, new_user)

        # 5. Add auto-comments (reference new task)
        add_reassignment_comments(new_task, old_user, new_user)

        frappe.logger().info(f"Successfully cancelled old task {task_doc.name} and created new task {new_task.name} for reassignment.")
        return True

    except Exception as e:
        frappe.logger().error(f"Error in process_task_reassignment for task {task.name}: {str(e)}")
        return False


def get_next_user_for_reassignment(task_doc):
    """
    Get next user using round-robin logic based on task context
    """
    try:
        # Determine role based on task context
        role = determine_role_from_task(task_doc)
        
        if not role:
            frappe.logger().error(f"Could not determine role for task {task_doc.name}")
            return None
        
        # Use existing RoleAssignmentTracker
        from crm.fcrm.doctype.role_assignment_tracker.role_assignment_tracker import RoleAssignmentTracker
        
        return RoleAssignmentTracker.assign_to_next_user(
            role_name=role,
            document_type="CRM Task",
            document_name=task_doc.name
        )
        
    except Exception as e:
        frappe.logger().error(f"Error getting next user for reassignment: {str(e)}")
        return None


def determine_role_from_task(task_doc):
    """
    Determine the appropriate role for reassignment based on task context
    """
    try:
        # Default role for task reassignment
        default_role = "Sales User"
        
        # If task is linked to a lead, use lead assignment role
        if task_doc.reference_doctype == "CRM Lead":
            return "Sales User"
        
        # If task is linked to a ticket, use ticket assignment role
        elif task_doc.reference_doctype == "CRM Ticket":
            return "Support User"
        
        # For standalone tasks, use default role
        else:
            return default_role
            
    except Exception as e:
        frappe.logger().error(f"Error determining role from task: {str(e)}")
        return "Sales User"  # Fallback role


def reassign_task(task_doc, new_user):
    """
    Reassign task to new user
    """
    try:
        # Update task assignment
        frappe.db.set_value("CRM Task", task_doc.name, {
            "assigned_to": new_user,
            "modified": now()
        })
        
        # Update task's _assign field to include new user
        if not task_doc._assign:
            task_doc._assign = []
        elif isinstance(task_doc._assign, str):
            task_doc._assign = json.loads(task_doc._assign)
        
        if new_user not in task_doc._assign:
            task_doc._assign.append(new_user)
        
        frappe.db.set_value("CRM Task", task_doc.name, {
            "_assign": json.dumps(task_doc._assign)
        })
        
        # Create ToDo for new user (Frappe's assignment system)
        frappe.get_doc({
            "doctype": "ToDo",
            "description": f"Task: {task_doc.title}",
            "reference_type": "CRM Task",
            "reference_name": task_doc.name,
            "assigned_by": frappe.session.user or "Administrator",
            "owner": new_user,
            "status": "Open"
        }).insert(ignore_permissions=True)
        
        frappe.logger().info(f"Task {task_doc.name} reassigned to {new_user}")
        
    except Exception as e:
        frappe.logger().error(f"Error reassigning task {task_doc.name}: {str(e)}")
        raise


def reassign_linked_document(task_doc, new_user):
    """
    Reassign linked lead or ticket to the same user
    """
    try:
        if not task_doc.reference_doctype or not task_doc.reference_docname:
            return
        
        # Get the document to update _assign field properly
        doc = frappe.get_doc(task_doc.reference_doctype, task_doc.reference_docname)
        
        # Reassign the linked document
        if task_doc.reference_doctype == "CRM Lead":
            # Update assign_to field
            frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, {
                "assign_to": new_user,
                "last_reassignment_at": now(),
                "modified": now()
            })
            
            # Update _assign field to include new user
            if not doc._assign:
                doc._assign = []
            elif isinstance(doc._assign, str):
                doc._assign = json.loads(doc._assign)
            
            if new_user not in doc._assign:
                doc._assign.append(new_user)
            
            frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, {
                "_assign": json.dumps(doc._assign)
            })
            
        elif task_doc.reference_doctype == "CRM Ticket":
            # Update assigned_to field
            frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, {
                "assigned_to": new_user,
                "last_reassignment_at": now(),
                "modified": now()
            })
            
            # Update _assign field to include new user
            if not doc._assign:
                doc._assign = []
            elif isinstance(doc._assign, str):
                doc._assign = json.loads(doc._assign)
            
            if new_user not in doc._assign:
                doc._assign.append(new_user)
            
            frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, {
                "_assign": json.dumps(doc._assign)
            })
        
        frappe.logger().info(f"Linked {task_doc.reference_doctype} {task_doc.reference_docname} reassigned to {new_user}")
        
    except Exception as e:
        frappe.logger().error(f"Error reassigning linked document: {str(e)}")
        # Don't raise exception here to avoid breaking task reassignment


def send_reassignment_notifications(task_doc, old_user, new_user):
    """
    Send notifications for reassignment
    """
    try:
        # Notification to new user
        create_task_notification(
            task_name=task_doc.name,
            notification_type="Task Assignment",
            assigned_to=new_user,
            message=f"Task '{task_doc.title}' has been reassigned to you due to overdue",
            reference_doctype=task_doc.reference_doctype,
            reference_docname=task_doc.reference_docname
        )
        
        # Notification to old user
        create_task_notification(
            task_name=task_doc.name,
            notification_type="Overdue Task",
            assigned_to=old_user,
            message=f"Task '{task_doc.title}' has been reassigned from you due to overdue",
            reference_doctype=task_doc.reference_doctype,
            reference_docname=task_doc.reference_docname
        )
        
        frappe.logger().info(f"Sent reassignment notifications for task {task_doc.name}")
        
    except Exception as e:
        frappe.logger().error(f"Error sending reassignment notifications: {str(e)}")


def add_reassignment_comments(task_doc, old_user, new_user):
    """
    Add auto-generated comments for reassignment
    """
    try:
        # Lead/Ticket reassignment comment - focus on document reassignment, not task
        if task_doc.reference_doctype == "CRM Lead":
            reassignment_comment = f"Lead reassigned from {old_user} to {new_user} due to overdue task"
        elif task_doc.reference_doctype == "CRM Ticket":
            reassignment_comment = f"Ticket reassigned from {old_user} to {new_user} due to overdue task"
        else:
            reassignment_comment = f"Document reassigned from {old_user} to {new_user} due to overdue task"
        
        # Add comment to task's reference document (lead/ticket)
        if task_doc.reference_doctype and task_doc.reference_docname:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": task_doc.reference_doctype,
                "reference_name": task_doc.reference_docname,
                "content": reassignment_comment,
                "comment_by": "System"
            }).insert(ignore_permissions=True)
            
            frappe.logger().info(f"Added reassignment comment to {task_doc.reference_doctype} {task_doc.reference_docname}")
        
    except Exception as e:
        frappe.logger().error(f"Error adding reassignment comments: {str(e)}")


@frappe.whitelist()
def test_overdue_reassignment():
    """
    Test function to manually trigger overdue reassignment check
    """
    if not frappe.has_permission("CRM Task", "write"):
        frappe.throw(_("You don't have permission to test overdue reassignment"))
    
    result = check_and_reassign_overdue_tasks()
    return result 