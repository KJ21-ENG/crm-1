from collections.abc import Iterable

import frappe
from frappe import _
from bs4 import BeautifulSoup
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user
from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification


def on_update(self, method):
    notify_mentions(self)


def notify_mentions(doc):
    """
    Extract mentions from `content`, and notify.
    `content` must have `HTML` content.
    """
    content = getattr(doc, "content", None)
    if not content:
        return
    mentions = extract_mentions(content)
    reference_doc = frappe.get_doc(doc.reference_doctype, doc.reference_name)
    for mention in mentions:
        owner = frappe.get_cached_value("User", doc.owner, "full_name")
        doctype = doc.reference_doctype
        if doctype.startswith("CRM "):
            doctype = doctype[4:].lower()
        name = (
            reference_doc.lead_name
            if doctype == "lead"
            else reference_doc.organization or reference_doc.lead_name
        )
        notification_text = f"""
            <div class="mb-2 leading-5 text-ink-gray-5">
                <span class="font-medium text-ink-gray-9">{ owner }</span>
                <span>{ _('mentioned you in {0}').format(doctype) }</span>
                <span class="font-medium text-ink-gray-9">{ name }</span>
            </div>
        """
        notify_user(
            {
                "owner": doc.owner,
                "assigned_to": mention.email,
                "notification_type": "Mention",
                "message": doc.content,
                "notification_text": notification_text,
                "reference_doctype": "Comment",
                "reference_docname": doc.name,
                "redirect_to_doctype": doc.reference_doctype,
                "redirect_to_docname": doc.reference_name,
            }
        )
        # Also create a Task Reminder style notification so it appears under Task Reminder
        debug_context = {
            "owner": owner,
            "assigned_to": mention.email,
            "reference_doctype": doc.reference_doctype,
            "reference_docname": doc.reference_name,
            "comment_name": doc.name,
        }
        try:
            frappe.logger().debug(f"Creating CRM Task Notification for mention: {debug_context}")

            # Use task notification system: task_name=None for non-task mentions, notification_type 'Mention'
            # Create the task notification using the comment content as message
            notification = create_task_notification(
                task_name=None,
                notification_type="Mention",
                assigned_to=mention.email,
                message=doc.content,
                reference_doctype=doc.reference_doctype,
                reference_docname=doc.reference_name,
            )

            if notification:
                try:
                    # Build enhanced notification_text: header, who mentioned, where, and message preview
                    # Extract plain text preview from HTML content
                    parsed = BeautifulSoup(doc.content or "", "html.parser")
                    preview_text = (parsed.get_text() or "").strip()
                    # Create a short word-based preview (first 20 words) and append ellipsis if truncated
                    words = preview_text.split()
                    if len(words) > 20:
                        preview = " ".join(words[:20]).rstrip() + "..."
                    else:
                        preview = preview_text

                    notification_text = f"""
                        <div class="mb-2 leading-5 text-ink-gray-5">
                            <span class="font-medium text-blue-600">💬 Mention</span>
                            <div class="mt-1">
                                <span class="font-medium text-ink-gray-9">{ owner }</span>
                                <span> mentioned you in </span>
                                <span class="font-medium text-ink-gray-9">{ doc.reference_name }</span>
                            </div>
                            <div class="mt-1 text-sm text-ink-gray-6">Message: { preview }</div>
                        </div>
                    """

                    # Persist the custom formatted notification text
                    try:
                        notification.db_set("notification_text", notification_text)
                    except Exception:
                        frappe.logger().exception("Failed to set notification_text on CRM Task Notification")

                    # Log essential notification fields
                    frappe.logger().info(
                        "CRM Task Notification created",
                        extra={
                            "name": getattr(notification, "name", None),
                            "status": getattr(notification, "status", None),
                            "assigned_to": getattr(notification, "assigned_to", None),
                            "notification_type": getattr(notification, "notification_type", None),
                        },
                    )
                    # Full doc dump for deeper debugging (may be large)
                    frappe.logger().debug(f"Notification full doc: {notification.as_dict()}")
                except Exception:
                    # If as_dict or attributes fail, still continue
                    frappe.logger().exception("Failed to log created notification details")
            else:
                frappe.logger().warning(f"create_task_notification returned None for mention: {debug_context}")

        except Exception:
            # Log exception with context — do not interrupt comment creation
            frappe.logger().exception("Failed to create task reminder notification for mention")
            frappe.logger().error(f"Debug context when failure occurred: {debug_context}")


def extract_mentions(html):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    mentions = []
    for d in soup.find_all("span", attrs={"data-type": "mention"}):
        mentions.append(
            frappe._dict(full_name=d.get("data-label"), email=d.get("data-id"))
        )
    return mentions


@frappe.whitelist()
def add_attachments(name: str, attachments: Iterable[str | dict]) -> None:
    """Add attachments to the given Comment

    :param name: Comment name
    :param attachments: File names or dicts with keys "fname" and "fcontent"
    """
    # loop through attachments
    for a in attachments:
        if isinstance(a, str):
            attach = frappe.db.get_value(
                "File", {"name": a}, ["file_url", "is_private"], as_dict=1
            )
            file_args = {
                "file_url": attach.file_url,
                "is_private": attach.is_private,
            }
        elif isinstance(a, dict) and "fcontent" in a and "fname" in a:
            # dict returned by frappe.attach_print()
            file_args = {
                "file_name": a["fname"],
                "content": a["fcontent"],
                "is_private": 1,
            }
        else:
            continue

        file_args.update(
            {
                "attached_to_doctype": "Comment",
                "attached_to_name": name,
                "folder": "Home/Attachments",
            }
        )

        _file = frappe.new_doc("File")
        _file.update(file_args)
        _file.save(ignore_permissions=True)
