import frappe
from frappe import _
from frappe.utils import now_datetime


ALLOWED_REFERENCE_DOCTYPES = {"CRM Lead", "CRM Ticket"}
# Admin roles: only true admin/system roles (exclude manager roles)
ADMIN_ROLES = {"Administrator", "System Manager"}


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
    """Return all enabled users whose roles are enabled (request flow, no admin perm required)."""
    try:
        # Pull every enabled Role from Role master
        enabled_roles = set(
            frappe.get_all("Role", filters={"disabled": 0}, pluck="name")
        )

        # Never surface these roles or system users in the public picker
        disallowed_roles = {"Guest"}
        enabled_roles = enabled_roles - disallowed_roles

        # Fetch users who have at least one enabled role (skip system accounts)
        role_rows = frappe.get_all(
            "Has Role",
            filters={
                "role": ["in", list(enabled_roles)],
                "parent": ["not in", ["Administrator", "admin@example.com", "Guest"]],
            },
            fields=["parent", "role"],
        )

        if not role_rows:
            return []

        # Group enabled roles per user for display
        roles_by_user = {}
        for row in role_rows:
            roles_by_user.setdefault(row.parent, []).append(row.role)

        user_ids = sorted(roles_by_user.keys())

        users = frappe.get_all(
            "User",
            filters={"name": ["in", user_ids], "enabled": 1},
            fields=["name", "full_name", "email", "user_image"],
        )

        result = []
        for u in users:
            # Use first enabled role for label; keep entire list available if needed later
            user_roles = roles_by_user.get(u.name, [])
            display_role = user_roles[0] if user_roles else ""
            result.append(
                {
                    "name": u.name,
                    "full_name": u.full_name or u.name,
                    "email": u.email,
                    "user_image": u.user_image,
                    "role": display_role,
                    "enabled": True,
                    "is_crm_user": "CRM User" in user_roles,
                }
            )

        # Sort by full name for stable UI
        result.sort(key=lambda x: x.get("full_name") or "")
        return result
    except Exception as e:
        frappe.log_error(f"Error in get_assignable_users_public: {str(e)}", "Assignment Requests")

def _perform_assignment(reference_doctype: str, reference_name: str, user: str, assigned_by: str):
    try:
        # Use ignore_permissions to bypass admin checks in assign_to_user/assign_ticket_to_user
        # This avoids session logout issues caused by frappe.set_user("Administrator")
        frappe.flags.ignore_permissions = True
        
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
    finally:
        frappe.flags.ignore_permissions = False


