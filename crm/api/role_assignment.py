import frappe
import json
from datetime import datetime, timedelta
from frappe.utils import get_fullname
from crm.fcrm.doctype.role_assignment_tracker.role_assignment_tracker import RoleAssignmentTracker
from crm.api.activities import emit_activity_update
from crm.utils import assert_office_open

def _get_assigned_users_for_document(doctype: str, docname: str):
    """Return a set of users already assigned to the given document.
    Looks at both the document's _assign field and open/working ToDo entries."""
    try:
        assigned = set()
        # From _assign JSON on the document
        try:
            parent = frappe.get_doc(doctype, docname)
            if parent and getattr(parent, "_assign", None):
                try:
                    arr = json.loads(parent._assign) if isinstance(parent._assign, str) else parent._assign
                    if isinstance(arr, list):
                        assigned.update([u for u in arr if isinstance(u, str) and u])
                except Exception:
                    pass
        except Exception:
            pass

        # From ToDo (Open/Working)
        try:
            todos = frappe.get_all(
                "ToDo",
                filters={
                    "reference_type": doctype,
                    "reference_name": docname,
                    "status": ["in", ["Open", "Working"]],
                },
                fields=["allocated_to"],
            )
            for t in todos:
                if t.get("allocated_to"):
                    assigned.add(t["allocated_to"])
        except Exception:
            pass

        return assigned
    except Exception:
        return set()

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
def get_current_assignments(doc_name, doctype="CRM Lead"):
    """Get current assignments for a document from _assign field"""
    try:
        import json
        
        # Get the document to access _assign field
        doc = frappe.get_doc(doctype, doc_name)
        
        if not doc or not doc._assign:
            return []
        
        # Parse the _assign field (JSON array of user emails)
        try:
            assigned_users = json.loads(doc._assign)
        except (json.JSONDecodeError, TypeError):
            # If _assign is not valid JSON, try to handle as string
            if isinstance(doc._assign, str):
                assigned_users = [doc._assign.strip()]
            else:
                assigned_users = []
        
        assignments = []
        
        # Create assignment objects for each assigned user
        for user_email in assigned_users:
            if user_email:
                try:
                    user = frappe.get_doc("User", user_email)
                    assignment = {
                        "name": f"assignment_{user_email}_{doc_name}",
                        "allocated_to": user_email,
                        "creation": doc.creation,  # Use document creation time
                        "status": "Open",
                        "description": f"Assigned to {user.full_name or user_email}",
                        "user_full_name": user.full_name or user.name,
                        "user_image": user.user_image
                    }
                    assignments.append(assignment)
                except Exception as user_error:
                    # If user doesn't exist, still show the assignment
                    assignment = {
                        "name": f"assignment_{user_email}_{doc_name}",
                        "allocated_to": user_email,
                        "creation": doc.creation,
                        "status": "Open",
                        "description": f"Assigned to {user_email}",
                        "user_full_name": user_email,
                        "user_image": None
                    }
                    assignments.append(assignment)
        
        return assignments
        
    except Exception as e:
        frappe.log_error(f"Error getting current assignments from _assign: {str(e)}", "Role Assignment Error")
        return []

@frappe.whitelist()
def get_assignable_roles():
    """Get list of roles that can be assigned to leads, with user counts and names (for debugging/visibility)"""
    roles = [
        'Sales User',
        'Sales Manager', 
        'Support User',
        'Support Manager',
    ]
    
    role_data = []
    for role in roles:
        # Users who have this role (exclude Administrator variants)
        role_users = frappe.get_all(
            "Has Role",
            filters={
                "role": role,
                "parent": ["not in", ["Administrator", "admin@example.com"]],
            },
            fields=["parent"],
        )

        enabled_user_ids = [u.parent for u in role_users if frappe.db.get_value("User", u.parent, "enabled")]
        # Extra safety: exclude special users like Guest
        excluded_ids = {"Administrator", "admin@example.com", "Guest"}
        filtered_ids = [uid for uid in enabled_user_ids if uid not in excluded_ids]

        # Fetch names for display
        user_details = []
        user_names = []
        if filtered_ids:
            user_details = frappe.get_all(
                "User",
                filters={"name": ["in", filtered_ids]},
                fields=["name", "full_name"],
            )
            user_names = [(ud.get("full_name") or ud.get("name")) for ud in user_details]

        role_data.append({
            "role": role,
            "user_count": len(filtered_ids),
            "enabled": len(filtered_ids) > 0,
            "user_names": user_names,
        })
    
    return role_data

