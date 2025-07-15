import frappe
from frappe import _
from frappe.utils import now, time_diff_in_seconds

from crm.api.doc import get_assigned_users, get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_ticket(name):
    ticket = frappe.get_doc("CRM Ticket", name)
    ticket.check_permission("read")

    ticket = ticket.as_dict()

    ticket["fields_meta"] = get_fields_meta("CRM Ticket")
    ticket["_form_script"] = get_form_script("CRM Ticket")
    ticket["_assign"] = get_assigned_users("CRM Ticket", name)

    return ticket

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

        # Handle resolved state
        if ticket_doc.status == "Resolved":
            ticket_doc.resolved = 1
            ticket_doc.resolved_on = now()
            # Calculate resolution time (in seconds)
            ticket_doc.resolution_time = time_diff_in_seconds(
                ticket_doc.resolved_on,
                ticket_doc.creation or now()
            )
                
        # Insert the ticket
        ticket_doc.insert(ignore_permissions=True)
        
        # Link call log to ticket AFTER ticket creation to get the ticket name
        if doc.get("call_log"):
            # Update the call log to link it to the ticket
            frappe.db.set_value(
                "CRM Call Log", 
                doc["call_log"], 
                "ticket", 
                ticket_doc.name
            )
            
            # Also set reference fields for consistency
            frappe.db.set_value(
                "CRM Call Log", 
                doc["call_log"], 
                {
                    "reference_doctype": "CRM Ticket",
                    "reference_docname": ticket_doc.name
                }
            )
        
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
def bulk_update_tickets(ticket_names, updates):
    """Bulk update multiple tickets with the same values"""
    if not ticket_names or not updates:
        frappe.throw(_("Ticket names and updates are required"))
    
    if isinstance(ticket_names, str):
        ticket_names = frappe.parse_json(ticket_names)
    
    if isinstance(updates, str):
        updates = frappe.parse_json(updates)
    
    updated_tickets = []
    
    for ticket_name in ticket_names:
        try:
            ticket = frappe.get_doc("CRM Ticket", ticket_name)
            
            # Track changes for activity log
            changes = []
            
            for field, value in updates.items():
                if field in ticket.as_dict() and ticket.get(field) != value:
                    old_value = ticket.get(field)
                    ticket.set(field, value)
                    changes.append(f"{field}: {old_value} → {value}")
            
            if changes:
                ticket.save(ignore_permissions=True)
                
                # Add activity log
                add_ticket_activity(
                    ticket=ticket.name,
                    activity_type="Bulk Update",
                    description=f"Bulk updated: {', '.join(changes)}"
                )
                
                updated_tickets.append(ticket.name)
                
        except Exception as e:
            frappe.log_error(f"Error updating ticket {ticket_name}: {str(e)}")
            continue
    
    frappe.msgprint(_("Successfully updated {0} tickets").format(len(updated_tickets)))
    return updated_tickets

@frappe.whitelist()
def bulk_assign_tickets(ticket_names, assigned_to):
    """Bulk assign multiple tickets to a user"""
    if not ticket_names or not assigned_to:
        frappe.throw(_("Ticket names and assigned user are required"))
    
    if isinstance(ticket_names, str):
        ticket_names = frappe.parse_json(ticket_names)
    
    updated_tickets = []
    
    for ticket_name in ticket_names:
        try:
            ticket = frappe.get_doc("CRM Ticket", ticket_name)
            old_assignee = ticket.assigned_to
            
            ticket.assigned_to = assigned_to
            ticket.save(ignore_permissions=True)
            
            # Add activity log
            add_ticket_activity(
                ticket=ticket.name,
                activity_type="Assignment",
                description=f"Assigned from {old_assignee or 'Unassigned'} to {assigned_to}"
            )
            
            updated_tickets.append(ticket.name)
            
        except Exception as e:
            frappe.log_error(f"Error assigning ticket {ticket_name}: {str(e)}")
            continue
    
    frappe.msgprint(_("Successfully assigned {0} tickets").format(len(updated_tickets)))
    return updated_tickets

