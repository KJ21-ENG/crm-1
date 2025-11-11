# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute():
    """Restructure referral system with new database schema"""
    frappe.reload_doc("fcrm", "doctype", "crm_lead")
    frappe.reload_doc("fcrm", "doctype", "crm_customer")
    
    # Update CRM Lead table
    update_lead_table()
    
    # Update CRM Customer table
    update_customer_table()
    
    # Drop old referral tracking table if exists
    drop_old_referral_table()
    
    print("✅ Referral system restructured successfully!")

def update_lead_table():
    """Add new columns to CRM Lead table"""
    try:
        # Add referral_through column
        if not frappe.db.exists("DocField", {"parent": "CRM Lead", "fieldname": "referral_through"}):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Lead` 
                ADD COLUMN `referral_through` VARCHAR(140) NULL 
                COMMENT 'Client ID used during lead creation'
            """)
            print("✅ Added referral_through column to CRM Lead")
        
        # Add account_type column
        if not frappe.db.exists("DocField", {"parent": "CRM Lead", "fieldname": "account_type"}):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Lead` 
                ADD COLUMN `account_type` VARCHAR(140) NULL 
                COMMENT 'Account type: Individual, HUF, Corporate, NRI, LLP, Minor, Partnership, Others'
            """)
            print("✅ Added account_type column to CRM Lead")
            
    except Exception as e:
        print(f"❌ Error updating CRM Lead table: {str(e)}")

def update_customer_table():
    """Update CRM Customer table"""
    try:
        # Remove old referral_code column if exists
        if frappe.db.exists("DocField", {"parent": "CRM Customer", "fieldname": "referral_code"}):
            frappe.db.sql("ALTER TABLE `tabCRM Customer` DROP COLUMN `referral_code`")
            print("✅ Removed referral_code column from CRM Customer")
        
        # Add accounts JSON column
        if not frappe.db.exists("DocField", {"parent": "CRM Customer", "fieldname": "accounts"}):
            frappe.db.sql("""
                ALTER TABLE `tabCRM Customer` 
                ADD COLUMN `accounts` JSON NULL 
                COMMENT 'Array of account objects with account_type and client_id'
            """)
            print("✅ Added accounts column to CRM Customer")
            
    except Exception as e:
        print(f"❌ Error updating CRM Customer table: {str(e)}")

def drop_old_referral_table():
    """Drop the old referral tracking table"""
    try:
        if frappe.db.exists("DocType", "CRM Referral Tracking"):
            # Drop the table
            frappe.db.sql("DROP TABLE IF EXISTS `tabCRM Referral Tracking`")
            
            # Remove the DocType
            frappe.delete_doc("DocType", "CRM Referral Tracking", force=True)
            
            print("✅ Dropped old CRM Referral Tracking table")
            
    except Exception as e:
        print(f"❌ Error dropping old referral table: {str(e)}") 