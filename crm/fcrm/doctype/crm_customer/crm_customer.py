# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, now, now_datetime


class CRMCustomer(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_values = None
    
    def validate(self):
        """Validate customer data before saving"""
        self.validate_mobile_number()
        self.set_customer_name()
        self.validate_email()

    def validate_mobile_number(self):
        """Ensure mobile number is unique and valid"""
        if self.mobile_no:
            # Check for duplicate mobile numbers
            existing_customer = frappe.db.get_value(
                "CRM Customer", 
                {"mobile_no": self.mobile_no, "name": ["!=", self.name]}, 
                "name"
            )
            if existing_customer:
                frappe.throw(_("Customer with mobile number {0} already exists").format(self.mobile_no))

    def set_customer_name(self):
        """Auto-generate customer name from first/last names"""
        if self.first_name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            if self.last_name:
                name_parts.append(self.last_name)
            self.customer_name = " ".join(name_parts)
        elif not self.customer_name:
            # Only set default if customer_name is empty
            if self.mobile_no:
                self.customer_name = f"Customer {self.mobile_no}"
            else:
                frappe.throw(_("Customer Name is required"))

    def validate_email(self):
        """Validate email format"""
        if self.email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email):
                frappe.throw(_("Please enter a valid email address"))

    def before_save(self):
        """Actions before saving the document"""
        # Ensure status is set
        if not self.status:
            self.status = "Active"
            
        # Store original values before saving for change detection
        if not self.is_new():
            self._store_original_values()

    def after_insert(self):
        """Actions after creating a new customer"""
        pass  # Frappe automatically tracks creation in Version table
        
    def on_update(self):
        """Track changes and update related records when customer is updated"""
        if not self.is_new() and self._original_values:
            changes = self.get_field_changes()
            if changes:
                # Debug: Log what fields changed
                frappe.logger().info(f"Customer {self.name} field changes detected: {changes}")
                
                # Update related leads and tickets
                self.update_related_records(changes)
                # Frappe automatically tracks changes in Version table
            else:
                frappe.logger().info(f"Customer {self.name} updated but no tracked field changes detected")
                
    def _store_original_values(self):
        """Store original field values before changes"""
        sync_fields = [
            'customer_name', 'first_name', 'last_name', 'middle_name', 'email', 
            'mobile_no', 'organization', 'phone', 'job_title',
            'salutation', 'gender', 'pan_card_number', 'aadhaar_card_number'
        ]
        
        # Get current values from database
        if frappe.db.exists("CRM Customer", self.name):
            db_doc = frappe.db.get_value(
                "CRM Customer", 
                self.name, 
                sync_fields,
                as_dict=True
            )
            self._original_values = db_doc or {}
    
    def get_field_changes(self):
        """Get list of fields that have changed"""
        if not self._original_values:
            return {}
            
        # Fields that should be synchronized across lead/ticket
        sync_fields = [
            'customer_name', 'first_name', 'last_name', 'middle_name', 'email', 
            'mobile_no', 'organization', 'phone', 'job_title',
            'salutation', 'gender', 'pan_card_number', 'aadhaar_card_number'
        ]
        
        changes = {}
        for field in sync_fields:
            old_value = self._original_values.get(field)
            new_value = getattr(self, field, None)
            
            if old_value != new_value:
                changes[field] = {
                    'old_value': old_value,
                    'new_value': new_value
                }
        
        return changes
    
    def update_related_records(self, changes):
        """Update related leads and tickets with the same changes"""
        if not changes:
            return
            
        updated_records = []
        
        # Find and update related leads using ORIGINAL contact info
        leads = self.get_related_leads_by_original_contact()
        for lead in leads:
            try:
                lead_doc = frappe.get_doc("CRM Lead", lead.name)
                lead_updated = False
                
                for field, change in changes.items():
                    # Map customer_name to lead_name for leads
                    target_field = 'lead_name' if field == 'customer_name' else field
                    if hasattr(lead_doc, target_field) and getattr(lead_doc, target_field) != change['new_value']:
                        setattr(lead_doc, target_field, change['new_value'])
                        lead_updated = True
                
                if lead_updated:
                    lead_doc.save(ignore_permissions=True)
                    updated_records.append(f"CRM Lead: {lead.name}")
                    
            except Exception as e:
                frappe.log_error(f"Failed to update lead {lead.name}: {str(e)}", "Customer Update Error")
        
        # Find and update related tickets using ORIGINAL contact info
        tickets = self.get_related_tickets_by_original_contact()
        for ticket in tickets:
            try:
                ticket_doc = frappe.get_doc("CRM Ticket", ticket.name)
                ticket_updated = False
                
                for field, change in changes.items():
                    # For tickets, customer_name maps to customer_name field directly
                    if hasattr(ticket_doc, field) and getattr(ticket_doc, field) != change['new_value']:
                        setattr(ticket_doc, field, change['new_value'])
                        ticket_updated = True
                
                if ticket_updated:
                    ticket_doc.save(ignore_permissions=True)
                    updated_records.append(f"CRM Ticket: {ticket.name}")
                    
            except Exception as e:
                frappe.log_error(f"Failed to update ticket {ticket.name}: {str(e)}", "Customer Update Error")
        
        # Log which records were updated
        if updated_records:
            frappe.msgprint(f"Updated related records: {', '.join(updated_records)}")
    
    def get_related_leads_by_original_contact(self):
        """Get all leads related to this customer using ORIGINAL contact info"""
        if not self._original_values:
            return self.get_related_leads()  # Fallback to current values
            
        # Use original mobile_no and email for matching
        original_mobile = self._original_values.get('mobile_no')
        original_email = self._original_values.get('email')
        
        if not original_mobile and not original_email:
            return []
            
        # Build OR filters properly
        or_filters = []
        if original_mobile:
            or_filters.append(["mobile_no", "=", original_mobile])
        if original_email:
            or_filters.append(["email", "=", original_email])
            
        leads = frappe.get_list(
            "CRM Lead",
            filters=or_filters,
            fields=["name", "lead_name", "mobile_no", "email"]
        )
        
        return leads
    
    def get_related_tickets_by_original_contact(self):
        """Get all tickets related to this customer using ORIGINAL contact info"""
        if not self._original_values:
            return self.get_related_tickets()  # Fallback to current values
            
        # Use original mobile_no and email for matching
        original_mobile = self._original_values.get('mobile_no')
        original_email = self._original_values.get('email')
        
        if not original_mobile and not original_email:
            return []
            
        # Build OR filters properly
        or_filters = []
        if original_mobile:
            or_filters.append(["mobile_no", "=", original_mobile])
        if original_email:
            or_filters.append(["email", "=", original_email])
            
        tickets = frappe.get_list(
            "CRM Ticket",
            filters=or_filters,
            fields=["name", "ticket_subject", "mobile_no", "email"]
        )
        
        return tickets
    
    def get_related_leads(self):
        """Get all leads related to this customer by mobile number or email"""
        if not self.mobile_no and not self.email:
            return []
            
        # Build OR filters properly
        or_filters = []
        if self.mobile_no:
            or_filters.append(["mobile_no", "=", self.mobile_no])
        if self.email:
            or_filters.append(["email", "=", self.email])
        
        leads = frappe.get_list(
            "CRM Lead",
            filters=or_filters,
            fields=["name", "lead_name", "mobile_no", "email"]
        )
        
        return leads
    
    def get_related_tickets(self):
        """Get all tickets related to this customer by mobile number or email"""
        if not self.mobile_no and not self.email:
            return []
            
        # Build OR filters properly
        or_filters = []
        if self.mobile_no:
            or_filters.append(["mobile_no", "=", self.mobile_no])
        if self.email:
            or_filters.append(["email", "=", self.email])
        
        tickets = frappe.get_list(
            "CRM Ticket",
            filters=or_filters,
            fields=["name", "ticket_subject", "mobile_no", "email"]
        )
        
        return tickets
    

    