@frappe.whitelist()
def bulk_close_tickets(ticket_names, resolution=None):
    """Bulk close multiple tickets"""
    if not ticket_names:
        frappe.throw(_("Ticket names are required"))
    
    if isinstance(ticket_names, str):
        ticket_names = frappe.parse_json(ticket_names)
    
    updated_tickets = []
    
    for ticket_name in ticket_names:
        try:
            ticket = frappe.get_doc("CRM Ticket", ticket_name)
            
            # Skip if already closed
            if ticket.status == "Closed":
                continue
                
            old_status = ticket.status
            ticket.status = "Closed"
            ticket.resolved = 1
            ticket.resolved_on = now()
            
            if resolution:
                ticket.resolution = resolution
            
            ticket.save(ignore_permissions=True)
            
            # Add activity log
            add_ticket_activity(
                ticket=ticket.name,
                activity_type="Status Update",
                description=f"Bulk closed: Status changed from {old_status} to Closed" + 
                           (f"\n\nResolution: {resolution}" if resolution else "")
            )
            
            updated_tickets.append(ticket.name)
            
        except Exception as e:
            frappe.log_error(f"Error closing ticket {ticket_name}: {str(e)}")
            continue
    
    frappe.msgprint(_("Successfully closed {0} tickets").format(len(updated_tickets)))
    return updated_tickets

@frappe.whitelist()
def bulk_set_priority(ticket_names, priority):
    """Bulk set priority for multiple tickets"""
    if not ticket_names or not priority:
        frappe.throw(_("Ticket names and priority are required"))
    
    if isinstance(ticket_names, str):
        ticket_names = frappe.parse_json(ticket_names)
    
    valid_priorities = ["Low", "Medium", "High", "Urgent"]
    if priority not in valid_priorities:
        frappe.throw(_("Priority must be one of: {0}").format(", ".join(valid_priorities)))
    
    updated_tickets = []
    
    for ticket_name in ticket_names:
        try:
            ticket = frappe.get_doc("CRM Ticket", ticket_name)
            
            if ticket.priority != priority:
                old_priority = ticket.priority
                ticket.priority = priority
                ticket.save(ignore_permissions=True)
                
                # Add activity log
                add_ticket_activity(
                    ticket=ticket.name,
                    activity_type="Priority Update",
                    description=f"Priority changed from {old_priority} to {priority}"
                )
                
                updated_tickets.append(ticket.name)
                
        except Exception as e:
            frappe.log_error(f"Error updating priority for ticket {ticket_name}: {str(e)}")
            continue
    
    frappe.msgprint(_("Successfully updated priority for {0} tickets").format(len(updated_tickets)))
    return updated_tickets

