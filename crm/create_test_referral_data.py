#!/usr/bin/env python3
import frappe
from frappe import _
import json
from datetime import datetime, timedelta

def create_test_referral_data():
    """Create comprehensive test data for referral analytics"""
    print("🔄 Creating test referral data...")
    
    # Clear existing test data
    clear_test_data()
    
    # Create test customers with accounts
    create_test_customers()
    
    # Create test leads with various scenarios
    create_test_leads()
    
    # Show summary
    show_referral_analytics()
    
    print("✅ Test referral data created successfully!")

def clear_test_data():
    """Clear existing test data"""
    print("🧹 Clearing existing test data...")
    
    # Delete test leads
    test_leads = frappe.get_all("CRM Lead", filters={
        "first_name": ["like", "Test Lead%"]
    })
    for lead in test_leads:
        frappe.delete_doc("CRM Lead", lead.name, force=True)
    
    # Delete test customers
    test_customers = frappe.get_all("CRM Customer", filters={
        "customer_name": ["like", "Test Customer%"]
    })
    for customer in test_customers:
        frappe.delete_doc("CRM Customer", customer.name, force=True)
    
    print(f"🗑️ Cleared {len(test_leads)} test leads and {len(test_customers)} test customers")

def create_test_customers():
    """Create test customers with accounts"""
    print("👥 Creating test customers...")
    
    customers_data = [
        {
            "customer_name": "Test Customer 1",
            "mobile_no": "9876543210",
            "email": "customer1@test.com",
            "accounts": [
                {
                    "account_type": "Individual",
                    "client_id": "CAAKED",
                    "created_on": "2024-01-15T10:00:00Z",
                    "lead_id": "LEAD-001"
                },
                {
                    "account_type": "HUF",
                    "client_id": "HUF123",
                    "created_on": "2024-02-20T14:30:00Z",
                    "lead_id": "LEAD-002"
                }
            ]
        },
        {
            "customer_name": "Test Customer 2",
            "mobile_no": "9876543211",
            "email": "customer2@test.com",
            "accounts": [
                {
                    "account_type": "Corporate",
                    "client_id": "CORP456",
                    "created_on": "2024-01-10T09:15:00Z",
                    "lead_id": "LEAD-003"
                }
            ]
        },
        {
            "customer_name": "Test Customer 3",
            "mobile_no": "9876543212", 
            "email": "customer3@test.com",
            "accounts": [
                {
                    "account_type": "NRI",
                    "client_id": "NRI789",
                    "created_on": "2024-03-05T16:45:00Z",
                    "lead_id": "LEAD-004"
                }
            ]
        }
    ]
    
    for customer_data in customers_data:
        customer = frappe.new_doc("CRM Customer")
        customer.customer_name = customer_data["customer_name"]
        customer.mobile_no = customer_data["mobile_no"]
        customer.email = customer_data["email"]
        customer.accounts = json.dumps(customer_data["accounts"])
            customer.insert(ignore_permissions=True)
        print(f"✅ Created customer: {customer.customer_name}")
    
