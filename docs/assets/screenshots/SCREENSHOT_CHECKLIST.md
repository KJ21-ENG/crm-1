# Screenshot Capture Checklist

**Complete audit of all screenshots needed for Eshin CRM documentation.**

## Target Directory
```
docs/assets/screenshots/
```

---

## Summary

| Category | Existing | Recommended | Total |
|----------|----------|-------------|-------|
| Index / Quick Start | 5 | 0 | 5 |
| User Guide | 10 | 19 | 29 |
| Admin Guide | 0 | 12 | 12 |
| SOPs | 0 | 18 | 18 |
| Developer Guide | 0 | 5 | 5 |
| **TOTAL** | **15** | **54** | **69** |

---

## Part 1: Existing Screenshots (15)

### Index / Quick Start (`docs/index.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `login.png` | Login Screen | 21 |
| [ ] | `leads-create.png` | Create Lead | 38 |
| [ ] | `activity-log.png` | Log Activity | 52 |
| [ ] | `task-create.png` | Create Task | 66 |
| [ ] | `dashboard.png` | Dashboard | 82 |

### User Guide - Overview (`docs/user-guide/overview.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `sidebar.png` | Sidebar Navigation | 47 |

### User Guide - Leads (`docs/user-guide/leads.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `leads-list-create.png` | Create Lead Button | 47 |
| [ ] | `leads-modal.png` | Lead Form | 70 |
| [ ] | `lead-detail.png` | Lead Detail | 111 |
| [ ] | `assignment-request.png` | Assignment Request | 156 |

### User Guide - Tasks (`docs/user-guide/tasks.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `task-create.png` | Create Task | 52 |

### User Guide - Tickets (`docs/user-guide/tickets.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `ticket-create.png` | Create Ticket | 63 |
| [ ] | `ticket-detail.png` | Ticket Detail | 94 |

### User Guide - Customers (`docs/user-guide/customers.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `customer-list.png` | Customer List | 41 |
| [ ] | `customer-detail.png` | Customer Detail | 76 |

### User Guide - Call Logs (`docs/user-guide/call-logs.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `call-logs-list.png` | Call Logs List | 43 |

### User Guide - Dashboard (`docs/user-guide/dashboard.md`)

| ✅ | Filename | Alt Text | Line |
|----|----------|----------|------|
| [ ] | `dashboard.png` | Dashboard | 39 |

---

## Part 2: Recommended Additional Screenshots (54)

### User Guide - Overview (2 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `main-interface.png` | Full CRM interface view | Line 30 |
| MEDIUM | `topbar-actions.png` | Top navigation bar | Line 55 |

### User Guide - Leads (4 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `lead-status-workflow.png` | Status dropdown showing all states | Line 85 |
| HIGH | `lead-activities-panel.png` | Activity panel with logged calls/notes | Line 130 |
| MEDIUM | `lead-quick-actions.png` | Quick action buttons (call, email) | Line 95 |
| LOW | `lead-bulk-actions.png` | Multi-select bulk actions | Line 175 |

### User Guide - Tickets (3 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `ticket-assignees-multi.png` | Multiple assignee selection | Line 75 |
| MEDIUM | `ticket-status-dropdown.png` | Status options dropdown | Line 55 |
| MEDIUM | `ticket-activity-timeline.png` | Activity timeline view | Line 110 |

### User Guide - Customers (2 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `customer-linked-leads.png` | Linked leads section | Line 90 |
| MEDIUM | `customer-linked-tickets.png` | Linked tickets section | Line 100 |

### User Guide - Call Logs (3 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `call-log-detail.png` | Call log detail view | Line 65 |
| MEDIUM | `call-log-link-lead.png` | Linking call to lead | Line 80 |
| LOW | `call-log-mobile-sync.png` | Mobile sync status indicator | Line 110 |

### User Guide - Dashboard (3 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `dashboard-charts.png` | Analytics charts section | Line 55 |
| MEDIUM | `dashboard-kpi-cards.png` | KPI metric cards | Line 45 |
| MEDIUM | `dashboard-filters.png` | Date range and filters | Line 70 |

### User Guide - Settings (5 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `settings-main.png` | Settings main page | Line 17 |
| HIGH | `settings-profile.png` | Profile settings tab | Line 28 |
| HIGH | `settings-notifications.png` | Notification preferences | Line 36 |
| MEDIUM | `settings-integrations.png` | Integration settings (WhatsApp) | Line 68 |
| MEDIUM | `settings-permissions.png` | Role permissions table | Line 98 |