@frappe.whitelist()
def get_assignable_users():
    """Get list of users that can be assigned to leads (Admin Only)"""
    try:
        # Check if user has admin permissions
        if not frappe.has_permission("Role Assignment Tracker", "write"):
            frappe.throw("Insufficient permissions to access assignable users")
        
        # Get all enabled users with CRM roles
        users = frappe.get_all("User",
            filters={
                "enabled": 1,
                "name": ["!=", "Administrator"]
            },
            fields=["name", "full_name", "email", "user_image"]
        )
        
        user_data = []
        for user in users:
            # Get user roles
            roles = frappe.get_roles(user.name)
            
            # Filter only CRM-related roles
            crm_roles = [role for role in roles if role in [
                'Sales User', 'Sales Manager', 'Support User', 'CRM User', 'CRM Manager'
            ]]
            
            if crm_roles:
                user_data.append({
                    "name": user.name,
                    "full_name": user.full_name or user.name,
                    "email": user.email,
                    "user_image": user.user_image,
                    "role": crm_roles[0] if crm_roles else "No Role",
                    "enabled": True
                })
        
        # Sort by full name
        user_data.sort(key=lambda x: x["full_name"])
        
        return user_data
        
    except Exception as e:
        frappe.log_error(f"Error getting assignable users: {str(e)}", "Role Assignment Error")
        return []

