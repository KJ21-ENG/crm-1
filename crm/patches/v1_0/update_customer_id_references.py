"""
Update existing leads and tickets with customer_id references
This script will populate the customer_id field in existing leads and tickets
based on mobile number matching with customer records.
"""

import frappe

def execute():
    """Update customer_id references in existing leads and tickets"""
    
    print("🔄 Starting customer_id reference update...")
    
    # Update CRM Lead records
    update_lead_customer_references()
    
    # Update CRM Ticket records  
    update_ticket_customer_references()
    
    print("✅ Customer ID reference update completed!")

def update_lead_customer_references():
    """Update customer_id in existing CRM Lead records"""
    print("📝 Updating CRM Lead customer references...")
    
    # Get all leads that have mobile_no but no customer_id using SQL
    leads = frappe.db.sql("""
        SELECT name, mobile_no, email 
        FROM `tabCRM Lead` 
        WHERE mobile_no IS NOT NULL AND mobile_no != '' 
        AND (customer_id IS NULL OR customer_id = '')
    """, as_dict=True)
    
    updated_count = 0
    for lead in leads:
        try:
            # Find customer by mobile number
            customer = frappe.db.get_value(
                "CRM Customer",
                {"mobile_no": lead.mobile_no},
                "name"
            )
            
            if customer:
                # Update the lead with customer_id
                frappe.db.set_value("CRM Lead", lead.name, "customer_id", customer)
                updated_count += 1
                print(f"  ✅ Updated lead {lead.name} with customer {customer}")
            else:
                print(f"  ⚠️ No customer found for lead {lead.name} (mobile: {lead.mobile_no})")
                
        except Exception as e:
            print(f"  ❌ Error updating lead {lead.name}: {str(e)}")
    
    print(f"📊 Updated {updated_count} out of {len(leads)} leads")

def update_ticket_customer_references():
    """Update customer_id in existing CRM Ticket records"""
    print("🎫 Updating CRM Ticket customer references...")
    
    # Get all tickets that have mobile_no but no customer_id using SQL
    tickets = frappe.db.sql("""
        SELECT name, mobile_no, email 
        FROM `tabCRM Ticket` 
        WHERE mobile_no IS NOT NULL AND mobile_no != '' 
        AND (customer_id IS NULL OR customer_id = '')
    """, as_dict=True)
    
    updated_count = 0
    for ticket in tickets:
        try:
            # Find customer by mobile number
            customer = frappe.db.get_value(
                "CRM Customer",
                {"mobile_no": ticket.mobile_no},
                "name"
            )
            
            if customer:
                # Update the ticket with customer_id
                frappe.db.set_value("CRM Ticket", ticket.name, "customer_id", customer)
                updated_count += 1
                print(f"  ✅ Updated ticket {ticket.name} with customer {customer}")
            else:
                print(f"  ⚠️ No customer found for ticket {ticket.name} (mobile: {ticket.mobile_no})")
                
        except Exception as e:
            print(f"  ❌ Error updating ticket {ticket.name}: {str(e)}")
    
    print(f"📊 Updated {updated_count} out of {len(tickets)} tickets")

def verify_updates():
    """Verify that customer_id references are properly set"""
    print("\n🔍 Verifying customer_id references...")
    
    # Check leads
    leads_with_customer_id = frappe.db.count("CRM Lead", {"customer_id": ["is", "set"]})
    total_leads = frappe.db.count("CRM Lead")
    print(f"📝 Leads with customer_id: {leads_with_customer_id}/{total_leads}")
    
    # Check tickets
    tickets_with_customer_id = frappe.db.count("CRM Ticket", {"customer_id": ["is", "set"]})
    total_tickets = frappe.db.count("CRM Ticket")
    print(f"🎫 Tickets with customer_id: {tickets_with_customer_id}/{total_tickets}")
    
    # Check for orphaned records (customer_id pointing to non-existent customer)
    orphaned_leads = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabCRM Lead` l 
        LEFT JOIN `tabCRM Customer` c ON l.customer_id = c.name 
        WHERE l.customer_id IS NOT NULL AND c.name IS NULL
    """)[0][0]
    
    orphaned_tickets = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabCRM Ticket` t 
        LEFT JOIN `tabCRM Customer` c ON t.customer_id = c.name 
        WHERE t.customer_id IS NOT NULL AND c.name IS NULL
    """)[0][0]
    
    print(f"⚠️ Orphaned leads: {orphaned_leads}")
    print(f"⚠️ Orphaned tickets: {orphaned_tickets}")

if __name__ == "__main__":
    execute()
    verify_updates() 