@frappe.whitelist()
def get_customer_history(mobile_no=None, email=None):
    """Get customer history including existing tickets and leads"""
    if not mobile_no and not email:
        return {
            "tickets": [],
            "leads": [],
            "summary": {
                "total_tickets": 0,
                "open_tickets": 0,
                "total_leads": 0,
                "last_interaction": None
            }
        }
    
    # Get tickets matching mobile_no or email (exclude closed tickets)
    tickets = []
    if mobile_no:
        mobile_tickets = frappe.get_list(
            "CRM Ticket",
            filters={
                "mobile_no": mobile_no,
                "status": ["not in", ["Closed", "Resolved"]]
            },
            fields=["name", "ticket_subject", "status", "priority", "creation", "modified"],
            order_by="creation desc",
            limit=20
        )
        tickets.extend(mobile_tickets)
    
    if email:
        email_tickets = frappe.get_list(
            "CRM Ticket", 
            filters={
                "email": email,
                "status": ["not in", ["Closed", "Resolved"]]
            },
            fields=["name", "ticket_subject", "status", "priority", "creation", "modified"],
            order_by="creation desc",
            limit=20
        )
        tickets.extend(email_tickets)
    
    # Remove duplicates (in case a ticket has both matching mobile and email)
    seen_tickets = set()
    unique_tickets = []
    for ticket in tickets:
        if ticket.name not in seen_tickets:
            seen_tickets.add(ticket.name)
            unique_tickets.append(ticket)
    
    # Sort by creation date and limit
    unique_tickets.sort(key=lambda x: x.creation, reverse=True)
    tickets = unique_tickets[:10]
    
    # Get leads matching mobile_no or email (exclude closed/converted leads)
    leads = []
    if mobile_no:
        mobile_leads = frappe.get_list(
            "CRM Lead",
            filters={
                "mobile_no": mobile_no,
                "status": ["not in", ["Converted", "Do Not Contact", "Lost"]]
            },
            fields=["name", "lead_name", "status", "creation", "modified"],
            order_by="creation desc",
            limit=20
        )
        leads.extend(mobile_leads)
    
    if email:
        email_leads = frappe.get_list(
            "CRM Lead",
            filters={
                "email": email,
                "status": ["not in", ["Converted", "Do Not Contact", "Lost"]]
            }, 
            fields=["name", "lead_name", "status", "creation", "modified"],
            order_by="creation desc",
            limit=20
        )
        leads.extend(email_leads)
    
    # Remove duplicates
    seen_leads = set()
    unique_leads = []
    for lead in leads:
        if lead.name not in seen_leads:
            seen_leads.add(lead.name)
            unique_leads.append(lead)
    
    # Sort by creation date and limit
    unique_leads.sort(key=lambda x: x.creation, reverse=True)
    leads = unique_leads[:10]
    
    # Calculate summary
    open_ticket_statuses = ["New", "Open", "In Progress", "Pending Customer"]
    open_tickets = len([t for t in tickets if t.status in open_ticket_statuses])
    
    # Get last interaction date
    all_interactions = []
    for ticket in tickets:
        all_interactions.append(ticket.modified)
    for lead in leads:
        all_interactions.append(lead.modified)
    
    last_interaction = max(all_interactions) if all_interactions else None
    
    summary = {
        "total_tickets": len(tickets),
        "open_tickets": open_tickets,
        "total_leads": len(leads),
        "last_interaction": last_interaction
    }
    
    return {
        "tickets": tickets,
        "leads": leads,
        "summary": summary
    }

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

