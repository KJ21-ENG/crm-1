import json

import frappe
from frappe import _
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.desk.form.assign_to import set_status
from frappe.model import no_value_fields
from frappe.model.document import get_controller
from frappe.utils import make_filter_tuple
from pypika import Criterion

from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.utils import get_dynamic_linked_docs, get_linked_docs


@frappe.whitelist()
def sort_options(doctype: str):
	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in no_value_fields]
	fields = [
		{
			"label": _(field.label),
			"value": field.fieldname,
			"fieldname": field.fieldname,
		}
		for field in fields
		if field.label and field.fieldname
	]

	standard_fields = [
		{"label": "Name", "fieldname": "name"},
		{"label": "Created On", "fieldname": "creation"},
		{"label": "Last Modified", "fieldname": "modified"},
		{"label": "Modified By", "fieldname": "modified_by"},
		{"label": "Owner", "fieldname": "owner"},
	]

	for field in standard_fields:
		field["label"] = _(field["label"])
		field["value"] = field["fieldname"]
		fields.append(field)

	return fields


@frappe.whitelist()
def get_filterable_fields(doctype: str):
	allowed_fieldtypes = [
		"Check",
		"Data",
		"Float",
		"Int",
		"Currency",
		"Dynamic Link",
		"Link",
		"Long Text",
		"Select",
		"Small Text",
		"Text Editor",
		"Text",
		"Duration",
		"Date",
		"Datetime",
	]

	c = get_controller(doctype)
	restricted_fields = []
	if hasattr(c, "get_non_filterable_fields"):
		restricted_fields = c.get_non_filterable_fields()

	res = []

	# append DocFields
	DocField = frappe.qb.DocType("DocField")
	doc_fields = get_doctype_fields_meta(DocField, doctype, allowed_fieldtypes, restricted_fields)
	res.extend(doc_fields)

	# append Custom Fields
	CustomField = frappe.qb.DocType("Custom Field")
	custom_fields = get_doctype_fields_meta(CustomField, doctype, allowed_fieldtypes, restricted_fields)
	res.extend(custom_fields)

	# append standard fields (getting error when using frappe.model.std_fields)
	standard_fields = [
		{"fieldname": "name", "fieldtype": "Link", "label": "ID", "options": doctype},
		{"fieldname": "owner", "fieldtype": "Link", "label": "Created By", "options": "User"},
		{
			"fieldname": "modified_by",
			"fieldtype": "Link",
			"label": "Last Updated By",
			"options": "User",
		},
		{"fieldname": "_user_tags", "fieldtype": "Data", "label": "Tags"},
		{"fieldname": "_liked_by", "fieldtype": "Data", "label": "Like"},
		{"fieldname": "_comments", "fieldtype": "Text", "label": "Comments"},
		{"fieldname": "_assign", "fieldtype": "Text", "label": "Assigned To"},
		{"fieldname": "creation", "fieldtype": "Datetime", "label": "Created On"},
		{"fieldname": "modified", "fieldtype": "Datetime", "label": "Last Updated On"},
	]
	for field in standard_fields:
		if field.get("fieldname") not in restricted_fields and field.get("fieldtype") in allowed_fieldtypes:
			field["name"] = field.get("fieldname")
			res.append(field)

	for field in res:
		field["label"] = _(field.get("label"))
		field["value"] = field.get("fieldname")

	return res


@frappe.whitelist()
def get_group_by_fields(doctype: str):
	allowed_fieldtypes = [
		"Check",
		"Data",
		"Float",
		"Int",
		"Currency",
		"Dynamic Link",
		"Link",
		"Select",
		"Duration",
		"Date",
		"Datetime",
	]

	fields = frappe.get_meta(doctype).fields
	fields = [
		field
		for field in fields
		if field.fieldtype not in no_value_fields and field.fieldtype in allowed_fieldtypes
	]
	fields = [
		{
			"label": _(field.label),
			"fieldname": field.fieldname,
		}
		for field in fields
		if field.label and field.fieldname
	]

	standard_fields = [
		{"label": "Name", "fieldname": "name"},
		{"label": "Created On", "fieldname": "creation"},
		{"label": "Last Modified", "fieldname": "modified"},
		{"label": "Modified By", "fieldname": "modified_by"},
		{"label": "Owner", "fieldname": "owner"},
		{"label": "Liked By", "fieldname": "_liked_by"},
		{"label": "Assigned To", "fieldname": "_assign"},
		{"label": "Comments", "fieldname": "_comments"},
		{"label": "Created On", "fieldname": "creation"},
		{"label": "Modified On", "fieldname": "modified"},
	]

	for field in standard_fields:
		field["label"] = _(field["label"])
		fields.append(field)

	return fields


