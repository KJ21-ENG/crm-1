import json

import frappe
from bs4 import BeautifulSoup
from frappe import _
from frappe.desk.form.load import get_docinfo
from frappe.query_builder import JoinType

from crm.fcrm.doctype.crm_call_log.crm_call_log import parse_call_log


def emit_activity_update(doctype, docname):
	"""Emit socket event for activity updates"""
	frappe.publish_realtime(
		"activity_update",
		{
			"reference_doctype": doctype,
			"reference_name": docname,
		},
	)


@frappe.whitelist()
def get_activities(name, limit=20, offset=0):
	limit = int(limit)
	offset = int(offset)
	if frappe.db.exists("CRM Deal", name):
		return get_deal_activities(name, limit, offset)
	elif frappe.db.exists("CRM Lead", name):
		return get_lead_activities(name, limit, offset)
	elif frappe.db.exists("CRM Ticket", name):
		return get_ticket_activities(name, limit, offset)
	else:
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)


def get_deal_activities(name, limit=20, offset=0):
	get_docinfo("", "CRM Deal", name)
	docinfo = frappe.response["docinfo"]
	deal_meta = frappe.get_meta("CRM Deal")
	deal_fields = {
		field.fieldname: {"label": field.label, "options": field.options} for field in deal_meta.fields
	}
	avoid_fields = [
		"lead",
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
	]

	doc = frappe.db.get_values("CRM Deal", name, ["creation", "owner", "lead"])[0]
	lead = doc[2]

	activities = []
	calls = []
	notes = []
	tasks = []
	attachments = []
	creation_text = "created this deal"

	if lead:
		activities, calls, notes, tasks, attachments = get_lead_activities(lead, limit, offset)
		creation_text = "converted the lead to this deal"

	activities.append(
		{
			"activity_type": "creation",
			"creation": doc[0],
			"owner": doc[1],
			"data": creation_text,
			"is_lead": False,
		}
	)

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		# Prefer a status change if multiple fields changed in the same version
		changes = data.get("changed") or []
		change = None
		if changes:
			for ch in changes:
				if ch and ch[0] == 'status':
					change = ch
					break
			if not change:
				change = changes[0]

		if change:
			field = deal_fields.get(change[0], None)

			if not field or change[0] in avoid_fields or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

			# If this was a status change, include extra fields from the lead record
			if change[0] == 'status':
				try:
					lead_vals = frappe.db.get_value('CRM Lead', name, ['client_id', 'rejection_reason'], as_dict=True)
					if lead_vals:
						if lead_vals.get('client_id'):
							data['client_id'] = lead_vals.get('client_id')
						if lead_vals.get('rejection_reason'):
							data['rejection_reason'] = lead_vals.get('rejection_reason')
				except Exception:
					# ignore errors; extra data is optional
					pass

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_lead": False,
		}
		activities.append(activity)

	# Pagination
	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = activities[offset:offset+limit]

	for comment in docinfo.comments:
		activity = {
			"name": comment.name,
			"activity_type": "comment",
			"creation": comment.creation,
			"owner": comment.owner,
			"content": comment.content,
			"attachments": get_attachments("Comment", comment.name),
			"is_lead": False,
		}
		activities.append(activity)
		emit_activity_update("CRM Deal", name)

	for communication in docinfo.communications + docinfo.automated_messages:
		activity = {
			"activity_type": "communication",
			"communication_type": communication.communication_type,
			"communication_date": communication.communication_date or communication.creation,
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"attachments": get_attachments("Communication", communication.name),
				"read_by_recipient": communication.read_by_recipient,
				"delivery_status": communication.delivery_status,
			},
			"is_lead": False,
		}
		activities.append(activity)
		emit_activity_update("CRM Deal", name)

	for attachment_log in docinfo.attachment_logs:
		activity = {
			"name": attachment_log.name,
			"activity_type": "attachment_log",
			"creation": attachment_log.creation,
			"owner": attachment_log.owner,
			"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
			"is_lead": False,
		}
		activities.append(activity)
		emit_activity_update("CRM Deal", name)

	calls = calls + get_linked_calls(name).get("calls", [])
	notes = notes + get_linked_notes(name) + get_linked_calls(name).get("notes", [])
	tasks = tasks + get_linked_tasks(name) + get_linked_calls(name).get("tasks", [])
	attachments = attachments + get_attachments("CRM Deal", name)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities, calls, notes, tasks, attachments


