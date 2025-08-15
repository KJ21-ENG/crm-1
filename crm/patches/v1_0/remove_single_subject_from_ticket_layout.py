import json
import frappe


def _remove_field(layout_json: str, fieldname: str) -> str:
	if not layout_json:
		return layout_json
	try:
		data = json.loads(layout_json)
	except Exception:
		return layout_json

	changed = False

	def process_sections(sections):
		nonlocal changed
		for section in sections or []:
			for column in (section.get("columns") or []):
				fields = column.get("fields") or []
				if fieldname in fields:
					fields = [f for f in fields if f != fieldname]
					column["fields"] = fields
					changed = True

	# Support tabs and simple sections
	if isinstance(data, list):
		if data and isinstance(data[0], dict) and "sections" in data[0]:
			for tab in data:
				process_sections(tab.get("sections") or [])
		else:
			process_sections(data)

	return json.dumps(data) if changed else layout_json


def execute():
	for layout_type in ["Quick Entry", "Data Fields", "Side Panel"]:
		if not frappe.db.exists("CRM Fields Layout", {"dt": "CRM Ticket", "type": layout_type}):
			continue
		doc = frappe.get_doc("CRM Fields Layout", {"dt": "CRM Ticket", "type": layout_type})
		new_layout = _remove_field(doc.layout or "", "ticket_subject")
		if new_layout != (doc.layout or ""):
			doc.layout = new_layout
			doc.save(ignore_permissions=True)

