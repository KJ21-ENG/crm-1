# DocType Development

Guide to creating and extending DocTypes in Eshin CRM.

---

## DocType Overview

DocTypes are Frappe's data model definitions. Each DocType creates:
- Database table
- REST API endpoints
- Form interface
- List view

---

## Existing CRM DocTypes

| DocType | Module | Purpose |
|---------|--------|---------|
| CRM Lead | FCRM | Lead management |
| CRM Ticket | FCRM | Support tickets |
| CRM Customer | FCRM | Customer records |
| CRM Call Log | FCRM | Call tracking |
| CRM Task | FCRM | Task management |
| CRM Assignment Request | FCRM | Assignment workflow |
| CRM Deal | FCRM | Deal/opportunity |

---

## Creating a New DocType

### 1. Create DocType via Desk

```bash
bench --site eshin.localhost console
```

Or use the web interface:
1. Go to `/app/doctype/new-doctype`
2. Fill in name and module
3. Add fields
4. Save

### 2. Create via Code

Create files in `crm/fcrm/doctype/crm_new_doctype/`:

**crm_new_doctype.json**
```json
{
    "name": "CRM New DocType",
    "module": "FCRM",
    "doctype": "DocType",
    "custom": 0,
    "fields": [
        {
            "fieldname": "title",
            "fieldtype": "Data",
            "label": "Title",
            "reqd": 1
        },
        {
            "fieldname": "description",
            "fieldtype": "Text Editor",
            "label": "Description"
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        }
    ]
}
```

**crm_new_doctype.py**
```python
import frappe
from frappe.model.document import Document

class CRMNewDocType(Document):
    def validate(self):
        # Validation logic
        pass
    
    def before_save(self):
        # Pre-save logic
        pass
    
    def after_insert(self):
        # Post-insert logic
        pass
```

**__init__.py**
```python
# Empty file to mark as Python package
```

### 3. Run Migration

```bash
bench --site eshin.localhost migrate
```

---

## Adding Fields to Existing DocTypes

### Via Custom Field

For non-breaking additions:

```python
# In a patch file
import frappe

def execute():
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "CRM Lead",
        "fieldname": "custom_field",
        "fieldtype": "Data",
        "label": "Custom Field",
        "insert_after": "existing_field"
    }).insert()
```

### Via JSON Definition

Edit the DocType JSON and add field:

```json
{
    "fieldname": "new_field",
    "fieldtype": "Link",
    "label": "New Field",
    "options": "Linked DocType"
}
```

---

## Field Types

| Type | Use Case |
|------|----------|
| Data | Single line text |
| Text | Multi-line text |
| Text Editor | Rich text |
| Int | Integer |
| Float | Decimal |
| Currency | Money values |
| Date | Date picker |
| Datetime | Date + time |
| Link | Reference to another DocType |
| Select | Dropdown |
| Check | Boolean |
| Table | Child table |
| Attach | File upload |

---

## DocType Hooks

### Document Events

In your DocType class:

```python
class CRMNewDocType(Document):
    def validate(self):
        """Called before save/submit"""
        self.validate_fields()
    
    def before_save(self):
        """Called before database write"""
        pass
    
    def after_insert(self):
        """Called after first save"""
        pass
    
    def on_update(self):
        """Called after any save"""
        pass
    
    def on_trash(self):
        """Called before delete"""
        pass
```

### External Hooks (hooks.py)

```python
doc_events = {
    "CRM Lead": {
        "validate": ["crm.api.custom.validate_lead"],
        "on_update": ["crm.api.custom.on_lead_update"],
    }
}
```

---

## Permissions

### Role-Based Permissions

In DocType JSON:

```json
{
    "permissions": [
        {
            "role": "Sales User",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0
        },
        {
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        }
    ]
}
```

### Custom Permission Logic

In hooks.py:

```python
has_permission = {
    "CRM New DocType": "crm.api.permissions.custom_permission"
}
```

---

## API Generation

Each DocType automatically gets:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/resource/CRM Lead` | GET | List records |
| `/api/resource/CRM Lead/:name` | GET | Single record |
| `/api/resource/CRM Lead` | POST | Create |
| `/api/resource/CRM Lead/:name` | PUT | Update |
| `/api/resource/CRM Lead/:name` | DELETE | Delete |

---

## Related Guides

- [API Reference](api-reference.md)
- [Hooks, Tasks & Patches](hooks-tasks-patches.md)
