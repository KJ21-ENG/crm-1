import frappe


@frappe.whitelist()
def add_existing_users(users, role="Sales User"):
	"""
	Add existing users to the CRM by assigning them a role.
	:param users: List of user names to be added
	"""
	frappe.only_for(["System Manager", "Sales Manager"])
	users = frappe.parse_json(users)

	for user in users:
		add_user(user, role)


@frappe.whitelist()
def update_user_role(user, new_role):
	"""
	Update the role of the user to any enabled Role.
	Only Administrator or System Manager can change user roles.
	:param user: The name of the user
	:param new_role: The new role to assign
	"""

	# Permission: Administrator or System Manager
	if not (frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()):
		frappe.throw("Only Administrator or System Manager can change user roles")

	# Validate role exists and is enabled
	if not frappe.db.exists("Role", new_role):
		frappe.throw("Role does not exist")
	if frappe.db.get_value("Role", new_role, "disabled"):
		frappe.throw("Cannot assign a disabled role")

	user_doc = frappe.get_doc("User", user)

	# Remove all existing enabled roles that are CRM-related and also any role being newly assigned to avoid duplicates
	# We will not hardcode roles; simply ensure user gets exactly the requested role for CRM access semantics.
	current_roles = [d.role for d in user_doc.roles]
	if current_roles:
		user_doc.remove_roles(*current_roles)

	# Then add only the selected role
	user_doc.append_roles(new_role)

	# If FCRM module is present, make sure user can access it
	try:
		from crm.fcrm.doctype.fcrm_settings.fcrm_settings import FCRMSettings  # type: ignore
		# Best-effort update: unblock other modules to avoid UI lockout
		user_doc.set("block_modules", [])
	except Exception:
		pass

	user_doc.save(ignore_permissions=True)

	# Safety: deduplicate Has Role entries so a user has at most one row per role
	_dedupe_has_role_rows(user, [new_role])
	return {"success": True}


@frappe.whitelist()
def add_user(user, role):
	"""
	Assign a role to the user (any enabled Role).
	:param user: The name of the user to be added
	:param role: The role to be assigned
	"""
	update_user_role(user, role)


@frappe.whitelist()
def remove_user(user):
	"""
	Remove user roles related to CRM usage.
	:param user: The name of the user to be removed
	"""
	frappe.only_for(["System Manager", "Sales Manager"])

	user_doc = frappe.get_doc("User", user)
	roles = [d.role for d in user_doc.roles]

	# Remove all roles (conservative for CRM admin usage)
	if roles:
		user_doc.remove_roles(*roles)

	user_doc.save(ignore_permissions=True)
	_dedupe_has_role_rows(user, roles)
	frappe.msgprint(f"User {user} has had roles removed.")


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
