# Hooks, Tasks & Patches

Guide to Frappe hooks, scheduled tasks, and database migrations.

---

## Hooks (hooks.py)

The `crm/hooks.py` file configures app behavior.

### Document Events

```python
doc_events = {
    "Contact": {
        "validate": ["crm.api.contact.validate"],
    },
    "ToDo": {
        "after_insert": ["crm.api.todo.after_insert"],
        "on_update": ["crm.api.todo.on_update"],
    },
    "WhatsApp Message": {
        "validate": ["crm.api.whatsapp.validate"],
        "on_update": ["crm.api.whatsapp.on_update"],
    },
    "CRM Deal": {
        "on_update": ["crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.create_customer_in_erpnext"],
    },
}
```

### Available Events

| Event | When Triggered |
|-------|----------------|
| `validate` | Before save/submit |
| `before_save` | Before DB write |
| `after_insert` | After first save |
| `on_update` | After any save |
| `on_trash` | Before delete |
| `after_delete` | After delete |
| `on_submit` | After submit |
| `on_cancel` | After cancel |

### Creating a Hook Function

```python
# crm/api/custom_hooks.py
import frappe

def on_lead_update(doc, method):
    """Called when CRM Lead is updated"""
    if doc.status == "Account Activated":
        # Create customer, send notification, etc.
        pass
```

Register in hooks.py:
```python
doc_events = {
    "CRM Lead": {
        "on_update": ["crm.api.custom_hooks.on_lead_update"],
    }
}
```

---

## Scheduled Tasks

### Scheduler Events

```python
scheduler_events = {
    "cron": {
        # Every minute
        "* * * * *": [
            "crm.api.task_reassignment.process_overdue_task_reassignments",
            "crm.api.task_notifications.check_and_send_task_notifications",
        ],
        # Daily at 2 AM
        "0 2 * * *": [
            "crm.utils.backup.run_system_backup_script",
        ],
        # Daily at 5:25 PM
        "25 17 * * *": [
            "crm.utils.backup.run_bench_backup_script",
        ],
    },
    "daily": [
        "crm.api.task_notifications.get_notification_stats",
    ],
}
```

### Cron Syntax

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Common Patterns

| Pattern | Meaning |
|---------|---------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `0 2 * * *` | Daily at 2 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |

### Creating a Scheduled Task

```python
# crm/api/custom_scheduler.py
import frappe

def daily_cleanup():
    """Run daily to clean up old records"""
    # Your cleanup logic
    frappe.db.delete("CRM Notification", {
        "creation": ["<", frappe.utils.add_days(frappe.utils.today(), -30)]
    })
    frappe.db.commit()
```

Register in hooks.py:
```python
scheduler_events = {
    "daily": [
        "crm.api.custom_scheduler.daily_cleanup",
    ],
}
```

---

## Patches (Database Migrations)

### Patch Structure

Patches are stored in `crm/patches/`:

```
patches/
├── patches.txt           # Patch registry
├── v1_0/                 # Version 1.0 patches
│   ├── add_custom_field.py
│   ├── update_lead_statuses.py
│   └── ...
└── v1_add_pod_id_field.py
```

### patches.txt

```
[pre_model_sync]
# Run before DocType changes
crm.patches.v1_0.move_crm_note_data_to_fcrm_note

[post_model_sync]
# Run after DocType changes
crm.patches.v1_0.create_default_fields_layout
crm.patches.v1_0.add_custom_lead_statuses
crm.patches.v1_0.add_device_call_id_to_crm_call_log
```

### Creating a Patch

**1. Create patch file:**

```python
# crm/patches/v1_0/add_new_field.py
import frappe

def execute():
    """Add new field to CRM Lead"""
    # Check if already applied
    if frappe.db.has_column("tabCRM Lead", "new_field"):
        return
    
    # Add column
    frappe.db.sql("""
        ALTER TABLE `tabCRM Lead`
        ADD COLUMN `new_field` VARCHAR(140)
    """)
    
    # Commit changes
    frappe.db.commit()
```

**2. Register in patches.txt:**

```
[post_model_sync]
crm.patches.v1_0.add_new_field
```

**3. Run migration:**

```bash
bench --site eshin.localhost migrate
```

### Patch Best Practices

1. **Check Before Acting**
   ```python
   if frappe.db.has_column("tabCRM Lead", "field"):
       return  # Already applied
   ```

2. **Use Transactions**
   ```python
   try:
       # Changes
       frappe.db.commit()
   except Exception:
       frappe.db.rollback()
       raise
   ```

3. **Log Progress**
   ```python
   frappe.logger().info("Migrating X records...")
   ```

4. **Handle Large Datasets**
   ```python
   # Process in batches
   for batch in frappe.db.get_all("CRM Lead", pluck="name", limit_page_length=1000):
       # Process batch
       frappe.db.commit()
   ```

---

## Override Classes

### Overriding Standard DocTypes

```python
# hooks.py
override_doctype_class = {
    "Contact": "crm.overrides.contact.CustomContact",
    "Email Template": "crm.overrides.email_template.CustomEmailTemplate",
}
```

### Custom Class Example

```python
# crm/overrides/contact.py
from frappe.contacts.doctype.contact.contact import Contact

class CustomContact(Contact):
    def validate(self):
        super().validate()
        # Custom validation
        self.custom_validation()
    
    def custom_validation(self):
        # Your logic
        pass
```

---

## After Migrate Hook

```python
# hooks.py
after_migrate = ["crm.fcrm.doctype.fcrm_settings.fcrm_settings.after_migrate"]
```

Use for:
- Setting up default data
- Fixing data inconsistencies
- Post-migration cleanup

---

## Testing Patches

```bash
# Run specific patch manually
bench --site eshin.localhost execute crm.patches.v1_0.add_new_field

# View pending patches
bench --site eshin.localhost show-pending-patches
```