def get_lead_activities(name, limit=20, offset=0):
	get_docinfo("", "CRM Lead", name)
	docinfo = frappe.response["docinfo"]
	lead_meta = frappe.get_meta("CRM Lead")
	lead_fields = {
		field.fieldname: {"label": field.label, "options": field.options} for field in lead_meta.fields
	}
	avoid_fields = [
		"converted",
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
		"customer_id",
	]

	doc = frappe.db.get_values("CRM Lead", name, ["creation", "owner"])[0]
	activities = [
		{
			"activity_type": "creation",
			"creation": doc[0],
			"owner": doc[1],
			"data": "created this lead",
			"is_lead": True,
		}
	]

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		# Prefer a status change if multiple fields changed in the same version
		changes = data.get("changed") or []
		change = None
		if changes:
			for ch in changes:
				if ch and ch[0] == 'status':
					change = ch
					break
			if not change:
				change = changes[0]

		if change:
			field = lead_fields.get(change[0], None)

			if not field or change[0] in avoid_fields or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_lead": True,
			"options": field_option,
		}
		activities.append(activity)

	for comment in docinfo.comments:
		activity = {
			"name": comment.name,
			"activity_type": "comment",
			"creation": comment.creation,
			"owner": comment.owner,
			"content": comment.content,
			"attachments": get_attachments("Comment", comment.name),
			"is_lead": True,
		}
		activities.append(activity)

	for communication in docinfo.communications + docinfo.automated_messages:
		activity = {
			"activity_type": "communication",
			"communication_type": communication.communication_type,
			"communication_date": communication.communication_date or communication.creation,
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"attachments": get_attachments("Communication", communication.name),
				"read_by_recipient": communication.read_by_recipient,
				"delivery_status": communication.delivery_status,
			},
			"is_lead": True,
		}
		activities.append(activity)

	for attachment_log in docinfo.attachment_logs:
		activity = {
			"name": attachment_log.name,
			"activity_type": "attachment_log",
			"creation": attachment_log.creation,
			"owner": attachment_log.owner,
			"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
			"is_lead": True,
		}
		activities.append(activity)

	# Combine lifecycle calls (by CRM Customer from customer_id) with direct links
	lifecycle_calls = []
	try:
		lead_doc = frappe.get_doc("CRM Lead", name)
		customer_phone = None
		customer_email = None
		if getattr(lead_doc, "customer_id", None):
			cust = frappe.db.get_value(
				"CRM Customer",
				lead_doc.customer_id,
				["mobile_no", "email"],
				as_dict=True,
			)
			if cust:
				customer_phone = cust.get("mobile_no")
				customer_email = cust.get("email")
		# Fallback to legacy fields if present
		customer_phone = customer_phone or getattr(lead_doc, "mobile_no", None)
		customer_email = customer_email or getattr(lead_doc, "email", None)

		lifecycle_calls = get_lead_lifecycle_calls(
			name,
			lead_doc.creation,
			lead_doc.get("customer_id"),
			customer_phone,
			customer_email,
		)
	except Exception as e:
		frappe.logger().warning(f"Lead lifecycle calls error for {name}: {e}")

	_linked = get_linked_calls(name)
	direct_calls = _linked.get("calls", [])
	# Combine and deduplicate
	all_call_data = (lifecycle_calls or []) + (direct_calls or [])
	unique_call_data = list({call["name"]: call for call in all_call_data}.values())
	calls = [parse_call_log(call) for call in unique_call_data]

	notes = get_linked_notes(name) + _linked.get("notes", [])
	tasks = get_linked_tasks(name) + _linked.get("tasks", [])
	attachments = get_attachments("CRM Lead", name)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = activities[offset:offset+limit]

	return activities, calls, notes, tasks, attachments


