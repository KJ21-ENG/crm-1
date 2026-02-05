# SOP: Restore from Backup

| Field | Value |
|-------|-------|
| **Purpose** | Restore CRM to a previous state from backup |
| **Scope** | Database and file restoration |
| **Role** | System Administrator |
| **Frequency** | As needed (disaster recovery, testing) |

---

## Prerequisites

- [ ] Valid backup file (.sql.gz)
- [ ] File backups (.tar) if restoring files
- [ ] SSH access to target server
- [ ] Target site exists or will be created
- [ ] Maintenance window communicated to users

---

## Procedure

### Step 1: Identify Backup to Restore

```bash
# List available backups
ls -la ~/frappe-bench/sites/eshin.localhost/private/backups/

# Sample output:
# 20260202_020000-eshin_db.sql.gz
# 20260202_020000-eshin_db-files.tar
# 20260202_020000-eshin_db-private-files.tar
```

Select the backup date/time you want to restore.

---

### Step 2: Enable Maintenance Mode

```bash
cd ~/frappe-bench
bench --site eshin.localhost set-maintenance-mode on
```

**Expected Result:** Site shows maintenance page to users.

---

### Step 3: Stop Background Services

```bash
# Stop workers to prevent data changes
sudo supervisorctl stop frappe-bench-frappe-workers:*
sudo supervisorctl stop frappe-bench-frappe-schedule
```

---

### Step 4: Restore Database

**Basic Restore:**
```bash
bench --site eshin.localhost restore \
    sites/eshin.localhost/private/backups/20260202_020000-eshin_db.sql.gz
```

**Restore with Files:**
```bash
bench --site eshin.localhost restore \
    --with-public-files sites/eshin.localhost/private/backups/20260202_020000-eshin_db-files.tar \
    --with-private-files sites/eshin.localhost/private/backups/20260202_020000-eshin_db-private-files.tar \
    sites/eshin.localhost/private/backups/20260202_020000-eshin_db.sql.gz
```

**Expected Result:** "Restored X tables" message.

---

### Step 5: Run Migrations

```bash
bench --site eshin.localhost migrate
```

This ensures any patches between backup date and current code are applied.

---

### Step 6: Clear Cache

```bash
bench --site eshin.localhost clear-cache
bench --site eshin.localhost clear-website-cache
```

---

### Step 7: Restart Services

```bash
sudo supervisorctl start frappe-bench-frappe-schedule
sudo supervisorctl start frappe-bench-frappe-workers:*
sudo supervisorctl restart all
```

---

### Step 8: Disable Maintenance Mode

```bash
bench --site eshin.localhost set-maintenance-mode off
```

**Expected Result:** Site accessible to users.

---

### Step 9: Verify Restoration

1. Login as Administrator
2. Check data matches backup date
3. Create test record to verify write access
4. Check background jobs running

---

## Restore to Staging Environment

To test backup before production restore:

```bash
# Create staging site
bench new-site staging.localhost

# Restore backup to staging
bench --site staging.localhost restore /path/to/backup.sql.gz

# Install apps
bench --site staging.localhost install-app crm

# Test on staging
```

---

## Verification Checklist

- [ ] Site accessible
- [ ] Data reflects backup date/time
- [ ] Login works for all user types
- [ ] Creating new records works
- [ ] Background jobs running
- [ ] No error logs

---

## Rollback / Undo

If restore causes issues, restore from a different backup:

```bash
# Use older backup
bench --site eshin.localhost restore /path/to/older-backup.sql.gz
bench --site eshin.localhost migrate
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Site not found" | Ensure site folder exists |
| Permission error | Run as frappe user |
| "Database doesn't exist" | Create DB: `bench new-site` |
| Migrations fail | Check patches.txt for issues |
| Files missing | Ensure file tar included in restore |

---

## Related Documents

- [Backup Database & Files](backup-database-files.md)
- [Apply Patches & Upgrades](apply-patches-upgrades.md)
