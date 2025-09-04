import frappe


@frappe.whitelist()
def get_users():
	users = frappe.qb.get_query(
		"User",
		fields=[
			"name",
			"email",
			"enabled",
			"user_image",
			"first_name",
			"last_name",
			"full_name",
			"user_type",
		],
		order_by="full_name asc",
		distinct=True,
	).run(as_dict=1)

	# Fetch enabled roles and which have desk access
	enabled_roles = frappe.get_all(
		"Role",
		filters={"disabled": 0},
		fields=["name", "desk_access"],
	)
	enabled_role_names = {r.name for r in enabled_roles}
	enabled_desk_roles = {r.name for r in enabled_roles if int(r.desk_access or 0) == 1}

	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True

		user_roles = frappe.get_roles(user.name)
		user.is_manager = ("Sales Manager" in user_roles) or ("Support Manager" in user_roles)
		user.is_admin = user.name == "Administrator"

		user.roles = user_roles

		# Primary role selection (generic):
		# 1) System Manager, else first enabled desk-access role, else first enabled role, else Guest
		user.role = ""
		if "System Manager" in user_roles:
			user.role = "System Manager"
		else:
			desk_matches = [r for r in user_roles if r in enabled_desk_roles]
			if desk_matches:
				user.role = desk_matches[0]
			else:
				any_enabled = [r for r in user_roles if r in enabled_role_names]
				if any_enabled:
					user.role = any_enabled[0]
				elif "Guest" in user_roles:
					user.role = "Guest"

		if frappe.session.user == user.name:
			user.session_user = True

		user.is_agent = frappe.db.exists("CRM Telephony Agent", {"user": user.name})

	crm_users = []

	# CRM users are System Managers or users with any enabled desk-access role
	for user in users:
		if ("System Manager" in user.roles) or any(role in enabled_desk_roles for role in user.roles):
			crm_users.append(user)

	return users, crm_users


@frappe.whitelist()
def get_organizations():
	organizations = frappe.qb.get_query(
		"CRM Organization",
		fields=["*"],
		order_by="name asc",
		distinct=True,
	).run(as_dict=1)

	return organizations
