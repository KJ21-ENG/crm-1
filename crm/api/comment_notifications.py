import frappe
import json
from frappe import _


COMMENT_TYPES = ("Mention", "New Message")


def _ensure_owner(notification):
    if getattr(notification, "assigned_to", None) != frappe.session.user:
        frappe.throw(_("You can only operate on your own notifications"))


@frappe.whitelist()
def get_comment_notifications(limit: int = 20, cursor: str | None = None, filter_type: str | None = None):
    """Return comment-related notifications for the current user.

    - Includes only CRM Task Notification of type Mention/New Message
    - Sorted by sent_at desc; falls back to creation desc
    - Supports simple cursor pagination using the last seen name
    """
    try:
        filters = {
            "assigned_to": frappe.session.user,
            "notification_type": ["in", list(COMMENT_TYPES)],
            "status": ["in", ["Pending", "Sent", "Read"]],
        }

        if cursor:
            # naive keyset pagination using name for stability
            filters.update({"name": ["<", cursor]})

        if filter_type == "mentions":
            filters["notification_type"] = "Mention"

        notifications = frappe.get_list(
            "CRM Task Notification",
            filters=filters,
            fields=[
                "name",
                "notification_type",
                "status",
                "message",
                "notification_text",
                "sent_at",
                "read_at",
                "reference_doctype",
                "reference_docname",
            ],
            order_by="coalesce(sent_at, creation) desc, name desc",
            limit=int(limit or 20),
        )

        return notifications
    except Exception as e:
        frappe.logger().exception(f"Error getting comment notifications: {e}")
        return []


@frappe.whitelist()
def mark_comment_notification_read(notification_name: str):
    try:
        doc = frappe.get_doc("CRM Task Notification", notification_name)
        _ensure_owner(doc)
        doc.mark_as_read()
        return {"success": True}
    except Exception as e:
        frappe.logger().exception(f"Error marking comment notification as read: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def mark_all_comment_notifications_read():
    try:
        rows = frappe.get_list(
            "CRM Task Notification",
            filters={
                "assigned_to": frappe.session.user,
                "notification_type": ["in", list(COMMENT_TYPES)],
                "status": "Sent",
            },
            fields=["name"],
        )
        for row in rows:
            frappe.db.set_value("CRM Task Notification", row.name, {
                "status": "Read",
            })
        frappe.db.commit()
        return {"success": True, "count": len(rows)}
    except Exception as e:
        frappe.logger().exception(f"Error marking all comment notifications read: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def quick_reply(reference_doctype: str | None = None, reference_docname: str | None = None, content: str | None = None):
    """Create a Comment on the referenced document with provided HTML content.

    Non-admins often lack direct "Create" on Comment. Allow users to reply if they:
    - Have write permission on the reference doc OR
    - Are assigned to it (in _assign) OR
    - Are the owner of the reference doc

    In those allowed cases, insert the Comment with ignore_permissions=True.
    """
    try:
        if not (reference_doctype and reference_docname and content):
            frappe.throw(_("Missing required parameters"))

        user = frappe.session.user
        ref_doc = frappe.get_doc(reference_doctype, reference_docname)  # enforces read

        # Determine if user is allowed to comment
        allowed = False
        try:
            if frappe.has_permission(reference_doctype, "write", doc=ref_doc, user=user):
                allowed = True
        except Exception:
            pass

        if not allowed:
            try:
                assign_json = ref_doc.get("_assign")
                assigned = json.loads(assign_json) if assign_json else []
                if user in (assigned or []):
                    allowed = True
            except Exception:
                # ignore json errors
                assigned = []

        if not allowed and getattr(ref_doc, "owner", None) == user:
            allowed = True

        # If still not allowed, fall back to Comment create permission
        if not allowed and frappe.has_permission("Comment", "create", user=user):
            allowed = True

        if not allowed:
            frappe.throw(_("You are not allowed to reply on this document."))

        comment = frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": reference_doctype,
            "reference_name": reference_docname,
            "content": content,
        })
        # Insert while bypassing generic Comment perms once we've validated access
        comment.insert(ignore_permissions=True)

        return {"success": True, "comment": comment.name}
    except Exception as e:
        frappe.logger().exception(f"Error posting quick reply: {e}")
        return {"success": False, "error": str(e)}

