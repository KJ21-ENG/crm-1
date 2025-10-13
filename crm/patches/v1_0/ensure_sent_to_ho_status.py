import frappe

def execute():
    """
    Simple patch to ensure 'Sent to HO' status exists with correct name and lead_status
    - If status exists: update both name and lead_status fields
    - If status doesn't exist: create new status
    """
    
    try:
        print("🔧 Starting simple patch: Ensure 'Sent to HO' status exists with correct fields")
        
        # Check if 'Sent to HO' status already exists
        existing_status = frappe.db.get_value("CRM Lead Status", 
            filters={"lead_status": "Sent to HO"}, 
            fieldname="name"
        )
        
        if existing_status:
            print(f"✅ Found existing 'Sent to HO' status: {existing_status}")
            
            # Update the name field to match lead_status if needed
            if existing_status != "Sent to HO":
                print(f"   → Updating name from '{existing_status}' to 'Sent to HO'")
                
                # Get the document details
                doc = frappe.get_doc("CRM Lead Status", existing_status)
                
                # Create new document with correct name
                new_doc = frappe.new_doc("CRM Lead Status")
                new_doc.lead_status = "Sent to HO"
                new_doc.color = doc.color
                new_doc.position = doc.position
                new_doc.insert()
                
                # Delete the old document
                frappe.delete_doc("CRM Lead Status", existing_status)
                print(f"   ✅ Renamed document to 'Sent to HO'")
            else:
                print("   ✅ Name field is already correct")
                
        else:
            print("❌ 'Sent to HO' status not found, creating new one")
            
            # Create new 'Sent to HO' status
            new_doc = frappe.new_doc("CRM Lead Status")
            new_doc.lead_status = "Sent to HO"
            new_doc.color = "purple"
            new_doc.position = 5
            new_doc.insert()
            print("✅ Created new 'Sent to HO' status")
        
        # Update any leads that still have the old status
        leads_with_old_status = frappe.get_all("CRM Lead", 
            filters={"status": "Sent to Bangalore"}, 
            fields=["name", "status"]
        )
        
        if leads_with_old_status:
            print(f"🔄 Found {len(leads_with_old_status)} leads with 'Sent to Bangalore' status")
            for lead in leads_with_old_status:
                frappe.db.set_value("CRM Lead", lead.name, "status", "Sent to HO")
            
            print(f"✅ Updated {len(leads_with_old_status)} leads from 'Sent to Bangalore' to 'Sent to HO'")
        else:
            print("ℹ️  No leads found with 'Sent to Bangalore' status")
        
        # Commit all changes
        frappe.db.commit()
        print("✅ All changes committed successfully!")
        
        # Final verification
        final_status = frappe.db.get_value("CRM Lead Status", 
            filters={"lead_status": "Sent to HO"}, 
            fieldname="name"
        )
        
        if final_status:
            print(f"✅ Final verification: 'Sent to HO' status exists with name: {final_status}")
            
            # Show the status details
            status_doc = frappe.get_doc("CRM Lead Status", final_status)
            print(f"   Status: {status_doc.lead_status}")
            print(f"   Color: {status_doc.color}")
            print(f"   Position: {status_doc.position}")
        else:
            print("❌ Final verification failed: 'Sent to HO' status not found")
            
    except Exception as e:
        print(f"❌ Error in patch: {str(e)}")
        frappe.log_error(f"Patch ensure_sent_to_ho_status failed: {str(e)}")
        frappe.db.rollback()
        raise

def rollback():
    """
    Rollback the patch by changing 'Sent to HO' back to 'Sent to Bangalore'
    """
    try:
        print("🔄 Rolling back patch: 'Sent to HO' to 'Sent to Bangalore'")
        
        # Find the 'Sent to HO' status
        ho_status = frappe.db.get_value("CRM Lead Status", 
            filters={"lead_status": "Sent to HO"}, 
            fieldname="name"
        )
        
        if ho_status:
            # Get the document details
            doc = frappe.get_doc("CRM Lead Status", ho_status)
            
            # Create new document with 'Sent to Bangalore' name
            new_doc = frappe.new_doc("CRM Lead Status")
            new_doc.lead_status = "Sent to Bangalore"
            new_doc.color = doc.color
            new_doc.position = doc.position
            new_doc.insert()
            
            # Delete the old document
            frappe.delete_doc("CRM Lead Status", ho_status)
            print("✅ Rolled back 'Sent to HO' status to 'Sent to Bangalore'")
        else:
            print("❌ 'Sent to HO' status not found for rollback")
        
        # Update leads back to old status
        leads_with_ho_status = frappe.get_all("CRM Lead", 
            filters={"status": "Sent to HO"}, 
            fields=["name", "status"]
        )
        
        if leads_with_ho_status:
            for lead in leads_with_ho_status:
                frappe.db.set_value("CRM Lead", lead.name, "status", "Sent to Bangalore")
            
            print(f"✅ Rolled back {len(leads_with_ho_status)} leads from 'Sent to HO' to 'Sent to Bangalore'")
        else:
            print("ℹ️  No leads found with 'Sent to HO' status for rollback")
        
        # Commit rollback changes
        frappe.db.commit()
        print("✅ Rollback completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in rollback: {str(e)}")
        frappe.log_error(f"Patch ensure_sent_to_ho_status rollback failed: {str(e)}")
        frappe.db.rollback()
        raise
