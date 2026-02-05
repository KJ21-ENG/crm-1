# Troubleshooting Guide

Common issues and their solutions for Eshin CRM.

---

## Quick Diagnostics

### Check System Health

```bash
cd ~/frappe-bench

# Site health check
bench --site eshin.localhost doctor

# Check running processes
sudo supervisorctl status

# Check disk space
df -h

# Check memory
free -h
```

---

## Common Issues

### Site Not Loading

**Symptoms:** Browser shows error or timeout

**Diagnosis:**
```bash
# Check nginx
sudo systemctl status nginx

# Check bench processes
sudo supervisorctl status

# Check logs
tail -f ~/frappe-bench/logs/web.error.log
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Nginx down | `sudo systemctl start nginx` |
| Workers crashed | `sudo supervisorctl restart all` |
| Database down | `sudo systemctl start mariadb` |
| Redis down | `sudo systemctl start redis` |

---

### "Internal Server Error" (500)

**Diagnosis:**
```bash
# Check error log
tail -100 ~/frappe-bench/logs/frappe.log
```

**Common Causes:**

| Error | Solution |
|-------|----------|
| Python exception | Check stack trace, fix code |
| Database connection | Restart MariaDB |
| Missing dependency | `pip install -r requirements.txt` |

---

### Login Fails

**Symptoms:** Correct password rejected

**Diagnosis:**
```bash
bench --site eshin.localhost console
```
```python
>>> user = frappe.get_doc("User", "user@example.com")
>>> print(user.enabled)
>>> print(user.last_login)
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| User disabled | Enable user |
| Password expired | Reset password |
| Session expired | Clear cookies, retry |
| Redis down | Start Redis |

---

### Slow Performance

**Diagnosis:**
```bash
# Check server load
top

# Check slow queries
tail -f ~/frappe-bench/logs/frappe.log | grep "slow query"

# Check queue backlog
bench --site eshin.localhost show-pending-jobs
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| High CPU | Check for runaway process |
| Database slow | Add indexes, optimize queries |
| Queue backlog | Add workers, clear old jobs |
| Memory full | Add RAM, clear cache |

---

### Background Jobs Not Running

**Symptoms:** Notifications delayed, emails not sending

**Diagnosis:**
```bash
# Check scheduler
bench --site eshin.localhost scheduler status

# Check workers
sudo supervisorctl status | grep worker
```

**Solutions:**
```bash
# Enable scheduler
bench --site eshin.localhost enable-scheduler

# Restart workers
sudo supervisorctl restart frappe-bench-frappe-workers:*
```

---

### Mobile App Not Syncing

**Symptoms:** Call logs not appearing in CRM

**Diagnosis:**
1. Check app connectivity
2. Check sync indicator in app
3. Review API logs

```bash
grep "mobile_sync" ~/frappe-bench/logs/frappe.log
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Network issue | Check phone connectivity |
| Auth expired | Re-login in app |
| API error | Check server logs |
| Duplicate check | Verify device_call_id unique |

---

### WhatsApp Not Working

**Symptoms:** Messages not sending/receiving

**Diagnosis:**
```bash
# Check WhatsApp service
cd ~/frappe-bench/apps/crm/local-whatsapp-service
docker-compose logs -f
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Session expired | Re-scan QR code |
| Service down | Restart container |
| Network issue | Check firewall |

---

### Emails Not Sending

See [SOP: Troubleshoot Email](sops/troubleshoot-email.md)

---

### Permission Denied Errors

See [SOP: Resolve Permission Issues](sops/resolve-permission-issues.md)

---

## Log File Locations

| Log | Path | Content |
|-----|------|---------|
| Frappe | `logs/frappe.log` | Application logs |
| Web errors | `logs/web.error.log` | HTTP errors |
| Worker | `logs/worker.log` | Background jobs |
| Scheduler | `logs/scheduler.log` | Scheduled tasks |
| Nginx access | `/var/log/nginx/access.log` | HTTP requests |
| Nginx errors | `/var/log/nginx/error.log` | Web server errors |

---

## Debugging Tools

### Python Console

```bash
bench --site eshin.localhost console
```
```python
# Query data
>>> frappe.db.sql("SELECT COUNT(*) FROM `tabCRM Lead`")

# Check user permissions
>>> frappe.has_permission("CRM Lead", "read", user="user@example.com")

# Debug document
>>> doc = frappe.get_doc("CRM Lead", "LEAD-001")
>>> print(doc.as_dict())
```

### Mariadb Console

```bash
bench --site eshin.localhost mariadb
```
```sql
-- Check table size
SELECT TABLE_NAME, TABLE_ROWS 
FROM information_schema.tables 
WHERE TABLE_SCHEMA = 'eshin_db';

-- Check slow queries
SHOW PROCESSLIST;
```

### Redis CLI

```bash
redis-cli

# Check queue size
LLEN frappe:queue:default

# Check cache
KEYS *cache*
```

---

## Emergency Procedures

### Site Down - Quick Recovery

```bash
# 1. Restart everything
sudo supervisorctl restart all

# 2. If still down, restart services
sudo systemctl restart mariadb
sudo systemctl restart redis
sudo systemctl restart nginx

# 3. If still down, check logs
tail -100 ~/frappe-bench/logs/frappe.log
```

### Database Corruption

```bash
# 1. Stop site
sudo supervisorctl stop all

# 2. Restore from backup
bench --site eshin.localhost restore /path/to/backup.sql.gz

# 3. Run migrations
bench --site eshin.localhost migrate

# 4. Restart
sudo supervisorctl start all
```

---

## Getting Help

1. Check this troubleshooting guide
2. Review relevant SOP
3. Check logs for specific errors
4. Contact development team with:
   - Error message
   - Steps to reproduce
   - Relevant log entries