@frappe.whitelist()
def assign_to_role(lead_name, role_name, assigned_by=None, skip_task_creation=False):
    """Assign a lead to a role using round-robin logic"""
    try:
        # Respect office hours for automatic role-based assignment; allow manual outside hours
        assert_office_open(allow_manual_outside_hours=True)
        if not assigned_by:
            assigned_by = frappe.session.user

        # Build eligible pool and exclude already-assigned users for this lead
        eligible_users = RoleAssignmentTracker.get_role_users(role_name)
        already_assigned = _get_assigned_users_for_document("CRM Lead", lead_name)
        available_users = [u for u in eligible_users if u not in already_assigned]

        if not available_users:
            return {
                "success": False,
                "error": f"All eligible users for role '{role_name}' are already assigned to this lead",
                "all_assigned": True,
                "eligible_users": eligible_users,
                "assigned_users": list(already_assigned),
            }

        # Get the next user from the filtered list using the tracker
        assigned_user = RoleAssignmentTracker.assign_to_next_user_from_list(
            role_name=role_name,
            user_list=available_users,
            document_type="CRM Lead",
            document_name=lead_name,
            assigned_by=assigned_by,
        )
        
        # Update the lead assigned_role directly in database to avoid timestamp conflicts
        frappe.db.set_value("CRM Lead", lead_name, "assigned_role", role_name)
        
        # Also update the assign_to field with the assigned user's name
        frappe.db.set_value("CRM Lead", lead_name, "assign_to", assigned_user)
        
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
        
        # Commit the database changes
        frappe.db.commit()
        
        task_created = None
        # Prefer modifying existing open task for this lead; create only if none exists and not skipped
        existing_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "reference_doctype": "CRM Lead",
                "reference_docname": lead_name,
                "status": ["not in", ["Done", "Canceled"]],
            },
            fields=["name", "_assign", "due_date"],
            order_by="creation asc",
            limit=1,
        )

        # Ensure parent _assign includes the user
        try:
            parent_assign_json = frappe.db.get_value("CRM Lead", lead_name, "_assign")
            parent_assign = json.loads(parent_assign_json) if parent_assign_json else []
            if not isinstance(parent_assign, list):
                parent_assign = []
        except Exception:
            parent_assign = []
        if assigned_user not in parent_assign:
            parent_assign.append(assigned_user)
            frappe.db.set_value("CRM Lead", lead_name, "_assign", json.dumps(parent_assign))

        task_doc = None
        if existing_tasks:
            # Reassign existing task
            task_doc = frappe.get_doc("CRM Task", existing_tasks[0].name)
            # Update assignment history on task
            assign_list = []
            try:
                assign_list = json.loads(task_doc._assign) if task_doc._assign else []
                if not isinstance(assign_list, list):
                    assign_list = []
            except Exception:
                assign_list = []
            if assigned_user not in assign_list:
                assign_list.append(assigned_user)
            task_doc.assigned_to = assigned_user
            # Extend due date to give time
            task_doc.due_date = frappe.utils.now_datetime() + timedelta(days=1)
            task_doc.save(ignore_permissions=True)
            frappe.db.set_value("CRM Task", task_doc.name, "_assign", json.dumps(assign_list))

            # Parent _assign already updated above

            # Comment on parent about manual reassignment
            comment_content = (
                f"🔄 Lead Reassigned\n\nNew Assignee: {get_fullname(assigned_user)}\nReason: Manual assignment"
            )
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "CRM Lead",
                "reference_name": lead_name,
                "content": comment_content,
                "comment_email": assigned_by,
            }).insert(ignore_permissions=True)

            # Send enhanced task notification with lead context
            try:
                lead_doc = frappe.get_doc("CRM Lead", lead_name)
                from crm.api.lead_notifications import create_task_with_lead_notification
                create_task_with_lead_notification(task_doc, lead_doc, is_assignment=True)
            except Exception:
                pass

        elif not skip_task_creation:
            # Create follow-up task if none exists
            lead_details = frappe.db.get_value("CRM Lead", lead_name, ["first_name", "last_name"], as_dict=True)
            first_name = lead_details.get("first_name") or ""
            last_name = lead_details.get("last_name") or ""
            task_doc = frappe.get_doc({
                "doctype": "CRM Task",
                "title": f"Follow up on lead: {first_name or lead_name}",
                "assigned_to": assigned_user,
                "reference_doctype": "CRM Lead",
                "reference_docname": lead_name,
                "description": f"Task created for lead assignment to {role_name} role - {first_name} {last_name}".strip(),
                "priority": "Medium",
                "status": "Todo",
                "due_date": frappe.utils.now_datetime(),
            })
            task_doc.insert(ignore_permissions=True)
            task_created = task_doc.name
        
        # Emit activity update to refresh frontend
        emit_activity_update("CRM Lead", lead_name)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "assigned_user": assigned_user,
            "role": role_name,
            "message": f"Lead successfully assigned to {assigned_user} from {role_name} role",
            "task_created": task_created
        }
        
    except Exception as e:
        frappe.log_error(f"Role assignment failed: {str(e)}", "Role Assignment Error")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def assign_to_user(lead_name, user_name, assigned_by=None):
    """Assign a lead directly to a specific user (Admin Only)"""
    try:
        # Check if user has admin permissions
        if not frappe.has_permission("Role Assignment Tracker", "write"):
            frappe.throw("Insufficient permissions for direct user assignment")
        
        if not assigned_by:
            assigned_by = frappe.session.user
        
        # Validate user exists and is enabled
        if not frappe.db.exists("User", user_name):
            frappe.throw(f"User {user_name} does not exist")
        
        if not frappe.db.get_value("User", user_name, "enabled"):
            frappe.throw(f"User {user_name} is not enabled")
        
        # Update the lead assigned_role directly in database to avoid timestamp conflicts
        frappe.db.set_value("CRM Lead", lead_name, "assigned_role", "Direct Assignment")
        
        # Also update the assign_to field with the assigned user's name
        frappe.db.set_value("CRM Lead", lead_name, "assign_to", user_name)
        
        # Use Frappe's standard assignment system
        frappe.desk.form.assign_to.add({
            "assign_to": [user_name],
            "doctype": "CRM Lead",
            "name": lead_name,
            "description": f"Lead directly assigned to {user_name} - admin assignment"
        })
        
        # Create activity timeline entry for the assignment
        assigned_user_name = get_fullname(user_name)
        assigned_by_name = get_fullname(assigned_by)
        
        # Create assignment activity
        assignment_comment = frappe.get_doc({
            "doctype": "Comment", 
            "comment_type": "Comment",
            "reference_doctype": "CRM Lead",
            "reference_name": lead_name,
            "content": f"🎯 <strong>{assigned_by_name}</strong> directly assigned this lead to <strong>{assigned_user_name}</strong> (admin assignment)",
            "comment_email": assigned_by,
            "creation": frappe.utils.now(),
        })
        assignment_comment.insert(ignore_permissions=True)
        
        # Emit activity update to refresh frontend
        emit_activity_update("CRM Lead", lead_name)
        
        # Commit the database changes
        frappe.db.commit()
        
        # Prefer modifying existing open task for this lead; create only if none exists
        existing_tasks = frappe.get_list(
            "CRM Task",
            filters={
                "reference_doctype": "CRM Lead",
                "reference_docname": lead_name,
                "status": ["not in", ["Done", "Canceled"]],
            },
            fields=["name", "_assign", "due_date"],
            order_by="creation asc",
            limit=1,
        )

        task_doc = None
        if existing_tasks:
            task_doc = frappe.get_doc("CRM Task", existing_tasks[0].name)
            assign_list = []
            try:
                assign_list = json.loads(task_doc._assign) if task_doc._assign else []
                if not isinstance(assign_list, list):
                    assign_list = []
            except Exception:
                assign_list = []
            if user_name not in assign_list:
                assign_list.append(user_name)
            task_doc.assigned_to = user_name
            task_doc.due_date = frappe.utils.now_datetime() + timedelta(days=1)
            task_doc.save(ignore_permissions=True)
            frappe.db.set_value("CRM Task", task_doc.name, "_assign", json.dumps(assign_list))

            # Ensure parent _assign includes the user
            parent_assign_json = frappe.db.get_value("CRM Lead", lead_name, "_assign")
            try:
                parent_assign = json.loads(parent_assign_json) if parent_assign_json else []
                if not isinstance(parent_assign, list):
                    parent_assign = []
            except Exception:
                parent_assign = []
            if user_name not in parent_assign:
                parent_assign.append(user_name)
                frappe.db.set_value("CRM Lead", lead_name, "_assign", json.dumps(parent_assign))

            # Comment on parent about manual reassignment
            comment_content = (
                f"🔄 Lead Reassigned\n\nNew Assignee: {get_fullname(user_name)}\nReason: Manual assignment"
            )
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "CRM Lead",
                "reference_name": lead_name,
                "content": comment_content,
                "comment_email": assigned_by,
            }).insert(ignore_permissions=True)

            # Send enhanced task notification with lead context
            try:
                lead_doc = frappe.get_doc("CRM Lead", lead_name)
                from crm.api.lead_notifications import create_task_with_lead_notification
                create_task_with_lead_notification(task_doc, lead_doc, is_assignment=True)
            except Exception:
                pass

        else:
            # Create follow-up task if none exists
            lead_details = frappe.db.get_value("CRM Lead", lead_name, ["first_name", "last_name"], as_dict=True)
            first_name = lead_details.get("first_name") or ""
            last_name = lead_details.get("last_name") or ""
            task_doc = frappe.get_doc({
                "doctype": "CRM Task",
                "title": f"Follow up on lead: {first_name or lead_name}",
                "assigned_to": user_name,
                "reference_doctype": "CRM Lead",
                "reference_docname": lead_name,
                "description": f"Task created for direct lead assignment to {user_name} - {first_name} {last_name}".strip(),
                "priority": "Medium",
                "status": "Todo",
            })
            task_doc.insert(ignore_permissions=True)
        
        # Emit activity update to refresh frontend
        emit_activity_update("CRM Lead", lead_name)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "assigned_user": user_name,
            "role": "Direct Assignment",
            "message": f"Lead successfully assigned directly to {user_name}",
            "task_created": task_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Direct user assignment failed: {str(e)}", "Role Assignment Error")
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
def get_roles_all_assigned_status(roles=None, doc_name=None, doctype="CRM Lead"):
    """Batch version of check_all_role_users_assigned for multiple roles.
    Returns a mapping { role: bool } indicating whether all eligible users for that role
    have already been assigned to the given document (current ToDos + _assign + history)."""
    try:
        if isinstance(roles, str):
            try:
                roles = json.loads(roles)
            except Exception:
                roles = []
        if not roles:
            roles = [
                'Sales User', 'Sales Manager', 'Support User', 'Support Manager'
            ]

        # Fetch eligible users for all roles in one query
        role_rows = frappe.get_all(
            "Has Role",
            filters={
                "role": ["in", roles],
                "parent": ["not in", ["Administrator", "admin@example.com"]],
            },
            fields=["role", "parent"],
        )

        all_user_ids = list({row.parent for row in role_rows})
        enabled_users = set()
        if all_user_ids:
            enabled = frappe.get_all(
                "User", filters={"name": ["in", all_user_ids], "enabled": 1}, fields=["name"]
            )
            enabled_users = {u.name for u in enabled}

        role_to_eligible = {r: [] for r in roles}
        for row in role_rows:
            if row.parent in enabled_users:
                role_to_eligible.setdefault(row.role, []).append(row.parent)

        # Current assignments: ToDo + _assign
        assigned_now = set()
        if doc_name:
            try:
                todos = frappe.get_all(
                    "ToDo",
                    filters={
                        "reference_type": doctype,
                        "reference_name": doc_name,
                        "status": ["in", ["Open", "Working"]],
                    },
                    fields=["allocated_to"],
                )
                assigned_now.update([t.allocated_to for t in todos if t.allocated_to])
            except Exception:
                pass

            try:
                parent = frappe.get_doc(doctype, doc_name)
                if parent and getattr(parent, "_assign", None):
                    arr = json.loads(parent._assign) if isinstance(parent._assign, str) else parent._assign
                    if isinstance(arr, list):
                        assigned_now.update([u for u in arr if isinstance(u, str) and u])
            except Exception:
                pass

        # History for all roles in one query
        trackers = frappe.get_all(
            "Role Assignment Tracker",
            filters={"name": ["in", roles]},
            fields=["name", "assignment_history"],
        )
        role_to_historical = {r: set() for r in roles}
        for tr in trackers:
            hist = []
            if tr.assignment_history:
                try:
                    hist = json.loads(tr.assignment_history) if isinstance(tr.assignment_history, str) else tr.assignment_history
                except Exception:
                    hist = []
            for entry in hist:
                if entry.get('document_name') == doc_name and entry.get('document_type') == doctype:
                    uid = entry.get('user')
                    if uid:
                        role_to_historical.setdefault(tr.name, set()).add(uid)

        # Compose final map
        result = {}
        all_assigned_users_now = assigned_now
        for role in roles:
            eligible = role_to_eligible.get(role, [])
            if not eligible:
                result[role] = False
                continue
            historical = role_to_historical.get(role, set())
            combined = set(eligible) & (all_assigned_users_now | historical | set(eligible))
            # all assigned if every eligible user is present in assigned_now ∪ historical
            result[role] = all(uid in (all_assigned_users_now | historical) for uid in eligible)

        return {"status": result}
    except Exception as e:
        frappe.log_error(f"Error in get_roles_all_assigned_status: {str(e)}", "Role Assignment Error")
        return {"status": {}}

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
        tracker = RoleAssignmentTracker.get_or_create_tracker(role_name)
        
        if not tracker.assignment_history:
            return []
        
        history = json.loads(tracker.assignment_history) if isinstance(tracker.assignment_history, str) else tracker.assignment_history

        # Only last N entries, default to 5 for UI efficiency
        effective_limit = int(limit) if limit else 5
        if effective_limit <= 0:
            effective_limit = 5

        subset = history[-effective_limit:]

        # Bulk fetch user names (avoid per-entry get_doc)
        user_ids = list({h.get('user') for h in subset if h.get('user')})
        if user_ids:
            users = frappe.get_all(
                "User",
                filters={"name": ["in", user_ids]},
                fields=["name", "full_name", "email"],
            )
            name_map = {u.name: (u.full_name or u.name, u.email) for u in users}
            for entry in subset:
                uid = entry.get('user')
                if uid and uid in name_map:
                    full_name, email = name_map[uid]
                    entry['user_full_name'] = full_name
                    entry['user_email'] = email

        return subset
        
    except Exception as e:
        frappe.log_error(f"Error getting assignment history: {str(e)}", "Role Assignment Error")
        return []

