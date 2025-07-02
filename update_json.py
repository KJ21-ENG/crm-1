#!/usr/bin/env python3
import json

# Read the current JSON file
with open('./apps/crm/crm/fcrm/doctype/crm_call_log/crm_call_log.json', 'r') as f:
    data = json.load(f)

# Check if customer_name is already in field_order
if 'customer_name' not in data.get('field_order', []):
    # Find the position of 'customer' and insert 'customer_name' after it
    field_order = data.get('field_order', [])
    if 'customer' in field_order:
        customer_idx = field_order.index('customer')
        field_order.insert(customer_idx + 1, 'customer_name')
        data['field_order'] = field_order
        print("✅ Added customer_name to field_order")
    else:
        print("❌ Customer field not found in field_order")

# Check if customer_name field definition exists
customer_name_exists = False
for field in data.get('fields', []):
    if field.get('fieldname') == 'customer_name':
        customer_name_exists = True
        break

if not customer_name_exists:
    # Find the customer field and insert customer_name after it
    fields = data.get('fields', [])
    customer_field_idx = None
    
    for i, field in enumerate(fields):
        if field.get('fieldname') == 'customer':
            customer_field_idx = i
            break
    
    if customer_field_idx is not None:
        # Create the customer_name field definition
        customer_name_field = {
            "fieldname": "customer_name",
            "fieldtype": "Data", 
            "in_list_view": 1,
            "in_standard_filter": 1,
            "label": "Customer Name"
        }
        
        # Insert after customer field
        fields.insert(customer_field_idx + 1, customer_name_field)
        data['fields'] = fields
        print("✅ Added customer_name field definition")
    else:
        print("❌ Customer field not found in fields array")
else:
    print("✅ customer_name field already exists")

# Write the updated JSON back to file
with open('./apps/crm/crm/fcrm/doctype/crm_call_log/crm_call_log.json', 'w') as f:
    json.dump(data, f, indent=1)

print("🎉 JSON file updated successfully!") 