def get_ticket_activities(name, limit=20, offset=0):
	"""Get comprehensive ticket activities with call log lifecycle logic"""
	get_docinfo("", "CRM Ticket", name)
	docinfo = frappe.response["docinfo"]
	
	ticket_meta = frappe.get_meta("CRM Ticket")
	ticket_fields = {
		field.fieldname: {"label": field.label, "options": field.options} for field in ticket_meta.fields
	}
	avoid_fields = [
		"response_by",
		"sla_creation",
		"sla",
		"first_response_time",
		"first_responded_on",
		"customer_id",
		"assigned_to",
	]

	# Get ticket basic info
	ticket_doc = frappe.get_doc("CRM Ticket", name)
	doc = frappe.db.get_values("CRM Ticket", name, ["creation", "owner", "mobile_no", "email"])[0]
	creation_time, owner, mobile_no, email = doc

	activities = []
	calls = []
	notes = []
	tasks = []
	attachments = []

	# Add ticket creation activity
	creation_text = "created this ticket"
	
	activities.append(
		{
			"activity_type": "creation",
			"creation": creation_time,
			"owner": owner,
			"data": creation_text,
			"is_ticket": True,
		}
	)

	# Note: Call logs are handled separately in the calls array to avoid duplication
	# The lifecycle logic is implemented in get_ticket_lifecycle_calls() and processed as calls

	# Add ticket version activities (field changes, status updates, etc.)
	if docinfo.versions:
		docinfo.versions.reverse()

		for version in docinfo.versions:
			data = json.loads(version.data)
			if not data.get("changed"):
				continue

			# Prefer a status change if multiple fields changed in the same version
			changes = data.get("changed") or []
			change = None
			if changes:
				for ch in changes:
					if ch and ch[0] == 'status':
						change = ch
						break
				if not change:
					change = changes[0]

			if change:
				field = ticket_fields.get(change[0], None)

				# Skip call log related changes and other irrelevant fields
				if (not field or 
					change[0] in avoid_fields or 
					(not change[1] and not change[2]) or
					change[0] in ["call_log", "employee", "customer", "recording_url"]):
					continue

				field_label = field.get("label") or change[0]
				field_option = field.get("options") or None

				activity_type = "changed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"old_value": change[1],
					"value": change[2],
				}

				if not change[1] and change[2]:
					activity_type = "added"
					data = {
						"field": change[0],
						"field_label": field_label,
						"value": change[2],
					}
				elif change[1] and not change[2]:
					activity_type = "removed"
					data = {
						"field": change[0],
						"field_label": field_label,
						"value": change[1],
					}

			activity = {
				"activity_type": activity_type,
				"creation": version.creation,
				"owner": version.owner,
				"data": data,
				"is_ticket": True,
				"options": field_option,
			}
			activities.append(activity)

	# Pagination
	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = activities[offset:offset+limit]

	# Add comments (filter out auto-generated and irrelevant comments)
	if docinfo.comments:
		for comment in docinfo.comments:
			# Skip auto-generated comments and comments without meaningful content
			if (comment.comment_type in ["Deleted", "Like", "Assignment", "Updated"] or 
				not comment.content or 
				"has made a call" in (comment.content or "") or
				"has reached out" in (comment.content or "")):
				continue
				
			# Determine activity type based on content
			activity_type = "comment"
			if "📱 WhatsApp Support" in comment.content:
				activity_type = "whatsapp_support"
				
			activity = {
				"name": comment.name,
				"activity_type": activity_type,
				"creation": comment.creation,
				"owner": comment.owner,
				"content": comment.content,
				"attachments": get_attachments("Comment", comment.name),
				"is_ticket": True,
			}
			activities.append(activity)
			emit_activity_update("CRM Ticket", name)

	# Add communications (emails)
	if docinfo.communications:
		for communication in docinfo.communications + docinfo.automated_messages:
			activity = {
				"activity_type": "communication",
				"communication_type": communication.communication_type,
				"communication_date": communication.communication_date or communication.creation,
				"creation": communication.creation,
				"data": {
					"subject": communication.subject,
					"content": communication.content,
					"sender_full_name": communication.sender_full_name,
					"sender": communication.sender,
					"recipients": communication.recipients,
					"cc": communication.cc,
					"bcc": communication.bcc,
					"attachments": get_attachments("Communication", communication.name),
					"read_by_recipient": communication.read_by_recipient,
					"delivery_status": communication.delivery_status,
				},
				"is_ticket": True,
			}
			activities.append(activity)
			emit_activity_update("CRM Ticket", name)

	# Add attachment logs
	if docinfo.attachment_logs:
		for attachment_log in docinfo.attachment_logs:
			activity = {
				"name": attachment_log.name,
				"activity_type": "attachment_log",
				"creation": attachment_log.creation,
				"owner": attachment_log.owner,
				"data": parse_attachment_log(attachment_log.content, attachment_log.comment_type),
				"is_ticket": True,
			}
			activities.append(activity)
			emit_activity_update("CRM Ticket", name)

	# Get linked items with proper lifecycle logic
	# Get calls using the lifecycle logic to avoid duplicates
	# Prefer CRM Customer contact info via customer_id; fallback to legacy fields
	customer_phone = ticket_doc.get("mobile_no")
	customer_email = ticket_doc.get("email")
	if ticket_doc.get("customer_id"):
		cust = frappe.db.get_value(
			"CRM Customer",
			ticket_doc.get("customer_id"),
			["mobile_no", "email"],
			as_dict=True,
		)
		if cust:
			customer_phone = cust.get("mobile_no") or customer_phone
			customer_email = cust.get("email") or customer_email

	lifecycle_calls = get_ticket_lifecycle_calls(
		name,
		customer_phone,
		customer_email,
		ticket_doc.creation,
	)
	
	# Also get any calls directly linked to the ticket via reference fields
	direct_ticket_calls = frappe.db.get_all(
		"CRM Call Log",
		filters={
			"reference_doctype": "CRM Ticket",
			"reference_docname": name
		},
		fields=[
			"name", "caller", "receiver", "from", "to", "duration",
			"start_time", "end_time", "status", "type", "recording_url", 
			"creation", "note", "customer_name", "employee", "customer"
		],
	)
	
	# Also include dynamic linked calls (via Dynamic Link table)
	linked_calls = get_linked_calls(name).get("calls", [])
	# Combine lifecycle, direct, and dynamic calls, then deduplicate
	all_call_data = lifecycle_calls + direct_ticket_calls + linked_calls
	unique_call_data = list({call["name"]: call for call in all_call_data}.values())
	calls = [parse_call_log(call) for call in unique_call_data]
	
	notes = get_linked_notes(name)
	tasks = get_linked_tasks(name)
	attachments = get_attachments("CRM Ticket", name)

	# Add custom ticket activities (escalations, assignments, etc.)
	custom_activities = get_custom_ticket_activities(name)
	activities.extend(custom_activities)

	# Sort all activities by creation time (oldest first for chronological order)
	activities.sort(key=lambda x: x["creation"], reverse=False)
	activities = handle_multiple_versions(activities)

	# Return activities as 'versions' to match the expected format in Activities.vue
	# The transform function expects [versions, calls, notes, tasks, attachments]
	return activities, calls, notes, tasks, attachments


