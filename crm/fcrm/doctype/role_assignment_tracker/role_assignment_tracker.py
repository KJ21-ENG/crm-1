# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class RoleAssignmentTracker(Document):
	def autoname(self):
		self.name = self.role_name
	
	def validate(self):
		"""Validate the user list and ensure data consistency"""
		if self.user_list:
			# Parse user_list if it's a string
			if isinstance(self.user_list, str):
				try:
					user_list = json.loads(self.user_list)
				except json.JSONDecodeError:
					user_list = []
			elif isinstance(self.user_list, list):
				# Convert list to JSON string for storage
				user_list = self.user_list
				self.user_list = json.dumps(user_list)
			else:
				user_list = []
				
			self.total_users = len(user_list)
			
			# Ensure current_position is within bounds
			if self.current_position >= self.total_users:
				self.current_position = 0
		else:
			self.total_users = 0
			self.current_position = 0
			self.user_list = "[]"

	@staticmethod
	def get_or_create_tracker(role_name):
		"""Get existing tracker or create new one for the role"""
		tracker = frappe.db.get_value("Role Assignment Tracker", role_name, "name")
		
		if not tracker:
			# Get users with this role (exclude admin and system users)
			users = frappe.get_all("Has Role", 
				filters={"role": role_name, "parent": ["not in", ["Administrator", "admin@example.com"]]},
				fields=["parent"]
			)
			
			user_list = [user.parent for user in users if frappe.db.get_value("User", user.parent, "enabled")]
			
			if not user_list:
				frappe.throw(f"No active users found with role: {role_name}")
			
			# Create new tracker
			tracker_doc = frappe.get_doc({
				"doctype": "Role Assignment Tracker",
				"role_name": role_name,
				"current_position": 0,
				"total_users": len(user_list),
				"user_list": json.dumps(user_list),
				"assignment_count": 0,
				"assignment_history": json.dumps([])
			})
			tracker_doc.insert(ignore_permissions=True)
			return tracker_doc
		else:
			return frappe.get_doc("Role Assignment Tracker", tracker)

	@staticmethod
	def get_next_user_for_role(role_name):
		"""Get the next user in round-robin for the specified role"""
		tracker = RoleAssignmentTracker.get_or_create_tracker(role_name)
		
		# Refresh user list to handle user changes (exclude admin and system users)
		users = frappe.get_all("Has Role", 
			filters={"role": role_name, "parent": ["not in", ["Administrator", "admin@example.com"]]},
			fields=["parent"]
		)
		
		current_user_list = [user.parent for user in users if frappe.db.get_value("User", user.parent, "enabled")]
		
		if not current_user_list:
			frappe.throw(f"No active users found with role: {role_name}")
		
		# Parse current stored user list
		stored_user_list = []
		if tracker.user_list:
			try:
				stored_user_list = json.loads(tracker.user_list) if isinstance(tracker.user_list, str) else tracker.user_list
			except json.JSONDecodeError:
				stored_user_list = []
		
		# Update user list if it has changed
		if json.dumps(sorted(current_user_list)) != json.dumps(sorted(stored_user_list)):
			# Smart position management when user list changes
			old_position = tracker.current_position
			old_user_list = stored_user_list
			
			tracker.user_list = json.dumps(current_user_list)
			tracker.total_users = len(current_user_list)
			
			# Smart position adjustment
			if len(current_user_list) > len(old_user_list):
				# Users were added - preserve current position
				tracker.current_position = min(old_position, len(current_user_list) - 1)
			elif len(current_user_list) < len(old_user_list):
				# Users were removed - adjust position if needed
				tracker.current_position = min(old_position, len(current_user_list) - 1)
			else:
				# Same number of users but different users - keep position
				tracker.current_position = min(old_position, len(current_user_list) - 1)
		
		# Get next user
		if tracker.current_position >= len(current_user_list):
			tracker.current_position = 0
		
		next_user = current_user_list[tracker.current_position]
		
		# Log position management for debugging
		frappe.logger().info(f"Role: {role_name}, Position: {tracker.current_position}/{len(current_user_list)}, Next User: {next_user}")
		
		return next_user, tracker

	@staticmethod
	def assign_to_next_user(role_name, document_type, document_name, assigned_by=None):
		"""Assign a document to the next user in round-robin and update tracker"""
		next_user, tracker = RoleAssignmentTracker.get_next_user_for_role(role_name)
		
		# Update tracker
		tracker.current_position = (tracker.current_position + 1) % tracker.total_users
		tracker.last_assigned_user = next_user
		tracker.last_assigned_on = datetime.now()
		tracker.assignment_count += 1
		
		# Parse and update assignment history
		assignment_history = []
		if tracker.assignment_history:
			try:
				assignment_history = json.loads(tracker.assignment_history) if isinstance(tracker.assignment_history, str) else tracker.assignment_history
			except json.JSONDecodeError:
				assignment_history = []
		
		history_entry = {
			"user": next_user,
			"document_type": document_type,
			"document_name": document_name,
			"assigned_on": tracker.last_assigned_on.isoformat(),
			"assigned_by": assigned_by or frappe.session.user,
			"position": tracker.current_position - 1 if tracker.current_position > 0 else tracker.total_users - 1
		}
		
		assignment_history.append(history_entry)
		
		# Keep only last 100 assignments in history
		if len(assignment_history) > 100:
			assignment_history = assignment_history[-100:]
		
		tracker.assignment_history = json.dumps(assignment_history)
		
		tracker.save(ignore_permissions=True)
		
		return next_user

	@staticmethod
	def get_role_status(role_name):
		"""Get current status of role assignment"""
		try:
			tracker = RoleAssignmentTracker.get_or_create_tracker(role_name)
			
			next_user, _ = RoleAssignmentTracker.get_next_user_for_role(role_name)
			
			# Parse user list for detailed info
			user_list = []
			if tracker.user_list:
				try:
					user_list = json.loads(tracker.user_list) if isinstance(tracker.user_list, str) else tracker.user_list
				except json.JSONDecodeError:
					user_list = []
			
			return {
				"role_name": role_name,
				"total_users": tracker.total_users,
				"current_position": tracker.current_position,
				"next_user": next_user,
				"last_assigned_user": tracker.last_assigned_user,
				"last_assigned_on": tracker.last_assigned_on,
				"assignment_count": tracker.assignment_count,
				"user_list": user_list,
				"position_info": {
					"current_user_at_position": user_list[tracker.current_position] if user_list and tracker.current_position < len(user_list) else None,
					"next_user_will_be": next_user,
					"position_percentage": (tracker.current_position / len(user_list) * 100) if user_list else 0
				}
			}
		except Exception as e:
			return {"error": str(e)}

	@staticmethod
	def reset_role_tracker(role_name):
		"""Reset the round-robin position for a role"""
		tracker = frappe.get_doc("Role Assignment Tracker", role_name)
		tracker.current_position = 0
		tracker.save(ignore_permissions=True)
		return "Role tracker reset successfully"

	@staticmethod
	def get_role_users(role_name):
		"""Get all users for a specific role (excluding admin)"""
		users = frappe.get_all(
			"Has Role",
			filters={
				"role": role_name,
				"parent": ["not in", ["Administrator", "admin@example.com"]],
			},
			fields=["parent"],
		)
		return [user.parent for user in users if frappe.db.get_value("User", user.parent, "enabled")]

	@staticmethod
	def assign_to_next_user_from_list(role_name, user_list, document_type, document_name, assigned_by=None):
		"""Assign a document to the next user from a specific user list using round-robin"""
		if not user_list:
			frappe.throw(f"No users provided for role: {role_name}")
		
		# Get or create tracker for this role
		tracker = RoleAssignmentTracker.get_or_create_tracker(role_name)
		
		# Find the current position in the provided user list
		current_position = 0
		if tracker.last_assigned_user in user_list:
			try:
				current_position = (user_list.index(tracker.last_assigned_user) + 1) % len(user_list)
			except ValueError:
				current_position = 0
		
		# Get next user from the provided list
		next_user = user_list[current_position]
		
		# Update tracker
		tracker.current_position = (current_position + 1) % len(user_list)
		tracker.last_assigned_user = next_user
		tracker.last_assigned_on = datetime.now()
		tracker.assignment_count += 1
		
		# Parse and update assignment history
		assignment_history = []
		if tracker.assignment_history:
			try:
				assignment_history = json.loads(tracker.assignment_history) if isinstance(tracker.assignment_history, str) else tracker.assignment_history
			except json.JSONDecodeError:
				assignment_history = []
		
		history_entry = {
			"user": next_user,
			"document_type": document_type,
			"document_name": document_name,
			"assigned_on": tracker.last_assigned_on.isoformat(),
			"assigned_by": assigned_by or frappe.session.user,
			"position": current_position,
			"user_list": user_list  # Store the user list used for this assignment
		}
		
		assignment_history.append(history_entry)
		
		# Keep only last 100 assignments in history
		if len(assignment_history) > 100:
			assignment_history = assignment_history[-100:]
		
		tracker.assignment_history = json.dumps(assignment_history)
		
		tracker.save(ignore_permissions=True)
		
		frappe.logger().info(f"Assigned {document_type} {document_name} to {next_user} from user list: {user_list}")
		
		return next_user 