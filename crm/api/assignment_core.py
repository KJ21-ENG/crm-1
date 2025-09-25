import frappe
import json
from datetime import timedelta
from frappe.utils import now_datetime, get_fullname

from crm.api.activities import emit_activity_update
from crm.fcrm.doctype.role_assignment_tracker.role_assignment_tracker import (
	RoleAssignmentTracker,
)


EXCLUDED_USER_IDS = {"Administrator", "admin@example.com"}


def _normalize_json_list(value):
	"""Return a Python list from a JSON string/list or empty list on failure."""
	if not value:
		return []
	try:
		if isinstance(value, str):
			parsed = frappe.parse_json(value)
		else:
			parsed = value
		return parsed if isinstance(parsed, list) else []
	except Exception:
		try:
			return json.loads(value) if isinstance(value, str) else []
		except Exception:
			return []


def _get_parent_assigned_users(doctype: str, docname: str) -> set:
	"""Collect users already assigned to the document via _assign and ToDo (Open/Working)."""
	assigned = set()
	# From parent _assign
	try:
		parent = frappe.get_doc(doctype, docname)
		arr = _normalize_json_list(getattr(parent, "_assign", None))
		assigned.update([u for u in arr if isinstance(u, str) and u])
	except Exception:
		pass

	# From ToDo entries
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
			user = (t.get("allocated_to") or "").strip()
			if user:
				assigned.add(user)
	except Exception:
		pass

	return assigned


def _get_eligible_users_for_role(role_name: str) -> list:
	"""Source-of-truth user list for a role from Has Role, filtered and enabled."""
	rows = frappe.get_all(
		"Has Role",
		filters={"role": role_name, "parent": ["not in", list(EXCLUDED_USER_IDS)]},
		fields=["parent"],
	)
	user_ids = [r.parent for r in rows]
	if not user_ids:
		return []
	# Only enabled users
	enabled = frappe.get_all("User", filters={"name": ["in", user_ids], "enabled": 1}, fields=["name"])
	return [u.name for u in enabled]


def _select_next_user_via_tracker(role_name: str, eligible_users: list, exclude_users: set) -> str:
	"""Pick next user from eligible_users not in exclude_users, respecting global round-robin order.

	- Keeps RoleAssignmentTracker order consistent
	- Skips invalid/disabled users defensively
	"""
	if not eligible_users:
		return None

	# Filter with exclusion
	candidates = [u for u in eligible_users if u not in exclude_users]
	if not candidates:
		return None

	# Use tracker to walk through global order but constrained to candidates
	selected = RoleAssignmentTracker.assign_to_next_user_from_list(
		role_name=role_name,
		user_list=candidates,
		document_type="",
		document_name="",
		assigned_by=frappe.session.user if frappe.session else None,
	)

	# Validate the selected user still exists and enabled
	if not (frappe.db.exists("User", selected) and frappe.db.get_value("User", selected, "enabled")):
		# Try a fallback from candidates
		for u in candidates:
			if frappe.db.exists("User", u) and frappe.db.get_value("User", u, "enabled"):
				return u
		return None

	return selected


def _ensure_parent_assignment(parent_doctype: str, parent_name: str, assigned_user: str, role_name: str):
	"""Update parent document assignment fields and _assign JSON consistently."""
	if parent_doctype == "CRM Lead":
		frappe.db.set_value("CRM Lead", parent_name, {
			"assigned_role": role_name,
			"assign_to": assigned_user,
		})
	elif parent_doctype == "CRM Ticket":
		frappe.db.set_value("CRM Ticket", parent_name, {
			"assigned_role": role_name,
			"assigned_to": assigned_user,
		})

	# Append to parent _assign
	current_assign = frappe.db.get_value(parent_doctype, parent_name, "_assign")
	arr = _normalize_json_list(current_assign)
	if assigned_user not in arr:
		arr.append(assigned_user)
		frappe.db.set_value(parent_doctype, parent_name, "_assign", frappe.as_json(arr))


def _ensure_parent_activity(parent_doctype: str, parent_name: str, assigned_user: str, role_name: str, assigned_by: str):
	assigned_user_name = get_fullname(assigned_user)
	assigned_by_name = get_fullname(assigned_by) if assigned_by else get_fullname(frappe.session.user)
	document_type = "Lead" if parent_doctype == "CRM Lead" else "Ticket"
	comment = frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": parent_doctype,
		"reference_name": parent_name,
		"content": f"🎯 <strong>{assigned_by_name}</strong> assigned this {document_type.lower()} to <strong>{assigned_user_name}</strong> from <strong>{role_name}</strong> role using round-robin assignment",
		"comment_email": assigned_by or frappe.session.user,
		"creation": frappe.utils.now(),
	})
	comment.insert(ignore_permissions=True)
	# Emit activity update
	emit_activity_update(parent_doctype, parent_name)


