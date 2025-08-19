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

					# Create CRM Task Notification
					try:
						from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
						tn = create_task_notification(
							task_name=None,
							notification_type='Assignment Request Approved',
							assigned_to=self.requested_by,
							message=f'Your assignment request for {self.reference_doctype} {self.reference_name} has been approved',
							reference_doctype=self.reference_doctype,
							reference_docname=self.reference_name,
						)
						if tn:
							tn.mark_as_sent()
						else:
							frappe.logger().info(f"No task notification created for requester {self.requested_by} on approval of {self.name}")
					except Exception as e:
						frappe.log_error(f"Error creating approval task notification: {str(e)}", "Assignment Request Notification")

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

					# Create CRM Task Notification for rejection
					try:
						from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
						tn = create_task_notification(
							task_name=None,
							notification_type='Assignment Request Rejected',
							assigned_to=self.requested_by,
							message=f'Your assignment request for {self.reference_doctype} {self.reference_name} has been rejected',
							reference_doctype=self.reference_doctype,
							reference_docname=self.reference_name,
						)
						if tn:
							tn.mark_as_sent()
						else:
							frappe.logger().info(f"No task notification created for requester {self.requested_by} on rejection of {self.name}")
					except Exception as e:
						frappe.log_error(f"Error creating rejection task notification: {str(e)}", "Assignment Request Notification")
		except Exception as e:
			frappe.log_error(f"Error in CRMAssignmentRequest.on_update: {str(e)}", "Assignment Request Notification")



