import frappe
import json
from datetime import datetime
from frappe.utils import get_fullname
from crm.fcrm.doctype.role_assignment_tracker.role_assignment_tracker import RoleAssignmentTracker
from crm.api.activities import emit_activity_update

@frappe.whitelist()
def test_role_assignment_tracker():
    """Test function to verify Role Assignment Tracker works with JSON serialization"""
    try:
        # Test getting/creating tracker for Sales User role
        tracker = RoleAssignmentTracker.get_or_create_tracker('Sales User')
        
        # Get next user
        next_user, updated_tracker = RoleAssignmentTracker.get_next_user_for_role('Sales User')
        
        return {
            "success": True,
            "tracker_name": tracker.name,
            "total_users": tracker.total_users,
            "user_list_type": str(type(tracker.user_list)),
            "user_list": tracker.user_list,
            "next_user": next_user,
            "current_position": updated_tracker.current_position
        }
    except Exception as e:
        frappe.log_error(f"Test role assignment tracker failed: {str(e)}", "Test Role Assignment Error")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_assignable_roles():
    """Get list of roles that can be assigned to leads"""
    roles = [
        'Sales User',
        'Sales Manager', 
        'Support User',
        'CRM User',
        'CRM Manager'
    ]
    
    role_data = []
    for role in roles:
        # Get users count for each role
        users = frappe.get_all("Has Role", 
            filters={"role": role, "parent": ["!=", "Administrator"]},
            fields=["parent"]
        )
        
        # Filter only enabled users
        enabled_users = [user.parent for user in users if frappe.db.get_value("User", user.parent, "enabled")]
        
        role_data.append({
            "role": role,
            "user_count": len(enabled_users),
            "enabled": len(enabled_users) > 0
        })
    
    return role_data

@frappe.whitelist()
def assign_to_role(lead_name, role_name, assigned_by=None):
    """Assign a lead to a role using round-robin logic"""
    try:
        if not assigned_by:
            assigned_by = frappe.session.user
        
        # Get the next user for this role using the dedicated tracker
        assigned_user = RoleAssignmentTracker.assign_to_next_user(
            role_name=role_name,
            document_type="CRM Lead",
            document_name=lead_name,
            assigned_by=assigned_by
        )
        
        # Update the lead (only assigned_role, NOT lead_owner)
        lead_doc = frappe.get_doc("CRM Lead", lead_name)
        lead_doc.assigned_role = role_name
        
        # Use Frappe's standard assignment system
        frappe.desk.form.assign_to.add({
            "assign_to": [assigned_user],
            "doctype": "CRM Lead",
            "name": lead_name,
            "description": f"Lead assigned to {role_name} role - round-robin assignment"
        })
        
        # Create activity timeline entry for the assignment
        assigned_user_name = get_fullname(assigned_user)
        assigned_by_name = get_fullname(assigned_by)
        
        # Create assignment activity
        assignment_comment = frappe.get_doc({
            "doctype": "Comment", 
            "comment_type": "Comment",  # Changed to Comment so it shows in docinfo.comments
            "reference_doctype": "CRM Lead",
            "reference_name": lead_name,
            "content": f"🎯 <strong>{assigned_by_name}</strong> assigned this lead to <strong>{assigned_user_name}</strong> from <strong>{role_name}</strong> role using round-robin assignment",
            "comment_email": assigned_by,
            "creation": frappe.utils.now(),
        })
        assignment_comment.insert(ignore_permissions=True)
        
        # Emit activity update to refresh frontend
        emit_activity_update("CRM Lead", lead_name)
        
        lead_doc.save(ignore_permissions=True)
        
        # Create follow-up task
        task_doc = frappe.get_doc({
            "doctype": "CRM Task",
            "title": f"Follow up on lead: {lead_doc.first_name or lead_name}",
            "assigned_to": assigned_user,
            "reference_doctype": "CRM Lead",
            "reference_docname": lead_name,
            "description": f"Task created for lead assignment to {role_name} role - {lead_doc.first_name or ''} {lead_doc.last_name or ''}".strip(),
            "priority": "Medium",
            "status": "Open"
        })
        task_doc.insert(ignore_permissions=True)
        
        # Create activity for task creation
        task_activity = {
            "activity_type": "task",
            "name": task_doc.name,
            "creation": frappe.utils.now(),
            "owner": assigned_by,
            "data": {
                "title": task_doc.title,
                "description": task_doc.description,
                "due_date": task_doc.due_date,
                "priority": task_doc.priority,
                "status": task_doc.status,
                "reference_doctype": task_doc.reference_doctype,
                "reference_docname": task_doc.reference_docname
            },
            "is_lead": True
        }
        
        # Add activity to timeline
        activity_comment = frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",  # Changed to Comment so it shows in docinfo.comments
            "reference_doctype": "CRM Lead", 
            "reference_name": lead_name,
            "content": f"📋 Task created: {task_doc.title}",
            "comment_email": assigned_by,
            "creation": frappe.utils.now(),
        })
        activity_comment.insert(ignore_permissions=True)
        
        # Emit activity update to refresh frontend
        emit_activity_update("CRM Lead", lead_name)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "assigned_user": assigned_user,
            "role": role_name,
            "message": f"Lead successfully assigned to {assigned_user} from {role_name} role",
            "task_created": task_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Role assignment failed: {str(e)}", "Role Assignment Error")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def preview_next_assignment(role_name):
    """Preview which user will be assigned next for a role"""
    try:
        next_user, tracker = RoleAssignmentTracker.get_next_user_for_role(role_name)
        
        return {
            "success": True,
            "next_user": next_user,
            "current_position": tracker.current_position,
            "total_users": tracker.total_users,
            "user_list": tracker.user_list
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_role_assignment_status(role_name):
    """Get detailed status of role assignment including round-robin state"""
    try:
        status = RoleAssignmentTracker.get_role_status(role_name)
        
        if "error" in status:
            return {
                "success": False,
                "error": status["error"]
            }
        
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def reset_role_assignment(role_name):
    """Reset round-robin position for a role (admin function)"""
    try:
        # Check if user has permission
        if not frappe.has_permission("Role Assignment Tracker", "write"):
            frappe.throw("Insufficient permissions to reset role assignment")
        
        result = RoleAssignmentTracker.reset_role_tracker(role_name)
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_assignment_history(role_name, limit=20):
    """Get assignment history for a role"""
    try:
        tracker = frappe.get_doc("Role Assignment Tracker", role_name)
        history = tracker.assignment_history or []
        
        # Return most recent assignments
        recent_history = history[-limit:] if len(history) > limit else history
        recent_history.reverse()  # Most recent first
        
        return {
            "success": True,
            "history": recent_history,
            "total_assignments": tracker.assignment_count
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 