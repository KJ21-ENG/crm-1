import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_to_date, get_fullname
from datetime import datetime, timedelta
import json
from crm.api.role_assignment import RoleAssignmentTracker
from crm.api.activities import emit_activity_update

# @frappe.whitelist()
# def auto_reassign_overdue_tasks():
#     """
#     Background function to check for overdue tasks and reassign them
#     This function should be called every 5 minutes by the scheduler
#     DEPRECATED: Replaced by process_overdue_task_reassignments() master function
#     """
#     try:
#         current_time = get_datetime(now())
#         
#         # Get tasks where due_date has passed and status is Todo
#         overdue_tasks = frappe.get_list(
#             "CRM Task",
#             filters={
#                 "due_date": ["<", current_time],
#                 "status": "Todo",
#                 "reference_doctype": ["in", ["CRM Lead", "CRM Ticket"]],
#                 "final_overdue": ["!=", 1]  # Exclude tasks marked as final overdue
#             },
#             fields=["name", "title", "priority", "start_date", "reference_doctype", 
#                    "reference_docname", "assigned_to", "status", "due_date", "description", 
#                    "_assign", "reassignment_processed"]
#         )
#         
#         frappe.logger().info(f"Found {len(overdue_tasks)} overdue tasks to reassign")
#         
#         reassigned_count = 0
#         exhaustion_data = {}  # Store exhaustion state for each task
#         
#         for task in overdue_tasks:
#             try:
#                 frappe.logger().info(f"Processing task {task.name} for reassignment")
#                 
#                 # Get the full task document
#                 try:
#                     task_doc = frappe.get_doc("CRM Task", task.name)
#                     task_doc.reload()  # Ensure all fields are properly loaded
#                     frappe.logger().info(f"Task document retrieved successfully for {task.name}")
#                 except Exception as e:
#                     frappe.logger().error(f"Error getting task document for {task.name}: {str(e)}")
#                     continue
#                 
#                 # Safety check: Skip if task is already marked as final overdue
#                 if task_doc.final_overdue:
#                     frappe.logger().info(f"Skipping task {task.name} - already marked as final overdue")
#                     continue
#                 
#                 # Determine the role based on reference_doctype
#                 if task_doc.reference_doctype == "CRM Lead":
#                     role_name = "Sales User"
#                 elif task_doc.reference_doctype == "CRM Ticket":
#                     role_name = "Support User"
#                 else:
#                     continue  # Skip if not Lead or Ticket
#                 
#                 # Get current assignment history from _assign field
#                 current_assignees = []
#                 if task_doc._assign:
#                     try:
#                         current_assignees = json.loads(task_doc._assign)
#                         if not isinstance(current_assignees, list):
#                             current_assignees = []
#                     except (json.JSONDecodeError, TypeError):
#                         current_assignees = []
#                 
#                 # Add current assignee to history if not already there
#                 if task_doc.assigned_to and task_doc.assigned_to not in current_assignees:
#                     current_assignees.append(task_doc.assigned_to)
#                 
#                 # Get all users for this role to check if all have been assigned
#                 role_users = RoleAssignmentTracker.get_role_users(role_name)
#                 if not role_users:
#                     frappe.logger().error(f"No users found for role {role_name}")
#                     continue
#                 
#                 # Filter out admin users
#                 role_users = [user for user in role_users if user not in ["Administrator", "admin@example.com"]]
#                 
#                 if not role_users:
#                     frappe.logger().error(f"No valid users found for role {role_name} (after filtering admin)")
#                     continue
#                 
#                 # Check if all users have been assigned to this task
#                 unassigned_users = [user for user in role_users if user not in current_assignees]
#                 
#                 # Store exhaustion state for this task
#                 exhaustion_data[task.name] = {
#                     "all_users_assigned": len(unassigned_users) == 0,
#                     "role_name": role_name,
#                     "total_users": len(role_users),
#                     "assigned_users": current_assignees.copy(),
#                     "unassigned_users": unassigned_users.copy(),
#                     "reference_doctype": task_doc.reference_doctype,
#                     "reference_docname": task_doc.reference_docname
#                 }
#                 
#                 if not unassigned_users:
#                     # All users have been assigned, mark as final overdue and notify admin
#                     frappe.logger().warning(f"All users for role {role_name} have been assigned to task {task.name}. Marking as final overdue and notifying admin.")
#                     
#                     # Mark task as final overdue using direct database update
#                     try:
#                         frappe.db.set_value("CRM Task", task_doc.name, "final_overdue", 1)
#                         frappe.logger().info(f"Marked task {task_doc.name} as final overdue")
#                     except Exception as e:
#                         frappe.logger().error(f"Error marking task {task_doc.name} as final overdue: {str(e)}")
#                     
#                     # Update parent document with final overdue task reference
#                     try:
#                         frappe.db.set_value(
#                             task_doc.reference_doctype, 
#                             task_doc.reference_docname, 
#                             "final_overdue_task", 
#                             task_doc.name
#                         )
#                         frappe.logger().info(f"Updated {task_doc.reference_doctype} {task_doc.reference_docname} with final_overdue_task: {task_doc.name}")
#                         # Commit the database changes
#                         frappe.db.commit()
#                     except Exception as e:
#                         frappe.logger().error(f"Error updating parent document with final_overdue_task: {str(e)}")
#                     
#                     # Create notification for admin with improved formatting
#                     document_type = "Lead" if task_doc.reference_doctype == "CRM Lead" else "Ticket"
#                     notification_content = f"⚠️ **{document_type} and Task Assignment Limit Reached**\n\n**Task:** {task_doc.title}\n**Current Assignee:** {task_doc.assigned_to or 'Unassigned'}\n**Role:** {role_name}\n**All Users Exhausted:** {', '.join(current_assignees)}\n**Status:** Marked as Final Overdue\n\n**Action Required:** Manual intervention needed. All eligible users have been assigned to this task. Please review and resolve manually."
#                     
#                     # Create comment for the task
#                     comment = frappe.get_doc({
#                         "doctype": "Comment",
#                         "comment_type": "Comment",
#                         "reference_doctype": "CRM Task",
#                         "reference_name": task_doc.name,
#                         "content": notification_content,
#                         "comment_email": "Administrator",
#                         "creation": frappe.utils.now(),
#                     })
#                     comment.insert(ignore_permissions=True)
#                     
#                     # Also create comment for parent document
#                     parent_comment = frappe.get_doc({
#                         "doctype": "Comment",
#                         "comment_type": "Comment",
#                         "reference_doctype": task_doc.reference_doctype,
#                         "reference_name": task_doc.reference_docname,
#                         "content": notification_content,
#                         "comment_email": "Administrator",
#                         "creation": frappe.utils.now(),
#                     })
#                     parent_comment.insert(ignore_permissions=True)
#                     
#                     # Create admin notification for Task Reminder system
#                     try:
#                         from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
#                         
#                         admin_notification = create_task_notification(
#                             task_name=task_doc.name,
#                             notification_type="Task Reassignment Limit",
#                             assigned_to="Administrator",
#                             message=f"All eligible users have been assigned to task: {task_doc.title} - Marked as Final Overdue",
#                             reference_doctype=task_doc.reference_doctype,
#                             reference_docname=task_doc.reference_docname
#                         )
#                         
#                         if admin_notification:
#                             # Mark notification as sent immediately
#                             admin_notification.mark_as_sent()
#                             frappe.logger().info(f"Admin notification created for task reassignment limit: {admin_notification.name}")
#                     except Exception as e:
#                         frappe.logger().error(f"Error creating admin notification for task {task_doc.name}: {str(e)}")
#                     
#                     continue
#                 
#                 # Get next user using round-robin (only from unassigned users)
#                 new_assignee = RoleAssignmentTracker.assign_to_next_user_from_list(
#                     role_name=role_name,
#                     user_list=unassigned_users,
#                     document_type=task_doc.reference_doctype,
#                     document_name=task_doc.reference_docname,
#                     assigned_by="Administrator"
#                 )
#                 
#                 if not new_assignee:
#                     frappe.logger().error(f"Failed to get next user for task {task.name}")
#                     continue
#                 
#                 # Get the old assignee
#                 old_assignee = task_doc.assigned_to
#                 old_assignee_name = get_fullname(old_assignee) if old_assignee else "Unassigned"
#                 new_assignee_name = get_fullname(new_assignee)
#                 
#                 # Update the existing task instead of creating new one
#                 task_doc.assigned_to = new_assignee
#                 
#                 # Add new assignee to _assign history (preserve existing assignees)
#                 if new_assignee not in current_assignees:
#                     current_assignees.append(new_assignee)
#                 
#                 # Increment reassignment_processed count
#                 current_processed = task_doc.reassignment_processed or 0
#                 task_doc.reassignment_processed = current_processed + 1
#                 
#                 # Update due date to give new assignee time
#                 new_due_date = get_datetime(now()) + timedelta(days=1)  # Give 1 day
#                 task_doc.due_date = new_due_date
#                 
#                 # Save the updated task (without _assign to avoid conflicts)
#                 task_doc.save(ignore_permissions=True)
#                 
#                 # Update _assign field directly in database to avoid interference
#                 frappe.db.set_value("CRM Task", task_doc.name, "_assign", json.dumps(current_assignees))
#                 
#                 frappe.logger().info(f"Successfully reassigned task {task.name} from {old_assignee_name} to {new_assignee_name}")
#                 frappe.logger().info(f"Task {task.name} has been reassigned {task_doc.reassignment_processed} times")
#                 frappe.logger().info(f"Assignment history for task {task.name}: {current_assignees}")
#                 
#                 reassigned_count += 1
#                 
#             except Exception as e:
#                 frappe.logger().error(f"Error auto-reassigning task {task.name}: {str(e)}")
#                 frappe.log_error(
#                     title=f"Task Reassignment Error - {task.name}",
#                     message=f"Error: {str(e)}\nTask: {task.name}"
#                 )
#                 continue
#         
#         frappe.db.commit()
#         
#         return {
#             "success": True,
#             "message": f"Successfully reassigned {reassigned_count} overdue tasks",
#             "reassigned_count": reassigned_count,
#             "exhaustion_data": exhaustion_data  # Pass exhaustion state to second function
#         }
#         
#     except Exception as e:
#         frappe.logger().error(f"Error in auto_reassign_overdue_tasks: {str(e)}")
#         frappe.log_error(
#             title="Auto Reassign Tasks Error",
#             message=str(e)
#         )
#         return {
#             "success": False,
#             "error": str(e)
#         }

