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
        result = update_customer_data(mobile_no, 
                                  first_name=first_name,
                                  last_name=last_name,
                                  email=email,
                                  organization=organization,
                                  job_title=job_title,
                                  **kwargs)
        return {
            "name": existing_customer.name,
            "action": "updated",
            "message": "Customer updated successfully"
        }
    else:
        # Create new customer
        from crm.fcrm.doctype.crm_customer.crm_customer import create_customer_from_lead_or_ticket
        result = create_customer_from_lead_or_ticket(mobile_no,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 email=email,
                                                 organization=organization,
                                                 job_title=job_title,
                                                 customer_source=customer_source,
                                                 reference_doctype=reference_doctype,
                                                 reference_docname=reference_docname,
                                                 **kwargs)
        return {
            "name": result["name"],
            "action": "created",
            "message": "Customer created successfully"
        }


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
            "customer_name": customer.get("customer_name", ""),
            "pan_card_number": customer.get("pan_card_number", ""),
            "aadhaar_card_number": customer.get("aadhaar_card_number", ""),
            "referral_code": customer.get("referral_code", ""),
            "referral_through": customer.get("referral_through", "")
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
            referral_code=lead_data.get("referral_code"),
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
            referral_code=ticket_data.get("referral_code"),
            customer_source="Ticket",
            reference_doctype="CRM Ticket",
            reference_docname=ticket_data.get("name")
        )
        
        return {"customer": customer, "ticket": ticket_data}
    
    return {"ticket": ticket_data}


@frappe.whitelist()
def get_customer_interactions(customer_mobile: str | None = None, customer_id: str | None = None):
    """Get all interactions (leads, tickets, call logs) for a customer.

    New logic: If ``customer_id`` (CRM Customer.name) is provided, match:
      - Leads by lead.client_id == customer_id
      - Tickets by ticket.client_id == customer_id when column exists,
        otherwise fallback to ticket.customer_id == customer_id

    Fallback: If only ``customer_mobile`` is provided, match by mobile_no as before.
    """
    if not customer_id and not customer_mobile:
        return {}

    leads_filters = {}
    tickets_filters = {}
    call_logs_filters = {}

    if customer_id:
        # Leads: match by client_id OR legacy customer_id link
        leads_or_filters = [["client_id", "=", customer_id], ["customer_id", "=", customer_id]]
        # Tickets: match by client_id if present OR customer_id (legacy)
        tickets_or_filters = [["customer_id", "=", customer_id]]
        if frappe.db.has_column("CRM Ticket", "client_id"):
            tickets_or_filters.insert(0, ["client_id", "=", customer_id])
        # Save for later call
        leads_filters = None
        tickets_filters = None
    else:
        # Fallback to mobile matching
        leads_filters = {"mobile_no": customer_mobile}
        tickets_filters = {"mobile_no": customer_mobile}
        call_logs_filters = {"customer": customer_mobile}

    # Get leads
    if customer_id:
        leads = frappe.get_list(
            "CRM Lead",
            or_filters=leads_or_filters,
            fields=["name", "lead_name", "customer_id", "status", "creation", "lead_owner"],
            order_by="creation desc",
        )
    else:
        leads = frappe.get_list(
            "CRM Lead",
            filters=leads_filters,
            fields=["name", "lead_name", "customer_id", "status", "creation", "lead_owner"],
            order_by="creation desc",
        )

    # Get tickets
    if customer_id:
        tickets = frappe.get_list(
            "CRM Ticket",
            or_filters=tickets_or_filters,
            fields=["name", "ticket_subject", "subject", "customer_id", "status", "creation", "assigned_to"],
            order_by="creation desc",
        )
    else:
        tickets = frappe.get_list(
            "CRM Ticket",
            filters=tickets_filters,
            fields=["name", "ticket_subject", "subject", "customer_id", "status", "creation", "assigned_to"],
            order_by="creation desc",
        )

    # Get call logs
    call_logs = []
    try:
        logs_by_mobile = []
        logs_by_ref = []
        if customer_mobile:
            logs_by_mobile = frappe.get_list(
                "CRM Call Log",
                filters={"customer": customer_mobile},
                fields=["name", "type", "status", "duration", "start_time", "employee"],
                order_by="start_time desc",
            )
        if customer_id:
            logs_by_ref = frappe.get_list(
                "CRM Call Log",
                filters={
                    "reference_doctype": "CRM Customer",
                    "reference_docname": customer_id,
                },
                fields=["name", "type", "status", "duration", "start_time", "employee"],
                order_by="start_time desc",
            )

        # Merge and de-duplicate by name, keep latest first
        merged = {log["name"]: log for log in logs_by_mobile}
        for log in logs_by_ref:
            merged.setdefault(log["name"], log)
        call_logs = sorted(merged.values(), key=lambda x: x.get("start_time") or 0, reverse=True)
    except Exception:
        # Non-fatal; interactions can still render
        call_logs = []

    # Enrich names using CRM Customer if missing
    try:
        customer_ids = set()
        for l in leads:
            if l.get("customer_id"):
                customer_ids.add(l["customer_id"])
        for t in tickets:
            if t.get("customer_id"):
                customer_ids.add(t["customer_id"])
        if customer_ids:
            rows = frappe.get_all("CRM Customer", filters={"name": ["in", list(customer_ids)]}, fields=["name", "customer_name"])
            id_to_name = {r["name"]: r["customer_name"] for r in rows}
            for l in leads:
                if not l.get("lead_name") and l.get("customer_id"):
                    l["lead_name"] = id_to_name.get(l["customer_id"]) or l.get("name")
            for t in tickets:
                if not (t.get("subject") or t.get("ticket_subject")) and t.get("customer_id"):
                    t["subject"] = id_to_name.get(t["customer_id"]) or t.get("name")
    except Exception:
        pass

    return {"leads": leads, "tickets": tickets, "call_logs": call_logs}


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


