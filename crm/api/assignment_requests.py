import frappe
from frappe import _
from frappe.utils import now_datetime


ALLOWED_REFERENCE_DOCTYPES = {"CRM Lead", "CRM Ticket"}
# Expand admin roles to include Administrator and CRM Manager
ADMIN_ROLES = {"Administrator", "System Manager", "Sales Manager", "Support Manager", "CRM Manager"}


def _get_admin_users():
    users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", list(ADMIN_ROLES)]},
        fields=["parent"],
    )
    user_ids = sorted({u.parent for u in users if u.parent})
    if not user_ids:
        return []
    enabled = frappe.get_all(
        "User", filters={"name": ["in", user_ids], "enabled": 1}, fields=["name"]
    )
    return [u.name for u in enabled]


def _notify_user(assigned_to: str, message: str, ref_dt: str = None, ref_dn: str = None, owner: str = None):
    """Send a CRM Notification to a user. Provide `owner` to avoid notify_user skipping when owner == assigned_to."""
    try:
        from crm.fcrm.doctype.crm_notification.crm_notification import notify_user

        notify_user(
            {
                "owner": owner or frappe.session.user,
                "assigned_to": assigned_to,
                "notification_type": "Assignment Request",
                "message": message,
                "notification_text": message,
                "reference_doctype": ref_dt or "",
                "reference_docname": ref_dn or "",
                "redirect_to_doctype": ref_dt or "",
                "redirect_to_docname": ref_dn or "",
            }
        )
    except Exception:
        frappe.log_error(
            f"Failed to send CRM Notification to {assigned_to}", "Assignment Request Notification"
        )


@frappe.whitelist()
def get_assignable_users_public():
    """Return list of enabled CRM users for request flow (no admin permission required)."""
    try:
        allowed_roles = ["Sales User", "Support User", "Sales Manager", "Support Manager"]
        role_rows = frappe.get_all(
            "Has Role",
            filters={
                "role": ["in", allowed_roles],
                "parent": ["not in", ["Administrator", "admin@example.com", "Guest"]],
            },
            fields=["parent"],
        )
        user_ids = sorted({r.parent for r in role_rows})
        if not user_ids:
            return []
        users = frappe.get_all(
            "User",
            filters={"name": ["in", user_ids], "enabled": 1},
            fields=["name", "full_name", "email", "user_image"],
        )
        # Add first matching CRM role for display
        result = []
        for u in users:
            roles = frappe.get_roles(u.name)
            first_role = next((r for r in roles if r in allowed_roles), None)
            result.append(
                {
                    "name": u.name,
                    "full_name": u.full_name or u.name,
                    "email": u.email,
                    "user_image": u.user_image,
                    "role": first_role or "",
                    "enabled": True,
                }
            )
        # Sort by full name
        result.sort(key=lambda x: x.get("full_name") or "")
        return result
    except Exception as e:
        frappe.log_error(f"Error in get_assignable_users_public: {str(e)}", "Assignment Requests")
        return []


@frappe.whitelist()
def create_assignment_request(reference_doctype, reference_name, requested_user, reason=None):
    if reference_doctype not in ALLOWED_REFERENCE_DOCTYPES:
        frappe.throw(_(f"Unsupported doctype for assignment request: {reference_doctype}"))

    if not frappe.db.exists(reference_doctype, reference_name):
        frappe.throw(_(f"{reference_doctype} {reference_name} does not exist"))

    # Validate requested user
    if not frappe.db.exists("User", requested_user) or not frappe.db.get_value(
        "User", requested_user, "enabled"
    ):
        frappe.throw(_(f"Requested user {requested_user} is not valid/enabled"))

    doc = frappe.get_doc(
        {
            "doctype": "CRM Assignment Request",
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "requested_user": requested_user,
            "requested_by": frappe.session.user,
            "reason": reason or "",
            "status": "Pending",
        }
    )
    doc.insert(ignore_permissions=True)

    # Add a timeline comment on the referenced document
    try:
        full = frappe.utils.get_fullname(frappe.session.user)
        target = frappe.utils.get_fullname(requested_user)
        comment = frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "content": _(
                    f"📩 {full} requested assignment to <strong>{target}</strong> (admin approval required)."
                ),
                "comment_email": frappe.session.user,
            }
        )
        comment.insert(ignore_permissions=True)
    except Exception:
        pass

    # Notify admins
    admin_users = _get_admin_users()
    for admin_user in admin_users:
        _notify_user(
            admin_user,
            _(
                f"New assignment request for {reference_doctype} {reference_name} → {requested_user}"
            ),
            reference_doctype,
            reference_name,
            owner=frappe.session.user,
        )

    # Mark admin notifications as sent if using task notification system
    try:
        # create a CRM Task Notification for admins so it appears in admin task reminders
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        admin_task_notifications = []
        for admin in admin_users:
            tn = create_task_notification(
                task_name=None,  # No specific task for assignment requests
                notification_type='Assignment Request',
                assigned_to=admin,
                message=f'Assignment request for {reference_name} by {frappe.utils.get_fullname(frappe.session.user)}',
                reference_doctype=reference_doctype,
                reference_docname=reference_name,
            )
            if tn:
                # Mark as sent so it appears in Task Reminder section
                tn.mark_as_sent()
                admin_task_notifications.append(tn.name)
    except Exception as e:
        frappe.logger().error(f"Error creating admin task notifications: {str(e)}")
        admin_task_notifications = []


    # Notify requester (ack)
    _notify_user(
        frappe.session.user,
        _(
            f"Your assignment request has been submitted for {reference_doctype} {reference_name}"
        ),
        reference_doctype,
        reference_name,
        owner=frappe.session.user,
    )

    # We do not create a Task Reminder notification for the submitted state to avoid noise.
    # Requester will be notified via Task Reminder only when request is Approved or Rejected.

    frappe.db.commit()
    debug = {
        "admin_users": admin_users,
        "admin_task_notifications": admin_task_notifications,
    }
    return {"success": True, "name": doc.name, "debug": debug}


