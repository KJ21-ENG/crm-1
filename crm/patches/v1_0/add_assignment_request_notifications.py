# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""
	Add new notification types for assignment requests to CRM Task Notification DocType
	"""
	
	# Get the CRM Task Notification DocType
	doc_type = frappe.get_doc("DocType", "CRM Task Notification")
	
	# Find the notification_type field
	notification_type_field = None
	for field in doc_type.fields:
		if field.fieldname == "notification_type":
			notification_type_field = field
			break
	
	if notification_type_field:
		# Add new notification types if they don't exist
		current_options = notification_type_field.options.split('\n')
		new_options = [
			"Assignment Request",
			"Assignment Request Submitted", 
			"Assignment Request Approved"
		]
		
		# Add only new options that don't exist
		for option in new_options:
			if option not in current_options:
				current_options.append(option)
		
		# Update the field options
		notification_type_field.options = '\n'.join(current_options)
		doc_type.save()
		
		frappe.db.commit()
		
		print("✅ Added new notification types to CRM Task Notification DocType")
	else:
		print("❌ Could not find notification_type field in CRM Task Notification DocType")
