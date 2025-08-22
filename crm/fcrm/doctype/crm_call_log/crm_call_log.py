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
		# Auto-link to all open Leads/Tickets for this customer if not explicitly linked
		try:
			self.auto_link_to_open_docs()
		except Exception as e:
			frappe.logger().error(f"CallLog auto-link failed for {self.name}: {str(e)}")
	
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

	def auto_link_to_open_docs(self):
		"""Link this call log to all open Leads and Tickets for the same customer.

		Open means:
		- Ticket: status NOT IN ('Closed', 'Resolved')
		- Lead: status != 'Account Activated'

		Matching is done via CRM Customer from customer_id if available on Lead/Ticket,
		otherwise by comparing contact phone/email with call log customer fields.
		"""
		# If already explicitly linked, respect it but still add dynamic links to others
		# Normalize phone (digits only) and extract possible email
		customer_contact = self.customer or self.get('from') or self.get('to') or ''
		customer_phone_digits = ''.join(filter(str.isdigit, str(customer_contact)))
		customer_email = None
		if isinstance(self.customer, str) and '@' in self.customer:
			customer_email = self.customer
		elif isinstance(self.customer_name, str) and '@' in self.customer_name:
			customer_email = self.customer_name

		# Gather candidate customers from phone/email
		candidate_customers = set()
		if customer_phone_digits:
			cust_by_phone = frappe.db.get_value(
				"CRM Customer",
				{"mobile_no": ("like", f"%{customer_phone_digits}")},
				"name",
			)
			if cust_by_phone:
				candidate_customers.add(cust_by_phone)
		if customer_email:
			cust_by_email = frappe.db.get_value(
				"CRM Customer",
				{"email": customer_email},
				"name",
			)
			if cust_by_email:
				candidate_customers.add(cust_by_email)

		# Tickets: link all open with matching customer
		open_tickets = []
		if candidate_customers:
			open_tickets = frappe.get_all(
				"CRM Ticket",
				filters={
					"customer_id": ("in", list(candidate_customers)),
					"status": ("not in", ["Closed", "Resolved"]),
				},
				pluck="name",
			)
		else:
			# Fallbacks: match by phone or email if no customer_id found
			if customer_phone_digits:
				open_tickets = frappe.get_all(
					"CRM Ticket",
					filters={
						"mobile_no": ("like", f"%{customer_phone_digits}"),
						"status": ("not in", ["Closed", "Resolved"]),
					},
					pluck="name",
				)
			elif customer_email:
				open_tickets = frappe.get_all(
					"CRM Ticket",
					filters={
						"email": customer_email,
						"status": ("not in", ["Closed", "Resolved"]),
					},
					pluck="name",
				)

		for t in open_tickets:
			self.link_with_reference_doc("CRM Ticket", t)

		# Leads: link all open with matching customer
		open_leads = []
		if candidate_customers:
			open_leads = frappe.get_all(
				"CRM Lead",
				filters={
					"customer_id": ("in", list(candidate_customers)),
					"status": ("!=", "Account Activated"),
				},
				pluck="name",
			)
		else:
			if customer_phone_digits:
				open_leads = frappe.get_all(
					"CRM Lead",
					filters={
						"mobile_no": ("like", f"%{customer_phone_digits}"),
						"status": ("!=", "Account Activated"),
					},
					pluck="name",
				)
			elif customer_email:
				open_leads = frappe.get_all(
					"CRM Lead",
					filters={
						"email": customer_email,
						"status": ("!=", "Account Activated"),
					},
					pluck="name",
				)

		for l in open_leads:
			self.link_with_reference_doc("CRM Lead", l)
	
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
			return f"Call From {phone_number}"
			
		except Exception as e:
			frappe.logger().error(f"Error getting customer name for {phone_number}: {str(e)}")
			return f"Call From {phone_number}"

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
		# Only create a dynamic link row; do NOT mutate reference_doctype/reference_docname here
		# to avoid marking lifecycle-suggested calls as explicitly linked
		if self.has_link(reference_doctype, reference_name):
			return
		self.append("links", {"link_doctype": reference_doctype, "link_name": reference_name})


@frappe.whitelist()
def link_call_log(call_log_name: str, reference_doctype: str, reference_docname: str):
	"""Explicitly link a call log to a specific Lead/Ticket and set reference fields.

	This makes the call appear only on that specific document in lifecycle views.
	"""
	if not call_log_name or not reference_doctype or not reference_docname:
		raise frappe.ValidationError("Missing parameters to link call log")

	call_log = frappe.get_doc("CRM Call Log", call_log_name)
	call_log.reference_doctype = reference_doctype
	call_log.reference_docname = reference_docname
	# Ensure a dynamic link row exists
	call_log.link_with_reference_doc(reference_doctype, reference_docname)
	call_log.save(ignore_permissions=True)
	return True


@frappe.whitelist()
def delink_call_log(call_log_name: str):
	"""Remove explicit Lead/Ticket link from a call log and clear dynamic links to them."""
	if not call_log_name:
		raise frappe.ValidationError("Missing call log name")

	call_log = frappe.get_doc("CRM Call Log", call_log_name)
	call_log.reference_doctype = None
	call_log.reference_docname = None
	# Remove dynamic links to CRM Lead/Ticket only; keep Notes/Tasks intact
	remaining_links = []
	for row in call_log.get("links") or []:
		if row.link_doctype not in ["CRM Lead", "CRM Ticket"]:
			remaining_links.append(row)
	call_log.set("links", remaining_links)
	call_log.save(ignore_permissions=True)
	return True


def parse_call_log(call):
	call["show_recording"] = False
	call["_duration"] = seconds_to_duration(call.get("duration"))
	
	# Use the new employee and customer fields for display
	employee_info = None
	customer_info = None
	
	if call.get("employee"):
		# Try to get a readable display name for the User. Prefer full_name, then first+last, then fallback to id/email
		employee_data = frappe.db.get_values(
			"User",
			call.get("employee"),
			["full_name", "first_name", "last_name", "user_image"],
		)[0] if call.get("employee") else [None, None, None, None]
		full_name, first_name, last_name, user_image = employee_data
		display_name = full_name or ' '.join([n for n in [first_name, last_name] if n]) or call.get("employee")
		employee_info = {
			"label": display_name or "Unknown Employee",
			"image": user_image,
		}

		# Expose employee display info for list views (show full name instead of id/email)
		if employee_info:
			call["_employee"] = employee_info
			# Also include a lightweight display string to simplify front-end rendering
			call["employee_display"] = display_name
	
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
		elif call.get("reference_doctype") == "CRM Ticket":
			call["_ticket"] = call.get("reference_docname")

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
			elif link.get("link_doctype") == "CRM Ticket":
				call["_ticket"] = link.get("link_name")

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
			lead_details["first_name"] = "Call From " + (
				lead_details.get("mobile_no") or call_log.get("name")
			)

	lead.update(lead_details)
	lead.save(ignore_permissions=True)

	# link call log with lead
	call_log = frappe.get_doc("CRM Call Log", call_log.get("name"))
	call_log.link_with_reference_doc("CRM Lead", lead.name)
	call_log.save(ignore_permissions=True)

	return lead.name