@frappe.whitelist()
def create_assignment_request(reference_doctype, reference_name, requested_user, reason):
    if reference_doctype not in ALLOWED_REFERENCE_DOCTYPES:
        frappe.throw(_(f"Unsupported doctype for assignment request: {reference_doctype}"))

    if not frappe.db.exists(reference_doctype, reference_name):
        frappe.throw(_(f"{reference_doctype} {reference_name} does not exist"))

    # Validate requested user
    if not frappe.db.exists("User", requested_user) or not frappe.db.get_value(
        "User", requested_user, "enabled"
    ):
        frappe.throw(_(f"Requested user {requested_user} is not valid/enabled"))
    
    if not reason:
        return {"success": False, "error": "Please enter the reason"}

    # Check if the requested user has the "CRM User" role for direct assignment
    if "CRM User" in frappe.get_roles(requested_user):
        try:
            _perform_assignment(
                reference_doctype=reference_doctype,
                reference_name=reference_name,
                user=requested_user,
                assigned_by=frappe.session.user
            )
            
            # Notify requester
            _notify_user(
                frappe.session.user,
                _(f"You have successfully assigned {reference_doctype} {reference_name} to {requested_user}."),
                reference_doctype,
                reference_name,
                owner=frappe.session.user
            )
            
            # Notify assigned user
            _notify_user(
                requested_user,
                _(f"You have been directly assigned to {reference_doctype} {reference_name}."),
                reference_doctype,
                reference_name,
                owner=frappe.session.user
            )

            # Create Task Notification for the assigned user
            try:
                from crm.fcrm.doctype.crm_task_notification.crm_task_notification import create_task_notification

                dynamic_notification_type = ""
                if reference_doctype == "CRM Lead":
                    dynamic_notification_type = "New Lead Assigned"
                elif reference_doctype == "CRM Ticket":
                    dynamic_notification_type = "New Ticket Assigned"
                else:
                    # Fallback for unexpected doctypes
                    dynamic_notification_type = "New Document Assigned"

                tn = create_task_notification(
                    task_name=None,
                    notification_type=dynamic_notification_type,
                    assigned_to=requested_user,
                    message=f'You have been directly assigned to {reference_name}',
                    reference_doctype=reference_doctype,
                    reference_docname=reference_name,
                )
                if tn:
                    tn.mark_as_sent()
            except Exception as e:
                frappe.logger().error(f"Error creating task notification for direct assignment: {str(e)}")
            
            return {"success": True, "message": f"Directly assigned to {requested_user}"}
            
        except Exception as e:
            frappe.log_error(f"Direct assignment failed: {str(e)}", "Assignment Request Error")
            # If direct assignment fails, we could either throw or fall back to request. 
            # Throwing is safer so the user knows something went wrong.
            frappe.throw(_(f"Direct assignment failed: {str(e)}"))


    doc = frappe.get_doc(
        {
            "doctype": "CRM Assignment Request",
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "requested_user": requested_user,
            "requested_by": frappe.session.user,
            "reason": reason,
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


# Lightweight helper to fetch reference summary for tooltips in Requests list
@frappe.whitelist()
def get_reference_summary(reference_doctype: str, reference_name: str) -> dict:
    """Return a small info summary for a referenced document.

    For CRM Lead:
      - customer_name / full name
      - mobile_no
      - account_type (if available)

    For CRM Ticket:
      - customer_name
      - mobile_no
      - issue_type (ticket_subject or subject)
    """
    try:
        # Defensive defaults
        summary = {
            "customer_name": "",
            "mobile_no": "",
            "extra_label": "",
            "extra_value": "",
        }

        if reference_doctype == "CRM Lead":
            # Prefer customer-linked data when available
            lead = frappe.db.get_value(
                "CRM Lead",
                reference_name,
                [
                    "customer_id",
                    "lead_name",
                    "first_name",
                    "last_name",
                    "mobile_no",
                    "account_type",
                ],
                as_dict=True,
            )
            if lead:
                full_name = None
                # If linked to a customer, extract display name and primary mobile
                cust_id = lead.get("customer_id")
                if cust_id:
                    cust = frappe.db.get_value(
                        "CRM Customer",
                        cust_id,
                        ["customer_name", "mobile_no"],
                        as_dict=True,
                    )
                    if cust:
                        full_name = cust.get("customer_name") or full_name
                        if not lead.get("mobile_no"):
                            lead["mobile_no"] = cust.get("mobile_no")
                if not full_name:
                    full_name = lead.get("lead_name") or " ".join(
                        filter(None, [lead.get("first_name"), lead.get("last_name")])
                    )
                summary.update(
                    {
                        "customer_name": full_name or "",
                        "mobile_no": lead.get("mobile_no") or "",
                        "extra_label": _("Account Type"),
                        "extra_value": lead.get("account_type") or "",
                    }
                )

        elif reference_doctype == "CRM Ticket":
            ticket = frappe.db.get_value(
                "CRM Ticket",
                reference_name,
                [
                    "customer_name",
                    "mobile_no",
                    "ticket_subject",
                    "subject",
                ],
                as_dict=True,
            )
            if ticket:
                issue = ticket.get("ticket_subject") or ticket.get("subject") or ""
                summary.update(
                    {
                        "customer_name": ticket.get("customer_name") or "",
                        "mobile_no": ticket.get("mobile_no") or "",
                        "extra_label": _("Issue Type"),
                        "extra_value": issue,
                    }
                )

        return summary
    except Exception as e:
        frappe.log_error(f"get_reference_summary failed for {reference_doctype} {reference_name}: {str(e)}", "Assignment Request Summary")
        return {
            "customer_name": "",
            "mobile_no": "",
            "extra_label": "",
            "extra_value": "",
        }