@frappe.whitelist()
def get_overdue_tasks_count():
    """Get count of overdue tasks that need reassignment"""
    try:
        current_time = get_datetime(now())
        
        count = frappe.db.count("CRM Task", filters={
            "due_date": ["<", current_time],
            "status": "Todo",
            "reference_doctype": ["in", ["CRM Lead", "CRM Ticket"]]
        })
        
        return {"count": count}
    except Exception as e:
        return {"error": str(e)}
        
@frappe.whitelist()
def test_reassignment_for_task(task_name):
    """Test reassignment for a specific task"""
    try:
        task_doc = frappe.get_doc("CRM Task", task_name)
        print(f"Task found: {task_doc.name}, Status: {task_doc.status}, Due: {task_doc.due_date}")
        
        if task_doc.status != "Todo":
            return {"error": "Task is not in Todo status"}
            
        # Reset status to Todo if needed
        if task_doc.status == "Canceled":
            task_doc.status = "Todo"
            task_doc.save(ignore_permissions=True)
            print(f"Reset task status to Todo")
        
        # Run reassignment (use new master function)
        process_overdue_task_reassignments()
        
        return {"success": True, "message": "Reassignment attempted"}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@frappe.whitelist()
def manually_trigger_reassignment():
    """Manually trigger the reassignment process (for testing)"""
    try:
        # Check if user has permission
        if not frappe.has_permission("CRM Task", "write"):
            frappe.throw("Insufficient permissions to trigger reassignment")
        
        process_overdue_task_reassignments()
        
        return {
            "success": True,
            "message": "Reassignment process triggered successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def test_document_assignment_update(task_name):
    """Test function to verify document assignment updates work correctly"""
    try:
        task_doc = frappe.get_doc("CRM Task", task_name)
        
        if not task_doc.reference_doctype or not task_doc.reference_docname:
            return {"error": "Task has no reference document"}
        
        # Get the linked document
        linked_doc = frappe.get_doc(task_doc.reference_doctype, task_doc.reference_docname)
        
        # Get current assignment values
        current_assignment = None
        if task_doc.reference_doctype == "CRM Lead":
            current_assignment = linked_doc.assign_to
        elif task_doc.reference_doctype == "CRM Ticket":
            current_assignment = linked_doc.assigned_to
        
        current_assign = linked_doc._assign
        
        return {
            "success": True,
            "task_name": task_name,
            "reference_doctype": task_doc.reference_doctype,
            "reference_docname": task_doc.reference_docname,
            "current_assignment": current_assignment,
            "current_assign": current_assign,
            "task_assigned_to": task_doc.assigned_to
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def process_overdue_task_reassignments():
    """
    Master function to find overdue tasks, reassign them, and update the
    parent Lead/Ticket documents in a single process.
    This should be called by the scheduler.
    """
    try:
        current_time = get_datetime(now())
        
        # Calculate grace period: 30 minutes after due date
        grace_period_minutes = 30
        grace_period_time = current_time - timedelta(minutes=grace_period_minutes)
        
        # Parent condition: only run reassignment inside office hours
        try:
            from crm.api.office_hours import is_office_open
            if not is_office_open():
                frappe.logger().info("Skipping reassignment processing: outside office hours")
                return {"success": True, "message": "Skipped (outside office hours)", "reassigned_count": 0}
        except Exception as e:
            frappe.logger().error(f"Failed to evaluate office hours: {str(e)}")

        # Get tasks where due_date has passed the grace period and status is Todo
        overdue_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "due_date": ["<", grace_period_time],  # Due date must be 30+ minutes ago
                "status": "Todo",
                "reference_doctype": ["in", ["CRM Lead", "CRM Ticket"]],
                "final_overdue": ["!=", 1]
            },
            fields=["name", "title", "assigned_to", "reference_doctype", "reference_docname", "_assign", "due_date"]
        )
        
        frappe.logger().info(f"Found {len(overdue_tasks)} overdue tasks (after {grace_period_minutes}min grace period) to process.")
        frappe.logger().info(f"Current time: {current_time}, Grace period cutoff: {grace_period_time}")
        
        reassigned_count = 0
        exhausted_tasks_count = 0
        
        for task in overdue_tasks:
            try:
                # Double-check grace period before processing
                task_due_date = get_datetime(task.due_date)
                if task_due_date >= grace_period_time:
                    frappe.logger().info(f"Skipping task {task.name} - still within grace period. Due: {task_due_date}, Grace cutoff: {grace_period_time}")
                    continue
                
                frappe.logger().info(f"Processing task {task.name} for reassignment and parent update. Due: {task_due_date}, Grace cutoff: {grace_period_time}")
                
                # Get the full task document
                task_doc = frappe.get_doc("CRM Task", task.name)
                
                # Determine the role based on the parent document
                if task_doc.reference_doctype == "CRM Lead":
                    role_name = "Sales User"
                    parent_assignee_field = "assign_to"
                elif task_doc.reference_doctype == "CRM Ticket":
                    role_name = "Support User"
                    parent_assignee_field = "assigned_to"
                else:
                    continue # Skip if not a Lead or Ticket task

                # --- 1. Reassignment Logic ---

                # Get current assignment history from the task's _assign field
                current_assignees = json.loads(task_doc._assign) if task_doc._assign else []
                if not isinstance(current_assignees, list): current_assignees = []
                
                if task_doc.assigned_to and task_doc.assigned_to not in current_assignees:
                    current_assignees.append(task_doc.assigned_to)

                # Get all users for the role and filter out admins
                role_users = RoleAssignmentTracker.get_role_users(role_name)
                role_users = [user for user in role_users if user not in ["Administrator", "admin@example.com"]]

                if not role_users:
                    frappe.logger().error(f"No valid users found for role {role_name} for task {task.name}")
                    continue

                # Find users who have not yet been assigned this task
                unassigned_users = [user for user in role_users if user not in current_assignees]

                # --- 2. Handle User Exhaustion or Reassign ---

                if not unassigned_users:
                    # ---- EXHAUSTION PATH ----
                    frappe.logger().warning(f"All users for role {role_name} exhausted for task {task.name}. Marking as final.")
                    
                    # Mark task as final overdue
                    frappe.db.set_value("CRM Task", task_doc.name, "final_overdue", 1)
                    
                    # Update parent document with the final overdue task reference
                    frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, "final_overdue_task", task_doc.name)

                    # Create notification and comments for admin
                    document_type = "Lead" if task_doc.reference_doctype == "CRM Lead" else "Ticket"
                    notification_content = f"⚠️ **{document_type} and Task Assignment Limit Reached**\n\n**Task:** {task_doc.title}\n**Current Assignee:** {get_fullname(task_doc.assigned_to) or 'Unassigned'}\n**Role:** {role_name}\n\n**Action Required:** Manual intervention needed. All eligible users have been assigned this task."
                    
                    # Create comment on the task and parent document
                    for doctype, name in [("CRM Task", task_doc.name), (task_doc.reference_doctype, task_doc.reference_docname)]:
                        frappe.get_doc({
                            "doctype": "Comment", "comment_type": "Comment",
                            "reference_doctype": doctype, "reference_name": name,
                            "content": notification_content, "comment_email": "Administrator"
                        }).insert(ignore_permissions=True)
                    
                    # Create admin notification for Task Reminder interface
                    try:
                        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
                        
                        admin_notification = create_task_notification(
                            task_name=task_doc.name,
                            notification_type="Task Reassignment Limit",
                            assigned_to="Administrator",
                            message=f"All eligible users have been assigned to task: {task_doc.title} - Marked as Final Overdue",
                            reference_doctype=task_doc.reference_doctype,
                            reference_docname=task_doc.reference_docname
                        )
                        
                        if admin_notification:
                            # Mark notification as sent immediately to show in Task Reminder interface
                            admin_notification.mark_as_sent()
                            frappe.logger().info(f"Admin notification created for task reassignment limit: {admin_notification.name}")
                    except Exception as e:
                        frappe.logger().error(f"Error creating admin notification for task {task_doc.name}: {str(e)}")
                    
                    exhausted_tasks_count += 1
                
                else:
                    # ---- REASSIGNMENT PATH ----
                    new_assignee = RoleAssignmentTracker.assign_to_next_user_from_list(
                        role_name=role_name, user_list=unassigned_users,
                        document_type=task_doc.reference_doctype, document_name=task_doc.reference_docname,
                        assigned_by="Administrator"
                    )

                    if not new_assignee:
                        frappe.logger().error(f"Failed to get next user for task {task.name}")
                        continue
                    
                    old_assignee_name = get_fullname(task_doc.assigned_to) or "Unassigned"
                    
                    # Update the task document
                    task_doc.assigned_to = new_assignee
                    task_doc.due_date = get_datetime(now()) + timedelta(days=1)
                    if new_assignee not in current_assignees:
                        current_assignees.append(new_assignee)
                    
                    task_doc.save(ignore_permissions=True) # Save the task first
                    frappe.db.set_value("CRM Task", task_doc.name, "_assign", json.dumps(current_assignees))

                    # --- 3. Immediate Parent Document Update ---
                    
                    # Get parent's current assignment history
                    parent_assign_history = json.loads(frappe.db.get_value(task_doc.reference_doctype, task_doc.reference_docname, "_assign")) or []
                    if not isinstance(parent_assign_history, list): parent_assign_history = []
                    
                    if new_assignee not in parent_assign_history:
                        parent_assign_history.append(new_assignee)
                    
                    # Update the parent document's fields directly
                    frappe.db.set_value(task_doc.reference_doctype, task_doc.reference_docname, {
                        parent_assignee_field: new_assignee,
                        "_assign": json.dumps(parent_assign_history)
                    })
                    
                    # Create a comment on the parent for the activity log
                    document_type = "Lead" if task_doc.reference_doctype == "CRM Lead" else "Ticket"
                    comment_content = f"🔄 **{document_type} Reassigned**\n\n**New Assignee:** {get_fullname(new_assignee)}\n**Reason:** Overdue task auto-reassigned (after 30min grace period)."
                    frappe.get_doc({
                        "doctype": "Comment", "comment_type": "Comment",
                        "reference_doctype": task_doc.reference_doctype, "reference_name": task_doc.reference_docname,
                        "content": comment_content, "comment_email": "Administrator"
                    }).insert(ignore_permissions=True)

                    frappe.logger().info(f"Successfully reassigned task {task.name} to {get_fullname(new_assignee)} and updated parent {task_doc.reference_docname}.")
                    reassigned_count += 1

            except Exception as e:
                frappe.logger().error(f"Error processing task {task.name}: {str(e)}")
                frappe.log_error(title=f"Task Reassignment Error - {task.name}", message=f"Error: {str(e)}")
                continue
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Process complete. Reassigned {reassigned_count} tasks and marked {exhausted_tasks_count} as final overdue.",
            "reassigned_count": reassigned_count,
            "exhausted_tasks_count": exhausted_tasks_count
        }
        
    except Exception as e:
        frappe.logger().error(f"Critical error in process_overdue_task_reassignments: {str(e)}")
        frappe.log_error(title="Auto Reassign Tasks Master Error", message=str(e))
        return {"success": False, "error": str(e)}

