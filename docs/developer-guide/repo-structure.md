# Repository Structure

Overview of the Eshin CRM codebase organization.

---

## Top-Level Structure

```
crm/
├── crm/                    # Core Python application
│   ├── api/               # Server-side APIs
│   ├── fcrm/              # DocTypes and modules
│   ├── hooks.py           # Frappe hooks configuration
│   ├── patches/           # Database migrations
│   └── templates/         # Server templates
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── pages/         # Route pages
│   │   └── stores/        # State management
│   └── vite.config.js
├── call-log-mobile-app/   # React Native mobile app
├── flutter-call-log-mobile-app/  # Flutter mobile app
├── local-whatsapp-service/  # WhatsApp integration
├── guides/                # Internal documentation
├── scripts/               # Utility scripts
├── docker/                # Docker configuration
├── docs/                  # Documentation (you are here)
└── mkdocs.yml            # Docs configuration
```

---

## Backend Structure (crm/)

### api/ - API Endpoints

| File | Purpose |
|------|---------|
| `__init__.py` | Route registrations |
| `activities.py` | Activity logging APIs |
| `assignment_requests.py` | Assignment workflow |
| `call_log.py` | Call log management |
| `comment.py` | Comments and mentions |
| `customers.py` | Customer operations |
| `dashboard.py` | Dashboard analytics |
| `doc.py` | Document operations |
| `lead_operations.py` | Lead business logic |
| `mobile_sync.py` | Mobile app sync |
| `permissions.py` | Permission checks |
| `role_assignment.py` | Role management |
| `search.py` | Search functionality |
| `task_notifications.py` | Task reminders |
| `task_reassignment.py` | Task reassignment logic |
| `ticket.py` | Ticket operations |
| `universal_search.py` | Cross-entity search |
| `whatsapp.py` | WhatsApp integration |
| `whatsapp_setup.py` | WhatsApp configuration |
| `whatsapp_support.py` | WhatsApp messaging |

### fcrm/doctype/ - DocTypes

| DocType | Description |
|---------|-------------|
| `crm_lead` | Lead records |
| `crm_ticket` | Support tickets |
| `crm_customer` | Customer records |
| `crm_task` | Task management |
| `crm_call_log` | Call logging |
| `crm_assignment_request` | Assignment workflow |
| `crm_deal` | Deal/opportunity |
| `crm_notification` | Notifications |
| `fcrm_settings` | CRM settings |

### hooks.py

Key configurations:

```python
# Document events
doc_events = {
    "Contact": {"validate": [...]},
    "ToDo": {"after_insert": [...], "on_update": [...]},
    "WhatsApp Message": {"validate": [...], "on_update": [...]},
}

# Scheduled tasks
scheduler_events = {
    "cron": {
        "* * * * *": [
            "crm.api.task_reassignment.process_overdue_task_reassignments",
            "crm.api.task_notifications.check_and_send_task_notifications",
        ],
        "0 2 * * *": ["crm.utils.backup.run_system_backup_script"],
    },
}

# Permission handlers
has_permission = {
    "CRM Lead": "crm.api.permissions.doctype_has_permission",
    "CRM Ticket": "crm.api.permissions.doctype_has_permission",
}
```

---

## Frontend Structure (frontend/)

### src/components/

```
components/
├── Activities/         # Activity feed components
├── CRM/               # Core CRM components
├── Layouts/           # Page layouts
├── Modals/            # Modal dialogs
│   ├── LeadModal.vue
│   ├── TicketModal.vue
│   └── TaskModal.vue
├── Settings/          # Settings components
└── ...
```

### src/pages/

| Page | Route | Description |
|------|-------|-------------|
| `Dashboard.vue` | `/crm` | Main dashboard |
| `Leads.vue` | `/crm/leads` | Lead list |
| `Lead.vue` | `/crm/leads/:id` | Lead detail |
| `Tickets.vue` | `/crm/tickets` | Ticket list |
| `Ticket.vue` | `/crm/tickets/:id` | Ticket detail |
| `Customers.vue` | `/crm/customers` | Customer list |
| `Customer.vue` | `/crm/customers/:id` | Customer detail |
| `CallLogs.vue` | `/crm/call-logs` | Call logs |

### src/stores/

State management with Pinia/Vuex:

| Store | Purpose |
|-------|---------|
| `user.js` | Current user state |
| `settings.js` | Application settings |
| `leads.js` | Lead data cache |
| `tickets.js` | Ticket data cache |

---

## Mobile Apps

### call-log-mobile-app/ (React Native)

```
call-log-mobile-app/
├── src/
│   ├── components/    # UI components
│   ├── screens/       # App screens
│   ├── services/      # API services
│   ├── store/         # Redux store
│   └── utils/         # Utilities
├── app.json          # Expo configuration
└── package.json
```

### flutter-call-log-mobile-app/ (Flutter)

```
flutter-call-log-mobile-app/
├── lib/
│   ├── models/       # Data models
│   ├── screens/      # App screens
│   ├── services/     # API services
│   └── widgets/      # Custom widgets
└── pubspec.yaml
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `start_crm_dev.sh` | Start development environment |
| `stop_crm_dev.sh` | Stop development environment |
| `status_crm_dev.sh` | Check service status |
| `scripts/backup_eshin_site.sh` | Site backup |
| `scripts/backup_site.sh` | Generic backup |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python project config |
| `package.json` | Node.js dependencies |
| `mkdocs.yml` | Documentation config |
| `docker-compose.yml` | Docker setup |

---

## Key Directories

| Path | Purpose | Access |
|------|---------|--------|
| `crm/api/` | Backend APIs | Developers |
| `crm/fcrm/doctype/` | DocType definitions | Developers |
| `crm/patches/` | DB migrations | Developers |
| `frontend/src/` | Frontend source | Developers |
| `docs/` | Documentation | All |
