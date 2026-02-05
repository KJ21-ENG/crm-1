# SOP: Onboard New Customer

| Field | Value |
|-------|-------|
| **Purpose** | Set up a new customer site and configure initial users |
| **Scope** | New customer onboarding, site creation, domain configuration |
| **Role** | System Administrator |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] Customer contract signed and approved
- [ ] Domain name registered (if custom domain)
- [ ] SSH access to production server
- [ ] Admin credentials for Frappe
- [ ] Customer contact information for initial users

---

## Procedure

### Step 1: Plan Site Configuration

Document the following before starting:

| Item | Value |
|------|-------|
| Site Name | e.g., customer.eshin-crm.com |
| Admin Email | |
| Initial Users | # of users |
| Custom Domain | Yes/No |

---

### Step 2: Create New Site

```bash
cd ~/frappe-bench

# Create the site
bench new-site customer.example.com \
    --db-name customersite_db \
    --admin-password "strong_admin_password"
```

**Expected Result:** Site created with success message.

---

### Step 3: Install CRM App

```bash
# Install CRM on the new site
bench --site customer.example.com install-app crm
```

**Expected Result:** CRM app installed successfully.

---

### Step 4: Configure Site Settings

```bash
# Enable scheduler
bench --site customer.example.com enable-scheduler

# Set production mode
bench --site customer.example.com set-config developer_mode 0
```

---

### Step 5: Configure Domain (if custom)

**Option A: Subdomain**
```bash
# Add to DNS: customer.eshin-crm.com → server IP
# Add domain to site
bench setup add-domain customer.eshin-crm.com --site customer.example.com
```

**Option B: Custom Domain**
```bash
# Add domain
bench setup add-domain customer-domain.com --site customer.example.com

# Set up SSL
sudo certbot --nginx -d customer-domain.com
```

---

### Step 6: Create Administrator User

1. Login to site as Administrator
2. Go to User List
3. Create new user:
   - Email: customer-admin@example.com
   - Role: System Manager
   - Send welcome email: Yes

---

### Step 7: Create Initial Users

1. For each user, go to User List → New
2. Fill in:
   - Email
   - First Name
   - Role (Sales User/Support User)
3. Send welcome email

---

### Step 8: Configure Roles and Permissions

1. Go to CRM Settings
2. Configure module access for each role
3. Set up lead assignment rules
4. Configure notification preferences

---

### Step 9: Import Initial Data (if applicable)

```bash
# If customer has existing data
bench --site customer.example.com import-csv /path/to/leads.csv --doctype "CRM Lead"
```

---

### Step 10: Final Testing

1. Login as customer admin
2. Create test lead
3. Create test ticket
4. Verify all modules accessible
5. Test email notifications

---

## Verification Checklist

- [ ] Site loads correctly at domain
- [ ] SSL certificate valid (https works)
- [ ] Admin user can login
- [ ] CRM modules visible
- [ ] Test lead/ticket created successfully
- [ ] Email notifications working
- [ ] Scheduler running

---

## Rollback / Undo

If onboarding fails:

```bash
# Remove site completely
bench drop-site customer.example.com

# Remove domain from nginx
sudo rm /etc/nginx/conf.d/customer.example.com.conf
sudo systemctl reload nginx
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Site not loading | Check nginx config, run `bench setup nginx` |
| SSL error | Run `sudo certbot --nginx -d domain.com` |
| Email not sending | Check SMTP settings in site_config.json |
| Scheduler not running | Run `bench --site X enable-scheduler` |

---

## Related Documents

- [Installation](../admin-guide/installation.md)
- [Add Sales User](add-sales-user.md)
- [SSL Setup](../admin-guide/ssl-email-setup.md)
