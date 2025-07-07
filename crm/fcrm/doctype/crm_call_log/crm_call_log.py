# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from crm.integrations.api import get_contact_by_phone_number
from crm.utils import seconds_to_duration


class CRMCallLog(Document):
	def before_save(self):
		"""Auto-populate employee and customer fields based on call type"""
		self.populate_employee_customer_fields()
		
		# Auto-link with existing lead if phone number matches
		phone_number = self.customer or self.get('from')
		if phone_number and not self.reference_doctype:  # Only if not already linked
			# Search for leads with this phone number
			lead = frappe.db.get_value(
				"CRM Lead",
				{"mobile_no": phone_number, "converted": 0},  # Only link to non-converted leads
				"name"
			)
			
			if lead:
				self.link_with_reference_doc("CRM Lead", lead)
				self.reference_doctype = "CRM Lead"
				self.reference_docname = lead
	
	def populate_employee_customer_fields(self):
		"""Populate employee and customer fields from caller/receiver data"""
		print("\n=== Debug Employee/Customer Population ===")
		print("Before - Employee:", self.employee)
		print("Before - Customer:", self.customer)
		print("Before - Customer Name:", self.customer_name)
		print("Call Type:", self.type)
		print("Caller:", self.caller)
		print("Receiver:", self.receiver)
		
		if self.type == "Outgoing":
			# Employee made the call
			self.employee = self.caller or self.employee
			print("Outgoing - Setting employee from caller:", self.employee)
			self.customer = self.to
			print("Outgoing - Setting customer from to:", self.customer)
		elif self.type == "Incoming":
			# Employee received the call
			self.employee = self.receiver or self.employee
			print("Incoming - Setting employee from receiver:", self.employee)
			self.customer = self.get('from')
			print("Incoming - Setting customer from from:", self.customer)
		
		# Only update customer name if it's not already set
		if self.customer and not self.customer_name:
			# Try to get name from contacts first
			try:
				contact = frappe.db.get_value(
					'Contact',
					[
						['phone', 'like', f'%{self.customer}%'],
						'or',
						['mobile_no', 'like', f'%{self.customer}%']
					],
					['first_name', 'last_name'],
					as_dict=True
				)
				
				if contact:
					first_name = contact.get('first_name', '') or ''
					last_name = contact.get('last_name', '') or ''
					self.customer_name = f"{first_name} {last_name}".strip()
				else:
					# Only set default name if no name exists
					self.customer_name = f"Lead from call {self.customer}"
			except Exception as e:
				frappe.log_error(f"Error getting customer name for {self.customer}: {str(e)}")
				# Only set default name if no name exists
				self.customer_name = f"Lead from call {self.customer}"
		
		print("After - Employee:", self.employee)
		print("After - Customer:", self.customer)
		print("After - Customer Name:", self.customer_name)
		print("=== End Debug ===\n")
	
	def get_customer_name_from_phone(self, phone_number):
		"""Get customer name from phone number by searching contacts and leads"""
		print("\n=== Debug Customer Name Lookup ===")
		print("Input phone number:", phone_number)
		
		if not phone_number:
			print("No phone number provided")
			return None
			
		try:
			# Clean phone number
			clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
			print("Cleaned phone number:", clean_phone)
			
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
			print("Contact search result:", contact)
			
			if contact:
				first_name = contact.get('first_name', '') or ''
				last_name = contact.get('last_name', '') or ''
				full_name = f"{first_name} {last_name}".strip()
				print("Found contact name:", full_name)
				return full_name
			
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
			print("Lead search result:", lead)
			
			if lead:
				print("Found lead name:", lead)
				return lead
			
			print("No matching contact or lead found")
			# If no contact or lead found, generate default name
			return f"Lead from call {phone_number}"
			
		except Exception as e:
			print("Error in customer name lookup:", str(e))
			frappe.logger().error(f"Error getting customer name for {phone_number}: {str(e)}")
			return f"Lead from call {phone_number}"
		finally:
			print("=== End Debug ===\n")

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
				"label": "To",
				"type": "Data",
				"key": "to",
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
				"type": "Duration",
				"key": "duration",
				"width": "6rem",
			},
			{
				"label": "Created On",
				"type": "Datetime",
				"key": "creation",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"employee",
			"customer",
			"customer_name",
			"type",
			"status",
			"duration",
			"from",
			"to",
			"caller",
			"receiver",
			"note",
			"recording_url",
			"reference_doctype",
			"reference_docname",
			"creation",
		]
		return {"columns": columns, "rows": rows}

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
	
	# Initialize default info structures
	default_info = {
		"label": "Unknown",
		"image": None
	}
	
	# If this is a DB record, get the latest data
	if call.get("name"):
		latest_data = frappe.get_doc("CRM Call Log", call.get("name"))
		if latest_data:
			call.update(latest_data.as_dict())
	
	# Handle employee info
	employee_info = default_info.copy()
	if call.get("employee"):
		try:
			employee_data = frappe.db.get_values("User", call.get("employee"), ["full_name", "user_image"])
			if employee_data and len(employee_data) > 0:
				employee_info = {
					"label": employee_data[0][0] or "Unknown Employee",
					"image": employee_data[0][1]
				}
		except Exception:
			frappe.log_error("Error getting employee info in parse_call_log")
	
	# Handle customer info
	customer_info = default_info.copy()
	try:
		# Get customer phone number and name
		customer_phone = call.get("customer") or call.get("from")
		customer_name = call.get("customer_name")
		
		if customer_name:
			customer_info = {
				"label": customer_name,
				"image": None
			}
		elif customer_phone:
			# Try to get customer name from phone
			found_name = frappe.get_value("Contact", 
				filters=[["phone", "like", f"%{customer_phone}%"]], 
				fieldname="first_name")
			if found_name:
				customer_info = {
					"label": found_name,
					"image": None
				}
	except Exception:
		frappe.log_error("Error getting customer info in parse_call_log")
	
	# Set caller and receiver based on call type
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

	# Get all call logs with the same phone number
	phone_number = call_log.get("customer") or call_log.get("from")
	if phone_number:
		all_calls = frappe.get_all(
			"CRM Call Log",
			filters=[
				["customer", "=", phone_number],
				["name", "!=", call_log.get("name")]  # Exclude current call log as it will be linked below
			],
			fields=["name"]
		)
		
		# Link all found call logs with the lead
		for call in all_calls:
			call_doc = frappe.get_doc("CRM Call Log", call.name)
			call_doc.link_with_reference_doc("CRM Lead", lead.name)
			call_doc.save(ignore_permissions=True)

	# Link the current call log with lead
	call_log = frappe.get_doc("CRM Call Log", call_log.get("name"))
	call_log.link_with_reference_doc("CRM Lead", lead.name)
	call_log.save(ignore_permissions=True)

	return lead.name


@frappe.whitelist()
def update_customer_name(call_log, customer_name):
	"""Update customer name for a call log"""
	if not call_log:
		frappe.throw(_("Call Log ID is required"))
	
	if not customer_name:
		frappe.throw(_("Customer Name is required"))
		
	doc = frappe.get_doc("CRM Call Log", call_log)
	doc.customer_name = customer_name
	doc.save(ignore_permissions=True)
	
	return doc.as_dict()
