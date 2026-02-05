# SOP: Backup Database & Files

| Field | Value |
|-------|-------|
| **Purpose** | Create reliable backups of CRM database and files |
| **Scope** | Database, public files, private files |
| **Role** | System Administrator |
| **Frequency** | Daily (automated), Ad-hoc (manual) |

---

## Prerequisites

- [ ] SSH access to production server
- [ ] Sufficient disk space for backup
- [ ] Backup destination accessible (local or remote)

---

## Procedure

### Daily Automated Backup

Automated backups run via scheduler (hooks.py):
- **02:00 AM** - System backup script
- **17:25 PM** - Bench backup

No action required for automated backups.

---

### Ad-hoc Manual Backup

#### Step 1: Check Available Space

```bash
df -h ~/frappe-bench/sites/
```

**Expected Result:** At least 2x database size available.

---

#### Step 2: Create Backup

**Database Only:**
```bash
cd ~/frappe-bench
bench --site eshin.localhost backup
```

**Database + Files:**
```bash
bench --site eshin.localhost backup --with-files
```

**Expected Result:**
```
Backup successfully created at:
/home/frappe/frappe-bench/sites/eshin.localhost/private/backups/
20260202_120000-eshin_db.sql.gz
20260202_120000-eshin_db-files.tar
20260202_120000-eshin_db-private-files.tar
```

---

#### Step 3: Verify Backup

```bash
# List recent backups
ls -la ~/frappe-bench/sites/eshin.localhost/private/backups/ | tail -10

# Check file size (should be > 0)
du -sh ~/frappe-bench/sites/eshin.localhost/private/backups/*.sql.gz | tail -3

# Verify integrity
gzip -t ~/frappe-bench/sites/eshin.localhost/private/backups/*.sql.gz
echo $?  # Should output 0
```

---

#### Step 4: Copy to Remote Storage

```bash
# Copy to remote server
rsync -avz ~/frappe-bench/sites/eshin.localhost/private/backups/ \
    backup-user@backup-server:/backups/eshin/

# Or copy to S3 (if configured)
aws s3 sync ~/frappe-bench/sites/eshin.localhost/private/backups/ \
    s3://your-bucket/eshin-backups/
```

---

### Using Custom Backup Script

```bash
cd ~/frappe-bench/apps/crm/scripts

# Run Eshin backup script
./backup_eshin_site.sh
```

---

## Verification Checklist

- [ ] Backup file created with today's date
- [ ] File size is reasonable (> previous backup)
- [ ] Gzip integrity check passes
- [ ] Remote copy completed (if applicable)
- [ ] Backup older than retention period cleaned up

---

## Rollback / Undo

Backups are non-destructive. To remove old backups:

```bash
# Remove backups older than 30 days
find ~/frappe-bench/sites/eshin.localhost/private/backups/ \
    -type f -mtime +30 -delete
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backup fails - disk full | Clean old backups or extend disk |
| Permission denied | Check frappe user owns backup dir |
| Remote copy fails | Check SSH keys and network |
| Corrupted backup | Re-run backup, check disk health |

---

## Related Documents

- [Restore from Backup](restore-from-backup.md)
- [Security Checklist](../admin-guide/security-checklist.md)
