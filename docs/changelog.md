# Changelog

Notable changes to Eshin Broking CRM.

---

## Version History

> **Note:** This changelog is generated based on analysis of the `development-kush-exp` branch. The branch shows 500+ commits ahead of upstream Frappe CRM.

---

## Custom Features (Summary)

### Branding & Identity
- Renamed from "Frappe CRM" to "Eshin Broking CRM System"
- Custom licensing (Proprietary)
- Financial services focus

### Lead Management
- **CRM Prospect** - Enhanced lead tracking
- Custom lead statuses: New, Working, Account Opened, Account Activated
- Custom lead sources: Google Ad, Meta Ad, Referral, Walk-in
- Lead assignment workflow with approval requests

### Ticket Management
- Multi-assignee support in CRM Ticket
- 36 predefined ticket subjects
- Enhanced status workflow
- Ticket-to-lead linking

### Call Logging
- Mobile app call sync (React Native & Flutter)
- `device_call_id` for deduplication
- Cold call tagging
- Monthly export functionality
- Call status normalization

### Task Management
- Task notifications (1-hour before due)
- Overdue task reassignment
- Task-to-lead/ticket linking

### Assignment Workflow
- CRM Assignment Request doctype
- Approval/rejection flow
- Audit trail for assignments

### Integrations
- WhatsApp local service
- Twilio SMS
- Exotel telephony

### Analytics
- Custom dashboard widgets
- Account Opened/Activated metrics
- Lead conversion tracking

---

## Patch History

The following patches have been applied (from `crm/patches.txt`):

### Post Model Sync Patches

| Patch | Description |
|-------|-------------|
| `create_email_template_custom_fields` | Email template customizations |
| `create_default_fields_layout` | Default form layouts |
| `add_device_call_id_to_crm_call_log` | Mobile sync support |
| `update_call_log_statuses_for_frontend_compatibility` | Status normalization |
| `update_lead_data` | Lead data migration |
| `update_lead_data_v2` | Enhanced lead fields |
| `update_lead_data_v3`, `v4`, `v5`, `v6`, `v7` | Iterative improvements |
| `add_phone_linked_leads` | Phone number linking |
| `update_lead_status_options` | Custom status values |
| `add_cold_call_status_to_call_log` | Cold call tagging |
| `set_cold_call_for_existing_call_logs` | Backfill cold calls |
| `update_ticket_statuses` | Ticket status options |
| `revert_ticket_status_change` | Status rollback |
| `update_ticket_subject_options` | Subject list update |
| `update_lead_phone_mobile_to_single_field` | Phone field consolidation |
| `add_new_ticket_subjects` | Additional subjects |
| `create_crm_role_module_permission_doctype` | Role permissions |
| `add_assignment_request_fields_to_lead` | Assignment support |
| `align_mobile_call_log_statuses` | Mobile sync alignment |

---

## Breaking Changes

### API Changes
- Call log statuses normalized to: Incoming, Outgoing, Missed
- Lead phone/mobile fields consolidated

### Schema Changes
- `device_call_id` added to CRM Call Log (unique constraint)
- Assignment fields added to CRM Lead
- Multi-assignee support in CRM Ticket

---

## Upgrade Notes

When upgrading from upstream Frappe CRM:

1. Run all patches: `bench migrate`
2. Rebuild frontend: `bench build --app crm`
3. Clear cache: `bench clear-cache`
4. Verify custom fields exist
5. Test mobile app sync

---

## Contributing

When adding new features:

1. Create patch for schema changes
2. Register in `patches.txt`
3. Update this changelog
4. Update documentation

---

## Related

- [Upgrading & Patching](admin-guide/upgrading-patching.md)
- [Apply Patches SOP](sops/apply-patches-upgrades.md)
