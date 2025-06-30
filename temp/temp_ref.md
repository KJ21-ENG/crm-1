
# 🔧 Change Management in Frappe CRM - Complete Guide

Let me explain the different types of changes and their workflows. In Frappe CRM, there are 6 main types of changes, each with different approaches.

```bash
bench --site mycrm.localhost list-commands | grep -E "(migrate|build|restart|clear)"
```
```bash
ls -la apps/crm/crm/fcrm/doctype/crm_lead/
```

## 📋 6 Types of Changes in Frappe CRM

### 1. 🏷️ Field Property Changes (Simple)
What: Change field labels, descriptions, options, default values  
Example: "Lead Owner" → "Relationship Manager"

#### Method A: Property Setter (Runtime)
```python
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
make_property_setter("CRM Lead", "lead_owner", "label", "Relationship Manager", "Data")
```

#### Method B: UI Customization  
```bash
http://localhost:8000/app/customize-form/CRM%20Lead
```

#### How to Apply:
```bash
bench --site mycrm.localhost console
>>> from frappe.custom.doctype.property_setter.property_setter import make_property_setter
>>> make_property_setter("CRM Lead", "lead_owner", "label", "Relationship Manager", "Data")
>>> frappe.db.commit()

bench --site mycrm.localhost execute-file your_customization_script.py
```

---

### 2. ➕ Adding New Fields (Moderate)
What: Add new fields to existing doctypes  
Example: Add "Investment Amount" field to CRM Lead

#### Method A: Custom Field (Recommended)
```python
custom_field = frappe.get_doc({
    'doctype': 'Custom Field',
    'dt': 'CRM Lead',
    'fieldname': 'investment_amount',
    'fieldtype': 'Currency',
    'label': 'Investment Amount',
    'insert_after': 'annual_revenue'
})
custom_field.insert()
```

#### Method B: Modify DocType JSON (Advanced)
Modify crm_lead.json directly.

#### How to Apply:
```bash
bench --site mycrm.localhost execute "<python_code>"
bench --site mycrm.localhost migrate
bench --site mycrm.localhost clear-cache
```

---

### 3. 🎨 Layout & UI Changes (Complex)
What: Change form layouts, views  
Example: Rearrange Quick Entry form

#### Method A: CRM Fields Layout (JSON)
Modify CRM Fields Layout JSON.

#### Method B: Frontend Vue.js Changes
Modify Vue.js files directly.

#### How to Apply:
```bash
bench --site mycrm.localhost execute-file layout_script.py
bench --site mycrm.localhost clear-cache

cd /path/to/frontend
yarn build
```

---

### 4. ⚙️ Business Logic Changes (Advanced)
What: Change validation, workflows  
Example: Auto-assign leads

#### Method: Python Code Modification
Modify Python files in doctype directory.

#### How to Apply:
```bash
bench --site mycrm.localhost restart
./stop_crm_dev.sh
./start_crm_dev.sh
```

---

### 5. 📊 Master Data Changes (Simple)
What: Modify statuses, territories  
Example: Add lead statuses

#### Method: Direct Data Creation
Insert directly via frappe.get_doc().

#### How to Apply:
```bash
bench --site mycrm.localhost execute "<python_code>"
frappe.db.commit()
```

---

### 6. 🔗 Integration & API Changes (Expert)
What: Modify integrations, API endpoints  
Example: WhatsApp integration

#### Method: Code Modification
Modify API files.

#### How to Apply:
```bash
bench --site mycrm.localhost restart
bench --site mycrm.localhost clear-cache
```

---

## 🔄 Change Application Workflow Summary

### 💡 Quick Reference Table

| Change Type | File Location | Apply Method | Restart Required |
|-------------|---------------|--------------|------------------|
| Field Labels | Database | execute command | ❌ |
| New Fields | Database/JSON | migrate + clear-cache | ❌ |
| Layouts | Database/Vue | clear-cache | ❌ |
| Business Logic | Python | restart | ✅ |
| Master Data | Database | execute command | ❌ |
| APIs/Integrations | Python | restart + clear-cache | ✅ |

---

## 🔧 Standard Application Commands

### For Database Changes:
```bash
bench --site mycrm.localhost execute "<python_code>"
bench --site mycrm.localhost migrate
bench --site mycrm.localhost clear-cache
```

### For Code Changes:
```bash
bench --site mycrm.localhost restart

cd /path/to/frontend  
yarn dev
```

### For Major Changes:
```bash
./stop_crm_dev.sh
./start_crm_dev.sh

bench --site mycrm.localhost restart
bench --site mycrm.localhost clear-cache
bench --site mycrm.localhost clear-website-cache
```

---

## ⚡ Development Workflow Example

### Step 1: Add the Field
```bash
bench --site mycrm.localhost execute "<python_code>"
```

### Step 2: Update Layout
```bash
bench --site mycrm.localhost execute "<python_code>"
```

### Step 3: Add Business Logic
Modify Python files in the doctype directory.

### Step 4: Apply All Changes
```bash
bench --site mycrm.localhost clear-cache
bench --site mycrm.localhost restart
```

---

## 🚨 Important Notes

### ⚠️ Change Persistence
- Database changes: Permanent
- Code changes: Version controlled
- Layout changes: Stored in DB
- Frontend changes: Require build

### 🔒 Client Production Considerations
- Lock down layout access
- Document changes thoroughly
- Create repeatable patches
- Test in development first
