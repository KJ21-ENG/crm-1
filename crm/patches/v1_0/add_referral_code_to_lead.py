import frappe

def execute():
    """Add referral_code field to CRM Lead DocType"""
    
    # Get the CRM Lead DocType
    doc = frappe.get_doc("DocType", "CRM Lead")
    
    # Check if field already exists
    existing_field = None
    for field in doc.fields:
        if field.fieldname == "referral_code":
            existing_field = field
            break
    
    if not existing_field:
        # Add the referral_code field
        doc.append("fields", {
            "fieldname": "referral_code",
            "fieldtype": "Data",
            "label": "Referral Code",
            "description": "Enter referral code if applicable"
        })
        
        # Add to field_order after lead_source
        field_order = doc.field_order
        if "lead_source" in field_order:
            lead_source_index = field_order.index("lead_source")
            field_order.insert(lead_source_index + 1, "referral_code")
        else:
            # If lead_source not found, add at the end
            field_order.append("referral_code")
        
        doc.save()
        print("✅ Added referral_code field to CRM Lead DocType")
    else:
        print("ℹ️ referral_code field already exists in CRM Lead DocType") 