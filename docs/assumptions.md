# Documentation Assumptions

This document records assumptions made during the automated documentation generation for Eshin Broking CRM.

---

## General Assumptions

1. **Target Audience**
   - Documentation covers four roles: Sales User, Manager, Admin, Developer
   - Technical knowledge assumed for Admin and Developer guides
   - No prior Frappe knowledge assumed for User guides

2. **Branch Context**
   - All analysis performed on `development-kush-exp` branch
   - This branch represents the current customized production state
   - Upstream frappe/crm serves as baseline for diff comparisons

3. **Environment Assumptions**
   - Production runs on Linux (Ubuntu 22.04 LTS recommended)
   - Python 3.10+ with Frappe v15
   - Node.js 18+ for frontend builds
   - MariaDB 10.8+ as database
   - Redis for caching and queue

---

## Feature Assumptions

4. **WhatsApp Integration**
   - Uses local-whatsapp-service for multi-user support
   - Requires Windows machine for initial QR pairing
   - Session files stored locally per user

5. **Mobile Call Log Sync**
   - React Native app (`call-log-mobile-app/`) is primary
   - Flutter app (`flutter-call-log-mobile-app/`) is secondary/alternative
   - Requires Android device with call log permissions

6. **Permissions Model**
   - Module-based permissions via `CRM Role Module Permission`
   - DocType-level permissions in hooks.py
   - Assignment requests require approval workflow

---

## Documentation Assumptions

7. **Screenshots**
   - All screenshots are placeholders with paths
   - Actual screenshots to be captured manually
   - UI file paths provided for reference

8. **Commands**
   - All bench commands assume standard Frappe bench setup
   - Site name `eshin.localhost` used as example
   - Adjust paths for your environment

9. **SOPs**
   - Procedures assume system administrator has bench access
   - Rollback steps provided where applicable
   - Commands tested on development environment

---

## Technical Assumptions

10. **Docker Setup**
    - docker-compose.yml provided for development only
    - Production deployment uses bench native setup
    - Docker not recommended for production

11. **Backup Scripts**
    - `scripts/backup_eshin_site.sh` is primary backup method
    - Backups stored in `/home/frappe/backups/` by default
    - Daily backups scheduled via hooks.py scheduler

12. **API Reference**
    - Only `@frappe.whitelist()` methods documented
    - Internal methods excluded
    - Curl examples use session-based auth
