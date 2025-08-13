import frappe


@frappe.whitelist()
def add_existing_users(users, role="Sales User"):
	"""
	Add existing users to the CRM by assigning them a role (Sales User or Sales Manager).
	:param users: List of user names to be added
	"""
	frappe.only_for(["System Manager", "Sales Manager"])
	users = frappe.parse_json(users)

	for user in users:
		add_user(user, role)


@frappe.whitelist()
def update_user_role(user, new_role):
	"""
	Update the role of the user to Sales Manager, Sales User, System Manager, or Support User.
	Only Administrator or System Manager can change user roles.
	:param user: The name of the user
	:param new_role: The new role to assign
	"""

	# Permission: Administrator or System Manager
	if not (frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()):
		frappe.throw("Only Administrator or System Manager can change user roles")

	allowed_roles = [
		"System Manager",
		"Sales Manager",
		"Sales User",
		"Support User",
		"Support Manager",
	]
	if new_role not in allowed_roles:
		frappe.throw("Cannot assign this role")

	user_doc = frappe.get_doc("User", user)

	# Remove all CRM-related roles first
	user_doc.remove_roles(*allowed_roles)

	# Then add only the selected role (no manager → user inheritance)
	if new_role == "System Manager":
		user_doc.append_roles("System Manager")
		user_doc.set("block_modules", [])
	elif new_role == "Sales Manager":
		user_doc.append_roles("Sales Manager")
	elif new_role == "Support Manager":
		user_doc.append_roles("Support Manager")
	elif new_role == "Sales User":
		user_doc.append_roles("Sales User")
		update_module_in_user(user_doc, "FCRM")
	elif new_role == "Support User":
		user_doc.append_roles("Support User")
		update_module_in_user(user_doc, "FCRM")

	user_doc.save(ignore_permissions=True)

	# Safety: deduplicate Has Role entries so a user has at most one row per role
	_dedupe_has_role_rows(user, allowed_roles)
	return {"success": True}


@frappe.whitelist()
def add_user(user, role):
	"""
	Add a user means adding role (Sales User or/and Sales Manager) to the user.
	:param user: The name of the user to be added
	:param role: The role to be assigned (Sales User or Sales Manager)
	"""
	update_user_role(user, role)


@frappe.whitelist()
def remove_user(user):
	"""
	Remove a user means removing Sales User & Sales Manager roles from the user.
	:param user: The name of the user to be removed
	"""
	frappe.only_for(["System Manager", "Sales Manager"])

	user_doc = frappe.get_doc("User", user)
	roles = [d.role for d in user_doc.roles]

	# Remove all CRM roles
	to_remove = [r for r in ("System Manager", "Sales Manager", "Sales User", "Support Manager", "Support User") if r in roles]
	if to_remove:
		user_doc.remove_roles(*to_remove)

	user_doc.save(ignore_permissions=True)
	_dedupe_has_role_rows(user, ("System Manager", "Sales Manager", "Sales User", "Support Manager", "Support User"))
	frappe.msgprint(f"User {user} has been removed from CRM roles.")


def update_module_in_user(user, module):
	block_modules = frappe.get_all(
		"Module Def",
		fields=["name as module"],
		filters={"name": ["!=", module]},
	)

	if block_modules:
		user.set("block_modules", block_modules)


def _dedupe_has_role_rows(user, roles):
	"""Ensure there is at most one `Has Role` row per (user, role). Deletes extras, keeps oldest."""
	try:
		for role in roles:
			rows = frappe.get_all(
				"Has Role",
				filters={"parent": user, "role": role},
				fields=["name"],
				order_by="creation asc",
			)
			if len(rows) > 1:
				keep = rows[0]["name"]
				for r in rows[1:]:
					frappe.db.delete("Has Role", r["name"])
		frappe.db.commit()
	except Exception:
		# Non-fatal; log and continue
		frappe.log_error(f"Failed deduping Has Role for user {user}", "Has Role Dedup")
