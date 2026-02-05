# SOP: Troubleshoot Email Not Sending

| Field | Value |
|-------|-------|
| **Purpose** | Diagnose and fix email delivery issues |
| **Scope** | SMTP configuration, email queue |
| **Role** | System Administrator |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] Admin access to system
- [ ] Access to SMTP credentials
- [ ] Ability to view email logs

---

## Procedure

### Step 1: Check Email Queue

```bash
cd ~/frappe-bench
bench --site eshin.localhost console
```

```python
>>> pending = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, limit=10)
>>> print(len(pending), "emails pending")
```

---

### Step 2: Check Email Account Configuration

In Frappe Desk:
1. Go to **Setup** → **Email Account**
2. Verify settings:
   - SMTP Server: smtp.gmail.com (or your provider)
   - Port: 587 (or 465 for SSL)
   - Use TLS: ✅
   - Password: Set correctly

---

### Step 3: Test SMTP Connection

```bash
bench --site eshin.localhost send-test-email recipient@email.com
```

**Expected Result:** "Test email sent"

---

### Step 4: Check Error Logs

```python
# In bench console
>>> errors = frappe.get_all("Email Queue", 
...     filters={"status": "Error"}, 
...     fields=["name", "error"], 
...     limit=5)
>>> for e in errors:
...     print(e.error)
```

---

### Step 5: Common Fixes

**Gmail - "Less secure app" blocked:**
- Use App-Specific Password
- Enable 2FA on Google account
- Generate app password

**Authentication Failed:**
- Verify username (full email)
- Update password in Email Account
- Check for account lockout

**Connection Timeout:**
- Check firewall allows outbound 587/465
- Try different SMTP port
- Verify server hostname

---

### Step 6: Retry Failed Emails

```bash
# Retry all failed emails
bench --site eshin.localhost retry-email-queue
```

Or manually:
```python
>>> frappe.db.sql("UPDATE `tabEmail Queue` SET status='Not Sent' WHERE status='Error'")
>>> frappe.db.commit()
```

---

### Step 7: Monitor After Fix

Watch email queue for next few minutes:
```python
>>> import time
>>> for i in range(5):
...     pending = frappe.db.count("Email Queue", {"status": "Not Sent"})
...     print(f"Pending: {pending}")
...     time.sleep(60)
```

---

## Verification Checklist

- [ ] Test email sends successfully
- [ ] Email queue processing (count decreasing)
- [ ] Recipients receiving emails
- [ ] No new errors in queue

---

## Rollback / Undo

Email configuration changes can be reverted:

1. Note current settings before changing
2. If broken, restore previous settings
3. Clear error emails if testing

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Authentication failed" | Check username/password, use app password |
| "Connection refused" | Check SMTP host/port, firewall |
| "Certificate verify failed" | Check TLS settings |
| "Rate limit exceeded" | Wait, or use different SMTP provider |
| "Relay denied" | Use authenticated account |

---

## Related Documents

- [SSL & Email Setup](../admin-guide/ssl-email-setup.md)
- [Troubleshooting](../troubleshooting.md)