def get_ticket_lifecycle_calls(ticket_name, mobile_no, email, ticket_creation_time):
	"""Get call logs that belong to this ticket's lifecycle based on the crucial logic"""
	if not mobile_no and not email:
		return []

	# Build proper SQL conditions for call logs matching customer phone/email
	# Use OR condition to check both 'from' and 'to' fields for the customer contact
	where_conditions = []
	values = []
	
	if mobile_no:
		where_conditions.append("(`from` = %s OR `to` = %s)")
		values.extend([mobile_no, mobile_no])
	
	if email:
		# Email might be in customer field or customer_name field
		if where_conditions:
			where_conditions.append("OR (customer = %s OR customer_name LIKE %s)")
		else:
			where_conditions.append("(customer = %s OR customer_name LIKE %s)")
		values.extend([email, f"%{email}%"])
	
	# Add time filter to only get calls AFTER ticket creation
	where_conditions.append("AND creation >= %s")
	values.append(ticket_creation_time)

	# Build the final where clause and respect explicit linking: if a call log
	# is explicitly linked (reference_doctype/docname) to a different document,
	# exclude it from lifecycle results. Allow unlinked or linked to this ticket.
	where_clause = " ".join(where_conditions)
	where_clause += " AND (reference_docname IS NULL OR reference_doctype IS NULL OR (reference_doctype = 'CRM Ticket' AND reference_docname = %s))"
	
	# Get calls using direct SQL to handle complex OR conditions properly
	# Filter out dummy calls that have no duration and no status (these are auto-generated entries)
	customer_calls = frappe.db.sql(f"""
		SELECT name, caller, receiver, `from`, `to`, duration, 
			   start_time, end_time, status, type, recording_url, 
			   creation, note, customer_name, employee, customer
		FROM `tabCRM Call Log`
        WHERE {where_clause}
		AND (duration IS NOT NULL AND duration > 0 OR status IS NOT NULL AND status != '')
		ORDER BY start_time ASC, creation ASC
	""", values + [ticket_name], as_dict=True)

	# Filter calls to only include those within this ticket's lifecycle
	# Lifecycle = from ticket creation until a newer ticket is created for same customer
	next_ticket_creation = None
	
	# Find if there's a newer ticket for the same customer
	next_ticket_filters = []
	if mobile_no and email:
		next_ticket_filters = [
			["mobile_no", "=", mobile_no],
			["email", "=", email]
		]
	elif mobile_no:
		next_ticket_filters = {"mobile_no": mobile_no}
	elif email:
		next_ticket_filters = {"email": email}
	
	# Add time and name filters to get newer tickets
	if next_ticket_filters:
		if isinstance(next_ticket_filters, list):
			# Handle OR conditions for mobile_no and email
			newer_tickets_mobile = frappe.get_list(
				"CRM Ticket",
				filters=[
					["mobile_no", "=", mobile_no],
					["creation", ">", ticket_creation_time],
					["name", "!=", ticket_name]
				],
				fields=["creation"],
				order_by="creation asc",
				limit=1
			)
			newer_tickets_email = frappe.get_list(
				"CRM Ticket", 
				filters=[
					["email", "=", email],
					["creation", ">", ticket_creation_time],
					["name", "!=", ticket_name]
				],
				fields=["creation"],
				order_by="creation asc", 
				limit=1
			) if email else []
			
			# Get the earliest next ticket
			all_newer_tickets = newer_tickets_mobile + newer_tickets_email
			if all_newer_tickets:
				next_ticket_creation = min([t.creation for t in all_newer_tickets])
		else:
			next_ticket_filters["creation"] = [">", ticket_creation_time]
			next_ticket_filters["name"] = ["!=", ticket_name]
			
			newer_tickets = frappe.get_list(
				"CRM Ticket",
				filters=next_ticket_filters,
				fields=["creation"],
				order_by="creation asc",
				limit=1
			)
			
			if newer_tickets:
				next_ticket_creation = newer_tickets[0].creation

	# Filter call logs to be within this ticket's lifecycle
	lifecycle_calls = []
	for call in customer_calls:
		call_time = call.creation
		
		# Include calls after ticket creation
		if call_time >= ticket_creation_time:
			# If there's a newer ticket, only include calls before that ticket's creation
			if next_ticket_creation is None or call_time < next_ticket_creation:
				lifecycle_calls.append(call)

	return lifecycle_calls


