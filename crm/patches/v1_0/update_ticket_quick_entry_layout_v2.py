import json
import frappe


def execute():
	"""Update CRM Ticket Quick Entry layout to match provided sketch:

	Layout (3 columns per section):
	Row 1: Ticket Source | Department | Ticket Owner
	Row 2: Subjects      | Description| Priority
	Row 3: Assign To Role| Status     | (empty)

	Also ensure `issue_type` is not present in the Quick Entry layout.
	"""

	layout = (
		frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
		if frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": "Quick Entry"})
		else frappe.new_doc("CRM Fields Layout")
	)

	layout.dt = "CRM Ticket"
	layout.type = "Quick Entry"

	new_layout = [
		{
			"name": "details",
			"label": "Details",
			"sections": [
				{
					"name": "contact_information",
					"label": "Contact Information",
					"columns": [
						{"name": "contact_col_1", "fields": ["first_name", "last_name", "pan_card_number"]},
						{"name": "contact_col_2", "fields": ["email", "mobile_no", "aadhaar_card_number"]},
						{"name": "contact_col_3", "fields": ["marital_status", "date_of_birth", "anniversary"]},
					],
				},
				{
					"name": "ticket_information",
					"label": "Ticket Information",
					"columns": [
						{"name": "ticket_col_1", "fields": ["ticket_owner", "ticket_subjects"]},
						{"name": "ticket_col_2", "fields": ["description", "status"]},
						{"name": "ticket_col_3", "fields": ["ticket_source", "priority"]},
					],
				},
			],
		}
	]

	layout.layout = json.dumps(new_layout)
	layout.save(ignore_permissions=True)
	frappe.db.commit()


