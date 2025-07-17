# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr


@frappe.whitelist()
def get_customer_by_mobile(mobile_no):
    """Get customer details by mobile number"""
    from crm.fcrm.doctype.crm_customer.crm_customer import get_customer_by_mobile as get_customer
    return get_customer(mobile_no)


@frappe.whitelist()
def create_or_update_customer(mobile_no, first_name=None, last_name=None, 
                             email=None, organization=None, job_title=None,
                             customer_source="Lead", reference_doctype=None, 
                             reference_docname=None, **kwargs):
    """Create new customer or update existing customer data"""
    
    if not mobile_no:
        frappe.throw(_("Mobile number is required"))
    
    # Check if customer already exists
    existing_customer = get_customer_by_mobile(mobile_no)
    
    if existing_customer:
        # Update existing customer
        from crm.fcrm.doctype.crm_customer.crm_customer import update_customer_data
        return update_customer_data(mobile_no, 
                                  first_name=first_name,
                                  last_name=last_name,
                                  email=email,
                                  organization=organization,
                                  job_title=job_title,
                                  **kwargs)
    else:
        # Create new customer
        from crm.fcrm.doctype.crm_customer.crm_customer import create_customer_from_lead_or_ticket
        return create_customer_from_lead_or_ticket(mobile_no,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 email=email,
                                                 organization=organization,
                                                 job_title=job_title,
                                                 customer_source=customer_source,
                                                 reference_doctype=reference_doctype,
                                                 reference_docname=reference_docname,
                                                 **kwargs)


@frappe.whitelist()
def get_customer_list(limit=20, start=0, search_term="", filters=None):
    """Get paginated customer list with search and filtering"""
    from crm.fcrm.doctype.crm_customer.crm_customer import get_customer_list as get_customers
    return get_customers(limit=limit, start=start, search_term=search_term)


@frappe.whitelist()
def auto_fill_customer_data(mobile_no):
    """Get customer data for auto-filling forms based on mobile number"""
    if not mobile_no:
        return {}
        
    customer = get_customer_by_mobile(mobile_no)
    if customer:
        return {
            "first_name": customer.get("first_name", ""),
            "last_name": customer.get("last_name", ""),
            "email": customer.get("email", ""),
            "organization": customer.get("organization", ""),
            "job_title": customer.get("job_title", ""),
            "phone": customer.get("phone", ""),
            "salutation": customer.get("salutation", ""),
            "gender": customer.get("gender", ""),
            "middle_name": customer.get("middle_name", ""),
            "customer_name": customer.get("customer_name", "")
        }
    
    return {}


@frappe.whitelist()
def process_lead_creation(lead_data):
    """Process lead creation and customer data management"""
    mobile_no = lead_data.get("mobile_no")
    
    if mobile_no:
        # Create or update customer record
        customer = create_or_update_customer(
            mobile_no=mobile_no,
            first_name=lead_data.get("first_name"),
            last_name=lead_data.get("last_name"),
            email=lead_data.get("email"),
            organization=lead_data.get("organization"),
            job_title=lead_data.get("job_title"),
            pan_card_number=lead_data.get("pan_card_number"),
            aadhaar_card_number=lead_data.get("aadhaar_card_number"),
            customer_source="Lead",
            reference_doctype="CRM Lead",
            reference_docname=lead_data.get("name")
        )
        
        return {"customer": customer, "lead": lead_data}
    
    return {"lead": lead_data}


@frappe.whitelist()
def process_ticket_creation(ticket_data):
    """Process ticket creation and customer data management"""
    mobile_no = ticket_data.get("mobile_no")
    
    if mobile_no:
        # Create or update customer record
        customer = create_or_update_customer(
            mobile_no=mobile_no,
            first_name=ticket_data.get("first_name"),
            last_name=ticket_data.get("last_name"),
            email=ticket_data.get("email"),
            organization=ticket_data.get("organization"),
            pan_card_number=ticket_data.get("pan_card_number"),
            aadhaar_card_number=ticket_data.get("aadhaar_card_number"),
            customer_source="Ticket",
            reference_doctype="CRM Ticket",
            reference_docname=ticket_data.get("name")
        )
        
        return {"customer": customer, "ticket": ticket_data}
    
    return {"ticket": ticket_data}


@frappe.whitelist()
def get_customer_interactions(customer_mobile):
    """Get all interactions (leads, tickets, call logs) for a customer"""
    if not customer_mobile:
        return {}
    
    # Get leads for this customer
    leads = frappe.get_list("CRM Lead",
                           filters={"mobile_no": customer_mobile},
                           fields=["name", "lead_name", "status", "creation", "lead_owner"],
                           order_by="creation desc")
    
    # Get tickets for this customer  
    tickets = frappe.get_list("CRM Ticket",
                             filters={"mobile_no": customer_mobile},
                             fields=["name", "ticket_subject", "status", "creation", "assigned_to"],
                             order_by="creation desc")
    
    # Get call logs for this customer
    call_logs = frappe.get_list("CRM Call Log",
                               filters={"customer": customer_mobile},
                               fields=["name", "type", "status", "duration", "start_time", "employee"],
                               order_by="start_time desc")
    
    return {
        "leads": leads,
        "tickets": tickets,
        "call_logs": call_logs
    }


@frappe.whitelist()
def get_customer_stats():
    """Get customer statistics for dashboard"""
    total_customers = frappe.db.count("CRM Customer", {"status": "Active"})
    
    # Customers created this month
    from frappe.utils import get_first_day, get_last_day
    import datetime
    
    today = datetime.date.today()
    first_day = get_first_day(today)
    last_day = get_last_day(today)
    
    new_customers_this_month = frappe.db.count("CRM Customer", {
        "status": "Active",
        "creation": ["between", [first_day, last_day]]
    })
    
    # Customer sources breakdown
    source_breakdown = frappe.db.sql("""
        SELECT customer_source, COUNT(*) as count
        FROM `tabCRM Customer`
        WHERE status = 'Active'
        GROUP BY customer_source
        ORDER BY count DESC
    """, as_dict=True)
    
    return {
        "total_customers": total_customers,
        "new_customers_this_month": new_customers_this_month,
        "source_breakdown": source_breakdown
    } 