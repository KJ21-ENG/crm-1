# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FCRMNote(Document):
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Title",
				"type": "Data",
				"key": "title",
				"width": "20rem",
			},
			{
				"label": "Content",
				"type": "Text Editor",
				"key": "content",
				"width": "30rem",
			},
		]
		rows = [
			"name",
			"title",
			"content",
			"reference_doctype",
			"reference_docname",
			"owner",
			"modified",
		]
		return {'columns': columns, 'rows': rows}
