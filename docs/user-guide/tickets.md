# Tickets Management

Tickets track customer support issues, requests, and service tasks. This guide covers creating, managing, and resolving tickets efficiently.

---

## Purpose

The Tickets module helps you:
- Log customer issues and requests
- Track resolution progress
- Maintain service history
- Ensure timely follow-up

**Typical Users:** Support Users, Sales Users, Managers

---

## Ticket Statuses

| Status | Description | SLA Impact |
|--------|-------------|------------|
| Open | New ticket, needs attention | Timer starts |
| In Progress | Actively being worked on | - |
| Waiting for Customer | Pending customer response | Timer paused |
| Resolved | Issue fixed | Timer stops |
| Closed | Ticket completed | Archived |

---

## Creating a Ticket

### Preconditions
- Customer or Lead exists in the system
- You have the issue details

### Steps

1. **Navigate to Tickets**
   - Click **Tickets** in the sidebar

2. **Click Create**
   - Click **+ Create** button

3. **Fill Required Fields**

   | Field | Required | Description |
   |-------|----------|-------------|
   | Subject(s) | ✅ | Select one or more ticket subjects |
   | Customer/Lead | ✅ | Link to existing record |
   | Mobile Number | ✅ | Contact number |
   | Source | ❌ | How ticket was received |
   | Description | ❌ | Detailed issue description |

4. **Select Subjects**
   - Click the subjects dropdown
   - Select applicable subjects (multi-select)
   - Common subjects include: Account Issue, Document Request, Technical Support

5. **Save Ticket**
   - Click **Save**

![Create Ticket](../assets/screenshots/ticket-create.png)
<!-- UI File: frontend/src/components/Modals/TicketModal.vue -->

### Expected Result
- Ticket created with status "Open"
- Assigned to you
- Appears in ticket queue

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No subjects available | Admin needs to configure Ticket Subjects |
| Cannot link customer | Search using mobile number |
| Missing fields | Check required fields are filled |

---

## Viewing Ticket Details

Click any ticket to view details:

### Information Displayed

| Section | Contents |
|---------|----------|
| **Header** | Status, priority, subject |
| **Customer Info** | Name, mobile, linked Lead/Customer |
| **Activity Feed** | Notes, status changes, communications |
| **Attachments** | Related files and documents |

![Ticket Detail](../assets/screenshots/ticket-detail.png)
<!-- UI File: frontend/src/pages/Ticket.vue -->

![Ticket Activity Timeline](../assets/screenshots/ticket-activity-timeline.png)
<!-- TODO: Capture activity feed showing notes, status changes, and communications -->

---

## Working on a Ticket

### Update Status

1. Open the ticket
2. Click status dropdown
3. Select new status
4. Add resolution note (optional)

### Add Notes

1. Open ticket
2. Type in the activity text area
3. Click **Add Note**
4. Note appears in activity feed

### Attach Files

1. Click **Attach File**
2. Select file from computer
3. File uploads and appears in attachments

---

## Multi-Assignee Workflow

Tickets can have multiple assignees for collaborative resolution:

### Adding Assignees

1. Open ticket
2. Click **Assigned To** area
3. Select additional users
4. All assignees see the ticket

### Assignment Visibility

Each assignee sees the ticket in:
- Their ticket list
- Dashboard task counts
- Notifications

![Multiple Assignees Selection](../assets/screenshots/ticket-assignees-multi.png)
<!-- TODO: Capture assignee field showing multiple selected users -->

---

## Linking to Lead/Customer

### Link to Existing Lead

1. In ticket form, click **Lead** field
2. Search by name or mobile
3. Select the lead
4. Lead information auto-populates

### Link to Customer

1. Click **Customer** field
2. Search existing customers
3. Select customer
4. Contact details sync

---

## Ticket Subjects

Ticket subjects categorize issues for reporting:

### Common Subjects

| Subject | Description |
|---------|-------------|
| Account Issue | Problems with customer account |
| Document Request | Customer needs documents |
| Technical Support | System or app issues |
| General Inquiry | Information requests |
| Complaint | Customer complaints |

### Multi-Select

Tickets can have multiple subjects:
- Select primary issue first
- Add secondary issues as needed
- All subjects appear in reports

---

## Ticket Source

Track where tickets originate:

| Source | Description |
|--------|-------------|
| Phone | Inbound call |
| WhatsApp | WhatsApp message |
| Email | Email received |
| Walk-in | In-person visit |
| App | Mobile app created |

---

## SOP: Resolving a Ticket

### Purpose
Properly close a ticket with full documentation.

### Steps

1. **Review Issue**
   - Read all notes and history
   - Understand customer's problem

2. **Take Action**
   - Perform required steps to resolve
   - Document actions in notes

3. **Update Status**
   - Change status to "Resolved"
   - Add resolution summary note

4. **Create Follow-up (if needed)**
   - Click **+ Task**
   - Schedule follow-up call

5. **Close Ticket**
   - After customer confirms resolution
   - Change status to "Closed"

### Verification
- [ ] Resolution note added
- [ ] Customer contacted/confirmed
- [ ] Related tasks completed
- [ ] Status is "Closed"

---

## Power User Tips

- **Quick Filters** - Filter by status, assignee, subject
- **Bulk Close** - Select multiple resolved tickets and close together
- **Templates** - Use saved responses for common issues
- **Keyboard Nav** - Use arrow keys in ticket list

---

## Related Guides

- [Leads](leads.md) - Link tickets to leads
- [Customers](customers.md) - Link tickets to customers
- [Tasks](tasks.md) - Create follow-up tasks
