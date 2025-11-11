# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as assign, remove as unassign
from frappe.utils import add_to_date, get_datetime
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


class CRMTask(Document):
	def after_insert(self):
		self.assign_to()
		# 🔔 Send enhanced notification if this task is for a lead
		self.send_lead_aware_notification()

	def validate(self):
		# Set notification time when due_date is set
		self.set_notification_time()
		
		if self.is_new() or not self.assigned_to:
			return

		if self.get_doc_before_save().assigned_to != self.assigned_to:
			self.unassign_from_previous_user(self.get_doc_before_save().assigned_to)
			self.assign_to()
			# 🔔 Send enhanced notification for task reassignment
			self.send_lead_aware_notification()

	def set_notification_time(self):
		"""Set notification_time to 5 minutes before due_date"""
		if self.due_date:
			try:
				# Convert due_date to datetime if it's not already
				due_datetime = get_datetime(self.due_date)
				# Set notification time to 5 minutes before due date
				self.notification_time = add_to_date(due_datetime, minutes=-5)
				# Reset notification status if due date changed
				if self.has_value_changed("due_date"):
					self.notification_status = "Not Sent"
			except Exception as e:
				frappe.logger().error(f"Error setting notification time for task {self.name}: {str(e)}")
		else:
			# Clear notification time if no due date
			self.notification_time = None
			self.notification_status = "Not Sent"

	def unassign_from_previous_user(self, user):
		unassign(self.doctype, self.name, user)

	def assign_to(self):
		if self.assigned_to:
			# Use assign without triggering default notifications for lead tasks
			# We'll send our enhanced notifications instead
			if self.reference_doctype == "CRM Lead" and self.reference_docname:
				# For lead tasks, assign silently and let our enhanced notification handle it
				assign({
					"assign_to": [self.assigned_to],
					"doctype": self.doctype,
					"name": self.name,
					"description": self.title or self.description,
				}, ignore_permissions=True)
			else:
				# For non-lead tasks, use standard assignment
				assign({
					"assign_to": [self.assigned_to],
					"doctype": self.doctype,
					"name": self.name,
					"description": self.title or self.description,
				})

	def send_lead_aware_notification(self):
		"""Send enhanced notification with parent context (Lead/Ticket) when available"""
		if not self.assigned_to or self.assigned_to == frappe.session.user:
			return

		# If there is no parent linkage, send standard notification
		if not self.reference_doctype or not self.reference_docname:
			self.send_standard_task_notification()
			return

		try:
			if self.reference_doctype == "CRM Lead":
				lead_doc = frappe.get_doc("CRM Lead", self.reference_docname)
				from crm.api.lead_notifications import create_task_with_lead_notification
				create_task_with_lead_notification(self, lead_doc)
				return
			elif self.reference_doctype == "CRM Ticket":
				ticket_doc = frappe.get_doc("CRM Ticket", self.reference_docname)
				from crm.api.ticket_notifications import create_task_with_ticket_notification
				create_task_with_ticket_notification(self, ticket_doc, is_assignment=True)
				return
			else:
				# Unknown parent type → use standard
				self.send_standard_task_notification()
		except Exception as e:
			frappe.logger().error(f"Failed to send context-aware task notification: {str(e)}")
			# Fallback to standard notification
			self.send_standard_task_notification()

	def send_standard_task_notification(self):
		"""Send standard task assignment notification using CRM Task Notification system"""
		try:
			if not self.assigned_to or self.assigned_to == frappe.session.user:
				return
				
			# Use the CRM Task Notification system for all task notifications
			from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
			
			message = f"Task '{self.title}' has been assigned to you"
			
			# Create the task notification
			notification = create_task_notification(
				task_name=self.name,
				notification_type="Task Assignment",
				assigned_to=self.assigned_to,
				message=message
			)
			
			if notification:
				# Mark as sent to trigger real-time notification
				notification.mark_as_sent()
				frappe.logger().info(f"Standard task notification sent to {self.assigned_to} for task {self.name}")
				
		except Exception as e:
			frappe.logger().error(f"Error sending standard task notification: {str(e)}")
			# Ultimate fallback to old CRM notification system
			try:
				from crm.fcrm.doctype.crm_notification.crm_notification import notify_user
				notify_user({
					"owner": frappe.session.user,
					"assigned_to": self.assigned_to,
					"notification_type": "Task",
					"message": f"Task '{self.title}' has been assigned to you",
					"notification_text": f"Task '{self.title}' has been assigned to you",
					"reference_doctype": "CRM Task",
					"reference_docname": self.name,
					"redirect_to_doctype": "CRM Task",
					"redirect_to_docname": self.name,
				})
			except Exception as fallback_error:
				frappe.logger().error(f"Fallback notification also failed: {str(fallback_error)}")


	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Title',
				'type': 'Data',
				'key': 'title',
				'width': '16rem',
			},
			{
				'label': 'Status',
				'type': 'Select',
				'key': 'status',
				'width': '8rem',
			},
			{
				'label': 'Priority',
				'type': 'Select',
				'key': 'priority',
				'width': '8rem',
			},
			{
				'label': 'Due Date',
				'type': 'Date',
				'key': 'due_date',
				'width': '8rem',
			},
			{
				'label': 'Assigned To',
				'type': 'Text',
				'key': '_assign',
				'width': '10rem',
			},
			{
				'label': 'Last Modified',
				'type': 'Datetime',
				'key': 'modified',
				'width': '8rem',
			},
		]

		rows = [
			"name",
			"title",
			"description",
			"assigned_to",
			"due_date",
			"status",
			"priority",
			"reference_doctype",
			"reference_docname",
			"modified",
		]
		return {'columns': columns, 'rows': rows}

	@staticmethod
	def default_kanban_settings():
		return {
			"column_field": "status",
			"title_field": "title",
			"kanban_fields": '["description", "priority", "creation"]'
		}
