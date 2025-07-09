# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from crm.integrations.api import get_contact_by_phone_number
from crm.utils import seconds_to_duration


class CRMCallLog(Document):
	def before_save(self):
		"""Auto-populate employee and customer fields based on call type"""
		self.populate_employee_customer_fields()
	
	def populate_employee_customer_fields(self):
		"""Populate employee and customer fields from caller/receiver data"""
		if self.type == "Outgoing":
			# Employee made the call
			self.employee = self.caller or self.employee
			self.customer = self.to
		elif self.type == "Incoming":
			# Employee received the call
			self.employee = self.receiver or self.employee
			self.customer = self.get('from')
		
		# Auto-populate customer name if not already set
		if self.customer and not self.customer_name:
			self.customer_name = self.get_customer_name_from_phone(self.customer)
	
	def get_customer_name_from_phone(self, phone_number):
		"""Get customer name from phone number by searching contacts and leads"""
		if not phone_number:
			return None
			
		try:
			# Clean phone number
			clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
			
			# Search in contacts first
			contact = frappe.db.get_value(
				'Contact',
				[
					['phone', 'like', f'%{clean_phone}%'],
					'or',
					['mobile_no', 'like', f'%{clean_phone}%']
				],
				['first_name', 'last_name'],
				as_dict=True
			)
			
			if contact:
				first_name = contact.get('first_name', '') or ''
				last_name = contact.get('last_name', '') or ''
				return f"{first_name} {last_name}".strip()
			
			# Search in leads
			lead = frappe.db.get_value(
				'Lead', 
				[
					['phone', 'like', f'%{clean_phone}%'],
					'or',
					['mobile_no', 'like', f'%{clean_phone}%']
				],
				'lead_name'
			)
			
			if lead:
				return lead
			
			# If no contact or lead found, generate default name
			return f"Lead from call {phone_number}"
			
		except Exception as e:
			frappe.logger().error(f"Error getting customer name for {phone_number}: {str(e)}")
			return f"Lead from call {phone_number}"

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Employee",
				"type": "Link",
				"key": "employee",
				"options": "User",
				"width": "9rem",
			},
			{
				"label": "Customer Name",
				"type": "Data",
				"key": "customer_name",
				"width": "10rem",
			},
			{
				"label": "Customer Phone",
				"type": "Data", 
				"key": "customer",
				"width": "9rem",
			},
			{
				"label": "Type",
				"type": "Select",
				"key": "type",
				"width": "9rem",
			},
			{
				"label": "Status",
				"type": "Select",
				"key": "status",
				"width": "9rem",
			},
			{
				"label": "Duration",
				"type": "Data",
				"key": "duration",
				"width": "8rem",
			},
			{
				"label": "Attended On",
				"type": "Datetime",
				"key": "start_time",
				"width": "8rem",
			},
		]

		rows = [
			"name",
			"employee",
			"customer_name",
			"customer",
			"type",
			"status",
			"duration",
			"start_time",
		]

		return {
			"columns": columns,
			"rows": rows,
			"order_by": "start_time desc",
		}

	def parse_list_data(calls):
		return [parse_call_log(call) for call in calls] if calls else []

	def has_link(self, doctype, name):
		for link in self.links:
			if link.link_doctype == doctype and link.link_name == name:
				return True

	def link_with_reference_doc(self, reference_doctype, reference_name):
		if self.has_link(reference_doctype, reference_name):
			return

		self.append("links", {"link_doctype": reference_doctype, "link_name": reference_name})


def parse_call_log(call):
	call["show_recording"] = False
	call["_duration"] = seconds_to_duration(call.get("duration"))
	
	# Use the new employee and customer fields for display
	employee_info = None
	customer_info = None
	
	if call.get("employee"):
		employee_data = frappe.db.get_values("User", call.get("employee"), ["full_name", "user_image"])[0] if call.get("employee") else [None, None]
		employee_info = {
			"label": employee_data[0] or "Unknown Employee",
			"image": employee_data[1],
		}
	
	# For customer info, prioritize customer_name over contact lookup
	customer_name = call.get("customer_name")
	if not customer_name and call.get("customer"):
		contact = get_contact_by_phone_number(call.get("customer"))
		customer_name = contact.get("full_name", "Unknown")
	
	customer_info = {
		"label": customer_name or "Unknown Customer",
		"image": None,  # Could be enhanced to get customer image
	}
	
	if call.get("type") == "Incoming":
		call["activity_type"] = "incoming_call"
		call["_caller"] = customer_info
		call["_receiver"] = employee_info
	elif call.get("type") == "Outgoing":
		call["activity_type"] = "outgoing_call"
		call["_caller"] = employee_info
		call["_receiver"] = customer_info

	return call


@frappe.whitelist()
def get_call_log(name):
	call = frappe.get_cached_doc(
		"CRM Call Log",
		name,
		fields=[
			"name",
			"employee",
			"customer",
			"customer_name",
			"caller",
			"receiver",
			"duration",
			"type",
			"status",
			"from",
			"to",
			"note",
			"recording_url",
			"reference_doctype",
			"reference_docname",
			"creation",
		],
	).as_dict()

	call = parse_call_log(call)

	notes = []
	tasks = []

	if call.get("note"):
		note = frappe.get_cached_doc("FCRM Note", call.get("note")).as_dict()
		notes.append(note)

	if call.get("reference_doctype") and call.get("reference_docname"):
		if call.get("reference_doctype") == "CRM Lead":
			call["_lead"] = call.get("reference_docname")
		elif call.get("reference_doctype") == "CRM Deal":
			call["_deal"] = call.get("reference_docname")

	if call.get("links"):
		for link in call.get("links"):
			if link.get("link_doctype") == "CRM Task":
				task = frappe.get_cached_doc("CRM Task", link.get("link_name")).as_dict()
				tasks.append(task)
			elif link.get("link_doctype") == "FCRM Note":
				note = frappe.get_cached_doc("FCRM Note", link.get("link_name")).as_dict()
				notes.append(note)
			elif link.get("link_doctype") == "CRM Lead":
				call["_lead"] = link.get("link_name")
			elif link.get("link_doctype") == "CRM Deal":
				call["_deal"] = link.get("link_name")

	call["_tasks"] = tasks
	call["_notes"] = notes
	return call


@frappe.whitelist()
def create_lead_from_call_log(call_log, lead_details=None):
	lead = frappe.new_doc("CRM Lead")
	lead_details = frappe.parse_json(lead_details or "{}")

	if not lead_details.get("lead_owner"):
		lead_details["lead_owner"] = frappe.session.user
	if not lead_details.get("mobile_no"):
		# Use customer field instead of from
		lead_details["mobile_no"] = call_log.get("customer") or call_log.get("from") or ""
	if not lead_details.get("first_name"):
		# Use customer_name if available
		if call_log.get("customer_name"):
			lead_details["first_name"] = call_log.get("customer_name")
		else:
			lead_details["first_name"] = "Lead from call " + (
				lead_details.get("mobile_no") or call_log.get("name")
			)

	lead.update(lead_details)
	lead.save(ignore_permissions=True)

	# link call log with lead
	call_log = frappe.get_doc("CRM Call Log", call_log.get("name"))
	call_log.link_with_reference_doc("CRM Lead", lead.name)
	call_log.save(ignore_permissions=True)

	return lead.name