def get_doctype_fields_meta(DocField, doctype, allowed_fieldtypes, restricted_fields):
	parent = "parent" if DocField._table_name == "tabDocField" else "dt"
	return (
		frappe.qb.from_(DocField)
		.select(
			DocField.fieldname,
			DocField.fieldtype,
			DocField.label,
			DocField.name,
			DocField.options,
		)
		.where(DocField[parent] == doctype)
		.where(DocField.hidden == False)  # noqa: E712
		.where(Criterion.any([DocField.fieldtype == i for i in allowed_fieldtypes]))
		.where(Criterion.all([DocField.fieldname != i for i in restricted_fields]))
		.run(as_dict=True)
	)


@frappe.whitelist()
def get_quick_filters(doctype: str, cached: bool = True):
	meta = frappe.get_meta(doctype, cached)
	quick_filters = []

	if global_settings := frappe.db.exists("CRM Global Settings", {"dt": doctype, "type": "Quick Filters"}):
		_quick_filters = frappe.db.get_value("CRM Global Settings", global_settings, "json")
		_quick_filters = json.loads(_quick_filters) or []

		fields = []

		for filter in _quick_filters:
			if filter == "name":
				fields.append({"label": "Name", "fieldname": "name", "fieldtype": "Data"})
			else:
				field = next((f for f in meta.fields if f.fieldname == filter), None)
				if field:
					fields.append(field)

	else:
		fields = [field for field in meta.fields if field.in_standard_filter]

	for field in fields:
		options = field.get("options")
		if field.get("fieldtype") == "Select" and options and isinstance(options, str):
			options = options.split("\n")
			options = [{"label": option, "value": option} for option in options]
			if not any([not option.get("value") for option in options]):
				options.insert(0, {"label": "", "value": ""})
		quick_filters.append(
			{
				"label": _(field.get("label")),
				"fieldname": field.get("fieldname"),
				"fieldtype": field.get("fieldtype"),
				"options": options,
			}
		)

	if doctype == "CRM Lead":
		quick_filters = [filter for filter in quick_filters if filter.get("fieldname") != "converted"]

	return quick_filters


@frappe.whitelist()
def update_quick_filters(quick_filters: str, old_filters: str, doctype: str):
	quick_filters = json.loads(quick_filters)
	old_filters = json.loads(old_filters)

	new_filters = [filter for filter in quick_filters if filter not in old_filters]
	removed_filters = [filter for filter in old_filters if filter not in quick_filters]

	# update or create global quick filter settings
	create_update_global_settings(doctype, quick_filters)

	# remove old filters
	for filter in removed_filters:
		update_in_standard_filter(filter, doctype, 0)

	# add new filters
	for filter in new_filters:
		update_in_standard_filter(filter, doctype, 1)


def create_update_global_settings(doctype, quick_filters):
	if global_settings := frappe.db.exists("CRM Global Settings", {"dt": doctype, "type": "Quick Filters"}):
		frappe.db.set_value("CRM Global Settings", global_settings, "json", json.dumps(quick_filters))
	else:
		# create CRM Global Settings doc
		doc = frappe.new_doc("CRM Global Settings")
		doc.dt = doctype
		doc.type = "Quick Filters"
		doc.json = json.dumps(quick_filters)
		doc.insert()


def update_in_standard_filter(fieldname, doctype, value):
	if property_name := frappe.db.exists(
		"Property Setter",
		{"doc_type": doctype, "field_name": fieldname, "property": "in_standard_filter"},
	):
		frappe.db.set_value("Property Setter", property_name, "value", value)
	else:
		make_property_setter(
			doctype,
			fieldname,
			"in_standard_filter",
			value,
			"Check",
			validate_fields_for_doctype=False,
		)