@frappe.whitelist()
def get_customer_list(limit=20, start=0, search_term=""):
    """Get paginated customer list with search"""
    filters = {"status": "Active"}
    
    if search_term:
        filters.update({
            "customer_name": ["like", f"%{search_term}%"]
        })
    
    customers = frappe.get_list(
        "CRM Customer",
        filters=filters,
        fields=["name", "customer_name", "first_name", "last_name", "email", 
               "mobile_no", "organization", "customer_source", "creation"],
        order_by="creation desc",
        limit=limit,
        start=start
    )
    
    return customers


@frappe.whitelist()
def get_customer_by_mobile(mobile_no):
    """Get customer details by mobile number"""
    if not mobile_no:
        return None
    
    customer = frappe.db.get_value(
        "CRM Customer",
        {"mobile_no": mobile_no},
        ["name", "customer_name", "first_name", "last_name", "email", 
         "mobile_no", "organization", "status", "customer_source",
         "pan_card_number", "aadhaar_card_number", "referral_code"],
        as_dict=True
    )
    
    return customer


@frappe.whitelist()
def update_customer_data(mobile_no, **customer_data):
    """Update existing customer data"""
    existing_customer = get_customer_by_mobile(mobile_no)
    
    if not existing_customer:
        frappe.throw(_("Customer with mobile number {0} not found").format(mobile_no))
    
    # Update customer record
    customer_doc = frappe.get_doc("CRM Customer", existing_customer.name)
    
    # Update fields if provided
    for field, value in customer_data.items():
        if value and hasattr(customer_doc, field):
            setattr(customer_doc, field, value)
    
    customer_doc.save()
    
    return {
        "name": customer_doc.name,
        "message": "Customer updated successfully"
    }