def get_lead_lifecycle_calls(lead_name, lead_creation_time, customer_id=None, mobile_no=None, email=None):
    """Get call logs that belong to this lead's lifecycle.

    Logic: use CRM Customer from customer_id when available to match phone/email; otherwise
    fallback to phone/email on the lead. Include calls on/after lead creation until a newer
    lead exists for the same customer, and exclude empty/dummy calls.
    """
    # If there's neither a customer ref nor contact data, nothing to infer
    if not customer_id and not mobile_no and not email:
        return []

    where_conditions = []
    values = []

    if mobile_no:
        where_conditions.append("(`from` = %s OR `to` = %s)")
        values.extend([mobile_no, mobile_no])

    if email:
        if where_conditions:
            where_conditions.append("OR (customer = %s OR customer_name LIKE %s)")
        else:
            where_conditions.append("(customer = %s OR customer_name LIKE %s)")
        values.extend([email, f"%{email}%"])

    # At minimum, require a condition; else return
    if not where_conditions:
        return []

    # Start from lead creation
    where_conditions.append("AND creation >= %s")
    values.append(lead_creation_time)

    where_clause = " ".join(where_conditions)
    where_clause += " AND (reference_docname IS NULL OR reference_doctype IS NULL OR (reference_doctype = 'CRM Lead' AND reference_docname = %s))"

    customer_calls = frappe.db.sql(
        f"""
        SELECT name, caller, receiver, `from`, `to`, duration,
               start_time, end_time, status, type, recording_url,
               creation, note, customer_name, employee, customer
        FROM `tabCRM Call Log`
        WHERE {where_clause}
        AND (duration IS NOT NULL AND duration > 0 OR status IS NOT NULL AND status != '')
        ORDER BY start_time ASC, creation ASC
        """,
        values + [lead_name],
        as_dict=True,
    )

    # Define end boundary: next lead for same customer
    next_lead_creation = None
    if customer_id:
        newer_leads = frappe.get_list(
            "CRM Lead",
            filters={
                "customer_id": customer_id,
                "creation": [">", lead_creation_time],
                "name": ["!=", lead_name],
            },
            fields=["creation"],
            order_by="creation asc",
            limit=1,
        )
        if newer_leads:
            next_lead_creation = newer_leads[0].creation

    lifecycle_calls = []
    for call in customer_calls:
        call_time = call.creation
        if call_time >= lead_creation_time and (next_lead_creation is None or call_time < next_lead_creation):
            lifecycle_calls.append(call)

    return lifecycle_calls


