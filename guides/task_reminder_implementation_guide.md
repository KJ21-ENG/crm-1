# Task Reminder Notification Implementation Guide

This guide explains how to implement Task Reminder style notifications for any activity in the CRM, using the Comment mention work as a reference example. The goal is that an activity can create a `CRM Task Notification` record so it shows in the recipient's **Task Reminders** UI and triggers realtime updates.

## Overview — key components

- **CRM Task Notification (DocType)**: central object for Task Reminder notifications. Key fields:
  - `task` (Link to `CRM Task`) — optional when notification is task-related
  - `assigned_to` (User) — recipient
  - `notification_type` (Select) — type shown in UI
  - `message` (Small Text) — short message
  - `notification_text` (HTML Editor) — formatted HTML content shown in UI
  - `status` (Select: Pending/Sent/Read/Failed) — when `Sent` realtime is published

- **create_task_notification(...)**: helper function in `crm.fcrm.doctype.crm_task_notification.crm_task_notification` that creates the Doc and inserts it. It handles de-duplication for task-based notifications and returns the created Doc or None on error.

- **Realtime publish**: `CRMTaskNotification.publish_realtime_notification()` runs when status becomes `Sent` — it publishes `crm_task_notification` to the assigned user so the frontend reloads.

- **Frontend resource**: `crm.api.task_notifications.get_task_notifications` provides the list; frontend uses `taskNotifications` resource and listens on `crm_task_notification` realtime channel.

## Steps to add Task Reminder notification for an activity

1. Identify the trigger point in server-side logic (e.g., `on_update`, after insert, scheduled job, or API endpoint).

2. Prepare notification data:
   - `assigned_to` (recipient user email)
   - `notification_type` (choose an existing type or add a new option to `CRM Task Notification` doctype JSON — see **DocType changes** below)
   - `message` and optionally `notification_text` (HTML). If `notification_text` is empty, the DocType's `before_insert` will generate it using `format_notification_text()`.
   - Optionally set `task` or `reference_doctype`/`reference_docname` for context.

3. Use the helper to create the notification:

```python
from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification

notification = create_task_notification(
    task_name=None,  # or task id
    notification_type="Task Assignment",  # or custom type
    assigned_to=recipient_email,
    message="Short message to show in reminder",
    reference_doctype="CRM Lead",
    reference_docname=lead_name,
)

if notification:
    # Optionally mark as sent immediately for instant visibility
    notification.mark_as_sent()

```

4. If you need the notification to appear immediately in the UI, ensure the `status` becomes `Sent` (call `mark_as_sent()` after insert). When `status` becomes `Sent`, `publish_realtime_notification()` sends a realtime event to the assigned user.

5. Add server-side logging for debugging (we recommend `frappe.logger().debug(...)` and `frappe.logger().exception(...)`).

## DocType changes (if adding a new notification type)

If you introduce a new `notification_type` value (e.g., `Mention`), update `apps/crm/crm/fcrm/doctype/crm_task_notification/crm_task_notification.json` `notification_type` `options` list and run:

```bash
bench --site crm.localhost migrate
bench restart
```

Then, implement a formatting helper in `CRMTaskNotification.format_notification_text()`:

```python
elif self.notification_type == "Mention":
    self.notification_text = self.get_mention_text()

def get_mention_text(self):
    return f"<div>... use self.message or reference to build html ...</div>"
```

## Realtime & Frontend notes

- The frontend `TaskNotifications` component listens to `crm_task_notification` socket events and reloads `taskNotifications` on event.
- For the realtime event to be sent, `CRM Task Notification.status` must be `Sent`. If notifications are created with `Pending`, the frontend won't receive live updates until they are marked `Sent`.
- Ensure `assigned_to` in the DB matches the logged-in user's `name` (email) used by Frappe sessions.

## Example: Adding mention-based reminders (what we did)

1. Hook: `apps/crm/crm/api/comment.py:on_update` calls `notify_mentions()`.
2. `notify_mentions()` extracts mention spans from comment HTML and calls both `notify_user(...)` (legacy CRM Notification) and `create_task_notification(...)` with `notification_type="Mention"`, `assigned_to` set to the mentioned user's email, and `reference_doctype/reference_docname` for context.
3. We added `Mention` to `CRM Task Notification` `notification_type` options and implemented `get_mention_text()` to render the HTML.
4. After insert we call `notification.mark_as_sent()` so the front-end receives the realtime event immediately.

## Debugging checklist

- If the notification doesn't appear for the recipient:
  - Verify a `CRM Task Notification` row exists with `assigned_to` matching recipient email.
  - Check `status` is `Sent` and `sent_at` is set.
  - Inspect server logs for exceptions during creation (we added logging inside `create_task_notification`).
  - Confirm browser websocket connection receives `crm_task_notification` events and `taskNotifications.reload()` runs.

- Useful console commands:
  - Check recent notifications for user:
    ```python
    frappe.get_all('CRM Task Notification', filters={'assigned_to': 'user@example.com'}, limit=20, order_by='creation desc')
    ```
  - Mark a notification as sent:
    ```python
    n = frappe.get_doc('CRM Task Notification', '<name>')
    n.mark_as_sent()
    ```

## Security & Permissions

- Creating `CRM Task Notification` uses `insert(ignore_permissions=True)` in our helper. Ensure calling code only passes safe data. If exposing an API to external users, validate `assigned_to` and content.

## Summary

To add Task Reminder notifications to any activity:

- Choose the trigger point in server code
- Build notification payload (assigned_to, notification_type, message, references)
- Use `create_task_notification(...)` helper and optionally `mark_as_sent()` for immediate delivery
- Add `notification_type` option and formatting helper if adding a new type
- Verify via console, logs, and frontend websocket events

---

For any activity you'd like me to wire up next (e.g., comment replies, ticket status changes, custom scheduler events), tell me the activity and I will create the integration and a short test script.