@frappe.whitelist()
def check_all_role_users_assigned(role_name, doc_name, doctype="CRM Lead"):
    """Check if all eligible users for a role have been assigned to a specific document"""
    try:
        # Get all users with this role
        users = frappe.get_all("Has Role", 
            filters={"role": role_name, "parent": ["!=", "Administrator"]},
            fields=["parent"]
        )
        
        eligible_users = [user.parent for user in users if frappe.db.get_value("User", user.parent, "enabled")]
        
        if not eligible_users:
            return {
                "all_assigned": False,
                "eligible_users": [],
                "assigned_users": [],
                "message": f"No eligible users found for role: {role_name}"
            }
        
        # Get current assignments for this document
        current_assignments = frappe.get_all("ToDo",
            filters={
                "reference_type": doctype,
                "reference_name": doc_name,
                "status": ["in", ["Open", "Working"]]
            },
            fields=["allocated_to"]
        )
        
        currently_assigned_users = [assignment.allocated_to for assignment in current_assignments if assignment.allocated_to]
        
        # Get assignment history for this role
        tracker = RoleAssignmentTracker.get_or_create_tracker(role_name)
        assignment_history = []
        
        if tracker.assignment_history:
            try:
                assignment_history = json.loads(tracker.assignment_history) if isinstance(tracker.assignment_history, str) else tracker.assignment_history
            except json.JSONDecodeError:
                assignment_history = []
        
        # Find users assigned to this specific document in history
        historically_assigned_users = []
        for entry in assignment_history:
            if entry.get('document_name') == doc_name and entry.get('document_type') == doctype:
                if entry.get('user') and entry['user'] not in historically_assigned_users:
                    historically_assigned_users.append(entry['user'])
        
        # Combine current and historical assignments
        all_assigned_users = list(set(currently_assigned_users + historically_assigned_users))
        
        # Check if all eligible users have been assigned at some point
        all_assigned = all(user in all_assigned_users for user in eligible_users)
        
        return {
            "all_assigned": all_assigned,
            "eligible_users": eligible_users,
            "assigned_users": all_assigned_users,
            "currently_assigned": currently_assigned_users,
            "historically_assigned": historically_assigned_users,
            "message": f"All eligible users from '{role_name}' role have been assigned to this {doctype.lower()}" if all_assigned else f"Some eligible users from '{role_name}' role are still available for assignment"
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking role assignment status: {str(e)}", "Role Assignment Error")
        return {
            "all_assigned": False,
            "error": str(e)
        } 

@frappe.whitelist()
def bulk_assign_leads(lead_names, assign_to_users, assigned_by=None):
    """Bulk assign leads to users and update assign_to field"""
    try:
        if not assigned_by:
            assigned_by = frappe.session.user
        
        if isinstance(lead_names, str):
            lead_names = json.loads(lead_names)
        
        if isinstance(assign_to_users, str):
            assign_to_users = json.loads(assign_to_users)
        
        results = []
        
        for lead_name in lead_names:
            try:
                # Validate lead exists
                if not frappe.db.exists("CRM Lead", lead_name):
                    results.append({
                        "lead_name": lead_name,
                        "success": False,
                        "error": "Lead does not exist"
                    })
                    continue
                
                # Use Frappe's standard assignment system
                frappe.desk.form.assign_to.add({
                    "assign_to": assign_to_users,
                    "doctype": "CRM Lead",
                    "name": lead_name,
                    "description": f"Bulk assignment by {assigned_by}"
                })
                
                # Update the assign_to field with the first assigned user (for backward compatibility)
                if assign_to_users and len(assign_to_users) > 0:
                    frappe.db.set_value("CRM Lead", lead_name, "assign_to", assign_to_users[0])
                
                # Create activity timeline entry for the assignment
                assigned_user_names = [get_fullname(user) for user in assign_to_users]
                assigned_by_name = get_fullname(assigned_by)
                
                assignment_comment = frappe.get_doc({
                    "doctype": "Comment", 
                    "comment_type": "Comment",
                    "reference_doctype": "CRM Lead",
                    "reference_name": lead_name,
                    "content": f"🎯 <strong>{assigned_by_name}</strong> bulk assigned this lead to <strong>{', '.join(assigned_user_names)}</strong>",
                    "comment_email": assigned_by,
                    "creation": frappe.utils.now(),
                })
                assignment_comment.insert(ignore_permissions=True)
                
                results.append({
                    "lead_name": lead_name,
                    "success": True,
                    "assigned_users": assign_to_users
                })
                
            except Exception as e:
                results.append({
                    "lead_name": lead_name,
                    "success": False,
                    "error": str(e)
                })
        
        # Emit activity updates for all leads
        for lead_name in lead_names:
            emit_activity_update("CRM Lead", lead_name)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "results": results,
            "message": f"Bulk assignment completed for {len(lead_names)} leads"
        }
        
    except Exception as e:
        frappe.log_error(f"Bulk assignment failed: {str(e)}", "Role Assignment Error")
        return {
            "success": False,
            "error": str(e)
        } 