def get_ticket_calls(name):
	"""Get calls directly linked to this ticket"""
	# Add filter to exclude dummy calls with no duration and no status
	call_filters = {
		"reference_docname": name, 
		"reference_doctype": "CRM Ticket"
	}
	
	calls = frappe.db.sql("""
		SELECT name, caller, receiver, `from`, `to`, duration,
			   start_time, end_time, status, type, recording_url,
			   creation, note, customer_name, employee, customer
		FROM `tabCRM Call Log`
		WHERE reference_docname = %s AND reference_doctype = %s
		AND (duration IS NOT NULL AND duration > 0 OR status IS NOT NULL AND status != '')
		ORDER BY start_time ASC, creation ASC
	""", [name, "CRM Ticket"], as_dict=True)

	# Also get calls linked via reference fields to this ticket
	ticket_calls = frappe.db.sql("""
		SELECT name, caller, receiver, `from`, `to`, duration,
			   start_time, end_time, status, type, recording_url, 
			   creation, note, customer_name, employee, customer
		FROM `tabCRM Call Log`
		WHERE reference_doctype = %s AND reference_docname = %s
		AND (duration IS NOT NULL AND duration > 0 OR status IS NOT NULL AND status != '')
		ORDER BY start_time ASC, creation ASC
	""", ["CRM Ticket", name], as_dict=True)

	# Combine and deduplicate
	all_calls = calls + ticket_calls
	unique_calls = list({call["name"]: call for call in all_calls}.values())

	return [parse_call_log(call) for call in unique_calls] if unique_calls else []


def get_custom_ticket_activities(ticket_name):
	"""Get custom ticket activities like escalations, assignments, etc."""
	activities = []
	
	# Get WhatsApp activities from Comment DocType
	whatsapp_comments = frappe.get_list(
		"Comment",
		filters={
			"reference_doctype": "CRM Ticket", 
			"reference_name": ticket_name,
			"content": ["like", "%📱 WhatsApp Support%"]
		},
		fields=["name", "content", "creation", "owner", "comment_email"],
		order_by="creation desc",
		ignore_permissions=True
	)
			
	for comment in whatsapp_comments:
		# Parse the content to extract details
		content_lines = comment.content.split("\n")
		data = {
			"title": "WhatsApp Support Activity",
			"status": "Success" if "✅" in comment.content else "Failed",
			"support_page": next((line.split(": ")[1] for line in content_lines if "*Support Page*:" in line), ""),
			"customer_phone": next((line.split(": ")[1] for line in content_lines if "*Customer Phone*:" in line), ""),
			"sent_by": comment.comment_email,
			"error": next((line.split(": ")[1] for line in content_lines if "*Error*:" in line), None)
		}
		
		activities.append({
			"activity_type": "whatsapp_support",
			"creation": comment.creation,
			"owner": comment.owner,
			"data": data,
			"is_ticket": True,
		})
	
	return activities


def get_attachments(doctype, name):
	attachments = frappe.db.get_all(
		"File",
		filters={"attached_to_doctype": doctype, "attached_to_name": name},
		fields=[
			"name",
			"file_name",
			"file_type",
			"file_url",
			"file_size",
			"is_private",
			"modified",
			"creation",
			"owner",
		],
	) or []
	
	if attachments:
		emit_activity_update(doctype, name)
	
	return attachments


def handle_multiple_versions(versions):
	activities = []
	grouped_versions = []
	old_version = None
	for version in versions:
		is_version = version["activity_type"] in ["changed", "added", "removed"]
		if not is_version:
			activities.append(version)
		if not old_version:
			old_version = version
			if is_version:
				grouped_versions.append(version)
			continue
		if is_version and old_version.get("owner") and version["owner"] == old_version["owner"]:
			grouped_versions.append(version)
		else:
			if grouped_versions:
				activities.append(parse_grouped_versions(grouped_versions))
			grouped_versions = []
			if is_version:
				grouped_versions.append(version)
		old_version = version
		if version == versions[-1] and grouped_versions:
			activities.append(parse_grouped_versions(grouped_versions))

	return activities


