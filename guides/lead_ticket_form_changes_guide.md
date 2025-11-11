# Lead & Ticket Form Changes — Implementation Guide

This document explains the recent changes made to the CRM Lead and Ticket Quick Entry forms, why they were made, what components are involved, and the exact steps required when changing, adding, or removing fields in these forms.

## Summary of changes
- Converted Ticket Quick Entry `Ticket Information` section to a 3-column layout for visual alignment with `Contact Information`.
- Removed `issue_type` from Ticket Quick Entry (frontend) and planned a server-side default of `issue_type = 'Account'` for created tickets.
- Removed `department` from Ticket Quick Entry layout.
- Redesigned CRM Lead Quick Entry layout to a 3-column format matching Ticket, removed helper descriptions, and hid `client_id` from Quick Entry.
- Adjusted frontend `FieldLayout` components and modal transforms to ensure consistent spacing and single-line labels (e.g., `Aadhaar Card Number`).

## Files changed (high level)
- Frontend:
  - `apps/crm/frontend/src/components/FieldLayout/Field.vue` — label styling; prevent wrapping and maintain consistent field height.
  - `apps/crm/frontend/src/components/FieldLayout/Section.vue` & `Column.vue` — grid and column alignment improvements.
  - `apps/crm/frontend/src/components/Modals/TicketModal.vue` — remove helper text and fine-tune field descriptions and visibility.
  - `apps/crm/frontend/src/components/Modals/LeadModal.vue` — remove `client_id` defaults, hide `client_id` field in Quick Entry, move `assign_to_role` under `status`, and clean helper descriptions.

- Backend / Patches:
  - `apps/crm/crm/patches/v1_0/update_ticket_quick_entry_three_column_layout.py` and subsequent ticket layout patches — programmatic layout updates applied via migration.
  - `apps/crm/crm/patches/v1_0/update_lead_quick_entry_three_column_layout.py` — lead layout migration.
  - `apps/crm/crm/patches/v1_0/remove_client_id_from_lead_quick_entry_layout.py` — remove `client_id` from stored Quick Entry layout.
  - `apps/crm/crm/patches.txt` — register new patches so they are executed on `bench migrate`.

## Why these changes were made
- Visual alignment: multi-column layouts must align fields horizontally so users can scan rows quickly.
- Spacing and helper texts: helper/description texts caused inconsistent vertical spacing. Removing or clearing these for Quick Entry produces uniform spacing.
- Single-line labels: long labels (e.g., `Aadhaar Card Number`) were wrapped; label CSS now enforces no-wrap with ellipsis to preserve row height.
- Data integrity: fields like `client_id` should not be editable in Quick Entry but still exist in the DocType for data consistency; hence hidden in the UI and controlled server-side.

## Factors to consider when changing/adding/removing fields

- Data model vs UI: decide whether change is purely presentation (hide/change label) or requires schema change (add/remove field in DocType JSON). Schema changes require patches and database migrations.
- Backwards compatibility: removing a field from UI doesn't delete data. If you plan to remove a field entirely (DocType JSON change), create a migration patch to migrate/clean existing data first.
- Field permissions: changes to read-only/hidden state may require permission checks; ensure only intended roles can edit sensitive fields (e.g., `lead_owner`).
- Validation: if a field becomes optional in UI but required server-side, reconcile validation rules to avoid failed saves.
- Patches & deployment: any DocType JSON or database-impacting changes must be added as a patch and registered in `apps/crm/crm/patches.txt` so `bench migrate` picks them up.
- Frontend transforms: Quick Entry uses `CRM Fields Layout` entries fetched from server; the client-side `transform` step can hide/modify fields for Quick Entry without changing DocType JSON.
- Testing: after changes, verify Quick Entry, full form, list and report views, and related automations (role assignment, referral updates, tasks).

## Step-by-step: How we implemented the Lead and Ticket changes

1. Analyze the DocType JSON for `CRM Lead` and `CRM Ticket` to identify field definitions and default `field_order`.
2. Create or update a `CRM Fields Layout` entry via a Python patch to define the desired Quick Entry layout (3-column sections). Example patch creates `layout.layout = json.dumps(new_layout)` and saves it.
3. Update `apps/crm/crm/patches.txt` to register the new patch under `[post_model_sync]` so it runs on `bench migrate`.
4. For frontend-only display tweaks (remove helper text, hide `client_id` in Quick Entry), modify the modal's layout transform (e.g., `LeadModal.vue` and `TicketModal.vue`) to:
   - clear `field.description`
   - set `field.visible = 0` for fields to hide from Quick Entry
   - change `field.read_only` where needed
   - insert synthetic fields like `assign_to_role` into the `column.fields` array at desired index
5. For global rendering/spacing fixes, edit `FieldLayout` child components to use CSS Grid and consistent row heights, and force no-wrapping of labels.
6. Add a backend patch if you need to remove a field from stored layouts (we added `remove_client_id_from_lead_quick_entry_layout.py`).
7. Run migrations locally:

```bash
cd /Volumes/MacSSD/Development/CursorAI_Project/frappe-crm-bench
bench --site crm.localhost migrate
bench --site crm.localhost restart
```

8. Verify in UI: open Quick Entry modals for Lead and Ticket, ensure fields match sketch, check spacing, and test create flows.

9. Run integration checks: ensure role assignment, referral updates, task creation logic still function as expected after field changes.

10. If a removed field is used in server logic, update server code to stop referencing it or to supply a default (e.g., `issue_type = 'Account'` when missing).

## Rollback and cleanup notes
- If a patch fails or layout is incorrect, restore previous `CRM Fields Layout` using the backups or by re-running a corrective patch.
- Do NOT delete a DocType field from JSON without a migration plan — first create a patch that migrates/cleans existing values, add it to `patches.txt`, run migrate, then remove the field in a following patch.

## Suggested checklist before merging changes
- [ ] DocType / field changes reviewed and approved
- [ ] Patch file added and listed in `patches.txt`
- [ ] Frontend transform updates implemented and linted
- [ ] Migration run on a staging site and verified
- [ ] UI verified for Quick Entry, full form, list view, and task flows
- [ ] Unit/integration tests updated if needed
- [ ] Clear developer notes in commits and guide (this file)

## Appendix — Useful Commands
- Run patches & migrations:

```bash
bench --site crm.localhost migrate
bench --site crm.localhost restart
```

- Test JS linting (project dependent):

```bash
cd apps/crm/frontend && npm run lint || true
```

---

If you want, I can also:
- add the `issue_type` server-side default patch now, or
- prepare a patch to completely remove `client_id` from the DocType JSON after migrating values.

File created: `apps/crm/guides/lead_ticket_form_changes_guide.md`