### User Guide - Power User Tips (5 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `universal-search.png` | Ctrl+K search modal | Line 25 |
| HIGH | `bulk-select.png` | Multiple items selected | Line 41 |
| MEDIUM | `saved-filters.png` | Saved filter dropdown | Line 61 |
| MEDIUM | `keyboard-shortcuts.png` | Shortcuts overlay (Ctrl+/) | Line 15 |
| LOW | `export-options.png` | Export format selection | Line 178 |

---

### Admin Guide - Installation (3 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `bench-start-terminal.png` | Terminal output of bench start | Line 188 |
| LOW | `frappe-desk-apps.png` | Frappe desk showing CRM app | Line 265 |
| LOW | `site-config-location.png` | file path in terminal | Line 230 |

### Admin Guide - Backup & Restore (3 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `backup-files-listing.png` | ls output of backup directory | Line 87 |
| MEDIUM | `backup-in-progress.png` | Terminal backup running | Line 43 |
| LOW | `restore-success.png` | Successful restore output | Line 142 |

### Admin Guide - Security Checklist (2 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `user-audit-report.png` | User list with last login | Line 65 |
| LOW | `role-permissions-table.png` | Permission matrix | Line 57 |

### Admin Guide - SSL & Email (2 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `ssl-padlock.png` | Browser showing valid SSL | Line 70 |
| MEDIUM | `email-domain-settings.png` | Frappe email domain config | Line 40 |

### Admin Guide - Deploy Production (2 new)

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `supervisor-status.png` | supervisorctl status output | Line 176 |
| LOW | `ufw-status.png` | Firewall status output | Line 35 |

---

### SOPs (18 new)

#### Add Sales User

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `user-list.png` | User list in settings | Line 27 |
| HIGH | `add-user-modal.png` | New user form | Line 35 |
| HIGH | `role-checkboxes.png` | Role assignment checkboxes | Line 55 |
| MEDIUM | `module-permissions.png` | Module access checkboxes | Line 69 |

#### Create Custom Report

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `report-builder.png` | Report Builder interface | Line 28 |
| HIGH | `report-columns.png` | Column selection | Line 51 |
| MEDIUM | `report-filters.png` | Filter configuration | Line 60 |
| MEDIUM | `report-preview.png` | Report preview/output | Line 67 |

#### Data Migration CSV Import

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| HIGH | `data-import-wizard.png` | Data Import main screen | Line 76 |
| HIGH | `import-doctype-select.png` | DocType selection dropdown | Line 77 |
| HIGH | `import-progress.png` | Import progress indicator | Line 81 |
| MEDIUM | `import-errors.png` | Error log display | Line 121 |

#### Onboard New Customer

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `new-site-command.png` | bench new-site output | Line 45 |
| LOW | `site-list.png` | Sites directory listing | Line 55 |

#### Rebuild Search Indexes

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `rq-workers.png` | RQ worker status | Line 65 |
| LOW | `rebuild-output.png` | Rebuild command output | Line 85 |

#### Resolve Permission Issues

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| MEDIUM | `permission-manager.png` | Permission Manager UI | Line 55 |
| LOW | `role-module-perm.png` | Role Module Permission list | Line 80 |

---

### Developer Guide (5 new)

#### Frontend Development

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `vue-devtools.png` | Vue DevTools panel | Line 280 |
| LOW | `vite-dev-server.png` | Vite dev server running | Line 55 |

#### DocType Development

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `doctype-form.png` | DocType form in Frappe | Line 85 |
| LOW | `field-list.png` | Field list editor | Line 120 |

#### API Reference

| Priority | Filename | Description | Insert After |
|----------|----------|-------------|--------------|
| LOW | `api-response-example.png` | API response in browser/Postman | Line 50 |

---

## Capture Guidelines

1. **Resolution**: 1920x1080 or retina (2x)
2. **Format**: PNG for UI, WebP for large images
3. **Theme**: Use consistent light or dark theme
4. **Data**: Use realistic sample data
5. **Privacy**: Blur/fake sensitive information
6. **Cropping**: Focus on relevant UI area
7. **Annotations**: Add arrows/highlights if needed

---

## Priority Legend

| Priority | Meaning |
|----------|---------|
| **HIGH** | Critical for user understanding |
| **MEDIUM** | Enhances documentation quality |
| **LOW** | Nice to have, can add later |

---

## Quick Stats

- **HIGH Priority**: 22 screenshots
- **MEDIUM Priority**: 23 screenshots
- **LOW Priority**: 24 screenshots
