import frappe
from frappe.model.document import Document
from frappe import _


class CRMAssignmentRequest(Document):
	def on_update(self):
		# When status changes to Approved or Rejected, notify the requester via CRM Task Notification
		try:
			if self.has_value_changed("status"):
				# Notify requester when approved
				if self.status == "Approved":
					# Send lightweight notify_user (legacy) and create task notification
					try:
						from crm.fcrm.doctype.crm_notification.crm_notification import notify_user
						notify_user({
							"owner": self.approved_by or frappe.session.user,
							"assigned_to": self.requested_by,
							"notification_type": "Assignment Request",
							"message": _(f"Your assignment request has been approved for {self.reference_doctype} {self.reference_name}."),
							"notification_text": _(f"Your assignment request has been approved for {self.reference_doctype} {self.reference_name}."),
							"reference_doctype": self.reference_doctype,
							"reference_docname": self.reference_name,
							"redirect_to_doctype": self.reference_doctype,
							"redirect_to_docname": self.reference_name,
						})
					except Exception:
						frappe.log_error(f"Failed to send notify_user for assignment request approval: {self.name}", "Assignment Request Notification")

					# REMOVED: Duplicate CRM Task Notification creation - now handled in approve_assignment_request API
					# This prevents duplicate notifications for the requester

				# Notify requester when rejected
				elif self.status == "Rejected":
					try:
						from crm.fcrm.doctype.crm_notification.crm_notification import notify_user
						notify_user({
							"owner": self.approved_by or frappe.session.user,
							"assigned_to": self.requested_by,
							"notification_type": "Assignment Request",
							"message": _(f"Your assignment request has been rejected for {self.reference_doctype} {self.reference_name}."),
							"notification_text": _(f"Your assignment request has been rejected for {self.reference_doctype} {self.reference_name}."),
							"reference_doctype": self.reference_doctype,
							"reference_docname": self.reference_name,
							"redirect_to_doctype": self.reference_doctype,
							"redirect_to_docname": self.reference_name,
						})
					except Exception:
						frappe.log_error(f"Failed to send notify_user for assignment request rejection: {self.name}", "Assignment Request Notification")

					# REMOVED: Duplicate CRM Task Notification creation - now handled in reject_assignment_request API
					# This prevents duplicate notifications for the requester
		except Exception as e:
			frappe.log_error(f"Error in CRMAssignmentRequest.on_update: {str(e)}", "Assignment Request Notification")



