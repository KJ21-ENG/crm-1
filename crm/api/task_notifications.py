import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_to_date
from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification


@frappe.whitelist()
def get_task_notifications():
    """Get task notifications for current user"""
    try:
        notifications = frappe.get_list(
            "CRM Task Notification",
            filters={
                "assigned_to": frappe.session.user,
                "status": ["in", ["Sent", "Read"]]
            },
            fields=[
                "name", "task", "notification_type", "status", 
                "message", "notification_text", "sent_at", "read_at"
            ],
            order_by="sent_at desc",
            limit=20
        )
        
        # Enhance with task details
        for notification in notifications:
            if notification.task:
                try:
                    task = frappe.get_doc("CRM Task", notification.task)
                    notification.task_title = task.title
                    notification.task_status = task.status
                    notification.task_priority = task.priority
                    notification.reference_doctype = task.reference_doctype
                    notification.reference_docname = task.reference_docname
                    
                    # Format timestamps
                    if notification.sent_at:
                        notification.sent_at_formatted = frappe.format(notification.sent_at, {"fieldtype": "Datetime"})
                    if notification.read_at:
                        notification.read_at_formatted = frappe.format(notification.read_at, {"fieldtype": "Datetime"})
                        
                except Exception as e:
                    frappe.logger().error(f"Error getting task details for notification {notification.name}: {str(e)}")
        
        return notifications
    except Exception as e:
        frappe.logger().error(f"Error getting task notifications: {str(e)}")
        return []


@frappe.whitelist()
def mark_notification_read(notification_name):
    """Mark a specific notification as read"""
    try:
        notification = frappe.get_doc("CRM Task Notification", notification_name)
        
        # Verify the notification belongs to current user
        if notification.assigned_to != frappe.session.user:
            frappe.throw(_("You can only mark your own notifications as read"))
        
        notification.mark_as_read()
        return {"success": True}
    except Exception as e:
        frappe.logger().error(f"Error marking notification as read: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    try:
        notifications = frappe.get_list(
            "CRM Task Notification",
            filters={
                "assigned_to": frappe.session.user,
                "status": "Sent"
            },
            fields=["name"]
        )
        
        for notification in notifications:
            frappe.db.set_value("CRM Task Notification", notification.name, {
                "status": "Read",
                "read_at": now()
            })
        
        frappe.db.commit()
        return {"success": True, "count": len(notifications)}
    except Exception as e:
        frappe.logger().error(f"Error marking all notifications as read: {str(e)}")
        return {"success": False, "error": str(e)}


def check_and_send_task_notifications():
    """
    Background function to check for tasks needing notifications
    This function should be called every 5 seconds by the scheduler
    """
    try:
        current_time = get_datetime(now())
        
        # Get tasks where notification_time has passed and notification not sent
        tasks_to_notify = frappe.get_list(
            "CRM Task",
            filters={
                "notification_time": ["<=", current_time],
                "notification_status": "Not Sent",
                "assigned_to": ["!=", ""],
                "status": ["not in", ["Done", "Canceled"]],
                "due_date": ["is", "set"]
            },
            fields=["name", "title", "assigned_to", "due_date", "notification_time", "status", "priority"]
        )
        
        notifications_sent = 0
        
        for task in tasks_to_notify:
            try:
                # Create due date reminder notification
                notification = create_task_notification(
                    task_name=task.name,
                    notification_type="Due Date Reminder",
                    assigned_to=task.assigned_to,
                    message=f"Task '{task.title}' is due in 5 minutes"
                )
                
                if notification:
                    # Mark notification as sent
                    notification.mark_as_sent()
                    
                    # Update task notification status
                    frappe.db.set_value("CRM Task", task.name, "notification_status", "Sent")
                    
                    notifications_sent += 1
                    
                    frappe.logger().info(f"Sent task notification for task {task.name} to {task.assigned_to}")
                
            except Exception as e:
                frappe.logger().error(f"Error sending notification for task {task.name}: {str(e)}")
        
        # Check for overdue tasks (1 hour after due time)
        overdue_time = add_to_date(current_time, hours=-1)
        overdue_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "due_date": ["<=", overdue_time],
                "status": ["not in", ["Done", "Canceled"]],
                "assigned_to": ["!=", ""]
            },
            fields=["name", "title", "assigned_to", "due_date"]
        )
        
        for task in overdue_tasks:
            try:
                # Check if overdue notification already sent today
                existing_overdue = frappe.db.exists("CRM Task Notification", {
                    "task": task.name,
                    "notification_type": "Overdue Task",
                    "assigned_to": task.assigned_to,
                    "creation": [">=", frappe.utils.today()]
                })
                
                if not existing_overdue:
                    notification = create_task_notification(
                        task_name=task.name,
                        notification_type="Overdue Task",
                        assigned_to=task.assigned_to,
                        message=f"Task '{task.title}' is overdue"
                    )
                    
                    if notification:
                        notification.mark_as_sent()
                        notifications_sent += 1
                        
                        frappe.logger().info(f"Sent overdue notification for task {task.name} to {task.assigned_to}")
                
            except Exception as e:
                frappe.logger().error(f"Error sending overdue notification for task {task.name}: {str(e)}")
        
        # Commit all changes
        frappe.db.commit()
        
        if notifications_sent > 0:
            frappe.logger().info(f"Task notification check completed. Sent {notifications_sent} notifications.")
        
        return {
            "success": True,
            "notifications_sent": notifications_sent,
            "tasks_checked": len(tasks_to_notify) + len(overdue_tasks)
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in check_and_send_task_notifications: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def test_notification_system():
    """Test function to manually trigger notification check"""
    if not frappe.has_permission("CRM Task", "write"):
        frappe.throw(_("You don't have permission to test notifications"))
    
    result = check_and_send_task_notifications()
    return result


@frappe.whitelist()
def create_test_task_notification():
    """Create a test notification for current user (for testing purposes)"""
    if not frappe.has_permission("CRM Task", "write"):
        frappe.throw(_("You don't have permission to create test notifications"))
    
    try:
        # Create a test notification
        notification = frappe.get_doc({
            "doctype": "CRM Task Notification",
            "task": "",  # Empty for test
            "notification_type": "Task Assignment",
            "assigned_to": frappe.session.user,
            "message": "This is a test notification",
            "notification_text": """
                <div class="mb-2 leading-5 text-ink-gray-5">
                    <span class="font-medium text-ink-gray-9">Test Notification</span>
                    <div class="mt-1">
                        <span>This is a test notification to verify the system is working</span>
                    </div>
                </div>
            """,
            "status": "Pending"
        })
        
        notification.insert(ignore_permissions=True)
        notification.mark_as_sent()
        
        return {"success": True, "notification": notification.name}
    except Exception as e:
        frappe.logger().error(f"Error creating test notification: {str(e)}")
        return {"success": False, "error": str(e)}


def get_notification_stats():
    """Get notification statistics for monitoring"""
    try:
        stats = frappe.db.sql("""
            SELECT 
                notification_type,
                status,
                COUNT(*) as count
            FROM `tabCRM Task Notification`
            WHERE creation >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
            GROUP BY notification_type, status
        """, as_dict=True)
        
        return stats
    except Exception as e:
        frappe.logger().error(f"Error getting notification stats: {str(e)}")
        return [] 