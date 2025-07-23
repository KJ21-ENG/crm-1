# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute():
    """
    Add reassignment tracking fields to CRM Task and CRM Ticket tables
    """
    try:
        # Add reassignment_processed field to CRM Task
        if not frappe.db.has_column("CRM Task", "reassignment_processed"):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Task` 
                ADD COLUMN `reassignment_processed` tinyint(1) DEFAULT 0
            """)
            frappe.logger().info("Added reassignment_processed field to CRM Task")
        
        # Add last_reassignment_at field to CRM Ticket
        if not frappe.db.has_column("CRM Ticket", "last_reassignment_at"):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Ticket` 
                ADD COLUMN `last_reassignment_at` datetime(6) NULL
            """)
            frappe.logger().info("Added last_reassignment_at field to CRM Ticket")
        
        # Add last_reassignment_at field to CRM Lead (if not exists)
        if not frappe.db.has_column("CRM Lead", "last_reassignment_at"):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Lead` 
                ADD COLUMN `last_reassignment_at` datetime(6) NULL
            """)
            frappe.logger().info("Added last_reassignment_at field to CRM Lead")
        
        frappe.db.commit()
        frappe.logger().info("Successfully added reassignment tracking fields")
        
    except Exception as e:
        frappe.logger().error(f"Error adding reassignment tracking fields: {str(e)}")
        frappe.db.rollback()
        raise