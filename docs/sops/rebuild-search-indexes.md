# SOP: Rebuild Search Indexes

| Field | Value |
|-------|-------|
| **Purpose** | Rebuild search indexes and reprocess background jobs |
| **Scope** | Full-text search, background queues |
| **Role** | System Administrator |
| **Frequency** | As needed (after issues) |

---

## Prerequisites

- [ ] SSH access to production server
- [ ] Admin access to CRM
- [ ] Maintenance window (if production)

---

## Procedure

### Rebuild Search Database

#### Step 1: Clear and Rebuild

```bash
cd ~/frappe-bench

# Clear all caches
bench --site eshin.localhost clear-cache

# Rebuild search index
bench --site eshin.localhost build-search-index
```

**Expected Result:** "Search index built for X documents"

---

### Reprocess Background Jobs

#### Step 1: Check Queue Status

```bash
# View queue status
bench --site eshin.localhost show-pending-jobs
```

---

#### Step 2: Clear Failed Jobs

```bash
# Clear failed jobs from queue
bench --site eshin.localhost clear-failed-jobs
```

---

#### Step 3: Restart Workers

```bash
sudo supervisorctl restart frappe-bench-frappe-workers:*
```

---

### Full Queue Reset

If queues are stuck:

```bash
# Stop all workers
sudo supervisorctl stop frappe-bench-frappe-workers:*

# Clear Redis queue
redis-cli FLUSHDB

# Restart workers
sudo supervisorctl start frappe-bench-frappe-workers:*
```

> ⚠️ **Warning:** This clears ALL pending jobs. Only use if necessary.

---

### Rebuild Website Routes

```bash
bench --site eshin.localhost rebuild-website
```

---

## Verification Checklist

- [ ] Search returns relevant results
- [ ] No pending failed jobs
- [ ] Workers running (check supervisorctl status)
- [ ] New records appear in search

---

## Rollback / Undo

Search index rebuilds are non-destructive. If issues persist:

1. Check logs: `tail -f ~/frappe-bench/logs/frappe.log`
2. Verify Redis is running: `redis-cli ping`
3. Contact development team if unable to resolve

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Search returns no results | Rebuild index |
| Jobs stuck in queue | Clear failed jobs, restart workers |
| "Redis connection refused" | Start Redis: `sudo systemctl start redis` |
| Workers not starting | Check supervisor config |

---

## Related Documents

- [Troubleshooting](../troubleshooting.md)