@frappe.whitelist()
def get_data(
	doctype: str,
	filters: dict,
	order_by: str,
	page_length=20,
	page_length_count=20,
	start=0,  # Add start parameter for pagination
	column_field=None,
	title_field=None,
	columns=[],
	rows=[],
	kanban_columns=[],
	kanban_fields=[],
	view=None,
	default_filters=None,
):
	# Debug logging for call log filtering
	frappe.logger().info(f"🔍 Backend Debug - Doctype: {doctype}")
	frappe.logger().info(f"🔍 Backend Debug - Original filters: {filters}")
	frappe.logger().info(f"🔍 Backend Debug - Default filters: {default_filters}")
	frappe.logger().info(f"🔍 Backend Debug - Current user: {frappe.session.user}")
	frappe.logger().info(f"🔍 Backend Debug - Original order_by: {order_by}")
	frappe.logger().info(f"🔍 Backend Debug - Pagination: start={start}, page_length={page_length}")
	
	custom_view = False
	filters = frappe._dict(filters)
	rows = frappe.parse_json(rows or "[]")
	columns = frappe.parse_json(columns or "[]")
	kanban_fields = frappe.parse_json(kanban_fields or "[]")
	kanban_columns = frappe.parse_json(kanban_columns or "[]")

	custom_view_name = view.get("custom_view_name") if view else None
	view_type = view.get("view_type") if view else None
	group_by_field = view.get("group_by_field") if view else None

	for key in filters:
		value = filters[key]
		if isinstance(value, list):
			if "@me" in value:
				value[value.index("@me")] = frappe.session.user
			elif "%@me%" in value:
				index = [i for i, v in enumerate(value) if v == "%@me%"]
				for i in index:
					value[i] = "%" + frappe.session.user + "%"
		elif value == "@me":
			filters[key] = frappe.session.user

	if default_filters:
		default_filters = frappe.parse_json(default_filters)
		frappe.logger().info(f"🔍 Backend Debug - Parsed default filters: {default_filters}")
		# Merge default filters WITHOUT overriding explicit filters from the client
		# This ensures manual date changes (e.g., Yesterday/Tomorrow) take precedence
		for _k, _v in (default_filters or {}).items():
			if _k not in filters:
				filters[_k] = _v
		frappe.logger().info(f"🔍 Backend Debug - Final merged filters (non-overriding): {filters}")

	# Special logging for Call Log debug
	if doctype == "CRM Call Log":
		frappe.logger().info(f"🔍 Call Log Debug - Final filters applied: {filters}")
		frappe.logger().info(f"🔍 Call Log Debug - Owner filter value: {filters.get('owner', 'NOT SET')}")
		
		# Ensure owner filter is applied for Call Logs if not already present
		if 'owner' not in filters and default_filters and 'owner' in default_filters:
			frappe.logger().info(f"🔍 Call Log Debug - Manually applying owner filter from default_filters")
			filters['owner'] = default_filters['owner']
		
		# If no owner filter but user is not Administrator, force user filter
		if 'owner' not in filters and frappe.session.user != 'Administrator':
			frappe.logger().info(f"🔍 Call Log Debug - No owner filter found, forcing current user filter")
			filters['owner'] = frappe.session.user
			
		frappe.logger().info(f"🔍 Call Log Debug - FINAL filters after manual checks: {filters}")

	# Normalize date filters for Assignment Requests: when user picks a date-only value
	# for Datetime fields like creation/approved_on, convert to a full-day range so time is ignored
	if doctype == "CRM Assignment Request":
		for _field in ["creation", "approved_on"]:
			if _field in filters:
				val = filters.get(_field)
				# If frontend passed a simple date string like '2025-09-01', convert to full-day range
				if isinstance(val, str):
					try:
						# Support ISO 'YYYY-MM-DD' only
						if len(val) >= 10 and val[4] == '-' and val[7] == '-':
							_date = val[:10]
							start_of_day = f"{_date} 00:00:00"
							end_of_day = f"{_date} 23:59:59"
							filters[_field] = ['between', [start_of_day, end_of_day]]
					except Exception:
						pass
				# If equal comparison came as a datetime tuple, leave as-is
		# Normalize date filters for Call Log: if user provided a date (no time),
		# convert to a between range for the full day so datetime equality works.
		if 'start_time' in filters:
			val = filters.get('start_time')
			# If frontend passed a simple date string like '2025-08-15', convert to full-day range
			if isinstance(val, str) and len(val) == 10 and val[4] == '-' and val[7] == '-':
				start_of_day = f"{val} 00:00:00"
				end_of_day = f"{val} 23:59:59"
				filters['start_time'] = ['between', [start_of_day, end_of_day]]

	is_default = True
	data = []
	_list = get_controller(doctype)
	default_rows = []
	default_order_by = None
	if hasattr(_list, "default_list_data"):
		default_list_data = _list.default_list_data()
		default_rows = default_list_data.get("rows")
		default_order_by = default_list_data.get("order_by")

	# Use default order_by from doctype if no custom order_by is provided or if it's the default
	if order_by == 'modified desc' and default_order_by:
		order_by = default_order_by
		frappe.logger().info(f"🔍 Backend Debug - Using default order_by from doctype: {order_by}")

	meta = frappe.get_meta(doctype)

	if view_type != "kanban":
		if columns or rows:
			custom_view = True
			is_default = False
			columns = frappe.parse_json(columns)
			rows = frappe.parse_json(rows)

		if not columns:
			columns = [
				{"label": "Name", "type": "Data", "key": "name", "width": "16rem"},
				{"label": "Last Modified", "type": "Datetime", "key": "modified", "width": "8rem"},
			]

		if not rows:
			rows = ["name"]

		default_view_filters = {
			"dt": doctype,
			"type": view_type or "list",
			"is_standard": 1,
			"user": frappe.session.user,
		}

		if not custom_view and frappe.db.exists("CRM View Settings", default_view_filters):
			list_view_settings = frappe.get_doc("CRM View Settings", default_view_filters)
			columns = frappe.parse_json(list_view_settings.columns)
			rows = frappe.parse_json(list_view_settings.rows)
			is_default = False
		elif not custom_view or (is_default and hasattr(_list, "default_list_data")):
			rows = default_rows
			columns = _list.default_list_data().get("columns")

		# check if rows has all keys from columns if not add them
		for column in columns:
			if column.get("key") not in rows:
				rows.append(column.get("key"))
			column["label"] = _(column.get("label"))

			if column.get("key") == "_liked_by" and column.get("width") == "10rem":
				column["width"] = "50px"

			# remove column if column.hidden is True
			column_meta = meta.get_field(column.get("key"))
			if column_meta and column_meta.get("hidden"):
				columns.remove(column)

		# check if rows has group_by_field if not add it
		if group_by_field and group_by_field not in rows:
			rows.append(group_by_field)

		frappe.logger().info(f"🔍 Backend Debug - Final order_by used: {order_by}")
		
		# Special handling for CRM Ticket and CRM Lead to join with customer table
		if doctype == "CRM Ticket" and "customer_name" in rows:
			# Ensure image field is included for customer avatar display
			if "image" not in rows:
				rows.append("image")
			data = get_ticket_list_with_customer_data(rows, filters, order_by, page_length, start)
		elif doctype == "CRM Lead" and "lead_name" in rows:
			# Ensure image field is included for customer avatar display
			if "image" not in rows:
				rows.append("image")
			data = get_lead_list_with_customer_data(rows, filters, order_by, page_length, start)
		else:
			# Use tuple-style filters to allow operators (>, <, between, like, etc.)
			data = (
				frappe.get_list(
					doctype,
					fields=rows,
					filters=convert_filter_to_tuple(doctype, filters),
					order_by=order_by,
					page_length=page_length,
					start=start,  # Add start parameter for pagination
				)
				or []
			)
		data = parse_list_data(data, doctype)

		# Enrich user link fields with full name and image for better UX
		# Specifically handle CRM Ticket to show user's full name instead of email
		if doctype == "CRM Ticket" and data:
			# Collect unique user emails from ticket_owner and assigned_to
			user_emails = set()
			for row in data:
				if row.get("ticket_owner"):
					user_emails.add(row.get("ticket_owner"))
				if row.get("assigned_to"):
					user_emails.add(row.get("assigned_to"))

			if user_emails:
				users_meta = {}
				# Fetch user full_name and image in one query
				users = frappe.get_all(
					"User",
					filters={"name": ["in", list(user_emails)]},
					fields=["name", "full_name", "user_image"],
				)
				for u in users:
					users_meta[u.name] = {"full_name": u.full_name or u.name, "user_image": u.user_image}

				# Attach enriched data so frontend can render Avatar with name instead of email
				for row in data:
					owner = row.get("ticket_owner")
					assignee = row.get("assigned_to")
					# Replace ticket_owner email with full name string for display
					if owner and owner in users_meta:
						row["ticket_owner"] = users_meta[owner]["full_name"]

		# Enrich FCRM Note list rows with linked customer info when possible
		if doctype == "FCRM Note" and data:
			for row in data:
				try:
					# initialize fields
					row["customer_name"] = None
					row["customer_mobile_no"] = None
					ref_doctype = row.get("reference_doctype")
					ref_name = row.get("reference_docname")
					if ref_doctype in ("CRM Lead", "CRM Ticket") and ref_name:
						# get customer_id from referenced doc
						customer_id = frappe.db.get_value(ref_doctype, ref_name, "customer_id")
						if customer_id:
							cust = frappe.db.get_value(
								"CRM Customer",
								customer_id,
								["customer_name", "mobile_no"],
								as_dict=True,
							)
							if cust:
								row["customer_name"] = cust.get("customer_name")
								row["customer_mobile_no"] = cust.get("mobile_no")
				except Exception as e:
					frappe.logger().error(f"Error enriching note {row.get('name')}: {e}")

	if view_type == "kanban":
		if not rows:
			rows = default_rows

		if not kanban_columns and column_field:
			field_meta = frappe.get_meta(doctype).get_field(column_field)
			if field_meta.fieldtype == "Link":
				kanban_columns = frappe.get_all(
					field_meta.options,
					fields=["name"],
					order_by="modified asc",
				)
			elif field_meta.fieldtype == "Select":
				kanban_columns = [{"name": option} for option in field_meta.options.split("\n")]

		if not title_field:
			title_field = "name"
			if hasattr(_list, "default_kanban_settings"):
				title_field = _list.default_kanban_settings().get("title_field")

		if title_field not in rows:
			rows.append(title_field)

		if not kanban_fields:
			kanban_fields = ["name"]
			if hasattr(_list, "default_kanban_settings"):
				kanban_fields = json.loads(_list.default_kanban_settings().get("kanban_fields"))

		for field in kanban_fields:
			if field not in rows:
				rows.append(field)

		for kc in kanban_columns:
			# Start with base filters
			column_filters = []

			# Convert and add the main filters first
			if filters:
				base_filters = convert_filter_to_tuple(doctype, filters)
				column_filters.extend(base_filters)

			# Add the column-specific filter
			if column_field and kc.get("name"):
				column_filters.append([doctype, column_field, "=", kc.get("name")])

			order = kc.get("order")
			if kc.get("delete"):
				column_data = []
			else:
				page_length = kc.get("page_length", 20)

				if order:
					column_data = get_records_based_on_order(
						doctype, rows, column_filters, page_length, order
					)
				else:
					column_data = frappe.get_list(
						doctype,
						fields=rows,
						filters=column_filters,
						order_by=order_by,
						page_length=page_length,
					)

				all_count = frappe.get_list(
					doctype,
					filters=column_filters,
					fields="count(*) as total_count",
				)[0].total_count

				kc["all_count"] = all_count
				kc["count"] = len(column_data)

			if order:
				column_data = sorted(
					column_data,
					key=lambda x: order.index(x.get("name")) if x.get("name") in order else len(order),
				)

			data.append({"column": kc, "fields": kanban_fields, "data": column_data})

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in no_value_fields]
	fields = [
		{
			"label": _(field.label),
			"fieldtype": field.fieldtype,
			"fieldname": field.fieldname,
			"options": field.options,
		}
		for field in fields
		if field.label and field.fieldname
	]

	std_fields = [
		{"label": "Name", "fieldtype": "Data", "fieldname": "name"},
		{"label": "Created On", "fieldtype": "Datetime", "fieldname": "creation"},
		{"label": "Last Modified", "fieldtype": "Datetime", "fieldname": "modified"},
		{
			"label": "Modified By",
			"fieldtype": "Link",
			"fieldname": "modified_by",
			"options": "User",
		},
		{"label": "Assigned To", "fieldtype": "Text", "fieldname": "_assign"},
		{"label": "Owner", "fieldtype": "Link", "fieldname": "owner", "options": "User"},
		{"label": "Like", "fieldtype": "Data", "fieldname": "_liked_by"},
	]

	for field in std_fields:
		if field.get("fieldname") not in rows:
			rows.append(field.get("fieldname"))
		if field not in fields:
			field["label"] = _(field["label"])
			fields.append(field)

	if not is_default and custom_view_name:
		is_default = frappe.db.get_value("CRM View Settings", custom_view_name, "load_default_columns")

	if group_by_field and view_type == "group_by":

		def get_options(type, options):
			if type == "Select":
				return [option for option in options.split("\n")]
			else:
				has_empty_values = any([not d.get(group_by_field) for d in data])
				options = list(set([d.get(group_by_field) for d in data]))
				options = [u for u in options if u]
				if has_empty_values:
					options.append("")

				if order_by and group_by_field in order_by:
					order_by_fields = order_by.split(",")
					order_by_fields = [
						(field.split(" ")[0], field.split(" ")[1]) for field in order_by_fields
					]
					if (group_by_field, "asc") in order_by_fields:
						options.sort()
					elif (group_by_field, "desc") in order_by_fields:
						options.sort(reverse=True)
				else:
					options.sort()
				return options

		for field in fields:
			if field.get("fieldname") == group_by_field:
				group_by_field = {
					"label": field.get("label"),
					"fieldname": field.get("fieldname"),
					"fieldtype": field.get("fieldtype"),
					"options": get_options(field.get("fieldtype"), field.get("options")),
				}

	return {
		"data": data,
		"columns": columns,
		"rows": rows,
		"column_field": column_field,
		"title_field": title_field,
		"kanban_columns": kanban_columns,
		"kanban_fields": kanban_fields,
		"group_by_field": group_by_field,
		"page_length": page_length,
		"page_length_count": page_length_count,
		"start": start,  # Add start parameter to response
		"is_default": is_default,
		"views": get_views(doctype),
		"total_count": frappe.get_list(doctype, filters=convert_filter_to_tuple(doctype, filters), fields="count(*) as total_count")[
			0
		].total_count,
		"row_count": len(data),
		"form_script": get_form_script(doctype),
		"list_script": get_form_script(doctype, "List"),
		"view_type": view_type,
	}


