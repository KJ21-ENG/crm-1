import json
import frappe


def execute():
	"""Update CRM Ticket Quick Entry layout to use a 3-column Ticket Information section.

	This patch standardizes the Ticket Quick Entry modal to mirror the 3-column
	layout used by Contact Information, improving scanability and reducing scroll.
	It updates/creates a `CRM Fields Layout` record for:
	- dt: "CRM Ticket"
	- type: "Quick Entry"

	Notes:
	- We intentionally do not include `assigned_to` in the layout to respect
	  prior patches that removed it.
	- `assign_to_role` is injected dynamically in the modal after `ticket_owner`,
	  so we ensure `ticket_owner` is present in the Ticket Information column.
	"""

	# Fetch or create the layout doc
	layout = (
		frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
		if frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
		else frappe.new_doc("CRM Fields Layout")
	)

	layout.dt = "CRM Ticket"
	layout.type = "Quick Entry"

	# Build a 3-column layout
	new_layout = [
		{
			"name": "details",
			"label": "Details",
			"sections": [
				{
					"name": "contact_information",
					"label": "Contact Information",
					"columns": [
						{
							"name": "contact_col_1",
							"fields": [
								"first_name",
								"last_name",
								"pan_card_number",
							]
						},
						{
							"name": "contact_col_2",
							"fields": [
								"email",
								"mobile_no",
								"aadhaar_card_number",
							]
						},
						{
							"name": "contact_col_3",
							"fields": [
								"marital_status",
								"date_of_birth",
								"anniversary",
							]
						},
					],
				},
				{
					"name": "ticket_information",
					"label": "Ticket Information",
					"columns": [
						{
							"name": "ticket_col_1",
							"fields": [
								"ticket_subjects",
								"description",
							]
						},
						{
							"name": "ticket_col_2",
							"fields": [
								"priority",
								"issue_type",
								"department",
							]
						},
						{
							"name": "ticket_col_3",
							"fields": [
								"ticket_source",
								"ticket_owner",
								"status",
							]
						},
					],
				},
			],
		}
	]

	layout.layout = json.dumps(new_layout)
	layout.save(ignore_permissions=True)
	frappe.db.commit()


