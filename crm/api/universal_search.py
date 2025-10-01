"""
Universal Search API for CRM
Provides intelligent search across all CRM DocTypes with advanced matching
"""

import frappe
from frappe import _
from frappe.utils import cstr
import re


@frappe.whitelist()
def universal_search(query, limit=20):
	"""
	Intelligent universal search across all CRM entities
	Searches: Leads, Customers, Tickets, Tasks, Call Logs, Notes, Support Pages
	
	Args:
		query: Search text
		limit: Maximum results per DocType (default: 20)
	
	Returns:
		Dictionary with results grouped by DocType
	"""
	if not query or len(query.strip()) < 2:
		return {"results": [], "total_count": 0}
	
	query = query.strip()
	results = []
	
	# Get user permissions
	from frappe.permissions import has_permission
	
	# Define searchable DocTypes with their search configurations
	search_configs = [
		{
			"doctype": "CRM Lead",
			"title_field": "lead_name",
			"subtitle_field": "organization",
			"search_fields": ["lead_name", "email", "mobile_no", "organization", "lead_owner"],
			"icon": "user",
			"route": "/crm/leads/{name}",
			"label": "Lead"
		},
		{
			"doctype": "CRM Customer",
			"title_field": "customer_name",
			"subtitle_field": "customer_type",
			"search_fields": ["customer_name", "email", "mobile_no", "pan_number", "aadhar_number"],
			"icon": "users",
			"route": "/crm/customers/{name}",
			"label": "Customer"
		},
		{
			"doctype": "CRM Ticket",
			"title_field": "subject",
			"subtitle_field": "status",
			"search_fields": ["subject", "description", "contact", "raised_by"],
			"icon": "ticket",
			"route": "/crm/tickets/{name}",
			"label": "Ticket"
		},
		{
			"doctype": "CRM Task",
			"title_field": "title",
			"subtitle_field": "assigned_to",
			"search_fields": ["title", "description", "assigned_to"],
			"icon": "check-square",
			"route": "/crm/tasks/view/list",
			"label": "Task"
		},
		{
			"doctype": "CRM Call Log",
			"title_field": "caller",
			"subtitle_field": "status",
			"search_fields": ["caller", "receiver", "note", "lead"],
			"icon": "phone",
			"route": "/crm/call-logs/view/list",
			"label": "Call Log"
		},
		{
			"doctype": "FCRM Note",
			"title_field": "title",
			"subtitle_field": "owner",
			"search_fields": ["title", "content"],
			"icon": "file-text",
			"route": "/crm/notes/view/list",
			"label": "Note"
		},
		{
			"doctype": "CRM Support Pages",
			"title_field": "page_name",
			"subtitle_field": "category",
			"search_fields": ["page_name", "content", "category"],
			"icon": "help-circle",
			"route": "/crm/support-pages/view/list",
			"label": "Support Page"
		},
	]
	
	# Search across each DocType
	for config in search_configs:
		try:
			# Check if user has permission to read this DocType
			if not has_permission(config["doctype"], "read"):
				continue
			
			# Check if DocType exists
			if not frappe.db.exists("DocType", config["doctype"]):
				continue
			
			# Build search query
			doctype_results = search_in_doctype(query, config, limit)
			
			if doctype_results:
				results.extend(doctype_results)
		
		except Exception as e:
			# Log error but continue searching other DocTypes
			frappe.log_error(f"Universal Search Error in {config['doctype']}: {str(e)}")
			continue
	
	# Sort results by relevance score (already sorted within each DocType)
	results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
	
	# Limit total results
	results = results[:50]  # Max 50 total results
	
	return {
		"results": results,
		"total_count": len(results),
		"query": query
	}