# @frappe.whitelist()
# def update_parent_document_assignments(exhaustion_data=None):
#     """Update parent document assignments based on latest task assignments"""
#     DEPRECATED: Replaced by process_overdue_task_reassignments() master function
#     """
#     try:
#         # Parse exhaustion_data if it's passed as a string (from frontend)
#         if exhaustion_data and isinstance(exhaustion_data, str):
#             try:
#                 exhaustion_data = json.loads(exhaustion_data)
#             except (json.JSONDecodeError, TypeError):
#                 exhaustion_data = None
#                 frappe.logger().warning("Failed to parse exhaustion_data, proceeding without it")
#         current_time = get_datetime(now())
#         
#         # Get all active tasks (Todo status) for CRM Lead and CRM Ticket, excluding final overdue tasks
#         active_tasks = frappe.get_list(
#             "CRM Task",
#             filters={
#                 "status": "Todo",
#                 "reference_doctype": ["in", ["CRM Lead", "CRM Ticket"]],
#                 "final_overdue": ["!=", 1]  # Exclude tasks marked as final overdue
#             },
#             fields=["name", "assigned_to", "reference_doctype", "reference_docname"]
#         )
#         
#         frappe.logger().info(f"Found {len(active_tasks)} active tasks to update parent documents")
#         
#         updated_count = 0
#         
#         for task in active_tasks:
#             try:
#                 # Double-check if task is marked as final overdue (safety check)
#                 task_final_overdue = frappe.db.get_value("CRM Task", task.name, "final_overdue")
#                 if task_final_overdue:
#                     frappe.logger().info(f"Skipping task {task.name} - marked as final overdue")
#                     continue
#                 
#                 # Check if this task was processed in the first function
#                 task_exhaustion_data = None
#                 if exhaustion_data and task.name in exhaustion_data:
#                     task_exhaustion_data = exhaustion_data[task.name]
#                     frappe.logger().info(f"Using exhaustion data for task {task.name}: all_users_assigned={task_exhaustion_data.get('all_users_assigned')}")
#                 
#                 # If we have exhaustion data and all users were assigned, skip this task
#                 if task_exhaustion_data and task_exhaustion_data.get("all_users_assigned"):
#                     frappe.logger().info(f"Skipping task {task.name} - all users already assigned based on exhaustion data")
#                     continue
# 
#                 
#                 # Get current _assign value to append to it
#                 current_assign = frappe.db.get_value(task.reference_doctype, task.reference_docname, "_assign")
#                 
#                 # Parse existing _assign or start with empty list
#                 if current_assign:
#                     try:
#                         existing_assignees = json.loads(current_assign)
#                         if not isinstance(existing_assignees, list):
#                             existing_assignees = []
#                     except (json.JSONDecodeError, TypeError):
#                         existing_assignees = []
#                 else:
#                     existing_assignees = []
#                 
#                 # Add new assignee if not already in the list
#                 if task.assigned_to not in existing_assignees:
#                     existing_assignees.append(task.assigned_to)
#                 
#                 # Create proper Comment document for Activity tab display
#                 document_type = "Lead" if task.reference_doctype == "CRM Lead" else "Ticket"
#                 comment_content = f"🔄 **{document_type} and Task Reassigned**\n\n**New Assignee:** {task.assigned_to}\n**Reason:** Auto-reassignment to new user"
#                 
#                 comment = frappe.get_doc({
#                     "doctype": "Comment",
#                     "comment_type": "Comment",
#                     "reference_doctype": task.reference_doctype,
#                     "reference_name": task.reference_docname,
#                     "content": comment_content,
#                     "comment_email": "Administrator",
#                     "creation": frappe.utils.now(),
#                 })
#                 comment.insert(ignore_permissions=True)
#                 
#                 # Update assignment directly in database to avoid field loading issues
#                 if task.reference_doctype == "CRM Lead":
#                     frappe.db.set_value("CRM Lead", task.reference_docname, "assign_to", task.assigned_to)
#                     frappe.db.set_value("CRM Lead", task.reference_docname, "_assign", json.dumps(existing_assignees))
#                     frappe.logger().info(f"Updated CRM Lead {task.reference_docname} assign_to to {task.assigned_to}, _assign now has {len(existing_assignees)} assignees")
#                 elif task.reference_doctype == "CRM Ticket":
#                     frappe.db.set_value("CRM Ticket", task.reference_docname, "assigned_to", task.assigned_to)
#                     frappe.db.set_value("CRM Ticket", task.reference_docname, "_assign", json.dumps(existing_assignees))
#                     frappe.logger().info(f"Updated CRM Ticket {task.reference_docname} assigned_to to {task.assigned_to}, _assign now has {len(existing_assignees)} assignees")
#                 
#                 frappe.logger().info(f"Successfully updated {task.reference_doctype} {task.reference_docname} assignment to {task.assigned_to}")
#                 updated_count += 1
#                 
#             except Exception as e:
#                 frappe.logger().error(f"Error updating parent document for task {task.name}: {str(e)}")
#                 frappe.log_error(
#                     title=f"Parent Document Update Error - {task.name}",
#                     message=f"Error: {str(e)}\nReference: {task.reference_doctype} - {task.reference_docname}"
#                 )
#         
#         frappe.db.commit()
#         
#         return {
#             "success": True,
#             "message": f"Updated {updated_count} parent documents",
#             "updated_count": updated_count
#         }
#         
#     except Exception as e:
#         frappe.logger().error(f"Error in update_parent_document_assignments: {str(e)}")
#         frappe.log_error(
#             title="Parent Document Update Error",
#             message=str(e)
#         )
#         return {
#             "success": False,
#             "error": str(e)
#         }