@frappe.whitelist()
def create_or_find_customer(lead_name, mobile_no, customer_name, email=None):
    """Create or find customer for a lead"""
    try:
        if not mobile_no:
            return {"success": False, "message": "Mobile number is required"}
        
        # Check if customer already exists with this mobile number
        existing_customers = frappe.get_all("CRM Customer", 
            filters={"mobile_no": mobile_no},
            fields=["name", "customer_name", "email"]
        )
        
        if existing_customers:
            # Customer exists, return the first one
            customer = existing_customers[0]
            return {
                "success": True, 
                "customer_name": customer.name,
                "action": "found",
                "message": f"Customer found: {customer.customer_name}"
            }
        else:
            # Create new customer
            customer = frappe.new_doc("CRM Customer")
            customer.customer_name = customer_name
            customer.mobile_no = mobile_no
            customer.email = email
            customer.status = "Active"
            customer.insert(ignore_permissions=True)
            
            return {
                "success": True,
                "customer_name": customer.name,
                "action": "created",
                "message": f"Customer created: {customer.customer_name}"
            }
            
    except Exception as e:
        frappe.log_error(f"Error in create_or_find_customer: {str(e)}")
        return {"success": False, "message": str(e)} 


@frappe.whitelist()
def get_customer_by_id(customer_id):
    """Get customer details by customer ID (customer name)"""
    if not customer_id:
        return None
    
    customer = frappe.db.get_value(
        "CRM Customer",
        {"name": customer_id},
        ["name", "customer_name", "first_name", "last_name", "email", 
         "mobile_no", "organization", "status", "customer_source",
         "pan_card_number", "aadhaar_card_number", "referral_code", "image"],
        as_dict=True
    )
    
    return customer


@frappe.whitelist()
def get_customer_data_for_lead(lead_name):
    """Get customer data for a specific lead using customer_id"""
    if not lead_name:
        return None
    
    # Get the customer_id from the lead
    customer_id = frappe.db.get_value("CRM Lead", lead_name, "customer_id")
    
    if not customer_id:
        return None
    
    # Get customer data using customer_id
    return get_customer_by_id(customer_id)


