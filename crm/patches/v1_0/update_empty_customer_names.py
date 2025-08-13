import frappe


def execute():
	"""
	Update existing call logs with empty customer_name fields
	to use auto-generated 'Call From xxxxx' format
	"""
	frappe.log("Starting customer name auto-generation migration...")
	
	try:
		# Get all call logs with empty customer_name but with customer phone
		call_logs = frappe.db.sql("""
			SELECT name, customer, customer_name
			FROM `tabCRM Call Log`
			WHERE (customer_name IS NULL OR customer_name = '')
			AND customer IS NOT NULL
			AND customer != ''
		""", as_dict=True)
		
		if not call_logs:
			frappe.log("No call logs found with empty customer names")
			return
		
		frappe.log(f"Found {len(call_logs)} call logs with empty customer names")
		
		updated_count = 0
		
		for call_log in call_logs:
			try:
				customer_phone = call_log.get('customer')
				if customer_phone:
					# First check if we can find an actual contact/lead
					customer_name = get_customer_name_from_phone(customer_phone)
					
					# If still no name found, use auto-generated format
					if not customer_name:
						customer_name = f"Call From {customer_phone}"
					
					# Update the call log
					frappe.db.set_value(
						'CRM Call Log',
						call_log.get('name'),
						'customer_name',
						customer_name
					)
					
					updated_count += 1
					
					if updated_count % 10 == 0:
						frappe.log(f"Updated {updated_count} call logs...")
						
			except Exception as e:
				frappe.log(f"Error updating call log {call_log.get('name')}: {str(e)}")
				continue
		
		# Commit the changes
		frappe.db.commit()
		
		frappe.log(f"Successfully updated {updated_count} call logs with auto-generated customer names")
		
	except Exception as e:
		frappe.log_error(f"Error in customer name migration: {str(e)}")
		raise


def get_customer_name_from_phone(phone_number):
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
		
		return lead if lead else None
		
	except Exception as e:
		frappe.log(f"Error getting customer name for {phone_number}: {str(e)}")
		return None 