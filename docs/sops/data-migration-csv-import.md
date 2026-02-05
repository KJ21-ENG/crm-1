# SOP: Data Migration (CSV Import)

| Field | Value |
|-------|-------|
| **Purpose** | Safely import data from CSV files into CRM |
| **Scope** | Lead import, Customer import, bulk data |
| **Role** | Administrator |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] CSV file prepared in correct format
- [ ] Backup completed
- [ ] Sample import tested
- [ ] User training on data format

---

## Procedure

### Step 1: Prepare CSV File

**Required Format:**

| Column | Example | Notes |
|--------|---------|-------|
| first_name | John | Required |
| mobile_no | 9876543210 | 10 digits, no spaces |
| email | john@example.com | Optional |
| lead_source | Website | Must match existing source |

**Sample CSV:**
```csv
first_name,last_name,mobile_no,email,lead_source
John,Doe,9876543210,john@example.com,Website
Jane,Smith,9876543211,jane@example.com,Referral
```

---

### Step 2: Validate Data Before Import

```bash
# Check for duplicates in CSV
awk -F',' 'NR>1 {print $3}' leads.csv | sort | uniq -d

# Check line count
wc -l leads.csv
```

---

### Step 3: Create Backup

```bash
bench --site eshin.localhost backup
```

---

### Step 4: Test with Small Sample

1. Create test CSV with 5-10 rows
2. Import test file
3. Verify imported data
4. Delete test records if needed

---

### Step 5: Import via Data Import Tool

**Option A: Web Interface**

1. Go to Settings → Data Import
2. Select DocType: "CRM Lead"

![Data Import Wizard](../assets/screenshots/data-import-wizard.png)
<!-- TODO: Capture Data Import main screen -->

![DocType Selection](../assets/screenshots/import-doctype-select.png)
<!-- TODO: Capture DocType selection dropdown -->

3. Download template to verify format
4. Upload your CSV
5. Click **Start Import**
6. Monitor progress

![Import Progress](../assets/screenshots/import-progress.png)
<!-- TODO: Capture import progress indicator -->

---

**Option B: Command Line**

```bash
cd ~/frappe-bench

bench --site eshin.localhost import-csv /path/to/leads.csv \
    --doctype "CRM Lead" \
    --submit-after-import 0
```

---

### Step 6: Monitor Import Progress

Watch for:
- Success count
- Error count
- Skipped records (duplicates)

---

### Step 7: Verify Imported Data

```bash
# Count records after import
bench --site eshin.localhost console
```

```python
>>> frappe.db.count("CRM Lead", {"creation": [">", "2026-02-02"]})
```

---

### Step 8: Handle Errors

1. Export error log from Data Import
2. Fix issues in source CSV
3. Re-import failed rows only

---

## Common Field Mappings

| CRM Field | CSV Column |
|-----------|------------|
| first_name | first_name |
| last_name | last_name |
| mobile_no | mobile_no |
| email | email |
| lead_source | lead_source |
| status | status |

---

## Verification Checklist

- [ ] Correct record count imported
- [ ] No duplicate records created
- [ ] Required fields populated
- [ ] Links to other DocTypes valid
- [ ] Data displays correctly in UI

---

## Rollback / Undo

To remove imported records:

```bash
bench --site eshin.localhost console
```

```python
# Delete records from specific import batch
leads = frappe.get_all("CRM Lead", 
    filters={"creation": [">", "2026-02-02 10:00:00"]},
    pluck="name")

for lead in leads:
    frappe.delete_doc("CRM Lead", lead)

frappe.db.commit()
```

Or restore from backup:
```bash
bench --site eshin.localhost restore /path/to/pre-import-backup.sql.gz
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Duplicate entry" | Check for existing mobile numbers |
| "Link not found" | Verify lead_source exists |
| "Value too long" | Check field length limits |
| Import hangs | Break into smaller batches |

---

## Related Documents

- [Backup Database & Files](backup-database-files.md)
- [Restore from Backup](restore-from-backup.md)
