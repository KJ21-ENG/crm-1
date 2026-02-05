# Settings

Configure your personal preferences and system settings.

---

## Purpose

The Settings module allows:
- Personal preference configuration
- System-wide settings (Admins)
- Integration setup
- Notification preferences

**Typical Users:** All users (personal), Admins (system)

![Settings Main Page](../assets/screenshots/settings-main.png)
<!-- TODO: Capture settings main page showing all configuration sections -->

---

## Personal Settings

### Profile

| Setting | Description |
|---------|-------------|
| Display Name | Name shown in CRM |
| Email | Your email address |
| Phone | Your contact number |
| Avatar | Profile picture |

![Profile Settings](../assets/screenshots/settings-profile.png)
<!-- TODO: Capture profile settings tab with form fields -->

### Notifications

| Setting | Description |
|---------|-------------|
| Email Alerts | Enable/disable email notifications |
| In-app Alerts | Browser notifications |
| Task Reminders | Reminder timing preferences |

![Notification Preferences](../assets/screenshots/settings-notifications.png)
<!-- TODO: Capture notification preferences with toggle switches -->

---

## System Settings (Admin)

### CRM Settings

| Setting | Description |
|---------|-------------|
| Lead Sources | Configure lead source options |
| Lead Statuses | Customize status workflow |
| Ticket Subjects | Define ticket subject options |

### Global Settings

| Setting | Description |
|---------|-------------|
| Company Name | Organization name |
| Date Format | DD/MM/YYYY, etc. |
| Time Zone | System time zone |

---

## Integration Settings

### WhatsApp

Configure WhatsApp integration:
- Session management
- Multi-user setup
- Message templates

![Integration Settings](../assets/screenshots/settings-integrations.png)
<!-- TODO: Capture WhatsApp and telephony integration configuration -->

### Telephony

| Integration | Configuration |
|-------------|---------------|
| Twilio | API credentials |
| Exotel | API credentials |

> **Note:** Only Admins can configure integrations.

---

## Role & Permission Settings

### Module Access

Control which roles can access:
- Leads module
- Tickets module
- Customers module
- Settings module

### Action Permissions

| Action | Configurable |
|--------|--------------|
| Create | ✅ |
| Read | ✅ |
| Update | ✅ |
| Delete | ✅ |
| Assign | ✅ |

![Role Permissions Table](../assets/screenshots/settings-permissions.png)
<!-- TODO: Capture permissions configuration table -->

---

## Backup Settings

### Manual Backup

1. Go to Settings → Backup
2. Click **Backup Now**
3. Wait for completion
4. Download backup file

### Scheduled Backups

Configured via system scheduler:
- Daily at 02:00 AM
- Daily at 17:25 PM

---

## SOP: Updating Notification Preferences

### Steps

1. Click **Settings** in sidebar
2. Go to **Notifications** tab
3. Toggle preferences:
   - Email notifications
   - Browser notifications
   - Reminder timing
4. Click **Save**

### Expected Result
- Preferences saved immediately
- Takes effect on next notification

---

## Related Guides

- [Admin Guide](../admin-guide/installation.md) - System setup
- [SOPs](../sops/add-sales-user.md) - User management
