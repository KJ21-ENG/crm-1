import frappe

from crm.api.doc import get_assigned_users, get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.customers import get_ticket_with_customer_data


@frappe.whitelist()
def get_ticket(name):
	ticket = frappe.get_doc("CRM Ticket", name)
	ticket.check_permission("read")

	# Get ticket data with customer data merged
	ticket_data = get_ticket_with_customer_data(name)
	if not ticket_data:
		ticket_data = ticket.as_dict()

	ticket_data["fields_meta"] = get_fields_meta("CRM Ticket")
	ticket_data["_form_script"] = get_form_script("CRM Ticket")
	ticket_data["_assign"] = get_assigned_users("CRM Ticket", name)

	return ticket_data


@frappe.whitelist()
def create_ticket_from_call_log(call_log, ticket_details=None):
	ticket = frappe.new_doc("CRM Ticket")
	ticket_details = frappe.parse_json(ticket_details or "{}")

	if not ticket_details.get("assigned_to"):
		ticket_details["assigned_to"] = frappe.session.user
	if not ticket_details.get("mobile_no"):
		# Use customer field instead of from
		ticket_details["mobile_no"] = call_log.get("customer") or call_log.get("from") or ""
	if not ticket_details.get("first_name"):
		# Use customer_name if available
		if call_log.get("customer_name"):
			ticket_details["first_name"] = call_log.get("customer_name")
		else:
			ticket_details["first_name"] = "Customer from call " + (
				ticket_details.get("mobile_no") or call_log.get("name")
			)
	if not ticket_details.get("ticket_subject"):
		ticket_details["ticket_subject"] = "Support request from call " + (
			ticket_details.get("mobile_no") or call_log.get("name")
		)

	ticket.update(ticket_details)
	ticket.save(ignore_permissions=True)

	# link call log with ticket
	call_log = frappe.get_doc("CRM Call Log", call_log.get("name"))
	call_log.link_with_reference_doc("CRM Ticket", ticket.name)
	call_log.save(ignore_permissions=True)

	return ticket.name 