def parse_list_data(data, doctype):
	_list = get_controller(doctype)
	if hasattr(_list, "parse_list_data"):
		data = _list.parse_list_data(data)
	return data


def convert_filter_to_tuple(doctype, filters):
	if isinstance(filters, dict):
		filters_items = filters.items()
		filters = []
		for key, value in filters_items:
			filters.append(make_filter_tuple(doctype, key, value))
	return filters


def get_records_based_on_order(doctype, rows, filters, page_length, order):
	records = []
	filters = convert_filter_to_tuple(doctype, filters)
	in_filters = filters.copy()
	in_filters.append([doctype, "name", "in", order[:page_length]])
	records = frappe.get_list(
		doctype,
		fields=rows,
		filters=in_filters,
		order_by="creation desc",
		page_length=page_length,
	)

	if len(records) < page_length:
		not_in_filters = filters.copy()
		not_in_filters.append([doctype, "name", "not in", order])
		remaining_records = frappe.get_list(
			doctype,
			fields=rows,
			filters=not_in_filters,
			order_by="creation desc",
			page_length=page_length - len(records),
		)
		for record in remaining_records:
			records.append(record)

	return records


@frappe.whitelist()
def get_fields_meta(doctype, restricted_fieldtypes=None, as_array=False, only_required=False):
	not_allowed_fieldtypes = [
		"Tab Break",
		"Section Break",
		"Column Break",
	]

	if restricted_fieldtypes:
		restricted_fieldtypes = frappe.parse_json(restricted_fieldtypes)
		not_allowed_fieldtypes += restricted_fieldtypes

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in not_allowed_fieldtypes]

	standard_fields = [
		{"fieldname": "name", "fieldtype": "Link", "label": "ID", "options": doctype},
		{"fieldname": "owner", "fieldtype": "Link", "label": "Created By", "options": "User"},
		{
			"fieldname": "modified_by",
			"fieldtype": "Link",
			"label": "Last Updated By",
			"options": "User",
		},
		{"fieldname": "_user_tags", "fieldtype": "Data", "label": "Tags"},
		{"fieldname": "_liked_by", "fieldtype": "Data", "label": "Like"},
		{"fieldname": "_comments", "fieldtype": "Text", "label": "Comments"},
		{"fieldname": "_assign", "fieldtype": "Text", "label": "Assigned To"},
		{"fieldname": "creation", "fieldtype": "Datetime", "label": "Created On"},
		{"fieldname": "modified", "fieldtype": "Datetime", "label": "Last Updated On"},
	]

	for field in standard_fields:
		if not restricted_fieldtypes or field.get("fieldtype") not in restricted_fieldtypes:
			fields.append(field)

	if only_required:
		fields = [field for field in fields if field.get("reqd")]

	if as_array:
		return fields

	fields_meta = {}
	for field in fields:
		fields_meta[field.get("fieldname")] = field
		if field.get("fieldtype") == "Table":
			_fields = frappe.get_meta(field.get("options")).fields
			fields_meta[field.get("fieldname")] = {"df": field, "fields": _fields}

	return fields_meta