@frappe.whitelist()
def create_customer_from_lead_or_ticket(mobile_no, first_name=None, last_name=None,
                                       email=None, organization=None, job_title=None,
                                       customer_source="Lead", reference_doctype=None,
                                       reference_docname=None, **kwargs):
    """Create new customer from lead or ticket data"""
    try:
        # Create customer document
        customer_doc = frappe.new_doc("CRM Customer")
        customer_doc.mobile_no = mobile_no
        customer_doc.first_name = first_name or ""
        customer_doc.last_name = last_name or ""
        customer_doc.email = email
        customer_doc.organization = organization
        customer_doc.job_title = job_title
        customer_doc.customer_source = customer_source
        customer_doc.status = "Active"
        
        # Set reference fields if provided
        if reference_doctype and reference_docname:
            if reference_doctype == "CRM Lead":
                customer_doc.created_from_lead = reference_docname
            elif reference_doctype == "CRM Ticket":
                customer_doc.created_from_ticket = reference_docname
        
        # Set any additional fields
        for field, value in kwargs.items():
            if value and hasattr(customer_doc, field):
                setattr(customer_doc, field, value)
        
        customer_doc.insert()
        
        return {
            "name": customer_doc.name,
            "message": "Customer created successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Failed to create customer: {str(e)}", "Customer Creation Error")
        frappe.throw(_("Failed to create customer: {0}").format(str(e)))


@frappe.whitelist()
def test_customer_sync(customer_name):
    """Test API to demonstrate the customer synchronization feature"""
    try:
        customer_doc = frappe.get_doc("CRM Customer", customer_name)
        
        # Get related leads and tickets before update
        leads_before = customer_doc.get_related_leads()
        tickets_before = customer_doc.get_related_tickets()
        
        result = {
            "customer": {
                "name": customer_doc.name,
                "customer_name": customer_doc.customer_name,
                "mobile_no": customer_doc.mobile_no,
                "email": customer_doc.email
            },
            "related_leads": [{"name": lead.name, "lead_name": lead.lead_name} for lead in leads_before],
            "related_tickets": [{"name": ticket.name, "ticket_subject": ticket.ticket_subject} for ticket in tickets_before],
            "message": f"Found {len(leads_before)} leads and {len(tickets_before)} tickets linked to this customer"
        }
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Test customer sync failed: {str(e)}", "Customer Sync Test Error")
        frappe.throw(_("Test failed: {0}").format(str(e)))


@frappe.whitelist()
def get_customer_update_history(customer_name):
    """Get the update history for a customer using Frappe's built-in versioning"""
    try:
        # Get all versions for this customer
        versions = frappe.get_all(
            "Version",
            filters={
                "ref_doctype": "CRM Customer",
                "docname": customer_name
            },
            fields=["name", "creation", "modified_by", "data"],
            order_by="creation desc"
        )
        
        history = []
        for version in versions:
            try:
                if version.data:
                    version_data = json.loads(version.data)
                    changes = version_data.get("changed", [])
                    
                    # Format changes into readable format
                    formatted_changes = {}
                    for change in changes:
                        if len(change) >= 3:
                            field_name = change[0]
                            old_value = change[1]
                            new_value = change[2]
                            formatted_changes[field_name] = {
                                "old_value": old_value,
                                "new_value": new_value
                            }
                    
                    if formatted_changes:  # Only include versions with actual changes
                        history.append({
                            "timestamp": version.creation.strftime("%Y-%m-%d %H:%M:%S"),
                            "user": version.modified_by,
                            "action": "Customer updated",
                            "changes": formatted_changes
                        })
                        
            except (json.JSONDecodeError, TypeError) as e:
                frappe.logger().error(f"Failed to parse version data for {version.name}: {str(e)}")
                continue
        
        return {
            "customer": customer_name,
            "history": history,
            "total_versions": len(versions)
        }
            
    except Exception as e:
        frappe.throw(_("Failed to get update history: {0}").format(str(e)))


 