@frappe.whitelist()
def get_assignment_requests(status=None, mine=False):
    filters = {}
    if status:
        filters["status"] = status

    # Non-admins can see only their own requests
    is_admin_like = any(role in ADMIN_ROLES for role in frappe.get_roles())
    if not is_admin_like or frappe.utils.cint(mine):
        filters["requested_by"] = frappe.session.user

    reqs = frappe.get_list(
        "CRM Assignment Request",
        filters=filters,
        fields=[
            "name",
            "creation",
            "reference_doctype",
            "reference_name",
            "requested_user",
            "requested_by",
            "reason",
            "status",
            "approved_by",
            "approved_on",
        ],
        order_by="creation desc",
        limit_page_length=200,
    )
    return reqs


def _perform_assignment(reference_doctype: str, reference_name: str, user: str, assigned_by: str):
    if reference_doctype == "CRM Lead":
        from crm.api.role_assignment import assign_to_user

        res = assign_to_user(lead_name=reference_name, user_name=user, assigned_by=assigned_by)
        if not res or not res.get("success"):
            frappe.throw(_(res.get("error") if res else "Lead assignment failed"))
    elif reference_doctype == "CRM Ticket":
        from crm.api.ticket import assign_ticket_to_user

        res = assign_ticket_to_user(
            ticket_name=reference_name, user_name=user, assigned_by=assigned_by
        )
        if not res or not res.get("success"):
            frappe.throw(_(res.get("error") if res else "Ticket assignment failed"))
    else:
        frappe.throw(_(f"Unsupported doctype: {reference_doctype}"))


@frappe.whitelist()
def approve_assignment_request(name, note=None):
    # Permission: admin roles only
    if not any(role in ADMIN_ROLES for role in frappe.get_roles()):
        frappe.throw(_("You are not permitted to approve assignment requests."))

    req = frappe.get_doc("CRM Assignment Request", name)
    if req.status != "Pending":
        frappe.throw(_("Only pending requests can be approved."))

    _perform_assignment(
        reference_doctype=req.reference_doctype,
        reference_name=req.reference_name,
        user=req.requested_user,
        assigned_by=frappe.session.user,
    )

    req.status = "Approved"
    req.approved_by = frappe.session.user
    req.approved_on = now_datetime()
    if note:
        req.db_set("assignment_notes", note)
    req.save(ignore_permissions=True)

    # Notify requester (support text uses doc name only)
    _notify_user(
        req.requested_by,
        _(
            f"Your assignment request for {req.reference_name} has been approved."
        ),
        req.reference_doctype,
        req.reference_name,
    )

    # Notify assigned user as well
    try:
        _notify_user(
            req.requested_user,
            _(f"You have been assigned to {req.reference_doctype} {req.reference_name} by admin approval."),
            req.reference_doctype,
            req.reference_name,
        )
    except Exception:
        pass

    # Also create task notification for requester
    try:
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        tn = create_task_notification(
            task_name=None,  # No specific task for assignment requests
            notification_type='Assignment Request Approved',
            assigned_to=req.requested_by,
            message=f'Your assignment request for {req.reference_name} has been approved',
            reference_doctype=req.reference_doctype,
            reference_docname=req.reference_name,
        )
        if tn:
            # Mark as sent so it appears in Task Reminder section
            tn.mark_as_sent()
        else:
            frappe.logger().info(f"No task notification created for requester {req.requested_by} on approval of {req.name}")
    except Exception as e:
        frappe.logger().error(f"Error creating approval task notification: {str(e)}")

    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def reject_assignment_request(name, reason=None):
    # Permission: admin roles only
    if not any(role in ADMIN_ROLES for role in frappe.get_roles()):
        frappe.throw(_("You are not permitted to reject assignment requests."))

    req = frappe.get_doc("CRM Assignment Request", name)
    if req.status != "Pending":
        frappe.throw(_("Only pending requests can be rejected."))

    req.status = "Rejected"
    if reason:
        req.rejection_reason = reason
    req.approved_by = frappe.session.user
    req.approved_on = now_datetime()
    req.save(ignore_permissions=True)

    # Notify requester (include reason when provided; support text uses doc name only)
    rejection_message = f"Your assignment request for {req.reference_name} has been rejected"
    if reason:
        rejection_message = f"{rejection_message} Reason : {reason}"

    _notify_user(
        req.requested_by,
        _(
            rejection_message
        ),
        req.reference_doctype,
        req.reference_name,
    )

    # Also create task notification for requester
    try:
        from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification
        tn = create_task_notification(
            task_name=None,  # No specific task for assignment requests
            notification_type='Assignment Request Rejected',
            assigned_to=req.requested_by,
            message=rejection_message,
            reference_doctype=req.reference_doctype,
            reference_docname=req.reference_name,
        )
        if tn:
            # Mark as sent so it appears in Task Reminder section
            tn.mark_as_sent()
        else:
            frappe.logger().info(f"No task notification created for requester {req.requested_by} on rejection of {req.name}")
    except Exception as e:
        frappe.logger().error(f"Error creating rejection task notification: {str(e)}")

    frappe.db.commit()
    return {"success": True}


