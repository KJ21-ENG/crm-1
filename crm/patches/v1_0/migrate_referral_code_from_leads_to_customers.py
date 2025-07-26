import frappe

def execute():
    """Migrate referral_code data from leads to customers"""
    
    print("🔄 Starting referral_code migration from leads to customers...")
    
    # Get all leads that have referral_code and mobile_no
    leads_with_referral = frappe.get_all(
        "CRM Lead",
        filters={
            "referral_code": ["!=", ""],
            "referral_code": ["is", "set"],
            "mobile_no": ["!=", ""],
            "mobile_no": ["is", "set"]
        },
        fields=["name", "mobile_no", "referral_code"]
    )
    
    print(f"📊 Found {len(leads_with_referral)} leads with referral codes")
    
    migrated_count = 0
    skipped_count = 0
    
    for lead in leads_with_referral:
        try:
            # Find the corresponding customer by mobile number
            customer = frappe.db.get_value(
                "CRM Customer",
                {"mobile_no": lead.mobile_no},
                ["name", "referral_code"],
                as_dict=True
            )
            
            if customer:
                # Check if customer already has a referral_code
                if not customer.referral_code:
                    # Update customer with referral_code from lead
                    frappe.db.set_value(
                        "CRM Customer",
                        customer.name,
                        "referral_code",
                        lead.referral_code
                    )
                    migrated_count += 1
                    print(f"✅ Migrated referral_code '{lead.referral_code}' from lead {lead.name} to customer {customer.name}")
                else:
                    skipped_count += 1
                    print(f"⏭️ Skipped customer {customer.name} - already has referral_code '{customer.referral_code}'")
            else:
                print(f"⚠️ No customer found for mobile number {lead.mobile_no} from lead {lead.name}")
                
        except Exception as e:
            print(f"❌ Error migrating referral_code for lead {lead.name}: {str(e)}")
    
    print(f"🎉 Migration completed!")
    print(f"   ✅ Successfully migrated: {migrated_count}")
    print(f"   ⏭️ Skipped (already exists): {skipped_count}")
    print(f"   📊 Total processed: {len(leads_with_referral)}") 