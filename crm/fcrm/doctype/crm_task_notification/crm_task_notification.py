# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, get_datetime


class CRMTaskNotification(Document):
	def on_update(self):
		"""Publish real-time notification when status changes to Sent"""
		if self.has_value_changed("status") and self.status == "Sent":
			self.publish_realtime_notification()
	
	def before_insert(self):
		"""Validate and format notification before creating"""
		self.format_notification_text()
	
	def format_notification_text(self):
		"""Generate formatted notification text based on task details"""
		if not self.notification_text:
			if self.notification_type == "Lead Assignment":
				self.notification_text = self.get_lead_assignment_text()
			elif self.notification_type == "Task Reassignment Limit":
				self.notification_text = self.get_task_reassignment_limit_text()
			elif self.notification_type == "Assignment Request":
				self.notification_text = self.get_assignment_request_text()
			elif self.notification_type == "Assignment Request Approved":
				self.notification_text = self.get_assignment_request_approved_text()
			elif self.notification_type == "Assignment Request Rejected":
				self.notification_text = self.get_assignment_request_rejected_text()
			elif self.notification_type == "Mention":
				self.notification_text = self.get_mention_text()
			elif self.task:
				task_doc = frappe.get_doc("CRM Task", self.task)
				
				if self.notification_type == "Due Date Reminder":
					self.notification_text = self.get_due_date_reminder_text(task_doc)
				elif self.notification_type == "Overdue Task":
					self.notification_text = self.get_overdue_task_text(task_doc)
				elif self.notification_type == "Task Assignment":
					self.notification_text = self.get_task_assignment_text(task_doc)
				elif self.notification_type == "Task Completion":
					self.notification_text = self.get_task_completion_text(task_doc)
	
	def get_due_date_reminder_text(self, task_doc):
		"""Generate due date reminder notification text"""
		due_date_str = str(task_doc.due_date) if task_doc.due_date else "Not set"
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-ink-gray-9">Task Reminder</span>
				<div class="mt-1">
					<span class="font-medium text-ink-gray-9">{task_doc.title}</span>
					<span> is due in 5 minutes</span>
				</div>
				<div class="text-sm text-ink-gray-6">Due: {due_date_str}</div>
			</div>
		"""
	
	def get_overdue_task_text(self, task_doc):
		"""Generate overdue task notification text"""
		due_date_str = str(task_doc.due_date) if task_doc.due_date else "Not set"
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-red-600">Task Overdue</span>
				<div class="mt-1">
					<span class="font-medium text-ink-gray-9">{task_doc.title}</span>
					<span> is overdue</span>
				</div>
				<div class="text-sm text-ink-gray-6">Was due: {due_date_str}</div>
			</div>
		"""
	
	def get_task_assignment_text(self, task_doc):
		"""Generate task assignment notification text"""
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-ink-gray-9">New Task Assigned</span>
				<div class="mt-1">
					<span class="font-medium text-ink-gray-9">{task_doc.title}</span>
					<span> has been assigned to you</span>
				</div>
			</div>
		"""
	
	def get_task_completion_text(self, task_doc):
		"""Generate task completion notification text"""
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-green-600">Task Completed</span>
				<div class="mt-1">
					<span class="font-medium text-ink-gray-9">{task_doc.title}</span>
					<span> has been marked as complete</span>
				</div>
			</div>
		"""
	
	def get_lead_assignment_text(self):
		"""Generate lead assignment notification text"""
		if self.reference_doctype == "CRM Lead" and self.reference_docname:
			lead_doc = frappe.get_doc("CRM Lead", self.reference_docname)
			return f"""
				<div class="mb-2 leading-5 text-ink-gray-5">
					<span class="font-medium text-ink-gray-9">Lead Assignment</span>
					<div class="mt-1">
						<span class="font-medium text-ink-gray-9">{lead_doc.lead_name}</span>
						<span> has been assigned to you</span>
					</div>
					{f'<div class="text-sm text-ink-gray-6">Organization: {lead_doc.organization}</div>' if lead_doc.organization else ''}
					{f'<div class="text-sm text-ink-gray-6">Contact: {lead_doc.mobile_no or lead_doc.email or "N/A"}</div>' if (lead_doc.mobile_no or lead_doc.email) else ''}
				</div>
			"""
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-ink-gray-9">Lead Assignment</span>
				<div class="mt-1">
					<span>A new lead has been assigned to you</span>
				</div>
			</div>
		"""
	
	def get_task_reassignment_limit_text(self):
		"""Generate task reassignment limit notification text"""
		if self.task:
			task_doc = frappe.get_doc("CRM Task", self.task)
			document_type = "Lead" if task_doc.reference_doctype == "CRM Lead" else "Ticket"
			return f"""
				<div class="mb-2 leading-5 text-ink-gray-5">
					<span class="font-medium text-red-600">⚠️ Task Reassignment Limit Reached</span>
					<div class="mt-1">
						<span class="font-medium text-ink-gray-9">{task_doc.title}</span>
						<span> - All eligible users have been assigned</span>
					</div>
					<div class="text-sm text-ink-gray-6">Reference: {document_type} - {task_doc.reference_docname}</div>
					<div class="text-sm text-ink-gray-6">Current Assignee: {task_doc.assigned_to or 'Unassigned'}</div>
					<div class="text-sm text-ink-gray-6">Manual intervention required</div>
				</div>
			"""
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-red-600">⚠️ Task Reassignment Limit Reached</span>
				<div class="mt-1">
					<span>All eligible users have been assigned to a task</span>
				</div>
				<div class="text-sm text-ink-gray-6">Manual intervention required</div>
			</div>
		"""
	
	def get_assignment_request_text(self):
		"""Generate assignment request notification text for admins"""
		# Expecting self.message to be like: 'Assignment request for {doc} by {user_fullname}'
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-blue-600">📩 New Assignment Request</span>
				<div class="mt-1">
					<span>{self.message}</span>
				</div>
			</div>
		"""
	
	def get_assignment_request_submitted_text(self):
		"""Generate assignment request submitted notification text for requester"""
		# Keep for compatibility; not used in Task Reminders
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-blue-600">📩 Assignment Request Submitted</span>
				<div class="mt-1">
					<span>{self.message}</span>
				</div>
				<div class="text-sm text-ink-gray-6">Status: Pending admin approval</div>
			</div>
		"""
	
	def get_assignment_request_approved_text(self):
		"""Generate assignment request approved notification text for requester"""
		# For requester we want: Header + 'Your assignment request for [doc name] has been approved'
		# self.message is already set to a user-friendly string; use it directly.
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-green-600">✅ Assignment Request Approved</span>
				<div class="mt-1">
					<span>{self.message}</span>
				</div>
			</div>
		"""
	
	def get_assignment_request_rejected_text(self):
		"""Generate assignment request rejected notification text for requester"""
		# For rejected we want header + message + optional reason appended
		reason_text = ""
		# message may not contain reason; try to include rejection reason if available in message
		# Convention: when creating rejection notification, include reason in message if provided.
		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-red-600">❌ Assignment Request Rejected</span>
				<div class="mt-1">
					<span>{self.message}</span>
				</div>
			</div>
		"""

	def get_mention_text(self):
		"""Generate mention notification text"""
		# Fallback: if message contains HTML, extract plain text preview
		msg = self.message or ""
		try:
			from bs4 import BeautifulSoup
			plain = BeautifulSoup(msg, "html.parser").get_text().strip()
		except Exception:
			plain = msg

		# Word-based preview: first 20 words
		words = plain.split()
		if len(words) > 20:
			preview = " ".join(words[:20]).rstrip() + "..."
		else:
			preview = plain
		owner = frappe.get_cached_value("User", self.from_user, "full_name") if getattr(self, "from_user", None) else ""

		return f"""
			<div class="mb-2 leading-5 text-ink-gray-5">
				<span class="font-medium text-blue-600">💬 Mention</span>
				<div class="mt-1">
					<span class="font-medium text-ink-gray-9">{ owner }</span>
					<span> mentioned you in </span>
					<span class="font-medium text-ink-gray-9">{ (self.reference_docname or '') }</span>
				</div>
				<div class="mt-1 text-sm text-ink-gray-6">Message: { preview }</div>
				{self.get_reference_context()}
			</div>
		"""

	def get_reference_context(self):
		"""Get reference context for notifications"""
		if self.reference_doctype and self.reference_docname:
			try:
				if self.reference_doctype == "CRM Lead":
					lead_doc = frappe.get_doc("CRM Lead", self.reference_docname)
					lead_name = lead_doc.lead_name or lead_doc.first_name or "Lead"
					org = f" ({lead_doc.organization})" if lead_doc.organization else ""
					return f'<div class="text-sm text-ink-gray-6">Reference: {lead_name}{org}</div>'
				elif self.reference_doctype == "CRM Ticket":
					ticket_doc = frappe.get_doc("CRM Ticket", self.reference_docname)
					return f'<div class="text-sm text-ink-gray-6">Reference: {ticket_doc.ticket_subject}</div>'
				else:
					return f'<div class="text-sm text-ink-gray-6">Reference: {self.reference_doctype} - {self.reference_docname}</div>'
			except Exception:
				return f'<div class="text-sm text-ink-gray-6">Reference: {self.reference_doctype} - {self.reference_docname}</div>'
		return ""
	
	def publish_realtime_notification(self):
		"""Publish real-time notification to the assigned user"""
		if self.assigned_to and self.status == "Sent":
			frappe.publish_realtime(
				"crm_task_notification", 
				{
					"name": self.name,
					"task": self.task,
					"notification_type": self.notification_type,
					"message": self.message,
					"notification_text": self.notification_text,
					"sent_at": self.sent_at
				},
				user=self.assigned_to
			)
	
	def mark_as_read(self):
		"""Mark notification as read"""
		if self.status != "Read":
			self.db_set("status", "Read")
			self.db_set("read_at", now())
	
	def mark_as_sent(self):
		"""Mark notification as sent"""
		if self.status == "Pending":
			self.db_set("status", "Sent")
			self.db_set("sent_at", now())
			self.publish_realtime_notification()
	
	def mark_as_failed(self, error_message=None):
		"""Mark notification as failed and increment retry count"""
		self.db_set("status", "Failed")
		self.db_set("retry_count", self.retry_count + 1)
		self.db_set("last_retry_at", now())
		
		if error_message:
			frappe.logger().error(f"Task notification {self.name} failed: {error_message}")