@frappe.whitelist()
def escalate_ticket(ticket_name, escalation_reason=None, escalate_to=None):
    """Escalate a ticket to higher priority or different department"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    
    # Determine escalation logic
    priority_escalation = {
        "Low": "Medium",
        "Medium": "High", 
        "High": "Urgent",
        "Urgent": "Urgent"  # Already at highest
    }
    
    old_priority = ticket.priority
    old_assigned_to = ticket.assigned_to
    
    # Escalate priority
    if ticket.priority != "Urgent":
        ticket.priority = priority_escalation.get(ticket.priority, "High")
    
    # Escalate assignment if specified
    if escalate_to:
        ticket.assigned_to = escalate_to
    elif ticket.department == "Support":
        # Auto-escalate to manager or senior support
        senior_users = frappe.get_list(
            "User",
            filters={
                "role_profile_name": ["in", ["Support Manager", "Senior Support"]],
                "enabled": 1
            },
            fields=["name"],
            limit=1
        )
        if senior_users:
            ticket.assigned_to = senior_users[0].name
    
    # Add escalation flag
    ticket.escalated = 1
    ticket.escalation_reason = escalation_reason or "Manual escalation"
    ticket.escalated_on = now()
    
    ticket.save(ignore_permissions=True)
    
    # Add activity log
    escalation_desc = f"Ticket escalated: Priority {old_priority} → {ticket.priority}"
    if old_assigned_to != ticket.assigned_to:
        escalation_desc += f"\nReassigned from {old_assigned_to or 'Unassigned'} to {ticket.assigned_to}"
    if escalation_reason:
        escalation_desc += f"\nReason: {escalation_reason}"
    
    add_ticket_activity(
        ticket=ticket.name,
        activity_type="Escalation",
        description=escalation_desc
    )
    
    frappe.msgprint(_("Ticket escalated successfully"))
    return ticket.name

@frappe.whitelist()
def auto_assign_ticket(ticket_name):
    """Auto-assign ticket based on department and issue type"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    
    # Define assignment rules based on department and issue type
    assignment_rules = {
        "Support": {
            "Technical": ["role_profile_name", "=", "Technical Support"],
            "Billing": ["role_profile_name", "=", "Billing Support"],
            "Account": ["role_profile_name", "=", "Account Support"],
            "General": ["role_profile_name", "=", "Support Agent"],
            "Complaint": ["role_profile_name", "=", "Support Manager"]
        },
        "Technical": {
            "Technical": ["role_profile_name", "=", "Technical Support"],
            "General": ["role_profile_name", "=", "Technical Support"]
        },
        "Billing": {
            "Billing": ["role_profile_name", "=", "Billing Support"],
            "Account": ["role_profile_name", "=", "Account Support"]
        }
    }
    
    # Get assignment rule for this ticket
    dept_rules = assignment_rules.get(ticket.department, {})
    rule = dept_rules.get(ticket.issue_type, ["role_profile_name", "=", "Support Agent"])
    
    # Find available users with round-robin assignment
    available_users = frappe.get_list(
        "User",
        filters={
            rule[0]: rule[2],
            "enabled": 1
        },
        fields=["name", "full_name"],
        order_by="last_assigned_ticket"
    )
    
    if available_users:
        # Assign to user with least recent assignment
        assigned_user = available_users[0]
        old_assigned_to = ticket.assigned_to
        
        ticket.assigned_to = assigned_user.name
        ticket.save(ignore_permissions=True)
        
        # Update user's last assignment timestamp
        frappe.db.set_value("User", assigned_user.name, "last_assigned_ticket", now())
        
        # Add activity log
        add_ticket_activity(
            ticket=ticket.name,
            activity_type="Auto Assignment",
            description=f"Auto-assigned from {old_assigned_to or 'Unassigned'} to {assigned_user.full_name} based on department ({ticket.department}) and issue type ({ticket.issue_type})"
        )
        
        return assigned_user.name
    
    return None

@frappe.whitelist()
def check_sla_breaches():
    """Check for SLA breaches and auto-escalate if needed"""
    # Get all open tickets with SLA
    open_tickets = frappe.get_list(
        "CRM Ticket",
        filters={
            "status": ["not in", ["Closed", "Resolved"]],
            "sla": ["!=", ""],
            "escalated": 0
        },
        fields=["name", "creation", "sla", "priority", "response_by"]
    )
    
    escalated_tickets = []
    
    for ticket_data in open_tickets:
        # Check if response time is breached
        if ticket_data.response_by and now() > ticket_data.response_by:
            # Auto-escalate
            escalate_ticket(
                ticket_data.name,
                escalation_reason="SLA breach - Response time exceeded",
                escalate_to=None
            )
            escalated_tickets.append(ticket_data.name)
    
    return escalated_tickets

