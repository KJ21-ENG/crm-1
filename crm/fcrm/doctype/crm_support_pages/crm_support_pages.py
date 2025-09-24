# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class CRMSupportPages(Document):
	def before_insert(self):
		"""Auto-populate created_by and creation_date fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now()
			
	def validate(self):
		"""Validate support link format"""
		if self.support_link:
			# Accept http(s) URLs or domain names like xyz.com
			import re
			pattern = r'^(https?://[\w\.-]+(?:/\S*)?|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
			if not re.match(pattern, self.support_link):
				frappe.throw("Support link must be a valid URL (http://, https://) or a domain name like xyz.com")
			# Check for duplicate active pages with same name
			existing = frappe.db.exists(
				'CRM Support Pages',
				{
					'page_name': self.page_name,
					'is_active': 1,
					'name': ['!=', self.name]
				}
			)
			if existing:
				frappe.throw(f"An active support page with name '{self.page_name}' already exists")


@frappe.whitelist()
def get_active_support_pages():
	"""Get all active support pages for dropdown selection"""
	pages = frappe.get_all(
		'CRM Support Pages',
		filters={'is_active': 1},
		fields=['name', 'page_name', 'support_link', 'description'],
		order_by='page_name'
	)
	return pages


@frappe.whitelist()
def get_support_page_link(page_name):
	"""Get support page link by name"""
	page = frappe.get_doc('CRM Support Pages', page_name)
	if page.is_active:
		return page.support_link
	else:
		frappe.throw("This support page is not active") 