@frappe.whitelist()
def mark_notification_as_read(notification_name):
	"""API endpoint to mark notification as read"""
	try:
		notification = frappe.get_doc("CRM Task Notification", notification_name)
		notification.mark_as_read()
		return {"success": True}
	except Exception as e:
		frappe.logger().error(f"Error marking notification as read: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_user_task_notifications(limit=20):
	"""Get task notifications for current user"""
	try:
		notifications = frappe.get_list(
			"CRM Task Notification",
			filters={
				"assigned_to": frappe.session.user,
				"status": ["in", ["Pending", "Sent", "Read"]]  # Include Pending for immediate visibility
			},
			fields=[
				"name", "task", "notification_type", "status", 
				"message", "notification_text", "sent_at", "read_at",
				"reference_doctype", "reference_docname"  # Include reference fields for all notifications
			],
			order_by="sent_at desc",
			limit=limit
		)
		
		# Get task details for each notification
		for notification in notifications:
			if notification.task:
				task = frappe.get_doc("CRM Task", notification.task)
				notification.task_title = task.title
				notification.task_status = task.status
				notification.task_priority = task.priority
				notification.reference_doctype = task.reference_doctype
				notification.reference_docname = task.reference_docname
		
		return notifications
	except Exception as e:
		frappe.logger().error(f"Error getting user task notifications: {str(e)}")
		return []


def create_task_notification(task_name, notification_type, assigned_to, message=None, reference_doctype=None, reference_docname=None):
	"""Helper function to create a task notification"""
	# Add detailed debug logging to help trace failures when called from comment mentions
	debug_ctx = {
		"task_name": task_name,
		"notification_type": notification_type,
		"assigned_to": assigned_to,
		"message_preview": (message or "")[:200],
		"reference_doctype": reference_doctype,
		"reference_docname": reference_docname,
	}
	frappe.logger().debug(f"create_task_notification called with: {debug_ctx}")

	try:
		# For Lead Assignment, Assignment Request, and Mention notifications, don't check for existing task notifications
		if notification_type in ["Lead Assignment", "Assignment Request", "Assignment Request Submitted", "Assignment Request Approved", "Assignment Request Rejected", "Mention"]:
			# Create new notification
			notification = frappe.get_doc({
				"doctype": "CRM Task Notification",
				"notification_type": notification_type,
				"assigned_to": assigned_to,
				"message": message,
				"reference_doctype": reference_doctype,
				"reference_docname": reference_docname,
				"status": "Pending"
			})
		else:
			# Check if notification already exists for task-based notifications
			try:
				existing = frappe.db.exists("CRM Task Notification", {
					"task": task_name,
					"notification_type": notification_type,
					"assigned_to": assigned_to,
					"status": ["in", ["Pending", "Sent"]]
				})
			except Exception as db_e:
				frappe.logger().exception(f"db.exists failed while checking existing notifications: {db_e} | context: {debug_ctx}")
				raise

			if existing:
				frappe.logger().debug(f"Existing CRM Task Notification found: {existing} | context: {debug_ctx}")
				return frappe.get_doc("CRM Task Notification", existing)
			
			# Create new task notification
			notification = frappe.get_doc({
				"doctype": "CRM Task Notification",
				"task": task_name,
				"notification_type": notification_type,
				"assigned_to": assigned_to,
				"message": message,
				"status": "Pending"
			})

		frappe.logger().debug(f"Inserting CRM Task Notification: {debug_ctx}")
		notification.insert(ignore_permissions=True)

		# For instant visibility in Task Reminder, mark Mention notifications as Sent
		try:
			if getattr(notification, "notification_type", None) == "Mention":
				notification.mark_as_sent()
		except Exception:
			frappe.logger().exception("Failed to mark Mention notification as sent")
		frappe.logger().info(f"CRM Task Notification created: {getattr(notification, 'name', None)} | context: {debug_ctx}")
		frappe.logger().debug(f"Notification full doc: {notification.as_dict()}")
		return notification

	except Exception as e:
		# Log full traceback plus context for deeper debugging
		frappe.logger().exception(f"Error creating task notification: {str(e)} | context: {debug_ctx}")
		return None