@frappe.whitelist()
def get_customer_data_for_ticket(ticket_name):
    """Get customer data for a specific ticket using customer_id"""
    if not ticket_name:
        return None
    
    # Get the customer_id from the ticket
    customer_id = frappe.db.get_value("CRM Ticket", ticket_name, "customer_id")
    
    if not customer_id:
        return None
    
    # Get customer data using customer_id
    return get_customer_by_id(customer_id)


@frappe.whitelist()
def update_lead_customer_data(lead_name, customer_data):
    """Update customer data for a lead - updates both lead and customer records"""
    if not lead_name:
        frappe.throw(_("Lead name is required"))
    
    lead = frappe.get_doc("CRM Lead", lead_name)
    customer_id = lead.customer_id
    
    if not customer_id:
        frappe.throw(_("No customer associated with this lead"))
    
    # Update customer record
    customer = frappe.get_doc("CRM Customer", customer_id)
    
    # Update customer fields
    for field, value in customer_data.items():
        if hasattr(customer, field) and value is not None:
            setattr(customer, field, value)
    
    customer.save()
    
    # Update lead fields to match customer
    sync_fields = ['first_name', 'last_name', 'email', 'mobile_no', 'pan_card_number', 'aadhaar_card_number']
    for field in sync_fields:
        if field in customer_data and customer_data[field] is not None:
            setattr(lead, field, customer_data[field])
    
    lead.save()
    
    return {
        "success": True,
        "message": "Customer and lead data updated successfully"
    }


@frappe.whitelist()
def update_ticket_customer_data(ticket_name, customer_data):
    """Update customer data for a ticket - updates both ticket and customer records"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    customer_id = ticket.customer_id
    
    if not customer_id:
        frappe.throw(_("No customer associated with this ticket"))
    
    # Update customer record
    customer = frappe.get_doc("CRM Customer", customer_id)
    
    # Update customer fields
    for field, value in customer_data.items():
        if hasattr(customer, field) and value is not None:
            setattr(customer, field, value)
    
    customer.save()
    
    # Update ticket fields to match customer
    sync_fields = ['first_name', 'last_name', 'email', 'mobile_no', 'pan_card_number', 'aadhaar_card_number']
    for field in sync_fields:
        if field in customer_data and customer_data[field] is not None:
            setattr(ticket, field, customer_data[field])
    
    ticket.save()
    
    return {
        "success": True,
        "message": "Customer and ticket data updated successfully"
    } 

@frappe.whitelist()
def get_lead_with_customer_data(lead_name):
	"""Get lead data with customer data merged"""
	if not lead_name: return None
	lead = frappe.get_doc("CRM Lead", lead_name)
	lead_dict = lead.as_dict()
	
	# Get customer data
	customer_data = get_customer_data_for_lead(lead_name)
	if customer_data:
		# Merge customer data into lead data
		for key, value in customer_data.items():
			if key not in lead_dict or lead_dict[key] is None:
				lead_dict[key] = value
	
	return lead_dict

@frappe.whitelist()
def update_customer_image(customer_id, image):
    """Update customer image"""
    if not customer_id:
        frappe.throw(_("Customer ID is required"))
    
    if not image:
        frappe.throw(_("Image URL is required"))
    
    try:
        customer = frappe.get_doc("CRM Customer", customer_id)
        customer.image = image
        customer.save()
        
        return {
            "success": True,
            "message": "Customer image updated successfully"
        }
    except Exception as e:
        frappe.log_error(f"Error updating customer image: {str(e)}", "Customer Image Update Error")
        frappe.throw(_("Error updating customer image: {0}").format(str(e)))


@frappe.whitelist()
def get_ticket_with_customer_data(ticket_name):
	"""Get ticket data with customer data merged"""
	if not ticket_name: return None
	ticket = frappe.get_doc("CRM Ticket", ticket_name)
	ticket_dict = ticket.as_dict()
	
	# Get customer data
	customer_data = get_customer_data_for_ticket(ticket_name)
	if customer_data:
		# Merge customer data into ticket data
		for key, value in customer_data.items():
			if key not in ticket_dict or ticket_dict[key] is None:
				ticket_dict[key] = value
	
	return ticket_dict 