def search_in_doctype(query, config, limit):
	"""
	Search within a specific DocType using intelligent matching
	"""
	doctype = config["doctype"]
	search_fields = config["search_fields"]
	title_field = config["title_field"]
	subtitle_field = config.get("subtitle_field")
	
	# Build WHERE conditions for search
	conditions = []
	query_lower = query.lower()
	
	# Escape special characters for SQL LIKE
	query_escaped = query.replace("%", "\\%").replace("_", "\\_")
	
	# Create search conditions for each field
	for field in search_fields:
		# Exact match gets highest priority
		conditions.append(f"LOWER(`{field}`) = {frappe.db.escape(query_lower)}")
		# Starts with match
		conditions.append(f"LOWER(`{field}`) LIKE {frappe.db.escape(query_lower + '%')}")
		# Contains match
		conditions.append(f"LOWER(`{field}`) LIKE {frappe.db.escape('%' + query_escaped + '%')}")
	
	# Build the query
	where_clause = " OR ".join(conditions)
	
	# Get meta to check if status field exists
	meta = frappe.get_meta(doctype)
	has_status = any(field.fieldname == "status" for field in meta.fields)
	
	# Select fields
	select_fields = ["name", title_field]
	if subtitle_field and subtitle_field != title_field:
		select_fields.append(subtitle_field)
	if has_status:
		select_fields.append("status")
	
	# Add search fields for highlighting
	for field in search_fields:
		if field not in select_fields:
			select_fields.append(field)
	
	# Execute query
	sql = f"""
		SELECT {', '.join([f'`{f}`' for f in select_fields])}, 'doctype_placeholder' as doctype
		FROM `tab{doctype}`
		WHERE ({where_clause})
		AND docstatus < 2
		ORDER BY modified DESC
		LIMIT {int(limit)}
	"""
	
	results = frappe.db.sql(sql, as_dict=True)
	
	# Process and score results
	processed_results = []
	for row in results:
		# Calculate relevance score
		relevance_score = calculate_relevance_score(query_lower, row, search_fields)
		
		# Build result object
		result = {
			"doctype": doctype,
			"name": row.get("name"),
			"title": cstr(row.get(title_field) or ""),
			"subtitle": cstr(row.get(subtitle_field) or "") if subtitle_field else "",
			"status": row.get("status") if has_status else None,
			"icon": config.get("icon", "file"),
			"route": config["route"].format(name=row.get("name")),
			"label": config["label"],
			"relevance_score": relevance_score,
			"matched_field": get_matched_field(query_lower, row, search_fields)
		}
		
		processed_results.append(result)
	
	# Sort by relevance score
	processed_results.sort(key=lambda x: x["relevance_score"], reverse=True)
	
	return processed_results


def calculate_relevance_score(query, row, search_fields):
	"""
	Calculate relevance score based on match quality
	Higher score = better match
	"""
	score = 0
	query_lower = query.lower()
	
	for field in search_fields:
		value = cstr(row.get(field, "")).lower()
		
		if not value:
			continue
		
		# Exact match: highest score
		if value == query_lower:
			score += 100
		
		# Starts with: high score
		elif value.startswith(query_lower):
			score += 50
		
		# Contains word boundary match: medium-high score
		elif re.search(r'\b' + re.escape(query_lower), value):
			score += 30
		
		# Contains anywhere: medium score
		elif query_lower in value:
			score += 10
		
		# Fuzzy match (words contain query): low score
		query_words = query_lower.split()
		for word in query_words:
			if word in value:
				score += 5
	
	return score


def get_matched_field(query, row, search_fields):
	"""
	Get the field name where the best match was found
	"""
	query_lower = query.lower()
	best_match = None
	best_score = 0
	
	for field in search_fields:
		value = cstr(row.get(field, "")).lower()
		
		if not value or query_lower not in value:
			continue
		
		# Score this match
		if value == query_lower:
			return field  # Perfect match, return immediately
		elif value.startswith(query_lower) and 50 > best_score:
			best_match = field
			best_score = 50
		elif query_lower in value and 10 > best_score:
			best_match = field
			best_score = 10
	
	return best_match or search_fields[0]


@frappe.whitelist()
def get_recent_items(limit=5):
	"""
	Get recently viewed/accessed items for quick access
	"""
	# This would track user's recently viewed items
	# For now, return recent modified items
	results = []
	
	doctypes = ["CRM Lead", "CRM Customer", "CRM Ticket"]
	
	for doctype in doctypes:
		try:
			if not frappe.has_permission(doctype, "read"):
				continue
			
			items = frappe.get_all(
				doctype,
				filters={"modified_by": frappe.session.user},
				fields=["name", "modified"],
				order_by="modified desc",
				limit=limit
			)
			
			results.extend([{
				"doctype": doctype,
				"name": item.name,
				"modified": item.modified
			} for item in items])
		
		except Exception:
			continue
	
	# Sort by modified date
	results.sort(key=lambda x: x["modified"], reverse=True)
	
	return results[:limit]
