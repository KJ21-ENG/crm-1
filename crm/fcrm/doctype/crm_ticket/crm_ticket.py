# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as assign
from frappe.model.document import Document
from frappe.utils import has_gravatar, validate_email_address
from frappe.utils import now_datetime

from crm.fcrm.doctype.crm_service_level_agreement.utils import get_sla
from crm.fcrm.doctype.crm_status_change_log.crm_status_change_log import (
	add_status_change_log,
)
from crm.api.activities import emit_activity_update
# Import ticket notification handler
from crm.api.ticket_notifications import handle_ticket_assignment_change
from crm.fcrm.utils.validation import validate_identity_documents


class CRMTicket(Document):
	def before_validate(self):
		self.set_sla()
		self.normalize_subjects()

	def validate(self):
		self.set_customer_name()
		self.normalize_subjects()
		self.set_title()
		# Skip customer-info validations when using centralized customer store
		if not getattr(self, "customer_id", None):
			self.validate_email()
			validate_identity_documents(self)
		# Handle ticket_owner assignment logic
		if not self.is_new() and self.has_value_changed("ticket_owner") and self.ticket_owner:
			self.share_with_agent(self.ticket_owner)
			self.assign_agent(self.ticket_owner)
		if self.has_value_changed("status"):
			add_status_change_log(self)
			self.check_resolution_status()
		
		# Handle ticket assignment notifications for ticket owner changes
		handle_ticket_assignment_change(self, method="validate")

	def after_insert(self):
		if self.ticket_owner:
			self.assign_agent(self.ticket_owner)
		
		# Create or update customer record
		self.create_or_update_customer()
		
		emit_activity_update("CRM Ticket", self.name)
		
		# Handle ticket assignment notifications for new tickets
		handle_ticket_assignment_change(self, method="after_insert")

	def on_update(self):
		# No longer sync customer-related field changes since we're not storing duplicate data
		# Customer data is now managed only in the customer table
		emit_activity_update("CRM Ticket", self.name)

	def before_save(self):
		self.apply_sla()

	def create_or_update_customer(self):
		"""Create or update customer record based on ticket data"""
		if not self.mobile_no:
			return
		
		try:
			# Import the customer API function
			from crm.api.customers import create_or_update_customer
			
			# Only pass customer-specific data to customer creation
			customer_result = create_or_update_customer(
				mobile_no=self.mobile_no,
				first_name=self.first_name,
				last_name=self.last_name,
				email=self.email,
				organization=self.organization,
				pan_card_number=self.pan_card_number,
				aadhaar_card_number=self.aadhaar_card_number,
				marital_status=self.marital_status,
				date_of_birth=self.date_of_birth,
				anniversary=self.anniversary,
				customer_source="Ticket",
				reference_doctype="CRM Ticket",
				reference_docname=self.name
			)
			
			# Update the customer_id field with the customer name using db.set_value to avoid activity log
			if customer_result and customer_result.get("name"):
				frappe.db.set_value("CRM Ticket", self.name, "customer_id", customer_result["name"])
				# Update the instance variable to keep it in sync
				self.customer_id = customer_result["name"]
				
				# Clear customer-specific fields from ticket table to avoid duplication
				customer_fields_to_clear = [
					'first_name', 'last_name', 'middle_name', 'email', 'mobile_no', 
					'phone', 'salutation', 'organization', 'pan_card_number', 
					'aadhaar_card_number', 'image', 'customer_name', 'marital_status',
					'date_of_birth', 'anniversary'
				]
				
				for field in customer_fields_to_clear:
					if hasattr(self, field):
						frappe.db.set_value("CRM Ticket", self.name, field, None)
						setattr(self, field, None)
			
			frappe.logger().info(f"Customer record processed for ticket {self.name}: {customer_result}")
			
		except Exception as e:
			# Log error but don't fail the ticket creation
			frappe.log_error(f"Error creating/updating customer for ticket {self.name}: {str(e)}", "Customer Creation Error")
			frappe.logger().error(f"Customer creation failed for ticket {self.name}: {str(e)}")

	def get_customer_data(self):
		"""Get customer data from customer table using customer_id"""
		if not self.customer_id:
			return None
		
		try:
			from crm.api.customers import get_customer_by_id
			return get_customer_by_id(self.customer_id)
		except Exception as e:
			frappe.log_error(f"Error fetching customer data for ticket {self.name}: {str(e)}", "Customer Data Fetch Error")
			return None

	def set_customer_name(self):
		"""Set customer name from customer data if available, otherwise use ticket-specific data"""
		if self.customer_id:
			# Try to get customer data
			customer_data = self.get_customer_data()
			if customer_data:
				self.customer_name = " ".join(
					filter(
						None,
						[
							customer_data.get('salutation'),
							customer_data.get('first_name'),
							customer_data.get('middle_name'),
							customer_data.get('last_name'),
						],
					)
				)
				return
		
		# Fallback to ticket-specific data if no customer data available
		if self.first_name:
			self.customer_name = " ".join(
				filter(
					None,
					[
						self.salutation,
						self.first_name,
						self.middle_name,
						self.last_name,
					],
				)
			)

	def set_title(self):
		# Derive subject/text for title from multi-select if available
		subject_text = None
		if getattr(self, "ticket_subjects", None):
			labels = []
			for row in (self.ticket_subjects or []):
				if not row.subject:
					continue
				try:
					s_doc = frappe.get_doc("CRM Ticket Subject", row.subject)
					labels.append(s_doc.subject_name)
				except Exception:
					labels.append(row.subject)
			if labels:
				subject_text = ", ".join(labels)
		# fallback to single link
		if not subject_text:
			subject_text = self.ticket_subject
			if self.ticket_subject:
				try:
					subject_doc = frappe.get_doc("CRM Ticket Subject", self.ticket_subject)
					subject_text = subject_doc.subject_name
				except frappe.DoesNotExistError:
					pass
		# store normalized subject for list/search
		self.subject = subject_text
		self.title = subject_text or f"Ticket from {self.customer_name or 'Customer'}"

	def normalize_subjects(self):
		"""Ensure compatibility between new multi-select and legacy single link.
		- If multi-select has values, set first into ticket_subject for compatibility.
		- If neither is set, leave as-is and let validations elsewhere handle requiredness.
		"""
		try:
			rows = list(self.ticket_subjects or [])
		except Exception:
			rows = []
		if rows:
			first = rows[0].subject if getattr(rows[0], "subject", None) else None
			if first and self.ticket_subject != first:
				self.ticket_subject = first

	def validate_email(self):
		if self.email:
			if not self.flags.ignore_email_validation:
				validate_email_address(self.email, throw=True)

			if self.email == self.ticket_owner:
				frappe.throw(_("Ticket Owner cannot be same as the Customer Email Address"))

			if self.is_new() or not self.image:
				self.image = has_gravatar(self.email)

	def check_resolution_status(self):
		"""Update resolved flag based on status"""
		if self.status in ["Resolved", "Closed"]:
			self.resolved = 1
			if not self.resolved_on:
				self.resolved_on = frappe.utils.now()
		else:
			self.resolved = 0
			self.resolved_on = None

	def assign_agent(self, agent):
		if not agent:
			return

		assignees = self.get_assigned_users()
		if assignees:
			for assignee in assignees:
				if agent == assignee:
					# the agent is already set as an assignee
					return

		assign({"assign_to": [agent], "doctype": "CRM Ticket", "name": self.name})

	def share_with_agent(self, agent):
		if not agent:
			return

		docshares = frappe.get_all(
			"DocShare",
			filters={"share_name": self.name, "share_doctype": self.doctype},
			fields=["name", "user"],
		)

		shared_with = [d.user for d in docshares] + [agent]

		for user in shared_with:
			if user == agent and not frappe.db.exists(
				"DocShare",
				{"user": agent, "share_name": self.name, "share_doctype": self.doctype},
			):
				frappe.share.add_docshare(
					self.doctype,
					self.name,
					agent,
					write=1,
					flags={"ignore_share_permission": True},
				)
			elif user != agent:
				frappe.share.remove(self.doctype, self.name, user)

	def set_sla(self):
		"""
		Find an SLA to apply to the ticket.
		"""
		if self.sla:
			return

		sla = get_sla(self)
		if not sla:
			self.first_responded_on = None
			self.first_response_time = None
			return
		self.sla = sla.name

	def apply_sla(self):
		"""
		Apply SLA if set.
		"""
		if not self.sla:
			return
		sla = frappe.get_last_doc("CRM Service Level Agreement", {"name": self.sla})
		if sla:
			sla.apply(self)

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Subject",
				"type": "Data",
				"key": "subject",
				"width": "16rem",
			},
			{
				"label": "Customer",
				"type": "Data",
				"key": "customer_name",
				"width": "12rem",
			},
			{
				"label": "Status",
				"type": "Select",
				"key": "status",
				"width": "8rem",
			},
			{
				"label": "Priority",
				"type": "Select",
				"key": "priority",
				"width": "8rem",
			},
			{
				"label": "Ticket Owner",
				"type": "Link",
				"key": "ticket_owner",
				"options": "User",
				"width": "10rem",
			},
			{
				"label": "Assigned To",
				"type": "Text",
				"key": "_assign",
				"width": "10rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"subject",
			"customer_name",
			"status",
			"priority",
			"ticket_owner",
			"assigned_to",
			"first_name",
			"email",
			"mobile_no",
			"sla_status",
			"response_by",
			"first_response_time",
			"first_responded_on",
			"modified",
			"_assign",
			"image",
		]
		return {"columns": columns, "rows": rows}

	@staticmethod
	def default_kanban_settings():
		return {
			"column_field": "status",
			"title_field": "subject",
			"kanban_fields": '["customer_name", "priority", "ticket_owner", "modified"]',
		} 