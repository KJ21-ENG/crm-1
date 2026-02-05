# SOP: Resolve Permission Issues

| Field | Value |
|-------|-------|
| **Purpose** | Diagnose and fix user permission problems |
| **Scope** | Role permissions, module access, document permissions |
| **Role** | Administrator |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] Administrator access
- [ ] User's role information
- [ ] Description of permission issue

---

## Procedure

### Step 1: Identify the Issue

Common symptoms:
- "You don't have permission to access this"
- Missing menu items
- Can't create/edit records
- Can't see certain data

---

### Step 2: Check User's Roles

1. Go to **Setup** → **User**
2. Find the affected user
3. View assigned roles
4. Verify correct role assigned

---

### Step 3: Check Role Permissions

1. Go to **Setup** → **Role Permission Manager**
2. Select the DocType (e.g., CRM Lead)
3. Find the user's role
4. Verify permissions:

| Permission | Needed For |
|------------|------------|
| Read | View records |
| Write | Edit records |
| Create | New records |
| Delete | Remove records |
| Submit | Submit documents |

---

### Step 4: Check Module Access

In CRM settings:
1. Go to **Role Module Permission**
2. Find user's role
3. Verify module access enabled:
   - Leads ✅
   - Tickets ✅
   - Customers ✅

---

### Step 5: Check Document-Level Permissions

If user can't see specific records:

1. Open the record they can't see
2. Check "Owner" field
3. Check if owner-based permission restricts access

---

### Step 6: Fix Permission

**Add Missing Role:**
```python
# In bench console
user = frappe.get_doc("User", "user@example.com")
user.add_roles("Sales User")
user.save()
```

**Add Module Access:**
1. Go to CRM Settings
2. Enable module for user's role

**Check Custom Permission in hooks.py:**
```python
# In crm/hooks.py
has_permission = {
    "CRM Lead": "crm.api.permissions.doctype_has_permission",
}
```

Review `crm/api/permissions.py` for custom logic.

---

### Step 7: Clear Cache

```bash
bench --site eshin.localhost clear-cache
```

Ask user to logout and login again.

---

### Step 8: Verify Fix

1. Have user login
2. Attempt the previously blocked action
3. Confirm access granted

---

## Common Permission Issues

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Can't see Leads module | Role not in module permission | Add to Role Module Permission |
| Can't create Lead | Role missing Create permission | Role Permission Manager |
| Can't see other's leads | Owner-based restriction | Add Share or expand permission |
| Can't assign leads | Not in assignable users | Check role assignment logic |

---

## Verification Checklist

- [ ] User can access required modules
- [ ] User can perform required actions
- [ ] User cannot access restricted areas
- [ ] Changes don't affect other users negatively

---

## Rollback / Undo

If permission change causes issues:

1. Revert role assignment
2. Remove module access
3. Clear cache
4. Have user logout/login

---

## Related Documents

- [Add Sales User](add-sales-user.md)
- [Security Checklist](../admin-guide/security-checklist.md)
