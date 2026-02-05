# SOP: Create Custom Report

| Field | Value |
|-------|-------|
| **Purpose** | Create and deploy a custom report in CRM |
| **Scope** | Report Builder, Query Report creation |
| **Role** | Developer, Administrator |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] Clear report requirements
- [ ] Developer mode enabled (for development)
- [ ] Understanding of data structure (DocTypes)

---

## Procedure

### Option A: Report Builder (No Code)

#### Step 1: Open Report Builder

1. Go to CRM Settings or Frappe Desk
2. Search for "Report Builder"
3. Click **New**

![Report Builder Interface](../assets/screenshots/report-builder.png)
<!-- TODO: Capture Report Builder main interface -->

---

#### Step 2: Configure Report

| Field | Value |
|-------|-------|
| Report Name | e.g., "Lead Conversion Report" |
| Reference DocType | CRM Lead |
| Report Type | Report Builder |

---

#### Step 3: Add Columns

1. Click **Add Column**
2. Select fields to include:
   - Name
   - First Name
   - Status
   - Created Date
   - Owner

![Report Columns Selection](../assets/screenshots/report-columns.png)
<!-- TODO: Capture column selection interface -->

---

#### Step 4: Add Filters

1. Click **Add Filter**
2. Configure:
   - Status = Account Activated
   - Date range

![Report Filters Configuration](../assets/screenshots/report-filters.png)
<!-- TODO: Capture filter configuration interface -->

---

#### Step 5: Save and Test

1. Click **Save**
2. Click **Show Report** to preview
3. Verify data is correct

![Report Preview](../assets/screenshots/report-preview.png)
<!-- TODO: Capture report preview showing data -->

---

### Option B: Query Report (SQL)

#### Step 1: Create Report File

```bash
cd ~/frappe-bench/apps/crm/crm
mkdir -p report/lead_conversion_report
```

Create `lead_conversion_report.py`:
```python
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Lead", "fieldname": "name", "fieldtype": "Link", "options": "CRM Lead"},
        {"label": "Name", "fieldname": "first_name", "fieldtype": "Data"},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data"},
        {"label": "Converted Date", "fieldname": "modified", "fieldtype": "Date"},
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT name, first_name, status, modified
        FROM `tabCRM Lead`
        WHERE status = 'Account Activated'
        ORDER BY modified DESC
    """, as_dict=True)
```

---

#### Step 2: Create Report JSON

Create `lead_conversion_report.json`:
```json
{
    "name": "Lead Conversion Report",
    "doctype": "Report",
    "ref_doctype": "CRM Lead",
    "report_type": "Script Report",
    "is_standard": "Yes",
    "module": "CRM"
}
```

---

#### Step 3: Register Report

Add to `crm/crm/config/desktop.py` or module configuration.

---

#### Step 4: Migrate

```bash
bench --site eshin.localhost migrate
```

---

#### Step 5: Test Report

1. Go to Reports in CRM
2. Find "Lead Conversion Report"
3. Run and verify data

---

## Deploy to Production

```bash
# On production server
cd ~/frappe-bench/apps/crm
git pull origin development-kush-exp
bench --site eshin.localhost migrate
```

---

## Verification Checklist

- [ ] Report appears in report list
- [ ] Data is accurate
- [ ] Filters work correctly
- [ ] Export to Excel works
- [ ] Permissions restrict access appropriately

---

## Rollback / Undo

To remove a custom report:

1. Delete from Report list (if Report Builder)
2. Or remove files and migrate (if Script Report)

---

## Related Documents

- [DocType Development](../developer-guide/doctype-development.md)
- [API Reference](../developer-guide/api-reference.md)