def _ensure_task(parent_doctype: str, parent_name: str, assigned_user: str, role_name: str, skip_task_creation: bool = False):
	"""Create or update the linked CRM Task to reflect the same assignee as the parent."""
	if skip_task_creation:
		return None

	# Try existing open task
	existing = frappe.get_list(
		"CRM Task",
		filters={
			"reference_doctype": parent_doctype,
			"reference_docname": parent_name,
			"status": ["not in", ["Done", "Canceled"]],
		},
		fields=["name", "_assign", "title"],
		order_by="creation asc",
		limit=1,
	)

	task_doc = None
	assign_list = []
	if existing:
		task_doc = frappe.get_doc("CRM Task", existing[0].name)
		assign_list = _normalize_json_list(task_doc._assign)
		if assigned_user not in assign_list:
			assign_list.append(assigned_user)
		task_doc.assigned_to = assigned_user
		# Update existing task to have a sooner due date of 2 hours
		task_doc.due_date = now_datetime() + timedelta(hours=2)
		task_doc.save(ignore_permissions=True)
		frappe.db.set_value("CRM Task", task_doc.name, "_assign", frappe.as_json(assign_list))
	else:
		# Create new task
		title = None
		if parent_doctype == "CRM Lead":
			lead = frappe.db.get_value("CRM Lead", parent_name, ["first_name", "last_name"], as_dict=True) or {}
			title = f"Follow up on lead: {(lead.get('first_name') or parent_name)}"
		else:
			details = frappe.db.get_value("CRM Ticket", parent_name, ["ticket_subject"], as_dict=True) or {}
			title = f"Handle ticket: {details.get('ticket_subject') or parent_name}"

		# Create new task with simple title and 2h due date, medium priority
		task_doc = frappe.get_doc({
			"doctype": "CRM Task",
			"title": title or ("Ticket Task" if parent_doctype == "CRM Ticket" else "Lead Task"),
			"assigned_to": assigned_user,
			"reference_doctype": parent_doctype,
			"reference_docname": parent_name,
			"description": f"Task created for {parent_doctype.replace('CRM ', '').lower()} assignment to {role_name} role - {parent_name}",
			"priority": "Medium",
			"status": "Todo",
			"due_date": now_datetime() + timedelta(hours=2),
		})
		task_doc.insert(ignore_permissions=True)

	return task_doc


def assign_document_by_role(document_type: str, document_name: str, role_name: str, assigned_by: str = None, skip_task_creation: bool = False):
	"""Unified role-based assignment for CRM Lead and CRM Ticket with consistent task sync.

	Returns dict: { success, assigned_user, role, message, task_created }
	"""
	if document_type not in ("CRM Lead", "CRM Ticket"):
		return {"success": False, "error": f"Unsupported document_type: {document_type}"}

	assigned_by = assigned_by or (frappe.session.user if frappe.session else None)

	# 1) Build eligible pool and current exclusions
	eligible = _get_eligible_users_for_role(role_name)
	if not eligible:
		return {"success": False, "error": f"No eligible users for role '{role_name}'"}

	exclude_users = _get_parent_assigned_users(document_type, document_name)

	# 2) Pick next user by round-robin (respecting tracker order)
	assigned_user = _select_next_user_via_tracker(role_name, eligible, exclude_users)
	if not assigned_user:
		return {
			"success": False,
			"error": f"All eligible users for role '{role_name}' are already assigned to this document",
			"all_assigned": True,
			"eligible_users": eligible,
			"assigned_users": list(exclude_users),
		}

	# 3) Update parent and activity
	_ensure_parent_assignment(document_type, document_name, assigned_user, role_name)
	_ensure_parent_activity(document_type, document_name, assigned_user, role_name, assigned_by)

	# 4) Create/update linked task
	task_doc = _ensure_task(document_type, document_name, assigned_user, role_name, skip_task_creation=skip_task_creation)

	# 5) System assignment using Frappe assignment framework (ToDo) for visibility
	frappe.desk.form.assign_to.add({
		"assign_to": [assigned_user],
		"doctype": document_type,
		"name": document_name,
		"description": f"{document_type.replace('CRM ', '')} assigned to {role_name} role - round-robin assignment",
	})

	# 6) Commit and return
	frappe.db.commit()

	return {
		"success": True,
		"assigned_user": assigned_user,
		"role": role_name,
		"message": f"{document_type.replace('CRM ', '')} successfully assigned to {assigned_user} from {role_name} role",
		"task_created": getattr(task_doc, "name", None) if task_doc else None,
	}


