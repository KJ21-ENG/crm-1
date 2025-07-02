import frappe

def execute():
    """
    Migrate existing caller/receiver data to employee/customer fields
    """
    frappe.logger().info("Starting migration from caller/receiver to employee/customer")
    
    # Get all call logs
    call_logs = frappe.get_all(
        'CRM Call Log',
        fields=['name', 'caller', 'receiver', 'type', 'from', 'to'],
        filters={'docstatus': ['!=', 2]}  # Not cancelled
    )
    
    frappe.logger().info(f"Found {len(call_logs)} call logs to migrate")
    
    migrated_count = 0
    error_count = 0
    
    for log in call_logs:
        try:
            employee = None
            customer = None
            customer_name = None
            
            if log.type == 'Outgoing':
                # Employee made the call
                employee = log.caller
                customer = log.to
                # Try to get customer name from contacts/leads
                customer_name = get_contact_name_by_phone(log.to)
                
            elif log.type == 'Incoming':
                # Employee received the call  
                employee = log.receiver
                customer = log.get('from')  # Using get() to handle None values
                customer_name = get_contact_name_by_phone(log.get('from'))
            
            # Update the document if we have meaningful data
            if employee or customer:
                frappe.db.set_value(
                    'CRM Call Log', 
                    log.name,
                    {
                        'employee': employee,
                        'customer': customer,
                        'customer_name': customer_name
                    }
                )
                migrated_count += 1
                
        except Exception as e:
            frappe.logger().error(f"Error migrating call log {log.name}: {str(e)}")
            error_count += 1
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Migration completed: {migrated_count} migrated, {error_count} errors")
    print(f"Migrated {migrated_count} call logs, {error_count} errors")

def get_contact_name_by_phone(phone_number):
    """Get contact name from phone number"""
    if not phone_number:
        return None
        
    try:
        # Clean phone number for better matching
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
        frappe.logger().error(f"Error getting contact name for {phone_number}: {str(e)}")
        return None 