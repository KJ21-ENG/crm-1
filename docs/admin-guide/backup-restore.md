# Backup & Restore

Procedures for backing up and restoring Eshin CRM data.

---

## Backup Types

| Type | Contents | Frequency |
|------|----------|-----------|
| **Database** | All site data | Daily |
| **Files** | Uploads, attachments | Daily |
| **Full** | Database + Files | Weekly |

---

## Automated Backups

### Scheduled Backups

The system runs automated backups via hooks.py scheduler:

| Time | Backup Type |
|------|-------------|
| 02:00 AM | System backup script |
| 17:25 PM | Bench backup |

### Backup Location

Default: `/home/frappe/frappe-bench/sites/eshin.localhost/private/backups/`

---

## Manual Backup

### Using Bench

```bash
cd ~/frappe-bench

# Full backup (database + files)
bench --site eshin.localhost backup --with-files

# Database only
bench --site eshin.localhost backup
```

![Backup In Progress](../assets/screenshots/backup-in-progress.png)
<!-- TODO: Capture terminal showing backup command running -->

### Using Custom Script

```bash
cd ~/frappe-bench/apps/crm/scripts

# Run backup script
./backup_eshin_site.sh
```

---

## SOP: Daily Backup Verification

### Title
Daily Backup Verification

### Purpose
Ensure backups are running and valid.

### Scope
All production environments.

### Role
System Administrator

### Prerequisites
- SSH access to production server
- Access to backup directory

### Procedure

1. **Login to Server**
   ```bash
   ssh frappe@your-server
   ```

2. **Check Backup Files**
   ```bash
   cd ~/frappe-bench/sites/eshin.localhost/private/backups
   ls -la | head -10
   ```

![Backup Files Listing](../assets/screenshots/backup-files-listing.png)
<!-- TODO: Capture ls output showing backup files with dates -->

3. **Verify Recent Backup**
   ```bash
   # Check today's backup exists
   ls -la | grep $(date +%Y%m%d)
   ```

4. **Check Backup Size**
   ```bash
   # Should be > 0 bytes
   du -sh *.sql.gz | tail -5
   ```

5. **Test Backup Integrity**
   ```bash
   # Verify gzip integrity
   gzip -t *.sql.gz 2>&1 | head -10
   ```

### Expected Results
- Today's backup file exists
- File size is reasonable (> previous backups)
- Gzip integrity check passes

### Verification Checklist
- [ ] Backup file exists for today
- [ ] File size > 0
- [ ] No integrity errors

### Rollback
N/A - This is a verification procedure.

---

## Restore Procedures

### Restore from Bench Backup

```bash
cd ~/frappe-bench

# List available backups
ls sites/eshin.localhost/private/backups/

# Restore database
bench --site eshin.localhost restore \
    sites/eshin.localhost/private/backups/20260202_120000-eshin_db.sql.gz

# Restore with files
bench --site eshin.localhost restore \
    --with-public-files sites/eshin.localhost/private/backups/20260202_120000-eshin_db-files.tar \
    --with-private-files sites/eshin.localhost/private/backups/20260202_120000-eshin_db-private-files.tar \
    sites/eshin.localhost/private/backups/20260202_120000-eshin_db.sql.gz
```

![Restore Success Output](../assets/screenshots/restore-success.png)
<!-- TODO: Capture terminal showing successful restore completion -->

### Restore to New Site

```bash
# Create new site
bench new-site staging.localhost

# Restore backup to new site
bench --site staging.localhost restore \
    /path/to/backup.sql.gz

# Install CRM app
bench --site staging.localhost install-app crm
```

---

## SOP: Restore from Backup

### Title
Restore Production from Backup

### Purpose
Restore CRM to a previous state.

### Scope
Production/Staging environments.

### Role
System Administrator

### Prerequisites
- Valid backup file
- SSH access
- Database credentials

### Procedure

1. **Enable Maintenance Mode**
   ```bash
   cd ~/frappe-bench
   bench --site eshin.localhost set-maintenance-mode on
   ```

2. **Stop Workers**
   ```bash
   sudo supervisorctl stop all
   ```

3. **Locate Backup**
   ```bash
   ls -la sites/eshin.localhost/private/backups/
   # Find the backup to restore
   ```

4. **Restore Database**
   ```bash
   bench --site eshin.localhost restore \
       sites/eshin.localhost/private/backups/BACKUP_FILE.sql.gz
   ```

5. **Restore Files (if needed)**
   ```bash
   bench --site eshin.localhost restore \
       --with-public-files path/to/files.tar \
       sites/eshin.localhost/private/backups/BACKUP_FILE.sql.gz
   ```

6. **Run Migrations**
   ```bash
   bench --site eshin.localhost migrate
   ```

7. **Clear Cache**
   ```bash
   bench --site eshin.localhost clear-cache
   ```

8. **Restart Services**
   ```bash
   sudo supervisorctl start all
   ```

9. **Disable Maintenance Mode**
   ```bash
   bench --site eshin.localhost set-maintenance-mode off
   ```

### Expected Results
- Site restored to backup state
- All users can access
- Data matches backup date

### Verification Checklist
- [ ] Site accessible
- [ ] Login works
- [ ] Data from backup date visible
- [ ] No error logs

### Rollback
If restore fails, restore from a different backup or contact development team.

---

## Backup Retention

| Environment | Retention |
|-------------|-----------|
| Production | 30 days |
| Staging | 7 days |
| Development | 3 days |

---

## Off-site Backup

For disaster recovery, copy backups off-site:

```bash
# Sync to remote server
rsync -avz ~/frappe-bench/sites/eshin.localhost/private/backups/ \
    backup-user@remote-server:/backups/eshin/
```

---

## Related Guides

- [Upgrading & Patching](upgrading-patching.md)
- [Security Checklist](security-checklist.md)
