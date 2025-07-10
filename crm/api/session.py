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

	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True

		user.is_manager = "Sales Manager" in frappe.get_roles(user.name)
		user.is_admin = user.name == "Administrator"

		user.roles = frappe.get_roles(user.name)

		user.role = ""

		if "System Manager" in user.roles:
			user.role = "System Manager"
		elif "Sales Manager" in user.roles:
			user.role = "Sales Manager"
		elif "Sales User" in user.roles:
			user.role = "Sales User"
		elif "Support User" in user.roles:
			user.role = "Support User"
		elif "Guest" in user.roles:
			user.role = "Guest"

		if frappe.session.user == user.name:
			user.session_user = True

		user.is_agent = frappe.db.exists("CRM Telephony Agent", {"user": user.name})

	crm_users = []

	# crm users are users with role Sales User, Sales Manager, or Support User
	for user in users:
		if any(role in user.roles for role in ["Sales User", "Sales Manager", "Support User"]):
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
