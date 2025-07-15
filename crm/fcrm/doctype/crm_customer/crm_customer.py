# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr


class CRMCustomer(Document):
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
        """Auto-generate customer name if not provided"""
        if not self.customer_name:
            if self.first_name:
                name_parts = [self.first_name]
                if self.middle_name:
                    name_parts.append(self.middle_name)
                if self.last_name:
                    name_parts.append(self.last_name)
                self.customer_name = " ".join(name_parts)
            elif self.mobile_no:
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

    def after_insert(self):
        """Actions after creating a new customer"""
        pass


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
         "mobile_no", "organization", "status", "customer_source"],
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