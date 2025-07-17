import frappe
from frappe import _

@frappe.whitelist()
def search_customer_by_mobile(mobile_no):
    """
    Search for a customer by mobile number and return customer details
    
    Args:
        mobile_no (str): Mobile number to search for
        
    Returns:
        dict: Customer details if found, None if not found
    """
    if not mobile_no:
        return None
    
    try:
        # Clean the mobile number (remove spaces, dashes, etc.)
        clean_mobile = ''.join(filter(str.isdigit, str(mobile_no)))
        
        if not clean_mobile:
            return None
        
        # Search for customer with exact mobile number match
        customer = frappe.db.get_value(
            'CRM Customer',
            {'mobile_no': mobile_no},
            ['name', 'customer_name', 'first_name', 'last_name', 'full_name'],
            as_dict=True
        )
        
        if customer:
            # Return the customer name, prioritizing customer_name field
            customer_name = customer.get('customer_name') or customer.get('full_name')
            if not customer_name:
                # Construct name from first and last name
                first_name = customer.get('first_name', '')
                last_name = customer.get('last_name', '')
                customer_name = f"{first_name} {last_name}".strip()
            
            return {
                'found': True,
                'customer_name': customer_name,
                'customer_id': customer.get('name')
            }
        else:
            # Also search with cleaned mobile number
            customer = frappe.db.get_value(
                'CRM Customer',
                {'mobile_no': clean_mobile},
                ['name', 'customer_name', 'first_name', 'last_name', 'full_name'],
                as_dict=True
            )
            
            if customer:
                customer_name = customer.get('customer_name') or customer.get('full_name')
                if not customer_name:
                    first_name = customer.get('first_name', '')
                    last_name = customer.get('last_name', '')
                    customer_name = f"{first_name} {last_name}".strip()
                
                return {
                    'found': True,
                    'customer_name': customer_name,
                    'customer_id': customer.get('name')
                }
        
        # If not found, return default structure
        return {
            'found': False,
            'customer_name': f"Lead from call {mobile_no}",
            'customer_id': None
        }
        
    except Exception as e:
        frappe.logger().error(f"Error searching customer by mobile {mobile_no}: {str(e)}")
        return {
            'found': False,
            'customer_name': f"Lead from call {mobile_no}",
            'customer_id': None,
            'error': str(e)
        } 