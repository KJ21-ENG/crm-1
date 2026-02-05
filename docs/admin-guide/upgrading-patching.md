# Upgrading & Patching

Procedures for applying updates and patches to Eshin CRM.

---

## Update Types

| Type | Frequency | Risk |
|------|-----------|------|
| Patch | As needed | Low |
| Minor Update | Monthly | Medium |
| Major Update | Annually | High |

---

## Pre-Update Checklist

- [ ] Backup database and files
- [ ] Test upgrade on staging first
- [ ] Review changelog for breaking changes
- [ ] Schedule maintenance window
- [ ] Notify users of downtime

---

## SOP: Apply Patches

### Title
Apply CRM Patches

### Purpose
Apply database and code patches after updates.

### Role
System Administrator

### Prerequisites
- Backup completed
- Staging test passed

### Procedure

1. **Enable Maintenance Mode**
   ```bash
   bench --site eshin.localhost set-maintenance-mode on
   ```

2. **Pull Latest Code**
   ```bash
   cd ~/frappe-bench/apps/crm
   git fetch origin
   git checkout development-kush-exp
   git pull origin development-kush-exp
   ```

3. **Run Migrations**
   ```bash
   cd ~/frappe-bench
   bench --site eshin.localhost migrate
   ```

4. **Build Frontend**
   ```bash
   bench build --app crm
   ```

5. **Clear Cache**
   ```bash
   bench --site eshin.localhost clear-cache
   ```

6. **Restart Services**
   ```bash
   sudo supervisorctl restart all
   ```

7. **Verify**
   ```bash
   bench --site eshin.localhost doctor
   ```

8. **Disable Maintenance Mode**
   ```bash
   bench --site eshin.localhost set-maintenance-mode off
   ```

### Expected Results
- No migration errors
- Site accessible
- New features working

### Rollback
```bash
# Restore from backup
bench --site eshin.localhost restore /path/to/backup.sql.gz
bench --site eshin.localhost migrate
```

---

## Staging Test

Always test on staging first:

```bash
# Create staging site
bench new-site staging.localhost

# Restore production backup
bench --site staging.localhost restore /path/to/prod-backup.sql.gz

# Apply update
git pull origin development-kush-exp
bench --site staging.localhost migrate

# Test functionality
```

---

## Viewing Patch Status

```bash
# View pending patches
bench --site eshin.localhost show-pending-patches

# View applied patches
cat ~/frappe-bench/apps/crm/crm/patches.txt
```

---

## Emergency Rollback

If update fails critically:

```bash
# Stop all services
sudo supervisorctl stop all

# Restore database
bench --site eshin.localhost restore /path/to/backup.sql.gz

# Revert code
cd ~/frappe-bench/apps/crm
git reset --hard COMMIT_HASH

# Rebuild and restart
bench build --app crm
sudo supervisorctl start all
```