@frappe.whitelist()
def remove_assignments(doctype, name, assignees, ignore_permissions=False):
	assignees = json.loads(assignees)

	if not assignees:
		return

	for assign_to in assignees:
		set_status(
			doctype,
			name,
			todo=None,
			assign_to=assign_to,
			status="Cancelled",
			ignore_permissions=ignore_permissions,
		)


@frappe.whitelist()
def get_assigned_users(doctype, name, default_assigned_to=None):
	assigned_users = frappe.get_all(
		"ToDo",
		fields=["allocated_to"],
		filters={
			"reference_type": doctype,
			"reference_name": name,
			"status": ("!=", "Cancelled"),
		},
		pluck="allocated_to",
	)

	users = list(set(assigned_users))

	# if users is empty, add default_assigned_to
	if not users and default_assigned_to:
		users = [default_assigned_to]
	return users


@frappe.whitelist()
def get_fields(doctype: str, allow_all_fieldtypes: bool = False):
	not_allowed_fieldtypes = [*list(frappe.model.no_value_fields), "Read Only"]
	if allow_all_fieldtypes:
		not_allowed_fieldtypes = []
	fields = frappe.get_meta(doctype).fields

	_fields = []

	for field in fields:
		if field.fieldtype not in not_allowed_fieldtypes and field.fieldname:
			_fields.append(field)

	return _fields