@frappe.whitelist()
def get_department_metrics(department=None):
    """Get support metrics for department analysis"""
    filters = {}
    if department:
        filters["department"] = department
    
    # Get ticket counts by status
    status_counts = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabCRM Ticket`
        WHERE department = %(department)s OR %(department)s IS NULL
        GROUP BY status
    """, {"department": department}, as_dict=True)
    
    # Get priority distribution
    priority_counts = frappe.db.sql("""
        SELECT priority, COUNT(*) as count
        FROM `tabCRM Ticket`
        WHERE department = %(department)s OR %(department)s IS NULL
        GROUP BY priority
    """, {"department": department}, as_dict=True)
    
    # Get escalation metrics
    escalation_metrics = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_escalated,
            AVG(TIMESTAMPDIFF(HOUR, creation, escalated_on)) as avg_escalation_time_hours
        FROM `tabCRM Ticket`
        WHERE escalated = 1 
        AND (department = %(department)s OR %(department)s IS NULL)
    """, {"department": department}, as_dict=True)
    
    # Get resolution time metrics
    resolution_metrics = frappe.db.sql("""
        SELECT 
            AVG(TIMESTAMPDIFF(HOUR, creation, resolved_on)) as avg_resolution_time_hours,
            COUNT(*) as total_resolved
        FROM `tabCRM Ticket`
        WHERE status = 'Closed' 
        AND resolved_on IS NOT NULL
        AND (department = %(department)s OR %(department)s IS NULL)
    """, {"department": department}, as_dict=True)
    
    return {
        "status_distribution": status_counts,
        "priority_distribution": priority_counts,
        "escalation_metrics": escalation_metrics[0] if escalation_metrics else {},
        "resolution_metrics": resolution_metrics[0] if resolution_metrics else {}
    }

def add_ticket_activity(ticket, activity_type, description):
    """Add an activity to the ticket timeline"""
    activity = frappe.get_doc({
        "doctype": "CRM Activity",
        "activity_type": activity_type,
        "description": description,
        "reference_doctype": "CRM Ticket",
        "reference_name": ticket,
        "user": frappe.session.user,
        "creation": now()
    })
    
    activity.insert() 

@frappe.whitelist()
def log_ticket_resolution(ticket_name, resolution_notes=None, resolution_time=None):
    """Log ticket resolution with detailed information"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    
    # Update resolution fields
    ticket.resolved = 1
    ticket.resolved_on = now()
    if resolution_notes:
        ticket.resolution = resolution_notes
    if resolution_time:
        ticket.resolution_time = resolution_time
    
    ticket.save(ignore_permissions=True)
    
    # Add detailed resolution activity
    description = f"Ticket resolved and closed"
    if resolution_notes:
        description += f"\n\nResolution Notes: {resolution_notes}"
    if resolution_time:
        description += f"\nResolution Time: {resolution_time} minutes"
    
    add_ticket_activity(
        ticket=ticket.name,
        activity_type="Resolution",
        description=description
    )
    
    return ticket.name

@frappe.whitelist()
def log_ticket_reopening(ticket_name, reason=None):
    """Log ticket reopening with reason"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    ticket = frappe.get_doc("CRM Ticket", ticket_name)
    old_status = ticket.status
    
    # Reopen ticket
    ticket.status = "Open"
    ticket.resolved = 0
    ticket.resolved_on = None
    ticket.save(ignore_permissions=True)
    
    # Add reopening activity
    description = f"Ticket reopened: Status changed from {old_status} to Open"
    if reason:
        description += f"\n\nReason: {reason}"
    
    add_ticket_activity(
        ticket=ticket.name,
        activity_type="Reopening",
        description=description
    )
    
    return ticket.name

@frappe.whitelist()
def log_sla_breach(ticket_name, breach_type, expected_time, actual_time):
    """Log SLA breach events"""
    if not ticket_name or not breach_type:
        frappe.throw(_("Ticket name and breach type are required"))
    
    description = f"SLA Breach Detected: {breach_type}"
    if expected_time and actual_time:
        description += f"\nExpected: {expected_time}"
        description += f"\nActual: {actual_time}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="SLA Breach",
        description=description
    )

@frappe.whitelist()
def log_customer_response(ticket_name, response_method="Email", response_content=None):
    """Log customer responses to ticket"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    description = f"Customer responded via {response_method}"
    if response_content:
        description += f"\n\nResponse: {response_content[:200]}{'...' if len(response_content) > 200 else ''}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="Customer Response",
        description=description
    )

@frappe.whitelist()
def log_internal_note(ticket_name, note_content, is_private=True):
    """Log internal notes for ticket"""
    if not ticket_name or not note_content:
        frappe.throw(_("Ticket name and note content are required"))
    
    description = f"Internal Note Added"
    if is_private:
        description += " (Private)"
    description += f"\n\n{note_content}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="Internal Note",
        description=description
    )

@frappe.whitelist()
def log_department_transfer(ticket_name, from_department, to_department, reason=None):
    """Log department transfers"""
    if not ticket_name or not to_department:
        frappe.throw(_("Ticket name and target department are required"))
    
    description = f"Ticket transferred: {from_department or 'Unassigned'} → {to_department}"
    if reason:
        description += f"\n\nReason: {reason}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="Department Transfer",
        description=description
    )

@frappe.whitelist()
def log_customer_feedback(ticket_name, rating=None, feedback_text=None):
    """Log customer feedback for closed tickets"""
    if not ticket_name:
        frappe.throw(_("Ticket name is required"))
    
    description = "Customer Feedback Received"
    if rating:
        description += f"\nRating: {rating}/5 stars"
    if feedback_text:
        description += f"\nFeedback: {feedback_text}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="Customer Feedback",
        description=description
    )

@frappe.whitelist()
def log_follow_up_scheduled(ticket_name, follow_up_date, follow_up_notes=None):
    """Log when follow-ups are scheduled"""
    if not ticket_name or not follow_up_date:
        frappe.throw(_("Ticket name and follow-up date are required"))
    
    description = f"Follow-up scheduled for {follow_up_date}"
    if follow_up_notes:
        description += f"\n\nNotes: {follow_up_notes}"
    
    add_ticket_activity(
        ticket=ticket_name,
        activity_type="Follow-up Scheduled",
        description=description
    )

@frappe.whitelist()
def auto_log_ticket_events():
    """Background job to auto-log certain ticket events"""
    # Check for SLA breaches
    overdue_tickets = frappe.get_list(
        "CRM Ticket",
        filters={
            "status": ["not in", ["Closed", "Resolved"]],
            "response_by": ["<", now()],
            "sla_breach_logged": 0
        },
        fields=["name", "response_by", "sla"],
        limit=50
    )
    
    for ticket in overdue_tickets:
        try:
            log_sla_breach(
                ticket.name,
                "Response Time",
                ticket.response_by,
                now()
            )
            # Mark as logged to avoid duplicate logs
            frappe.db.set_value("CRM Ticket", ticket.name, "sla_breach_logged", 1)
        except Exception as e:
            frappe.log_error(f"Error logging SLA breach for {ticket.name}: {str(e)}")
    
    return len(overdue_tickets)

# Hooks for automatic event logging
def on_ticket_update(doc, method):
    """Hook that runs when a ticket is updated to auto-log changes"""
    if method == "on_update":
        # Get the previous document state
        old_doc = doc.get_doc_before_save()
        if not old_doc:
            return
        
        # Track important field changes
        important_fields = {
            'status': 'Status Update',
            'assigned_to': 'Assignment', 
            'priority': 'Priority Update',
            'department': 'Department Transfer',
            'escalated': 'Escalation',
            'sla': 'SLA Update'
        }
        
        for field, activity_type in important_fields.items():
            old_value = old_doc.get(field)
            new_value = doc.get(field)
            
            if old_value != new_value:
                if field == 'assigned_to':
                    description = f"Assigned from {old_value or 'Unassigned'} to {new_value or 'Unassigned'}"
                elif field == 'department':
                    description = f"Department changed from {old_value or 'None'} to {new_value or 'None'}"
                elif field == 'escalated' and new_value:
                    description = f"Ticket escalated"
                else:
                    description = f"{field.replace('_', ' ').title()} changed from {old_value or 'None'} to {new_value or 'None'}"
                
                try:
                    add_ticket_activity(
                        ticket=doc.name,
                        activity_type=activity_type,
                        description=description
                    )
                except Exception as e:
                    frappe.log_error(f"Error adding activity for {doc.name}: {str(e)}")

def on_ticket_creation(doc, method):
    """Hook that runs when a ticket is created"""
    if method == "after_insert":
        # Log ticket creation with source information
        source = doc.get("creation_source", "Manual")
        description = f"Ticket created via {source}"
        
        if hasattr(doc, 'call_log') and doc.call_log:
            description += f" from call log {doc.call_log}"
        
        try:
            add_ticket_activity(
                ticket=doc.name,
                activity_type="Creation",
                description=description
            )
        except Exception as e:
            frappe.log_error(f"Error logging ticket creation for {doc.name}: {str(e)}")

@frappe.whitelist()
def associate_call_log_to_recent_ticket(call_log_name, customer_mobile=None, customer_email=None):
    """Associate a call log to the most recent open ticket for the same customer"""
    if not call_log_name:
        frappe.throw(_("Call log name is required"))
    
    call_log = frappe.get_doc("CRM Call Log", call_log_name)
    
    # Determine customer contact info
    if not customer_mobile and not customer_email:
        # Extract from call log
        customer_mobile = call_log.customer if call_log.customer else None
        customer_email = call_log.email if hasattr(call_log, 'email') and call_log.email else None
    
    if not customer_mobile and not customer_email:
        # No customer info available, can't associate
        return None
    
    # Find the most recent open ticket for this customer
    recent_ticket = find_most_recent_open_ticket(customer_mobile, customer_email)
    
    if recent_ticket:
        # Update call log to link to this ticket
        frappe.db.set_value(
            "CRM Call Log",
            call_log_name,
            {
                "ticket": recent_ticket.name,
                "reference_doctype": "CRM Ticket", 
                "reference_docname": recent_ticket.name
            }
        )
        
        # Add activity to ticket
        add_ticket_activity(
            ticket=recent_ticket.name,
            activity_type="Call Log",
            description=f"Call log {call_log_name} associated with ticket during lifecycle"
        )
        
        return recent_ticket.name
    
    return None

@frappe.whitelist()
def find_most_recent_open_ticket(mobile_no=None, email=None):
    """Find the most recent open ticket for a customer"""
    if not mobile_no and not email:
        return None
    
    # Build filters
    filters = []
    if mobile_no and email:
        filters = [
            ["mobile_no", "=", mobile_no],
            ["email", "=", email]
        ]
    elif mobile_no:
        filters = {"mobile_no": mobile_no}
    elif email:
        filters = {"email": email}
    
    # Add status filter for open tickets
    open_statuses = ["New", "Open", "In Progress", "Pending Customer", "Escalated"]
    if isinstance(filters, list):
        # Handle OR conditions - need to search both mobile and email separately
        tickets_mobile = frappe.get_list(
            "CRM Ticket",
            filters=[
                ["mobile_no", "=", mobile_no],
                ["status", "in", open_statuses]
            ],
            fields=["name", "creation", "status"],
            order_by="creation desc",
            limit=1
        ) if mobile_no else []
        
        tickets_email = frappe.get_list(
            "CRM Ticket", 
            filters=[
                ["email", "=", email],
                ["status", "in", open_statuses]
            ],
            fields=["name", "creation", "status"],
            order_by="creation desc",
            limit=1
        ) if email else []
        
        # Get the most recent of both
        all_tickets = tickets_mobile + tickets_email
        if all_tickets:
            # Return the most recent ticket
            most_recent = max(all_tickets, key=lambda x: x.creation)
            return frappe.get_doc("CRM Ticket", most_recent.name)
    else:
        filters["status"] = ["in", open_statuses]
        tickets = frappe.get_list(
            "CRM Ticket",
            filters=filters,
            fields=["name", "creation", "status"],
            order_by="creation desc",
            limit=1
        )
        
        if tickets:
            return frappe.get_doc("CRM Ticket", tickets[0].name)
    
    return None

@frappe.whitelist()
def auto_associate_call_logs():
    """Background job to auto-associate unlinked call logs to recent tickets"""
    # Get call logs that are not linked to any ticket
    unlinked_calls = frappe.get_list(
        "CRM Call Log",
        filters={
            "ticket": ["is", "not set"],
            "reference_doctype": ["!=", "CRM Ticket"]
        },
        fields=["name", "customer", "creation"],
        order_by="creation desc",
        limit=100  # Process in batches
    )
    
    associated_count = 0
    
    for call in unlinked_calls:
        if call.customer:
            result = associate_call_log_to_recent_ticket(call.name, call.customer)
            if result:
                associated_count += 1
    
    frappe.msgprint(_("Auto-associated {0} call logs to recent tickets").format(associated_count))
    return associated_count

@frappe.whitelist()  
def update_call_log_associations_for_customer(mobile_no=None, email=None):
    """Update all call log associations for a specific customer based on ticket lifecycle"""
    if not mobile_no and not email:
        frappe.throw(_("Mobile number or email is required"))
    
    # Get all tickets for this customer in chronological order
    customer_tickets = get_customer_tickets_chronological(mobile_no, email)
    
    if not customer_tickets:
        return {"message": "No tickets found for customer", "updated_calls": 0}
    
    # Get all call logs for this customer
    call_filters = []
    if mobile_no and email:
        call_filters = [
            ["customer", "=", mobile_no],
            ["customer", "=", email]
        ]
    elif mobile_no:
        call_filters = {"customer": mobile_no}
    elif email:
        call_filters = {"customer": email}
    
    customer_calls = frappe.get_list(
        "CRM Call Log",
        filters=call_filters,
        fields=["name", "creation"],
        order_by="creation asc"
    )
    
    updated_calls = 0
    
    # For each call log, determine which ticket it should belong to
    for call in customer_calls:
        correct_ticket = determine_ticket_for_call(call.creation, customer_tickets)
        
        if correct_ticket:
            # Update the call log association
            current_ticket = frappe.db.get_value("CRM Call Log", call.name, "ticket")
            
            if current_ticket != correct_ticket.name:
                frappe.db.set_value(
                    "CRM Call Log",
                    call.name,
                    {
                        "ticket": correct_ticket.name,
                        "reference_doctype": "CRM Ticket",
                        "reference_docname": correct_ticket.name
                    }
                )
                updated_calls += 1
    
    return {
        "message": f"Updated {updated_calls} call log associations",
        "updated_calls": updated_calls
    }

def get_customer_tickets_chronological(mobile_no=None, email=None):
    """Get all tickets for a customer in chronological order"""
    filters = []
    if mobile_no and email:
        # Handle OR condition for both mobile and email
        tickets_mobile = frappe.get_list(
            "CRM Ticket",
            filters={"mobile_no": mobile_no},
            fields=["name", "creation"],
            order_by="creation asc"
        )
        tickets_email = frappe.get_list(
            "CRM Ticket",
            filters={"email": email},
            fields=["name", "creation"],
            order_by="creation asc"
        )
        # Combine and sort
        all_tickets = tickets_mobile + tickets_email
        # Remove duplicates and sort
        unique_tickets = list({t.name: t for t in all_tickets}.values())
        return sorted(unique_tickets, key=lambda x: x.creation)
    elif mobile_no:
        filters = {"mobile_no": mobile_no}
    elif email:
        filters = {"email": email}
    
    return frappe.get_list(
        "CRM Ticket",
        filters=filters,
        fields=["name", "creation"],
        order_by="creation asc"
    )

def determine_ticket_for_call(call_creation_time, customer_tickets):
    """Determine which ticket a call should be associated with based on lifecycle logic"""
    if not customer_tickets:
        return None
    
    # Find the ticket that was active when this call was made
    # Logic: call belongs to the most recent ticket created before the call
    # unless there's a newer ticket, in which case it belongs to that newer ticket's lifecycle
    
    active_ticket = None
    
    for ticket in customer_tickets:
        # If call was made after this ticket was created
        if call_creation_time >= ticket.creation:
            active_ticket = ticket
        else:
            # We've found a ticket created after the call
            # The call belongs to the previous ticket's lifecycle
            break
    
    return frappe.get_doc("CRM Ticket", active_ticket.name) if active_ticket else None 