def create_test_leads():
    """Create test leads with various referral scenarios"""
    print("📋 Creating test leads...")
    
    # Get customer accounts for referral codes
    customers = frappe.get_all("CRM Customer", fields=["name", "accounts"])
    referral_codes = []
    
    for customer in customers:
        if customer.accounts:
            try:
                accounts = json.loads(customer.accounts)
                for account in accounts:
                    referral_codes.append({
                        "client_id": account["client_id"],
                        "account_type": account["account_type"]
                    })
            except:
                continue
    
    # Create leads with different scenarios
    leads_data = [
        # Direct leads with referrals
        {
            "first_name": "Test Lead 1",
            "last_name": "Direct Referral",
            "mobile_no": "1111111111",
            "email": "lead1@test.com",
            "lead_category": "Direct",
            "referral_through": "CAAKED",
            "account_type": "Individual",
            "status": "Account Opened",
            "branch": "Mumbai",
            "creation": "2024-01-20 10:00:00"
        },
        {
            "first_name": "Test Lead 2", 
            "last_name": "Direct Referral",
            "mobile_no": "1111111112",
            "email": "lead2@test.com",
            "lead_category": "Direct",
            "referral_through": "CAAKED",
            "account_type": "HUF",
            "status": "Account Opened",
            "branch": "Delhi",
            "creation": "2024-02-25 14:30:00"
        },
        {
            "first_name": "Test Lead 3",
            "last_name": "Direct Referral",
            "mobile_no": "1111111113", 
            "email": "lead3@test.com",
            "lead_category": "Direct",
            "referral_through": "CORP456",
            "account_type": "Corporate",
            "status": "Account Opened",
            "branch": "Mumbai",
            "creation": "2024-01-15 09:15:00"
        },
        {
            "first_name": "Test Lead 4",
            "last_name": "Direct Referral",
            "mobile_no": "1111111114",
            "email": "lead4@test.com",
            "lead_category": "Direct", 
            "referral_through": "NRI789",
            "account_type": "NRI",
            "status": "Account Active",
            "branch": "Delhi",
            "creation": "2024-03-10 16:45:00"
        },
        # Indirect leads
        {
            "first_name": "Test Lead 5",
            "last_name": "Indirect Referral",
            "mobile_no": "1111111115",
            "email": "lead5@test.com",
            "lead_category": "Indirect",
            "referral_through": "CAAKED",
            "account_type": "Individual", 
            "status": "New",
            "branch": "Mumbai",
            "creation": "2024-04-01 11:00:00"
        },
        {
            "first_name": "Test Lead 6",
            "last_name": "Indirect Referral",
            "mobile_no": "1111111116",
            "email": "lead6@test.com",
            "lead_category": "Indirect",
            "referral_through": "HUF123",
            "account_type": "HUF",
            "status": "Qualified",
            "branch": "Delhi",
            "creation": "2024-04-05 15:20:00"
        },
        # Leads without referrals
        {
            "first_name": "Test Lead 7",
            "last_name": "No Referral",
            "mobile_no": "1111111117",
            "email": "lead7@test.com",
            "lead_category": "Direct",
            "referral_through": "",
            "account_type": "Individual",
            "status": "New",
            "branch": "Mumbai",
            "creation": "2024-04-10 12:00:00"
        },
        {
            "first_name": "Test Lead 8",
            "last_name": "No Referral",
            "mobile_no": "1111111118",
            "email": "lead8@test.com",
            "lead_category": "Indirect",
            "referral_through": "",
            "account_type": "Corporate",
            "status": "Qualified",
            "branch": "Delhi",
            "creation": "2024-04-12 13:30:00"
        }
    ]
    
    for lead_data in leads_data:
        lead = frappe.new_doc("CRM Lead")
        lead.first_name = lead_data["first_name"]
        lead.last_name = lead_data["last_name"]
        lead.mobile_no = lead_data["mobile_no"]
        lead.email = lead_data["email"]
        lead.lead_category = lead_data["lead_category"]
        lead.referral_through = lead_data["referral_through"]
        lead.account_type = lead_data["account_type"]
        lead.status = lead_data["status"]
        lead.branch = lead_data["branch"]
        lead.lead_source = "Website"
        lead.annual_revenue = 500000
        
        # Set creation date
        lead.creation = lead_data["creation"]
        lead.modified = lead_data["creation"]
        
            lead.insert(ignore_permissions=True)
        print(f"✅ Created lead: {lead.first_name} {lead.last_name} ({lead.status})")

def show_referral_analytics():
    """Show summary of created referral data"""
    print("\n📊 Referral Analytics Summary:")
    print("=" * 50)
    
    # Total leads with referrals
    total_leads_with_referral = frappe.db.count("CRM Lead", {
        "referral_through": ["!=", ""]
    })
    print(f"Total Leads with Referral: {total_leads_with_referral}")
    
    # Converted leads
    converted_leads = frappe.db.count("CRM Lead", {
        "referral_through": ["!=", ""],
        "status": ["in", ["Account Opened", "Account Active"]]
    })
    print(f"Converted Leads: {converted_leads}")
    
    # Conversion rate
    conversion_rate = round((converted_leads / total_leads_with_referral * 100) if total_leads_with_referral > 0 else 0, 2)
    print(f"Referral Conversion Rate: {conversion_rate}%")
    
    # Direct vs Indirect
    direct_leads = frappe.db.count("CRM Lead", {
        "lead_category": "Direct",
        "referral_through": ["!=", ""]
    })
    indirect_leads = frappe.db.count("CRM Lead", {
        "lead_category": "Indirect",
        "referral_through": ["!=", ""]
    })
    print(f"Direct Leads: {direct_leads}")
    print(f"Indirect Leads: {indirect_leads}")
    
    # Top referrers
    print("\n🏆 Top Referrers:")
    customers = frappe.get_all("CRM Customer", fields=["customer_name", "accounts"])
    for customer in customers:
        if customer.accounts:
            try:
                accounts = json.loads(customer.accounts)
                for account in accounts:
                    referral_count = frappe.db.count("CRM Lead", {
                        "referral_through": account["client_id"]
                    })
                    print(f"  {customer.customer_name} ({account['client_id']}): {referral_count} referrals")
            except:
                continue
    
    print("=" * 50)

if __name__ == "__main__":
    create_test_referral_data()