def getCounts(d, doctype):
	d["_email_count"] = (
		frappe.db.count(
			"Communication",
			filters={
				"reference_doctype": doctype,
				"reference_name": d.get("name"),
				"communication_type": "Communication",
			},
		)
		or 0
	)
	d["_email_count"] = d["_email_count"] + frappe.db.count(
		"Communication",
		filters={
			"reference_doctype": doctype,
			"reference_name": d.get("name"),
			"communication_type": "Automated Message",
		},
	)
	d["_comment_count"] = frappe.db.count(
		"Comment",
		filters={"reference_doctype": doctype, "reference_name": d.get("name"), "comment_type": "Comment"},
	)
	d["_task_count"] = frappe.db.count(
		"CRM Task", filters={"reference_doctype": doctype, "reference_docname": d.get("name")}
	)
	d["_note_count"] = frappe.db.count(
		"FCRM Note", filters={"reference_doctype": doctype, "reference_docname": d.get("name")}
	)
	return d


@frappe.whitelist()
def get_linked_docs_of_document(doctype, docname):
	doc = frappe.get_doc(doctype, docname)
	linked_docs = get_linked_docs(doc)
	dynamic_linked_docs = get_dynamic_linked_docs(doc)

	linked_docs.extend(dynamic_linked_docs)
	linked_docs = list({doc["reference_docname"]: doc for doc in linked_docs}.values())

	docs_data = []
	for doc in linked_docs:
		data = frappe.get_doc(doc["reference_doctype"], doc["reference_docname"])
		title = data.get("title")
		if data.doctype == "CRM Call Log":
			title = f"Call from {data.get('from')} to {data.get('to')}"

		if data.doctype == "CRM Deal":
			title = data.get("organization")

		docs_data.append(
			{
				"doc": data.doctype,
				"title": title or data.get("name"),
				"reference_docname": doc["reference_docname"],
				"reference_doctype": doc["reference_doctype"],
			}
		)
	return docs_data


