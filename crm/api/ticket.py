import frappe
from frappe import _
from datetime import datetime

@frappe.whitelist()
def get_ticket(name):
    """Get ticket details by name"""
    return frappe.get_doc("CRM Ticket", name)

@frappe.whitelist()
def get_tickets(filters=None, order_by="creation desc"):
    """Get list of tickets based on filters"""
    if not filters:
        filters = {}
    
    return frappe.get_list(
        "CRM Ticket",
        filters=filters,
        fields=["*"],
        order_by=order_by
    )

@frappe.whitelist()
def create_ticket(doc):
    """Create a new ticket from either call log or manual entry"""
    if not doc:
        frappe.throw(_("Ticket data is required"))
        
    # Debug logs
    print("=== TICKET API DEBUG ===")
    print("Incoming doc data:", doc)
    
    try:
        # Parse the doc data if it's a string
        if isinstance(doc, str):
            doc = frappe.parse_json(doc)
            
        # Create base ticket doc
        ticket_doc = frappe.get_doc({
            "doctype": "CRM Ticket",
            **doc,
            "owner": frappe.session.user
        })
        
        # If this is from a call log, handle the call log data
        if doc.get("call_log"):
            call_log_doc = frappe.get_doc("CRM Call Log", doc["call_log"])
            
            # Add any missing data from call log
            if not ticket_doc.mobile_no:
                ticket_doc.mobile_no = (
                    call_log_doc.from_number if call_log_doc.type == "Incoming" 
                    else call_log_doc.to_number
                )
                
            # Update the call log to link it to the ticket
            frappe.db.set_value(
                "CRM Call Log", 
                doc["call_log"], 
                "ticket", 
                ticket_doc.name
            )
            
        # Insert the ticket
        ticket_doc.insert(ignore_permissions=True)
        
        # Show success message
        frappe.msgprint(_("Ticket {0} created successfully").format(ticket_doc.name))
        
        return ticket_doc.as_dict()
        
    except Exception as e:
        frappe.log_error(f"Error creating ticket: {str(e)}")
        frappe.throw(_("Error creating ticket: {0}").format(str(e)))

@frappe.whitelist()
def create_ticket_from_call_log(call_log=None, doc=None):
    """Legacy endpoint - redirects to create_ticket"""
    if not call_log or not doc:
        frappe.throw(_("Both call_log and doc are required"))
        
    if isinstance(doc, str):
        doc = frappe.parse_json(doc)
        
    # Add call log to doc data
    doc["call_log"] = call_log
    doc["creation_source"] = "Call Log"
    
    return create_ticket(doc)

@frappe.whitelist()
def update_ticket_status(ticket, status, comment=None):
    """Update ticket status and add comment to timeline"""
    if not ticket or not status:
        frappe.throw(_("Ticket and status are required"))
        
    doc = frappe.get_doc("CRM Ticket", ticket)
    old_status = doc.status
    
    # Update status
    doc.status = status
    doc.save()
    
    # Add comment/activity
    if comment:
        add_ticket_activity(
            ticket=doc.name,
            activity_type="Status Update",
            description=f"Status changed from {old_status} to {status}\n\nComment: {comment}"
        )
    else:
        add_ticket_activity(
            ticket=doc.name,
            activity_type="Status Update",
            description=f"Status changed from {old_status} to {status}"
        )
    
    return doc

@frappe.whitelist()
def get_ticket_activities(ticket):
    """Get all activities for a ticket"""
    if not ticket:
        frappe.throw(_("Ticket is required"))
        
    activities = frappe.get_all(
        "CRM Activity",
        filters={
            "reference_doctype": "CRM Ticket",
            "reference_name": ticket
        },
        fields=["*"],
        order_by="creation desc"
    )
    
    return activities

def add_ticket_activity(ticket, activity_type, description):
    """Add an activity to the ticket timeline"""
    activity = frappe.get_doc({
        "doctype": "CRM Activity",
        "activity_type": activity_type,
        "description": description,
        "reference_doctype": "CRM Ticket",
        "reference_name": ticket,
        "user": frappe.session.user,
        "creation": datetime.now()
    })
    
    activity.insert() 