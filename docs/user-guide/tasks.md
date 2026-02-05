# Tasks Management

Tasks help you track follow-up activities, deadlines, and action items for leads and tickets.

---

## Purpose

The Tasks module helps you:
- Schedule follow-up activities
- Track deadlines and due dates
- Manage workload across team
- Get notifications before tasks are due

**Typical Users:** All CRM users

---

## Task Properties

| Property | Description |
|----------|-------------|
| Title | What needs to be done |
| Due Date | When it's due |
| Assigned To | Who's responsible |
| Priority | Low/Medium/High/Urgent |
| Status | Open/In Progress/Completed |
| Related To | Linked Lead/Ticket |

---

## Creating a Task

### From a Lead/Ticket

1. Open the Lead or Ticket
2. Click **+ Task** button
3. Fill in:
   - Task title
   - Due date/time
   - Assignee (defaults to you)
4. Click **Save**

### Standalone Task

1. Go to Dashboard or Tasks section
2. Click **+ Create Task**
3. Fill in details
4. Optionally link to Lead/Ticket
5. Save

![Create Task](../assets/screenshots/task-create.png)
<!-- UI File: frontend/src/components/Modals/TaskModal.vue -->

---

## Task Views

### Weekly View

Tasks default to weekly view showing:
- Current week's tasks
- Grouped by day
- Due date indicators
- Priority colors

### By Status

| Status | Description |
|--------|-------------|
| 📋 Open | Not started |
| 🔄 In Progress | Being worked on |
| ✅ Completed | Done |
| ⚠️ Overdue | Past due date |

---

## Task Notifications

### Before Due Date

You receive notifications:
- 1 hour before due time
- At due time
- When task becomes overdue

### Customization

Admins can configure notification timing in settings.

---

## Task Reassignment

### Overdue Task Reassignment

If tasks become overdue, the system can:
1. Auto-notify managers
2. Escalate to supervisors
3. Trigger reassignment workflow

### Manual Reassignment

1. Open the task
2. Click **Assigned To** field
3. Select new user
4. Add note explaining reassignment
5. Save

---

## Completing a Task

1. Open the task
2. Review the requirements
3. Perform the action
4. Click **Mark Complete**
5. Add completion notes (optional)

### Bulk Complete

1. Select multiple tasks
2. Click **Mark Selected Complete**
3. Confirm action

---

## SOP: Daily Task Review

### Purpose
Start each day by reviewing tasks.

### Steps

1. **Check Dashboard**
   - View "Today's Tasks" widget

2. **Review Overdue**
   - Address overdue tasks first
   - Update or complete

3. **Plan Today's Work**
   - Prioritize by due time
   - Prioritize by urgency

4. **Update Status**
   - Mark tasks "In Progress" as you start

5. **Complete or Defer**
   - Mark done when finished
   - Reschedule if needed

---

## Related Guides

- [Leads](leads.md) - Create tasks from leads
- [Tickets](tickets.md) - Create tasks from tickets
- [Dashboard](dashboard.md) - Task widgets