def remove_doc_link(doctype, docname):
	linked_doc_data = frappe.get_doc(doctype, docname)
	linked_doc_data.update(
		{
			"reference_doctype": None,
			"reference_docname": None,
		}
	)
	linked_doc_data.save(ignore_permissions=True)


def remove_contact_link(doctype, docname):
	linked_doc_data = frappe.get_doc(doctype, docname)
	linked_doc_data.update(
		{
			"contact": None,
			"contacts": [],
		}
	)
	linked_doc_data.save(ignore_permissions=True)


@frappe.whitelist()
def remove_linked_doc_reference(items, remove_contact=None, delete=False):
	if isinstance(items, str):
		items = frappe.parse_json(items)

	for item in items:
		if remove_contact:
			remove_contact_link(item["doctype"], item["docname"])
		else:
			remove_doc_link(item["doctype"], item["docname"])

		if delete:
			frappe.delete_doc(item["doctype"], item["docname"])

	return "success"


@frappe.whitelist()
def delete_bulk_docs(doctype, items, delete_linked=False):
	from frappe.desk.reportview import delete_bulk

	items = frappe.parse_json(items)
	for doc in items:
		linked_docs = get_linked_docs_of_document(doctype, doc)
		for linked_doc in linked_docs:
			remove_linked_doc_reference(
				[
					{
						"doctype": linked_doc["reference_doctype"],
						"docname": linked_doc["reference_docname"],
					}
				],
				remove_contact=doctype == "Contact",
				delete=delete_linked,
			)

	if len(items) > 10:
		frappe.enqueue("frappe.desk.reportview.delete_bulk", doctype=doctype, items=items)
	else:
		delete_bulk(doctype, items)
	return "success"


def get_ticket_list_with_customer_data(rows, filters, order_by, page_length, start):
	"""
	Get ticket list data with customer information joined from customer table.
	Prioritizes customer_name from customer table over ticket table.
	"""
	from frappe.database.database import Database
	
	# Build the query to join tickets with customer table
	fields = []
	for field in rows:
		if field == "customer_name":
			# Use customer name from customer table if available, fallback to ticket table
			fields.append(f"COALESCE(c.customer_name, t.customer_name) as customer_name")
		elif field == "email":
			# Use email from customer table if available, fallback to ticket table
			fields.append(f"COALESCE(c.email, t.email) as email")
		elif field == "mobile_no":
			# Use mobile from customer table if available, fallback to ticket table
			fields.append(f"COALESCE(c.mobile_no, t.mobile_no) as mobile_no")
		elif field == "image":
			# Use customer image from customer table if available, fallback to ticket table
			fields.append(f"COALESCE(c.image, t.image) as image")
		else:
			fields.append(f"t.{field}")
	
	fields_str = ", ".join(fields)
	
	# Build WHERE clause from filters with proper operator handling and SQL parameters
	def _parse_op(val):
		if isinstance(val, (list, tuple)) and len(val) >= 2:
			op = str(val[0]).upper()
			rhs = val[1]
			return op, rhs
		return "=", val

	where_conditions = []
	values = []
	for key, value in filters.items():
		op, rhs = _parse_op(value)
		if key in ("customer_name", "customer"):
			# Customer quick filter: support LIKE on display name and equality on ID
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.customer_name, t.customer_name) LIKE %s)")
				values.append(rhs)
			else:
				# Treat as ID equality (customer docname)
				where_conditions.append("(c.name = %s OR t.customer_id = %s)")
				values.extend([rhs, rhs])
		elif key == "email":
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.email, t.email) LIKE %s)")
				values.append(rhs)
			else:
				where_conditions.append("(COALESCE(c.email, t.email) = %s)")
				values.append(rhs)
		elif key == "mobile_no":
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.mobile_no, t.mobile_no) LIKE %s)")
				values.append(rhs)
			else:
				where_conditions.append("(COALESCE(c.mobile_no, t.mobile_no) = %s)")
				values.append(rhs)
		elif key == "name":
			if op == "LIKE":
				where_conditions.append("t.name LIKE %s")
				values.append(rhs)
			else:
				where_conditions.append("t.name = %s")
				values.append(rhs)
		else:
			if op == "LIKE":
				where_conditions.append(f"t.{key} LIKE %s")
				values.append(rhs)
			else:
				where_conditions.append(f"t.{key} = %s")
				values.append(rhs)

	where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
	
	# Build ORDER BY clause
	order_clause = order_by.replace("modified", "t.modified").replace("creation", "t.creation")
	
	query = f"""
		SELECT {fields_str}
		FROM `tabCRM Ticket` t
		LEFT JOIN `tabCRM Customer` c ON t.customer_id = c.name
		WHERE {where_clause}
		ORDER BY {order_clause}
		LIMIT {page_length}
		OFFSET {start}
	"""
	
	try:
		result = frappe.db.sql(query, values=values, as_dict=True)
		return result
	except Exception as e:
		frappe.logger().error(f"Error in get_ticket_list_with_customer_data: {str(e)}")
		# Fallback to regular query if join fails
		return frappe.get_list(
			"CRM Ticket",
			fields=rows,
			filters=filters,
			order_by=order_by,
			page_length=page_length,
			start=start,
		) or []


