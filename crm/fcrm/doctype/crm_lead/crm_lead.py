# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as assign
from frappe.model.document import Document
from frappe.utils import has_gravatar, validate_email_address

from crm.fcrm.doctype.crm_service_level_agreement.utils import get_sla
from crm.fcrm.doctype.crm_status_change_log.crm_status_change_log import (
	add_status_change_log,
)
from crm.api.activities import emit_activity_update
from crm.api.lead_notifications import handle_lead_assignment_change
from crm.fcrm.utils.validation import validate_identity_documents


class CRMLead(Document):
	def before_validate(self):
		self.set_sla()
		self.set_default_referral_code()

	def validate(self):
		self.set_full_name()
		self.set_lead_name()
		self.set_title()
		# Skip customer-info validations when using centralized customer store
		if not getattr(self, "customer_id", None):
			self.validate_email()
			validate_identity_documents(self)
		if not self.is_new() and self.has_value_changed("lead_owner") and self.lead_owner:
			self.share_with_agent(self.lead_owner)
			self.assign_agent(self.lead_owner)
		if self.has_value_changed("status"):
			add_status_change_log(self)
		
		# 🔔 Send lead assignment notification for lead owner changes
		handle_lead_assignment_change(self, method="validate")

	def after_insert(self):
		if self.lead_owner:
			self.assign_agent(self.lead_owner)
		
		# Create or update customer record
		self.create_or_update_customer()
		# If a customer is linked and their created_from_lead is empty, set it to this lead
		try:
			if getattr(self, "customer_id", None):
				current_val = frappe.db.get_value("CRM Customer", self.customer_id, "created_from_lead")
				if not current_val:
					frappe.db.set_value("CRM Customer", self.customer_id, "created_from_lead", self.name)
		except Exception:
			# non-fatal
			pass
		
		emit_activity_update("CRM Lead", self.name)
		
		# 🔔 Send lead assignment notification for new leads
		handle_lead_assignment_change(self, method="after_insert")

	def on_update(self):
		# No longer sync customer-related field changes since we're not storing duplicate data
		# Customer data is now managed only in the customer table
		emit_activity_update("CRM Lead", self.name)

	def before_save(self):
		self.apply_sla()

	def set_full_name(self):
		"""Set full name from customer data if available, otherwise use lead-specific data"""
		if self.customer_id:
			# Try to get customer data
			customer_data = self.get_customer_data()
			if customer_data:
				self.lead_name = " ".join(
					filter(
						None,
						[
							customer_data.get('salutation'),
							customer_data.get('first_name'),
							customer_data.get('middle_name'),
							customer_data.get('last_name'),
						],
					)
				)
				return
		
		# Fallback to lead-specific data if no customer data available
		if self.first_name:
			self.lead_name = " ".join(
				filter(
					None,
					[
						self.salutation,
						self.first_name,
						self.middle_name,
						self.last_name,
					],
				)
			)

	def set_lead_name(self):
		if not self.lead_name:
			# When linked to a customer, do not enforce person/org name locally
			if (
				not getattr(self, "customer_id", None)
				and not self.organization
				and not self.email
				and not self.flags.ignore_mandatory
			):
				frappe.throw(_("A Lead requires either a person's name or an organization's name"))
			elif self.organization:
				self.lead_name = self.organization
			elif self.email:
				self.lead_name = self.email.split("@")[0]
			else:
				self.lead_name = "Unnamed Lead"

	def set_title(self):
		self.title = self.organization or self.lead_name

	def validate_email(self):
		if self.email:
			if not self.flags.ignore_email_validation:
				validate_email_address(self.email, throw=True)

			if self.email == self.lead_owner:
				frappe.throw(_("Lead Owner cannot be same as the Lead Email Address"))

			if self.is_new() or not self.image:
				self.image = has_gravatar(self.email)

	def assign_agent(self, agent):
		if not agent:
			return

		assignees = self.get_assigned_users()
		if assignees:
			for assignee in assignees:
				if agent == assignee:
					# the agent is already set as an assignee
					return

		# Update the assign_to field with the assigned user's name
		self.assign_to = agent
		
		assign({"assign_to": [agent], "doctype": "CRM Lead", "name": self.name})

	def share_with_agent(self, agent):
		if not agent:
			return

		docshares = frappe.get_all(
			"DocShare",
			filters={"share_name": self.name, "share_doctype": self.doctype},
			fields=["name", "user"],
		)

		shared_with = [d.user for d in docshares] + [agent]

		for user in shared_with:
			if user == agent and not frappe.db.exists(
				"DocShare",
				{"user": agent, "share_name": self.name, "share_doctype": self.doctype},
			):
				frappe.share.add_docshare(
					self.doctype,
					self.name,
					agent,
					write=1,
					flags={"ignore_share_permission": True},
				)
			elif user != agent:
				frappe.share.remove(self.doctype, self.name, user)

	def on_trash(self):
		"""Custom delete logic to handle customer unlinking before deletion"""
		try:
			# Log all linked documents before deletion
			self._log_deletion_blockers()
			
			# Unlink customer before deletion to prevent LinkExistsError
			if self.customer_id:
				frappe.db.set_value("CRM Lead", self.name, "customer_id", None)
				frappe.db.commit()
				frappe.logger().info(f"✅ Unlinked customer {self.customer_id} from lead {self.name}")
			else:
				frappe.logger().info(f"ℹ️ No customer linked to lead {self.name}")
				
		except Exception as e:
			frappe.log_error(f"❌ Error unlinking customer from lead {self.name}: {str(e)}")
			# Don't raise the exception, let deletion continue

	def _log_deletion_blockers(self):
		"""Log all potential blockers for deletion"""
		try:
			from crm.utils import get_linked_docs, get_dynamic_linked_docs
			
			# Get all linked documents
			linked_docs = get_linked_docs(self) + get_dynamic_linked_docs(self)
			
			frappe.logger().info(f"🔍 Checking deletion blockers for lead {self.name}:")
			
			if not linked_docs:
				frappe.logger().info("✅ No linked documents found - deletion should proceed")
				return
			
			# Group by doctype
			blockers_by_type = {}
			for doc in linked_docs:
				doctype = doc.get("reference_doctype") or doc.get("link_dt")
				if doctype not in blockers_by_type:
					blockers_by_type[doctype] = []
				blockers_by_type[doctype].append(doc)
			
			# Log each type of blocker
			for doctype, docs in blockers_by_type.items():
				frappe.logger().info(f"📋 Found {len(docs)} {doctype} documents linked to lead {self.name}")
				for doc in docs[:5]:  # Show first 5
					docname = doc.get("reference_docname") or doc.get("doc")
					frappe.logger().info(f"   - {doctype}: {docname}")
				if len(docs) > 5:
					frappe.logger().info(f"   ... and {len(docs) - 5} more")
			
			# Check for specific problematic links
			problematic_links = []
			for doc in linked_docs:
				doctype = doc.get("reference_doctype") or doc.get("link_dt")
				if doctype in ["CRM Customer"]:
					problematic_links.append(f"{doctype} (will be unlinked)")
				elif doctype not in ["Communication", "Comment", "File", "FCRM Note", "CRM Task", "CRM Notification", "CRM Assignment Request", "CRM Call Log", "WhatsApp Message"]:
					problematic_links.append(f"{doctype} (may block deletion)")
			
			if problematic_links:
				frappe.logger().warning(f"⚠️ Potentially problematic links: {', '.join(problematic_links)}")
			else:
				frappe.logger().info("✅ All linked documents are safe to delete/unlink")
				
		except Exception as e:
			frappe.log_error(f"Error checking deletion blockers for lead {self.name}: {str(e)}")

	def create_or_update_customer(self):
		"""Create or update customer record based on lead data"""
		if not self.mobile_no:
			return
		
		try:
			# Import the customer API function
			from crm.api.customers import create_or_update_customer
			
			# Only pass customer-specific data to customer creation
			customer_result = create_or_update_customer(
				mobile_no=self.mobile_no,
				first_name=self.first_name,
				last_name=self.last_name,
				email=self.email,
				organization=self.organization,
				job_title=self.job_title,
				alternative_mobile_no=self.alternative_mobile_no,
				pan_card_number=self.pan_card_number,
				aadhaar_card_number=self.aadhaar_card_number,
				referral_through=self.referral_through,
				marital_status=self.marital_status,
				date_of_birth=self.date_of_birth,
				anniversary=self.anniversary,
				customer_source="Lead",
				reference_doctype="CRM Lead",
				reference_docname=self.name
			)
			
			# Update the customer_id field with the customer name using db.set_value to avoid activity log
			if customer_result and customer_result.get("name"):
				frappe.db.set_value("CRM Lead", self.name, "customer_id", customer_result["name"])
				# Update the instance variable to keep it in sync
				self.customer_id = customer_result["name"]
				
				# Clear customer-specific fields from lead table to avoid duplication
				customer_fields_to_clear = [
					'first_name', 'last_name', 'middle_name', 'email', 'mobile_no', 
					'phone', 'salutation', 'gender', 'organization', 'job_title',
					'pan_card_number', 'aadhaar_card_number', 'image', 'lead_name',
					'marital_status', 'date_of_birth', 'anniversary'
				]
				
				for field in customer_fields_to_clear:
					if hasattr(self, field):
						frappe.db.set_value("CRM Lead", self.name, field, None)
						setattr(self, field, None)
			
			frappe.logger().info(f"Customer record processed for lead {self.name}: {customer_result}")
			
		except Exception as e:
			# Log error but don't fail the lead creation
			frappe.log_error(f"Error creating/updating customer for lead {self.name}: {str(e)}", "Customer Creation Error")
			frappe.logger().error(f"Customer creation failed for lead {self.name}: {str(e)}")

	def get_customer_data(self):
		"""Get customer data from customer table using customer_id"""
		if not self.customer_id:
			return None
		
		try:
			from crm.api.customers import get_customer_by_id
			return get_customer_by_id(self.customer_id)
		except Exception as e:
			frappe.log_error(f"Error fetching customer data for lead {self.name}: {str(e)}", "Customer Data Fetch Error")
			return None

	def create_contact(self, existing_contact=None, throw=True):
		if not self.lead_name:
			self.set_full_name()
			self.set_lead_name()

		existing_contact = existing_contact or self.contact_exists(throw)
		if existing_contact:
			self.update_lead_contact(existing_contact)
			return existing_contact

		contact = frappe.new_doc("Contact")
		contact.update(
			{
				"first_name": self.first_name or self.lead_name,
				"last_name": self.last_name,
				"salutation": self.salutation,
				"gender": self.gender,
				"designation": self.job_title,
				"company_name": self.organization,
				"image": self.image or "",
			}
		)

		if self.email:
			contact.append("email_ids", {"email_id": self.email, "is_primary": 1})

		if self.phone:
			contact.append("phone_nos", {"phone": self.phone, "is_primary_phone": 1})

		if self.mobile_no:
			contact.append("phone_nos", {"phone": self.mobile_no, "is_primary_mobile_no": 1})

		contact.insert(ignore_permissions=True)
		contact.reload()  # load changes by hooks on contact

		return contact.name

	def create_organization(self, existing_organization=None):
		if not self.organization and not existing_organization:
			return

		existing_organization = existing_organization or frappe.db.exists(
			"CRM Organization", {"organization_name": self.organization}
		)
		if existing_organization:
			self.db_set("organization", existing_organization)
			return existing_organization

		organization = frappe.new_doc("CRM Organization")
		organization.update(
			{
				"organization_name": self.organization,
				"website": self.website,
				"territory": self.territory,
				"industry": self.industry,
				"annual_revenue": self.annual_revenue,
			}
		)
		organization.insert(ignore_permissions=True)
		return organization.name

	def update_lead_contact(self, contact):
		contact = frappe.get_cached_doc("Contact", contact)
		frappe.db.set_value(
			"CRM Lead",
			self.name,
			{
				"salutation": contact.salutation,
				"first_name": contact.first_name,
				"last_name": contact.last_name,
				"email": contact.email_id,
				"mobile_no": contact.mobile_no,
			},
		)

	def contact_exists(self, throw=True):
		email_exist = frappe.db.exists("Contact Email", {"email_id": self.email})
		phone_exist = frappe.db.exists("Contact Phone", {"phone": self.phone})
		mobile_exist = frappe.db.exists("Contact Phone", {"phone": self.mobile_no})

		doctype = "Contact Email" if email_exist else "Contact Phone"
		name = email_exist or phone_exist or mobile_exist

		if name:
			text = "Email" if email_exist else "Phone" if phone_exist else "Mobile No"
			data = self.email if email_exist else self.phone if phone_exist else self.mobile_no

			value = "{0}: {1}".format(text, data)

			contact = frappe.db.get_value(doctype, name, "parent")

			if throw:
				frappe.throw(
					_("Contact already exists with {0}").format(value),
					title=_("Contact Already Exists"),
				)
			return contact

		return False

	def create_deal(self, contact, organization, deal=None):
		new_deal = frappe.new_doc("CRM Deal")

		lead_deal_map = {
			"lead_owner": "deal_owner",
		}

		restricted_fieldtypes = [
			"Tab Break",
			"Section Break",
			"Column Break",
			"HTML",
			"Button",
			"Attach",
		]
		restricted_map_fields = [
			"name",
			"naming_series",
			"creation",
			"owner",
			"modified",
			"modified_by",
			"idx",
			"docstatus",
			"status",
			"email",
			"mobile_no",
			"phone",
			"sla",
			"sla_status",
			"response_by",
			"first_response_time",
			"first_responded_on",
			"communication_status",
			"sla_creation",
			"status_change_log",
		]

		for field in self.meta.fields:
			if field.fieldtype in restricted_fieldtypes:
				continue
			if field.fieldname in restricted_map_fields:
				continue

			fieldname = field.fieldname
			if field.fieldname in lead_deal_map:
				fieldname = lead_deal_map[field.fieldname]

			if hasattr(new_deal, fieldname):
				if fieldname == "organization":
					new_deal.update({fieldname: organization})
				else:
					new_deal.update({fieldname: self.get(field.fieldname)})

		new_deal.update(
			{
				"lead": self.name,
				"contacts": [{"contact": contact}],
			}
		)

		if self.first_responded_on:
			new_deal.update(
				{
					"sla_creation": self.sla_creation,
					"response_by": self.response_by,
					"sla_status": self.sla_status,
					"communication_status": self.communication_status,
					"first_response_time": self.first_response_time,
					"first_responded_on": self.first_responded_on,
				}
			)

		if deal:
			new_deal.update(deal)

		new_deal.insert(ignore_permissions=True)
		return new_deal.name

	def set_default_referral_code(self):
		"""
		Set default referral code from FCRM Settings if not already set
		"""
		if not self.referral_through:
			try:
				# Get default referral code from FCRM Settings
				fcrm_settings = frappe.get_single("FCRM Settings")
				if fcrm_settings and fcrm_settings.default_referral_code:
					self.referral_through = fcrm_settings.default_referral_code
			except Exception as e:
				# If settings not found or error, use fallback
				frappe.log_error(f"Error getting default referral code: {str(e)}")
				self.referral_through = "AUOMC"  # Fallback default

	def set_sla(self):
		"""
		Find an SLA to apply to the lead.
		"""
		if self.sla:
			return

		sla = get_sla(self)
		if not sla:
			self.first_responded_on = None
			self.first_response_time = None
			return
		self.sla = sla.name

	def apply_sla(self):
		"""
		Apply SLA if set.
		"""
		if not self.sla:
			return
		sla = frappe.get_last_doc("CRM Service Level Agreement", {"name": self.sla})
		if sla:
			sla.apply(self)

	def convert_to_deal(self, deal=None):
		return convert_to_deal(lead=self.name, doc=self, deal=deal)

	@staticmethod
	def get_non_filterable_fields():
		return ["converted"]

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Name",
				"type": "Data",
				"key": "lead_name",
				"width": "12rem",
			},
			{
				"label": "Status",
				"type": "Select",
				"key": "status",
				"width": "8rem",
			},
			{
				"label": "Email",
				"type": "Data",
				"key": "email",
				"width": "12rem",
			},
			{
				"label": "Mobile No",
				"type": "Data",
				"key": "mobile_no",
				"width": "11rem",
			},
			{
				"label": "Assigned To",
				"type": "Text",
				"key": "_assign",
				"width": "10rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = [
			"name",
			"lead_name",
			"status",
			"email",
			"mobile_no",
			"lead_owner",
			"first_name",
			"sla_status",
			"response_by",
			"first_response_time",
			"first_responded_on",
			"modified",
			"_assign",
			"image",
		]
		return {"columns": columns, "rows": rows}

	@staticmethod
	def default_kanban_settings():
		return {
			"column_field": "status",
			"title_field": "lead_name",
			"kanban_fields": '["email", "mobile_no", "_assign", "modified"]',
		}


@frappe.whitelist()
def convert_to_deal(lead, doc=None, deal=None, existing_contact=None, existing_organization=None):
	if not (doc and doc.flags.get("ignore_permissions")) and not frappe.has_permission(
		"CRM Lead", "write", lead
	):
		frappe.throw(_("Not allowed to convert Lead to Deal"), frappe.PermissionError)

	lead = frappe.get_cached_doc("CRM Lead", lead)
	if frappe.db.exists("CRM Lead Status", "Qualified"):
		lead.db_set("status", "Qualified")
	lead.db_set("converted", 1)
	if lead.sla and frappe.db.exists("CRM Communication Status", "Replied"):
		lead.db_set("communication_status", "Replied")
	contact = lead.create_contact(existing_contact, False)
	organization = lead.create_organization(existing_organization)
	_deal = lead.create_deal(contact, organization, deal)
	return _deal
