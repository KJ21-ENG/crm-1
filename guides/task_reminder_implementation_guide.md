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

### Example: Adding New Message notifications (what we implemented)

This is the exact flow we implemented to surface chat-like comment messages to assigned users as Task Reminder notifications.

1. Add `New Message` to `CRM Task Notification` `notification_type` options (edit `crm_task_notification.json`) and run `bench --site <site> migrate`.
2. In the comment hook (`apps/crm/crm/api/comment.py`):
   - Read the parent document's `_assign` JSON field (e.g., `CRM Lead._assign`) to get the list of assigned users.
   - Skip notifying the comment owner and users who were explicitly mentioned in the same comment (to avoid duplicate notifications).
   - For each remaining assigned user, call `create_task_notification(..., notification_type="New Message", assigned_to=assigned_user, message=doc.content, reference_doctype=..., reference_docname=...)`.
   - Build a short word-based preview from the HTML comment (first 20 words + `...`) and write it into `notification_text`.
   - Immediately call `notification.mark_as_sent()` (or create the doc with status `Sent`) so realtime publish fires and the frontend reloads.
3. In the notification DocType Python (`apps/crm/crm/fcrm/doctype/crm_task_notification/crm_task_notification.py`):
   - Implement `get_new_message_text()` which formats the header (`💬 New Message In Chat`), support text (`{owner} posted a new message in {doc}`) and the preview.
   - Ensure `create_task_notification()` treats `New Message` notifications as non-de-duplicated (always create a new row) so subsequent comments create separate notifications rather than overwriting existing rows.

### Why we made these choices

- Marking `New Message` as Sent immediately is required because the frontend's realtime handler reloads `taskNotifications` only when a `crm_task_notification` event is published for `status == 'Sent'`.
- We intentionally skip assigned users that are explicitly mentioned to avoid duplicate notifications for the same recipient (they already receive a 'Mention' notification).
- We changed the de-duplication logic in `create_task_notification()` to always create rows for `New Message`/`Mention` so each new comment maps to a new Task Reminder entry.

### Checklist: what the guide now includes (and what we executed)

- [x] Add notification type to DocType JSON and run migrate
- [x] Create helper call in server-side hook to call `create_task_notification` for each recipient
- [x] Add formatted `notification_text` (HTML) via `get_new_message_text()` and/or by setting `notification.db_set("notification_text", ...)`
- [x] Mark notifications as `Sent` to trigger realtime publish
- [x] Avoid duplicate notifications for the same user in the same comment (skip mentioned users)
- [x] Update `create_task_notification()` to bypass de-duplication for chat-like notifications
- [x] Add debug logging for easier troubleshooting

### Recommended additions (not yet in the guide)

- **Add `reference_comment` field** to `CRM Task Notification` and store the comment `name` for traceability (helps debugging and linking notification → comment). This also prevents ambiguous NULL `task` matches.
- **Unit/integration tests**: add a small test or console script that creates multiple comments and verifies separate `CRM Task Notification` rows exist for each assigned recipient.
- **Configurable preview length & verbosity**: make preview word count or character limit a config constant so it is easy to tweak.
- **Permissions**: consider validating `assigned_to` values before insertion if the notification creation could be exposed to external inputs.
- **Realtime throttling**: if chat is very chatty, consider batching or rate-limiting notifications to avoid UI noise.

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