def parse_grouped_versions(versions):
	version = versions[0]
	if len(versions) == 1:
		return version
	other_versions = versions[1:]
	version["other_versions"] = other_versions
	return version


def get_linked_calls(name):
	calls = frappe.db.get_all(
		"CRM Call Log",
		filters={"reference_docname": name},
		fields=[
			"name",
			"caller",
			"receiver",
			"from",
			"to",
			"duration",
			"start_time",
			"end_time",
			"status",
			"type",
			"recording_url",
			"creation",
			"note",
			"customer_name",
			"employee",
			"customer"
		],
	)

	linked_calls = frappe.db.get_all(
		"Dynamic Link", filters={"link_name": name, "parenttype": "CRM Call Log"}, pluck="parent"
	)

	notes = []
	tasks = []

	if linked_calls:
		CallLog = frappe.qb.DocType("CRM Call Log")
		Link = frappe.qb.DocType("Dynamic Link")
		query = (
			frappe.qb.from_(CallLog)
			.select(
				CallLog.name,
				CallLog.caller,
				CallLog.receiver,
				CallLog["from"],
				CallLog.to,
				CallLog.duration,
				CallLog.start_time,
				CallLog.end_time,
				CallLog.status,
				CallLog.type,
				CallLog.recording_url,
				CallLog.creation,
				CallLog.note,
				CallLog.customer_name,
				CallLog.employee,
				CallLog.customer,
				Link.link_doctype,
				Link.link_name,
			)
			.join(Link, JoinType.inner)
			.on(Link.parent == CallLog.name)
			.where(CallLog.name.isin(linked_calls))
		)
		_calls = query.run(as_dict=True)

		for call in _calls:
			if call.get("link_doctype") == "FCRM Note":
				notes.append(call.link_name)
			elif call.get("link_doctype") == "CRM Task":
				tasks.append(call.link_name)

		_calls = [call for call in _calls if call.get("link_doctype") not in ["FCRM Note", "CRM Task"]]
		if _calls:
			calls = calls + _calls

	if notes:
		notes = frappe.db.get_all(
			"FCRM Note",
			filters={"name": ("in", notes)},
			fields=["name", "title", "content", "owner", "modified"],
		)

	if tasks:
		tasks = frappe.db.get_all(
			"CRM Task",
			filters={"name": ("in", tasks)},
			fields=[
				"name",
				"title",
				"description",
				"assigned_to",
				"due_date",
				"priority",
				"status",
				"modified",
			],
		)

	calls = [parse_call_log(call) for call in calls] if calls else []

	if calls or notes or tasks:
		# Get the doctype from the first call's reference_doctype
		if calls:
			doctype = frappe.db.get_value("CRM Call Log", calls[0]["name"], "reference_doctype")
			if doctype:
				emit_activity_update(doctype, name)

	return {"calls": calls, "notes": notes, "tasks": tasks}


def get_linked_notes(name):
	notes = frappe.db.get_all(
		"FCRM Note",
		filters={"reference_docname": name},
		fields=["name", "title", "content", "owner", "modified"],
	)
	
	if notes:
		# Get the doctype from the first note's reference_doctype
		doctype = frappe.db.get_value("FCRM Note", notes[0]["name"], "reference_doctype")
		if doctype:
			emit_activity_update(doctype, name)
	
	return notes or []


def get_linked_tasks(name):
	tasks = frappe.db.get_all(
		"CRM Task",
		filters={"reference_docname": name},
		fields=[
			"name",
			"title",
			"description",
			"assigned_to",
			"due_date",
			"priority",
			"status",
			"modified",
			"owner",
			"creation",
		],
	)
	
	if tasks:
		# Get the doctype from the first task's reference_doctype
		doctype = frappe.db.get_value("CRM Task", tasks[0]["name"], "reference_doctype")
		if doctype:
			emit_activity_update(doctype, name)
	
	return tasks or []


def parse_attachment_log(html, type):
	soup = BeautifulSoup(html, "html.parser")
	a_tag = soup.find("a")
	type = "added" if type == "Attachment" else "removed"
	if not a_tag:
		return {
			"type": type,
			"file_name": html.replace("Removed ", ""),
			"file_url": "",
			"is_private": False,
		}

	is_private = False
	if "private/files" in a_tag["href"]:
		is_private = True

	return {
		"type": type,
		"file_name": a_tag.text,
		"file_url": a_tag["href"],
		"is_private": is_private,
	}
