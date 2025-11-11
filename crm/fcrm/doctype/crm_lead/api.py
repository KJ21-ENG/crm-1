import frappe

from crm.api.doc import get_assigned_users, get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.customers import get_lead_with_customer_data


@frappe.whitelist()
def get_lead(name):
	lead = frappe.get_doc("CRM Lead", name)
	lead.check_permission("read")

	# Get lead data with customer data merged
	lead_data = get_lead_with_customer_data(name)
	if not lead_data:
		lead_data = lead.as_dict()

	lead_data["fields_meta"] = get_fields_meta("CRM Lead")
	lead_data["_form_script"] = get_form_script("CRM Lead")
	return lead_data
