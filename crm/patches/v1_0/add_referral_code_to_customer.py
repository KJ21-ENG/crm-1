import frappe

def execute():
    """Add referral_code field to CRM Customer DocType and database table"""
    
    # Get the CRM Customer DocType
    doc = frappe.get_doc("DocType", "CRM Customer")
    
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
        
        # Add to field_order after customer_source
        field_order = doc.field_order
        if "customer_source" in field_order:
            customer_source_index = field_order.index("customer_source")
            field_order.insert(customer_source_index + 1, "referral_code")
        else:
            # If customer_source not found, add at the end
            field_order.append("referral_code")
        
        doc.save()
        print("✅ Added referral_code field to CRM Customer DocType")
    else:
        print("ℹ️ referral_code field already exists in CRM Customer DocType")
    
    # Add the field to the database table if it doesn't exist
    try:
        # Check if the column exists in the database
        columns = frappe.db.sql("SHOW COLUMNS FROM `tabCRM Customer` LIKE 'referral_code'", as_dict=True)
        
        if not columns:
            # Add the column to the database
            frappe.db.sql("ALTER TABLE `tabCRM Customer` ADD COLUMN `referral_code` VARCHAR(140) NULL")
            print("✅ Added referral_code column to tabCRM Customer table")
        else:
            print("ℹ️ referral_code column already exists in tabCRM Customer table")
            
    except Exception as e:
        print(f"⚠️ Error adding referral_code column to database: {str(e)}")
        # Continue even if database update fails, as the DocType field is more important 