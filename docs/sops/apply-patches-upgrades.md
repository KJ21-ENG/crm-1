# SOP: Apply Patches & Upgrades

| Field | Value |
|-------|-------|
| **Purpose** | Apply code updates and database patches safely |
| **Scope** | Code updates, database migrations |
| **Role** | System Administrator |
| **Frequency** | As releases are available |

---

## Prerequisites

- [ ] Backup completed (see [Backup SOP](backup-database-files.md))
- [ ] Staging test completed (if major update)
- [ ] Maintenance window scheduled
- [ ] Users notified of downtime

---

## Procedure

### Step 1: Create Pre-Update Backup

```bash
cd ~/frappe-bench
bench --site eshin.localhost backup --with-files
```

---

### Step 2: Enable Maintenance Mode

```bash
bench --site eshin.localhost set-maintenance-mode on
```

---

### Step 3: Pull Latest Code

```bash
cd ~/frappe-bench/apps/crm

# Fetch updates
git fetch origin

# Check current branch
git branch

# Pull updates (development-kush-exp branch)
git checkout development-kush-exp
git pull origin development-kush-exp
```

**Expected Result:** Files updated, no merge conflicts.

---

### Step 4: Update Frappe (if applicable)

```bash
cd ~/frappe-bench/apps/frappe
git pull origin version-15
```

---

### Step 5: Install Dependencies

```bash
cd ~/frappe-bench

# Python dependencies
pip install -e apps/crm

# Node dependencies
cd apps/crm
yarn install
```

---

### Step 6: Run Migrations

```bash
cd ~/frappe-bench
bench --site eshin.localhost migrate
```

**Expected Result:** "X patches executed" message.

---

### Step 7: Build Frontend

```bash
bench build --app crm
```

**Expected Result:** Assets built successfully.

---

### Step 8: Clear Cache

```bash
bench --site eshin.localhost clear-cache
```

---

### Step 9: Restart Services

```bash
sudo supervisorctl restart all
```

---

### Step 10: Verify Update

```bash
# Check service status
sudo supervisorctl status

# Check for errors
tail -f ~/frappe-bench/logs/frappe.log
```

---

### Step 11: Disable Maintenance Mode

```bash
bench --site eshin.localhost set-maintenance-mode off
```

---

### Step 12: Smoke Test

1. Login as Administrator
2. Navigate to Leads, Tickets, Customers
3. Create test record
4. Verify new features (if applicable)

---

## Verification Checklist

- [ ] Site loads correctly
- [ ] No console errors
- [ ] All modules accessible
- [ ] New features working
- [ ] Background jobs running
- [ ] No errors in logs

---

## Rollback / Undo

If update causes issues:

### Revert Code

```bash
cd ~/frappe-bench/apps/crm
git reset --hard PREVIOUS_COMMIT_HASH
```

### Restore Database

```bash
bench --site eshin.localhost restore /path/to/pre-update-backup.sql.gz
bench --site eshin.localhost migrate
```

### Rebuild and Restart

```bash
bench build --app crm
sudo supervisorctl restart all
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Merge conflicts | Resolve manually or reset |
| Migration fails | Check error, may need patch fix |
| Build fails | Clear node_modules, reinstall |
| Site won't load | Check nginx config, restart |

---

## Related Documents

- [Backup Database & Files](backup-database-files.md)
- [Restore from Backup](restore-from-backup.md)
- [Upgrading & Patching](../admin-guide/upgrading-patching.md)
