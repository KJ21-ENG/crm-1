# Leads Management

Leads represent potential customers who have shown interest in Eshin Broking's services. This guide covers creating, managing, and converting leads through the sales pipeline.

---

## Purpose

The Leads module helps you:
- Capture prospect information from various sources
- Track lead progress through defined statuses
- Log communication activities
- Convert qualified leads to customers

**Typical Users:** Sales Users, Managers

---

## Lead Statuses

| Status | Description | Next Actions |
|--------|-------------|--------------|
| New | Fresh lead, not yet contacted | Make first contact |
| Contacted | Initial call/message made | Follow up, gather documents |
| Documents Sent | KYC/forms sent to prospect | Track document receipt |
| Sent to HO | Documents forwarded to Head Office | Await processing |
| Account Opened | Account created | Complete activation |
| Account Activated | Fully onboarded | Convert to Customer |
| Lead Expired | No activity timeout | Review or close |

---

## Creating a Lead

### Preconditions
- You are logged in as Sales User, Manager, or Admin
- You have the prospect's contact information

### Steps

1. **Navigate to Leads**
   - Click **Leads** in the sidebar

2. **Click Create**
   - Click the **+ Create** button (top right)
   
   ![Create Lead Button](../assets/screenshots/leads-list-create.png)
   <!-- UI File: frontend/src/pages/Leads.vue -->

3. **Fill Required Fields**

   | Field | Required | Description |
   |-------|----------|-------------|
   | First Name | ✅ | Prospect's first name |
   | Last Name | ❌ | Prospect's last name |
   | Mobile Number | ✅ | Primary contact (10 digits) |
   | Alternative Mobile | ❌ | Secondary contact |
   | Lead Source | ✅ | How they heard about you |
   | Email | ❌ | Email address |

4. **Add Optional Information**
   - Client ID (if existing)
   - Referral Code
   - POD ID (auto-generated)
   - Address details

5. **Save Lead**
   - Click **Save** button
   
   ![Lead Form](../assets/screenshots/leads-modal.png)
   <!-- UI File: frontend/src/components/Modals/LeadModal.vue -->

### Expected Result
- Lead appears in your leads list
- Status set to "New"
- You are assigned as owner

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Mobile number rejected | Ensure 10 digits, no spaces or dashes |
| "Lead already exists" | Search for existing lead with that mobile |
| Cannot see Create button | Check your role permissions |

![Lead Status Workflow](../assets/screenshots/lead-status-workflow.png)
<!-- TODO: Capture status dropdown showing all available lead statuses -->

---

## Viewing Lead Details

Click any lead in the list to open the detail view:

### Information Tabs

| Tab | Contents |
|-----|----------|
| **Activities** | Communication history, notes |
| **Tasks** | Related tasks and follow-ups |
| **Emails** | Email correspondence |
| **WhatsApp** | WhatsApp message history |
| **Calls** | Call log entries |

### Side Panel

The right panel shows:
- Lead status with change history
- Assigned user
- Contact information
- POD ID and Client ID
- Quick action buttons

![Lead Detail](../assets/screenshots/lead-detail.png)
<!-- UI File: frontend/src/pages/Lead.vue -->

![Lead Activities Panel](../assets/screenshots/lead-activities-panel.png)
<!-- TODO: Capture activity panel showing notes, calls, and timeline -->

---

## Updating Lead Status

### Steps

1. Open the lead
2. Click the **Status** dropdown in the side panel
3. Select new status
4. Add optional note explaining the change
5. Status updates automatically

### Status Change Log

All status changes are recorded:
- Timestamp
- Previous status → New status
- User who made the change

---

## Assigning Leads

### Direct Assignment (Managers/Admins)

1. Open the lead
2. Click **Assigned To** field
3. Select new assignee
4. Click **Save**

### Assignment Request (Sales Users)

If you need to transfer a lead:

1. Open the lead
2. Click **Request Assignment**
3. Select target user
4. Enter reason for transfer
5. Submit request

The request goes to your manager for approval.

![Assignment Request](../assets/screenshots/assignment-request.png)
<!-- UI File: frontend/src/components/Modals/AssignmentRequestModal.vue -->

---

## Logging Activities

### Add a Note

1. Open lead
2. Click in the activity input area
3. Type your note
4. Click **Add Note**

### Log a Call

1. Open lead
2. Click **+ Activity** → **Call**
3. Select call type (Incoming/Outgoing)
4. Enter duration and outcome
5. Add notes
6. Save

---

## Mobile Number Actions

### Swap Primary/Alternative

If the alternative mobile is the better contact:

1. Open lead
2. Click the **swap** icon next to mobile fields
3. Numbers are exchanged
4. Related fields update automatically

### Clear Fields on Number Change

When changing the mobile number:
- Linked customer reference is unlinked
- Related call logs may need re-association

---

## Converting to Customer

When a lead's account is activated:

1. Open the lead with status "Account Activated"
2. Click **Convert to Customer**
3. Review customer details
4. Confirm conversion

The lead is marked as converted and a CRM Customer record is created.

---

## Power User Tips

- **Bulk Actions** - Select multiple leads for bulk status update
- **Saved Filters** - Create custom filters and save for quick access
- **Keyboard Shortcut** - Press `Ctrl+K` then type lead name to quick-search
- **Quick Call** - Click the phone icon to initiate a call

![Lead Bulk Actions](../assets/screenshots/lead-bulk-actions.png)
<!-- TODO: Capture multi-select with bulk action options -->

---

## Related Guides

- [Tasks](tasks.md) - Create follow-up tasks for leads
- [Call Logs](call-logs.md) - View synced call history
- [Dashboard](dashboard.md) - Track lead conversion metrics
