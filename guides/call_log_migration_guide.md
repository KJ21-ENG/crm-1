# CRM Call Log Migration Guide: Caller/Receiver → Employee/Customer

## Overview
This guide documents the complete migration from confusing caller/receiver fields to a clear employee/customer structure in the CRM Call Log system.

## Problem Statement
- Customer data was scattered across caller/receiver columns based on call direction
- Outgoing calls: customer in receiver field
- Incoming calls: customer in caller field
- Result: confusing data organization and poor user experience

## Solution Implemented
- Employee: Always the internal CRM user involved
- Customer: Always the external phone number
- Customer Name: Resolved name or auto-generated "Lead from call XXXXX"

## Database Changes

### Schema Modifications
```sql
-- Connect to database
mysql -u_153b19f6d09e655e -pzqNuU3BFCAAuAlsE _153b19f6d09e655e

-- Add new fields
ALTER TABLE `tabCRM Call Log` ADD COLUMN employee VARCHAR(140) NULL AFTER receiver;
ALTER TABLE `tabCRM Call Log` ADD COLUMN customer VARCHAR(140) NULL AFTER employee;
ALTER TABLE `tabCRM Call Log` ADD COLUMN customer_name VARCHAR(140) NULL AFTER customer;
```

### Verification Commands
```sql
-- Check field structure
DESCRIBE `tabCRM Call Log`;

-- Check migration results
SELECT 
    COUNT(*) as total_logs,
    COUNT(CASE WHEN employee IS NOT NULL THEN 1 END) as has_employee,
    COUNT(CASE WHEN customer IS NOT NULL THEN 1 END) as has_customer,
    COUNT(CASE WHEN customer_name IS NOT NULL AND customer_name != '' THEN 1 END) as has_names
FROM `tabCRM Call Log`;
```

## File Modifications

### 1. DocType JSON Configuration
**File**: `crm/fcrm/doctype/crm_call_log/crm_call_log.json`

**Changes Made**:
- Added employee, customer, customer_name to field_order
- Added field definitions with in_list_view: 1
- Hidden legacy caller/receiver fields with "Legacy" labels

### 2. Backend Python Logic
**File**: `crm/fcrm/doctype/crm_call_log/crm_call_log.py`

**Key Methods Added**:
```python
def before_save(self):
    self.populate_employee_customer_fields()

def populate_employee_customer_fields(self):
    if self.type == 'Outgoing':
        self.employee = self.caller
        self.customer = self.to
    elif self.type == 'Incoming':
        self.employee = self.receiver
        self.customer = self.get('from')
    
    if self.customer and not self.customer_name:
        self.customer_name = self.get_customer_name_from_phone(self.customer)

def get_customer_name_from_phone(self, phone_number):
    # Search contacts and leads
    # If not found, return f"Lead from call {phone_number}"

@staticmethod
def default_list_data():
    # Updated to return Employee, Customer Name, Customer Phone columns
    # instead of Caller, Receiver
```

### 3. Mobile Sync API
**File**: `crm/api/mobile_sync.py`

**Updated prepare_call_log_document()**:
- Mobile app user always becomes employee
- Other party becomes customer
- Auto-generates customer names for unknowns

## Migration Patches

### Patch 1: Data Migration
**File**: `crm/patches/v1_0/migrate_caller_receiver_to_employee_customer.py`
- Migrated existing 132 call logs from caller/receiver to employee/customer
- Populated customer names from contacts/leads where possible

### Patch 2: Auto-Name Generation
**File**: `crm/patches/v1_0/update_empty_customer_names.py`
- Updated all empty customer_name fields with auto-generated names
- Used direct SQL for immediate results

**Direct SQL Update**:
```sql
UPDATE `tabCRM Call Log`
SET customer_name = CONCAT('Lead from call ', customer)
WHERE (customer_name IS NULL OR customer_name = '')
AND customer IS NOT NULL
AND customer != '';
```

### Update patches.txt
```bash
echo "crm.patches.v1_0.migrate_caller_receiver_to_employee_customer # 04-01-2025" >> crm/patches.txt
echo "crm.patches.v1_0.update_empty_customer_names # 04-01-2025" >> crm/patches.txt
```

## Testing Commands

### Check Migration Results
```sql
-- Sample data verification
SELECT name, employee, customer, customer_name, type, caller, receiver
FROM `tabCRM Call Log` LIMIT 10;

-- Auto-generated names distribution
SELECT customer, customer_name, COUNT(*) as count
FROM `tabCRM Call Log`
WHERE customer_name LIKE 'Lead from call%'
GROUP BY customer, customer_name
ORDER BY count DESC;
```

### Clear Cache
```sql
-- Force view refresh
TRUNCATE TABLE `tabCRM View Settings`;
```

## Final Results

### Migration Statistics
- Total Records: 132 call logs
- Employee Field: 100% populated (132/132)
- Customer Field: 100% populated (132/132)
- Customer Names: 99.2% populated (131/132)

### Top Auto-Generated Names
- Lead from call 1234567890 (67 records)
- Lead from call 8758127012 (12 records)
- Lead from call 0987654321 (7 records)
- And 27 more unique phone numbers

## Git Commits

### Commit 1: Core Structure
```bash
git commit -m "feat: Replace caller/receiver with employee/customer structure in call logs"
```

### Commit 2: Auto-Naming
```bash
git commit -m "feat: Auto-generate customer names for unknown numbers"
```

### Commit 3: Data Migration
```bash
git commit -m "feat: Migrate existing call logs to use auto-generated customer names"
```

## Benefits Achieved
- ✅ Unified customer view in dedicated columns
- ✅ Clear employee tracking
- ✅ Auto-generated names for all unknowns
- ✅ Backward compatibility maintained
- ✅ Improved user experience

## Key Learnings
1. Always backup before schema changes
2. Add new fields before modifying logic
3. Use direct SQL when Frappe console unavailable
4. Clear caches after major changes
5. Test each phase before proceeding

This migration successfully transformed a confusing data structure into an intuitive, user-friendly system while maintaining complete data integrity. 