def get_lead_list_with_customer_data(rows, filters, order_by, page_length, start):
	"""
	Get lead list data with customer information joined from customer table.
	Prioritizes customer_name from customer table over lead_name in lead table.
	"""
	from frappe.database.database import Database
	
	# Build the query to join leads with customer table
	fields = []
	for field in rows:
		if field == "lead_name":
			# Use customer name from customer table if available, fallback to lead table
			fields.append(f"COALESCE(c.customer_name, l.lead_name) as lead_name")
		elif field == "email":
			# Use email from customer table if available, fallback to lead table
			fields.append(f"COALESCE(c.email, l.email) as email")
		elif field == "mobile_no":
			# Use mobile from customer table if available, fallback to lead table
			fields.append(f"COALESCE(c.mobile_no, l.mobile_no) as mobile_no")
		elif field == "image":
			# Use customer image from customer table if available, fallback to lead table
			fields.append(f"COALESCE(c.image, l.image) as image")
		else:
			fields.append(f"l.{field}")
	
	fields_str = ", ".join(fields)
	
	# Build WHERE clause from filters with proper operator handling and SQL parameters
	def _parse_op(val):
		if isinstance(val, (list, tuple)) and len(val) >= 2:
			op = str(val[0]).upper()
			rhs = val[1]
			return op, rhs
		return "=", val

	where_conditions = []
	values = []
	for key, value in filters.items():
		op, rhs = _parse_op(value)
		if key in ("lead_name", "customer_name"):
			# Lead name quick filter should match customer display name or lead_name
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.customer_name, l.lead_name) LIKE %s)")
				values.append(rhs)
			else:
				where_conditions.append("(COALESCE(c.customer_name, l.lead_name) = %s)")
				values.append(rhs)
		elif key == "email":
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.email, l.email) LIKE %s)")
				values.append(rhs)
			else:
				where_conditions.append("(COALESCE(c.email, l.email) = %s)")
				values.append(rhs)
		elif key == "mobile_no":
			if op == "LIKE":
				where_conditions.append("(COALESCE(c.mobile_no, l.mobile_no) LIKE %s)")
				values.append(rhs)
			else:
				where_conditions.append("(COALESCE(c.mobile_no, l.mobile_no) = %s)")
				values.append(rhs)
		elif key == "name":
			if op == "LIKE":
				where_conditions.append("l.name LIKE %s")
				values.append(rhs)
			else:
				where_conditions.append("l.name = %s")
				values.append(rhs)
		else:
			if op == "LIKE":
				where_conditions.append(f"l.{key} LIKE %s")
				values.append(rhs)
			else:
				where_conditions.append(f"l.{key} = %s")
				values.append(rhs)

	where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
	
	# Build ORDER BY clause
	order_clause = order_by.replace("modified", "l.modified").replace("creation", "l.creation")
	
	query = f"""
		SELECT {fields_str}
		FROM `tabCRM Lead` l
		LEFT JOIN `tabCRM Customer` c ON l.customer_id = c.name
		WHERE {where_clause}
		ORDER BY {order_clause}
		LIMIT {page_length}
		OFFSET {start}
	"""
	
	try:
		result = frappe.db.sql(query, values=values, as_dict=True)
		return result
	except Exception as e:
		frappe.logger().error(f"Error in get_lead_list_with_customer_data: {str(e)}")
		# Fallback to regular query if join fails
		return frappe.get_list(
			"CRM Lead",
			fields=rows,
			filters=filters,
			order_by=order_by,
			page_length=page_length,
			start=start,
		) or []
